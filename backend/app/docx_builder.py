import io
from datetime import datetime

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor


def _answered_option_text(opts: list[dict], key: str | None) -> str:
    if not key:
        return ""
    for o in opts:
        if o.get("key") == key:
            return o.get("text", "")
    return ""


def build_docx(
    user_email: str,
    channel_title: str,
    mcqs: list[dict],
    user_answers: dict[str, str],
) -> bytes:
    """mcqs: list of rows from DB (id, category, question, options, correct_answer, source_date)
    user_answers: { mcq_id: selected_key }
    """
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    # Cover
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("TeleMCQ Export")
    run.bold = True
    run.font.size = Pt(24)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(f"Channel: {channel_title}\n").bold = True
    meta.add_run(f"User: {user_email}\n")
    meta.add_run(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
    meta.add_run(f"Total MCQs: {len(mcqs)}")

    doc.add_page_break()

    current_category = object()
    for n, m in enumerate(mcqs, 1):
        cat = m.get("category") or "Uncategorised"
        if cat != current_category:
            current_category = cat
            h = doc.add_paragraph()
            hr = h.add_run(cat)
            hr.bold = True
            hr.font.size = Pt(14)
            hr.font.color.rgb = RGBColor(0x00, 0x6E, 0xC1)

        q = doc.add_paragraph()
        qr = q.add_run(f"Q{n}. {m['question']}")
        qr.bold = True
        qr.font.size = Pt(12)

        for opt in m["options"]:
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Pt(18)
            p.add_run(f"{opt['key']}) {opt['text']}")

        selected = user_answers.get(m["id"])
        correct = m.get("correct_answer")

        if selected:
            sel_line = doc.add_paragraph()
            sr = sel_line.add_run(f"Your answer: {selected}) {_answered_option_text(m['options'], selected)}")
            sr.italic = True
            if correct:
                sr.font.color.rgb = (
                    RGBColor(0x00, 0x80, 0x00) if selected == correct else RGBColor(0xC0, 0x00, 0x00)
                )

        if correct and selected:
            c_line = doc.add_paragraph()
            cr = c_line.add_run(f"Correct: {correct}) {_answered_option_text(m['options'], correct)}")
            cr.bold = True
            cr.font.color.rgb = RGBColor(0x00, 0x80, 0x00)

        doc.add_paragraph("")

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
