from db.base_class import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column


class Like(Base):
    __tablename__ = "table_likes"
    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("table_tweets.tweet_id"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("table_users.user_id"),
        primary_key=True,
    )

    user: Mapped["User"] = relationship(lazy="raise")
