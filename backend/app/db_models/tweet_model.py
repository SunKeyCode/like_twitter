from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Identity, DateTime
from sqlalchemy.orm import Mapped, relationship

from db.base_class import Base
from db_models.tweet_media_relation import MediaTweetRelation  # не удалять


class Tweet(Base):
    __tablename__ = "table_tweets"

    tweet_id: int = Column(Integer, Identity(always=True), primary_key=True)
    author_id: int = Column(ForeignKey("table_users.user_id"), nullable=False)
    content: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now)

    likes: Mapped[List["Like"]] = relationship(lazy="raise")

    author: Mapped["User"] = relationship(back_populates="tweets", lazy="raise")

    attachments: Mapped[List["Media"]] = relationship(
        secondary="table_media_tweet_relation",
        lazy="raise",
    )

    def __repr__(self):
        return "Tweet(id={},author={}, text={}, created={})".format(
            self.tweet_id, self.author_id, self.content, self.created_at
        )
