import os
from datetime import datetime
from typing import List

import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db_models.media_model import Media


async def create_media(
        session: AsyncSession,
        files: List[UploadFile],
        user_id: int
):
    path = MEDIA_PATH.format(user=user_id)

    if not os.path.exists(path):
        os.mkdir(path)
        # logger.debug(f"Created path: {path}")

    medias = []

    for file in files:
        timestamp = datetime.timestamp(datetime.now())
        # обработать filename
        # from werkzeug.utils import secure_filename
        # или написать свой вариант
        new_filename = "{:.4f}_{}".format(timestamp, file.filename)

        content = await file.read()
        async with aiofiles.open(
                file="".join(
                    [MEDIA_PATH.format(user=user_id), new_filename]
                ),
                mode="wb"
        ) as file_to_write:
            await file_to_write.write(content)

        media = Media(name=new_filename, path=path)
        medias.append(media)

    async with session.begin():
        session.add_all(medias)

    return medias