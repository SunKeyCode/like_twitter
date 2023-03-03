from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import FlushError
from starlette import status
from starlette.exceptions import HTTPException

from db.session import async_session
from crud import crud_user
from custom_exc.db_exception import DbIntegrityError


async def get_db_session():
    try:
        async with async_session() as session:
            yield session
    except IntegrityError as exc:
        raise DbIntegrityError(exc.args)
    except FlushError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0]
        )

# TODO добавить вариант авторизации с oauth2 или jwt
# async def _get_current_user(token: str = Depends(oauth2_scheme),
#                             session: AsyncSession = Depends(get_db_session),
#                             include_relation: str | None = None):
#     if token in storage and storage[token]["exp_date"] > datetime.now():
#         # user_id = storage[token]["user_id"]  # получить user_id из токена
#         user_id = 1
#         user = await crud.read_user(
#             session=session,
#             include_relations=include_relation,
#             user_id=int(user_id)
#         )
#         return user
#     else:
#         return None


async def get_current_user_by_apikey(
        session: AsyncSession = Depends(get_db_session),
        include_relation: str | None = None
):
    # TODO реализовать получение ключа из заголовка
    user_id = 1
    user = await crud_user.read_user(
        session=session,
        include_relations=include_relation,
        user_id=int(user_id)
    )
    return user
