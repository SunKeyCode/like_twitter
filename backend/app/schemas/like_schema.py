from pydantic import BaseModel, Field


class LikeBaseModel(BaseModel):
    pass


class LikeForTweetModel(LikeBaseModel):
    user_id: int
    name: str

    class Config:
        orm_mode = True
