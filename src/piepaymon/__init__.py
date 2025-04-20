import asyncio
import logging
import sys

from piepaymon.monitor import PiePayMonitor
from piepaymon.logger import setup_logger

logger = logging.getLogger(__name__)


def main():
    try:
        setup_logger()
        monitor = PiePayMonitor()
        asyncio.run(monitor.run())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e!r}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
