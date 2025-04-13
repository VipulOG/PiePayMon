import asyncio
import logging
import random
import signal
from typing import final

from piepaybot.client import PiePayAPIClient
from piepaybot.offers import fetch_offers
from piepaybot.session import SessionManager

logger = logging.getLogger(__name__)


MIN_CASHBACK = 100  # Minimum cashback amount to consider an offer interesting
MIN_DELAY = 3  # Minimum delay between checks in seconds
MAX_DELAY = 10  # Maximum delay between checks in seconds
MAX_PAYMENT = 1000  # Maximum payment amount to avoid large transactions
PAY_TO_EARN_RATIO = 0.1  # Acceptable ratio between payment and expected cashback
MAX_CONSECUTIVE_ERRORS = 3  # Maximum consecutive errors before exiting
ERROR_DELAY_INCREMENT = 1  # Additional delay after each error in seconds


@final
class PiePayBot:
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
            async with SessionManager(client) as session_manager:
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
                            min_pay_earn_ratio=PAY_TO_EARN_RATIO,
                        )

                        if offers is None:
                            offers = []

                        logger.info(f"Found {len(offers)} available offers.")

                        self.consecutive_errors = 0
                        delay = random.uniform(MIN_DELAY, MAX_DELAY)

                        logger.info(f"Waiting {delay:.2f} seconds before next check...")

                        await asyncio.sleep(delay)

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
                            break

                        delay = random.uniform(MIN_DELAY, MAX_DELAY) + (
                            ERROR_DELAY_INCREMENT * self.consecutive_errors
                        )

                        logger.info(
                            f"Waiting {delay:.2f} seconds before next attempt..."
                        )

                        await asyncio.sleep(delay)

        logger.info("Application shutdown complete.")
