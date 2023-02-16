import os
from datetime import datetime
from typing import List

import aiofiles
from fastapi import FastAPI, status, HTTPException, UploadFile, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import FlushError

from models import User, Tweet, Like, Media, MEDIA_PATH
from database import async_session
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
    reformat_any_response
)
import crud

app = FastAPI()

storage = dict()


async def get_db_session():
    try:
        async with async_session() as session:
            yield session
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.args
        )
    except FlushError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.args
        )


@app.on_event("startup")
async def get_current_user():
    storage["current_user"] = await crud.read_user(user_id=1, session=async_session())


@app.get("/api/users/{user_id}", response_model=UserMainResponseModelBrief,
         tags=["users"])
async def get_user(user_id: int, session: AsyncSession = Depends(get_db_session)):
    user = await crud.read_user(
        session=session, user_id=user_id, include_relations="all"
    )
    if user:
        return reformat_any_response(user, "user")
    else:
        pass
        #  raise


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
    if await crud.delete_tweet(
            session=session, tweet_id=tweet_id, user_id=user.user_id
    ):
        return {"result": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="tweet not found"
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
    await crud.remove_like(session=session, tweet_id=tweet_id, user_id=user.user_id)
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
