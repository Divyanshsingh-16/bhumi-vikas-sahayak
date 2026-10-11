"""Rule-flow visualizer: 12 -> 14 -> 21 -> 23 -> 31 chain as SVG decision graph."""

NODES = [
    ("12", "Permission\nneeded?", "#1B5E20"),
    ("14", "Apply\nA-1 / A-2", "#2E7D32"),
    ("21", "Pay fee\nslabs", "#EF6C00"),
    ("23", "Valid 3yr\n+2x1 renewal", "#1565C0"),
    ("31", "Occupy\n(E-4, 30d)", "#6A1B9A"),
]


def flow_svg(lang="en", highlight=None) -> str:
    W, H = 640, 150
    n = len(NODES)
    step = W / n
    parts = [f'<svg width="{W}" height="{H}" style="max-width:100%;background:#FAFAFA;border:1px solid #E0E0E0;border-radius:10px">']
    for i, (rule, label, color) in enumerate(NODES):
        x = step * i + step / 2
        hl = " stroke-width=\"4\"" if rule == highlight else ""
        parts.append(f'<line x1="{x+34}" y1="60" x2="{x+step-34}" y2="60" stroke="#9E9E9E" stroke-width="2" marker-end="url(#ah)"/>'
                     if i < n - 1 else "")
        parts.append(f'<circle cx="{x}" cy="60" r="30" fill="{color}" opacity="0.92"{hl}/>'
                     f'<text x="{x}" y="56" fill="white" font-size="15" font-weight="bold" text-anchor="middle">R{rule}</text>'
                     f'<text x="{x}" y="72" fill="white" font-size="9" text-anchor="middle">Rule</text>')
        for j, ln in enumerate(label.split("\n")):
            parts.append(f'<text x="{x}" y="{108+j*14}" font-size="12" text-anchor="middle" fill="#333">{ln}</text>')
    parts.append('<defs><marker id="ah" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">'
                 '<path d="M0,0 L8,4 L0,8" fill="none" stroke="#9E9E9E" stroke-width="2"/></marker></defs></svg>')
    return "".join(parts)
