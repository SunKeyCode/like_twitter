from datetime import date, datetime
from typing import List

from db.base_class import Base
from db_models.follower_model import Follower
from db_models.tweet_model import Tweet
from sqlalchemy import Column, Date, Identity, Integer, String
from sqlalchemy.orm import Mapped, relationship


class User(Base):
    __tablename__ = "table_users"

    user_id: int = Column(Integer, Identity(always=True), primary_key=True)
    user_name: str = Column(String(20), nullable=False, unique=True)
    password: str = Column(String, nullable=False)
    first_name: str = Column(String(50), nullable=True)
    last_name: str = Column(String(50), nullable=True)
    reg_date: date = Column(Date, default=datetime.today)

    # TODO это нужно удалить????????????
    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author", lazy="raise")

    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary="table_followers",
        primaryjoin=user_id == Follower.user_id,
        secondaryjoin=user_id == Follower.follower_id,
        viewonly=True,
        lazy="raise",
    )

    following: Mapped[List["User"]] = relationship(
        secondary="table_followers",
        primaryjoin=user_id == Follower.follower_id,
        secondaryjoin=user_id == Follower.user_id,
        viewonly=True,
        lazy="raise",
    )

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, user_name={self.user_name})"
