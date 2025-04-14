from typing import final

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    @final
    class Config:
        env_file = ".env"

    LOG_LEVEL: str = "INFO"
    MIN_CASHBACK: int = 100  # Minimum cashback amount to consider an offer interesting
    MIN_DELAY: int = 1  # Minimum delay between offer checks in seconds
    MAX_DELAY: int = 5  # Maximum delay between offer checks in seconds
    MAX_PAYMENT: int = 100000  # Maximum payment amount to avoid large transactions
    PAY_EARN_RATIO: float = 0.1  # Acceptable ratio between payment and cashback
    MAX_CONSECUTIVE_ERRORS: int = 3  # Maximum consecutive errors before exiting
    ERROR_DELAY_INCREMENT: int = 1  # Additional delay after each error in seconds


settings = Settings()
