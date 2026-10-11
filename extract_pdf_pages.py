"""Extract key PDF pages as images for in-app evidence viewer. Needs pymupdf.
Source PDF lives in the track pack (not redistributed); images go to pdf_pages/ (gitignored)."""
from pathlib import Path

KEY_PAGES = [36, 37, 69, 70, 77, 78, 79, 80]  # fee, electric, residential (1-indexed PDF pages)

CANDIDATES = [
    Path("/Users/divyansh/Tracks/bhopal-impact-lab-2026/tracks/01-bhumi-vikas-sahayak/resources/MP_Bhumi_Vikas_Rules_2012_upto_2025-03-06_EN.pdf"),
]
OUT = Path(__file__).parent / "pdf_pages"

def main():
    try:
        import fitz
    except ImportError:
        print("pymupdf not installed; skip (pip install pymupdf)")
        return
    src = next((p for p in CANDIDATES if p.exists()), None)
    if not src:
        print("source PDF not found; skip")
        return
    OUT.mkdir(exist_ok=True)
    doc = fitz.open(src)
    for p in KEY_PAGES:
        pix = doc[p - 1].get_pixmap(dpi=110)
        pix.save(OUT / f"p{p}.png")
    print(f"wrote {len(KEY_PAGES)} images -> {OUT}")

if __name__ == "__main__":
    main()
