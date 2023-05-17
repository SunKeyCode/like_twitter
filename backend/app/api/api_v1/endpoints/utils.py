from fastapi import APIRouter

from configs import app_config

router = APIRouter()


@router.get("/configs", include_in_schema=False)
async def get_configs():
    return {
        "db_name": app_config.DB_NAME,
        "db_host": app_config.DB_HOST,
        "base_dir": app_config.BASE_DIR,
    }


@router.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0
