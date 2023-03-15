from sqlalchemy import Column, ForeignKey

from db.base_class import Base


class Follower(Base):
    __tablename__ = "table_followers"
    # constraint user_id != follower_id
    # on_delete???
    user_id = Column(ForeignKey("table_users.user_id"), primary_key=True)
    follower_id = Column(ForeignKey("table_users.user_id"), primary_key=True)
