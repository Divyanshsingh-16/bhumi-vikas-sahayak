"""Deterministic bilingual answers for top intents.
Used ALWAYS (offline and LLM modes) to guarantee numbers + perfect Hindi.
LLM output is kept as 'detail'; template is the trusted headline."""

TEMPLATES = {
    "front_setback": {
        "en": "Front open space: {value} m (road {road} m wide). Rule 56(1)(a), PDF p.77.",
        "hi": "सामने की खुली जगह: {value} मीटर (सड़क {road} मीटर चौड़ी)। नियम 56(1)(a), PDF पृ.77।",
    },
    "rear_setback": {
        "en": "Rear open space: {value} m ({nil}for {area} sq m plot). Rule 56(2)(a), PDF p.78.",
        "hi": "पीछे की खुली जगह: {value} मीटर ({area} वर्ग मीटर प्लॉट)। नियम 56(2)(a), PDF पृ.78।",
    },
    "electric": {
        "en": "Balcony/electric clearance: {v} m vertical, {h} m horizontal. Rule 52, PDF p.69.",
        "hi": "बालकनी/बिजली दूरी: {v} मीटर ऊपर, {h} मीटर बगल। नियम 52, PDF पृ.69।",
    },
    "farmhouse": {
        "en": "Farm house: min plot 0.40 hectare, max FAR 0.10, height 7.5 m (sloping roof), 7.5 m open space all sides. Rule 17, PDF p.34.",
        "hi": "फार्म हाउस: न्यूनतम प्लॉट 0.40 हेक्टेयर, अधिकतम FAR 0.10, ऊंचाई 7.5 मी (ढलवां छत), चारों ओर 7.5 मी खुली जगह। नियम 17, PDF पृ.34।",
    },
    "validity": {
        "en": "Development permission valid 3 years; revalidation 2 × 1 year, then fresh proposal (max 5 years). Rule 23, PDF p.41.",
        "hi": "विकास अनुमति 3 साल वैध; नवीनीकरण 2 बार 1-1 साल, फिर नया प्रस्ताव (अधिकतम 5 साल)। नियम 23, PDF पृ.41।",
    },
    "lift": {
        "en": "Lift provision required above 12.5 m height (NBC Part-VIII Sec-5; details in Appendix A-2(A)). Rule 83, PDF p.95.",
        "hi": "12.5 मीटर से ऊंची इमारत में लिफ्ट जरूरी (NBC भाग-VIII खंड-5; विवरण परिशिष्ट A-2(A))। नियम 83, PDF पृ.95।",
    },
    "conversion": {
        "en": "1 hectare = 10,000 sq m = 2.471 acre; 1 sq m = 10.764 sq ft. (Helper math; development application fee Rs 5,000/hectare — Rule 21(2).)",
        "hi": "1 हेक्टेयर = 10,000 वर्ग मीटर = 2.471 एकड़; 1 वर्ग मीटर = 10.764 वर्ग फुट। (विकास आवेदन शुल्क ₹5,000/हेक्टेयर — नियम 21(2)।)",
    },
    "documents": {
        "en": "Building application: Appendix A-2/A-2(1) with fee receipt, ownership proof, plans + sections (Rule 14); key/site/layout/service plans + project report for development (Rule 16).",
        "hi": "भवन आवेदन: परिशिष्ट A-2/A-2(1), शुल्क रसीद, स्वामित्व प्रमाण, योजना + काट-चित्र सहित (नियम 14); विकास हेतु मुख्य/स्थल/ले-आउट/सेवा योजना + परियोजना रिपोर्ट (नियम 16)।",
    },
    "sign": {
        "en": "Plans must be prepared and signed by Architect/Structural Engineer/Engineer/Supervisor/Town Planner with name, address, qualification, licence number + validity; owner signs too (Rule 18). Building permission may go via authorised Architect/Structural Engineer (Rule 26-B).",
        "hi": "योजना आर्किटेक्ट/स्ट्रक्चरल इंजीनियर/इंजीनियर/सुपरवाइजर/टाउन प्लानर द्वारा नाम, पता, योग्यता, लाइसेंस नंबर + वैधता सहित तैयार व हस्ताक्षरित हो; स्वामी भी हस्ताक्षर करे (नियम 18)। भवन अनुमति अधिकृत आर्किटेक्ट/इंजीनियर से भी (नियम 26-B)।",
    },
    "plan_change": {
        "en": "No deviation from sanctioned plan is allowed if it affects front open space, exceeds 30% of permissible FAR, or hits parking/road/water-body (Rule 24). Alteration applications need only affected plans (Rule 19).",
        "hi": "स्वीकृत योजना से विचलन अनुमत नहीं यदि सामने की खुली जगह प्रभावित हो, FAR 30% से अधिक बढ़े, या पार्किंग/सड़क/जलाशय प्रभावित हो (नियम 24)। परिवर्तन हेतु केवल प्रभावित योजना चाहिए (नियम 19)।",
    },
    "deemed": {
        "en": "If the Authority does not intimate refusal in writing within the Section 30(5) period, permission is deemed sanctioned — but nothing illegal/anti-plan is authorised (Rule 28, PDF p.49).",
        "hi": "यदि प्राधिकारी धारा 30(5) की अवधि में लिखित अस्वीकृति न दे तो अनुमति स्वीकृत मानी जाती है — पर अवैध/योजना-विरुद्ध कार्य अधिकृत नहीं (नियम 28, PDF पृ.49)।",
    },
    "precedence": {
        "en": "Plan-area norms are as in the Development Plan; if the Plan and these rules differ, the Director examines and sends a proposal to Government, whose decision applies (Rule 103, PDF p.107).",
        "hi": "योजना क्षेत्र के मानक विकास योजना अनुसार; योजना और इन नियमों में भिन्नता हो तो निदेशक शासन को प्रस्ताव भेजते हैं, शासन का निर्णय लागू होता है (नियम 103, PDF पृ.107)।",
    },
    "instant": {
        "en": "Instant/deemed approval: residential plots up to 186 sq m in an approved layout, individual holder only (not colonisers). Apply in Appendix A-2(2) + affidavit A-2(3) with Rule 21 fee — submission itself is deemed sanction; violation auto-cancels it (Rule 12-A, PDF p.21).",
        "hi": "तुरंत/मानित स्वीकृति: अनुमोदित ले-आउट में 186 वर्ग मीटर तक के आवासीय प्लॉट, केवल व्यक्तिगत धारक (कॉलोनाइज़र नहीं)। परिशिष्ट A-2(2) + शपथपत्र A-2(3) व नियम 21 शुल्क सहित आवेदन ही मानित स्वीकृति है; उल्लंघन पर स्वतः निरस्त (नियम 12-A, PDF पृ.21)।",
    },
    "standard_plan": {
        "en": "Standard plans: for plots up to 300 sq m in an approved layout, pick an Authority-approved standard plan — the fee receipt counts as building permission (Rule 21(4), PDF p.38).",
        "hi": "मानक योजना: अनुमोदित ले-आउट में 300 वर्ग मीटर तक के प्लॉट हेतु स्वीकृत मानक योजना चुनें — शुल्क रसीद ही भवन अनुमति मानी जाएगी (नियम 21(4), PDF पृ.38)।",
    },
    "competence": {
        "en": "Who may submit: Architect — all buildings; Structural Engineer — residential up to 500 sq m / 3 storeys / 11 m; Engineer — residential up to 300 sq m / 2 storeys / 7.5 m; Supervisor — residential up to 200 sq m / 2 storeys / 7.5 m (Rule 26(9), PDF p.45-46).",
        "hi": "कौन प्रस्तुत करे: आर्किटेक्ट — सभी भवन; स्ट्रक्चरल इंजीनियर — 500 वर्ग मीटर/3 मंजिल/11 मी तक आवासीय; इंजीनियर — 300 वर्ग मीटर/2 मंजिल/7.5 मी तक; सुपरवाइजर — 200 वर्ग मीटर/2 मंजिल/7.5 मी तक (नियम 26(9), PDF पृ.45-46)।",
    },
    "occupancy": {
        "en": "Occupancy: apply in Appendix E-4 before occupying; Authority decides in 30 days, else deemed issued (Rule 31(2)(g)-(h), PDF p.49-50). Completion certificate per sanctioned plan first (Rule 102).",
        "hi": "अधिभोग: रहने से पहले परिशिष्ट E-4 में आवेदन; प्राधिकारी 30 दिन में निर्णय दे अन्यथा मानित जारी (नियम 31(2)(g)-(h), PDF पृ.49-50)। पहले स्वीकृत योजना अनुसार पूर्णता प्रमाणपत्र (नियम 102)।",
    },
    "inspection": {
        "en": "Inspection: after plinth notice, inspection within 7 days (then work may continue per plan); final inspection within 21 days of completion notice; stop-work if unsafe (Rule 33, PDF p.50-51).",
        "hi": "निरीक्षण: प्लिंथ सूचना पर 7 दिन में निरीक्षण (फिर योजना अनुसार कार्य जारी); पूर्णता सूचना पर 21 दिन में अंतिम निरीक्षण; असुरक्षित पर रोक (नियम 33, PDF पृ.50-51)।",
    },
    "far": {
        "en": "FAR limits: residential 1.25; commercial 2.50/2.00/1.75/1.50/1.25 by centre tier; public 1.00 (Rule 61 Table 8, PDF p.83; town plan may adopt its own).",
        "hi": "FAR सीमा: आवासीय 1.25; वाणिज्यिक 2.50/2.00/1.75/1.50/1.25 (केंद्र श्रेणी अनुसार); सार्वजनिक 1.00 (नियम 61 तालिका 8, PDF पृ.83)।",
    },
    "side_setback": {
        "en": "Side open space: detached 3 m both sides (if frontage <12 m and height ≤7 m: 3 m + 1.5 m); semi-detached 3 m one side (2.5 m if frontage ≤10 m, height ≤10 m); row-type nil (Rule 56(3), PDF p.78).",
        "hi": "बगल की खुली जगह: पृथक भवन दोनों ओर 3 मी (अग्रभाग <12 मी व ऊंचाई ≤7 मी: 3 मी + 1.5 मी); अर्ध-पृथक एक ओर 3 मी; पंक्ति भवन शून्य (नियम 56(3), PDF पृ.78)।",
    },
    "plot300": {
        "en": "Verdict: under the March-2025 rules, a 300 sq m plot in an approved layout could use an authorised Architect/Structural Engineer (Rule 6(3)) or standard plans (Rule 21(4)) — BUT the 28-08-2026 amendment to Rule 2(5)(c) changed plots up to 500 sq m. Do NOT decide on old rules alone; confirm the August-2026 position with the Authority.",
        "hi": "निर्णय: मार्च-2025 नियमों में 300 वर्ग मीटर प्लॉट हेतु अधिकृत आर्किटेक्ट (नियम 6(3)) या मानक योजना (नियम 21(4)) का रास्ता था — पर 28-08-2026 संशोधन (नियम 2(5)(c), 500 वर्ग मीटर तक) के बाद पुराने नियमों पर निर्णय न लें; प्राधिकारी से अगस्त-2026 स्थिति जांचें।",
    },
}

