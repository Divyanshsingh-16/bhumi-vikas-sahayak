"""SVG top-view plot diagram: road on top, front/rear/side gaps shaded."""


def plot_svg(plot_w: float = 10, plot_d: float = 20, front: float = 3.0,
             rear: float = 1.5, side: float = 1.5, lang: str = "en") -> str:
    W, H = 300, 360
    mx, my = 20, 50
    pw, ph = W - 2 * mx, H - my - 20
    sx, sy = pw / plot_w, ph / plot_d
    fx, rx, sxd = front * sy, rear * sy, side * sx
    labels = {
        "road": "सड़क" if lang == "hi" else "ROAD",
        "front": f"{'सामने' if lang == 'hi' else 'Front'} {front}m",
        "rear": f"{'पीछे' if lang == 'hi' else 'Rear'} {rear}m",
        "build": "भवन" if lang == "hi" else "BUILD",
    }
    return f"""<svg width="{W}" height="{H}" style="border:1px solid #ccc;background:#fafafa">
<rect x="0" y="0" width="{W}" height="34" fill="#555"/>
<text x="{W/2}" y="22" fill="white" font-size="13" text-anchor="middle">{labels['road']}</text>
<rect x="{mx}" y="{my}" width="{pw}" height="{ph}" fill="#e8f5e9" stroke="#333"/>
<rect x="{mx}" y="{my}" width="{pw}" height="{fx}" fill="#fff3e0" opacity="0.9"/>
<rect x="{mx}" y="{my+ph-rx}" width="{pw}" height="{rx}" fill="#fff3e0" opacity="0.9"/>
<rect x="{mx}" y="{my+fx}" width="{sxd}" height="{ph-fx-rx}" fill="#fff3e0" opacity="0.9"/>
<rect x="{mx+pw-sxd}" y="{my+fx}" width="{sxd}" height="{ph-fx-rx}" fill="#fff3e0" opacity="0.9"/>
<rect x="{mx+sxd}" y="{my+fx}" width="{pw-2*sxd}" height="{ph-fx-rx}" fill="#c8e6c9" stroke="#2e7d32" stroke-width="2"/>
<text x="{W/2}" y="{my+fx/2+4}" font-size="11" text-anchor="middle">{labels['front']}</text>
<text x="{W/2}" y="{my+ph-rx/2+4}" font-size="11" text-anchor="middle">{labels['rear']}</text>
<text x="{W/2}" y="{my+fx+(ph-fx-rx)/2+4}" font-size="12" text-anchor="middle" font-weight="bold">{labels['build']}</text>
</svg>"""
