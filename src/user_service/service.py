from fastapi import HTTPException, File, UploadFile
from src.user_service.models import UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.uitils.uitils import Hash
from src.uitils.scheme import SUser
import logging
from src.user_service.scheme import SUserResponse, SUpdateUserComponents
from sqlalchemy import select
import aiofiles
import os
import uuid
import json
from redis.asyncio import StrictRedis
from datetime import datetime
from typing import Type, TypeVar, Optional

T = TypeVar("T")


KAFKA_SERVER = "localhost:9092"
TOPIC = "user_data"
MEDIA_ROOT = "media/user_pictures/"
CACHE_KEY = None


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class UserService:

    def __init__(
        self,
        session: AsyncSession = None,
        current_user: SUser = None,
        redis_client: StrictRedis = None,
    ):
        self._session = session
        self._current_user = current_user
        self._producer = None
        self._redis_client = redis_client

    async def _sign_up(
        self,
        username: str,
        password: str,
        email: str,
        name: str,
        picture_: UploadFile = File(...),
    ):

        exist_user_query = await self._session.execute(
            select(UserModel).filter_by(username=username, email=email)
        )

        exist_user = exist_user_query.scalars().first()
        if exist_user:
            raise HTTPException(
                detail="Username Or Email All ready used by other user !",
                status_code=422,
            )

        if picture_ is not None:
            picture_.filename = f"{uuid.uuid4()}.jpg"
            file_path = os.path.join(MEDIA_ROOT, picture_.filename)

            async with aiofiles.open(file_path, "wb") as out_file:
                while content := await picture_.read(1024):
                    await out_file.write(content)
            log.info(f"Picture {picture_.filename} saved at {file_path}")

        ################################ HASH REQ PASSWORD #############################
        hash_req_password = Hash.bcrypt(password)
        log.debug("USER PASSWORD HASHED")

        user = UserModel(
            username=username,
            name=name,
            email=email,
            picture_url=picture_.filename if picture_.filename else None,
            password=hash_req_password,
        )

        self._session.add(user)
        await self._session.commit()

    async def _get_user_by_username_password(
        self, username: str, password: str
    ) -> SUserResponse:

        user_query = await self._session.execute(
            select(UserModel).filter_by(username=username)
        )
        user = user_query.scalars().first()

        if not user:
            log.info(f"User By username {username} not found")
            raise HTTPException(detail="User Not Found", status_code=404)

        if not Hash.verify(hashed_password=user.password, plain_password=password):
            log.info("In correct Password")
            raise HTTPException(detail="Password Error", status_code=422)

        return SUserResponse.from_orm(user)

    async def _get_user_by_username(self, username: str) -> SUserResponse:

        user_query = await self._session.execute(
            select(UserModel).filter_by(username=username)
        )

        user = user_query.scalars().first()
        if not user:
            raise HTTPException(detail="Not Found", status_code=404)

        return SUserResponse.from_orm(user)

    async def get_user_by_id(self, pk: int) -> SUserResponse:

        cached_data = await self.get_cached_data(f"get-user-by-id-{pk}")

        if cached_data:
            return SUserResponse(**cached_data)

        user = await self._session.execute(select(UserModel).filter_by(id=pk))
        user = user.scalars().first()

        if not user:
            raise HTTPException(detail="User Not Found", status_code=404)

        user_response = SUserResponse.model_validate(user)

        await self._redis_client.setex(
            f"get-user-by-id-{pk}",
            3600,
            json.dumps(user_response.dict(), cls=DateTimeEncoder),
        )

        return user_response

    async def _update_user_components(self, request: SUpdateUserComponents) -> dict:

        user = (
            (
                await self._session.execute(
                    select(UserModel).filter(UserModel.id == self._current_user.id)
                )
            )
            .scalars()
            .first()
        )

        for field, value in request.dict(exclude_unset=True).items():
            if field in ["username", "email", "bio", "name"] and value is not None:
                setattr(user, field, value)

        await self._session.commit()

        return {"detail": "Updated Succsesfully"}

    async def get_cached_data(self, cache_name: str) -> Type[Optional[dict]]:
        cache_key = f"{cache_name}"
        cached_data = await self._redis_client.get(cache_key)

        if cached_data:
            log.warn(f"Cache hit for {cache_name}")
            return json.loads(cached_data)

        return None