# Second-rule synthesis: shown right after the headline (EN+HI same-language pick).
SECONDARY = {
    "deemed": {
        "en": "Exception: delay at an authorised Architect/Structural Engineer is NOT deemed sanction (Rule 28 proviso).",
        "hi": "अपवाद: अधिकृत आर्किटेक्ट/इंजीनियर की देरी मानित स्वीकृति नहीं (नियम 28 परंतुक)।",
    },
    "sign": {
        "en": "Size limits: Structural Engineer ≤500 sq m/3 storeys, Engineer ≤300 sq m/2 storeys, Supervisor ≤200 sq m/2 storeys (Rule 26(9)).",
        "hi": "सीमा: स्ट्रक्चरल इंजीनियर ≤500 वर्ग मीटर/3 मंजिल, इंजीनियर ≤300/2, सुपरवाइजर ≤200/2 (नियम 26(9))।",
    },
    "documents": {
        "en": "Tip: earthquake-area certificates (A-3 to A-11) ride along where applicable (Rule 15).",
        "hi": "सुझाव: भूकंप क्षेत्र प्रमाणपत्र (A-3 से A-11) लागू हो तो साथ लगेंगे (नियम 15)।",
    },
    "plan_change": {
        "en": "Related: alteration needs only the affected plans (Rule 19).",
        "hi": "संबंधित: परिवर्तन हेतु केवल प्रभावित योजना चाहिए (नियम 19)।",
    },
    "validity": {
        "en": "Fee note: revalidation after expiry costs the Rule 21(3)(a) fee; before expiry it is free (Rule 23).",
        "hi": "शुल्क: समाप्ति के बाद नवीनीकरण पर नियम 21(3)(a) शुल्क; पहले निःशुल्क (नियम 23)।",
    },
    "front_setback": {
        "en": "Also check: side gaps (Rule 56(3)) and projections like balcony ≤1.2 m (Rule 58).",
        "hi": "साथ देखें: बगल की जगह (नियम 56(3)) व बालकनी ≤1.2 मी (नियम 58)।",
    },
    "rear_setback": {
        "en": "Also check: side gaps (Rule 56(3)) and projections like balcony ≤1.2 m (Rule 58).",
        "hi": "साथ देखें: बगल की जगह (नियम 56(3)) व बालकनी ≤1.2 मी (नियम 58)।",
    },
}

