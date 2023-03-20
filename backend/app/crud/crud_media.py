import os
import pathlib
from datetime import datetime
from typing import Any
from logging import getLogger

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from db_models.media_model import Media
from configs import app_config

logger = getLogger("main.crud_media")
# IMAGES_PATH = pathlib.Path().absolute().parents[1].as_posix() + "/static"
IMAGES_PATH = app_config.BASE_DIR.parents[1].as_posix() + "/static"


# TODO рассчитать путь до переменной и добавить ее в configs


async def create_media(
        session: AsyncSession,
        file_data: dict[str, Any],
        user_id: int
) -> Media:
    link = "/images/{user}/".format(user=user_id)

    if not os.path.exists(IMAGES_PATH + link):
        os.mkdir(IMAGES_PATH + link)
        logger.debug(f"Created path: {IMAGES_PATH + link}")

    timestamp = datetime.timestamp(datetime.now())
    # TODO обработать filename from werkzeug.utils import secure_filename
    # или написать свой вариант
    new_filename = "{:.4f}_{}".format(timestamp, file_data["filename"])
    link = "".join([link, new_filename])

    async with aiofiles.open(
            file="".join(
                [IMAGES_PATH, link]
            ),
            mode="wb"
    ) as file_to_write:
        await file_to_write.write(file_data["content"])

    media = Media(link=link)

    async with session.begin():
        session.add(media)

    return media
