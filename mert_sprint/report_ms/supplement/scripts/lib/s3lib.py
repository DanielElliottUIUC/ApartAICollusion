"""Shared paths, run parsing and figure checks for the S3 (Setup and design) figures of the supplement.

Colors, reference lines and font sizes come from the main report's style module, which is imported
read-only from report_ms/scripts/lib/style.py, so the supplement stays consistent with the report.

Inputs:
  experiments/runs/...                      our run folders (never experiments/invalid_429_shard3/)
  report_ms/supplement/data/daniel/...      copies of D.E.'s CSVs (ApartAICollusion origin/main, see SOURCE_COMMIT.txt)
  report_ms/supplement/data/S3/...          tables written by scripts/S3/build_s3_data.py
Outputs:
  report_ms/supplement/figures/S3/S3_<nn>_<short>.png, 300 dpi, 6.5 in wide
"""
import ast
import json
import re
import sys
from pathlib import Path

SUPP = Path(__file__).resolve().parents[2]            # report_ms/supplement/
REPORT_MS = SUPP.parent                               # report_ms/
REPO = REPORT_MS.parent                               # repository root
RUNS = REPO / "experiments" / "runs"
DANIEL = SUPP / "data" / "daniel"
S3DATA = SUPP / "data" / "S3"
FIGDIR = SUPP / "figures" / "S3"

sys.path.insert(0, str(REPORT_MS / "scripts" / "lib"))
import style  # noqa: E402  (the report's style module, read-only)

SLOT_IN = style.SLOT_IN
DPI = style.DPI
COLOR = style.COLOR
NAME = style.NAME
GRAY = style.GRAY
LIGHT = style.LIGHT

SELLER_KEY = {"gpt-5.6-sol": "sol", "gpt-6-luna": "luna", "grok-4.7": "grok",
              "google/gemini-3.8-flash": "gemini", "anthropic/claude-haiku-5.5": "haiku"}
BUYER_KEY = {"anthropic/claude-haiku-5.5": "haiku", "gpt-6-luna": "luna", "openai/gpt-4.1-mini": "gpt41mini"}
BUYER_NAME = {"haiku": "Claude Haiku 5.5", "luna": "GPT-6 Luna", "gpt41mini": "GPT-4.1-mini"}

# Every folder group of ours that the S3 figures read, with a short block name.
# step_AB are M.S.'s reruns of D.E.'s step A and B designs (Haiku buyers); the report uses the Haiku-seller
# ones in Table B1 and the Gemini ones for the Grok-judge comparison in section 4.3.
RUN_GROUPS = [
    ("box/frontier", "frontier"),
    ("shard2/frontier", "frontier"),
    ("shard2/frontier_b41", "frontier_b41"),
    ("shard2/frontier_lowanchor", "frontier_lowanchor"),
    ("shard2/A_lowanchor", "A_lowanchor"),
    ("shard2/A_agycontrol", "A_agycontrol"),
    ("shard2/prereg_anchor", "prereg_anchor"),
    ("shard2/A", "step_AB"),
    ("shard2/B", "step_AB"),
    ("shard3/A", "step_AB"),
    ("shard3/B", "step_AB"),
]
# The one run whose unified.log and collusion_metrics.json stop after hour 1 (notes/strategy_oct25/01_our_results.md,
# section 5.1). Its seller files hold 15 hours, but no per-hour market data exists, so S3 figures that need hours
# or the joint criterion leave it out and say so.
BROKEN_LOG = "shard3/B/20261024_224207_danielB_GGGG-seed0"


def read_config(log_text):
    start = log_text.index("Auction configured with:") + len("Auction configured with:")
    obj, _ = json.JSONDecoder().raw_decode(log_text[start:].lstrip())
    return obj


def read_rounds(log_text):
    return [json.loads(line.split("completed with result: ", 1)[1])
            for line in log_text.splitlines() if "completed with result: " in line]


