"""Component catalog: 18 rule-grounded building components.
Each entry: rule, clause, PDF page, check(proposal)->(ok|None, note).
Numbers transcribed from the EN PDF consolidated upto 06-03-2025; verified by eval/grounding.py."""

COMPONENTS = [
    {"id": "balcony", "rule": "58", "clause": "58(1)(c)", "page": 81,
     "en": "Projected balcony up to 1.20 m, 1.5 m clear of plot boundary",
     "hi": "बालकनी अधिकतम 1.2 मी, सीमा से 1.5 मी अंतर",
     "check": lambda p: (p.get("balcony_m", 1.2) <= 1.2, "balcony ≤1.20 m")},
    {"id": "chhajja", "rule": "58", "clause": "58(1)(b)", "page": 81,
     "en": "Sunshade/chhajja over openings up to 0.75 m",
     "hi": "छज्जा अधिकतम 0.75 मी",
     "check": lambda p: (p.get("chhajja_m", 0.75) <= 0.75, "chhajja ≤0.75 m")},
    {"id": "parapet", "rule": "77", "clause": "77", "page": 91,
     "en": "Parapet/handrail at least 1.05 m above finished floor",
     "hi": "पैरापिट कम से कम 1.05 मी",
     "check": lambda p: (p.get("parapet_m", 1.05) >= 1.05, "parapet ≥1.05 m")},
    {"id": "staircase", "rule": "80", "clause": "80(2)-(6)", "page": 93,
     "en": "Stair width 0.85 m residential / 1.5 m others (2.0 m tall edu/institutional); "
           "tread ≥25 cm (30 cm others), riser ≤17 cm (15 cm others), headroom ≥2.2 m",
     "hi": "सीढ़ी चौड़ाई आवासीय 0.85 मी / अन्य 1.5 मी; पायदान ≥25 सेमी, राइज़र ≤17 सेमी",
     "check": lambda p: (p.get("stair_w", 0.85) >= (2.0 if p.get("tall_block") else
                         (1.5 if p.get("use") != "residential" else 0.85)), "width per Rule 80")},
    {"id": "lift", "rule": "83", "clause": "83", "page": 95,
     "en": "Lift provision compulsory above 12.5 m height (NBC); registration + 6-monthly audit",
     "hi": "12.5 मी से ऊपर लिफ्ट अनिवार्य; पंजीकरण + छमाही ऑडिट",
     "check": lambda p: ((None, "height ≤12.5 m: no lift needed") if p.get("height_m", 0) <= 12.5
                         else ((True, "lift provided") if p.get("has_lift") else
                               (None, "lift required >12.5 m — confirm provided") if "has_lift" not in p
                               else (False, "lift required >12.5 m")))},
    {"id": "ventilation_shaft", "rule": "56", "clause": "56(6)(b)", "page": 79,
     "en": "Vent shaft by height: ≤10m→1.2 sqm/0.9m side; 12.5m→2.8/1.2; 18m→4.0/1.5; "
           "24m→5.4/1.8; 30m→8.0/2.4; above 30m→9.0/3.0 (+mechanical ventilation)",
     "hi": "वेंट शाफ्ट ऊंचाई अनुसार (नियम 56(6)(b) तालिका)",
     "check": lambda p: (None, "shaft table applies where bath/WC lack open-space opening")},
    {"id": "courtyard", "rule": "56", "clause": "56(6)(a)", "page": 79,
     "en": "Inner courtyard min side 3 m; area ≥ (highest abutting wall / 5)^2; outer courtyard min width 2.4 m",
     "hi": "भीतरी आंगन न्यूनतम 3 मी; क्षेत्रफल ≥ (ऊंची दीवार/5)^2",
     "check": lambda p: (None, "courtyard geometry per 56(6)(a)")},
    {"id": "stilt_parking", "rule": "61", "clause": "61(4)", "page": 84,
     "en": "Covered parking 2.4 m clear height within ground coverage on plots ≥200 sqm; "
           "not counted in FAR/height",
     "hi": "≥200 वर्ग मी पर 2.4 मी स्टिल्ट पार्किंग; FAR/ऊंचाई में नहीं",
     "check": lambda p: (None, "stilt needs ≥200 sqm plot")},
    {"id": "basement", "rule": "76", "clause": "76(2)-(4)", "page": 90,
     "en": "Basement clear height ≥2.4 m (3.6 m commercial use); plinth ≤0.45 m above ground; "
           "not into MOS (12 m front / 7.5 m sides exception); max 3 levels (frontage 21 m, depth 30 m, road 18 m)",
     "hi": "बेसमेंट ≥2.4 मी (वाणिज्यिक 3.6 मी); प्लिंथ ≤0.45 मी",
     "check": lambda p: (None, "basement norms per 76(2)-(4)")},
    {"id": "boundary_wall", "rule": "78", "clause": "78(a)-(b)", "page": 92,
     "en": "Compound wall: front ≤1.5 m; rear/side ≤2 m (3 m on service road)",
     "hi": "चारदीवारी: सामने ≤1.5 मी; बगल/पीछे ≤2 मी",
     "check": lambda p: (p.get("wall_front_m", 1.5) <= 1.5, "front wall ≤1.5 m")},
    {"id": "gate", "rule": "41", "clause": "41(c)", "page": 58,
     "en": "Main entrance ≥4.5 m wide for non-residential/other-than-residential buildings; "
           "gate folds back against compound wall; 4.5 m clearance if built over",
     "hi": "गैर-आवासीय मुख्य द्वार ≥4.5 मी",
     "check": lambda p: (None, "gate ≥4.5 m for non-residential")},
    {"id": "garage", "rule": "75", "clause": "75(2)", "page": 90,
     "en": "Private garage ≥2.5 m x 5.0 m (≤25 sqm in rear side space per 58(4)(b))",
     "hi": "निजी गैराज ≥2.5×5.0 मी",
     "check": lambda p: (None, "garage 2.5x5.0 m")},
    {"id": "trees", "rule": "67", "clause": "67", "page": 87,
     "en": "1 tree per 100 sqm (plots ≥100 sqm); occupancy only after planting",
     "hi": "प्रति 100 वर्ग मी 1 पेड़",
     "check": lambda p: (None, "trees per Rule 67")},
    {"id": "septic_tank", "rule": "79", "clause": "79(1)-(2)", "page": 92,
     "en": "Septic ≥18 m from drinking water, ≥2 m from building; min 75 cm wide, 1 m deep, "
           "1 cum; length 2-4x width; never into open drain/water",
     "hi": "सेप्टिक: पेयजल से ≥18 मी, भवन से ≥2 मी",
     "check": lambda p: (None, "septic siting per 79")},
    {"id": "rainwater_harvesting", "rule": "81", "clause": "81(4)", "page": 93,
     "en": "Rain/roof-water harvesting compulsory on plots >140 sqm (Appendix H-1/H-2/H-3)",
     "hi": ">140 वर्ग मी पर वर्षा-जल संचयन अनिवार्य",
     "check": lambda p: (None, "RWH per 81(4)")},
    {"id": "electric_line", "rule": "52", "clause": "52(1)", "page": 69,
     "en": "LV 2.5 m vertical / 1.2 m horizontal; HV ≤33kV 3.7/1.2; EHV 15 m corridor",
     "hi": "बिजली दूरी: 2.5/1.2; 33kV तक 3.7/1.2; उस पार 15 मी",
     "check": lambda p: (None, "clearance per 52")},
    {"id": "water_body", "rule": "50", "clause": "50(b)", "page": 68,
     "en": "No construction within 9 m of water body / 15 m of river (or plan prescription)",
     "hi": "जलाशय से 9 मी / नदी से 15 मी के भीतर निर्माण नहीं",
     "check": lambda p: (None, "buffer per 50(b)")},
    {"id": "servant_quarter", "rule": "61", "clause": "61(3)", "page": 84,
     "en": "Servant quarter ≤25 sqm each (not in FAR): 1 on 200-500 sqm plots, 2 above 500 sqm",
     "hi": "सर्वेंट क्वार्टर ≤25 वर्ग मी; 200-500 पर 1, 500+ पर 2",
     "check": lambda p: (None, "servant quarter per 61(3)")},
]

BY_ID = {c["id"]: c for c in COMPONENTS}
