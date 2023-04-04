from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dependencies import get_db_session, get_current_user_by_apikey, get_file
from db_models.user_model import User
from schemas.media_schema import MediaModelOut
from crud import crud_media
from api import utils

router = APIRouter(prefix="/medias")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MediaModelOut)
async def create_medias(
        file_data: dict = Depends(get_file),
        session: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_user_by_apikey)
) -> dict[str, int]:
    media = await crud_media.create_media(
        session=session,
        file_data=file_data,
        user_id=current_user.user_id
    )
    return utils.reformat_any_response(key="media_id", value=media.media_id)
