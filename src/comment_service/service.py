from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from src.comment_service.models import CommentModel
from src.uitils.scheme import SUser
from src.comment_service.scheme import CreateCommentRequest, CommentResponse
from src.requests.request import GET_SIGNAL, GET_USER
from src.uitils.uitils import log
from sqlalchemy import select
import redis.asyncio as redis
import httpx
import asyncio


class CommentService:
    def __init__(self, session: AsyncSession = None, current_user: SUser = None, redis_client: redis.StrictRedis = None):
        self._redis_client = redis_client
        self._session = session
        self._current_user = current_user

    

    async def _create_comment(self, request: CreateCommentRequest):
        signal_data = await self._get_data_from_url(f"{GET_SIGNAL}/{request.signal_id}/")
        if signal_data is None:
            raise HTTPException(
                detail="Signal Not Found",
                status_code=404
            )


        comment = CommentModel(

            comment = request.comment,
            user_id = self._current_user.id,
            signal_id = signal_data.get("id")

        )

        log.info(f"<Comment id - {comment.id}, user_id - {comment.user_id}, created_at - {comment.created_at} ")


        self._session.add(comment)
        await self._session.commit()

    async def _get_comments_from_signal(self, signal_id: int):
        
        comments = (await self._session.execute(
            select(CommentModel)
            .filter_by(signal_id = signal_id)
            .order_by(CommentModel.created_at.desc())
        )).scalars().all()
        

        if not comments:
            return []
        
        
        user_data = {
            user["id"]: user
            for user in await asyncio.gather(
                *(
                    self._get_data_from_url(f"{GET_USER}/{comment.user_id}/")
                    for comment in comments
                ),
                return_exceptions=True,
            )
            if isinstance(user, dict)
        }


        return [
            CommentResponse(
                **comment.__dict__,
                user = SUser(**user_data[comment.user_id])

            )
            for comment in comments
        ]
    
    async def _delete_comment(self, comment_id: int):
        comment = (await self._session.execute(
            select(CommentModel)
            .filter_by(id = comment_id, user_id = self._current_user.id)
        )).scalars().first()

        if not comment:
            log.warning("Comment Not Found")
            raise HTTPException(
                detail="Not Found",
                status_code=404
            )
        
        log.info(f"Comment Deleted Succsesfully")
        log.info(f"<<< id -- {comment.id}")

        await self._session.delete(comment)
        await self._session.commit()



    async def _get_data_from_url(self, url: str):
        async with httpx.AsyncClient(timeout=httpx.Timeout(15.0)) as client:
            response = await client.get(url=url, headers={"Authorization": f"Bearer {self._current_user.token}"})
            if response is not None:
                log.info(f"Data {response.json()}")
                return response.json()
            return None        