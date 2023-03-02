import os
import pathlib
from datetime import datetime
from typing import List

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db_models.media_model import Media

# IMAGES_PATH = pathlib.Path().absolute().parents[1].as_posix() + "/static/images/{user}/"
IMAGES_PATH = pathlib.Path().absolute().parents[1].as_posix() + "/static"


# LINK =

async def create_media(
        session: AsyncSession,
        files: List[UploadFile],
        user_id: int
):
    link = "/images/{user}".format(user=user_id)

    # path = IMAGES_PATH.format(user=user_id)

    if not os.path.exists(IMAGES_PATH + link):
        os.mkdir(IMAGES_PATH + link)
        # logger.debug(f"Created path: {path}")

    medias = []

    for file in files:
        timestamp = datetime.timestamp(datetime.now())
        # обработать filename
        # from werkzeug.utils import secure_filename
        # или написать свой вариант
        new_filename = "{:.4f}_{}".format(timestamp, file.filename)
        link = "".join([link, new_filename])

        content = await file.read()
        async with aiofiles.open(
                file="".join(
                    # [IMAGES_PATH.format(user=user_id), new_filename]
                    [IMAGES_PATH, link]
                ),
                mode="wb"
        ) as file_to_write:
            await file_to_write.write(content)

        # media = Media(name=new_filename, path=path)
        media = Media(link=link)
        medias.append(media)

    async with session.begin():
        session.add_all(medias)

    return medias
