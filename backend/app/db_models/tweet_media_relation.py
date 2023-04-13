from db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped


class MediaTweetRelation(Base):
    __tablename__ = "table_media_tweet_relation"

    tweet_id: Mapped[int] = Column(
        ForeignKey("table_tweets.tweet_id"),
        primary_key=True,
    )
    media_id: Mapped[int] = Column(
        ForeignKey("table_media.media_id", ondelete="CASCADE"),
        primary_key=True,
    )
