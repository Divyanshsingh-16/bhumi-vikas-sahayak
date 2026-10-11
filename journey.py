"""Application journey stepper: apply -> inspect -> sanction -> build -> occupy.
Each step shows timeline + deemed flags (Rules 28/31/33/100/101). EN+HI."""

STEPS = [
    {"en": "Apply (A-1/A-2 + fee receipt)", "hi": "आवेदन (A-1/A-2 + शुल्क रसीद)",
     "rule": "14", "detail_en": "Appendix A-1 (development) or A-2/A-2(1) (building), with ownership proof + plans.",
     "detail_hi": "परिशिष्ट A-1 (विकास) या A-2/A-2(1) (भवन), स्वामित्व प्रमाण + योजना सहित।"},
    {"en": "Inspection (7 days / 21 days)", "hi": "निरीक्षण (7 दिन / 21 दिन)",
     "rule": "33", "detail_en": "Plinth notice → inspect in 7 days (then continue); final check in 21 days.",
     "detail_hi": "प्लिंथ सूचना → 7 दिन में निरीक्षण (फिर कार्य जारी); 21 दिन में अंतिम जांच।"},
    {"en": "Sanction / deemed (Sec 30(5))", "hi": "स्वीकृति / मानित (धारा 30(5))",
     "rule": "28", "detail_en": "No written refusal in time → deemed sanctioned (nothing illegal authorised).",
     "detail_hi": "समय पर लिखित अस्वीकृति नहीं → मानित स्वीकृति (अवैध कार्य अधिकृत नहीं)।"},
    {"en": "Build + plinth certificate", "hi": "निर्माण + प्लिंथ प्रमाणपत्र",
     "rule": "100", "detail_en": "High-rise: plinth check certificate; 15 days else deemed.",
     "detail_hi": "उच्च भवन: प्लिंथ जांच प्रमाणपत्र; 15 दिन अन्यथा मानित।"},
    {"en": "Completion + occupancy (30 days)", "hi": "पूर्णता + अधिभोग (30 दिन)",
     "rule": "31", "detail_en": "Completion certificate per plan, then E-4 occupancy; 30 days else deemed.",
     "detail_hi": "योजना अनुसार पूर्णता प्रमाणपत्र, फिर E-4 अधिभोग; 30 दिन अन्यथा मानित।"},
]


def journey_html(lang: str = "en", done: int = 0) -> str:
    dots = []
    for i, s in enumerate(STEPS):
        cls = "done" if i < done else ("now" if i == done else "todo")
        color = {"done": "#2e7d32", "now": "#ef6c00", "todo": "#bdbdbd"}[cls]
        dots.append(
            f"<div style='flex:1;text-align:center'>"
            f"<div style='width:34px;height:34px;margin:0 auto;border-radius:50%;background:{color};"
            f"color:white;font-weight:bold;line-height:34px'>{i+1}</div>"
            f"<div style='font-size:12px;margin-top:4px'>{s['hi' if lang=='hi' else 'en']}</div>"
            f"<div style='font-size:11px;color:#666'>Rule {s['rule']}</div></div>")
        if i < len(STEPS) - 1:
            dots.append("<div style='flex:0 0 12px;height:2px;background:#ccc;margin-top:16px'></div>")
    return f"<div style='display:flex;align-items:flex-start'>{''.join(dots)}</div>"
