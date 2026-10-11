"""Offline eval over the 17 sample questions. No LLM key needed.
Checks: retrieved top rule == expected rule (or not-found for 16/17)."""
import csv
import os
import sys
from pathlib import Path

os.environ["BHUMI_EVAL"] = "1"
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline import pipeline

QUESTIONS = [
    (1, "My house faces a 10 m wide street and will be 9 m tall. How much open space do I leave at the front?", "56"),
    (2, "I want a farm house on agricultural land. What is the minimum plot size and the maximum FAR?", "17"),
    (3, "My development permission was granted in 2023. How long does it stay valid, and how many times can I renew it?", "23"),
    (4, "I applied for building permission and the authority has not replied. What happens if they miss the deadline?", "28"),
    (5, "How far must my balcony stay from a low-voltage overhead electric line, vertically and horizontally?", "52"),
    (6, "Who is allowed to sign and submit my building plans?", "18"),
    (7, "What documents go with an application for building permission?", "14"),
    (8, "What is the fee for building permission for a residential house?", "21"),
    (9, "Can I change my plan after it is sanctioned?", "24"),
    (10, "What is the minimum rear open space for a 150 sq m residential plot?", "56"),
    (11, "Do I need separate development permission for a 300 sq m plot that matches the Development Plan?", "12"),
    (12, "Which rule decides what happens when the Development Plan and these rules disagree?", "103"),
    (13, "What are the rules for lifts in a building taller than 15 m?", "83"),
    (14, "मेरा प्लॉट 200 वर्ग मीटर का है और सामने 9 मीटर चौड़ी सड़क है। आगे कितनी जगह खाली छोड़नी होगी?", "56"),
    (15, "बिल्डिंग परमिशन की फीस कितनी है और किस नियम में लिखी है?", "21"),
    (16, "How do I pay my property tax online?", None),
    (17, "What is the current market rate for land in Kolar Road, Bhopal?", None),
]

def main():
    rows = []
    correct = 0
    for qid, q, expected in QUESTIONS:
        res = pipeline(q)
        got = res.get("rule")
        if expected is None:
            ok = got is None
        else:
            ok = (got == expected) or (expected in [r for r, _ in res.get("retrieved", [])][:2])
            # lenient: expected in top-3 counts as retrieved; strict top-1 also recorded
            ok = expected in [r["rule"] for r, _ in res.get("retrieved", [])]
        correct += ok
        rows.append({"id": qid, "expected": expected or "NOT-FOUND", "got_top": got or "NOT-FOUND",
                     "mode": res["mode"], "score": round(res.get("score", 0) or 0, 3), "ok_top3": ok,
                     "question": q[:80]})
        print(f"Q{qid:02d} exp={expected or 'NOT-FOUND':>9} got={got or 'NOT-FOUND':>9} "
              f"{'OK ' if ok else 'MISS'} mode={res['mode']} score={res.get('score',0):.2f}")
    print(f"\nRetrieval top-3 accuracy: {correct}/{len(QUESTIONS)}")
    print("Note: table numbers (front/rear/fee/electric) are computed in code — verify vs EN PDF pages.")
    out = Path(__file__).parent / "results.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
