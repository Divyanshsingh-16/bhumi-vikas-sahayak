"""Shared pipeline: retrieval -> calc -> not-found gate -> LLM/offline answer."""
from calculators import detect_calculation
from parse_query import parse_hint
from patch_2026 import NOT_FOUND_EN, NOT_FOUND_HI, PATCH_NOTE_EN, PATCH_NOTE_HI
from rag import RuleRetriever, short_quote
from llm import answer_query, is_hindi
from templates import template_answer, SECONDARY, CITIZEN, FOLLOWUPS

NOT_FOUND_THRESHOLD = 0.08
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = RuleRetriever()
    return _retriever

def pipeline(query: str, top_k: int = 3):
    retr = get_retriever()
    hi = is_hindi(query)
    # 1. out-of-scope shortcut (property tax, land rates...)
    if retr.is_out_of_scope(query):
        nf = NOT_FOUND_HI if hi else NOT_FOUND_EN
        return {"answer": nf, "rule": None, "pages": None, "quote": None,
                "mode": "not-found-oos", "calc": None, "retrieved": []}
    retrieved = retr.search(query, top_k=top_k)
    calc = detect_calculation(query)
    # promote the calc's rule to top when retrieval already found it in top-k
    # (headline <-> citation stay consistent without overriding retrieval)
    if calc and calc.get("rule"):
        for i, (r, s) in enumerate(retrieved):
            if r["rule"] == calc["rule"] and i > 0:
                retrieved = [retrieved[i]] + retrieved[:i] + retrieved[i+1:]
                break
    top_rule, top_score = retrieved[0]
    # 2. low-similarity + no calculator -> not found (don't guess)
    if top_score < NOT_FOUND_THRESHOLD and calc is None:
        nf = NOT_FOUND_HI if hi else NOT_FOUND_EN
        return {"answer": nf, "rule": None, "pages": None, "quote": None,
                "mode": "not-found-low-score", "calc": None, "retrieved": retrieved,
                "score": top_score}
    # pick best chunk FIRST so LLM + offline paths cite the same right paragraph
    best = retr.best_chunk(top_rule["rule"], query) or top_rule.get("_chunk")
    top_rule = dict(top_rule)
    top_rule["_chunk"] = best
    retrieved = [(top_rule, top_score)] + list(retrieved[1:])
    # 3. grounded answer (quote = most query-relevant chunk *within* top rule)
    text, mode = answer_query(query, retrieved, calc)
    # deterministic bilingual headline guarantees numbers + Hindi even offline
    lang = "hi" if hi else "en"
    head = template_answer(calc, lang)
    parts = []
    if head:
        parts.append(head)
    if calc and calc.get("kind") in SECONDARY:
        parts.append("➕ " + SECONDARY[calc["kind"]][lang])
    if calc and calc.get("kind") in CITIZEN:
        parts.append("🗣️ " + CITIZEN[calc["kind"]][lang])
    if not parts:
        parts.append("नियम में लिखा है:" if hi else "The rules say:")
    extra = "\n".join(parts)
    if extra and extra not in text:
        text = extra + "\n" + text
    followups = FOLLOWUPS.get((calc or {}).get("kind", ""), []) if calc else []
    chunk = best
    quote_src = chunk["text"] if isinstance(chunk, dict) and chunk.get("text") else top_rule["text"]
    quote = short_quote(quote_src)
    subref = (chunk or {}).get("subref", "") if isinstance(chunk, dict) else ""
    # confidence: calc-backed or high-score = high; mid = medium; else low
    if calc is not None or top_score >= 0.30:
        conf = "high"
    elif top_score >= 0.12:
        conf = "medium"
    else:
        conf = "low"
    return {"answer": text, "rule": top_rule["rule"], "pages": (top_rule["page_start"], top_rule["page_end"]),
            "quote": quote, "title": top_rule["title"], "mode": mode, "calc": calc,
            "retrieved": retrieved, "score": top_score, "subref": subref,
            "entities": parse_hint(query), "confidence": conf, "followups": followups}
