import os
from logging import getLogger

from configs.app_config import DEBUG, MEDIA_ROOT
from db.base_class import Base
from sqlalchemy import Column, Identity, Integer, String, event

logger = getLogger("main.media_model")


class Media(Base):
    __tablename__ = "table_media"

    media_id = Column(Integer, Identity(always=True), primary_key=True)
    link = Column(String, nullable=False)


@event.listens_for(Media, "after_delete")
def after_delete_media(_, __, target):
    file_path = os.path.join(MEDIA_ROOT.as_posix(), target.link)
    try:
        os.remove(file_path)
        logger.debug("File '%s' deleted.", file_path)
    except FileNotFoundError as exc:
        if DEBUG:
            raise FileNotFoundError(exc)
        else:
            logger.error("File '%s' not found.", file_path)
