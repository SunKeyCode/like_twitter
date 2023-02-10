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
    user: BriefInfoUserModel

    class Config:
        orm_mode = True


class TweetBaseModel(BaseModel):
    content: str


class CreateTweetModel(TweetBaseModel):
    author_id: int
    picture_id: int | None = None


class TweetResponseModel(TweetBaseModel):
    tweet_id: int
    author: AuthorOfTweetModel | None = None
    likes: List[LikeForTweetModel] | None = None

    class Config:
        orm_mode = True
