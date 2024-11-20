from fastapi import HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from src.news_service.models import NewsModel
from src.uitils.scheme import SUser
from src.news_service.scheme import NewsResponse
from sqlalchemy import select
from src.requests.request import GET_USER
from datetime  import datetime
import logging
import os
import uuid
import aiofiles
import httpx
import asyncio
import redis.asyncio as redis
import json

MEDIA_ROOT = "media/news_picture/"


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class CustomDateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)
    

class NewsService:
    def __init__(self, session: AsyncSession, current_user: SUser, redis_client: redis.StrictRedis = None):
        self._session = session
        self._current_user = current_user
        self._redis_client = redis_client


    async def _create_news(self, news_title: str, picture: UploadFile = File(...)):

        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(MEDIA_ROOT, filename)

        
        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await picture.read(1024):
                await out_file.write(content)
        log.info(f"News picture {filename} saved at {file_path}")

        news = NewsModel(
            news_title=news_title,
            user_id=self._current_user.id,
            picture_of_news=filename,
        )

        self._session.add(news)
        await self._session.commit()
        log.warn(f"<NewsObect id {news.id} {news.news_title} {news.user_id}")
        return {"detail": "News Created Succsesfully"}
    

    async def _get_all_news(self):
        news = (
            (
                await self._session.execute(
                    select(NewsModel).order_by(NewsModel.date_pub.desc())
                )
            )
            .scalars()
            .all()
        )

        user_data = {
            user["id"]: user
            for user in await asyncio.gather(
                *(
                    self._get_data_from_url(f"{GET_USER}/{new.user_id}/")
                    for new in news
                ),
                return_exceptions=True,
            )
            if isinstance(user, dict)
        }

        return [
            NewsResponse(
                **new.__dict__,
                user=(
                    SUser(**user_data[new.user_id])
                    if new.user_id in user_data
                    else None
                ),
            )
            for new in news
        ]

    async def _delete_news(self, news_id: int):

        news = (
            (
                await self._session.execute(
                    select(NewsModel).filter_by(
                        user_id=self._current_user.id, id=news_id
                    )
                )
            )
            .scalars()
            .first()
        )  


        if not news:
            log.warn(f"News Not Found {news_id}")
            raise HTTPException(detail="Not Found", status_code=404)



        await self._delete_picture(picture_name=news.picture_of_news)


        await self._session.delete(news)
        await self._session.commit()
        return {"detail": "Deleted Succsesfully"}
    

    async def _get_news(self, news_id: int):
        cached_data = await self._get_cached_data(cache_key=f"get-news-{news_id}")
        if cached_data:
            return NewsResponse(**cached_data)
        

        news = (
            (await self._session.execute(select(NewsModel).filter_by(id=news_id)))
            .scalars()
            .first()
        )

        if not news:
            raise HTTPException(detail="Not found", status_code=404)

        user_data = await self._get_data_from_url(f"{GET_USER}/{news.user_id}/")

        news_response = NewsResponse(
            **news.__dict__, user=SUser(**user_data if user_data else None)
        )

        await self._redis_client.setex(
            f"get-news-{news_id}",
            3600,
            json.dumps(news_response.dict(), cls=CustomDateTimeEncoder),
        )

        return news_response

    async def _get_data_from_url(self, url: str):
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {self._current_user.token}"},
            )

            return response.json() if response.status_code == 200 else None


    async def _get_cached_data(self, cache_key: str):
        cache_key = f"{cache_key}"
        cached_data = await self._redis_client.get(cache_key)
        if cached_data:
            log.warn(f"Returing News Data")
            return json.loads(cached_data)
        return None


    async def _delete_picture(self, picture_name: str):

        file_path = os.path.join(MEDIA_ROOT, str(picture_name))
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            log.warn(f"News OF picure not found for <NewsModel id {picture_name} >")