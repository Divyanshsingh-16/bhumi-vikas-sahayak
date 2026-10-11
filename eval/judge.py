"""Offline answer judge: grades the FINAL answer text (beyond retrieval).
Checks per question: expected rule cited? key number present? quote verbatim
from the cited rule? not-found correct? Writes eval/grade.csv"""
import csv
import json
import os
import re
import sys
from pathlib import Path

os.environ["BHUMI_EVAL"] = "1"
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline import pipeline
from rag import clean_for_search

NUM_RE = re.compile(r"\d+(?:\.\d+)?")

# expected key numbers per question id (from the rule tables)
NUMBERS = {
    1: ["3.6"], 5: ["2.5", "1.2"], 8: ["2000"], 10: ["1.5"], 14: ["3.0"],
    46: ["186"], 48: ["1.25"], 50: ["300"], 66: ["5.0"], 67: ["5"],    76: ["12"], 77: ["9"], 78: ["18", "2"], 79: ["0.85"], 81: ["4000", "10000"],
    82: ["2000", "1200"], "H85": ["3.6"], "H86": ["2.5"], "H88": ["2.5", "1.2"],
}


def grade(qid, question, expected, res):
    notes = []
    score = 0
    got = res.get("rule")
    if expected == "NOT-FOUND" or expected is None:
        ok = got is None
        return ok, 1.0 if ok else 0.0, "not-found ok" if ok else f"guessed Rule {got}"
    if got == expected:
        score += 0.5
        notes.append("rule ok")
    else:
        # half credit if expected rule cited anywhere in answer text
        if re.search(rf"\b{re.escape(str(expected))}\b", res.get("answer", "")):
            score += 0.25
            notes.append("rule mentioned")
        else:
            notes.append(f"rule {got} != {expected}")
    key = NUMBERS.get(qid)
    ans_flat = res.get("answer", "").replace(",", "")
    if key:
        if all(n in ans_flat for n in key):
            score += 0.3
            notes.append("numbers ok")
        else:
            notes.append(f"numbers missing {key}")
    else:
        score += 0.3
        notes.append("no numbers needed")
    quote = (res.get("quote") or "")[:60].lower()
    if quote and quote[:40] in clean_for_search(res.get("answer", "").lower() + " "):
        pass
    # quote verbatim from cited rule text: check first 8 words appear in rule
    if res.get("retrieved"):
        full = " ".join(r["text"] for r, _ in res["retrieved"]).lower()
        if quote[:40] and quote[:40] in full:
            score += 0.2
            notes.append("quote grounded")
        else:
            notes.append("quote ungrounded")
    else:
        notes.append("no retrieval")
    return score >= 0.75, round(min(score, 1.0), 2), "; ".join(notes)


def main():
    from run_17 import QUESTIONS as Q17
    from run_v2 import EXTRA
    allq = [(i, q, e) for i, q, e in Q17] + [(n, q, e) for n, q, e in EXTRA]
    rows, passed = [], 0
    for qid, q, exp in allq:
        res = pipeline(q)
        ok, sc, note = grade(qid, q, exp, res)
        passed += ok
        rows.append({"id": qid, "expected": exp or "NOT-FOUND", "got": res.get("rule") or "NOT-FOUND",
                     "score": sc, "pass": ok, "note": note})
        if not ok:
            print(f"FAIL {qid} exp={exp} got={res.get('rule')} [{note}] :: {q[:60]}")
    print(f"\nAnswer-grade pass: {passed}/{len(rows)}")
    out = Path(__file__).parent / "grade.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
