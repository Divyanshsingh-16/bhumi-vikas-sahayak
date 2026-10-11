"""Deterministic table math. Numbers come from CODE, never from LLM memory.
All values verified against EN PDF consolidated upto 06-03-2025."""
import re

# --- Rule 56(1): front open space by street width ---
def front_open_space(street_width_m: float) -> float:
    if street_width_m <= 9.0:
        return 3.0
    if street_width_m <= 12.0:
        return 3.6
    if street_width_m <= 18.0:
        return 4.5
    return 6.0

# --- Rule 56(2): rear open space by plot area ---
def rear_open_space(plot_area_sqm: float):
    if plot_area_sqm <= 40:
        return 0.0  # Nil
    if plot_area_sqm <= 150:
        return 1.5
    if plot_area_sqm <= 225:
        return 2.5
    return 3.0

# --- Rule 52: electric line clearance (meters) ---
ELECTRIC_TABLE = {
    "low": (2.5, 1.2),      # low & medium voltage + service lines
    "medium": (2.5, 1.2),
    "high33k": (3.7, 1.2),  # high voltage up to 33000 V
    "extra": (None, 15.0),  # >33000 V: 15 m horizontal corridor
}

def electric_clearance(query: str):
    q = query.lower()
    if "33000" in q or "extra" in q or "high voltage lines beyond" in q:
        return {"vertical": None, "horizontal": 15.0, "note": "15 m corridor (7.5 m each side of centre line)"}
    if "high" in q or "33000" in q or "33000 volts" in q:
        return {"vertical": 3.7, "horizontal": 1.2}
    return {"vertical": 2.5, "horizontal": 1.2}  # default low/medium

# --- Rule 21(3)(b): residential building permission fee slabs (Rs) ---
# (upto_sqm, fee). Commercial/shops = +50%.
RESI_FEE_SLABS = [
    (75, 750), (125, 1250), (200, 2000), (300, 3000), (400, 4000),
    (600, 6000), (750, 7500), (1000, 10000), (1250, 12500),
    (1500, 15000), (2000, 20000), (2500, 25000), (float("inf"), 50000),
]

def building_fee(builtup_sqm: float, commercial: bool = False) -> int:
    for upto, fee in RESI_FEE_SLABS:
        if builtup_sqm <= upto:
            return int(fee * 1.5) if commercial else fee
    return 50000

# --- number extraction helpers ---
NUM_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(m\b|meter|metre|sq\s?m|sqm|sq\.?\s?m|sqm\.|hectare|ha)?", re.I)

def extract_numbers(query: str):
    """Return dict with road_width_m, plot_area_sqm, height_m, builtup_sqm (best effort)."""
    # normalise Hindi units so regexes work
    q = query.replace("वर्ग मीटर", "sqm").replace("वर्गमीटर", "sqm").replace("मीटर", "m").replace("मी\udb40\udc00", "m")
    out = {}
    # explicit patterns first
    m = re.search(r"(\d+(?:\.\d+)?)\s*m\b.*(?:road|street|street|सड़क)", q, re.I) or \
        re.search(r"(?:road|street|सड़क)[^\d]{0,20}(\d+(?:\.\d+)?)\s*m", q, re.I)
    if m:
        out["road_width_m"] = float(m.group(1))
    if "road_width_m" not in out:
        # fallback: "<N> m ... (front|सामने|आगे|सड़क)" — covers Hindi "9 m चौड़ी सड़क"
        m2 = re.search(r"(\d+(?:\.\d+)?)\s*m\b[^\d]{0,25}(?:front|सामने|आगे|सड़क|चौड़ी)", q, re.I)
        if m2:
            out["road_width_m"] = float(m2.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:sq\s?m|sqm|वर्ग\s*मीटर)", q, re.I)
    if m:
        # disambiguate plot vs built-up by nearby words
        out["area_sqm"] = float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)\s*m\b.*(?:tall|height|high|ऊंच|ऊँच)", query, re.I) or \
        re.search(r"(?:tall|height|ऊंच)[^\d]{0,20}(\d+(?:\.\d+)?)", query, re.I)
    if m:
        try:
            out["height_m"] = float(m.group(1))
        except ValueError:
            pass
    return out

