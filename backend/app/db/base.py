from db.base_class import Base
from db_models.follower_model import Follower
from db_models.like_model import Like
from db_models.media_model import Media
from db_models.tweet_media_relation import tweet_media_relationship
from db_models.tweet_model import Tweet
from db_models.user_model import User

"""
This is necessary so that alembic can create tables
"""
