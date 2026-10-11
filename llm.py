"""Claude/Cerebras wiring with strict grounding + offline fallback."""
import os
import re

from patch_2026 import NOT_FOUND_EN, NOT_FOUND_HI

DEVA_RE = re.compile(r"[\u0900-\u097F]")

SYSTEM_PROMPT = """You are Bhumi Vikas Sahayak, a helper for a BMC building-permission clerk.
Answer ONLY from the CONTEXT rules given. Rules are MP Bhumi Vikas Rules 2012 consolidated upto 06-03-2025.

Rules:
- Reply in the SAME language as the question (Hindi if Devanagari, else English). Plain words.
- Keep the answer SHORT: max 3 lines, then the citation block.
- If VERIFIED_TABLE_VALUE is given, use that number exactly. Never recompute tables yourself.
- Citation block format (always include):
  Rule: <number> | Pages: <start-end>
  Quote: "<verbatim <=40 words from CONTEXT>"
- If the answer is not in CONTEXT, output exactly: NOT_FOUND and nothing else.
- Never invent a rule number, fee, or distance. The clerk decides; you only point to the rule.
"""

def is_hindi(query: str) -> bool:
    return bool(DEVA_RE.search(query))

def build_user_prompt(query, retrieved, calc):
    ctx = []
    for r, score in retrieved:
        txt = r["text"][:2600].replace("\n", " ")
        ctx.append(f"[Rule {r['rule']} — {r['title']} — PDF pages {r['page_start']}-{r['page_end']}]\n{txt}")
    calc_line = f"VERIFIED_TABLE_VALUE: {calc}" if calc else "VERIFIED_TABLE_VALUE: none"
    notfound = NOT_FOUND_HI if is_hindi(query) else NOT_FOUND_EN
    return (
        f"CONTEXT:\n{chr(10).join(ctx)}\n\n{calc_line}\n\n"
        f"NOT_FOUND string to use: {notfound}\n\nQUESTION: {query}\n"
        "Answer now with short answer + citation block, or the NOT_FOUND string."
    )

def call_claude(system: str, user: str) -> str | None:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        from anthropic import Anthropic
        client = Anthropic()
        msg = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
            max_tokens=400, temperature=0,
            system=system, messages=[{"role": "user", "content": user}],
        )
        return msg.content[0].text.strip()
    except Exception:
        return None

def call_cerebras(system: str, user: str) -> str | None:
    key = os.getenv("CEREBRAS_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.cerebras.ai/v1", api_key=key)
        resp = client.chat.completions.create(
            model=os.getenv("CEREBRAS_MODEL", "llama-3.3-70b"),
            temperature=0, max_tokens=400,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return None

def offline_answer(query, retrieved, calc) -> str:
    """Extractive fallback: citation only — pipeline adds headline/secondary/citizen."""
    from rag import short_quote
    r, _ = retrieved[0]
    chunk = r.get("_chunk")
    quote = short_quote(chunk["text"] if chunk else r["text"])
    return (f"Rule: {r['rule']} | Pages: {r['page_start']}-{r['page_end']}\nQuote: \"{quote}\"")

def answer_query(query, retrieved, calc):
    user = build_user_prompt(query, retrieved, calc)
    for fn in (call_claude, call_cerebras):
        out = fn(SYSTEM_PROMPT, user)
        if out:
            return out, "llm"
    return offline_answer(query, retrieved, calc), "offline-extractive"
