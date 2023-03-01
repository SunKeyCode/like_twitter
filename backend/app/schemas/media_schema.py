from pydantic import BaseModel


class AttachmentModel(BaseModel):
    path: str
    name: str
    media_id: int
