"""Rule-vs-proposal checker: citizen's proposed numbers checked against the code.
Returns list of {item, proposed, required, ok, rule} — drives 3D red/green + verdict."""

from calculators import front_open_space, rear_open_space, side_setback, far_limit


def check_proposal(plot_sqm=None, road_m=None, front_m=None, rear_m=None,
                   building="detached", frontage_m=None, height_m=None,
                   floors=None, use="residential", builtup_sqm=None, plot_for_far=None):
    out = []
    if road_m is not None and front_m is not None:
        req = front_open_space(road_m)
        out.append({"item": "Front open space", "proposed": front_m, "required": req,
                    "ok": front_m >= req - 1e-9, "rule": "56(1)"})
    if plot_sqm is not None and rear_m is not None:
        req = rear_open_space(plot_sqm)
        out.append({"item": "Rear open space", "proposed": rear_m, "required": req,
                    "ok": rear_m >= req - 1e-9, "rule": "56(2)"})
    if height_m is not None and height_m > 12.5:
        out.append({"item": "Height band", "proposed": f"{height_m} m",
                    "required": "Rule 42 Table 4/5 norms apply above 12.5 m",
                    "ok": None, "rule": "42"})
    if use and builtup_sqm and plot_for_far:
        lim = far_limit("residential" if "resi" in use.lower() or use == "residential" else use)
        if lim:
            got = builtup_sqm / plot_for_far
            out.append({"item": "FAR", "proposed": round(got, 2), "required": lim,
                        "ok": got <= lim + 1e-9, "rule": "61"})
    if floors is not None and floors > 10:
        out.append({"item": "High-rise", "proposed": f"{floors} storeys",
                    "required": ">10 storeys or >30 m = high-rise (site committee + fire NOC)",
                    "ok": None, "rule": "2(38)/12(2)"})
    return out


def verdict(checks):
    fails = [c for c in checks if c["ok"] is False]
    if not checks:
        return "neutral", "Enter proposed numbers to check."
    if not fails:
        return "pass", "✅ Proposal meets the checked rules."
    return "fail", f"❌ {len(fails)} violation(s): " + "; ".join(
        f"{c['item']} needs {c['required']} (Rule {c['rule']})" for c in fails)
