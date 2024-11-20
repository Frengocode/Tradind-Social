from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from src.config.news_database import NewsBASE
from datetime import datetime


class NewsModel(NewsBASE):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    news_title: Mapped[str] = mapped_column(String, nullable=False)
    picture_of_news: Mapped[str] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    date_pub: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
