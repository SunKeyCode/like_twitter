import logging
import time
from typing import List

from fastapi import FastAPI, status, HTTPException, UploadFile, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError
from logging_tree import printout

from models import Tweet
from database import async_session, async_engine
from schemas import (
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
    reformat_error,
)
import custom_exceptions
import crud
from config import DEBUG, TESTING
from logger import init_logger
from main import app

test_session = async_session()

if not TESTING:
    init_logger()

logger = logging.getLogger("main.routes")

# app = FastAPI()

storage = dict()

# printout()

logger.info("Application started.")


@app.get("/api/test/{user_id}")
async def get_usr_test(user_id: int):
    user = await crud.get_user_test(test_session, user_id)
    return user


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
        storage["current_user"] = await crud.read_user(user_id=1, session=session)
        logger.debug(f"current_user={storage['current_user']}")


@app.on_event("shutdown")
async def shutdown():
    await test_session.close()
    await async_engine.dispose()


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


@app.post("/api/tweets", tags=["tweets"], description="Creates new tweet",
          response_model=CreateTweetModelOut)
async def create_tweet(
        tweet_data: CreateTweetModelIn, session: AsyncSession = Depends(get_db_session)
):
    tweet = await crud.create_tweet(session=session, tweet_data=tweet_data)
    return reformat_any_response(key="tweet_id", value=tweet.tweet_id)


@app.delete("/api/tweets/{tweet_id}", tags=["tweets"])
async def delete_tweet(tweet_id: int, session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    await crud.delete_tweet(
        session=session, tweet_id=tweet_id, user_id=user.user_id
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


@app.post("/api/tweets/{tweet_id}/likes", description="Add like to tweet")
async def add_like(tweet_id: int, session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    await crud.create_like(session=session, tweet_id=tweet_id, user_id=user.user_id)
    return {"result": True}


@app.delete("/api/tweets/{tweet_id}/likes", status_code=status.HTTP_202_ACCEPTED)
async def delete_like(tweet_id: int, session: AsyncSession = Depends(get_db_session)):
    user = storage["current_user"]
    await crud.delete_like(session=session, tweet_id=tweet_id, user_id=user.user_id)
    return {"result": True}


@app.post("/api/medias")
async def add_medias(
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
