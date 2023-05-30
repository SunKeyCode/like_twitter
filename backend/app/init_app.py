from logging import getLogger
from os import getpid

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
import sentry_sdk
from starlette.exceptions import HTTPException

from api.api_v1 import exception_handlers
from api.api_v1.routers import api_router
from auth.endpoints import auth_router
from custom_exc.db_exception import DbIntegrityError
from custom_exc.no_user_found import NoUserFoundError
from logger import init_logger

logger = getLogger("main.init_app")

sentry_sdk.init(
    dsn="https://baa5f60a11bb44399c12a97ff60ee570@o4504164192681984"
    ".ingest.sentry.io/4505124061118464",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
)


def create_app() -> FastAPI:
    init_logger()

    app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.include_router(api_router, prefix="/api")
    app.include_router(auth_router)

    app.add_exception_handler(
        exc_class_or_status_code=DbIntegrityError,
        handler=exception_handlers.integrity_error_handler,
    )

    app.add_exception_handler(
        exc_class_or_status_code=NoUserFoundError,
        handler=exception_handlers.no_user_found_handler,
    )

    app.add_exception_handler(
        exc_class_or_status_code=HTTPException,
        handler=exception_handlers.http_exceptions_handler,
    )

    app.add_exception_handler(
        exc_class_or_status_code=RequestValidationError,
        handler=exception_handlers.validation_error_handler,
    )

    app.add_exception_handler(
        exc_class_or_status_code=Exception,
        handler=exception_handlers.unexpected_error_handler,
    )

    logger.info("Application started. Worker pid=%s.", getpid())

    return app
