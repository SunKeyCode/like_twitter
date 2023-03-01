from pydantic import BaseModel


class LikeBaseModel(BaseModel):
    pass


class LikeForTweetModel(LikeBaseModel):
    user_id: int
    user_name: str

    class Config:
        orm_mode = True
