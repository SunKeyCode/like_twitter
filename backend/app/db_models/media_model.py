from sqlalchemy import Column, Integer, String, Identity

from db.base_class import Base

MEDIA_PATH = "static/images/{user}/"


class Media(Base):
    __tablename__ = "table_media"

    media_id: int = Column(Integer, Identity(always=True), primary_key=True)
    name: str = Column(String, nullable=False)
    path: str = Column(String, default=MEDIA_PATH.format(user="unknown_user"))
