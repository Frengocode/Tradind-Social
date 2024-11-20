from pydantic import BaseModel
from typing import Optional


class TokenData(BaseModel):
    accsess_token: Optional[str] = None
    type: Optional[str] = None
