from pydantic import BaseModel, Field
from typing import List

from schemas import user_schema, media_schema, like_schema


class TweetBaseModel(BaseModel):
    content: str


class CreateTweetModelIn(TweetBaseModel):
    tweet_media_ids: List[int] = []


class CreateTweetModelOut(BaseModel):
    result: bool
    tweet_id: int

    class Config:
        orm_mode = True


class TweetFullInfoModel(TweetBaseModel):
    tweet_id: int
    author: user_schema.BriefInfoUserModel
    likes: List[like_schema.LikeForTweetModel] | None = []
    attachments: List[media_schema.AttachmentModel]

    class Config:
        orm_mode = True


class TweetsResponseModel(BaseModel):
    result: bool
    tweets: List[TweetFullInfoModel] | None
