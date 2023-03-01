from datetime import datetime, date
from typing import List

from sqlalchemy import Column, Integer, Identity, String, Date
from sqlalchemy.orm import Mapped, relationship

from db.base_class import Base
from db_models.follower_model import Follower


class User(Base):
    __tablename__ = "table_users"

    user_id: int = Column(Integer, Identity(always=True), primary_key=True)
    user_name: str = Column(String(20), nullable=False, unique=True)
    hashed_password: str = Column(String, nullable=False)
    first_name: str = Column(String(50), nullable=True)
    last_name: str = Column(String(50), nullable=True)
    reg_date: date = Column(Date, default=datetime.today)

    # delete orphan???
    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author", lazy="raise")

    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary="table_followers",
        primaryjoin=user_id == Follower.user_id,
        secondaryjoin=user_id == Follower.follower_id,
        viewonly=True,
    )

    following: Mapped[List["User"]] = relationship(
        secondary="table_followers",
        primaryjoin=user_id == Follower.follower_id,
        secondaryjoin=user_id == Follower.user_id,
        viewonly=True
    )

    def __repr__(self):
        return f"User(id={self.user_id}, user_name={self.user_name})"
