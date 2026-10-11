"""Browser voice (Web Speech API): zero-backend, works offline in Chrome.
STT: mic -> transcript shown + auto-copied; clerk pastes into chat box (1 tap).
TTS: 🔊 button under every answer reads it aloud (hi-IN / en-IN)."""
import html
import streamlit.components.v1 as components


def mic_box():
    components.html(
        """
<div style="font-family:sans-serif">
<button id="mic_hi" style="font-size:16px;padding:8px 12px">🎤 हिंदी बोले</button>
<button id="mic_en" style="font-size:16px;padding:8px 12px">🎤 Speak English</button>
<p id="vout" style="background:#f5f5f5;padding:8px;border-radius:6px;min-height:40px">…</p>
<button id="vcopy" style="font-size:14px">📋 Copy</button>
<script>
let lastText = "";
function listen(lang){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  const out = document.getElementById('vout');
  if(!SR){ out.innerText = 'Mic not supported in this browser. Use Chrome.'; return; }
  const r = new SR(); r.lang = lang; r.interimResults = false;
  out.innerText = 'सुन रहे हैं… listening…';
  r.onresult = (e)=>{ lastText = e.results[0][0].transcript; out.innerText = lastText;
    try{ navigator.clipboard.writeText(lastText); }catch(err){} };
  r.onerror = (e)=>{ out.innerText = 'Error: ' + e.error; };
  r.start();
}
document.getElementById('mic_hi').onclick = ()=>listen('hi-IN');
document.getElementById('mic_en').onclick = ()=>listen('en-IN');
document.getElementById('vcopy').onclick = ()=>{ try{ navigator.clipboard.writeText(lastText);}catch(e){} };
</script>
<p style="font-size:12px;color:#666">Transcript auto-copies → paste (Ctrl+V) into the chat box below.</p>
</div>
""",
        height=230,
    )


def speak_button(text: str, lang: str, key: str):
    safe = html.escape(text[:300]).replace("\n", " ")
    voice = "hi-IN" if lang == "hi" else "en-IN"
    components.html(
        f"""<button onclick="speechSynthesis.cancel();var u=new SpeechSynthesisUtterance('{safe}');u.lang='{voice}';speechSynthesis.speak(u);"
style="font-size:14px">🔊 Suno / Listen</button>""",
        height=45,
    )
