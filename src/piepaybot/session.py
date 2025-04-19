import json
import logging
import os
from types import TracebackType
from typing import TypedDict, cast, final, override

import questionary
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator

from piepaybot.client import PiePayAPIClient
from piepaybot.crypto import generate_session_key

logger = logging.getLogger(__name__)

SESSION_FILE = ".session.json"


class SessionData(TypedDict):
    accessToken: str
    sessionKey: str


class LoginResponseJson(TypedDict):
    data: "LoginData"


class LoginData(TypedDict):
    accessToken: str
    isNewUser: bool


class PhoneValidator(Validator):
    @override
    def validate(self, document: Document):
        if not document.text.isdigit():
            raise ValidationError(message="Please enter a valid phone number.")


class OTPValidator(Validator):
    @override
    def validate(self, document: Document):
        if not document.text.isdigit():
            raise ValidationError(message="Please enter a valid otp.")


@final
class SessionManager:
    def __init__(self, client: PiePayAPIClient | None = None):
        self.session_file: str = SESSION_FILE
        self.client = client or PiePayAPIClient()
        self._cached_session: SessionData | None = None

    async def create_session(self) -> SessionData | None:
        phone = await self._input_phone()
        if not await self._send_otp(phone):
            return None

        otp = await self._input_otp()
        if not (token := await self._verify_otp(phone, otp)):
            return None

        session_data: SessionData = {
            "accessToken": token,
            "sessionKey": generate_session_key(),
        }

        if not await self._save_session_data(session_data):
            return None

        self._cached_session = session_data
        logger.debug(f"Session created.")
        return session_data

    async def load_session(self) -> SessionData | None:
        if self._cached_session:
            return self._cached_session

        if not os.path.exists(self.session_file):
            logger.debug("Session file does not exist.")
            return None

        with open(self.session_file, "r") as f:
            if not (content := f.read().strip()):
                logger.warning("Empty session file found.")
                return None

            data = cast(SessionData, json.loads(content))

            if not data.get("accessToken") or not data.get("sessionKey"):
                logger.warning("Invalid session data format in file.")
                return None

            logger.debug("Session data loaded successfully.")
            self._cached_session = data
            return data

    async def _send_otp(self, phone_number: int) -> bool:
        _ = await self.client.request(
            "otps/login/send",
            "POST",
            json={"phoneNumber": phone_number},
        )
        logger.info("OTP sent successfully.")
        return True

    async def _verify_otp(self, phone_number: int, otp: int) -> str | None:
        response = await self.client.request(
            "users/login-with-mobile",
            "POST",
            json={"phoneNumber": phone_number, "otp": otp},
        )

        response_json = cast(LoginResponseJson, response.json())
        login_data = response_json["data"]

        if login_data["isNewUser"]:
            logger.warning(
                "Account not found. "
                + "Please create an account using the PiePay mobile app first."
            )
            return None

        logger.info("Logged in successfully.")
        return login_data["accessToken"]

    async def _input_phone(self) -> int:
        return int(
            cast(
                str,
                await questionary.text(
                    "Enter your phone number:",
                    validate=PhoneValidator,
                ).ask_async(),
            )
        )

    async def _input_otp(self) -> int:
        return int(
            cast(
                str,
                await questionary.text(
                    "Enter OTP:",
                    validate=OTPValidator,
                ).ask_async(),
            )
        )

    async def _save_session_data(self, data: SessionData) -> bool:
        with open(self.session_file, "w") as f:
            json.dump(data, f)
        logger.debug("Session data saved to file.")
        return True

    async def close(self) -> None:
        logger.debug("Closing session.")
        await self.client.close()
        self._cached_session = None

    async def __aenter__(self) -> "SessionManager":
        _ = await self.load_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.close()
