"""Person-like voice Sahayak: hands-free guided loop (fully client-side JS)
+ one-shot mic-to-Python bridge + auto-speak answers.
STT needs internet (Chrome); TTS + text always work as fallback."""
import html as _html

import streamlit.components.v1 as components

from avatar import FACE_SVG


def _front_js(w):
    return ("(w<=9?3.0:(w<=12?3.6:(w<=18?4.5:6.0)))").replace("w", str(w))


GUIDED_HTML = """
<div style="font-family:sans-serif;text-align:center">
<div id="g_av" style="display:inline-block;border-radius:50%;border:4px solid #BDBDBD;padding:6px;background:#FFF8E1">FACE_SVG</div>
<div style="font-weight:700;margin-top:4px">🤖 सहायक / Sahayak</div>
<div id="g_status" style="font-size:13px;color:#555;min-height:20px">taiyaar — Start dabao, bolo</div>
<div>
<button id="g_lang" style="font-size:13px;padding:6px 10px;margin:4px">🌐 हिंदी</button>
<button id="g_start" style="font-size:16px;padding:10px 18px;background:#1B5E20;color:white;border:none;border-radius:10px">🎤 Baat shuru karo</button>
<button id="g_stop" style="font-size:16px;padding:10px 18px;margin-left:6px">⏹️ Roko</button>
</div>
<div id="g_log" style="text-align:left;background:#FAFAFA;border:1px solid #E0E0E0;border-radius:8px;
  padding:10px;margin-top:8px;max-height:190px;overflow-y:auto;font-size:14px"></div>
</div>
<script>
(function(){
let lang = 'hi', step = 'idle', D = {}, running = false, rec = null;
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
const $ = id => document.getElementById(id);
const deva = {'०':0,'१':1,'२':2,'३':3,'४':4,'५':5,'६':6,'७':7,'८':8,'९':9};
function normNum(s){ s = s.replace(/[०-९]/g, ch=>deva[ch]);
  const m = s.replace(/,/g,'').match(/(\\d+(?:\\.\\d+)?)/); return m ? parseFloat(m[1]) : null; }
function setAv(mode){
  const av = $('g_av');
  av.style.borderColor = mode==='listen' ? '#1565C0' : (mode==='speak' ? '#2E7D32' : '#BDBDBD');
  window.speaking = (mode==='speak');
}
function say(text, next){
  setAv('speak'); $('g_status').innerText = (lang==='hi'?'🔊 bol raha hai…':'🔊 speaking…');
  try{
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = (lang==='hi' ? 'hi-IN' : 'en-IN'); u.rate = 0.95;
    u.onend = ()=>{ setAv('idle'); if(next) next(); };
    u.onerror = ()=>{ setAv('idle'); if(next) next(); };
    speechSynthesis.speak(u);
  }catch(e){ if(next) next(); }
}
function log(who, txt){
  const d = $('g_log');
  d.innerHTML += `<p><b>${who}:</b> ${txt}</p>`; d.scrollTop = d.scrollHeight;
}
const P = {
  hi: { plot:'Namaste! Main Sahayak hu. Aapka plot kitne verg meter ka hai? Jaise: do sau.',
        road:'Samajh gaya. Saamne sadak kitni chaudi hai, meter me? Jaise: nau.',
        height:'Theek hai. Imaarat kitni unchi hogi, meter me?',
        use:'Aavaasiy hai ya dukaan? Aavaasiy kaho ya dukaan.',
        done:(p,r,f,v,h)=>`Aapka hisaab: saamne ${f} meter, peeche ${v} meter. Niyam chhappan. Oonchaai ${h} meter. Dhanyavaad!`,
        bye:'Dhanyavaad! Phir milenge.' },
  en: { plot:'Hello! I am Sahayak. How big is your plot, in square meters? For example: two hundred.',
        road:'Got it. How wide is the road in front, in meters?',
        height:'Okay. How tall will the building be, in meters?',
        use:'Residential or shop? Say residential or shop.',
        done:(p,r,f,v,h)=>`Your numbers: front ${f} meters, rear ${v} meters. Rule fifty six. Height ${h} meters. Thank you!`,
        bye:'Thank you! See you again.' }
};
function front(w){ return w<=9?3.0:(w<=12?3.6:(w<=18?4.5:6.0)); }
function rear(a){ return a<=40?0:(a<=150?1.5:(a<=225?2.5:3.0)); }
function handle(txt){
  log(lang==='hi'?'🧑':'🧑', txt);
  const n = normNum(txt);
  if(step==='plot' && n && n>=10 && n<=100000){ D.plot=n; step='road';
    const t=P[lang].road; log('🤖',t); say(t, listen); }
  else if(step==='road' && n && n>=1 && n<=60){ D.road=n; step='height';
    const t=P[lang].height; log('🤖',t); say(t, listen); }
  else if(step==='height' && n && n>=1 && n<=100){ D.h=n; step='use';
    const t=P[lang].use; log('🤖',t); say(t, listen); }
  else if(step==='use'){
    const comm = /shop|commercial|dukaan|दुकान|vyapaar/i.test(txt);
    const t=P[lang].done(D.plot,D.road,front(D.road),rear(D.plot),D.h);
    log('🤖',t); step='idle'; say(t, ()=>{ running=false; setAv('idle');
      $('g_status').innerText = (lang==='hi'?'Ho gaya! Dobara? Start dabao.':'Done! Again? Press Start.'); });
  }
  else { const t = P[lang][step] || P[lang].plot; log('🤖',t); say(t, listen); }
}
function listen(){
  if(!running) return;
  if(!SR){ $('g_status').innerText='Mic not supported — use Chrome.'; running=false; return; }
  setAv('listen'); $('g_status').innerText=(lang==='hi'?'🎤 sun raha hu… bolo':'🎤 listening… speak');
  try{
    rec = new SR(); rec.lang = (lang==='hi'?'hi-IN':'en-IN'); rec.interimResults=false;
    rec.onresult = e => handle(e.results[0][0].transcript);
    rec.onerror = e => { $('g_status').innerText='Mic error: '+e.error+' — tap Start again.'; running=false; setAv('idle'); };
    rec.onend = ()=>{ if(running && step!=='idle' && !window.speaking){ setTimeout(()=>listen(), 400); } };
    rec.start();
    setTimeout(()=>{ try{ if(running && step!=='idle') rec.stop(); }catch(e){} }, 12000);
  }catch(e){ running=false; }
}
$('g_start').onclick = ()=>{ running=true; D={}; step='plot';
  const t=P[lang].plot; log('🤖',t); say(t, listen); };
$('g_stop').onclick = ()=>{ running=false; step='idle'; try{speechSynthesis.cancel();rec&&rec.stop();}catch(e){}
  setAv('idle'); const t=P[lang].bye; log('🤖',t); say(t,null); };
$('g_lang').onclick = (e)=>{ lang = (lang==='hi'?'en':'hi');
  e.target.innerText = (lang==='hi'?'🌐 हिंदी':'🌐 English'); };
})();
</script>
""".replace("FACE_SVG", FACE_SVG)


