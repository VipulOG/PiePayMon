import json
import logging
import os
from typing import TypedDict, cast, final, override

import httpx
import questionary
from prompt_toolkit.document import Document
from prompt_toolkit.validation import ValidationError, Validator

from piepaymon.client import PiePayAPIClient
from piepaymon.crypto import generate_session_key

logger = logging.getLogger(__name__)

SESSION_FILE = ".session.json"


class SessionData(TypedDict):
    accessToken: str
    sessionKey: str


class SendOtpResponseJson(TypedDict):
    msg: str


class VerifyOtpResponseJson(TypedDict):
    data: "LoginData"
    msg: str


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
    def __init__(self, client: PiePayAPIClient):
        self.session_file: str = SESSION_FILE
        self.client = client
        self._cached_session: SessionData | None = None

    async def create_session(self) -> SessionData | None:
        logger.debug("Creating session...")

        while True:
            phone = await self._input_phone()
            if await self._send_otp(phone):
                break

        while True:
            otp = await self._input_otp()
            if token := await self._verify_otp(phone, otp):
                break

        session_data: SessionData = {
            "accessToken": token,
            "sessionKey": generate_session_key(),
        }

        self._cached_session = session_data
        await self._save_session_data(session_data)
        logger.debug("Session created successfully.")
        return session_data

    async def load_session(self) -> SessionData | None:
        logger.debug("Loading session...")

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
        self._cached_session = data
        logger.debug("Session data loaded successfully.")
        return data

    async def _send_otp(self, phone_number: int) -> bool:
        logger.debug("Sending otp...")

        try:
            response = await self.client.request(
                "otps/login/send",
                "POST",
                json={"phoneNumber": phone_number},
            )
            response_json = cast(SendOtpResponseJson, response.json())
            msg = response_json["msg"]
            print(f"✔️ {msg}")
            logger.info(f"Success: {msg}")
            return True

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                response_json = cast(SendOtpResponseJson, e.response.json())
                msg = response_json["msg"]
                print(f"❌ {msg}")
                logger.info(f"Failed: {msg}")
                return False
            raise

    async def _verify_otp(self, phone_number: int, otp: int) -> str | None:
        logger.debug("Verifying otp...")

        try:
            response = await self.client.request(
                "users/login-with-mobile",
                "POST",
                json={"phoneNumber": phone_number, "otp": otp},
            )
            response_json = cast(VerifyOtpResponseJson, response.json())
            login_data = response_json["data"]

            if login_data["isNewUser"]:
                msg = "⚠️ Account not found. Please create an account using the PiePay mobile app first."
                print(msg)
                logger.warning("Failed to verify otp: Account not found.")
                return None

            msg = response_json["msg"]
            print(f"✔️ {msg}")
            logger.info(f"Success: {msg}")
            return login_data["accessToken"]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                response_json = cast(VerifyOtpResponseJson, e.response.json())
                msg = response_json["msg"]
                print(f"❌ {msg}")
                logger.info(f"Failed: {msg}")
                return None
            raise

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

    async def _save_session_data(self, data: SessionData):
        logger.debug("Saving session...")
        with open(self.session_file, "w") as f:
            json.dump(data, f)
        logger.debug("Session data saved to file.")
