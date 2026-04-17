from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..core.deps import current_user_id
from ..core.supabase import service_client

router = APIRouter(prefix="/mcqs", tags=["mcqs"])


@router.get("")
async def list_mcqs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    q: str | None = None,
    user_id: str = Depends(current_user_id),
):
    sb = service_client()
    frm = (page - 1) * page_size
    to = frm + page_size - 1

    query = sb.table("mcqs").select(
        "id, category, question, options, correct_answer, source_date", count="exact"
    ).eq("user_id", user_id)

    if q:
        # Reject characters that could break out of PostgREST's `or=()` filter syntax.
        # Allow alphanumerics, spaces, and common punctuation in questions. Cap length.
        safe = q.strip()[:80]
        safe = "".join(ch for ch in safe if ch.isalnum() or ch in " -._'?&")
        if safe:
            safe = safe.replace("%", r"\%").replace("_", r"\_")
            pat = f"%{safe}%"
            query = query.or_(f"question.ilike.{pat},category.ilike.{pat}")

    res = query.order("source_date", desc=False).range(frm, to).execute()

    ans = sb.table("user_answers").select("mcq_id, selected_answer").eq("user_id", user_id).execute()
    ans_map = {a["mcq_id"]: a["selected_answer"] for a in (ans.data or [])}

    for row in res.data or []:
        row["selected_answer"] = ans_map.get(row["id"])

    return {
        "items": res.data or [],
        "total": res.count or 0,
        "page": page,
        "page_size": page_size,
    }


class SubmitAnswersIn(BaseModel):
    answers: dict[str, str]  # mcq_id -> selected key


@router.post("/answers")
async def submit_answers(body: SubmitAnswersIn, user_id: str = Depends(current_user_id)):
    if not body.answers:
        return {"saved": 0}
    sb = service_client()
    rows = [
        {"user_id": user_id, "mcq_id": mid, "selected_answer": key}
        for mid, key in body.answers.items()
    ]
    sb.table("user_answers").upsert(rows, on_conflict="user_id,mcq_id").execute()
    return {"saved": len(rows)}


@router.get("/stats")
async def stats(user_id: str = Depends(current_user_id)):
    sb = service_client()
    total = sb.table("mcqs").select("id", count="exact").eq("user_id", user_id).execute()
    answered = sb.table("user_answers").select("mcq_id", count="exact").eq("user_id", user_id).execute()
    ch = sb.table("channels").select("last_synced_at, title").eq("user_id", user_id).execute()
    return {
        "total": total.count or 0,
        "answered": answered.count or 0,
        "channel_title": ch.data[0]["title"] if ch.data else None,
        "last_synced_at": ch.data[0]["last_synced_at"] if ch.data else None,
    }
