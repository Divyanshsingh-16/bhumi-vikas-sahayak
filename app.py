"""Bhumi Vikas Sahayak — kiosk-ready chat for BMC counter. Offline-first, LLM optional."""
import csv
from datetime import datetime
from pathlib import Path

import streamlit as st

from pipeline import pipeline
from patch_2026 import (VERSION_STRING, PATCH_NOTE_EN, PATCH_NOTE_HI,
                        DISCLAIMER_EN, DISCLAIMER_HI)
from llm import is_hindi
from visual import plot_svg
from slip import slip_text, slip_pdf_bytes
from voice import mic_box, speak_button
from calculators import front_open_space, rear_open_space, building_fee
from amendment_forms import AMENDMENT, FORMS, route_form

st.set_page_config(page_title="Bhumi Vikas Sahayak", page_icon="🏠", layout="centered")

LOG_PATH = Path(__file__).parent / "eval" / "counter_log.csv"
CONF_ICON = {"high": "🟢", "medium": "🟡", "low": "🔴"}

with st.sidebar:
    st.header("⚙️ Counter settings")
    kiosk = st.toggle("Kiosk mode (large text)", value=False)
    show_evidence = st.toggle("Show PDF evidence", value=True)
    show_diagram = st.toggle("Show plot diagram", value=True)
    st.divider()
    st.subheader("🎤 Voice input (Hindi + English)")
    mic_box()
    st.divider()
    st.caption(f"📖 {VERSION_STRING}")

if kiosk:
    st.markdown("<style>html{font-size:20px} .stChatMessage{font-size:1.15rem}</style>", unsafe_allow_html=True)

st.title("🏠 Bhumi Vikas Sahayak")
st.caption("Ask the Bhopal building rulebook — get the answer with the rule number.")
st.info(f"📖 Source: {VERSION_STRING}\n\n⚠️ {PATCH_NOTE_EN}")

tab_chat, tab_case, tab_forms, tab_eval = st.tabs(["💬 Chat", "📋 Case file (forms)", "📜 Amendment + Forms", "📊 Officer"])

with tab_case:
    st.subheader("Counter forms — no typing needed")
    c1, c2 = st.columns(2)
    road = c1.number_input("Road width (m)", 0.0, 60.0, 9.0, 0.5)
    area = c2.number_input("Plot area (sq m)", 0.0, 100000.0, 200.0, 1.0)
    built = st.number_input("Proposed built-up area (sq m)", 0.0, 100000.0, 150.0, 1.0)
    use = st.selectbox("Use", ["residential", "shop/commercial"])
    if st.button("Calculate case", type="primary"):
        f, r = front_open_space(road), rear_open_space(area)
        fee = building_fee(built, commercial=(use != "residential"))
        st.success(f"Front: {f} m (R56) · Rear: {r if r else 'Nil'} m (R56) · Fee: Rs {fee} (R21)")
        st.markdown(plot_svg(front=f, rear=(r or 0) or 0.1, lang="en"), unsafe_allow_html=True)
        slip = (f"BHUMI VIKAS SAHAYAK — Case {datetime.now():%d-%m-%Y %H:%M}\n"
                f"Road {road} m -> front {f} m (Rule 56 p.77)\n"
                f"Plot {area} sqm -> rear {r if r else 'Nil'} m (Rule 56 p.78)\n"
                f"Built-up {built} sqm ({use}) -> fee Rs {fee} (Rule 21 p.36-37)\n"
                f"Source: {VERSION_STRING}. Clerk decides; not legal advice.")
        st.download_button("🧾 Download case slip", slip, file_name="case_slip.txt")

