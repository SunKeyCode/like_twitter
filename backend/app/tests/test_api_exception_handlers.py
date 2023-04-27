import pytest

from fastapi.exceptions import RequestValidationError
from fastapi import Request

from api.api_v1 import exception_handlers
from custom_exc.db_exception import DbIntegrityError
from custom_exc.no_user_found import NoUserFoundError

pytestmark = pytest.mark.asyncio


async def test_integrity_error_handler():
    response = await exception_handlers.integrity_error_handler(
        True,
        DbIntegrityError(),
    )
    assert response.status_code == 400


async def test_no_user_found_handler():
    response = await exception_handlers.no_user_found_handler(
        True,
        NoUserFoundError(),
    )
    assert response.status_code == 404


async def test_validation_error_handler():
    response = await exception_handlers.validation_error_handler(
        Request(scope={"type": "http", "path": "/", "headers": []}),
        RequestValidationError(errors=[]),
    )
    assert response.status_code == 422


async def test_unexpected_error_handler():
    response = await exception_handlers.unexpected_error_handler(
        True,
        Exception(),
    )
    assert response.status_code == 500
