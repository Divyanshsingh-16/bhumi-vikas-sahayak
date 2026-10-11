"""Split rules into sub-rule clause chunks for precise citations.
Chunk = Rule + subref (e.g. 56(1)(a)) with page span. Cached to data/chunks.jsonl."""
import json
import re
from pathlib import Path

SRC = Path(__file__).parent / "data" / "bhumi_vikas_rules.jsonl"
OUT = Path(__file__).parent / "data" / "chunks.jsonl"

SUB_RE = re.compile(r"(?m)^\s*(\(\d+\)|\(?[a-z]\)|\[?[0-9]+[a-z]?[\.\)\]]|S\.No\.|\(i+\)|\(ii+\)|Note\s*:)")
HEADER_RE = re.compile(r"Rule\s+\d+[A-Z\-]*\s+M\.P\. Bhumi Vikas Rules,?\s*2012\s+\d+", re.I)
WS_RE = re.compile(r"\s+")


def split_rule(rule: dict):
    text = HEADER_RE.sub(" ", rule["text"])
    parts = SUB_RE.split(text)
    chunks = []
    if len(parts) <= 1:
        t = WS_RE.sub(" ", text).strip()
        return [{"subref": "", "text": t[:2000]}]
    pre = WS_RE.sub(" ", parts[0]).strip()
    if pre:
        chunks.append({"subref": "(head)", "text": pre[:2000]})
    for i in range(1, len(parts), 2):
        marker = parts[i].strip()
        body = WS_RE.sub(" ", parts[i + 1]).strip() if i + 1 < len(parts) else ""
        t = f"{marker} {body}".strip()
        if len(t) < 60 and chunks:
            chunks[-1]["text"] = (chunks[-1]["text"] + " " + t)[:2000]
        else:
            chunks.append({"subref": marker[:24], "text": t[:2000]})
    return [c for c in chunks if c["text"].strip()]


def main():
    rules = [json.loads(l) for l in open(SRC, encoding="utf-8")]
    out = []
    for r in rules:
        for c in split_rule(r):
            out.append({
                "rule": r["rule"], "title": r["title"],
                "page_start": r["page_start"], "page_end": r["page_end"],
                "subref": c["subref"], "text": c["text"],
            })
    with open(OUT, "w", encoding="utf-8") as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"rules={len(rules)} chunks={len(out)} -> {OUT}")


if __name__ == "__main__":
    main()
