from datetime import datetime
from typing import List

from sqlalchemy import DateTime, ForeignKey, Identity, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base_class import Base
from db_models.like_model import Like
from db_models.media_model import Media
from db_models.user_model import User
from db_models.tweet_media_relation import tweet_media_relationship


class Tweet(Base):
    __tablename__ = "table_tweets"

    tweet_id = mapped_column(Integer, Identity(always=True), primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("table_users.user_id"),
        nullable=False,
    )
    content = mapped_column(String, nullable=False)
    created_at = mapped_column(DateTime, default=datetime.now)

    likes: Mapped[List["Like"]] = relationship(
        lazy="raise", cascade="all, delete-orphan"
    )

    author: Mapped["User"] = relationship(lazy="raise")

    attachments: Mapped[List["Media"]] = relationship(
        secondary=tweet_media_relationship,
        lazy="raise",
        cascade="all, delete-orphan",
        single_parent=True,
    )

    def __repr__(self) -> str:
        return "Tweet(id={},author={}, text={}, created={}, likes={})".format(
            self.tweet_id, self.author_id, self.content, self.created_at, self.likes
        )
