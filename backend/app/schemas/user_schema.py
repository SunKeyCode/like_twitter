from typing import List

from pydantic import BaseModel, Field


class UserBaseModel(BaseModel):
    name: str = Field(alias="user_name")


class CreateUserModel(BaseModel):
    user_name: str
    first_name: str | None = None
    last_name: str | None = None
    password: str


class BriefInfoUserModel(UserBaseModel):
    id: int = Field(alias="user_id")

    class Config:
        orm_mode = True


class UserInfoModel(BriefInfoUserModel):
    followers: List[BriefInfoUserModel]
    following: List[BriefInfoUserModel]

    class Config:
        orm_mode = True


class UserMainResponseModel(BaseModel):
    result: bool = True
    user: UserInfoModel

    class Config:
        orm_mode = True
