from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from typing import AnyStr
from datetime import datetime, timedelta
import logging
import colorlog


ACCESS_TOKEN_EXPIRE_DAYS = 50
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth-login/")


pwd_password = CryptContext(schemes=["bcrypt"])


class Hash:

    def bcrypt(password: str) -> AnyStr:
        return pwd_password.hash(password)

    def verify(plain_password: str, hashed_password: str) -> bool:
        return pwd_password.verify(plain_password, hashed_password)


class AuthUitils:

    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt



log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

handler = colorlog.StreamHandler()

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    log_colors={
        'DEBUG': 'blue',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
)

handler.setFormatter(formatter)

log.addHandler(handler)