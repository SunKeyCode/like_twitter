import logging
import pathlib
from typing import List
from datetime import datetime, timedelta

from fastapi import status, HTTPException, UploadFile, Depends, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from models import Tweet, create_all, User
from database import async_session, async_engine
from _schemas import (
    CreateUserModel,
    CreateTweetModelIn,
    UserMainResponseModelBrief,
    MainTweetResponseModel,
    CreateTweetModelOut,
)
from utils import (
    reformat_tweet_response,
    reformat_response_iterable,
    reformat_any_response,
)
import custom_exceptions
import _crud
from configs.config import DEBUG, TESTING
from logger import init_logger

if TESTING != "True":
    init_logger()

logger = logging.getLogger("main.routes_")

app = FastAPI()

storage = dict()

logger.info(f"Application started at {pathlib.Path.cwd()}")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")


async def get_db_session():
    try:
        async with async_session() as session:
            yield session
    except IntegrityError as exc:
        raise custom_exceptions.DbIntegrityError(exc.args)
    except FlushError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.args
        )


# async def _get_current_user(token: str = Depends(oauth2_scheme),
#                             session: AsyncSession = Depends(get_db_session),
#                             include_relation: str | None = None):
#     if token in storage and storage[token]["exp_date"] > datetime.now():
#         # user_id = storage[token]["user_id"]  # получить user_id из токена
#         user_id = 1
#         user = await crud.read_user(
#             session=session,
#             include_relations=include_relation,
#             user_id=int(user_id)
#         )
#         return user
#     else:
#         return None


# для тестов
async def get_current_user(session: AsyncSession = Depends(get_db_session),
                           include_relation: str | None = None):
    user_id = 1
    user = await crud.read_user(
        session=session,
        include_relations=include_relation,
        user_id=int(user_id)
    )
    return user


@app.exception_handler(HTTPException)
async def http_exceptions_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "http_exception",
                "error_message": exc.detail,
            }
        )
    )


@app.exception_handler(custom_exceptions.NoUserFoundError)
async def no_user_found_handler(_, exc: custom_exceptions.NoUserFoundError):
    # сделать объект ErrorMessage через дата класс???
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "No user found error",
                "error_message": exc.error_message,
            }
        )
    )


@app.exception_handler(custom_exceptions.DbIntegrityError)
async def integrity_error_handler(_, exc: custom_exceptions.DbIntegrityError):
    logger.error(f"Integrity error: {exc.error_message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "DbIntegrityError",
                "error_message": exc.error_message,
            }
        )
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "RequestValidationError",
                "error_message": exc.errors() if DEBUG else "wrong input field(s)",
            }
        )
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(_, exc: Exception):
    # logger.error(f"Unexpected error:", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "Exception",
                "error_message": "Unexpected server error",
            }
        )
    )


@app.on_event("startup")
async def startup():
    async with async_session() as session:
        if TESTING == 'True':
            await create_all()
        storage["current_user"] = await crud.read_user(user_id=1, session=session)
        logger.debug(f"current_user={storage['current_user']}")


@app.on_event("shutdown")
async def shutdown():
    await async_engine.dispose()


@app.post("/api/auth")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
                session: AsyncSession = Depends(get_db_session)):
    user = await crud.read_user_by_auth_data(
        session=session, user_name=form_data.username, password=form_data.password
    )
    if user:
        storage[str(user.user_id)] = {
            "user_id": user.user_id,
            "exp_date": datetime.now() + timedelta(minutes=10)
        }
        return {"access_token": user.user_id, "token_type": "bearer"}
    return False


@app.get("/api/users/me")
# async def show_me(curren_user=Depends(get_current_user)):
async def show_me(curren_user=Depends(get_current_user)):
    if curren_user:
        return reformat_any_response(key="user", value=curren_user)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )


@app.get("/api/users/{user_id}", response_model=UserMainResponseModelBrief,
         tags=["users"])
async def get_user(user_id: int, session: AsyncSession = Depends(get_db_session)):
    user = await crud.read_user(
        session=session, user_id=user_id, include_relations="all"
    )
    if user:
        return reformat_any_response(user, "user")
    else:
        raise custom_exceptions.NoUserFoundError(user_id)


@app.post("/api/users", status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(
        user_data: CreateUserModel,
        session: AsyncSession = Depends(get_db_session)
):
    user = await crud.create_user(session=session, user_data=user_data)

    return reformat_any_response(user.user_id, "user_id")


@app.post(
    "/api/tweets",
    tags=["tweets"],
    description="Creates new tweet",
    response_model=CreateTweetModelOut,
    status_code=status.HTTP_201_CREATED
)
async def create_tweet(
        tweet_data: CreateTweetModelIn,
        session: AsyncSession = Depends(get_db_session),
        current_user=Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"You are not authenticated user"}
        )

    tweet = await crud.create_tweet(
        session=session,
        tweet_data=tweet_data,
        author=current_user
    )
    return reformat_any_response(key="tweet_id", value=tweet.tweet_id)


@app.delete("/api/tweets/{tweet_id}", tags=["tweets"])
async def delete_tweet(
        tweet_id: int,
        session: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_user)
):
    result = await crud.delete_tweet(
        session=session, tweet_id=tweet_id, user_id=current_user.user_id
    )
    if result:
        return {"result": result}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tweet does not exists or belongs another user"
        )


@app.get("/api/tweets/{tweet_id}", response_model=MainTweetResponseModel,
         tags=["tweets"])
async def get_tweet(tweet_id: int):
    tweet = await Tweet.tweet_by_id(tweet_id)

    return reformat_response_iterable(
        [jsonable_encoder(tweet)],
        func=reformat_tweet_response,
        key_name="tweets"
    )


@app.get("/api/tweets", response_model=MainTweetResponseModel, tags=["feed"])
async def get_feed(session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    tweets = await crud.read_feed(session=session, user_id=user.user_id)

    tweets_as_json = map(jsonable_encoder, tweets)

    return reformat_response_iterable(
        tweets_as_json,
        func=reformat_tweet_response,
        key_name="tweets"
    )


@app.post(
    "/api/tweets/{tweet_id}/likes",
    description="Add like to tweet",
    status_code=status.HTTP_201_CREATED
)
async def add_like(tweet_id: int, session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    await crud.create_like(session=session, tweet_id=tweet_id, user_id=user.user_id)
    return {"result": True}


@app.delete("/api/tweets/{tweet_id}/likes", status_code=status.HTTP_202_ACCEPTED)
async def delete_like(tweet_id: int, session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    await crud.delete_like(session=session, tweet_id=tweet_id, user_id=user.user_id)
    return {"result": True}


@app.post("/api/medias", status_code=status.HTTP_201_CREATED)
async def create_medias(
        files: List[UploadFile], session: AsyncSession = Depends(get_db_session)
):
    user = storage["current_user"]
    medias = await crud.create_media(
        session=session,
        files=files,
        user_id=user.user_id
    )

    return medias


@app.post("/api/users/{user_id}/follow")
async def follow_user(user_id: int, session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    await crud.follow_user(session=session, user_who_follow=user, user_id=user_id)

    return {"result": True}


@app.delete("/api/users/{user_id}/follow")
async def unfollow_user(user_id: int, session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    await crud.unfollow(session=session, user_who_unfollow=user, user_id=user_id)

    return {"result": True}
