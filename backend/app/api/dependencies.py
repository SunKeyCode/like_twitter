from logging import getLogger
from typing import Any, Callable

from fastapi import Depends, UploadFile
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import FlushError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.requests import Request

from configs import app_config
from crud import crud_user
from custom_exc.db_exception import DbIntegrityError
from custom_exc.no_user_found import NoUserFoundError
from db.session import async_session
from db_models.user_model import User

logger = getLogger("main.dependencies")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def get_db_session():
    try:
        async with async_session() as session:
            yield session
    except IntegrityError as exc:
        raise DbIntegrityError(exc.args)
    except FlushError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exc.args[0],
        )


async def get_user_by_jwt_token(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_db_session),
) -> User:
    """Authentication with JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if app_config.SECRET_KEY is None:
        raise JWTError("SECRET_KEY is not set")

    try:
        payload = jwt.decode(
            token, app_config.SECRET_KEY, algorithms=[app_config.ALGORITHM]
        )
        user_id = payload.get("user_id")
    except JWTError:
        print("jwt error")
        raise credentials_exception

    if user_id is None:
        raise credentials_exception

    user: User | None = await crud_user.read_user(user_id=user_id, session=db_session)

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_by_apikey(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """Authentication with api-key"""
    api_key = request.headers.mutablecopy().get("api-key")
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Api-key is omitted.",
        )
    if api_key == "test":
        api_key = "1"
    # TODO хранить api-key в базе

    try:
        user_id = int(api_key)
    except ValueError:
        raise NoUserFoundError

    user: User | None = await crud_user.read_user(
        session=session,
        include_relations=None,
        user_id=user_id,
    )

    if user is None:
        error_message = "Wrong api-key, user not found. ApiKey=%s, URL=%s" % (
            api_key,
            request.url,
        )
        logger.error(error_message)
        raise NoUserFoundError

    return user


def get_auth_dependency() -> Callable:
    if app_config.AUTH_CONFIG == "API-KEY":
        return get_current_user_by_apikey
    elif app_config.AUTH_CONFIG == "JWT":
        return get_user_by_jwt_token
    else:
        return get_current_user_by_apikey


async def get_current_user(curren_user=Depends(get_auth_dependency())) -> User:
    return curren_user


async def pagination(
    offset: int | None = None, limit: int | None = None
) -> dict[str, int | None]:
    """Pagination dependency"""
    if limit is None:
        offset = None
        return {"offset": offset, "limit": limit}

    if offset is not None:
        offset = limit * (offset - 1)
    else:
        offset = None

    return {"offset": offset, "limit": limit}


async def get_file(file: UploadFile) -> dict[str, Any]:
    """Uploads file considering file size constraint"""
    chunk = await file.read(1024)
    content: bytes = chunk
    real_size = len(chunk)

    while chunk := await file.read(1024):
        real_size += len(chunk)
        if real_size > app_config.MAX_IMG_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large",
            )
        content += chunk

    return {"content": content, "filename": file.filename}
