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


def case_report_text(case: dict) -> str:
    lines = [
        "BHUMI VIKAS SAHAYAK — Full Case Report",
        f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        f"Plot: {case.get('area')} sqm | Road: {case.get('road')} m | "
        f"Built-up: {case.get('built')} sqm ({case.get('use')})",
        f"Front gap: {case.get('front')} m (Rule 56) | Rear gap: {case.get('rear')} m (Rule 56)",
        f"Total fee: Rs {case.get('fee')} (Rule 21)",
    ]
    for label, rs in case.get("rows", []):
        lines.append(f"  {label}: Rs {rs}")
    for g in case.get("green", []):
        lines.append(f"  {g}")
    tl = case.get("timeline")
    if tl:
        lines.append(f"Valid until {tl['valid_until']}; renewals {tl['renewal_1_until']}, "
                     f"{tl['renewal_2_until']} (Rule 23)")
    lines += ["Source: MP Bhumi Vikas Rules 2012 upto 06-03-2025; Aug-2026 patch check for <=500 sqm.",
              "Tool points; clerk decides. Not legal advice."]
    return "\n".join(lines)


def case_report_pdf_bytes(case: dict) -> bytes | None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from io import BytesIO
    except ImportError:
        return None
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 780
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, y, "Bhumi Vikas Sahayak — Full Case Report")
    c.setFont("Helvetica", 10)
    for line in case_report_text(case).split("\n")[1:]:
        y -= 18
        for chunk in [line[i:i+100] for i in range(0, len(line), 100)]:
            c.drawString(40, y, chunk[:100])
            y -= 14
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = 780
    c.save()
    return buf.getvalue()
