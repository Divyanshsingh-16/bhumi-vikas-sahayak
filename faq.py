"""Top-10 clerk FAQ: instant deterministic answers, zero retrieval.
Each entry: keywords -> (rule, pages, answer_en, answer_hi). Checked vs EN PDF."""

FAQ = [
    (("front", "gap", "setback", "sadak", "road"), ("56", "77",
        "Front gap depends on road: up to 9m→3.0m; 9-12m→3.6m; 12-18m→4.5m; above 18m→6.0m (Rule 56).",
        "सड़क 9मी तक→3.0मी; 9-12→3.6; 12-18→4.5; 18 से ऊपर→6.0मी (नियम 56)।")),
    (("rear", "peeche", "peechhe"), ("56", "78",
        "Rear gap by plot: up to 40→Nil; 40-150→1.5m; 150-225→2.5m; above 225→3.0m (Rule 56).",
        "40 तक→शून्य; 40-150→1.5मी; 150-225→2.5मी; 225 से ऊपर→3.0मी (नियम 56)।")),
    (("fee", "fees", "fees", "shulk"), ("21", "36",
        "Residential fee by built-up slabs (Rule 21): 0-75→Rs750; 76-125→1250; 126-200→2000; above 2500→50000. Shops +50%.",
        "आवासीय शुल्क (नियम 21): 0-75→₹750; 76-125→1250; 126-200→2000; 2500 से ऊपर→50000। दुकान +50%।")),
    (("valid", "renew", "avadhi"), ("23", "41",
        "Permission valid 3 years; renew 2 times x 1 year; then fresh (Rule 23).",
        "अनुमति 3 साल; 2 बार 1-1 साल नवीनीकरण; फिर नया प्रस्ताव (नियम 23)।")),
    (("lift",), ("83", "95",
        "Lift compulsory above 12.5 m height, per NBC with registration + 6-monthly audit (Rule 83).",
        "12.5 मी से ऊपर लिफ्ट अनिवार्य, पंजीकरण + छमाही ऑडिट सहित (नियम 83)।")),
    (("farm",), ("17", "34",
        "Farmhouse: min 0.40 ha plot, FAR 0.10, height 7.5m sloping roof, 7.5m open all sides, 100 trees/ha first (Rule 17).",
        "फार्म हाउस: न्यूनतम 0.40 हे., FAR 0.10, 7.5मी ढलवां छत, चारों ओर 7.5मी, पहले 100 पेड़/हे. (नियम 17)।")),
    (("electric", "bijli", "wire", "taar"), ("52", "69",
        "Low/medium wires: 2.5m above, 1.2m sideways. Above 33000V: 15m corridor (Rule 52).",
        "सामान्य तार: 2.5मी ऊपर, 1.2मी बगल। 33000V से ऊपर: 15मी गलियारा (नियम 52)।")),
    (("document", "kagaz", "paper"), ("14", "22",
        "Form A-1 (development) or A-2 (building) + fee receipt + ownership proof + plans (Rule 14).",
        "फॉर्म A-1 (विकास) या A-2 (भवन) + शुल्क रसीद + स्वामित्व प्रमाण + योजना (नियम 14)।")),
    (("sign", "sign", "hastakshar"), ("18", "34",
        "Plans signed by Architect/Engineer/Supervisor/Town Planner with licence number + owner (Rule 18).",
        "योजना पर आर्किटेक्ट/इंजीनियर + स्वामी के हस्ताक्षर, लाइसेंस नंबर सहित (नियम 18)।")),
    (("deemed", "no reply", "jawab nahi"), ("28", "49",
        "No written refusal in time = deemed sanctioned; nothing illegal allowed (Rule 28).",
        "समय पर लिखित मना नहीं = मानित स्वीकृति; अवैध कार्य नहीं (नियम 28)।")),
]


def faq_lookup(query: str):
    q = query.lower()
    best, best_n = None, 0
    for keys, val in FAQ:
        n = sum(1 for k in keys if k in q)
        if n > best_n:
            best, best_n = val, n
    return best if best_n else None
