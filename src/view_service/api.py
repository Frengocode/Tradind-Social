from fastapi import Depends, APIRouter
from src.view_service.scheme import ViewResponse
from src.view_service.service import ViewService
from src.uitils.scheme import SUser
from src.auth_service.oauth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.view_database import get_views_session


view_service_router = APIRouter(tags=["View Service"], prefix="/view-service/api/v1")


@view_service_router.post("/create-view-for-signal/{signal_id}/")
async def create_view_for_signal(
    signal_id: int,
    session: AsyncSession = Depends(get_views_session),
    current_user: SUser = Depends(get_current_user),
):
    service = ViewService(session=session, current_user=current_user)
    return await service._create_view_for_signal(signal_id=signal_id)


@view_service_router.get(
    "/get-views-from-signal/{signal_id}/", response_model=list[ViewResponse]
)
async def get_view_from_signal(
    signal_id: int,
    session: AsyncSession = Depends(get_views_session),
    current_user: SUser = Depends(get_current_user),
):
    service = ViewService(session=session, current_user=current_user)
    return await service._get_view_from_signal(signal_id=signal_id)


@view_service_router.get("/get-views/", response_model=list[ViewResponse])
async def get_views(
    session: AsyncSession = Depends(get_views_session),
    current_user: SUser = Depends(get_current_user),
):
    service = ViewService(session=session, current_user=current_user)
    return await service._get_all_user_views()
