from db.base_class import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, relationship


class Like(Base):
    __tablename__ = "table_likes"
    tweet_id: Mapped[int] = Column(
        ForeignKey("table_tweets.tweet_id"),
        primary_key=True,
    )
    user_id: Mapped[int] = Column(
        ForeignKey("table_users.user_id"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(lazy="raise")
