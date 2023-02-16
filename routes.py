import os
import time
from datetime import datetime
from typing import List

import aiofiles
from fastapi import FastAPI, Path, status, HTTPException, File, UploadFile, Depends
from fastapi.encoders import jsonable_encoder

from models import User, Tweet, Like, Media, MEDIA_PATH
from schemas import (
    CreateUserModel,
    CreateTweetModelIn,
    UserMainResponseModelBrief,
    MainTweetResponseModel,
    CreateTweetModelOut,
)
from custom_exceptions import DbIntegrityError
from utils import (
    reformat_tweet_response,
    reformat_response_iterable,
    reformat_any_response
)

app = FastAPI()

storage = dict()


@app.on_event("startup")
async def create_current_user():
    storage["current_user"] = await User.get_user(user=1)


@app.get("/api/users/{user_id}", response_model=UserMainResponseModelBrief,
         tags=["users"])
async def get_user(user_id: int):
    user = await User.get_user(user_id, include_relations="all")
    if user:
        return reformat_any_response(user, "user")
    else:
        pass
        #  raise


@app.post("/api/users", status_code=status.HTTP_201_CREATED, tags=["users"])
async def create_user(user_data: CreateUserModel):
    user = User(**user_data.dict())
    await user.add_user()
    return reformat_any_response(user.user_id, "user_id")


@app.post("/api/tweets", tags=["tweets"], description="Creates new tweet",
          response_model=CreateTweetModelOut)
async def create_tweet(tweet_data: CreateTweetModelIn):
    tweet_as_dict = tweet_data.dict()
    media = tweet_as_dict.pop("tweet_media_ids")
    tweet = Tweet(**tweet_as_dict)
    await tweet.add_tweet(media)

    return reformat_any_response(key="tweet_id", value=tweet.tweet_id)


@app.delete("/api/tweets/{tweet_id}", tags=["tweets"])
async def delete_tweet(tweet_id: int):
    user = storage["current_user"]
    if await Tweet.delete_tweet(tweet_id, user):
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
async def get_feed():
    user = storage["current_user"]
    tweets = await Tweet.feed(user.user_id)

    tweets_as_json = map(jsonable_encoder, tweets)

    return reformat_response_iterable(
        tweets_as_json,
        func=reformat_tweet_response,
        key_name="tweets"
    )


@app.post("/api/tweets/{tweet_id}/likes", description="Add like to tweet")
async def add_like(tweet_id: int):
    user = storage["current_user"]
    if await Like.add_like(tweet_id=tweet_id, user=user):
        return {"result": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="like exists"
        )


@app.delete("/api/tweets/{tweet_id}/likes", status_code=status.HTTP_202_ACCEPTED)
async def delete_like(tweet_id: int):
    user = storage["current_user"]
    if await Like.remove_like(tweet_id=tweet_id, user=user):
        return {"result": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="like not found"
        )


@app.post("/api/medias")
async def add_medias(files: List[UploadFile]):
    user = storage["current_user"]
    medias = []

    if not os.path.exists(MEDIA_PATH.format(user=user.user_id)):
        os.mkdir(MEDIA_PATH.format(user=user.user_id))

    for file in files:
        timestamp = datetime.timestamp(datetime.now())
        # обработать filename
        # from werkzeug.utils import secure_filename
        # или написать свой вариант
        new_filename = "{:.4f}_{}".format(timestamp, file.filename)

        media = Media(name=new_filename)
        await media.add(user=user)

        content = await file.read()
        async with aiofiles.open(
                file="".join(
                    [MEDIA_PATH.format(user=user.user_id), new_filename]
                ),
                mode="wb"
        ) as file_to_write:
            await file_to_write.write(content)

        medias.append(media)

    return {"result": True, "medias": medias}


@app.post("/api/users/{user_id}/follow")
async def follow_user(user_id: int):
    user = storage["current_user"]
    if await user.follow(user=user_id):
        return {"result": True}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="already followed"
        )


@app.delete("/api/users/{user_id}/follow")
async def unfollow_user(user_id: int):
    user = storage["current_user"]
    await user.unfollow(user=user_id)

    return {"result": True}
