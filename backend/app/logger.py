import logging.config
import os
from logging import getLogger

from configs.logger_config import LOGGER_CONF
from configs import app_config

logger = getLogger("main.logger")


def init_logger():
    if not os.path.exists("logs"):
        os.mkdir("logs")
    logging.config.dictConfig(LOGGER_CONF)
    logger.debug(f"Debug={app_config.DEBUG}")
    logger.debug(f"Base_dir={app_config.BASE_DIR}")
