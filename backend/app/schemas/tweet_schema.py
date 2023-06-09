from typing import List

from pydantic import BaseModel, Field, validator

from schemas import like_schema, media_schema, user_schema


class TweetBaseModel(BaseModel):
    content: str


class CreateTweetModelIn(BaseModel):
    content: str = Field(alias="tweet_data")
    tweet_media_ids: List[int] = []


class CreateTweetModelOut(BaseModel):
    result: bool
    tweet_id: int

    class Config:
        orm_mode = True


class TweetFullInfoModel(TweetBaseModel):
    id: int = Field(alias="tweet_id")
    author: user_schema.BriefInfoUserModel
    likes: List[like_schema.LikeForTweetModel] = []
    attachments: List[media_schema.AttachmentModel] = []

    @validator("attachments")
    def extract_link(cls, attachments: List[media_schema.AttachmentModel]) -> list[str]:
        return [attachment.link for attachment in attachments]

    class Config:
        orm_mode = True


class TweetsResponseModel(BaseModel):
    result: bool
    tweets: List[TweetFullInfoModel] | None