def detect_calculation(query: str):
    """If query maps to a deterministic table, return {kind, ...} else None."""
    q = query.lower()
    nums = extract_numbers(query)
    if any(k in q for k in ["front", "सामने", "आगे", "front open"]):
        if "area_sqm" in nums or "road_width_m" in nums:
            w = nums.get("road_width_m", nums.get("area_sqm"))
            # road width is the sensible one (usually <= 30m); plot areas are bigger
            if w is not None and w <= 30:
                return {"kind": "front_setback", "road_width_m": w,
                        "value_m": front_open_space(w), "rule": "56"}
    if any(k in q for k in ["rear", "पीछे", "rear open"]):
        if "area_sqm" in nums:
            a = nums["area_sqm"]
            return {"kind": "rear_setback", "plot_area_sqm": a,
                    "value_m": rear_open_space(a), "rule": "56"}
    if any(k in q for k in ["electric", "बिजली", "overhead", "volt", "वोल्टेज",
                             "power line", "power", "wire", "taar", "तार"]):
        return {"kind": "electric", "rule": "52", **electric_clearance(query)}
    if "farm" in q or "फार्म" in q:
        return {"kind": "farmhouse", "rule": "17",
                "min_plot": "0.40 hectare", "max_far": "0.10",
                "max_height": "7.5 m sloping roof", "mos": "7.5 m all sides"}
    if any(k in q for k in ["valid", "renew", "revalid", "अवधि", "नवीनीकरण", "how long"]):
        return {"kind": "validity", "rule": "23",
                "valid": "3 years", "renewal": "2 x 1 year, then fresh proposal (max 5 years)"}
    if "lift" in q or "लिफ्ट" in q or "escalator" in q:
        return {"kind": "lift", "rule": "83",
                "note": "Provision for lifts required above 12.5 m height (NBC Part-VIII Sec-5); details in Appendix A-2(A)"}
    if "convert" in q and ("hectare" in q or "sqm" in q or "sqft" in q or "acre" in q):
        return {"kind": "conversion", "rule": "21",
                "note": "1 hectare = 10,000 sqm = 2.471 acre; 1 sqm = 10.764 sqft (helper math; fee rate Rs 5000/ha in Rule 21(2))"}
    if any(k in q for k in ["document", "appendix", "accompanying", "दस्तावेज", "आवेदन"]) and "permission" in q:
        return {"kind": "documents", "rule": "14"}
    if any(k in q for k in ["who", "sign", "submit", "architect", "हस्ताक्षर"]) and any(k in q for k in ["plan", "sign", "submit", "architect", "योजना"]):
        # precise competence table only when the job size is given (numbers present)
        import re as _re2
        if re.search(r"\d", q) and any(k in q for k in ["sq", "storey", "floor", "height", "plot", "मंजिल"]):
            from competence import competent_who
            nums = extract_numbers(q)
            m = _re2.search(r"(\d+)\s*(?:storey|storeys|floor|floors|मंजिल)", q, _re2.I)
            who = competent_who(plot_sqm=nums.get("area_sqm"),
                                storeys=int(m.group(1)) if m else None,
                                height_m=nums.get("height_m"))
            return {"kind": "competence", "rule": "26", "who": who,
                    "plot": nums.get("area_sqm"), "storeys": int(m.group(1)) if m else None}
        return {"kind": "sign", "rule": "18"}
    # occupancy / inspection BEFORE generic plan_change/deemed (more specific wins)
    # deadline summary first of all: explicit timeline questions beat everything generic
    if any(k in q for k in ["timeline", "kitne din", "how many days", "kab tak", "कब तक", "time limit"]):
        return {"kind": "deadline", "rule": "23"}
    if any(k in q for k in ["occupancy", "completion certificate", "भोग", "अधिभोग"]):
        return {"kind": "occupancy", "rule": "31"}
    if any(k in q for k in ["inspect", "निरीक्षण"]) or ("plinth" in q and "certificate" in q):
        return {"kind": "inspection", "rule": "33"}
    if any(k in q for k in ["change", "alteration", "deviation", "modify", "sanctioned", "परिवर्तन"]):
        return {"kind": "plan_change", "rule": "24"}
    # word boundaries: "miss"/"fail" must not match inside "permission"
    if re.search(r"\bdeemed\b|\bdeadline\b|\bmiss\b|\bfail\b|not replied|no reply|\blimitation\b", q):
        return {"kind": "deemed", "rule": "28"}
    if "development plan" in q and any(k in q for k in ["disagree", "precedence", "contrary", "differ", "against"]):
        return {"kind": "precedence", "rule": "103"}
    # --- Q11-type: 300 sqm + development permission + plan match (Aug-2026 verdict) ---
    if "300" in q and "development permission" in q:
        return {"kind": "plot300", "rule": "12"}
    # --- Rule 12-A: instant/deemed approval (residential <=186 sqm, June 2024) ---
    if any(k in q for k in ["instant", "deemed approval", "deemed building", "186", "turant", "तुरंत"]):
        return {"kind": "instant", "rule": "12"}
    # --- Rule 21(4): standard plan permission (approved layout, <=300 sqm) ---
    if any(k in q for k in ["standard plan", "मानक योजना", "standard building plan"]):
        return {"kind": "standard_plan", "rule": "21"}
    # --- Rule 26(9): handled inside the sign block above (competence table) ---
    # --- FAR (Rule 61). NOTE: \bFAR\b is case-SENSITIVE ("far" is a common word) ---
    if re.search(r"\bFAR\b|F\.A\.R|एफएआर", query) or "floor area ratio" in q:
        return {"kind": "far", "rule": "61"}
    # --- side open space (Rule 56(3)) ---
    if "side" in q and any(k in q for k in ["open", "gap", "setback", "बगल"]):
        return {"kind": "side_setback", "rule": "56"}
    # --- room sizes (Rules 69-71); after electric so balcony-wire stays electric ---
    if any(k in q for k in ["kitchen", "bedroom", "bathroom", "रसोई", "कमरा"]) or \
            re.search(r"\broom\b|\bbath\b|\bwc\b|\btoilet\b", q):
        return {"kind": "room", "rule": "69"}
    # --- plantation & rainwater (Rules 67, 81); RWH split for exact citation ---
    if any(k in q for k in ["rwh", "rainwater", "rain water", "harvesting", "वर्षा"]):
        return {"kind": "rwh", "rule": "81"}
    if any(k in q for k in ["plantation", "पेड़", "पौध"]) or \
            re.search(r"\btree\b|\btrees\b|\bplant\b", q):
        return {"kind": "plantation", "rule": "67"}
    # --- projections & boundary walls (Rules 58, 78); electric handled earlier ---
    if any(k in q for k in ["projection", "cornice", "sunshade", "chhajja", "boundary wall",
                            "compound wall", "दीवार", "छज्जा", "बालकनी"]) or \
            (("balcony" in q) and ("electric" not in q and "बिजली" not in q and "volt" not in q)):
        return {"kind": "projection", "rule": "58"}
    # --- high-rise bands (Rule 42) ---
    if re.search(r"\bhigh[\s-]?rise\b|tall building|बहुमंजिल|ऊंची इमारत", q):
        return {"kind": "highrise_band", "rule": "42"}
    # --- route wizard ---
    if any(k in q for k in ["rasta", "kaunsa", "konsa", "which route", "best option", "fastest"]):
        return {"kind": "route", "rule": "12"}
    # --- layout access roads (Rule 38) ---
    if any(k in q for k in ["means of access", "access road", "approach road", "colony road",
                            "colony", "sub-division", "subdivision"]):
        return {"kind": "layout", "rule": "38"}
    # --- site near water (Rule 50) ---
    if any(k in q for k in ["water body", "talab", "river", "lake", "नदी", "तालाब", "flood"]) and \
            any(k in q for k in ["distance", "buffer", "site", "plot", "build", "construct",
                                 "दूर", "ban", "allowed"]):
        return {"kind": "site", "rule": "50"}
    # --- septic tank (Rule 79) ---
    if any(k in q for k in ["septic", "soak pit", "सेप्टिक"]):
        return {"kind": "septic", "rule": "79"}
    # --- staircase (Rule 80) ---
    if any(k in q for k in ["staircase", "stairs", "stair", "सीढ़ी"]):
        return {"kind": "stair", "rule": "80"}
    # --- marriage garden (Rule 53) ---
    if any(k in q for k in ["marriage garden", "marriage hall", "mangal karyalaya",
                            "मैरिज", "शादी", "विवाह"]):
        return {"kind": "marriage", "rule": "53"}
    # --- multiplex / cinema (Rules 95, 21); fee questions stay with Rule 21 ---
    if any(k in q for k in ["multiplex", "cinema", "theatre", "theater", "सिनेमा", "मल्टीप्लेक्स"]) and \
            not any(k in q for k in ["fee", "fees", "फीस", "शुल्क", "charges"]):
        return {"kind": "multiplex", "rule": "95"}
    return None


