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


@router.get("/sentry-debug", include_in_schema=False)
async def trigger_error():
    division_by_zero = 1 / 0
    return {"result": division_by_zero}


@router.get("/test_endpoint", include_in_schema=False)
async def speed_test():
    return {"result": True}
