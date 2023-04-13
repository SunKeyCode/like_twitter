import logging.config
import os
from logging import getLogger

from configs import app_config
from configs.logger_config import LOGGER_CONF

logger = getLogger("main.logger")


def init_logger():
    if not os.path.exists("logs"):
        os.mkdir("logs")
    logging.config.dictConfig(LOGGER_CONF)
    logger.debug("Debug=%s", app_config.DEBUG)
    logger.debug("Base_dir=%s", app_config.BASE_DIR)
