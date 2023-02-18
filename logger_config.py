import sys

LOGGER_CONF = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s:%(name)s  --->  %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "to_file": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s"
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": sys.stdout,
        },
        "access_file_handler": {
            "class": "logging.FileHandler",
            "formatter": "to_file",
            "filename": "logs/access.log",
            "mode": "a"
        },
        "error_file_handler": {
            "class": "logging.FileHandler",
            "level": "ERROR",
            "formatter": "to_file",
            "filename": "logs/error.log",
            "mode": "a"
        }
    },
    "loggers": {
        "main": {
            "level": "DEBUG",
            "handlers": ["console_handler", "error_file_handler"]
        },
        "uvicorn.access": {
            "handlers": ["access_file_handler"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["error_file_handler"],
            "level": "ERROR",
            "propagate": False,
        }
    }
}
