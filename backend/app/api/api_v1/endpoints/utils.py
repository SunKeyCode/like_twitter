from fastapi import APIRouter, Depends

from api.dependencies import get_db_session
from db import init_db
from configs import app_config

router = APIRouter()


@router.post("/init_db", include_in_schema=False)
async def initialize_db(session=Depends(get_db_session)):
    await init_db.create_all(session)

    return "OK"


@router.get("/configs", include_in_schema=False)
async def get_configs():
    return {
        "db_name": app_config.DB_NAME,
        "db_host": app_config.DB_HOST,
        "base_dir": app_config.BASE_DIR,
    }
