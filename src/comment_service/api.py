from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.comment_service.service import CommentService
from src.comment_service.scheme import CreateCommentRequest, CommentResponse
from src.uitils.scheme import SUser
from src.config.comment_database import get_comment_session
from src.auth_service.oauth import get_current_user


comment_service_router = APIRouter(tags=["Comment Service"], prefix="/comment-service/api/v1")


@comment_service_router.post("/create-comment/")
async def create_comment(request: CreateCommentRequest, session: AsyncSession = Depends(get_comment_session), current_user: SUser = Depends(get_current_user)):
    service = CommentService(session=session, current_user=current_user)
    return await service._create_comment(request=request)


@comment_service_router.get("/get-comments-from-signal/{signal_id}/", response_model=list[CommentResponse])
async def get_comments_from_signal(signal_id: int, session: AsyncSession  = Depends(get_comment_session), current_user: SUser = Depends(get_current_user)):
    service = CommentService(session=session, current_user=current_user)
    return await service._get_comments_from_signal(signal_id=signal_id)


@comment_service_router.delete("/delete-comment/{comment_id}/")
async def delete_comment(comment_id: int, session: AsyncSession = Depends(get_comment_session), current_user: SUser = Depends(get_current_user)):
    service = CommentService(session=session, current_user=current_user)
    return await service._delete_comment(comment_id=comment_id)