import logging
from pathlib import Path

from colorlog import ColoredFormatter

from piepaymon.config import settings

CONSOLE_LOG_LEVEL = settings.LOG_LEVEL
LOG_FILE_PATH = Path("logs/piepaymon.log")

LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def setup_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    file_log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_log_formatter)
    root_logger.addHandler(file_handler)

    console_formatter = ColoredFormatter(
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
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
