from pydantic import BaseModel, Field, validator
from schemas.user_schema import BriefInfoUserModel


class LikeBaseModel(BaseModel):
    pass


class LikeForTweetModel(LikeBaseModel):
    user_id: int
    name: BriefInfoUserModel = Field(alias="user")

    @validator("name")
    def extract_user_name_value(cls, user_model: BriefInfoUserModel) -> str:
        return user_model.name

    class Config:
        orm_mode = True