# --- v2 additions (kept) ---
def application_fee(kind: str = "building", builtup_sqm: float = 0, hectares: float = 0) -> str:
    """Rule 21(2): Dev Rs 5000/ha; Building Rs 1/sqm of proposed built-up. Non-refundable."""
    if kind == "development":
        import math
        return f"Rs {int(math.ceil(hectares or 0.0001) * 5000)} (Rs 5000/ha or part thereof)"
    return f"Rs {builtup_sqm:.0f} (Rs 1 per sqm of proposed built-up area)"


def revalidation_fee(original_permission_fee: float) -> float:
    """Rule 21(3)(b)(9): 10% of original building permission fee."""
    return round(original_permission_fee * 0.10, 2)


def convert_area(value: float, frm: str, to: str) -> float:
    factors = {"sqm": 1.0, "sqft": 10.7639, "hectare": 10000.0, "acre": 4046.86}
    return value * factors[frm] / factors[to]


# --- Rule 12-A: instant/deemed approval eligibility (residential, June 2024) ---
def instant_approval_eligible(plot_sqm: float | None, approved_layout: bool = True,
                             individual_holder: bool = True):
    """12-A: residential plots up to 186 sqm in approved layout, individual holder only."""
    if plot_sqm is not None and plot_sqm > 186:
        return False, "Plot exceeds 186 sq m — instant approval not available."
    if not approved_layout:
        return False, "Layout must be approved by Town & Country Planning."
    if not individual_holder:
        return False, "Only individual plot holders (not colonisers selling plots/flats)."
    return True, "Eligible: Appendix A-2(2) + affidavit A-2(3) + Rule 21 fee = deemed sanction."


