from sqlalchemy.ext.asyncio import AsyncSession
from src.uitils.scheme import SUser
from typing import Optional
import httpx
from sqlalchemy import select
from src.view_service.models import ViewModel
from fastapi import HTTPException
from src.requests.request import GET_SIGNAL, GET_USER
from src.view_service.scheme import ViewResponse, SignalResponse
import logging
import asyncio
import redis.asyncio as redis


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ViewService:

    def __init__(
        self,
        session: AsyncSession = None,
        current_user: SUser = None,
        redis_client: redis.StrictRedis = None,
    ):
        self._session = session
        self._current_user = current_user
        self._redis_client = redis_client

    async def _create_view_for_signal(self, signal_id: int):

        exist_view = (
            (
                await self._session.execute(
                    select(ViewModel).filter_by(
                        signal_id=signal_id, user_id=self._current_user.id
                    )
                )
            )
            .scalars()
            .first()
        )

        if exist_view:
            log.warning(f"Exist View For {signal_id}")
            raise HTTPException(
                detail=f"View allready created for {signal_id}", status_code=422
            )

        signal = await self._get_data_from_url(f"{GET_SIGNAL}/{signal_id}/")

        if not signal:
            logging.info("Signal Not Found")
            raise HTTPException(detail="Signal Not found", status_code=404)

        view = ViewModel(
            signal_id=signal_id,
            user_id=self._current_user.id,
        )

        self._session.add(view)
        await self._session.commit()
        log.info(f"Created Succsesfully for Signal {signal_id}")
        return {"detail": "View Created Succsesfully"}

    async def _get_view_from_signal(
        self, signal_id: int
    ) -> Optional[ViewResponse] | None:
        views = (
            (
                await self._session.execute(
                    select(ViewModel).filter_by(signal_id=signal_id)
                )
            )
            .scalars()
            .all()
        )

        user_data_map = {
            user["id"]: user
            for user in await asyncio.gather(
                *(
                    self._get_data_from_url(f"{GET_USER}/{view.user_id}/")
                    for view in views
                )
            )
            if user
        }

        return [
            ViewResponse(
                **view.__dict__,
                user=(
                    SUser(**user_data_map[view.user_id])
                    if view.user_id in user_data_map
                    else None
                ),
            )
            for view in views
        ]

    async def _get_all_user_views(self):

        views = (
            (
                await self._session.execute(
                    select(ViewModel)
                    .filter_by(user_id=self._current_user.id)
                    .order_by(ViewModel.viewed_at.desc())
                )
            )
            .scalars()
            .all()
        )

        if not views:
            return []

        signal_data_map = {
            signal["id"]: signal
            for signal in await asyncio.gather(
                *(
                    self._get_data_from_url(f"{GET_SIGNAL}/{view.signal_id}/")
                    for view in views
                )
            )
            if signal
        }

        return [
            ViewResponse(
                signal=SignalResponse(**(signal_data_map.get(view.signal_id) or {})),
                **view.__dict__,
            )
            for view in views
        ]

    async def _get_data_from_url(self, url: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {self._current_user.token}"},
            )
        return response.json() if response.status_code == 200 else None
