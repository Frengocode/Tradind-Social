from src.config.user_database import UserBS
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime


class UserModel(UserBS):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[str] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    picture_url: Mapped[str] = mapped_column(String, nullable=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())
    password: Mapped[str] = mapped_column(String, nullable=False)
