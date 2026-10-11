"""Answer cache: repeat questions answered instantly + popularity counts.
CSV-backed, offline. Keyed by normalised query."""
import csv
import re
from pathlib import Path

CACHE_PATH = Path(__file__).parent / "eval" / "answer_cache.csv"
WS = re.compile(r"\s+")


def norm(q: str) -> str:
    return WS.sub(" ", q.strip().lower())


def lookup(query: str):
    try:
        for row in csv.DictReader(open(CACHE_PATH, encoding="utf-8")):
            if row["nquery"] == norm(query):
                return row
    except FileNotFoundError:
        pass
    return None


def store(query: str, rule: str, mode: str):
    try:
        new = not CACHE_PATH.exists()
        with open(CACHE_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["nquery", "query", "rule", "mode", "count"])
                w.writerow([norm(query), query[:200], rule or "", mode, 1])
                return 1
        rows = list(csv.DictReader(open(CACHE_PATH, encoding="utf-8")))
        hit = False
        for r in rows:
            if r["nquery"] == norm(query):
                r["count"] = str(int(r.get("count", 1)) + 1)
                hit = True
        if not hit:
            rows.append({"nquery": norm(query), "query": query[:200], "rule": rule or "",
                         "mode": mode, "count": "1"})
        with open(CACHE_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["nquery", "query", "rule", "mode", "count"])
            w.writeheader()
            w.writerows(rows)
        return int([r["count"] for r in rows if r["nquery"] == norm(query)][0])
    except OSError:
        return 1


def popular(limit: int = 5):
    try:
        rows = list(csv.DictReader(open(CACHE_PATH, encoding="utf-8")))
        rows.sort(key=lambda r: -int(r.get("count", 0)))
        return [(r["query"], r["rule"], int(r["count"])) for r in rows[:limit]]
    except (FileNotFoundError, ValueError):
        return []
