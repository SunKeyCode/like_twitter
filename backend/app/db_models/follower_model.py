from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from db.base_class import Base


class Follower(Base):
    __tablename__ = "table_followers"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("table_users.user_id"),
        primary_key=True,
    )
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("table_users.user_id"),
        primary_key=True,
    )
