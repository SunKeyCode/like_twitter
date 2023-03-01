from typing import List

from fastapi import APIRouter, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.dependencies import get_db_session, get_current_user_by_apikey
from db_models.user_model import User
from crud import crud_media

router = APIRouter(prefix="/medias")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_medias(
        files: List[UploadFile],
        session: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_user_by_apikey)
):
    medias = await crud_media.create_media(
        session=session,
        files=files,
        user_id=current_user.user_id
    )

    return medias
