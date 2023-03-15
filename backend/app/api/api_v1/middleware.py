from starlette.types import Scope, Receive, Send
from starlette.requests import Request
import aiofiles
import pathlib
import json


class LoggingRequestsAsJson:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            request = Request(scope)
            for key, value in request.headers.mutablecopy().items():
                print(f"{key}: {value}")
            # async with aiofiles.open("temp/request_log.json", "a") as file:
            #     pass

        await self.app(scope, receive, send)
