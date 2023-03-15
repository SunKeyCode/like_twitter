from typing import List

from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dependencies import get_db_session, get_current_user_by_apikey
from db_models.user_model import User
from db_models.media_model import Media
from schemas.media_schema import MediaModelOut
from crud import crud_media
from api import utils

router = APIRouter(prefix="/medias")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MediaModelOut)
async def create_medias(
        file: List[UploadFile],
        session: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_user_by_apikey)
) -> dict[str, int]:
    medias = await crud_media.create_media(
        session=session,
        files=file,
        user_id=current_user.user_id
    )
    if len(medias) == 1:
        return utils.reformat_any_response(key="media_id", value=medias[0].media_id)
    # TODO дописать возвращаемое значение если несколько файлов
    return medias
