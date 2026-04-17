from dataclasses import dataclass
from datetime import datetime

from telethon.tl.types import (
    Channel,
    InputPeerChannel,
    MessageMediaPoll,
)

from .client import build_client

LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]


@dataclass
class ParsedMCQ:
    tg_msg_id: int
    category: str | None
    question: str
    options: list[dict]  # [{key:"A", text:"..."}]
    correct_answer: str | None
    source_date: datetime


def _parse_poll_message(msg) -> ParsedMCQ | None:
    media = msg.media
    if not isinstance(media, MessageMediaPoll):
        return None
    poll = media.poll
    results = media.results
    if not poll or not getattr(poll, "quiz", False):
        return None

    question_text = poll.question.text if hasattr(poll.question, "text") else str(poll.question)

    options = []
    correct_key = None
    for idx, ans in enumerate(poll.answers):
        key = LETTERS[idx] if idx < len(LETTERS) else str(idx + 1)
        text = ans.text.text if hasattr(ans.text, "text") else str(ans.text)
        options.append({"key": key, "text": text})

    if results and results.results:
        for idx, r in enumerate(results.results):
            if getattr(r, "correct", False):
                correct_key = LETTERS[idx] if idx < len(LETTERS) else str(idx + 1)
                break

    category = None
    raw_text = (msg.message or "").strip()
    if raw_text:
        first_line = raw_text.splitlines()[0].strip()
        if first_line and len(first_line) <= 60:
            category = first_line

    return ParsedMCQ(
        tg_msg_id=msg.id,
        category=category,
        question=question_text,
        options=options,
        correct_answer=correct_key,
        source_date=msg.date,
    )


async def _resolve_peer(client, tg_channel_id: int, tg_access_hash: int | None):
    """Find the InputPeerChannel by scanning dialogs.

    We can't trust stored access_hash alone because Telegram may have rotated it,
    and signed/unsigned bigint round-tripping via Postgres can confuse things.
    So we enumerate dialogs (cheap) and match by id.
    """
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.id == tg_channel_id:
            return InputPeerChannel(channel_id=entity.id, access_hash=entity.access_hash)

    # Fall back to the stored hash if dialog scan missed it
    if tg_access_hash is not None:
        return InputPeerChannel(channel_id=tg_channel_id, access_hash=tg_access_hash)
    raise ValueError(f"Channel {tg_channel_id} not found in dialogs")


async def scrape_channel(
    session_str: str,
    tg_channel_id: int,
    tg_access_hash: int | None,
    min_msg_id: int,
    limit: int = 500,
) -> list[ParsedMCQ]:
    client = build_client(session_str)
    await client.connect()
    try:
        peer = await _resolve_peer(client, tg_channel_id, tg_access_hash)

        out: list[ParsedMCQ] = []
        async for msg in client.iter_messages(peer, limit=limit, min_id=min_msg_id):
            parsed = _parse_poll_message(msg)
            if parsed:
                out.append(parsed)
        return out
    finally:
        await client.disconnect()