# --- Rule 21(4): standard plan permission (approved layout, <=300 sqm) ---
def standard_plan_eligible(plot_sqm: float | None, approved_layout: bool = True):
    if plot_sqm is not None and plot_sqm > 300:
        return False, "Plot exceeds 300 sq m — standard plan route not available."
    if not approved_layout:
        return False, "Plot must be in an approved layout."
    return True, "Eligible: choose an approved standard plan; fee receipt = permission."


# --- Rule 61 Table 8: FAR by use group ---
FAR_TABLE = {
    "residential": 1.25,
    "commercial-city-centre": 2.50, "commercial-sub-city": 2.00,
    "commercial-community": 1.75, "commercial-local": 1.50,
    "commercial-convenience": 1.25,
    "public": 1.00,
}

def far_limit(use: str = "residential") -> float | None:
    return FAR_TABLE.get(use.lower().replace(" ", "-"), FAR_TABLE.get("residential") if use == "residential" else None)


# --- Rule 56(3): side open space ---
def side_setback(building: str = "detached", frontage_m: float | None = None,
                 height_m: float | None = None):
    b = building.lower()
    if "row" in b:
        return "Nil (row-type needs no side open space)"
    if "semi" in b:
        if frontage_m is not None and frontage_m <= 10 and (height_m or 0) <= 10:
            return "2.5 m on one side"
        return "3.0 m on one side"
    # detached
    if frontage_m is not None and frontage_m < 12 and (height_m or 0) <= 7:
        return "3.0 m one side + 1.5 m other side"
    return "3.0 m both sides"


# --- Rule 21(3)(c): high-rise building fees (per sqm of built-up) ---
def highrise_fee(builtup_sqm: float, use: str = "residential") -> float:
    base = builtup_sqm * 10.0
    u = use.lower()
    if any(k in u for k in ("shop", "commercial", "industrial", "factory")):
        return base * 2.0
    if "cum" in u or "shop-cum" in u or "residence" in u and "shop" in u:
        return base * 1.5
    return base


