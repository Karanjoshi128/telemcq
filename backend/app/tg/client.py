from telethon import TelegramClient
from telethon.sessions import StringSession

from ..core.config import get_settings


def build_client(session_str: str = "") -> TelegramClient:
    s = get_settings()
    return TelegramClient(StringSession(session_str), s.TELEGRAM_API_ID, s.TELEGRAM_API_HASH)
