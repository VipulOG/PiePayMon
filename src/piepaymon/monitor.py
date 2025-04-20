import asyncio
import logging
import random
import signal
from typing import final

from piepaymon.client import PiePayAPIClient, SessionExpiredError
from piepaymon.config import settings
from piepaymon.offers import fetch_offers
from piepaymon.session import SessionManager

logger = logging.getLogger(__name__)


MIN_CASHBACK = settings.MIN_CASHBACK
MIN_DELAY = settings.MIN_DELAY
MAX_DELAY = settings.MAX_DELAY
MAX_PAYMENT = settings.MAX_PAYMENT
PAY_EARN_RATIO = settings.PAY_EARN_RATIO
MAX_CONSECUTIVE_ERRORS = settings.MAX_CONSECUTIVE_ERRORS
ERROR_DELAY_INCREMENT = settings.ERROR_DELAY_INCREMENT


@final
class PiePayMonitor:
    def __init__(self):
        self.consecutive_errors = 0
        self.shutdown_event = asyncio.Event()

    def handle_shutdown_signal(self):
        logger.info("Shutdown signal received. Exiting gracefully...")
        self.shutdown_event.set()

    async def run(self):
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.handle_shutdown_signal)

        async with PiePayAPIClient() as client:
            session_manager = SessionManager(client)
            if not (session := await session_manager.load_session()):
                session = await session_manager.create_session()

            if not session:
                logger.error("Failed to create a session. Exiting...")
                return

            client.set_auth_token(session.get("accessToken"))

            while not self.shutdown_event.is_set():
                try:
                    logger.info("Fetching offers...")

                    offers = await fetch_offers(
                        client=client,
                        session_key=session.get("sessionKey"),
                        min_earn=MIN_CASHBACK,
                        max_pay=MAX_PAYMENT,
                        min_pay_earn_ratio=PAY_EARN_RATIO,
                    )

                    logger.info(f"Found {len(offers)} available offers.")

                    self.consecutive_errors = 0
                    delay = random.uniform(MIN_DELAY, MAX_DELAY)

                    logger.info(f"Waiting {delay:.2f} seconds before next check...")

                    await asyncio.sleep(delay)

                except SessionExpiredError:
                    logger.error("Session expired.")
                    session = await session_manager.create_session()

                    if not session:
                        logger.error("Failed to create a session. Exiting...")
                        return

                    client.set_auth_token(session.get("accessToken"))
                    continue

                except Exception as e:
                    self.consecutive_errors += 1

                    logger.error(
                        "Error fetching offers "
                        + f"({self.consecutive_errors}/{MAX_CONSECUTIVE_ERRORS}): {e!r}",
                        exc_info=True,
                    )

                    if self.consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        logger.error(
                            "Reached maximum consecutive errors "
                            + f"({MAX_CONSECUTIVE_ERRORS}). Exiting..."
                        )
                        self.shutdown_event.set()
                        return

                    delay = random.uniform(MIN_DELAY, MAX_DELAY) + (
                        ERROR_DELAY_INCREMENT * self.consecutive_errors
                    )

                    logger.info(f"Waiting {delay:.2f} seconds before next attempt...")

                    await asyncio.sleep(delay)

        logger.info("Application shutdown complete.")
