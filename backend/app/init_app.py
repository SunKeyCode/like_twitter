from logging import getLogger

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from api.api_v1.routers import api_router
from api.api_v1 import exception_handlers
from custom_exc.db_exception import DbIntegrityError
from custom_exc.no_user_found import NoUserFoundError
from logger import init_logger
from api.api_v1 import middleware

logger = getLogger("main")


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router, prefix="/api")

    init_logger()

    app.add_exception_handler(
        exc_class_or_status_code=DbIntegrityError,
        handler=exception_handlers.integrity_error_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=NoUserFoundError,
        handler=exception_handlers.no_user_found_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=HTTPException,
        handler=exception_handlers.http_exceptions_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=RequestValidationError,
        handler=exception_handlers.validation_error_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=Exception,
        handler=exception_handlers.unexpected_error_handler
    )

    # app.add_middleware(middleware.LoggingRequestsAsJson)
    logger.info("Application started.")

    return app
