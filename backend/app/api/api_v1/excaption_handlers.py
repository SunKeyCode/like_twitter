from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette import status
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from custom_exc.db_exception import DbIntegrityError
from custom_exc.no_user_found import NoUserFoundError

DEBUG = True


async def integrity_error_handler(_, exc: DbIntegrityError):
    # logger.error(f"Integrity error: {exc.error_message}")
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


async def no_user_found_handler(_, exc: NoUserFoundError):
    # сделать объект ErrorMessage через дата класс???
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


async def http_exceptions_handler(_, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "result": False,
                "error_type": "http_exception",
                "error_message": exc.detail,
            }
        )
    )


async def validation_error_handler(_, exc: RequestValidationError):
    # logger.error(f"Validation error: {exc.errors()}")
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


async def unexpected_error_handler(_, exc: Exception):
    # logger.error(f"Unexpected error:", exc_info=exc)
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
