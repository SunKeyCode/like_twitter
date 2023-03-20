from typing import Any

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies, utils
from db_models.user_model import User
from schemas import tweet_schema
from crud import crud_tweet

router = APIRouter(prefix="/tweets", )


@router.post(
    "/",
    description="Creates new tweet",
    response_model=tweet_schema.CreateTweetModelOut,
    status_code=status.HTTP_201_CREATED
)
async def create_tweet(
        tweet_data: tweet_schema.CreateTweetModelIn,
        session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey)
) -> dict[str, Any]:

    tweet = await crud_tweet.create_tweet(
        session=session,
        tweet_data=tweet_data,
        author=current_user
    )

    return utils.reformat_any_response(key="tweet_id", value=tweet.tweet_id)


@router.delete("/{tweet_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_tweet(
        tweet_id: int,
        session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey)
) -> dict[str, Any]:
    result = await crud_tweet.delete_tweet(
        session=session, tweet_id=tweet_id, user_id=current_user.user_id
    )
    if result:
        return {"result": result}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tweet does not exists or belongs to another user"
        )


@router.get(
    "/",
    response_model=tweet_schema.TweetsResponseModel,
    response_model_by_alias=False
)
async def get_feed(
        session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey),
        pagination: dict = Depends(dependencies.pagination)
) -> dict[str, Any]:
    user = current_user

    tweets_as_obj = await crud_tweet.read_feed(
        session=session,
        user_id=user.user_id,
        offset=0 if pagination.get("offset") is None else pagination["offset"],
        limit=100 if pagination.get("limit") is None else pagination["limit"]
    )
    tweets_as_json = map(jsonable_encoder, tweets_as_obj)

    return utils.reformat_any_response(key="tweets", value=list(tweets_as_json))


@router.post(
    "/{tweet_id}/likes",
    description="Add like to tweet",
    status_code=status.HTTP_201_CREATED
)
async def add_like(
        tweet_id: int, session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey)
) -> dict[str, Any]:
    user = current_user
    await crud_tweet.add_like(session=session, tweet_id=tweet_id, user_id=user.user_id)
    return {"result": True}


@router.delete("/{tweet_id}/likes", status_code=status.HTTP_202_ACCEPTED)
async def delete_like(
        tweet_id: int,
        session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey)
) -> dict[str, Any]:
    user = current_user
    await crud_tweet.remove_like(
        session=session, tweet_id=tweet_id, user_id=user.user_id
    )
    return {"result": True}
