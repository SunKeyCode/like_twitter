from pydantic import BaseModel
from typing import List


class UserBaseModel(BaseModel):
    user_name: str


class LikeBaseModel(BaseModel):
    pass


class AuthorOfTweetModel(UserBaseModel):
    user_id: int

    class Config:
        orm_mode = True


class BriefInfoUserModel(UserBaseModel):
    user_id: int

    class Config:
        orm_mode = True


class CreateUserModel(UserBaseModel):
    first_name: str | None = None
    last_name: str | None = None


class UserInfoModel(BriefInfoUserModel):
    followers: List[BriefInfoUserModel]
    following: List[BriefInfoUserModel]

    class Config:
        orm_mode = True


class UserMainResponseModelBrief(BaseModel):
    result: bool = True
    user: UserInfoModel

    class Config:
        orm_mode = True


class LikeForTweetModel(LikeBaseModel):
    user_id: int
    user_name: str

    class Config:
        orm_mode = True


class AttachmentModel(BaseModel):
    path: str
    name: str
    media_id: int


class TweetBaseModel(BaseModel):
    content: str


class CreateTweetModelIn(TweetBaseModel):
    author_id: int
    tweet_media_ids: List[int] = []


class CreateTweetModelOut(BaseModel):
    result: bool
    tweet_id: int

    class Config:
        orm_mode = True


class TweetResponseModel(TweetBaseModel):
    tweet_id: int
    author: AuthorOfTweetModel
    likes: List[LikeForTweetModel] | None = []
    attachments: List[AttachmentModel]

    class Config:
        orm_mode = True


class MainTweetResponseModel(BaseModel):
    result: bool
    tweets: TweetResponseModel | List[TweetResponseModel] | None
