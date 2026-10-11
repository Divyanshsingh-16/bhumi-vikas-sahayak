"""Grounding tests: every hardcoded number must occur in the rule text.
Fails loudly listing misses (like facts.rs tests). Run: python3 eval/grounding.py"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

DATA = Path(__file__).parent.parent / "data" / "bhumi_vikas_rules.jsonl"

# (rule, regex that must match the rule's text, what it grounds)
CHECKS = [
    ("56", r"3\.0 meters", "front setback 3.0"),
    ("56", r"3\.6 meters", "front 3.6"), ("56", r"4\.5 meters", "front 4.5"),
    ("56", r"6\.0 meters", "front 6.0"), ("56", r"1\.50", "rear 1.5"),
    ("56", r"2\.50", "rear 2.5"), ("56", r"3\.00", "rear 3.0"),
    ("56", r"3\s*meters?\s*on both", "detached sides"),
    ("52", r"2\.5", "LV vertical"), ("52", r"3\.7", "HV vertical"),
    ("52", r"15 meters", "EHV corridor"),
    ("17", r"0\.40 hectare", "farm plot"), ("17", r"0\.10", "farm FAR"),
    ("17", r"7\.5 meters", "farm height/MOS"),
    ("21", r"5000 per hectare", "dev application fee"), ("21", r"Rs 1\.00 per Square meter", "building app fee"),
    ("21", r"1,250", "fee slab"), ("21", r"50,000", "fee top slab"),
    ("21", r"10%", "revalidation 10%"), ("21", r"Rs\. 10\.00 per square meter", "high-rise fee"),
    ("23", r"three years", "validity"), ("23", r"one year each", "renewal"),
    ("28", r"deemed to have been", "deemed sanction"),
    ("58", r"1\.20 meters", "balcony"), ("58", r"0\.75", "cornice/sunshade"),
    ("58", r"25 square meters", "garage"), ("77", r"1\.05 meters", "parapet"),
    ("78", r"1\.5 meters", "front wall"), ("80", r"0\.85 meters", "res stair"),
    ("80", r"2\.2 meters", "headroom"), ("83", r"12\.5 meters", "lift height"),
    ("61", r"1\.25", "res FAR"), ("61", r"25 sq\. m", "servant quarter"),
    ("67", r"100 square meters", "trees"), ("79", r"18 meters", "septic water gap"),
    ("79", r"2 meters thereof", "septic building gap"), ("81", r"140 Square meter", "RWH"),
    ("50", r"9 meters", "water buffer"), ("50", r"15 mtrs", "river buffer"),
    ("26", r"500.*[Ss]q", "SE competence"), ("26", r"300 sq", "engineer competence"),
    ("26", r"200 sq", "supervisor competence"),
    ("12", r"186 sqm", "instant approval"), ("21", r"300\s+square meters", "standard plans"),
    ("42", r"1000 sq", "Table 4 band"), ("42", r"1:1\.50", "Table 4 FAR"),
    ("33", r"7 days", "inspection"), ("33", r"21 days", "final inspection"),
    ("31", r"30 days", "occupancy deemed"),
    ("2A", r"500 sq\. m", "amendment area (gazette)"),
]


_RULES = {}


def _text_of(rule):
    if rule == "2A":
        try:
            a = json.load(open(Path(__file__).parent.parent / "data" / "amendment_2026.json"))
            return a.get("quote_en", "")
        except (OSError, ValueError):
            return ""
    return _RULES.get(rule, "")


def main():
    global _RULES
    _RULES = {}
    for line in open(DATA, encoding="utf-8"):
        r = json.loads(line)
        _RULES[r["rule"]] = r["text"]
    fails = []
    for rule, pat, what in CHECKS:
        txt = _text_of(rule)
        if not re.search(pat, txt):
            fails.append((rule, what, pat))
    print(f"grounded {len(CHECKS) - len(fails)}/{len(CHECKS)}")
    for rule, what, pat in fails:
        print(f"MISS Rule {rule}: {what} [{pat}]")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
