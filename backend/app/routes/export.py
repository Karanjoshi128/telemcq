from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from ..core.deps import current_user_id
from ..core.supabase import service_client
from ..docx_builder import build_docx

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/docx")
async def export_docx(
    start: int = Query(1, ge=1),
    end: int | None = Query(None, ge=1),
    user_id: str = Depends(current_user_id),
):
    sb = service_client()

    user_res = sb.auth.admin.get_user_by_id(user_id)
    email = user_res.user.email if user_res and user_res.user else ""

    ch = (
        sb.table("channels")
        .select("id, title")
        .eq("user_id", user_id)
        .execute()
    )
    if not ch.data:
        raise HTTPException(400, "No channel selected")
    channel = ch.data[0]

    total_res = (
        sb.table("mcqs")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    total = total_res.count or 0
    if total == 0:
        raise HTTPException(404, "No MCQs yet — run Sync first.")

    effective_end = min(end or total, total)
    if start > total:
        raise HTTPException(400, f"Start ({start}) is beyond total ({total})")
    if start > effective_end:
        raise HTTPException(400, "Start must be <= end")

    mcqs = (
        sb.table("mcqs")
        .select("id, category, question, options, correct_answer, source_date")
        .eq("user_id", user_id)
        .order("source_date")
        .range(start - 1, effective_end - 1)
        .execute()
    )

    if not mcqs.data:
        raise HTTPException(404, "No MCQs in that range")

    answers_res = (
        sb.table("user_answers")
        .select("mcq_id, selected_answer")
        .eq("user_id", user_id)
        .execute()
    )
    answer_map = {a["mcq_id"]: a["selected_answer"] for a in (answers_res.data or [])}

    is_range = start > 1 or effective_end < total
    subtitle = (
        f"Questions {start}-{effective_end} of {total}"
        if is_range
        else f"All MCQs ({total})"
    )

    content = build_docx(
        user_email=email,
        channel_title=channel["title"],
        mcqs=mcqs.data,
        user_answers=answer_map,
        subtitle=subtitle,
    )

    sb.table("channels").update({"last_exported_at": "now()"}).eq("id", channel["id"]).execute()

    range_suffix = f"-Q{start}-{effective_end}" if is_range else ""
    filename = f"TeleMCQ-{channel['title'].replace(' ', '_')}{range_suffix}.docx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
