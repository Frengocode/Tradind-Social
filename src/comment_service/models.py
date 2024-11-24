from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from src.config.comment_database import CommentBase


class CommentModel(CommentBase):
    __tablename__ = "comments"

    comment: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    news_id: Mapped[int] = mapped_column(Integer, nullable=True)
    signal_id: Mapped[int] = mapped_column(Integer, nullable=True)

