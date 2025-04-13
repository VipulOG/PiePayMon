import logging
from typing import TypedDict

from piepaybot.client import PiePayAPIClient
from piepaybot.models import Offer

logger = logging.getLogger(__name__)


class OffersResponseJson(TypedDict):
    data: "OffersData | None"


class OffersData(TypedDict):
    deals: "list[Deal] | None"


class Deal(TypedDict):
    amountToPay: int
    cardholderEarnings: int
    userOrderId: str


async def fetch_offers(
    client: PiePayAPIClient,
    session_key: str,
    *,
    min_earn: float | None = None,
    max_pay: float | None = None,
    min_pay_earn_ratio: float | None = None,
) -> list[Offer] | None:
    try:
        response = await client.request(
            "orders-available/cardholder",
            "POST",
            json={"id": session_key},
        )

        if response.status_code != 200:
            logger.error(f"Failed to fetch offers. Status code: {response.status_code}")
            return None

        response_data: OffersResponseJson = response.json()

        if not (offers_data := response_data.get("data")):
            logger.error("Invalid response: missing 'data' field.")
            return None

        if (deals := offers_data.get("deals")) is None:
            logger.error("Invalid response: missing 'deals' field.")
            return None

        offers = [
            Offer(pay=deal["amountToPay"], earn=deal["cardholderEarnings"])
            for deal in deals
            if (min_earn is None or deal["cardholderEarnings"] >= min_earn)
            and (max_pay is None or deal["amountToPay"] <= max_pay)
            and (
                min_pay_earn_ratio is None
                or (deal["amountToPay"] / deal["cardholderEarnings"])
                >= min_pay_earn_ratio
            )
        ]

        return offers if offers else None

    except Exception as e:
        logger.error(f"Failed to fetch offers: {e!r}", exc_info=True)
        return None
