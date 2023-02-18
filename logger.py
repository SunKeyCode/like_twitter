import logging
import logging.config
from logger_config import LOGGER_CONF

LOG_LEVEL = logging.DEBUG


def init_logger():
    logging.config.dictConfig(LOGGER_CONF)
    # logging.basicConfig(level=LOG_LEVEL)
    # logger = logging.getLogger("main")

