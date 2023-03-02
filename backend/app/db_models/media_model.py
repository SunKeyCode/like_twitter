from sqlalchemy import Column, Integer, String, Identity

from db.base_class import Base


class Media(Base):
    __tablename__ = "table_media"

    media_id: int = Column(Integer, Identity(always=True), primary_key=True)
    # name: str = Column(String, nullable=False)
    # path: str = Column(String, nullable=False)
    link: str = Column(String, nullable=False)
