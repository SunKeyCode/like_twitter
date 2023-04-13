from datetime import datetime, timedelta

from configs import app_config
from jose import jwt, JWTError
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: str, hashed_password: str) -> bool:
    return password_context.verify(secret=password, hash=hashed_password)


def get_hash(password: str) -> str:
    return password_context.hash(secret=password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(
        minutes=int(app_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    if app_config.SECRET_KEY is None:
        raise JWTError("SECRET_KEY is not set")

    return jwt.encode(
        claims=to_encode, key=app_config.SECRET_KEY, algorithm=app_config.ALGORITHM
    )
