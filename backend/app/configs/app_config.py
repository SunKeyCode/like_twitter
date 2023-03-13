import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG")
TESTING = os.environ.get("TESTING")
DB_NAME = os.environ.get("DB_NAME")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
