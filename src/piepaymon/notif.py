import httpx

from piepaymon.config import settings


async def send(message: str):
    _validate_settings()

    url = f"https://api.telegram.org/bot{settings.NOTIF_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": settings.NOTIF_CHAT_ID, "text": message}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
    return response.status_code == 200


def _validate_settings():
    if not settings.NOTIF_ENABLE:
        raise RuntimeError(
            "Notification feature is currently disabled. "
            + "To enable notifications, set NOTIF_ENABLE=True."
        )

    if not settings.NOTIF_BOT_TOKEN:
        raise ValueError(
            "Telegram bot token is required for notifications but not configured. "
            + "Please set NOTIF_BOT_TOKEN with your Telegram bot's API token."
        )

    if not settings.NOTIF_CHAT_ID:
        raise ValueError(
            "Telegram chat ID is required for notifications but not configured. "
            + "Please set NOTIF_CHAT_ID with the ID of the chat you want to "
            + "receive notifications in."
        )
