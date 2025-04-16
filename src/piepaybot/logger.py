import logging
from pathlib import Path

from colorlog import ColoredFormatter

from piepaybot.config import settings

CONSOLE_LOG_LEVEL = settings.LOG_LEVEL
LOG_FILE_PATH = Path("logs/piepaybot.log")

LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def setup_logger():
    file_logger = logging.getLogger()
    file_logger.setLevel(logging.DEBUG)

    for handler in file_logger.handlers[:]:
        file_logger.removeHandler(handler)

    file_log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_log_handler = logging.FileHandler(LOG_FILE_PATH)
    file_log_handler.setLevel(logging.DEBUG)
    file_log_handler.setFormatter(file_log_formatter)
    file_logger.addHandler(file_log_handler)

    console_logger = logging.getLogger("piepaybot")
    console_logger.setLevel(logging.DEBUG)
    console_logger.propagate = True

    for handler in console_logger.handlers[:]:
        console_logger.removeHandler(handler)

    console_log_formatter = ColoredFormatter(
        "%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - %(message)s",
        datefmt="%H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(CONSOLE_LOG_LEVEL)
    console_handler.setFormatter(console_log_formatter)
    console_logger.addHandler(console_handler)
