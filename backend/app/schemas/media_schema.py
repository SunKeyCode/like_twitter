from typing import List

from pydantic import BaseModel


class MediaBasModel(BaseModel):
    media_id: int


class AttachmentModel(BaseModel):
    link: str


class MediaModelOut(BaseModel):
    result: bool
    media_id: int