def fee_breakdown(builtup_sqm: float, use: str = "residential", highrise: bool = False,
                  revalidation_of: float | None = None):
    """Full Rule-21 math. Returns (rows[(label, Rs)], total). All deterministic."""
    rows = [("Application fee (Rs 1/sqm built-up)", round(builtup_sqm * 1.0))]
    u = use.lower()
    if highrise:
        base = builtup_sqm * 10.0
        rows.append(("High-rise permission (Rs 10/sqm)", round(base)))
        if any(k in u for k in ("shop", "commercial", "industrial")):
            rows.append(("+100% commercial", round(base)))
            total = round(base * 2)
        elif "cum" in u:
            rows.append(("+50% shop-cum-residence", round(base * 0.5)))
            total = round(base * 1.5)
        else:
            total = round(base)
    else:
        fee = building_fee(builtup_sqm, commercial=("commercial" in u or "shop" in u or "industrial" in u))
        rows.append(("Permission fee (slab, Rule 21(3)(b))", fee))
        total = fee
    total += round(builtup_sqm)
    if revalidation_of:
        rows.append(("Revalidation 10% (if expired)", round(revalidation_of * 0.10)))
    return rows, total


# --- Rules 69-71: room sizes (PDF p.87-89). Returns (ok, required_str, problems). ---
def check_room(kind="habitable1", area=None, width=None, height=None):
    """kind: habitable1 (only room), habitable2a/b, kitchen, kitchen_store,
    kitchen_dining, bath, wc, bath_wc, wc_basin."""
    R = {
        "habitable1": (9.5, 2.4, 2.6), "habitable2a": (9.5, 2.4, 2.6),
        "habitable2b": (7.5, 2.1, 2.6), "kitchen": (5.0, 1.8, 2.6),
        "kitchen_store": (4.5, 1.8, 2.6), "kitchen_dining": (7.5, 2.1, 2.6),
        "bath": (1.5, 1.1, 2.2), "wc": (1.1, 0.9, 2.2),
        "bath_wc": (2.4, 1.2, 2.2), "wc_basin": (1.3, None, 2.2),
    }
    req_area, req_w, req_h = R[kind]
    probs = []
    if area is not None and area < req_area - 1e-9:
        probs.append(f"area {area} < {req_area} sqm")
    if width is not None and req_w and width < req_w - 1e-9:
        probs.append(f"width {width} < {req_w} m")
    if height is not None and height < req_h - 1e-9:
        probs.append(f"height {height} < {req_h} m")
    need = f"area >= {req_area} sqm" + (f", width >= {req_w} m" if req_w else "") + f", height >= {req_h} m"
    return (not probs, need, "; ".join(probs))


# --- Rules 67 + 81(4): plantation & rainwater harvesting ---
def plantation_needed(plot_sqm: float) -> int:
    """Rule 67: 1 tree per 100 sqm (plots >=100 sqm); occupancy only after compliance."""
    if plot_sqm < 100:
        return 0
    import math
    return math.ceil(plot_sqm / 100)


def rwh_needed(plot_sqm: float) -> bool:
    """Rule 81(4): rain/roof-water harvesting required on plots >140 sqm."""
    return plot_sqm > 140


# --- Rules 58 + 78: projections & boundary walls ---
PROJECTION_LIMITS = {
    "balcony": (1.20, "Rule 58(1)(c): projected balcony up to 1.20 m, 1.5 m clear of plot boundary"),
    "cornice": (0.75, "Rule 58(1)(a): cornice/roof/weather shade up to 0.75 m"),
    "sunshade": (0.75, "Rule 58(1)(b): sunshade over window up to 0.75 m"),
    "garage_area": (25.0, "Rule 58(4)(b): private garage up to 25 sqm in rear side space"),
    "wall_front": (1.5, "Rule 78(a): front compound wall up to 1.5 m"),
    "wall_side": (2.0, "Rule 78(b): side/rear wall up to 2 m (3 m on service road)"),
}


def check_projection(kind: str, value: float):
    lim, note = PROJECTION_LIMITS[kind]
    return (value <= lim + 1e-9, lim, note)


