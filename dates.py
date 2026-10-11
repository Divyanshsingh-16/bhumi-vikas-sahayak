"""Deadline math: application/validity/deemed dates. Deterministic date arithmetic.
Rules: 23 (3yr + 2x1yr), 28 (Sec 30(5) deemed), 31 (occupancy 30d), 33 (inspect 7d/21d)."""
from datetime import date, timedelta


def add_years(d: date, y: int) -> date:
    try:
        return d.replace(year=d.year + y)
    except ValueError:  # Feb 29
        return d.replace(year=d.year + y, day=28)


def permission_timeline(applied: date, validity_years: int = 3):
    """Development permission lifecycle from application date (approx; Act periods govern)."""
    return {
        "applied": applied.isoformat(),
        "valid_until": add_years(applied, validity_years).isoformat(),
        "renewal_1_until": add_years(applied, validity_years + 1).isoformat(),
        "renewal_2_until": add_years(applied, validity_years + 2).isoformat(),
        "note": "Renewal 2x1yr, then fresh proposal; execution begun = no lapse (Rule 23).",
    }


def occupancy_deadline(applied: date) -> str:
    return (applied + timedelta(days=30)).isoformat()


def inspection_windows(notice: date):
    return {"plinth_inspect_by": (notice + timedelta(days=7)).isoformat(),
            "final_inspect_by": (notice + timedelta(days=21)).isoformat()}
