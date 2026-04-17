from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

from .client import build_client


async def send_code(phone: str) -> dict:
    client = build_client()
    await client.connect()
    try:
        sent = await client.send_code_request(phone)
        session_str = client.session.save()
        return {
            "phone_code_hash": sent.phone_code_hash,
            "temp_session": session_str,
        }
    finally:
        await client.disconnect()


async def verify_code(
    phone: str,
    code: str,
    phone_code_hash: str,
    temp_session: str,
    password: str | None = None,
) -> str:
    client = build_client(temp_session)
    await client.connect()
    try:
        try:
            await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        except SessionPasswordNeededError:
            if not password:
                raise
            await client.sign_in(password=password)
        return client.session.save()
    finally:
        await client.disconnect()
