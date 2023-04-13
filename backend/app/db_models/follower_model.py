from db.base_class import Base
from sqlalchemy import Column, ForeignKey, Integer


class Follower(Base):
    __tablename__ = "table_followers"

    user_id = Column(Integer, ForeignKey("table_users.user_id"), primary_key=True)
    follower_id = Column(Integer, ForeignKey("table_users.user_id"), primary_key=True)
