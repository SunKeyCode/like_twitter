from api import utils
from api.dependencies import get_current_user, get_db_session, get_file
from crud import crud_media
from db_models.user_model import User
from fastapi import APIRouter, Depends
from schemas.media_schema import MediaModelOut
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter(prefix="/medias")


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MediaModelOut)
async def create_medias(
    file_data: dict = Depends(get_file),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    media = await crud_media.create_media(
        session=session, file_data=file_data, user_id=current_user.user_id
    )
    return utils.reformat_any_response(key="media_id", value=media.media_id)