def seeded_book(folder):
    """The opening order book the harness seeded, read from the Hour 1 prompt of every seller file.
    Returns (asks {seller: price}, bids {buyer: price}); raises if the seller files disagree."""
    books = set()
    for f in sorted(folder.glob("Seller *.md")):
        t = f.read_text(encoding="utf-8")
        seg = t[t.index("This is Hour #1."):][:2000]
        bids = re.search(r"## Current Status of Bid Queue\s*\n\s*(\[.*?\])\s*\n", seg).group(1)
        asks = re.search(r"## Current Status of Ask Queue\s*\n\s*(\[.*?\])\s*\n", seg).group(1)
        books.add((asks, bids))
    if len(books) != 1:
        raise ValueError(f"{folder}: seller files show different opening books")
    asks, bids = books.pop()
    return ({name: p for p, name in ast.literal_eval(asks)}, {name: p for p, name in ast.literal_eval(bids)})


def run_folders():
    """(relative folder, block) for every run folder S3 reads, sorted."""
    out = []
    for sub, block in RUN_GROUPS:
        for d in sorted((RUNS / sub).iterdir()):
            if d.is_dir():
                out.append((d.relative_to(RUNS).as_posix(), block))
    if any("invalid_429" in f for f, _ in out):
        raise ValueError("invalid runs must never be read")
    return out


# ----------------------------------------------------------------------------------------------- figure helpers

def setup():
    style.setup()


def ref_lines(ax, unit="price", which=(90.0, 95.0, 97.5), **kw):
    for r in style.REF_LINES:
        if r["price"] in which:
            ax.axhline(r[unit], color=GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5, **kw)


def ref_vlines(ax, unit="index", which=(90.0, 95.0), **kw):
    for r in style.REF_LINES:
        if r["price"] in which:
            ax.axvline(r[unit], color=GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5, **kw)


def panel_letter(ax, letter, x=-0.02, y=1.02, ha_left=False, **kw):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=16, fontweight="bold",
            ha="left" if ha_left else "right", va="bottom", **kw)


def tint(c, amount=0.55):
    return style.tint(c, amount)


def check_text(fig, min_pt=12.0, allow_overlap=()):
    """Refuse text below min_pt or outside the figure, and report overlapping text boxes.
    allow_overlap: substrings of texts that may touch others (none by default)."""
    import matplotlib.text as mtext
    drawn = []
    orig = mtext.Text.draw

    def spy(self, renderer):          # record only the text artists matplotlib actually draws
        if self.get_visible() and self.get_text().strip():
            drawn.append(self)
        return orig(self, renderer)

    mtext.Text.draw = spy
    try:
        fig.canvas.draw()
    finally:
        mtext.Text.draw = orig
    r = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    boxes = []
    for t in drawn:
        s = t.get_text()
        if t.get_fontsize() < min_pt - 1e-6:
            raise ValueError(f"text below {min_pt} pt: {s!r} at {t.get_fontsize()} pt")
        bb = t.get_window_extent(r)
        if bb.x0 < -0.5 or bb.y0 < -0.5 or bb.x1 > W + 0.5 or bb.y1 > H + 0.5:
            raise ValueError(f"text outside the figure: {s!r} {bb}")
        boxes.append((s, bb))
    clashes = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i][1], boxes[j][1]
            if a.x0 < b.x1 - 1 and b.x0 < a.x1 - 1 and a.y0 < b.y1 - 1 and b.y0 < a.y1 - 1:
                if not any(k in boxes[i][0] or k in boxes[j][0] for k in allow_overlap):
                    clashes.append((boxes[i][0], boxes[j][0]))
    if clashes:
        raise ValueError("overlapping text: " + "; ".join(f"{a!r} / {b!r}" for a, b in clashes[:8]))


def save(fig, name, **check_kw):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    w, h = fig.get_size_inches()
    if abs(w - SLOT_IN) > 1e-6:
        raise ValueError(f"{name}: width {w} in, slot is {SLOT_IN} in")
    check_text(fig, **check_kw)
    path = FIGDIR / name
    fig.savefig(path, dpi=DPI)
    print(f"wrote {path.relative_to(REPO).as_posix()} ({w:.2f} x {h:.2f} in)")
    return path


def fmt_p(p):
    return f"{p:.2g}" if p < 0.01 else f"{p:.2f}"
