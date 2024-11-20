from typing import Optional
from src.uitils.scheme import SUser
from src.signals_service.scheme import SignalResponse
from pydantic import BaseModel
from datetime import datetime


class ViewResponse(BaseModel):
    id: int
    signal: Optional[SignalResponse] = None
    user: Optional[SUser] = None
    viewed_at: datetime
