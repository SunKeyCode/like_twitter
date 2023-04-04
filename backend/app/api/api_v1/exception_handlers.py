from logging import getLogger

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from custom_exc.db_exception import DbIntegrityError
from custom_exc.no_user_found import NoUserFoundError
from configs.app_config import DEBUG

logger = getLogger("main.exception_handlers")


async def integrity_error_handler(_, exc: DbIntegrityError) -> JSONResponse:
    logger.error(f"Integrity error: {exc.error_message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "DbIntegrityError",
                "error_message": exc.error_message,
            }
        )
    )


async def no_user_found_handler(_, exc: NoUserFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "No user found error",
                "error_message": exc.error_message,
            }
        )
    )


async def http_exceptions_handler(request: Request, exc: HTTPException) -> JSONResponse:
    error_message = f"{exc.detail}. URL={request.url}"
    logger.error(error_message)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "http_exception",
                "error_message": error_message,
            }
        )
    )


async def validation_error_handler(
        request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.error(f"Validation error: {exc.errors()}. url={request.url}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "RequestValidationError",
                "error_message": exc.errors() if DEBUG else "wrong input field(s)",
            }
        )
    )


async def unexpected_error_handler(_, exc: Exception) -> JSONResponse:
    logger.error(f"Unexpected error:", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "Exception",
                "error_message": "Internal server error",
            }
        )
    )
