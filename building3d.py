"""Three.js 3D plot+building viewer (CDN) with 2D-SVG offline fallback.
Shows: ground plot, setback margins (green), building block (green/red),
floor lines, road strip. Orbit with mouse."""

THREE_CDN = "https://unpkg.com/three@0.152.2/build/three.min.js"


def building_3d_html(plot_w=12.0, plot_d=20.0, front=3.0, rear=1.5, side=1.5,
                      height=9.0, floors=3, violations=(), lang="en"):
    import json as _json
    cfg = _json.dumps({"plot_w": plot_w, "plot_d": plot_d, "front": front, "rear": rear,
                       "side": side, "height": height, "floors": max(1, int(floors or 1)),
                       "bad": list(violations or [])})
    return f"""
<div id="b3d" style="width:100%;height:420px;border:1px solid #ccc;border-radius:8px"></div>
<script src="{THREE_CDN}"></script>
<script>
(function(){{
const cfg = {cfg};
const el = document.getElementById('b3d');
if(!window.THREE){{ el.innerHTML = '<p style="padding:20px">3D needs internet (three.js CDN). Offline: see 2D diagram.</p>'; return; }}
const W = el.clientWidth || 600, H = 420;
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xf7f9fc);
const cam = new THREE.PerspectiveCamera(45, W/H, 0.1, 1000);
const ren = new THREE.WebGLRenderer({{antialias:true}}); ren.setSize(W,H); el.appendChild(ren.domElement);
scene.add(new THREE.AmbientLight(0xffffff, 0.75));
const sun = new THREE.DirectionalLight(0xffffff, 0.8); sun.position.set(20,30,15); scene.add(sun);
const S = 1.2; // scale
const PW = cfg.plot_w*S, PD = cfg.plot_d*S;
// ground plot
const ground = new THREE.Mesh(new THREE.BoxGeometry(PW, 0.3, PD),
  new THREE.MeshLambertMaterial({{color:0xdfe8d5}}));
scene.add(ground);
// road strip (front = -z edge)
const road = new THREE.Mesh(new THREE.BoxGeometry(PW, 0.32, 4),
  new THREE.MeshLambertMaterial({{color:0x555555}}));
road.position.set(0, 0.01, -PD/2-2); scene.add(road);
// setback zone (translucent)
const bw = PW - 2*cfg.side*S, bd = PD - (cfg.front+cfg.rear)*S;
const margin = new THREE.Mesh(new THREE.BoxGeometry(PW, 0.5, PD),
  new THREE.MeshLambertMaterial({{color:0xffe0b2, transparent:true, opacity:0.55}}));
margin.position.y = 0.15; scene.add(margin);
// building block
const bad = (cfg.bad||[]).length > 0;
const bh = Math.max(1, cfg.height*S);
const bmat = new THREE.MeshLambertMaterial({{color: bad ? 0xe57373 : 0x81c784}});
const bld = new THREE.Mesh(new THREE.BoxGeometry(Math.max(1,bw), bh, Math.max(1,bd)), bmat);
bld.position.set(0, bh/2+0.3, (cfg.front-cfg.rear)*S/2 + 0.3); scene.add(bld);
// floor lines
for(let i=1;i<cfg.floors;i++){{
  const y = 0.3 + bh*i/cfg.floors;
  const eg = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(Math.max(1,bw)+0.05, 0.06, Math.max(1,bd)+0.05)),
    new THREE.LineBasicMaterial({{color:0x2e7d32}}));
  eg.position.set(0, y, (cfg.front-cfg.rear)*S/2 + 0.3); scene.add(eg);
}}
// edges outline
scene.add(new THREE.BoxHelper(bld, 0x333333));
const cx = 0, cy = bh/2;
cam.position.set(PW*0.9, bh+14, PD*1.1); cam.lookAt(cx, cy, 0);
// simple orbit
let ax = 0.7, dragging = false, px = 0;
el.addEventListener('pointerdown', e=>{{dragging=true; px=e.clientX;}});
window.addEventListener('pointerup', ()=>dragging=false);
window.addEventListener('pointermove', e=>{{
  if(!dragging) return; ax += (e.clientX-px)*0.01; px=e.clientX;
  const r = Math.sqrt(cam.position.x**2 + cam.position.z**2);
  cam.position.x = r*Math.sin(ax); cam.position.z = r*Math.cos(ax); cam.lookAt(cx,cy,0);
}});
(function anim(){{ requestAnimationFrame(anim); ren.render(scene, cam); }})();
}})();
</script>
<p style="font-size:12px;color:#666">🖱️ Drag to rotate · Green = OK, Red = violation · Offline? 2D diagram below.</p>
"""


BHOPAL_MAP_IFRAME = (
    '<iframe width="100%" height="380" frameborder="0" style="border:1px solid #ccc;border-radius:8px" '
    'src="https://www.openstreetmap.org/export/embed.html?bbox=77.30%2C23.15%2C77.55%2C23.35'
    '&layer=mapnik&marker=23.2599%2C77.4126"></iframe>'
    '<p style="font-size:12px;color:#666">📍 Bhopal — BMC HQ (marker). Real OpenStreetMap; needs internet.</p>'
)
