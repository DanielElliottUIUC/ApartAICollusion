"""Shared helpers for the print-size figures: locate Mert's original scripts, verify size and text, save png+pdf."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORT_MS = HERE.parent / "report_ms"           # mert_sprint/report_ms (public) or report_ms (private repo)
sys.dont_write_bytecode = True                  # never write into report_ms/
for p in (REPORT_MS / "scripts" / "lib", REPORT_MS / "scripts" / "figures",
          REPORT_MS / "supplement" / "scripts" / "lib", REPORT_MS / "supplement" / "scripts" / "S3"):
    sys.path.insert(0, str(p))

WIDTH_IN = 6.5
DPI = 300


def text_sizes(fig):
    import matplotlib.text as mtext
    drawn = []
    orig = mtext.Text.draw

    def spy(self, renderer):
        if self.get_visible() and self.get_text().strip():
            drawn.append(self)
        return orig(self, renderer)

    mtext.Text.draw = spy
    try:
        fig.canvas.draw()
    finally:
        mtext.Text.draw = orig
    return sorted({round(t.get_fontsize(), 2) for t in drawn}), drawn


def save(fig, stem, min_pt=8.0):
    w, h = fig.get_size_inches()
    if abs(w - WIDTH_IN) > 1e-6:
        raise ValueError(f"{stem}: width {w} in, must be {WIDTH_IN} in")
    sizes, drawn = text_sizes(fig)
    if min(sizes) < min_pt:
        raise ValueError(f"{stem}: text below {min_pt} pt: {sizes}")
    W, H = fig.bbox.width, fig.bbox.height
    r = fig.canvas.get_renderer()
    for t in drawn:
        bb = t.get_window_extent(r)
        if bb.x0 < -0.5 or bb.y0 < -0.5 or bb.x1 > W + 0.5 or bb.y1 > H + 0.5:
            raise ValueError(f"{stem}: text outside the figure: {t.get_text()!r}")
    for ext in ("png", "pdf"):
        fig.savefig(HERE / f"{stem}.{ext}", dpi=DPI)    # no bbox_inches: the page stays exactly 6.5 in wide
    print(f"{stem}: {w:.2f} x {h:.2f} in, font sizes used (pt): {sizes}")
