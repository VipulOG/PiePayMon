import logging
from pathlib import Path
from typing import Literal

from colorlog import ColoredFormatter

from piepaymon.config import settings

LOG_FILE_PATH = Path("logs/piepaymon.log")
LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)


def setup_logger(mode: Literal["interactive", "service"] = "service"):
    """
    Set up logging configuration based on mode:
    - interactive: Minimal console output, full file logging
    - service: Full console output, full file logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    file_handler = logging.FileHandler(LOG_FILE_PATH)
    file_handler.setLevel(logging.DEBUG)
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_handler.setFormatter(logging.Formatter(fmt))
    root_logger.addHandler(file_handler)

    if mode == "service":
        console_handler = logging.StreamHandler()
        console_handler.setLevel(settings.LOG_LEVEL)
        console_handler.addFilter(lambda record: record.name.startswith("piepaymon"))
        fmt = (
            "%(asctime)s - %(name)s - %(log_color)s%(levelname)s%(reset)s - %(message)s"
        )
        console_handler.setFormatter(ColoredFormatter(fmt, datefmt="%H:%M:%S"))
        root_logger.addHandler(console_handler)
