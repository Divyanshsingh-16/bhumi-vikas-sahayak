"""1-page counter slip: answer + rule + quote + version. ReportLab if present, else text."""
from datetime import datetime


def slip_text(query, res, lang="en") -> str:
    lines = [
        "BHUMI VIKAS SAHAYAK — Counter Slip",
        f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        f"Q: {query}",
        f"A: {res['answer'][:600]}",
    ]
    if res.get("rule"):
        lines += [f"Rule: {res['rule']} | Pages: {res['pages'][0]}-{res['pages'][1]}",
                  f"Quote: \"{res['quote']}\""]
    lines += ["Source: MP Bhumi Vikas Rules 2012 upto 06-03-2025; 28-08-2026 patch check needed for <=500 sqm.",
              "Tool points; clerk decides. Not legal advice."]
    return "\n".join(lines)


def slip_pdf_bytes(query, res) -> bytes | None:
    try:
        from reportlab.lib.pagesizes import A5
        from reportlab.pdfgen import canvas
        from io import BytesIO
    except ImportError:
        return None
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A5)
    y = 540
    c.setFont("Helvetica-Bold", 12)
    c.drawString(30, y, "Bhumi Vikas Sahayak — Counter Slip")
    c.setFont("Helvetica", 9)
    for line in slip_text(query, res).split("\n")[1:]:
        y -= 16
        for chunk in [line[i:i+95] for i in range(0, len(line), 95)]:
            c.drawString(30, y, chunk[:95])
            y -= 13
            if y < 40:
                c.showPage()
                y = 540
    c.save()
    return buf.getvalue()
