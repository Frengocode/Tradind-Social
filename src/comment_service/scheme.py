from pydantic import BaseModel
from src.uitils.scheme import SUser
from typing import Optional
from datetime import datetime


class CreateCommentRequest(BaseModel):
    comment: str
    news_id: int = None
    signal_id: int = None


class CommentResponse(BaseModel):
    id: int
    user: Optional[SUser] = None
    signal_id: Optional[int] = None
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
