from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies, utils
from db_models.user_model import User
from schemas import user_schema
from crud import crud_user
from custom_exc.no_user_found import NoUserFoundError

router = APIRouter(prefix="/users")


@router.get("/me")
async def show_me(curren_user: User = Depends(dependencies.get_current_user_by_apikey)):
    if curren_user:
        return utils.reformat_any_response(key="user", value=curren_user)
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )


@router.get("/{user_id}", response_model=user_schema.UserMainResponseModel)
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(dependencies.get_db_session)
):
    user = await crud_user.read_user(
        session=session, user_id=user_id, include_relations="all"
    )
    if user:
        return utils.reformat_any_response(user, "user")
    else:
        raise NoUserFoundError(user_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
        user_data: user_schema.CreateUserModel,
        session: AsyncSession = Depends(dependencies.get_db_session)
):
    user = await crud_user.create_user(session=session, user_data=user_data)

    return utils.reformat_any_response(user.user_id, "user_id")


@router.post("/api/users/{user_id}/follow")
async def follow_user(
        user_id: int,
        session: AsyncSession = Depends(dependencies.get_db_session),
        curren_user: User = Depends(dependencies.get_current_user_by_apikey)
):
    await crud_user.follow_user(
        session=session, user_who_follow=curren_user, user_id=user_id
    )

    return {"result": True}


@router.delete("/api/users/{user_id}/follow")
async def unfollow_user(
        user_id: int,
        session: AsyncSession = Depends(dependencies.get_db_session),
        curren_user: User = Depends(dependencies.get_current_user_by_apikey)
):
    await crud_user.unfollow(
        session=session, user_who_unfollow=curren_user, user_id=user_id
    )

    return {"result": True}
