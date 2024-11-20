from pydantic import BaseModel
from src.uitils.scheme import SUser
from typing import Optional
from datetime import datetime


class BaseNewsSchema(BaseModel):
    news_title: Optional[str] = None


class NewsResponse(BaseNewsSchema):
    id: int
    user: Optional[SUser] = None
    picture_of_news: Optional[str] = None
    date_pub: datetime
