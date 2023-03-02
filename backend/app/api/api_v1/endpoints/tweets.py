from fastapi import APIRouter, Depends, status, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import dependencies, utils
from db_models.user_model import User
from schemas import tweet_schema
from crud import crud_tweet

router = APIRouter(prefix="/tweets", )


# @router.post("/", )
# async def req_test(req: Request, ):
#     print(req.headers)
#     boby = await req.json()
#     print(boby)


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
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"You are not authenticated user"}
        )

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
):
    result = await crud_tweet.delete_tweet(
        session=session, tweet_id=tweet_id, user_id=current_user.user_id
    )
    if result:
        return {"result": result}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tweet does not exists or belongs another user"
        )


@router.get(
    "/",
    response_model=tweet_schema.TweetsResponseModel,
    response_model_by_alias=False
)
async def get_feed(
        session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey)
):
    user = current_user
    tweets_as_obj = await crud_tweet.read_feed(session=session, user_id=user.user_id)

    tweets_as_json = map(jsonable_encoder, tweets_as_obj)

    return utils.reformat_response_iterable(
        tweets_as_json,
        func=utils.reformat_tweet_response,
        key_name="tweets"
    )


@router.post(
    "/{tweet_id}/likes",
    description="Add like to tweet",
    status_code=status.HTTP_201_CREATED
)
async def add_like(
        tweet_id: int, session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey)
):
    user = current_user
    await crud_tweet.add_like(session=session, tweet_id=tweet_id, user_id=user.user_id)
    return {"result": True}


@router.delete("/{tweet_id}/likes", status_code=status.HTTP_202_ACCEPTED)
async def delete_like(
        tweet_id: int,
        session: AsyncSession = Depends(dependencies.get_db_session),
        current_user: User = Depends(dependencies.get_current_user_by_apikey)
):
    user = current_user
    await crud_tweet.remove_like(
        session=session, tweet_id=tweet_id, user_id=user.user_id
    )
    return {"result": True}
