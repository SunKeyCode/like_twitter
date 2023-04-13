import os
from datetime import datetime
from logging import getLogger
from typing import Any

import aiofiles
from configs import app_config
from db_models.media_model import Media
from sqlalchemy.ext.asyncio import AsyncSession

logger = getLogger("main.crud_media")


async def create_media(
    session: AsyncSession,
    file_data: dict[str, Any],
    user_id: int,
) -> Media:
    link = "images/{user}/".format(user=user_id)

    if not os.path.exists(app_config.MEDIA_ROOT / link):
        os.mkdir(app_config.MEDIA_ROOT / link)
        logger.debug("Created path: %s", app_config.MEDIA_ROOT / link)

    timestamp = datetime.timestamp(datetime.now())

    new_filename = "{:.4f}_{}".format(timestamp, file_data["filename"])

    link = "".join([link, new_filename])

    async with aiofiles.open(
        file=app_config.MEDIA_ROOT / link,
        mode="wb",
    ) as file_to_write:
        await file_to_write.write(file_data["content"])

    media = Media(link=link)

    async with session.begin():
        session.add(media)

    return media
