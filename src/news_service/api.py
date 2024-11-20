from fastapi import APIRouter, Depends, File, UploadFile, Form
from src.news_service.service import NewsService
from src.news_service.scheme import NewsResponse
from src.uitils.scheme import SUser
from src.auth_service.oauth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from src.config.news_database import get_news_session
import redis.asyncio as redis


def get_redis_client() -> redis.StrictRedis:
    return redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)


news_service_router = APIRouter(tags=["News Service"], prefix="/news-service/api/v1")


@news_service_router.post("/create-news/")
async def create_news(
    news_title: str = Form(...),
    news_picture: UploadFile = File(...),
    session: AsyncSession = Depends(get_news_session),
    current_user: SUser = Depends(get_current_user),
):
    service = NewsService(session=session, current_user=current_user)
    return await service._create_news(news_title=news_title, picture=news_picture)


@news_service_router.get("/get-all-news/", response_model=list[NewsResponse])
async def get_all_news(
    session: AsyncSession = Depends(get_news_session),
    current_user: SUser = Depends(get_current_user),
):
    service = NewsService(session=session, current_user=current_user)
    return await service._get_all_news()


@news_service_router.get("/get-news/{news_id}/", response_model=NewsResponse)
async def get_news(
    news_id: int,
    session: AsyncSession = Depends(get_news_session),
    current_user: SUser = Depends(get_current_user),
    redis_client: redis.StrictRedis = Depends(get_redis_client),
):
    service = NewsService(
        session=session, current_user=current_user, redis_client=redis_client
    )
    return await service._get_news(news_id=news_id)


@news_service_router.delete("/delete-news/{news_id}/")
async def delete_news(
    news_id: int,
    session: AsyncSession = Depends(get_news_session),
    current_user: SUser = Depends(get_current_user),
):
    service = NewsService(session=session, current_user=current_user)
    return await service._delete_news(news_id=news_id)
