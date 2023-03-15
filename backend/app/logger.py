import logging
import logging.config
import os

from configs.logger_config import LOGGER_CONF


LOG_LEVEL = logging.DEBUG


def init_logger():
    if not os.path.exists("logs"):
        os.mkdir("logs")
    logging.config.dictConfig(LOGGER_CONF)
