import os
from logging import getLogger

from sqlalchemy import Column, Integer, String, Identity, event

from db.base_class import Base
from configs.app_config import MEDIA_ROOT, DEBUG

logger = getLogger("main.media_model")


class Media(Base):
    __tablename__ = "table_media"

    media_id: int = Column(Integer, Identity(always=True), primary_key=True)
    link: str = Column(String, nullable=False)


@event.listens_for(Media, "after_delete")
def after_delete_media(_, __, target):
    file_path = os.path.join(MEDIA_ROOT.as_posix(), target.link)
    try:
        os.remove(file_path)
        logger.debug(f"File '{file_path}' deleted.")
    except FileNotFoundError as exc:
        if DEBUG:
            raise FileNotFoundError(exc)
        else:
            logger.error(f"File '{file_path}' not found.")
