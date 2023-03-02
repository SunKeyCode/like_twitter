from fastapi import Request


async def add_process_time_header(request: Request, call_next):
    headers = request.headers
    body = await request.json()
    print(headers)
    print(body)
    response = await call_next(request)
    return response
