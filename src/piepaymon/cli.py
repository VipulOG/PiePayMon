import asyncio
import logging
import sys
from collections.abc import Coroutine

import click

from piepaymon.client import PiePayAPIClient
from piepaymon.logger import setup_logger
from piepaymon.monitor import PiePayMonitor
from piepaymon.session import SessionManager

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """PiePayMon - Your PiePay deal watchdog"""
    pass


@cli.command()
def run():
    """Run the monitor service"""
    setup_logger()
    _safe_async_run(_run_monitor())


@cli.command()
def create_session():
    """Create a new session interactively"""
    setup_logger()
    _safe_async_run(_create_session())


async def _run_monitor():
    monitor = PiePayMonitor()
    await monitor.run()


async def _create_session():
    async with PiePayAPIClient() as client:
        session_manager = SessionManager(client)
        _ = await session_manager.create_session()


def _safe_async_run(coro: Coroutine[None, None, None]):
    try:
        asyncio.run(coro)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting...")
        sys.exit(0)
    except Exception as err:
        msg = "An unexpected error occurred during command execution: %r"
        logger.error(msg, err, exc_info=True)
        sys.exit(1)
