import logging
from typing import TypedDict, cast

from piepaymon.client import PiePayAPIClient
from piepaymon.models import Offer

logger = logging.getLogger(__name__)


class OffersResponseJson(TypedDict):
    data: "OffersData"


class OffersData(TypedDict):
    deals: "list[Deal]"


class Deal(TypedDict):
    userOrderId: str
    amountToPay: int
    cardholderEarnings: int


async def fetch_offers(
    client: PiePayAPIClient,
    session_key: str,
    *,
    min_earn: float = 0,
    max_pay: float = 100000000,
    min_earn_pay_ratio: float = 0,
) -> list[Offer]:
    response = await client.request(
        "orders-available/cardholder",
        "POST",
        json={"id": session_key},
    )

    response_data = cast(OffersResponseJson, response.json())
    deals = response_data["data"]["deals"]

    return [
        Offer(
            id=deal["userOrderId"],
            pay=deal["amountToPay"],
            earn=deal["cardholderEarnings"],
        )
        for deal in deals
        if (deal["cardholderEarnings"] >= min_earn)
        and (deal["amountToPay"] <= max_pay)
        and ((deal["cardholderEarnings"] / deal["amountToPay"]) >= min_earn_pay_ratio)
    ]