with tab_forms:
    st.subheader("28-08-2026 Amendment — Rule 2(5)(c), plots ≤500 sq m")
    st.warning(AMENDMENT["en"])
    st.write(AMENDMENT["hi"])
    st.caption("Source: teamleaseregtech article 59469 (read 10-10-2026). Full amendment text is NOT in our data — verify with the Authority.")
    st.divider()
    st.subheader("Which form / checklist?")
    fq = st.text_input("Describe the work (e.g. new house, shop alteration, layout, revalidation)")
    if fq:
        key = route_form(fq)
        if key:
            f = FORMS[key]
            st.success(f"→ {f['label_en']} / {f['label_hi']}\n\nForm: {f['form']}\n\nFee: {f['fee']}")
            lang_f = st.radio("Checklist language", ["English", "हिंदी"], horizontal=True, key="fl")
            docs = f["docs_en"] if lang_f == "English" else f["docs_hi"]
            for d in docs:
                st.checkbox(d, key=f"doc_{key}_{d[:20]}")
        else:
            st.caption("Ask in chat for guidance.")

with tab_eval:
    st.subheader("How often is it right?")
    st.write("Offline retrieval scores (re-run with `python3 eval/run_v2.py`):")
    try:
        import csv as _csv
        rows = list(_csv.DictReader(open(Path(__file__).parent / "eval" / "results_v2.csv")))
        top3 = sum(1 for r in rows if r["ok_top3"] == "True")
        st.metric("Top-3 rule accuracy", f"{top3}/{len(rows)}")
        # officer analytics from counter log
        try:
            log = list(_csv.DictReader(open(LOG_PATH)))
            from collections import Counter
            st.metric("Counter queries logged", len(log))
            if log:
                st.write("Top rules asked:", dict(Counter(r["rule"] for r in log if r["rule"]).most_common(5)))
                st.write("Not-found rate:", f"{sum(1 for r in log if not r['rule'])}/{len(log)}")
        except FileNotFoundError:
            st.caption("No counter log yet — it builds as the clerk asks.")
        with st.expander("Per-question scores"):
            st.dataframe(rows, height=300)
    except FileNotFoundError:
        st.caption("Run `python3 eval/run_v2.py` to generate scores.")

