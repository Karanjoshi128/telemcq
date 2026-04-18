import logging
from dataclasses import dataclass
from datetime import datetime

from telethon.tl.functions.messages import SendVoteRequest
from telethon.tl.types import (
    Channel,
    InputPeerChannel,
    MessageMediaPoll,
)

from .client import build_client

log = logging.getLogger(__name__)

LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]


@dataclass
class ParsedMCQ:
    tg_msg_id: int
    category: str | None
    question: str
    options: list[dict]  # [{key:"A", text:"..."}]
    correct_answer: str | None
    source_date: datetime


def _extract_correct_from_results(results) -> str | None:
    if not results or not getattr(results, "results", None):
        return None
    for idx, r in enumerate(results.results):
        if getattr(r, "correct", False):
            return LETTERS[idx] if idx < len(LETTERS) else str(idx + 1)
    return None


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
    for idx, ans in enumerate(poll.answers):
        key = LETTERS[idx] if idx < len(LETTERS) else str(idx + 1)
        text = ans.text.text if hasattr(ans.text, "text") else str(ans.text)
        options.append({"key": key, "text": text})

    correct_key = _extract_correct_from_results(results)

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


async def _reveal_answer_via_vote(client, peer, msg) -> str | None:
    """Vote on option 0 of a quiz poll to trigger Telegram revealing the correct answer.

    Telegram's SendVote response contains a PollResults with the correct flag set
    on the right option. The user's tally goes up by 1 — acceptable tradeoff for
    getting the answer key populated.
    """
    media = msg.media
    if not isinstance(media, MessageMediaPoll):
        return None
    poll = media.poll
    if not poll or not poll.answers:
        return None
    option_bytes = poll.answers[0].option
    try:
        result = await client(
            SendVoteRequest(peer=peer, msg_id=msg.id, options=[option_bytes])
        )
    except Exception as e:
        log.warning("SendVote failed for msg %s: %s", msg.id, e)
        return None

    for update in getattr(result, "updates", []) or []:
        r = getattr(update, "results", None)
        key = _extract_correct_from_results(r)
        if key:
            return key
    return None


async def _resolve_peer(client, tg_channel_id: int, tg_access_hash: int | None):
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel) and entity.id == tg_channel_id:
            return InputPeerChannel(channel_id=entity.id, access_hash=entity.access_hash)

    if tg_access_hash is not None:
        return InputPeerChannel(channel_id=tg_channel_id, access_hash=tg_access_hash)
    raise ValueError(f"Channel {tg_channel_id} not found in dialogs")


async def scrape_channel(
    session_str: str,
    tg_channel_id: int,
    tg_access_hash: int | None,
    min_msg_id: int,
    limit: int = 500,
    reveal_answers: bool = True,
) -> list[ParsedMCQ]:
    client = build_client(session_str)
    await client.connect()
    try:
        peer = await _resolve_peer(client, tg_channel_id, tg_access_hash)

        out: list[ParsedMCQ] = []
        async for msg in client.iter_messages(peer, limit=limit, min_id=min_msg_id):
            parsed = _parse_poll_message(msg)
            if not parsed:
                continue
            if parsed.correct_answer is None and reveal_answers:
                revealed = await _reveal_answer_via_vote(client, peer, msg)
                if revealed:
                    parsed.correct_answer = revealed
            out.append(parsed)
        return out
    finally:
        await client.disconnect()
