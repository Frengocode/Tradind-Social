from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.uitils.scheme import SUser


class SignalResponse(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    signal_picture: Optional[str] = None
    signal_for_coin: Optional[str] = None
    created_at: Optional[datetime] = None
    when: Optional[datetime] = None
    when_end: Optional[datetime] = None
    short_or_long: Optional[str] = None
    user_id: Optional[int] = None
    user: Optional[SUser] = None


class UpdateSignalRequest(BaseModel):
    title: str
    signal_for_coin: str
    when: datetime
    when_end: datetime
    short_or_long: str
