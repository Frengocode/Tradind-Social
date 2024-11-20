from sqlalchemy.orm import Mapped, mapped_column, validates
from sqlalchemy import String, Integer, DateTime
from datetime import datetime
from src.config.signals_database import SignalBASE


class SignalModel(SignalBASE):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    signal_picture: Mapped[str] = mapped_column(String, nullable=False)
    signal_for_coin: Mapped[str] = mapped_column(String, nullable=False)
    short_or_long: Mapped[str] = mapped_column(String, nullable=False)
    when: Mapped[datetime] = mapped_column(DateTime)
    when_end: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow())

    ### Other Params

    user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    @validates("when", "when_end", "created_at")
    def convert_naive(self, key, value):
        if isinstance(value, datetime) and value.tzinfo is not None:
            return value.replace(tzinfo=None)
        return value
