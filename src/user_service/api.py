from fastapi import Depends, APIRouter, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from src.user_service.service import (
    UserService,
    SUser,
    SUserResponse,
    SUpdateUserComponents,
)
from src.config.user_database import get_user_session
from src.auth_service.oauth import get_current_user
from redis.asyncio import Redis, StrictRedis


def get_redis_client() -> StrictRedis:
    return StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)


user_service_router = APIRouter(tags=["User Service"], prefix="/user-service/api/v1")


@user_service_router.post("/sign-up/")
async def create_account(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    name: str = Form(...),
    session: AsyncSession = Depends(get_user_session),
    profile_picture: UploadFile = File(...),
):
    service = UserService(session=session)
    return await service._sign_up(
        username=username,
        password=password,
        picture_=profile_picture,
        email=email,
        name=name,
    )


@user_service_router.get(
    "/get-user-by-username-password/{username}/{password}", response_model=SUserResponse
)
async def get_user_by_username(
    username: str,
    password: str,
    session: AsyncSession = Depends(get_user_session),
    redis_client: Redis = Depends(get_redis_client),
):
    service = UserService(session=session, redis_client=redis_client)
    return await service._get_user_by_username_password(
        username=username,
        password=password,
    )


@user_service_router.get("/get-user/{username}/", response_model=SUserResponse)
async def get_user_use_username(
    username: str, session: AsyncSession = Depends(get_user_session)
):
    service = UserService(session=session)
    return await service._get_user_by_username(username=username)


@user_service_router.get("/get-user-by-pk/{user_id}/", response_model=SUserResponse)
async def get_user_use_id(
    user_id: int,
    session: AsyncSession = Depends(get_user_session),
    current_user: SUser = Depends(get_current_user),
    redis_client: Redis = Depends(get_redis_client),
):
    service = UserService(
        session=session, current_user=current_user, redis_client=redis_client
    )
    return await service.get_user_by_id(pk=user_id)


@user_service_router.patch("/update-user-components/")
async def update_user_components(
    request: SUpdateUserComponents,
    current_user: SUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_user_session),
):
    service = UserService(session=session, current_user=current_user)
    return await service._update_user_components(request)
