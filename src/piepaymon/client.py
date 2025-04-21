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
        self._closed = False

    def set_auth_token(self, token: str) -> None:
        self._ensure_open()
        logger.debug("Applying auth headers to client...")
        self.default_headers["Authorization"] = f"Bearer {token}"
        logger.debug("Auth headers applied.")

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
        self._ensure_open()
        url = f"{self.base_url}/{endpoint}"
        logger.debug(f"Request: {endpoint}")

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
        status_code = response.status_code

        if status_code == 401:
            logger.error(f"Failed: {endpoint} [{status_code}] - {msg}")
            raise SessionExpiredError("Session has expired or is invalid.")

        try:
            _ = response.raise_for_status()
        except httpx.HTTPStatusError:
            logger.error(f"Failed: {endpoint} [{status_code}] - {msg}")
            raise

        logger.debug(f"Success: {endpoint} [{status_code}] - {msg}")
        return response

    async def close(self) -> None:
        if not self._closed:
            logger.debug("Closing client connection...")
            await self.client.aclose()
            self._closed = True
            logger.debug("Client connection closed.")

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("Cannot use PiePayAPIClient: client is already closed.")

    async def __aenter__(self) -> PiePayAPIClient:
        self._ensure_open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
