from typing import final

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    @final
    class Config:
        env_file = ".env"

    LOG_LEVEL: str = "INFO"
    MIN_CASHBACK: int = 100
    MIN_DELAY: int = 1
    MAX_DELAY: int = 5
    MAX_PAYMENT: int = 100000
    EARN_PAY_RATIO: float = 0.03
    MAX_ERRORS: int = 3
    ERROR_DELAY_INCREMENT: int = 1
    NOTIF_ENABLE: bool = False
    NOTIF_BOT_TOKEN: str | None = None
    NOTIF_CHAT_ID: str | None = None


settings = Settings()
