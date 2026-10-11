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
    if "electric" in q or "बिजली" in q or "overhead" in q or "volt" in q:
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
    # --- Rule 12-A: instant/deemed approval (residential <=186 sqm, June 2024) ---
    if any(k in q for k in ["instant", "deemed approval", "deemed building", "186", "turant", "तुरंत"]):
        return {"kind": "instant", "rule": "12"}
    # --- Rule 21(4): standard plan permission (approved layout, <=300 sqm) ---
    if any(k in q for k in ["standard plan", "मानक योजना", "standard building plan"]):
        return {"kind": "standard_plan", "rule": "21"}
    # --- Rule 26(9): handled inside the sign block above (competence table) ---
    # --- FAR (Rule 61) ---
    if re.search(r"\bFAR\b|floor area ratio|एफएआर|F\.A\.R", query, re.I):
        return {"kind": "far", "rule": "61"}
    # --- side open space (Rule 56(3)) ---
    if "side" in q and any(k in q for k in ["open", "gap", "setback", "बगल"]):
        return {"kind": "side_setback", "rule": "56"}
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
