import os
from pathlib import Path
from logging import getLogger

from dotenv import load_dotenv

load_dotenv()

DEBUG = True

DB_NAME = os.environ.get("DB_NAME")
DB_NAME_TEST = os.environ.get("DB_NAME_TEST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")

# максимальный размер изображения в байтах, 1Мб = 1048576
MAX_IMG_SIZE = 1048576

# main.py directory
BASE_DIR = Path(__file__).resolve().parents[1]

MEDIA_ROOT = BASE_DIR.parents[1] / "static"

TEST_MEDIA_DIR = ""
