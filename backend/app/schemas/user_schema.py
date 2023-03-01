from pydantic import BaseModel, Field
from typing import List


class UserBaseModel(BaseModel):
    user_name: str


class CreateUserModel(UserBaseModel):
    first_name: str | None = None
    last_name: str | None = None
    hashed_password: str


class BriefInfoUserModel(UserBaseModel):
    user_id: int

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
