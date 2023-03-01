from fastapi import APIRouter, Depends

from api.dependencies import get_db_session
from db import init_db

router = APIRouter()


@router.post("/init_db")
async def initialize_db(session=Depends(get_db_session)):
    await init_db.create_all(session)
    return "OK"
