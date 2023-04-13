from starlette.requests import Request
from starlette.types import Receive, Scope, Send


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
