from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import Integer, DateTime
from datetime import datetime
from src.config.view_database import ViewBASE


class ViewModel(ViewBASE):
    __tablename__ = "views"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    news_id: Mapped[int] = mapped_column(Integer, nullable=True)
    signal_id: Mapped[int] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    @validates
    async def validate_data(self):
        pass