with tab_chat:
    EXAMPLES = [
        "My house faces a 10 m wide street and will be 9 m tall. How much open space at front?",
        "What is the minimum rear open space for a 150 sq m residential plot?",
        "What is the fee for building permission for a residential house of 150 sqm?",
        "How far must my balcony stay from a low-voltage overhead electric line?",
        "मेरा प्लॉट 200 वर्ग मीटर का है और सामने 9 मीटर चौड़ी सड़क है। आगे कितनी जगह छोड़नी होगी?",
        "बिल्डिंग परमिशन की फीस कितनी है और किस नियम में लिखी है?",
        "12 मीटर चौड़ी सड़क पर सामने कितनी जगह?",
        "How do I pay my property tax online?",
    ]
    if "history" not in st.session_state:
        st.session_state.history = []
    if "votes" not in st.session_state:
        st.session_state.votes = {}

    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLES[:4]):
        if cols[i % 2].button(ex[:44] + "…", key=f"ex{i}"):
            st.session_state.pending = ex
            st.rerun()

    if st.button("▶️ Guided demo (3 questions, ~60 sec)", key="demo"):
        for dq in [EXAMPLES[4], EXAMPLES[2], EXAMPLES[7]]:
            with st.spinner("Niyam khoj rahe hain…"):
                st.session_state.history.append((dq, pipeline(dq)))
        st.rerun()

    query = st.chat_input("Sawal likhein / Ask — English या हिंदी में… (mic above ☝️)")
    if "pending" in st.session_state:
        query = st.session_state.pop("pending")

    if query:
        # follow-up context: short follow-ups inherit the previous question
        if len(query.strip()) < 30 and st.session_state.history:
            last_q = st.session_state.history[-1][0]
            query = f"{last_q} Follow-up: {query}"
        with st.spinner("Niyam khoj rahe hain…"):
            res = pipeline(query)
        st.session_state.history.append((query, res))
        try:
            new = not LOG_PATH.exists()
            with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(["time", "query", "rule", "mode", "score", "confidence"])
                w.writerow([datetime.now().isoformat(timespec="seconds"), query[:200],
                            res.get("rule") or "", res["mode"], round(res.get("score", 0) or 0, 3),
                            res.get("confidence", "")])
        except OSError:
            pass

    PDF_DIR = Path(__file__).parent / "pdf_pages"

    for idx, (q, res) in enumerate(st.session_state.history):
        hi = is_hindi(q)
        lang = "hi" if hi else "en"
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            st.write(res["answer"])
            speak_button(res["answer"], lang, f"sp{idx}")
            st.caption(f"{CONF_ICON.get(res.get('confidence','medium'))} confidence: {res.get('confidence','?')}")
            ent = res.get("entities") or {}
            if ent.get("needs") and not res.get("calc"):
                st.warning(f"❓ {'Aur jaankari dein' if hi else 'Need one more detail'}: {ent['needs']}")
            if res.get("rule"):
                sub = f"({res['subref']})" if res.get("subref") else ""
                st.success(f"📜 Rule {res['rule']}{sub} — {res.get('title','')} | PDF p.{res['pages'][0]}–{res['pages'][1]}")
                with st.expander("Exact text (quote)"):
                    st.write(f"\"{res['quote']}\"")
                retr = res.get("retrieved", [])
                if len(retr) > 1 and retr[1][0]["rule"] in ("103", "12", "28") and retr[1][0]["rule"] != res["rule"]:
                    r2 = retr[1][0]
                    st.info(f"Also see Rule {r2['rule']} — {r2['title']} (p.{r2['page_start']}). "
                            f"{'Rule 103: Development Plan prevails.' if r2['rule']=='103' else ''}")
                if show_diagram and res.get("calc") and res["calc"].get("kind") in ("front_setback", "rear_setback"):
                    c = res["calc"]
                    front = c["value_m"] if c["kind"] == "front_setback" else 3.0
                    rear = c["value_m"] if c["kind"] == "rear_setback" else 1.5
                    st.markdown(plot_svg(front=front, rear=rear or 0.1, lang=lang), unsafe_allow_html=True)
                if show_evidence:
                    p = res["pages"][0]
                    img = PDF_DIR / f"p{p}.png"
                    if img.exists():
                        with st.expander(f"📄 PDF page {p} (source of truth)"):
                            st.image(str(img))
                    else:
                        st.caption(f"PDF evidence: open EN PDF at page {p} to verify.")
                if res["rule"] in ("2", "12") or "500" in q or "300" in q:
                    st.warning(PATCH_NOTE_HI if hi else PATCH_NOTE_EN)
                fk = route_form(q)
                if fk:
                    st.caption(f"📝 Form: {FORMS[fk]['form']} · Fee: {FORMS[fk]['fee']} (see 📜 Amendment + Forms tab for checklist)")
                pdf = slip_pdf_bytes(q, res)
                if pdf:
                    st.download_button("🖨️ Print slip (PDF)", pdf, file_name=f"slip_{idx+1}.pdf",
                                       key=f"pdf{idx}", mime="application/pdf")
                st.download_button("🧾 Slip (text)", slip_text(q, res), file_name=f"slip_{idx+1}.txt", key=f"txt{idx}")
            st.caption(DISCLAIMER_HI if hi else DISCLAIMER_EN)
            c1, c2 = st.columns(2)
            if c1.button("👍", key=f"up{idx}"):
                st.session_state.votes[idx] = "up"
            if c2.button("👎", key=f"dn{idx}"):
                st.session_state.votes[idx] = "down"
            st.caption(f"mode: {res['mode']}" + (f" · score: {res.get('score',0):.2f}" if res.get("score") else "")
                       + (f" · vote: {st.session_state.votes.get(idx)}" if idx in st.session_state.votes else ""))

    st.divider()
    st.caption("More examples — tap to ask:")
    for ex in EXAMPLES[4:]:
        if st.button(ex, key=ex[:24]):
            st.session_state.pending = ex
            st.rerun()
