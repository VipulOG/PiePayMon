import asyncio
import logging
import random
import signal
from typing import final

from piepaymon.client import PiePayAPIClient, SessionExpiredError
from piepaymon.config import settings
from piepaymon.notif import send as notif_send
from piepaymon.offers import fetch_offers
from piepaymon.session import SessionManager

logger = logging.getLogger(__name__)


@final
class PiePayMonitor:
    def __init__(self):
        self.consecutive_errors = 0
        self.shutdown_event = asyncio.Event()

    async def run(self):
        logger.info("PiePayMon service is now running...")
        self._setup_signal_handlers()

        async with PiePayAPIClient() as client:
            session_manager = SessionManager(client)
            session = await session_manager.load_session()

            if not session:
                logger.error("Session not found. Create one manually. Exiting...")
                return None

            session_key = session.get("sessionKey")
            access_token = session.get("accessToken")
            client.set_auth_token(access_token)

            if settings.NOTIF_ENABLE:
                _ = await notif_send("PiePayMon service started.")

            while not self.shutdown_event.is_set():
                try:
                    await self._monitor_offers(client, session_key)

                    self.consecutive_errors = 0
                    delay = random.uniform(settings.MIN_DELAY, settings.MAX_DELAY)

                    logger.info(f"Waiting {delay:.2f}s...")
                    await asyncio.sleep(delay)

                except SessionExpiredError:
                    logger.error("Session expired. Exiting...")
                    break

                except Exception as e:
                    if await self._handle_error(e):
                        break

        if settings.NOTIF_ENABLE:
            _ = await notif_send("PiePayMon service stoped.")

        logger.info("PiePayMon service stopped.")

    def _setup_signal_handlers(self):
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self._handle_shutdown_signal)

    def _handle_shutdown_signal(self):
        logger.info("Shutdown signal received. Exiting gracefully...")
        self.shutdown_event.set()

    async def _monitor_offers(self, client: PiePayAPIClient, session_key: str):
        logger.info("Fetching offers...")

        offers = await fetch_offers(
            client=client,
            session_key=session_key,
            min_earn=settings.MIN_CASHBACK,
            max_pay=settings.MAX_PAYMENT,
            min_pay_earn_ratio=settings.PAY_EARN_RATIO,
        )

        if not (num_offers := len(offers)) > 0:
            logger.info("No interesting offers available.")
            return

        logger.info(f"{num_offers} interesting offer(s) available:")
        for i, offer in enumerate(offers, 1):
            logger.info(f"Offer {i}: Pay ${offer.pay:.2f} → Earn ${offer.earn:.2f}")

        if settings.NOTIF_ENABLE:
            header = f"{num_offers} interesting offer(s) found:"
            offer_lines = [
                f"• Pay ${offer.pay:.2f} → Earn ${offer.earn:.2f}" for offer in offers
            ]

            notification_message = "\n".join([header, *offer_lines])
            _ = await notif_send(notification_message)

    async def _handle_error(self, error: Exception) -> bool:
        self.consecutive_errors += 1

        error_count = f"{self.consecutive_errors}/{settings.MAX_ERRORS}"
        logger.error(f"Error fetching offers ({error_count}): {error!r}", exc_info=True)

        max_errors = settings.MAX_ERRORS
        if self.consecutive_errors >= settings.MAX_ERRORS:
            logger.error(f"Max errors reached ({max_errors}). Exiting...")
            return True

        delay = random.uniform(settings.MIN_DELAY, settings.MAX_DELAY) + (
            settings.ERROR_DELAY_INCREMENT * self.consecutive_errors
        )

        logger.info(f"Retrying in {delay:.2f}s...")
        await asyncio.sleep(delay)
        return False
