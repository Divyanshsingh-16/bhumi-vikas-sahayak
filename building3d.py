"""Full-wow 3D plot+building viewer (three.js modules + OrbitControls via CDN).
Zoom + rotate + pan, shadows, windows, trees, setback labels, FAR envelope,
required-vs-proposed morph, view presets, violation pulse, click-info.
Offline (no CDN): shows 2D-SVG fallback message instead."""

IMPORTMAP = """
<script type="importmap">
{"imports":{
"three":"https://unpkg.com/three@0.160.0/build/three.module.js",
"three/addons/":"https://unpkg.com/three@0.160.0/examples/jsm/"}}
</script>
"""


def building_3d_html(plot_w=12.0, plot_d=20.0, front=3.0, rear=1.5, side=1.5,
                      height=9.0, floors=3, violations=(), lang="en",
                      far_max_height=None, uid="b3d"):
    import json as _json
    cfg = _json.dumps({"plot_w": plot_w, "plot_d": plot_d, "front": front, "rear": rear,
                       "side": side, "height": height, "floors": max(1, int(floors or 1)),
                       "bad": list(violations or []),
                       "farH": far_max_height, "lang": lang})
    hi = lang == "hi"
    L = {"road": "सड़क", "front": "सामने", "rear": "पीछे", "side": "बगल",
         "build": "भवन"} if hi else {"road": "ROAD", "front": "Front",
                                     "rear": "Rear", "side": "Side", "build": "BUILD"}
    lab = _json.dumps(L)
    return f"""
<div id="{uid}" style="width:100%;height:480px;border:1px solid #ccc;border-radius:10px;overflow:hidden"></div>
<div style="display:flex;gap:6px;flex-wrap:wrap;margin:6px 0">
<button onclick="window['{uid}_view']('3d')">🏠 3D</button>
<button onclick="window['{uid}_view']('top')">⬇️ Top</button>
<button onclick="window['{uid}_view']('front')">🧱 Front</button>
<button onclick="window['{uid}_rot']()">🔄 Auto-rotate</button>
<button onclick="window['{uid}_far']()">📦 FAR envelope</button>
<button onclick="window['{uid}_morph']()">⚖️ Required vs proposed</button>
</div>
<div id="{uid}_info" style="font-size:13px;background:#E8F5E9;border-radius:6px;padding:6px 10px;min-height:22px"></div>
{IMPORTMAP}
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
(function(){{
const cfg = {cfg}, L = {lab};
const el = document.getElementById('{uid}');
const info = document.getElementById('{uid}_info');
const W = el.clientWidth || 700, H = 480;
const renderer = new THREE.WebGLRenderer({{antialias:true}});
renderer.setSize(W,H); renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
el.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeaf2fb);
scene.fog = new THREE.Fog(0xeaf2fb, 90, 220);
const camera = new THREE.PerspectiveCamera(46, W/H, 0.1, 1000);
const ctl = new OrbitControls(camera, renderer.domElement);
ctl.enableDamping = true; ctl.dampingFactor = 0.08;
ctl.maxPolarAngle = Math.PI/2 - 0.03; ctl.minDistance = 12; ctl.maxDistance = 160;
scene.add(new THREE.HemisphereLight(0xffffff, 0x9db38a, 0.9));
const sun = new THREE.DirectionalLight(0xfff6e5, 1.6);
sun.position.set(30, 42, 22); sun.castShadow = true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-40; sun.shadow.camera.right=40;
sun.shadow.camera.top=40; sun.shadow.camera.bottom=-40;
scene.add(sun);
const S = 1.1;
const PW = cfg.plot_w*S, PD = cfg.plot_d*S;
function label(text, scale=1){{
  const c = document.createElement('canvas'); c.width=256; c.height=80;
  const g = c.getContext('2d');
  g.fillStyle='rgba(20,30,20,0.82)'; g.beginPath(); g.roundRect(4,4,248,72,14); g.fill();
  g.fillStyle='#fff'; g.font='bold 30px sans-serif'; g.textAlign='center'; g.textBaseline='middle';
  g.fillText(text,128,42);
  const t = new THREE.CanvasTexture(c);
  const m = new THREE.SpriteMaterial({{map:t, depthTest:false}});
  const sp = new THREE.Sprite(m); sp.scale.set(9*scale,2.8*scale,1); return sp;
}}
// ground + grid
const ground = new THREE.Mesh(new THREE.BoxGeometry(PW+26, 0.4, PD+30),
  new THREE.MeshStandardMaterial({{color:0xcfe0c3, roughness:1}}));
ground.position.y=-0.2; ground.receiveShadow = true; scene.add(ground);
const grid = new THREE.GridHelper(Math.max(PW,PD)+24, 24, 0x9db38a, 0xb9cba9);
grid.position.y = 0.02; scene.add(grid);
// road with dashes + footpath
const roadW = 5;
const road = new THREE.Mesh(new THREE.BoxGeometry(PW+26, 0.42, roadW),
  new THREE.MeshStandardMaterial({{color:0x4e5359, roughness:0.9}}));
road.position.set(0, 0.0, -PD/2-1-roadW/2); road.receiveShadow = true; scene.add(road);
for(let x=-(PW+26)/2+3; x<(PW+26)/2-2; x+=5){{
  const d = new THREE.Mesh(new THREE.BoxGeometry(2.2,0.05,0.28),
    new THREE.MeshBasicMaterial({{color:0xffee58}}));
  d.position.set(x, 0.24, -PD/2-1-roadW/2); scene.add(d);
}}
const rl = label(L.road); rl.position.set(0, 2.2, -PD/2-1-roadW/2); scene.add(rl);
// plot slab + compound wall
const slab = new THREE.Mesh(new THREE.BoxGeometry(PW, 0.5, PD),
  new THREE.MeshStandardMaterial({{color:0xe6eedb, roughness:1}}));
slab.position.y = 0.25; slab.receiveShadow = true; slab.castShadow = true; scene.add(slab);
const wallM = new THREE.MeshStandardMaterial({{color:0x8d6e63, roughness:0.9}});
[[0,-PD/2,PW+0.3,0.25],[0,PD/2,PW+0.3,0.25],[-PW/2,0,0.25,PD],[PW/2,0,0.25,PD]].forEach(w=>{{
  const m = new THREE.Mesh(new THREE.BoxGeometry(w[2],1.1,w[3]), wallM);
  m.position.set(w[0], 1.0, w[1]); m.castShadow = true; scene.add(m);
}});
// setback tint
const tint = new THREE.Mesh(new THREE.BoxGeometry(PW, 0.56, PD),
  new THREE.MeshStandardMaterial({{color:0xffcc80, transparent:true, opacity:0.35}}));
tint.position.y = 0.28; scene.add(tint);
// building footprint (required position)
const bw = Math.max(1.5, PW - 2*cfg.side*S), bd = Math.max(1.5, PD - (cfg.front+cfg.rear)*S);
const bz = (cfg.front-cfg.rear)*S/2;
const bad = (cfg.bad||[]).length > 0;
const bh = Math.max(1.2, cfg.height*S);
const bmat = new THREE.MeshStandardMaterial({{color: bad?0xc62828:0x2e7d32, roughness:0.55, metalness:0.08,
  emissive: bad?0x7f0000:0x000000, emissiveIntensity: bad?0.55:0}});
const bld = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, bd), bmat);
bld.position.set(0, 0.5+bh/2, bz); bld.castShadow = true; bld.receiveShadow = true; scene.add(bld);
// windows (sunset-lit grid on front + back faces)
const winM = new THREE.MeshBasicMaterial({{color:0xffe9a8}});
const cols = Math.max(2, Math.floor(bw/2.2)), rowsN = Math.max(1, Math.round(cfg.floors));
for(let f=0; f<rowsN; f++){{
  for(let c=0; c<cols; c++){{
    [1,-1].forEach(s=>{{
      const wmesh = new THREE.Mesh(new THREE.PlaneGeometry(0.9,0.9), winM);
      wmesh.position.set(-bw/2+1.1+c*(bw-2.2)/Math.max(1,cols-1), 1.6+f*(bh-2)/Math.max(1,rowsN-1), bz+s*(bd/2+0.03));
      if(s<0) wmesh.rotation.y = Math.PI;
      scene.add(wmesh);
    }});
  }}
}}
// parapet
const par = new THREE.Mesh(new THREE.BoxGeometry(bw+0.25, 0.5, bd+0.25),
  new THREE.MeshStandardMaterial({{color:0x1b5e20, roughness:0.8}}));
par.position.set(0, 0.5+bh+0.25, bz); par.castShadow = true; scene.add(par);
// floor lines
for(let i=1;i<cfg.floors;i++){{
  const y = 0.5 + bh*i/cfg.floors;
  const eg = new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(bw+0.06,0.07,bd+0.06)),
    new THREE.LineBasicMaterial({{color:0xffffff}}));
  eg.position.set(0, y, bz); scene.add(eg);
}}
// trees in setback (cone + trunk)
function tree(x,z,s=1){{
  const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.18*s,0.24*s,1.4*s),
    new THREE.MeshStandardMaterial({{color:0x6d4c41}}));
  tr.position.set(x,1.2*s,z); tr.castShadow=true; scene.add(tr);
  const cr = new THREE.Mesh(new THREE.ConeGeometry(1.0*s,2.4*s,8),
    new THREE.MeshStandardMaterial({{color:0x2e7d32, roughness:0.9}}));
  cr.position.set(x,2.6*s,z); cr.castShadow=true; scene.add(cr);
}}
tree(-PW/2+1.2, -PD/2+cfg.front*S/2); tree(PW/2-1.2, -PD/2+cfg.front*S/2);
tree(-PW/2+1.2, PD/2-1.2, 0.85); tree(PW/2-1.2, PD/2-1.2, 0.85);
// setback dimension labels
const fl = label(L.front+' '+cfg.front+'m'); fl.position.set(-PW/2-4.5, 1.6, -PD/2+cfg.front*S/2); scene.add(fl);
const rl2 = label(L.rear+' '+(cfg.rear||0)+'m'); rl2.position.set(PW/2+4.5, 1.6, PD/2-(cfg.rear||0)*S/2); scene.add(rl2);
const sl = label(L.side+' '+cfg.side+'m', 0.85); sl.position.set(-PW/2+cfg.side*S/2, 1.4, bz); scene.add(sl);
const bl = label(L.build+' '+cfg.height+'m/'+cfg.floors+'F'); bl.position.set(0, 0.5+bh+2.2, bz); scene.add(bl);
// FAR max envelope (wireframe), toggled
let env = null;
function toggleEnv(){{
  if(env){{ scene.remove(env); env=null; return; }}
  const eh = Math.max(bh, (cfg.farH||cfg.height*1.4)*S);
  env = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(PW*0.92, eh, PD*0.92)),
    new THREE.LineBasicMaterial({{color:0x1565c0}}));
  env.position.set(0, 0.5+eh/2, 0); scene.add(env);
  info.innerHTML = '📦 ' + (cfg.lang==='hi' ? 'अधिकतम FAR घेरा (नीला तार)' : 'Max FAR envelope (blue wire)');
}}
// required-vs-proposed morph (slide building to required gaps)
let morphed = false, baseX = 0;
function morph(){{
  morphed = !morphed;
  bld.position.x = morphed ? Math.min(2.5, PW*0.08) : baseX;
  bmat.color.set(morphed ? 0xef6c00 : (bad ? 0xc62828 : 0x2e7d32));
  info.innerHTML = morphed
    ? ('⚖️ ' + (cfg.lang==='hi' ? 'प्रस्तावित (नारंगी) बनाम आवश्यक स्थिति' : 'Proposed (orange) vs required footprint'))
    : ('⚖️ ' + (cfg.lang==='hi' ? 'आवश्यक स्थिति' : 'Required footprint'));
}}
// camera presets + autorotate
function setView(v){{
  const cx=0, cy=0.5+bh/2;
  if(v==='top') camera.position.set(cx, Math.max(PW,PD)*1.9, 0.01);
  else if(v==='front') camera.position.set(cx, cy+3, PD*1.5);
  else camera.position.set(PW*0.95, bh+13, PD*1.15);
  ctl.target.set(cx, cy, 0); ctl.update();
}}
window['{uid}_view'] = setView;
window['{uid}_rot'] = ()=>{{ ctl.autoRotate = !ctl.autoRotate; ctl.autoRotateSpeed = 1.2; }};
window['{uid}_far'] = toggleEnv;
window['{uid}_morph'] = morph;
setView('3d');
// click building -> info
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2();
renderer.domElement.addEventListener('pointerdown', e=>{{
  const r = renderer.domElement.getBoundingClientRect();
  ptr.x = ((e.clientX-r.left)/r.width)*2-1; ptr.y = -((e.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ptr, camera);
  if(ray.intersectObject(bld).length){{
    info.innerHTML = '🏢 ' + L.build + ': ' + cfg.height + 'm / ' + cfg.floors + 'F'
      + ' · ' + L.front + ' ' + cfg.front + 'm · ' + L.rear + ' ' + cfg.rear + 'm'
      + ((cfg.bad||[]).length ? ' · ❌ ' + cfg.bad.join(', ') : ' · ✅ OK');
  }}
}});
// violation pulse
let t0 = 0;
(function anim(t){{
  requestAnimationFrame(anim);
  if(bad){{ bmat.emissiveIntensity = 0.35 + 0.3*Math.abs(Math.sin(t*0.004)); }}
  ctl.update(); renderer.render(scene, camera);
}})(0);
}})();
</script>
<p style="font-size:12px;color:#666">🖱️ Drag = rotate · Wheel = zoom · Right-drag = pan · Click building = info · Offline? 2D diagram below.</p>
"""


BHOPAL_MAP_IFRAME = (
    '<iframe width="100%" height="380" frameborder="0" style="border:1px solid #ccc;border-radius:8px" '
    'src="https://www.openstreetmap.org/export/embed.html?bbox=77.30%2C23.15%2C77.55%2C23.35'
    '&layer=mapnik&marker=23.2599%2C77.4126"></iframe>'
    '<p style="font-size:12px;color:#666">📍 Bhopal — BMC HQ, ISBT (marker). T&CP Head Office: Paryavas Bhawan, Arera Hills. Real OpenStreetMap; needs internet.</p>'
)
