import logging

from fastapi import APIRouter, Depends, HTTPException

from ..core import ratelimit
from ..core.crypto import decrypt
from ..core.deps import current_user_id, require_cron_secret
from ..core.supabase import service_client
from ..tg.scraper import scrape_channel

log = logging.getLogger(__name__)
router = APIRouter(prefix="/scrape", tags=["scrape"])


async def _scrape_for_user(user_id: str) -> dict:
    sb = service_client()
    acct = sb.table("telegram_accounts").select("session_encrypted").eq("user_id", user_id).execute()
    if not acct.data:
        return {"user_id": user_id, "scraped": 0, "skipped": "no_account"}
    ch = sb.table("channels").select("*").eq("user_id", user_id).execute()
    if not ch.data:
        return {"user_id": user_id, "scraped": 0, "skipped": "no_channel"}
    channel = ch.data[0]

    session_str = decrypt(acct.data[0]["session_encrypted"])

    parsed = await scrape_channel(
        session_str=session_str,
        tg_channel_id=channel["tg_channel_id"],
        tg_access_hash=channel.get("tg_access_hash"),
        min_msg_id=channel.get("last_scraped_msg_id") or 0,
    )

    if not parsed:
        sb.table("channels").update({"last_synced_at": "now()"}).eq("id", channel["id"]).execute()
        return {"user_id": user_id, "scraped": 0}

    rows = [{
        "user_id": user_id,
        "channel_id": channel["id"],
        "tg_msg_id": p.tg_msg_id,
        "category": p.category,
        "question": p.question,
        "options": p.options,
        "correct_answer": p.correct_answer,
        "source_date": p.source_date.isoformat(),
    } for p in parsed]

    sb.table("mcqs").upsert(rows, on_conflict="channel_id,tg_msg_id").execute()

    max_msg_id = max(p.tg_msg_id for p in parsed)
    sb.table("channels").update({
        "last_scraped_msg_id": max_msg_id,
        "last_synced_at": "now()",
    }).eq("id", channel["id"]).execute()

    return {"user_id": user_id, "scraped": len(rows)}


@router.post("/me")
async def scrape_me(user_id: str = Depends(current_user_id)):
    ratelimit.check(user_id, "scrape", limit=10, window_seconds=600)
    try:
        return await _scrape_for_user(user_id)
    except Exception:
        log.exception("scrape_me failed")
        raise HTTPException(400, "Scrape failed")


@router.post("/all", dependencies=[Depends(require_cron_secret)])
async def scrape_all():
    sb = service_client()
    users = sb.table("channels").select("user_id").execute()
    results = []
    for row in users.data or []:
        try:
            results.append(await _scrape_for_user(row["user_id"]))
        except Exception as e:
            results.append({"user_id": row["user_id"], "error": str(e)})
    return {"results": results}
