from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SignUpRequest(BaseModel):
    username: str
    password: str
    email: str
    bio: Optional[str] = None
    name: Optional[str] = None


class SUserResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str] = None
    name: Optional[str] = None
    joined_at: Optional[datetime] = None
    picture_url: Optional[str] = None

    class Config:
        from_attributes = True


class SUpdateUserComponents(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[str] = None
