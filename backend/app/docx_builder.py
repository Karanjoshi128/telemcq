import io
from datetime import datetime

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor


def _option_text(opts: list[dict], key: str | None) -> str:
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
    incremental: bool = False,
    subtitle: str | None = None,
) -> bytes:
    """Produce an answer-key style DOCX.

    Each question shows its options and the correct answer in green.
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

    subtitle_para = doc.add_paragraph()
    subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if subtitle is None:
        subtitle = "New MCQs since last export" if incremental else "All MCQs"
    st = subtitle_para.add_run(subtitle)
    st.italic = True
    st.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.add_run(f"Channel: {channel_title}\n").bold = True
    meta.add_run(f"User: {user_email}\n")
    meta.add_run(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n")
    meta.add_run(f"Total MCQs: {len(mcqs)}")

    doc.add_page_break()

    current_category: object | str = object()
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

        correct = m.get("correct_answer")

        for opt in m["options"]:
            p = doc.add_paragraph(style="List Bullet")
            p.paragraph_format.left_indent = Pt(18)
            run = p.add_run(f"{opt['key']}) {opt['text']}")
            if correct and opt["key"] == correct:
                run.bold = True
                run.font.color.rgb = RGBColor(0x00, 0x80, 0x00)

        if correct:
            ans_line = doc.add_paragraph()
            ar = ans_line.add_run(
                f"Answer: {correct}) {_option_text(m['options'], correct)}"
            )
            ar.bold = True
            ar.font.color.rgb = RGBColor(0x00, 0x80, 0x00)
        else:
            ans_line = doc.add_paragraph()
            ar = ans_line.add_run("Answer: (not provided)")
            ar.italic = True
            ar.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

        doc.add_paragraph("")

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
