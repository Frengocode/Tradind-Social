from fastapi import HTTPException, Form, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import os
import uuid
import aiofiles
import logging
from typing import List, Optional
import httpx
import asyncio
from sqlalchemy import select
from src.signals_service.models import SignalModel
from src.signals_service.scheme import SignalResponse, UpdateSignalRequest
from src.uitils.scheme import SUser
from src.uitils.uitils import log
from redis.asyncio import StrictRedis
import json
from src.requests.request import GET_USER




MEDIA_ROOT = "media/signals/"


class CustomDateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


class SignalService:
    def __init__(
        self,
        session: AsyncSession = None,
        current_user: SUser = None,
        redis_client: StrictRedis = None,
    ):
        self.session = session
        self.current_user = current_user
        self.redis_client = redis_client

    async def _create_signal(
        self,
        title: str = Form(...),
        signal_picture: UploadFile = File(...),
        signal_for_coin: str = Form(...),
        short_or_long: str = Form(...),
        when: datetime = Form(...),
        when_end: datetime = Form(...),
    ) -> SignalResponse:
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(MEDIA_ROOT, filename)

        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await signal_picture.read(1024):
                await out_file.write(content)
        log.info(f"Signal picture {filename} saved at {file_path}")

        signal = SignalModel(
            title=title,
            signal_picture=filename,
            signal_for_coin=signal_for_coin,
            short_or_long=short_or_long,
            when=when,
            when_end=when_end,
            user_id=self.current_user.id,
        )

        self.session.add(signal)
        await self.session.commit()
        log.info(f"Signal with id {signal.id} created successfully")

        return SignalResponse.model_validate(signal.__dict__)

    async def _get_all_signals(self) -> List[SignalResponse]:
        cache_key = "get-all-signals"

        cache_data = await self._get_cached_data(cache_name=cache_key)
        if cache_data:
            log.warn("Returing data from cache Please Wait")
            return [
                SignalResponse(
                    **{key: value for key, value in signal.items() if key != "user"},
                    user=SUser(**signal["user"]) if signal.get("user") else None,
                )
                for signal in cache_data
            ]

        signals = (
            (
                await self.session.execute(
                    select(SignalModel).order_by(SignalModel.created_at.desc())
                )
            )
            .scalars()
            .all()
        )

        if not signals:
            return []

        user_data = {}
        user_responses = await asyncio.gather(
            *(
                self.get_data_from_url(f"{GET_USER}/{signal.user_id}/")
                for signal in signals
            ),
            return_exceptions=True,
        )

        for signal, user_response in zip(signals, user_responses):
            if isinstance(user_response, dict):
                user_data[signal.user_id] = user_response
            else:
                log.warning(
                    f"Error of getting user data ID {signal.user_id}: {user_response}"
                )
                user_data[signal.user_id] = None

        signal_response = [
            {
                **{
                    key: value
                    for key, value in vars(signal).items()
                    if not key.startswith("_")
                },
                "user": user_data.get(signal.user_id),
            }
            for signal in signals
        ]

        await self.redis_client.setex(
            cache_key,
            3600,
            json.dumps(signal_response, cls=CustomDateTimeEncoder),
        )

        return [
            SignalResponse(
                **{key: value for key, value in signal.items() if key != "user"},
                user=SUser(**signal["user"]) if signal["user"] else None,
            )
            for signal in signal_response
        ]

    async def _get_user_signals(self, user_id: int) -> List[SignalResponse]:
        result = await self.session.execute(
            select(SignalModel)
            .filter_by(user_id=user_id)
            .order_by(SignalModel.created_at.desc())
        )
        signals = result.scalars().all()
        return (
            [SignalResponse.model_validate(signal.__dict__) for signal in signals]
            if signals
            else []
        )

    async def _get_signal(self, signal_id: int) -> SignalResponse:
        result = await self.session.execute(select(SignalModel).filter_by(id=signal_id))
        signal = result.scalars().first()

        if not signal:
            raise HTTPException(detail="Notfound", status_code=404)

        user_data = await self.get_data_from_url(f"{GET_USER}/{signal.user_id}/")

        cached_data = await self._get_cached_data(cache_name=f"get-signal-{signal_id}")
        if cached_data:
            return SignalResponse(**signal.__dict__, user=SUser(**user_data))

        signal_response = SignalResponse(**signal.__dict__)

        if not signal:
            raise HTTPException(detail="Not Found", status_code=404)

        await self.redis_client.setex(
            f"get-signal-{signal_id}",
            3600,
            json.dumps(signal_response.dict(), cls=CustomDateTimeEncoder),
        )

        return SignalResponse(
            **signal.__dict__, user=SUser(**user_data) if user_data else None
        )

    async def get_data_from_url(self, url: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {self.current_user.token}"},
            )
        if response.status_code == 200:
            return response.json()
        return None

    async def _update_signal_obj(
        self, signal_id: int, request: UpdateSignalRequest
    ) -> dict:
        result = await self.session.execute(
            select(SignalModel).filter_by(user_id=self.current_user.id, id=signal_id)
        )

        signal = result.scalars().first()
        if not signal:
            log.info(f"Signal with id {signal_id} not found")
            raise HTTPException(detail="Not Found", status_code=404)

        for name, value in request.model_dump().items():
            setattr(signal, name, value)

        await self.session.commit()
        return {"detail": "Updated Successfully"}

    async def _delete_signal(self, signal_id: int) -> dict:
        result = await self.session.execute(
            select(SignalModel).filter_by(user_id=self.current_user.id, id=signal_id)
        )
        signal = result.scalars().first()
        if not signal:
            log.warning("Signal not found")
            raise HTTPException(detail="Not Found", status_code=404)

        await self.session.delete(signal)
        await self.session.commit()
        log.warning(f"Signal {signal_id} deleted successfully")
        return {"detail": "Deleted Successfully"}

    async def _get_cached_data(self, cache_name: str):
        cache_key = f"{cache_name}"
        cached_data = await self.redis_client.get(cache_key)

        if cached_data:
            log.warn("Getting Data From Cache")
            return json.loads(cached_data)

        return None

    async def _get_signal_picture(self, filename: str):
        file_path = os.path.join(MEDIA_ROOT, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        async def file_streamer(file_path):
            async with aiofiles.open(file_path, mode="rb") as file:
                chunk_size = 1024 * 1024
                while chunk := await file.read(chunk_size):
                    yield chunk

        return StreamingResponse(file_streamer(file_path), media_type="image/jpg")
