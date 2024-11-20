from fastapi import APIRouter, Depends, UploadFile, File, Form
from src.signals_service.models import SignalModel
from src.uitils.scheme import SUser
from src.signals_service.service import (
    SignalResponse,
    SignalService,
    UpdateSignalRequest,
)
from src.config.signals_database import get_signal_session, AsyncSession
from typing import Type, Optional
from datetime import datetime
from src.auth_service.oauth import get_current_user
import redis.asyncio as redis


def get_redis_client() -> redis.StrictRedis:
    return redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)


signal_service = APIRouter(tags=["Signal Service"], prefix="/signal/service/api/v1")


@signal_service.post("/create-signal/", response_model=SignalResponse)
async def create_signal(
    short_or_long: str = Form(...),
    signal_picture: UploadFile = File(...),
    title: str = Form(...),
    signal_for_coin: str = Form(...),
    when: datetime = Form(...),
    when_end: datetime = Form(...),
    session: AsyncSession = Depends(get_signal_session),
    current_user: SUser = Depends(get_current_user),
) -> Type[SignalModel]:

    service = SignalService(session=session, current_user=current_user)

    return await service._create_signal(
        short_or_long=short_or_long,
        signal_for_coin=signal_for_coin,
        signal_picture=signal_picture,
        title=title,
        when=when,
        when_end=when_end,
    )


@signal_service.get("/get-all-signals/", response_model=list[SignalResponse])
async def get_signals(
    session: AsyncSession = Depends(get_signal_session),
    current_user: SUser = Depends(get_current_user),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
) -> Optional[list[SignalResponse]] | None:
    service = SignalService(
        session=session, current_user=current_user, redis_client=redis_client
    )
    return await service._get_all_signals()


@signal_service.get("/get-user-signals/{user_id}/", response_model=list[SignalResponse])
async def get_user_signals(
    user_id: int,
    session: AsyncSession = Depends(get_signal_session),
    redis_cliten: redis.Redis = Depends(get_redis_client),
    current_user: SUser = Depends(get_current_user),
):
    service = SignalService(session=session, redis_client=redis_cliten)
    return await service._get_user_signals(user_id=user_id)


@signal_service.get("/get-signal/{signal_id}/", response_model=SignalResponse)
async def get_signal(
    signal_id: int,
    session: AsyncSession = Depends(get_signal_session),
    current_user: SUser = Depends(get_current_user),
    redis_cliten: redis.Redis = Depends(get_redis_client),
):
    service = SignalService(
        session=session, current_user=current_user, redis_client=redis_cliten
    )
    return await service._get_signal(signal_id=signal_id)


@signal_service.patch("/update-signal/{signal_id}/")
async def update_signal(
    signal_id: int,
    request: UpdateSignalRequest,
    session: AsyncSession = Depends(get_signal_session),
    current_user: SUser = Depends(get_current_user),
):

    service = SignalService(session=session, current_user=current_user)
    return await service._update_signal_obj(signal_id, request)


@signal_service.delete("/delete-signal/{signal_id}/")
async def delete_signal_obj(
    signal_id: int,
    session: AsyncSession = Depends(get_signal_session),
    current_user: SUser = Depends(get_current_user),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    service = SignalService(session=session, current_user=current_user, redis_client=redis_client)
    return await service._delete_signal(signal_id=signal_id)


@signal_service.get("/get-signal-picture/{filename}/")
async def get_picture(filename: str):
    service = SignalService()
    return await service._get_signal_picture(filename=filename)