# One plain citizen-facing line per kind (simpler than the clerk headline).
CITIZEN = {
    "front_setback": {"en": "Tell the citizen: leave this much gap in front, it is part of your plot.",
                      "hi": "नागरिक से कहें: सामने इतनी जगह छोड़नी है, यह आपके प्लॉट का हिस्सा है।"},
    "rear_setback": {"en": "Tell the citizen: leave this much gap at the back.",
                     "hi": "नागरिक से कहें: पीछे इतनी जगह छोड़नी है।"},
    "electric": {"en": "Tell the citizen: keep the balcony this far from the wire, for safety.",
                 "hi": "नागरिक से कहें: सुरक्षा हेतु बालकनी तार से इतनी दूर रखें।"},
    "farmhouse": {"en": "Tell the citizen: farmhouse needs a big plot with 100 trees per hectare first.",
                  "hi": "नागरिक से कहें: फार्म हाउस हेतु बड़ा प्लॉट व पहले 100 पेड़/हेक्टेयर चाहिए।"},
    "validity": {"en": "Tell the citizen: start work in time or renew before 3 years end.",
                 "hi": "नागरिक से कहें: समय पर कार्य शुरू करें या 3 साल से पहले नवीनीकरण कराएं।"},
    "lift": {"en": "Tell the citizen: a lift is compulsory above 12.5 m height.",
             "hi": "नागरिक से कहें: 12.5 मीटर से ऊपर लिफ्ट अनिवार्य है।"},
    "instant": {"en": "Tell the citizen: your application itself becomes the approval — but any violation cancels it.",
                "hi": "नागरिक से कहें: आपका आवेदन ही स्वीकृति है — पर उल्लंघन पर निरस्त हो जाएगी।"},
    "standard_plan": {"en": "Tell the citizen: pick a ready-made approved design and the receipt is your permission.",
                      "hi": "नागरिक से कहें: तैयार स्वीकृत डिज़ाइन चुनें, रसीद ही अनुमति है।"},
    "competence": {"en": "Tell the citizen: only the listed professional may sign for this size.",
                   "hi": "नागरिक से कहें: इस आकार हेतु केवल सूचीबद्ध पेशेवर हस्ताक्षर कर सकता है।"},
    "occupancy": {"en": "Tell the citizen: do not occupy before the E-4 permission.",
                  "hi": "नागरिक से कहें: E-4 अनुमति से पहले रहना शुरू न करें।"},
    "plot300": {"en": "Tell the citizen: rules changed in August 2026 — the counter will confirm the latest position.",
                "hi": "नागरिक से कहें: अगस्त 2026 में नियम बदले — काउंटर नवीनतम स्थिति बताएगा।"},
}

