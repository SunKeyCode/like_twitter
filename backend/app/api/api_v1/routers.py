from fastapi import APIRouter

from api.api_v1.endpoints import media, tweets, users, utils

api_router = APIRouter()

api_router.include_router(tweets.router, tags=["tweet"])
api_router.include_router(users.router, tags=["user"])
api_router.include_router(media.router, tags=["media"])
api_router.include_router(utils.router, tags=["utils"])
