import os
import pathlib
from datetime import datetime
from typing import List
from logging import getLogger

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db_models.media_model import Media


logger = getLogger("main.crud_media")
IMAGES_PATH = pathlib.Path().absolute().parents[1].as_posix() + "/static"


# TODO рассчитать путь до переменной и добавить ее в configs

async def create_media(
        session: AsyncSession,
        files: List[UploadFile],
        user_id: int
) -> list[Media]:
    link = "/images/{user}/".format(user=user_id)

    if not os.path.exists(IMAGES_PATH + link):
        os.mkdir(IMAGES_PATH + link)
        logger.debug(f"Created path: {IMAGES_PATH + link}")

    medias = []

    for file in files:
        timestamp = datetime.timestamp(datetime.now())
        # TODO обработать filename from werkzeug.utils import secure_filename
        # или написать свой вариант
        new_filename = "{:.4f}_{}".format(timestamp, file.filename)
        link = "".join([link, new_filename])
        print(link)
        content = await file.read()
        async with aiofiles.open(
                file="".join(
                    [IMAGES_PATH, link]
                ),
                mode="wb"
        ) as file_to_write:
            await file_to_write.write(content)

        media = Media(link=link)
        medias.append(media)

    async with session.begin():
        session.add_all(medias)

    return medias