def guided_voice_bot(height: int = 560):
    """Hands-free person-like loop. Needs internet for mic; TTS + text always shown."""
    components.html(GUIDED_HTML, height=height)


def say_on_render(text: str, lang: str, auto: bool = True):
    """Auto-speak an answer when rendered (same-language voice). No-op if auto off."""
    if not auto or not text:
        return
    safe = _html.escape(text[:280]).replace("\n", " ")
    voice = "hi-IN" if lang == "hi" else "en-IN"
    components.html(
        f"""<script>try{{speechSynthesis.cancel();
var u=new SpeechSynthesisUtterance('{safe}');u.lang='{voice}';u.rate=0.95;
u.onend=()=>{{window.speaking=false;}};window.speaking=true;speechSynthesis.speak(u);}}catch(e){{}}</script>""",
        height=0,
    )


def hear_once(lang: str = "hi-IN", key: str = "hear") -> str | None:
    """One-shot mic -> transcript string in Python (needs streamlit-javascript + internet).
    Returns None if unavailable; '__ERROR__:..' / '__TIMEOUT__' on failure."""
    try:
        from streamlit_javascript import st_javascript
    except ImportError:
        return None
    js = (
        "new Promise((resolve)=>{ const SR=window.SpeechRecognition||window.webkitSpeechRecognition;"
        f" if(!SR){{resolve('__NOSUPPORT__');return;}} const r=new SR(); r.lang='{lang}'; r.interimResults=false;"
        " const to=setTimeout(()=>{try{r.stop()}catch(e){} resolve('__TIMEOUT__');},12000);"
        " r.onresult=(e)=>{clearTimeout(to); resolve(e.results[0][0].transcript);};"
        " r.onerror=(e)=>{clearTimeout(to); resolve('__ERROR__:'+e.error);}; r.start(); })"
    )
    try:
        return st_javascript(js, key=key)
    except Exception:
        return None
