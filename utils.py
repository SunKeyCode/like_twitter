def reformat_tweet(tweet: dict) -> dict:
    print(tweet)
    try:
        user_data: dict = tweet.pop(tweet["likes"]["user"])
        tweet["likes"] = user_data["user_name"]
    except KeyError:
        raise KeyError
    #     как то обработать
    return tweet