# Follow-up chips per kind: (button label, query to ask).
FOLLOWUPS = {
    "front_setback": [("Rear gap?", "What is the rear open space for this plot?"),
                      ("Fee?", "What is the building permission fee?")],
    "rear_setback": [("Front gap?", "What is the front open space for this plot?"),
                     ("Fee?", "What is the building permission fee?")],
    "fee": [("Validity?", "How long does building permission stay valid?")],
    "validity": [("Revalidation fee?", "Revalidation fee for building permission?")],
    "electric": [("Projection rules?", "What projections are allowed in open spaces?")],
    "instant": [("Validity?", "How long does building permission stay valid?"),
                ("Standard plan?", "Can I use a standard plan?")],
    "standard_plan": [("Instant approval?", "Can I get instant approval?")],
    "documents": [("Who signs?", "Who is allowed to sign my building plans?")],
    "sign": [("Competence limits?", "Who can sign plans for a 250 sq m 2-storey house?")],
    "plan_change": [("Documents?", "What documents go with an application for building permission?")],
    "plot300": [("Standard plan?", "Can I use a standard plan?"),
                ("Instant approval?", "Can I get instant approval?")],
}


def template_answer(calc: dict, lang: str) -> str | None:
    """Return headline string or None if no template for this calc kind."""
    if not calc:
        return None
    t = TEMPLATES.get(calc.get("kind"))
    if not t:
        return None
    s = t["hi" if lang == "hi" else "en"]
    try:
        if calc["kind"] == "front_setback":
            return s.format(value=calc["value_m"], road=calc["road_width_m"])
        if calc["kind"] == "rear_setback":
            v = "Nil" if calc["value_m"] == 0 else f"{calc['value_m']} m"
            vh = "शून्य" if calc["value_m"] == 0 else f"{calc['value_m']} मीटर"
            return s.format(value=vh if lang == "hi" else v,
                            nil="" if lang == "en" else "",
                            area=calc["plot_area_sqm"])
        if calc["kind"] == "electric":
            v = calc.get("vertical") or "—"
            return s.format(v=v, h=calc.get("horizontal"))
        if calc["kind"] == "competence" and calc.get("who"):
            from competence import ROLE_HI
            who = calc["who"]
            if lang == "hi":
                names = ", ".join(ROLE_HI.get(w, w) for w in who)
                extra = f" | इस काम हेतु: {names}"
                if calc.get("plot"):
                    extra += f" ({calc['plot']} वर्ग मीटर"
                    if calc.get("storeys"):
                        extra += f", {calc['storeys']} मंजिल"
                    extra += ")"
                return s + extra
            extra = f" | For this job: {', '.join(who)}"
            if calc.get("plot"):
                extra += f" ({calc['plot']} sqm"
                if calc.get("storeys"):
                    extra += f", {calc['storeys']} storeys"
                extra += ")"
            return s + extra
        return s
    except KeyError:
        return s
