"""Multilingual query understanding: entities + intent + confidence.
Handles Hindi numerals, units (मीटर/sqm), and use-types."""
import re

DEVA_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")

USE_TYPES = {
    "residential": ["residence", "residential", "house", "ghar", "घर", "मकान", "आवास"],
    "commercial": ["shop", "store", "factory", "commercial", "trade", "business", "दुकान"],
    "farmhouse": ["farm", "फार्म"],
    "industrial": ["industrial", "factory"],
}

INTENTS = {
    "front_setback": ["front", "सामने", "आगे"],
    "rear_setback": ["rear", "पीछे"],
    "fee": ["fee", "fees", "फीस", "शुल्क"],
    "validity": ["valid", "renew", "revalid", "अवधि", "नवीनीकरण"],
    "electric": ["electric", "बिजली", "overhead", "volt", "balcony", "बालकनी"],
    "lift": ["lift", "लिफ्ट", "escalator"],
    "farmhouse": ["farm house", "farmhouse", "फार्म"],
    "documents": ["document", "appendix", "apply", "application", "आवेदन"],
    "sign": ["sign", "architect", "submit", "हस्ताक्षर"],
    "plan_change": ["change", "alteration", "deviation", "modify", "sanctioned"],
}


def normalize(query: str) -> str:
    q = query.translate(DEVA_DIGITS)
    q = q.replace("वर्ग मीटर", "sqm").replace("वर्गमीटर", "sqm")
    q = q.replace("मीटर", "m").replace("मी.", "m")
    return q


def parse_hint(query: str) -> dict:
    q = normalize(query)
    ql = q.lower()
    ent = {}
    m = re.search(r"(\d+(?:\.\d+)?)\s*m\b[^\d]{0,25}(?:road|street|सड़क|front|सामने|आगे|चौड़ी|wide)", q, re.I)
    if m:
        ent["road_width_m"] = float(m.group(1))
    else:
        m = re.search(r"(?:road|street|सड़क)[^\d]{0,20}(\d+(?:\.\d+)?)\s*m", q, re.I)
        if m:
            ent["road_width_m"] = float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq\s?m|sqm)", q, re.I)
    if m:
        ent["area_sqm"] = float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*m\b[^\d]{0,25}(?:tall|height|high|ऊंच|taller)", q, re.I)
    if m:
        try:
            ent["height_m"] = float(m.group(1))
        except ValueError:
            pass
    for use, kws in USE_TYPES.items():
        if any(k in ql for k in kws):
            ent["use"] = use
            break
    intents = [name for name, kws in INTENTS.items() if any(k in ql for k in kws)]
    ent["intents"] = intents
    ent["confidence"] = "high" if intents and (("road_width_m" in ent) or ("area_sqm" in ent) or len(intents) == 1) else ("medium" if intents else "low")
    # clarifying question for low info
    if ent["confidence"] == "low" or (any(i in intents for i in ("front_setback", "rear_setback")) and not ent.get("road_width_m") and not ent.get("area_sqm")):
        ent["needs"] = "road width (m) and plot area (sqm)"
    return ent
