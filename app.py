"""Bhumi Vikas Sahayak — counter tool for BMC building permissions. Offline-first, LLM optional."""
import csv
import math
import urllib.parse as urlparse
from datetime import datetime, date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from pipeline import pipeline
from patch_2026 import (VERSION_STRING, PATCH_NOTE_EN, PATCH_NOTE_HI,
                        DISCLAIMER_EN, DISCLAIMER_HI, AMEND_QUOTE_EN, AMEND_QUOTE_HI, AMEND_REF)
from llm import is_hindi
from visual import plot_svg
from slip import slip_text, slip_pdf_bytes, case_report_pdf_bytes
from voice import mic_box, speak_button
from voice_loop import guided_voice_bot, say_on_render, hear_once
from avatar import show_avatar
from bot import bot_reply, QUICK_PLOTS
from building3d import building_3d_html, BHOPAL_MAP_IFRAME
from violation import check_proposal, verdict
from calculators import (front_open_space, rear_open_space, fee_breakdown,
                         plantation_needed, rwh_needed)
from amendment_forms import AMENDMENT, FORMS, route_form
from dates import permission_timeline, occupancy_deadline
from faq import FAQ
from i18n import t
from journey import journey_html, STEPS

st.set_page_config(page_title="Bhumi Vikas Sahayak", page_icon="🏠", layout="wide")

LOG_PATH = Path(__file__).parent / "eval" / "counter_log.csv"
VOTES_PATH = Path(__file__).parent / "eval" / "votes.csv"
CONF_ICON = {"high": "🟢", "medium": "🟡", "low": "🔴"}


def save_vote(idx, query, vote):
    try:
        new = not VOTES_PATH.exists()
        with open(VOTES_PATH, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["time", "idx", "query", "vote"])
            w.writerow([datetime.now().isoformat(timespec="seconds"), idx, query[:200], vote])
    except OSError:
        pass

