from pydantic import BaseModel
from typing import Optional


class SUser(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None

    @classmethod
    def __str__(self) -> str:
        return f"<User {self.username} {self.id} {self.email} >"

    token: Optional[str] = None
    picture_url: Optional[str] = None
