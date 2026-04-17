from telethon.tl.types import Channel

from .client import build_client


async def list_channels(session_str: str) -> list[dict]:
    client = build_client(session_str)
    await client.connect()
    try:
        out = []
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            if isinstance(entity, Channel):
                out.append({
                    "tg_channel_id": entity.id,
                    "tg_access_hash": entity.access_hash,
                    "title": entity.title or "(untitled)",
                    "username": entity.username,
                    "is_broadcast": bool(getattr(entity, "broadcast", False)),
                })
        return out
    finally:
        await client.disconnect()
