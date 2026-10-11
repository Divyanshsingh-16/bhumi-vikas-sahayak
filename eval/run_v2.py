"""Eval v2: 17 original + 28 edge/Hindi/adversarial. Offline, no LLM key needed."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline import pipeline
from run_17 import QUESTIONS as Q17

EXTRA = [
    ("E18", "Front open space for a 9.0 m wide street?", "56"),
    ("E19", "Front open space for a 9.1 m wide street?", "56"),
    ("E20", "Front open space for a 20 m wide street?", "56"),
    ("E21", "Rear open space for a 40 sq m plot?", "56"),
    ("E22", "Rear open space for a 100 sq m plot?", "56"),
    ("E23", "Rear open space for a 225 sq m plot?", "56"),
    ("E24", "Rear open space for a 300 sq m plot?", "56"),
    ("E25", "Clearance for high voltage lines up to 33000 volts?", "52"),
    ("E26", "Corridor for extra high voltage lines beyond 33000 volts?", "52"),
    ("E27", "Is a lift needed for a 13 m tall building?", "83"),
    ("E28", "Max height of a farm house?", "17"),
    ("E29", "What is the application fee for development permission for 2 hectares?", "21"),
    ("E30", "Revalidation fee for building permission?", "21"),
    ("E31", "Which plans must an architect sign with licence number?", "18"),
    ("E32", "What plans accompany an alteration application?", "19"),
    ("E33", "Is deviation affecting front open space allowed?", "24"),
    ("E34", "Development next to government land — share plans?", "20"),
    ("E35", "Must the authority give reasons when refusing permission?", "29"),
    ("E36", "12 मीटर चौड़ी सड़क पर सामने कितनी जगह?", "56"),
    ("E37", "100 वर्ग मीटर प्लॉट में पीछे कितनी जगह?", "56"),
    ("E38", "परमिशन कितने साल वैध रहती है?", "23"),
    ("E39", "हाई वोल्टेज लाइन से कितनी दूरी?", "52"),
    ("E40", "फार्म हाउस की अधिकतम ऊंचाई?", "17"),
    ("E41", "What is stamp duty for my sale deed?", None),
    ("E42", "My water bill is wrong, how to fix?", None),
    ("E43", "Convert 1 hectare to sqm for my application?", "21"),  # helper math + Rule 21 fee/ha context
    ("E44", "What is the building line?", "2"),
    ("E45", "Lift engineer licence qualification?", "26"),
    # source-grounded round 3 (Rules 12-A, 21(4), 26(9), 31, 33, 56(3), 61)
    ("E46", "My plot is 150 sq m in an approved layout. Can I get instant approval?", "12"),
    ("E47", "Who can sign plans for a 250 sq m 2-storey house?", "26"),
    ("E48", "What is the FAR for residential buildings?", "61"),
    ("E49", "Side open space for a detached house?", "56"),
    ("E50", "My 250 sq m plot is in an approved layout. Can I use a standard plan?", "21"),
    ("E51", "How soon must the building be inspected after plinth notice?", "33"),
    ("E52", "When is occupancy permission deemed to be issued?", "31"),
    ("E53", "150 वर्ग मीटर प्लॉट, तुरंत स्वीकृति मिलेगी?", "12"),
    # paraphrase robustness round (reworded citizen phrasing)
    ("P54", "Front gap for 10m road?", "56"),
    ("P55", "Rear gap for 200 sqm plot?", "56"),
    ("P56", "Permission validity period?", "23"),
    ("P57", "Deemed approval if no response?", "28"),
    ("P58", "Balcony distance from power line?", "52"),
    ("P59", "Farmhouse plot minimum?", "17"),
    ("P60", "Plans signed by whom?", "18"),
    ("P61", "Permission papers needed?", "14"),
    ("P62", "House construction charges?", "21"),
    ("P63", "Modify sanctioned design allowed?", "24"),
    ("P64", "Plan vs rules conflict which wins?", "103"),
    ("P65", "Lift mandatory above what height?", "83"),
]

def main():
    allq = [(q, e) for _, q, e in Q17] + [(q, e) for _, q, e in EXTRA]
    rows, correct, top1 = [], 0, 0
    for i, (q, exp) in enumerate(allq, 1):
        res = pipeline(q)
        got = res.get("rule")
        retr_rules = [r["rule"] for r, _ in res.get("retrieved", [])]
        if exp is None:
            ok = got is None
        else:
            ok = exp in retr_rules
        if got == exp or (exp is None and got is None):
            top1 += 1
        correct += ok
        rows.append({"n": i, "expected": exp or "NOT-FOUND", "got": got or "NOT-FOUND",
                     "ok_top3": ok, "mode": res["mode"], "q": q[:70]})
        print(f"{i:02d} exp={exp or 'NOT-FOUND':>9} got={got or 'NOT-FOUND':>9} {'OK ' if ok else 'MISS'} {q[:60]}")
    print(f"\nTop-3: {correct}/{len(allq)} | Top-1: {top1}/{len(allq)}")
    out = Path(__file__).parent / "results_v2.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