st.markdown("""
<style>
.hero-bar{height:6px;border-radius:3px;background:linear-gradient(90deg,#FF9933 0%,#FFFFFF 50%,#138808 100%);margin-bottom:10px}
.stat-chip{display:inline-block;background:#E8F5E9;border:1px solid #A5D6A7;border-radius:20px;
  padding:4px 14px;margin:2px;font-size:14px;font-weight:600;color:#1B5E20}
.answer-card{background:#FAFAFA;border:1px solid #E0E0E0;border-left:5px solid #1B5E20;
  border-radius:8px;padding:12px 14px;margin:6px 0}
.rule-chip{display:inline-block;background:#1B5E20;color:white;border-radius:6px;
  padding:2px 10px;font-size:13px;font-weight:700}
.conf-pill{display:inline-block;border-radius:12px;padding:1px 10px;font-size:12px;font-weight:600}
.quote-box{border-left:3px solid #9E9E9E;padding:6px 12px;color:#424242;font-style:italic;margin:8px 0}
</style>
<div class="hero-bar"></div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Counter settings")
    ui_lang = st.radio("🌐 भाषा / Language", ["English", "हिंदी"], horizontal=True)
    UL = "hi" if ui_lang == "हिंदी" else "en"
    kiosk = st.toggle("Kiosk mode (large text + contrast)", value=False)
    auto_say = st.toggle("🔊 Jawab bolkar sunao (auto-speak)", value=False)
    tts_rate = st.slider("🗣️ Bolne ki gati (voice speed)", 0.7, 1.3, 0.95, 0.05)
    tts_voice = st.text_input("🎙️ Voice name (optional, jaise Google हिन्दी)", value="")
    from voice import tts_settings_box
    tts_settings_box(tts_rate, tts_voice)
    show_evidence = st.toggle("Show PDF evidence", value=True)
    show_diagram = st.toggle("Show plot diagram", value=True)
    dev_mode = st.toggle("🛠️ Developer details", value=False)
    st.divider()
    st.subheader("🎤 Voice input (Hindi + English)")
    mic_box()
    st.divider()
    st.caption(f"📖 {VERSION_STRING}")

if kiosk:
    st.markdown("""<style>
html{font-size:22px} .stChatMessage{font-size:1.25rem}
.stButton>button{font-size:1.15rem !important;padding:12px 20px !important;border-radius:12px !important}
.answer-card{font-size:1.15rem}
</style>""", unsafe_allow_html=True)

st.title("🏠 Bhumi Vikas Sahayak" if UL == "en" else "🏠 भूमि विकास सहायक")
st.caption(t("tagline", UL))
c1, c2, c3 = st.columns(3)
c1.markdown('<span class="stat-chip">📜 106 rules</span>', unsafe_allow_html=True)
c2.markdown('<span class="stat-chip">🎯 84/84 answers traced</span>', unsafe_allow_html=True)
c3.markdown('<span class="stat-chip">🗣️ EN + हिंदी + 🎤</span>', unsafe_allow_html=True)
st.info(f"📖 Source: {VERSION_STRING}\n\n⚠️ {PATCH_NOTE_EN if UL=='en' else PATCH_NOTE_HI}")

tab_chat, tab_bot, tab_3d, tab_case, tab_forms, tab_eval = st.tabs(
    ["💬 Chat", "🤖 Sahayak Bot", "🏙️ 3D View", "📋 Case file (forms)", "📜 Amendment + Forms", "📊 Officer"])

with tab_bot:
    st.subheader("🤖 Sahayak — guided, no typing needed")
    st.caption("Tap quick replies or type numbers. Speaks Hindi + English.")
    show_avatar(state="idle", label="सहायक", key="botav")
    with st.expander("🎙️ Person-like voice Sahayak (hands-free — bolo, jawab suno)", expanded=False):
        st.caption("Start dabao → Hindi/English me bolo → Sahayak bolkar jawab dega → mic khud wapas sunega. Mic ke liye internet chahiye; text hamesha saath hai.")
        guided_voice_bot()
    if "bot_state" not in st.session_state:
        st.session_state.bot_state = {"step": "greet", "lang": "en"}
        st.session_state.bot_hist = []
    if not st.session_state.bot_hist:
        rep, st.session_state.bot_state, _ = bot_reply(dict(st.session_state.bot_state), None)
        st.session_state.bot_hist.append(("bot", rep))
    for who, msg in st.session_state.bot_hist:
        with st.chat_message("assistant" if who == "bot" else "user"):
            st.markdown(msg)
    if st.session_state.bot_state.get("step") == "plot":
        cols = st.columns(3)
        for i, p in enumerate(QUICK_PLOTS):
            if cols[i % 3].button(f"{p} sqm", key=f"qp{i}"):
                rep, st.session_state.bot_state, _ = bot_reply(dict(st.session_state.bot_state), str(p))
                st.session_state.bot_hist.append(("user", f"{p} sqm"))
                st.session_state.bot_hist.append(("bot", rep))
                st.rerun()
    bq = st.chat_input("Bot se baat karein…", key="botinput")
    if bq:
        st.session_state.bot_hist.append(("user", bq))
        rep, st.session_state.bot_state, done = bot_reply(dict(st.session_state.bot_state), bq)
        st.session_state.bot_hist.append(("bot", rep))
        say_on_render(rep, "hi" if is_hindi(bq + rep) else "en",
                      auto=st.session_state.get("bot_autosay", False))
        if done:
            st.session_state.bot_state = {"step": "greet", "lang": st.session_state.bot_state.get("lang", "en")}
        st.rerun()
    st.toggle("🔊 Bot jawab bolkar de (auto-speak)", value=False, key="bot_autosay")

with tab_3d:
    st.subheader("🏙️ 3D plot + building (drag to rotate)")
    v1, v2, v3 = st.columns(3)
    v_road = v1.number_input("Road width (m)", 0.0, 60.0, 9.0, 0.5, key="v3road")
    v_plot = v2.number_input("Plot area (sqm)", 0.0, 100000.0, 200.0, 1.0, key="v3plot")
    v_height = v3.number_input("Building height (m)", 0.0, 100.0, 9.0, 0.5, key="v3h")
    v4, v5, v6 = st.columns(3)
    v_front = v4.number_input("Proposed front gap (m)", 0.0, 30.0, 3.0, 0.1, key="v3f")
    v_rear = v5.number_input("Proposed rear gap (m)", 0.0, 30.0, 1.5, 0.1, key="v3r")
    v_floors = v6.number_input("Floors", 1, 30, 3, 1, key="v3fl")
    req_f, req_r = front_open_space(v_road), rear_open_space(v_plot)
    checks = check_proposal(plot_sqm=v_plot, road_m=v_road, front_m=v_front, rear_m=v_rear,
                            height_m=v_height, floors=v_floors)
    status, msg = verdict(checks)
    if status == "pass":
        st.success(msg)
    elif status == "fail":
        st.error(msg)
    else:
        st.info(msg)
    for c in checks:
        icon = "✅" if c["ok"] else ("❌" if c["ok"] is False else "ℹ️")
        st.write(f"{icon} {c['item']}: proposed **{c['proposed']}** vs required **{c['required']}** (Rule {c['rule']})")
    pw = math.sqrt(v_plot * 0.6) or 10
    pd = (v_plot / pw) if pw else 20
    components.html(building_3d_html(plot_w=round(pw, 1), plot_d=round(pd, 1),
                                     front=req_f, rear=req_r or 0.1, side=1.5,
                                     height=v_height, floors=v_floors,
                                     violations=[c["item"] for c in checks if c["ok"] is False],
                                     lang=UL, far_max_height=round(v_height * 1.5, 1),
                                     uid="b3dmain"),
                    height=680)
    st.markdown(plot_svg(front=req_f, rear=req_r or 0.1, lang="en"), unsafe_allow_html=True)
    st.divider()
    st.subheader("📍 Bhopal — counter map")
    components.html(BHOPAL_MAP_IFRAME, height=440)

with tab_case:
    st.subheader("Counter forms — no typing needed" if UL == "en" else "काउंटर फॉर्म — टाइपिंग नहीं चाहिए")
    c1, c2 = st.columns(2)
    road = c1.number_input("Road width (m)", 0.0, 60.0, 9.0, 0.5)
    area = c2.number_input("Plot area (sq m)", 0.0, 100000.0, 200.0, 1.0)
    built = st.number_input("Proposed built-up area (sq m)", 0.0, 100000.0, 150.0, 1.0)
    u1, u2 = st.columns(2)
    use = u1.selectbox("Use", ["residential", "shop/commercial", "shop-cum-residence", "cinema"])
    highrise = u2.toggle("High-rise (>10 storeys / >30 m)", value=False)
    if st.button("Calculate case", type="primary"):
        f, r = front_open_space(road), rear_open_space(area)
        rows, total = fee_breakdown(built, use=("commercial" if use.startswith("shop/") else use),
                                    highrise=highrise)
        st.success(f"Front: {f} m (R56) · Rear: {r if r else 'Nil'} m (R56) · Total fee: Rs {total} (R21)")
        trees, rwh = plantation_needed(area), rwh_needed(area)
        green = []
        if trees:
            green.append(f"🌳 Plant {trees} tree(s) before occupancy (Rule 67)")
        if rwh:
            green.append("🌧️ Rain/roof-water harvesting required (Rule 81(4))")
        for g in green:
            st.info(g)
        with st.expander("💰 Fee breakdown (Rule 21)" if UL == "en" else "💰 शुल्क विवरण (नियम 21)"):
            for label, rs in rows:
                st.write(f"• {label}: **Rs {rs}**")
            st.write(f"**Total: Rs {total}**")
        st.markdown(plot_svg(front=f, rear=(r or 0) or 0.1, lang="en"), unsafe_allow_html=True)
        slip = (f"BHUMI VIKAS SAHAYAK — Case {datetime.now():%d-%m-%Y %H:%M}\n"
                f"Road {road} m -> front {f} m (Rule 56 p.77)\n"
                f"Plot {area} sqm -> rear {r if r else 'Nil'} m (Rule 56 p.78)\n"
                f"Built-up {built} sqm ({use}{' high-rise' if highrise else ''}) -> fee Rs {total} (Rule 21)\n"
                + "\n".join(f"  {label}: Rs {rs}" for label, rs in rows) + "\n"
                + "\n".join(f"  {g}" for g in green) + "\n"
                f"Source: {VERSION_STRING}. Clerk decides; not legal advice.")
        st.download_button("🧾 Download case slip", slip, file_name="case_slip.txt")
        _case = {"area": area, "road": road, "built": built, "use": use, "front": f,
                 "rear": (r if r else "Nil"), "fee": total, "rows": rows, "green": green,
                 "timeline": permission_timeline(date.today())}
        _pdf = case_report_pdf_bytes(_case)
        if _pdf:
            st.download_button("📕 Full case report (PDF)", _pdf, file_name="case_report.pdf",
                               mime="application/pdf")
        cname = st.text_input("Save this case as (name)", key="casename")
        if st.button("💾 Save case", key="savecase") and cname:
            cp = Path(__file__).parent / "eval" / "cases.csv"
            new = not cp.exists()
            with open(cp, "a", newline="", encoding="utf-8") as cf:
                w = csv.writer(cf)
                if new:
                    w.writerow(["name", "time", "road", "area", "built", "use", "highrise",
                                "front", "rear", "fee"])
                w.writerow([cname, datetime.now().isoformat(timespec="seconds"), road, area,
                            built, use, highrise, f, r if r else "Nil", total])
            st.success(f"Saved '{cname}'")
    with st.expander("📂 Saved cases" if UL == "en" else "📂 सहेजे केस"):
        try:
            saved = list(csv.DictReader(open(Path(__file__).parent / "eval" / "cases.csv")))
            for s in saved[-10:]:
                st.write(f"**{s['name']}** — road {s['road']}m, plot {s['area']}sqm, "
                         f"front {s['front']}m, rear {s['rear']}m, fee Rs {s['fee']}")
        except FileNotFoundError:
            st.caption("No saved cases yet.")

with tab_forms:
    st.subheader("28-08-2026 Gazette — Rule 2(5)(c), plots ≤500 sq m")
    st.warning(AMENDMENT["en"])
    st.write(AMENDMENT["hi"])
    st.caption(f"Source: {AMEND_REF} (copy in repo resources/). "
               "Status: DRAFT for 15-day objections — confirm final position with the Authority.")
    with st.expander("📜 Exact gazette text (English)"):
        st.write(f'"{AMEND_QUOTE_EN}"')
    with st.expander("📜 राजपत्र पाठ (हिंदी)"):
        st.write(f'"{AMEND_QUOTE_HI}"')
    for _aimg, _alab in (("a1.png", "Gazette p.313 (Hindi draft)"), ("a2.png", "Gazette p.314 (English text)")):
        _p = Path(__file__).parent / "pdf_pages" / _aimg
        if _p.exists():
            with st.expander(f"📰 {_alab}"):
                st.image(str(_p))
    st.divider()
    st.subheader("🗺️ Application journey (click a step)" if UL == "en" else "🗺️ आवेदन यात्रा")
    components.html(journey_html(lang=UL, done=int(st.session_state.get("jstep", 0))), height=110)
    jc = st.columns(5)
    for i, s in enumerate(STEPS):
        if jc[i].button(f"{i+1}. {s['hi' if UL=='hi' else 'en'][:22]}…", key=f"j{i}"):
            st.session_state["jstep"] = i
            st.rerun()
    cur = STEPS[int(st.session_state.get("jstep", 0))]
    st.info(f"**{cur['hi' if UL=='hi' else 'en']}** (Rule {cur['rule']})\n\n{cur['detail_hi' if UL=='hi' else 'detail_en']}")
    st.divider()
    st.subheader("🔗 Rule map: permission chain" if UL == "en" else "🔗 नियम-श्रृंखला")
    from flow import flow_svg
    st.markdown(flow_svg(lang=UL), unsafe_allow_html=True)
    st.caption("12 permission → 14 apply → 21 fee → 23 validity → 31 occupy" if UL == "en"
               else "12 अनुमति → 14 आवेदन → 21 शुल्क → 23 वैधता → 31 अधिभोग")
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
    st.divider()
    st.subheader("📅 Deadline calculator" if UL == "en" else "📅 समय-सीमा गणक")
    applied = st.date_input("Application date", value=date(2026, 1, 10), key="appdate")
    if st.button("Show dates", key="dates"):
        tl = permission_timeline(applied)
        st.write(f"Valid until: **{tl['valid_until']}** (3 yrs) · Renewals: **{tl['renewal_1_until']}**, **{tl['renewal_2_until']}** (Rule 23)")
        st.write(f"Occupancy decision by: **{occupancy_deadline(applied)}** (30 days, Rule 31)")
        st.caption(tl["note"])

with tab_eval:
    st.subheader("How often is it right?")
    st.write("Offline retrieval scores (re-run with `python3 eval/run_v2.py`):")
    try:
        rows = list(csv.DictReader(open(Path(__file__).parent / "eval" / "results_v2.csv")))
        top3 = sum(1 for r in rows if r["ok_top3"] == "True")
        st.metric("Top-3 rule accuracy", f"{top3}/{len(rows)}")
        # officer analytics from counter log
        try:
            log = list(csv.DictReader(open(LOG_PATH)))
            from collections import Counter
            st.metric("Counter queries logged", len(log))
            if log:
                st.write("Top rules asked:", dict(Counter(r["rule"] for r in log if r["rule"]).most_common(5)))
                st.write("Not-found rate:", f"{sum(1 for r in log if not r['rule'])}/{len(log)}")
        except FileNotFoundError:
            st.caption("No counter log yet — it builds as the clerk asks.")
        with st.expander("Per-question scores"):
            st.dataframe(rows, height=300)
        with st.expander("🏥 System health" if UL == "en" else "🏥 सिस्टम स्थिति"):
            import os as _os
            st.write("Claude API:", "✅ key present" if _os.getenv("ANTHROPIC_API_KEY") else "⚪ not set (offline mode)")
            st.write("Cerebras API:", "✅ key present" if _os.getenv("CEREBRAS_API_KEY") else "⚪ not set (offline mode)")
            components.html(
                """<div id="hz" style="font-size:13px">checking…</div><script>
Promise.all([
 fetch('https://unpkg.com/three@0.160.0/build/three.module.js',{method:'HEAD',mode:'no-cors'}).then(()=>1).catch(()=>0),
 fetch('https://www.openstreetmap.org/',{method:'HEAD',mode:'no-cors'}).then(()=>1).catch(()=>0)
]).then(r=>{document.getElementById('hz').innerHTML =
 '3D CDN: '+(r[0]?'✅':'❌ offline-2D')+' · Map: '+(r[1]?'✅':'❌')});</script>""",
                height=40,
            )
            from cache import popular as _popular
            pop = _popular(5)
            if pop:
                st.write("🔥 Most asked:")
                for _q, _r, _c in pop:
                    st.write(f"×{_c} Rule {_r}: {_q[:60]}")
        with st.expander("👎 Feedback review (wrong answers to fix)" if UL == "en" else "👎 सुधार सूची"):
            votes = st.session_state.get("votes", {})
            bad = [(i, q) for i, (q, r) in enumerate(st.session_state.get("history", []))
                   if votes.get(i) == "down"]
            if bad:
                for i, q in bad:
                    st.write(f"#{i+1}: {q[:90]}")
            else:
                st.caption("No 👎 yet — good sign.")
        try:
            chlog = list(csv.DictReader(open(LOG_PATH)))
            if chlog:
                from collections import Counter as _C2
                st.bar_chart(dict(_C2(r["rule"] for r in chlog if r["rule"]).most_common(10)))
        except FileNotFoundError:
            pass
        with st.expander("📰 Daily digest" if UL == "en" else "📰 दैनिक सार"):
            try:
                log = list(csv.DictReader(open(LOG_PATH)))
            except FileNotFoundError:
                log = []
            try:
                all_votes = list(csv.DictReader(open(VOTES_PATH)))
            except FileNotFoundError:
                all_votes = []
            if log or all_votes:
                from collections import Counter as _C
                counts = _C(r["rule"] for r in log if r["rule"])
                nf = sum(1 for r in log if not r["rule"])
                ups = sum(1 for r in all_votes if r["vote"] == "up")
                dns = sum(1 for r in all_votes if r["vote"] == "down")
                dg = (f"BHUMI SAHAYAK — daily digest {datetime.now():%d-%m-%Y}\n"
                      f"Queries: {len(log)} | Not-found: {nf} | Votes: {ups} up / {dns} down\n"
                      f"Top rules: {dict(counts.most_common(5))}\nClerk decides; not legal advice.")
                st.text(dg)
                st.download_button("⬇️ Download digest", dg, file_name="digest.txt")
            else:
                st.caption("No counter log yet.")
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
    citizen = st.toggle("👁️ Citizen view (big result only)", value=False)

    if citizen and st.session_state.history:
        q, res = st.session_state.history[-1]
        st.markdown("<style>.bigans{font-size:1.6rem;line-height:1.5}</style>", unsafe_allow_html=True)
        st.markdown(f'<div class="answer-card bigans">{res["answer"].split(chr(10))[0]}</div>',
                    unsafe_allow_html=True)
        if res.get("rule"):
            st.markdown(f'<span class="rule-chip">📜 Rule {res["rule"]}</span>', unsafe_allow_html=True)
        st.divider()

    if not st.session_state.history:
        st.markdown(f'<span class="stat-chip">👉 {t("steps", UL)}</span>', unsafe_allow_html=True)

    cols = st.columns(2)

    cols = st.columns(2)
    for i, ex in enumerate(EXAMPLES[:4]):
        if cols[i % 2].button(ex[:44] + "…", key=f"ex{i}"):
            st.session_state.pending = ex
            st.rerun()

    if st.button(t("demo_btn", UL), key="demo"):
        for dq in [EXAMPLES[4], EXAMPLES[2], EXAMPLES[7]]:
            with st.spinner(t("searching", UL)):
                st.session_state.history.append((dq, pipeline(dq)))
        st.rerun()

    mc1, mc2 = st.columns([1, 3])
    if mc1.button("🎤 Bolo (mic → chat)", key="micchat"):
        st.session_state["mic_n"] = st.session_state.get("mic_n", 0) + 1
        st.session_state["mic_wait"] = True
        st.rerun()
    if st.session_state.pop("mic_wait", False):
        with st.spinner("🎤 Sun rahe hain… bolo" if UL == "hi" else "🎤 Listening… speak"):
            heard = hear_once("hi-IN" if UL == "hi" else "en-IN", key=f"hear{st.session_state.get('mic_n', 0)}")
        if heard and not heard.startswith("__"):
            st.session_state.pending = heard
            st.rerun()
        elif heard:
            st.warning("Mic nahi chala (Chrome + internet chahiye) — type karo." if UL == "hi"
                       else "Mic failed (needs Chrome + internet) — please type.")

    with st.expander("⚡ Instant answers (no waiting)" if UL == "en" else "⚡ तुरंत उत्तर"):
        fq_cols = st.columns(2)
        for i, (keys, (rule, pages, a_en, a_hi)) in enumerate(FAQ):
            ans = a_en if UL == "en" else a_hi
            if fq_cols[i % 2].button(f"Rule {rule}: {keys[0]}", key=f"faq{rule}{keys[0]}"):
                st.session_state.history.append(
                    (keys[0], {"answer": ans, "rule": rule, "pages": (int(pages), int(pages)),
                               "quote": ans, "title": "", "mode": "faq-instant", "calc": None,
                               "retrieved": [], "score": 1.0, "subref": "", "entities": {},
                               "confidence": "high", "followups": []}))
                st.rerun()

    query = st.chat_input(t("ask_ph", UL))
    if "pending" in st.session_state:
        query = st.session_state.pop("pending")

    if query:
        # follow-up context: short follow-ups inherit the previous question
        if len(query.strip()) < 30 and st.session_state.history:
            last_q = st.session_state.history[-1][0]
            query = f"{last_q} Follow-up: {query}"
        with st.spinner(t("searching", UL)):
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
        hi = is_hindi(q) or is_hindi(res.get("answer", ""))
        lang = "hi" if hi else "en"
        with st.chat_message("user"):
            st.write(q)
        with st.chat_message("assistant"):
            conf = res.get("confidence", "?")
            conf_color = {"high": "#2E7D32", "medium": "#EF6C00", "low": "#C62828"}.get(conf, "#616161")
            st.markdown(f'<div class="answer-card">{res["answer"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="conf-pill" style="background:{conf_color}22;color:{conf_color};'
                        f'border:1px solid {conf_color}">{CONF_ICON.get(conf, "⚪")} {conf}</span>',
                        unsafe_allow_html=True)
            if res.get("asked", 0) > 1:
                st.caption(f"🔁 {res['asked']} baar pucha gaya" if hi else f"🔁 asked {res['asked']} times")
            speak_button(res["answer"], lang, f"sp{idx}")
            if auto_say:
                from voice_loop import say_on_render as _say
                _say(res["answer"], lang, auto=True)
            ent = res.get("entities") or {}
            if ent.get("needs") and not res.get("calc"):
                st.warning(f"❓ {'Aur jaankari dein' if hi else 'Need one more detail'}: {ent['needs']}")
            if res.get("rule"):
                sub = f"({res['subref']})" if res.get("subref") else ""
                st.markdown(f'<span class="rule-chip">📜 Rule {res["rule"]}{sub}</span> '
                            f'**{res.get("title","")}** | PDF p.{res["pages"][0]}–{res["pages"][1]}',
                            unsafe_allow_html=True)
                with st.expander(t("exact_text", UL)):
                    st.markdown(f'<div class="quote-box">"{res["quote"]}"</div>', unsafe_allow_html=True)
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
                        with st.expander(f"📄 {t('evidence', UL, p=p)}"):
                            st.image(str(img))
                    else:
                        st.caption(t("evidence_hint", UL, p=p))
                if res["rule"] in ("2", "12") or "500" in q or "300" in q:
                    st.warning(PATCH_NOTE_HI if hi else PATCH_NOTE_EN)
                    from patch_2026 import AMEND_QUOTE_EN, AMEND_QUOTE_HI, AMEND_REF
                    with st.expander("📜 28-08-2026 gazette text" if UL == "en" else "📜 28-08-2026 राजपत्र पाठ"):
                        st.write(f'"{AMEND_QUOTE_HI if hi else AMEND_QUOTE_EN}"')
                        st.caption(AMEND_REF + " — DRAFT for objections; confirm final status.")
                    for _aimg, _alab in (("a1.png", "p.313"), ("a2.png", "p.314")):
                        _p = PDF_DIR / _aimg
                        if _p.exists():
                            with st.expander(f"📰 Rajpatra {_alab}"):
                                st.image(str(_p))
                fk = route_form(q)
                if fk:
                    st.caption(f"📝 Form: {FORMS[fk]['form']} · Fee: {FORMS[fk]['fee']} (see 📜 Amendment + Forms tab for checklist)")
                for label, fq in (res.get("followups") or []):
                    if st.button(f"➡️ {label}", key=f"fu{idx}_{label}"):
                        st.session_state.pending = fq
                        st.rerun()
                pdf = slip_pdf_bytes(q, res)
                if pdf:
                    st.download_button(t("print_pdf", UL), pdf, file_name=f"slip_{idx+1}.pdf",
                                       key=f"pdf{idx}", mime="application/pdf")
                st.download_button(t("slip_txt", UL), slip_text(q, res), file_name=f"slip_{idx+1}.txt", key=f"txt{idx}")
                import urllib.parse as _up
                wa = "https://wa.me/?text=" + urlparse.quote(f"Bhumi Vikas Sahayak — Rule {res['rule']}\n" + res["answer"][:800])
                st.link_button("📲 WhatsApp par bhejo", wa)
            st.caption(DISCLAIMER_HI if hi else DISCLAIMER_EN)
            c1, c2 = st.columns(2)
            if c1.button("👍", key=f"up{idx}"):
                st.session_state.votes[idx] = "up"
                save_vote(idx, q, "up")
            if c2.button("👎", key=f"dn{idx}"):
                st.session_state.votes[idx] = "down"
                save_vote(idx, q, "down")
            if dev_mode:
                st.caption(f"mode: {res['mode']}" + (f" · score: {res.get('score',0):.2f}" if res.get("score") else "")
                           + (f" · vote: {st.session_state.votes.get(idx)}" if idx in st.session_state.votes else ""))

    st.divider()
    st.caption(t("examples", UL))
    for ex in EXAMPLES[4:]:
        if st.button(ex, key=ex[:24]):
            st.session_state.pending = ex
            st.rerun()

st.divider()
st.caption(
    f"🏠 {'Bhumi Vikas Sahayak' if UL == 'en' else 'भूमि विकास सहायक'} · "
    f"{'Rules upto 06-03-2025 + Rajpatra 28-08-2026' if UL == 'en' else 'नियम 06-03-2025 तक + राजपत्र 28-08-2026'} · "
    f"{DISCLAIMER_EN if UL == 'en' else DISCLAIMER_HI}"
)
