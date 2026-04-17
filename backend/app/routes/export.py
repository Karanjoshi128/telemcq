from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from ..core.deps import current_user_id
from ..core.supabase import service_client
from ..docx_builder import build_docx

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/docx")
async def export_docx(user_id: str = Depends(current_user_id)):
    sb = service_client()

    user_res = sb.auth.admin.get_user_by_id(user_id)
    email = user_res.user.email if user_res and user_res.user else ""

    ch = sb.table("channels").select("title").eq("user_id", user_id).execute()
    channel_title = ch.data[0]["title"] if ch.data else "(no channel)"

    mcqs = sb.table("mcqs").select(
        "id, category, question, options, correct_answer, source_date"
    ).eq("user_id", user_id).order("source_date").execute()

    answers = sb.table("user_answers").select("mcq_id, selected_answer").eq("user_id", user_id).execute()
    ans_map = {a["mcq_id"]: a["selected_answer"] for a in (answers.data or [])}

    if not mcqs.data:
        raise HTTPException(404, "No MCQs yet — run a sync first.")

    content = build_docx(email, channel_title, mcqs.data, ans_map)
    filename = f"TeleMCQ-{channel_title.replace(' ', '_')}.docx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
