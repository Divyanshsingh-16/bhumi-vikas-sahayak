"""Global UI labels EN/HI. Answers already bilingual; this switches chrome + helpers."""

LABELS = {
    "tagline": {"en": "Ask the Bhopal building rulebook — get the answer with the rule number.",
                "hi": "भोपाल भवन नियमावली से पूछो — नियम नंबर सहित जवाब पाओ।"},
    "ask_ph": {"en": "Ask in English or Hindi… (mic in sidebar ☝️)",
               "hi": "अंग्रेजी या हिंदी में पूछें… (माइक बाईं ओर ☝️)"},
    "searching": {"en": "Searching the rules…", "hi": "नियम खोज रहे हैं…"},
    "exact_text": {"en": "Exact text (quote)", "hi": "मूल पाठ (उद्धरण)"},
    "print_pdf": {"en": "🖨️ Print slip (PDF)", "hi": "🖨️ पर्ची छापें (PDF)"},
    "slip_txt": {"en": "🧾 Slip (text)", "hi": "🧾 पर्ची (टेक्स्ट)"},
    "need_more": {"en": "Need one more detail", "hi": "और जानकारी दें"},
    "evidence": {"en": "PDF page {p} (source of truth)", "hi": "PDF पृष्ठ {p} (मूल स्रोत)"},
    "evidence_hint": {"en": "PDF evidence: open EN PDF at page {p} to verify.",
                      "hi": "PDF प्रमाण: सत्यापन हेतु EN PDF पृष्ठ {p} खोलें।"},
    "examples": {"en": "More examples — tap to ask:", "hi": "और उदाहरण — पूछने हेतु दबाएं:"},
    "demo_btn": {"en": "▶️ Guided demo (3 questions, ~60 sec)", "hi": "▶️ निर्देशित डेमो (3 प्रश्न, ~60 सेकंड)"},
    "steps": {"en": "① Ask ② See the rule ③ Print the slip",
              "hi": "① पूछो ② नियम देखो ③ पर्ची छापो"},
}


def t(key: str, lang: str, **kw) -> str:
    s = LABELS.get(key, {}).get(lang if lang in ("en", "hi") else "en", key)
    return s.format(**kw) if kw else s
