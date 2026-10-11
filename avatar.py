"""Sahayak avatar: SVG clerk face with talking/listening animation.
Animation state is driven from JS (speechSynthesis.speaking / mic active),
so lips + meter always stay in sync with the voice."""
import streamlit.components.v1 as components

FACE_SVG = """
<svg viewBox="0 0 200 210" width="170" height="180">
  <circle cx="100" cy="78" r="52" fill="#FFDBB4" stroke="#8D6E63" stroke-width="3"/>
  <path d="M48 78 a52 52 0 0 1 104 0 l0 -14 a52 40 0 0 0 -104 0 z" fill="#37474F"/>
  <rect x="46" y="60" width="108" height="16" rx="8" fill="#1B5E20"/>
  <circle cx="82" cy="78" r="6" fill="#212121" class="eye"/>
  <circle cx="118" cy="78" r="6" fill="#212121" class="eye"/>
  <circle cx="84" cy="76" r="2" fill="white"/><circle cx="120" cy="76" r="2" fill="white"/>
  <path d="M70 66 q12 -8 24 0 M106 66 q12 -8 24 0" stroke="#5D4037" stroke-width="3" fill="none"/>
  <ellipse id="mouth" cx="100" cy="106" rx="12" ry="4" fill="#5D4037"/>
  <circle cx="62" cy="96" r="8" fill="#F8BBD0" opacity="0.7"/>
  <circle cx="138" cy="96" r="8" fill="#F8BBD0" opacity="0.7"/>
  <rect x="55" y="132" width="90" height="60" rx="14" fill="#1B5E20"/>
  <rect x="92" y="132" width="16" height="60" fill="#FAFAFA"/>
  <circle cx="100" cy="176" r="5" fill="#FFC107"/>
</svg>
"""


def avatar_html(state: str = "idle", label: str = "सहायक") -> str:
    ring = {"listening": "#1565C0", "speaking": "#2E7D32"}.get(state, "#BDBDBD")
    anim = ""
    if state == "speaking":
        anim = ("<script>setInterval(()=>{const m=document.getElementById('mouth');"
                "if(m&&window.speaking){const r=3+Math.round(Math.random()*9);"
                "m.setAttribute('ry',r);m.setAttribute('rx',10+Math.round(Math.random()*5));}},140);</script>")
    pulse = ("<style>@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(21,101,192,.5)}"
             "100%{box-shadow:0 0 0 18px rgba(21,101,192,0)}}"
             ".pulse{animation:pulse 1.2s infinite}</style>" if state == "listening" else "")
    bars = ""
    if state == "speaking":
        bars = ("<div style='display:flex;gap:3px;justify-content:center;margin-top:6px'>"
                + "".join(
                    f"<div style='width:6px;background:#2E7D32;border-radius:3px;"
                    f"animation:bar 0.7s ease-in-out {i*0.12}s infinite alternate'></div>"
                    for i in range(7))
                + "</div><style>@keyframes bar{from{height:6px}to{height:22px}}</style>")
    return f"""
<div style="text-align:center;font-family:sans-serif">
<div class="{'pulse' if state=='listening' else ''}"
 style="display:inline-block;border-radius:50%;border:4px solid {ring};padding:6px;background:#FFF8E1">
{FACE_SVG}</div>
<div style="font-weight:700;margin-top:4px">🤖 {label}</div>
<div style="font-size:12px;color:#666">{"🎤 sun raha hai…" if state=='listening' else ("🔊 bol raha hai…" if state=='speaking' else "taiyaar hai")}</div>
{bars}</div>{pulse}{anim}
"""


def show_avatar(state: str = "idle", label: str = "सहायक", key: str = "av"):
    components.html(avatar_html(state, label), height=290)
