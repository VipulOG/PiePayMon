from __future__ import annotations

import logging
from collections.abc import Mapping
from types import TracebackType
from typing import TypedDict, cast, final

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://prod.api.piepay.in/v1"

HEADERS = {
    "version": "2.0.8",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",
    "user-agent": "okhttp/4.9.2",
}


class ResponseJson(TypedDict):
    msg: str


class SessionExpiredError(Exception):
    """Raised when the session has expired or is unauthorized (401)."""

    pass


@final
class PiePayAPIClient:
    def __init__(self) -> None:
        self.base_url = BASE_URL
        self.default_headers = HEADERS.copy()
        self.client = httpx.AsyncClient()

    def set_auth_token(self, token: str) -> None:
        self.default_headers["Authorization"] = f"Bearer {token}"

    async def request(
        self,
        endpoint: str,
        method: str,
        *,
        params: httpx.QueryParams | None = None,
        data: Mapping[str, object] | None = None,
        json: object | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        url = f"{self.base_url}/{endpoint}"

        request_headers = self.default_headers.copy()
        if headers:
            request_headers.update(headers)

        response = await self.client.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            headers=request_headers,
        )

        msg = cast(ResponseJson, response.json())["msg"]

        if 200 <= (status_code := response.status_code) < 300:
            logger.debug(f"Success: {endpoint} [{status_code}] - {msg}")
            return response

        if status_code == 401:
            logger.error(f"Failed: {endpoint} [{status_code}] - {msg}")
            raise SessionExpiredError("Session has expired or is invalid.")

        logger.error(f"Failed: {endpoint} [{status_code}] - {msg}")
        return response

    async def close(self) -> None:
        logger.debug("Closing connection.")
        await self.client.aclose()

    async def __aenter__(self) -> PiePayAPIClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
