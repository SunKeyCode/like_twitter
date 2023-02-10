from typing import List

from fastapi import FastAPI, Path, status

from models import User, Tweet, Like
from schemas import (
    CreateUserModel,
    CreateTweetModel,
    TweetResponseModel,
    UserMainResponseModelBrief
)
from custom_exceptions import DbIntegrityError

app = FastAPI()

storage = dict()


# current_user = None


@app.on_event("startup")
async def create_current_user():
    storage["current_user"] = await User.get_user(user_id=1)


@app.get("/api/users/{user_id}", response_model=UserMainResponseModelBrief)
async def get_user(user_id: int):
    user: User = await User.get_user(user_id=user_id)
    followers = await user.get_followers()
    following = await user.user_follows()

    extended_user_data = user.to_json()
    extended_user_data["followers"] = followers
    extended_user_data["following"] = following

    return {"result": True, "user": extended_user_data}


@app.post("/api/users", status_code=status.HTTP_201_CREATED)
async def create_user(user_data: CreateUserModel):
    user = User(**user_data.dict())
    await user.add_user()
    return user


@app.post("/api/tweets")
async def create_tweet(tweet_data: CreateTweetModel):
    tweet = Tweet(**tweet_data.dict())
    await tweet.add_tweet()
    return tweet


@app.delete("/api/tweets/{tweet_id}")
async def delete_tweet(tweet_id: int):
    pass


@app.get("/api/tweets/{tweet_id}", response_model=TweetResponseModel | None)
async def get_tweet(tweet_id: int):
    tweet = await Tweet.tweet_by_id(tweet_id)
    # доделать response_model, чтобы было как в тз
    return tweet


@app.get("/api/tweets", response_model=List[TweetResponseModel])
async def get_tweets():
    user = storage["current_user"]
    users = await user.user_follows(only_id=True)
    tweets = await Tweet.tweets_list(users)

    response = {"result": True}
    # reformatted_tweets = []
    for tweet in tweets:
        # превратить в json через pydantic и реформатировать
        print(tweet.to_json())

    return tweets


@app.post("/api/tweets/{tweet_id}/likes")
async def add_like(tweet_id: int):
    user = storage["current_user"]
    like = Like(user_id=user.user_id, tweet_id=tweet_id)
    try:
        await like.add_like()
    except DbIntegrityError as exc:
        return {"result": False, "message": exc.args[0]}
        #     ??????????????????????????????????????????
    return {"result": True}


@app.delete("/api/tweets/{tweet_id}/likes")
async def delete_like(tweet_id: int):
    user = storage["current_user"]
    deleted_row = await Like.remove_like(tweet_id=tweet_id, user_id=user.user_id)
    if deleted_row:
        return {"result": True}
    else:
        return {"result": False, "message": "there is no such row"}


@app.post("/api/users/{user_id}/follow")
async def follow_user(user_id: int):
    user = storage["current_user"]
    success = await user.follow(user=user_id)
    if success:
        return {"result": True}


@app.get("/api/")
async def root():
    return {"message": "Hello World"}
