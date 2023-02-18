from typing import Any, Iterable, Callable, List


def reformat_tweet_response(tweet: dict | None) -> dict:
    new_likes = []
    if tweet is None:
        return tweet
    try:
        likes: list = tweet.pop("likes")
        while likes:
            like: dict = likes.pop()
            user: dict | None = like.pop("user")
            like["user_name"] = user["user_name"]
            new_likes.append(like)

        tweet["likes"] = new_likes
    except KeyError:
        raise KeyError
    #     как то обработать
    # return reformat_any_response(tweet, "tweet")
    return tweet


def reformat_response_iterable(iterable: Iterable, func: Callable,
                               key_name: str) -> dict:
    if isinstance(iterable, dict):
        return reformat_any_response(iterable, key_name)

    response = []

    for item in iterable:
        response.append(func(item))

    if not all(response):
        return reformat_any_response([], key_name)

    return reformat_any_response(response, key_name)


def reformat_any_response(value: Any | List[Any], key: str | List[str] = None) -> dict:
    if isinstance(key, list) and isinstance(value, list) and len(key) == len(value):
        key.append("result")
        value.append(True)
        return dict(zip(key, value))
    elif isinstance(key, str):
        return {"result": True, key: value}
    else:
        raise TypeError


def reformat_error(exc: tuple):
    try:
        return exc[0][0]
    except IndexError:
        return "error massage failed"

