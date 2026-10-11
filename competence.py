"""Who may prepare/submit plans — Rule 26(9) competence table (PDF p.45-46).
Deterministic: plot size + storeys/height + use -> who is competent.
Note: per Association of Civil Engineers Vs State of MP (2014 MPLJ 193),
Engineers claim Architect-level scope; tool reports the rule text, clerk decides."""

# (role, max_plot_sqm, max_storeys, max_height_m, scope note)
COMPETENCE = [
    ("Architect", float("inf"), float("inf"), float("inf"),
     "all buildings irrespective of size/height + development up to 4 ha"),
    ("Structural Engineer", 500, 3, 11,
     "residential plans up to 500 sqm / 3 storeys / 11 m; structural details for all"),
    ("Engineer", 300, 2, 7.5,
     "residential plans up to 300 sqm / 2 storeys / 7.5 m"),
    ("Supervisor", 200, 2, 7.5,
     "residential plans up to 200 sqm / 2 storeys / 7.5 m"),
]


def competent_who(plot_sqm: float | None = None, storeys: int | None = None,
                  height_m: float | None = None, residential: bool = True):
    """Return list of competent roles for the given job. Architect always competent."""
    ok = []
    for role, sqm, st, ht, _note in COMPETENCE:
        if role == "Architect":
            ok.append(role)
            continue
        if not residential:
            continue  # table limits below are residential; others need Architect/SE
        if ((plot_sqm is None or plot_sqm <= sqm)
                and (storeys is None or storeys <= st)
                and (height_m is None or height_m <= ht)):
            ok.append(role)
    return ok


ROLE_HI = {
    "Architect": "आर्किटेक्ट",
    "Structural Engineer": "स्ट्रक्चरल इंजीनियर",
    "Engineer": "इंजीनियर",
    "Supervisor": "सुपरवाइजर",
}
