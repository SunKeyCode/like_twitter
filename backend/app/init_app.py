from typing import NewType

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException

from api.api_v1.routers import api_router
from api.api_v1 import excaption_handlers
from custom_exc.db_exception import DbIntegrityError
from custom_exc.no_user_found import NoUserFoundError
from api.api_v1 import middleware


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api_router, prefix="/api")

    app.add_exception_handler(
        exc_class_or_status_code=DbIntegrityError,
        handler=excaption_handlers.integrity_error_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=NoUserFoundError,
        handler=excaption_handlers.no_user_found_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=HTTPException,
        handler=excaption_handlers.http_exceptions_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=RequestValidationError,
        handler=excaption_handlers.validation_error_handler
    )

    app.add_exception_handler(
        exc_class_or_status_code=Exception,
        handler=excaption_handlers.unexpected_error_handler
    )

    # app.add_middleware(middleware.LoggingRequestsAsJson)

    return app