# --- Rule 42 Tables 4-5: height bands (PDF p.58-60) ---
MID_BANDS = [  # (max_height, road, plot, frontage, far, front_mos, side_mos)
    (18, 12.0, 1000, 18, 1.50, 7.5, 6.0),
    (24, 18.0, 1500, 21, 1.75, 9.0, 6.0),
    (30, 24.0, 2000, 30, 2.00, 12.0, 7.5),
]
HIGH_BANDS = [  # (max_height, road, plot, frontage, far, front_mos, side_mos)
    (45, 30.0, 2500, 30, 2.25, 15.0, 7.5),
    (60, 36.0, 3000, 40, 2.50, 18.0, 9.0),
    (75, 45.0, 3500, 45, 2.75, 21.0, 9.0),
    (90, 60.0, 4000, 50, 3.00, 24.0, 10.0),
    (float("inf"), 75.0, 4500, 60, 3.00, 30.0, 12.0),
]


def height_band(height_m: float):
    """Return dict with band norms for a proposed height, or None if <=12.5 m."""
    if height_m <= 12.5:
        return None
    for mx, road, plot, frontage, far, fmos, smos in MID_BANDS + HIGH_BANDS:
        if height_m <= mx:
            return {"max": mx if mx != float("inf") else "90+",
                    "highrise": height_m > 30 or False, "road": road, "plot": plot,
                    "frontage": frontage, "far": far, "front_mos": fmos, "side_mos": smos}
    return None


# --- Rule 38(4): means-of-access width by length (residential, PDF p.56) ---
ACCESS_TABLE = [(150, 7.5), (250, 9.0), (400, 12.0), (1000, 18.0), (float("inf"), 24.0)]

def access_width(length_m: float) -> float:
    for mx, w in ACCESS_TABLE:
        if length_m <= mx:
            return w
    return 24.0


# --- Rule 50(b): water-body buffers (PDF p.68) ---
def water_buffer_ok(kind: str, distance_m: float):
    """kind: waterbody (9 m) | river (15 m). Returns (ok, required)."""
    req = 15.0 if "river" in kind.lower() else 9.0
    return (distance_m >= req - 1e-9, req)


# --- Rule 79: septic tank siting (PDF p.92) ---
def septic_ok(dist_water_m=None, dist_building_m=None):
    probs = []
    if dist_water_m is not None and dist_water_m < 18 - 1e-9:
        probs.append(f"drinking-water source {dist_water_m}m < 18 m")
    if dist_building_m is not None and dist_building_m < 2 - 1e-9:
        probs.append(f"building {dist_building_m}m < 2 m")
    return (not probs, "water source >=18 m; building >=2 m; min 75cm wide, 1m deep, 1 cum",
            "; ".join(probs))


# --- Rule 80: staircase widths (PDF p.93) ---
STAIR_TABLE = {
    "residential": 0.85, "hotel": 1.5, "assembly": 1.5,
    "educational_low": 1.5, "educational_high": 2.0,
    "institutional_low": 1.5, "institutional_high": 2.0, "other": 1.5,
}

def stair_width(building: str = "residential", tall: bool = False) -> float:
    b = building.lower()
    if "education" in b or "school" in b or "college" in b:
        return 2.0 if tall else 1.5
    if "hospital" in b or "institution" in b:
        return 2.0 if tall else 1.5
    return STAIR_TABLE.get("residential" if "resi" in b or "house" in b or "home" in b else
                           "hotel" if "hotel" in b else
                           "assembly" if any(k in b for k in ("cinema", "theatre", "assembly", "mall")) else "other",
                           1.5)


# --- Rule 53(iii): marriage garden norms by town population (PDF p.70-71) ---
def marriage_garden_norms(population_lakh: float | None = None):
    """Return norms dict. >5 lakh: 10000 sqm/18m road/40m frontage; else 4000/12m/25m."""
    big = population_lakh is not None and population_lakh > 5
    return {"plot": 10000 if big else 4000, "road": 18 if big else 12,
            "frontage": 40 if big else 25, "far": 0.10, "coverage": "10%",
            "parking": "40% of plot" if big else "30% of plot",
            "mos_front": "6.0 m after parking"}


# --- Rule 95: multiplex plot area by seats (PDF p.102-103) ---
def multiplex_plot(seats: int, shopping: bool = False):
    """Min plot: <=300 seats 1200 (1500 w/ shopping); <=500 seats 2000 (2500); above @4-5 sqm/seat."""
    if seats <= 300:
        return 1500 if shopping else 1200
    if seats <= 500:
        return 2500 if shopping else 2000
    return seats * (5 if shopping else 4)
