from sqlalchemy import ForeignKey, Table, Column

from db.base_class import Base

tweet_media_relationship = Table(
    "table_media_tweet_relation",
    Base.metadata,
    Column(
        "tweet_id",
        ForeignKey("table_tweets.tweet_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "media_id",
        ForeignKey("table_media.media_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
