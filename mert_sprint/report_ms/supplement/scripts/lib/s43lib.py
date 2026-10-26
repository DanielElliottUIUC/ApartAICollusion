"""Loaders, style, statistics and checks for the S4.3 supplement figures (frontier sellers and other families).

Style constants are copied from report_ms/scripts/lib/style.py (2026-10-25), so these figures keep their look
if the report's style file is edited. Every input is read from report_ms/supplement/data/s43/, which
scripts/S43/build_s43_data.py writes from experiments/runs/.

  runs()            one row per auction run (data/s43/s43_runs.csv)
  seller_asks()     one row per run, hour and seller (data/s43/s43_seller_asks.csv)
  bertrand()        one row per Bertrand run (data/s43/s43_bertrand.csv)
  audit(fig)        font floors, text inside the image, no two text boxes overlapping
  save(fig, name)   checks the width, runs the audit and writes figures/S43/<name> at 300 dpi
Outputs go only to report_ms/supplement/{figures,data}/S43 (data: s43) and report_ms/supplement/sections/S43.md.
"""
import itertools
import math
from pathlib import Path

import matplotlib as mpl
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, spearmanr

try:                                    # captions use the minus sign; the Windows console default is cp1252
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

LIB = Path(__file__).resolve().parent
SUP = LIB.parents[1]                       # report_ms/supplement/
MS = SUP.parent                            # report_ms/
REPO = MS.parent                           # apart-collusion-sprint-2026/
RUNS = REPO / "experiments" / "runs"
FIG_DIR = SUP / "figures" / "S43"
DATA_DIR = SUP / "data" / "s43"
HOURS = list(range(1, 16))
ASK_COLS = [f"ask_h{h}" for h in HOURS]
LAST_THIRD = [11, 12, 13, 14, 15]

# ---------------------------------------------------------------- style (copied from report_ms style.py)
SLOT_IN = 6.5
DPI = 300
COLOR = {"gemini": "#0072B2", "sol": "#D55E00", "luna": "#009E73", "grok": "#CC79A7",
         "gpt41": "#E69F00", "haiku": "#56B4E9"}
NAME = {"gemini": "Gemini 3.8 Flash", "sol": "GPT-5.6 Sol", "luna": "GPT-6 Luna", "grok": "Grok 4.7",
        "gpt41": "GPT-4.1", "haiku": "Claude Haiku 5.5"}
SHORT = {"gemini": "Gemini", "sol": "Sol", "luna": "Luna", "grok": "Grok", "haiku": "Haiku"}
BUYER_NAME = {"haiku": "Claude Haiku 5.5", "luna": "GPT-6 Luna", "gpt41mini": "GPT-4.1-mini"}
BUYER_SHORT = {"haiku": "Haiku", "luna": "Luna", "gpt41mini": "GPT-4.1-mini"}
GRAY = "#555555"
LIGHT = "#BBBBBB"
WINDOW = "#F2F2F2"         # pale band behind hours 11 to 15, the last third the criterion reads
REF_LINES = [
    {"price": 90.0, "index": 0.0, "ls": (0, (5, 3)), "lw": 1.2},
    {"price": 95.0, "index": 0.5, "ls": (0, (1, 2)), "lw": 1.6},
    {"price": 97.5, "index": 0.75, "ls": "-", "lw": 0.7},
]
MSG_LS = {"on": "-", "off": (0, (7, 2.5, 1.5, 2.5))}

MODEL_KEY = {"gpt-5.6-sol": "sol", "gpt-6-luna": "luna", "grok-4.7": "grok",
             "anthropic/claude-haiku-5.5": "haiku", "google/gemini-3.8-flash": "gemini",
             "openai/gpt-4.1-mini": "gpt41mini"}


def setup():
    mpl.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12, "axes.labelsize": 14, "axes.titlesize": 16,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "legend.fontsize": 12, "legend.title_fontsize": 12,
        "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.9,
        "xtick.major.width": 0.9, "ytick.major.width": 0.9, "savefig.dpi": DPI, "figure.dpi": 100,
        "text.parse_math": False,
    })


def ref_lines(ax, unit="price", which=(90.0, 95.0, 97.5), **kw):
    """Reference lines: $90 dashed, $95 (index 0.5) dotted, $97.50 (index 0.75) thin solid."""
    for r in REF_LINES:
        if r["price"] in which:
            ax.axhline(r[unit], color=GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5, **kw)


def window(ax, **kw):
    """Pale band over hours 11 to 15 (x in hours)."""
    ax.axvspan(10.5, 15.5, color=WINDOW, lw=0, zorder=0.1, **kw)


def panel_letter(ax, letter, x=-0.02, y=1.02):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=16, fontweight="bold", ha="right", va="bottom")


def tint(hex_color, amount=0.55):
    """Blend a color with white; amount 0 gives the color, 1 gives white."""
    r, g, b = mpl.colors.to_rgb(hex_color)
    return (r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount)


def shade(hex_color, amount=0.35):
    """Blend a color with black; amount 0 gives the color."""
    r, g, b = mpl.colors.to_rgb(hex_color)
    return (r * (1 - amount), g * (1 - amount), b * (1 - amount))


# ---------------------------------------------------------------- text formatting for captions
def num(x, nd=2):
    """A number for prose, with a true minus sign."""
    s = f"{x:.{nd}f}"
    return s.replace("-", "−")


def usd(x, nd=2):
    return "$" + num(x, nd) if x >= 0 else "−$" + f"{-x:.{nd}f}"


def pval(p):
    if p < 0.001:
        mant, exp = f"{p:.1e}".split("e")
        return f"{mant} x 10^{int(exp)}"
    if p < 0.01:
        return f"{p:.4f}"
    return f"{p:.2f}" if p >= 0.1 else f"{p:.3f}"


def kofn(k, n):
    return f"{k} of {n}"


# ---------------------------------------------------------------- loaders
def runs():
    df = pd.read_csv(DATA_DIR / "s43_runs.csv")
    df["passed"] = df["passed"].astype(bool)
    return df


def seller_asks():
    return pd.read_csv(DATA_DIR / "s43_seller_asks.csv")


def bertrand():
    df = pd.read_csv(DATA_DIR / "s43_bertrand.csv")
    return df


def frontier36(df=None):
    df = runs() if df is None else df
    f = df[df["phase"] == "frontier"]
    if len(f) != 36:
        raise ValueError(f"expected 36 frontier runs, found {len(f)}")
    return f


# ---------------------------------------------------------------- statistics
def fisher(k1, n1, k2, n2):
    return fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative="two-sided")[1]


def spearman_exact(x, y):
    """Spearman rho and the exact two-sided permutation p over all orderings of y (n <= 8)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    rho = spearmanr(x, y).correlation
    perms = list(itertools.permutations(range(len(y))))
    null = np.array([spearmanr(x, y[list(p)]).correlation for p in perms])
    p = float(np.mean(np.abs(null) >= abs(rho) - 1e-12))
    return float(rho), p, int(round(p * len(perms))), len(perms)


# ---------------------------------------------------------------- figure checks
def _text_artists(fig):
    out = []
    for t in fig.findobj(mpl.text.Text):
        if not t.get_visible() or not t.get_text().strip():
            continue
        out.append(t)
    return out


def audit(fig, allow_overlap=()):
    """Raise if any text is under its floor, leaves the image, or overlaps another text box.
    Floors: axis labels 14 pt, tick labels 12 pt, titles 16 pt, every other text 12 pt.
    allow_overlap: pairs of strings (substrings of the two texts) whose overlap is intended."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    W, H = fig.bbox.width, fig.bbox.height
    problems = []
    axis_labels, titles, ticks = set(), set(), set()
    for ax in fig.axes:
        axis_labels.update([id(ax.xaxis.label), id(ax.yaxis.label)])
        titles.update([id(ax.title), id(ax._left_title), id(ax._right_title)])
        for tk in ax.get_xticklabels() + ax.get_yticklabels():
            ticks.add(id(tk))
    if fig._suptitle is not None:
        titles.add(id(fig._suptitle))
    for lab in (getattr(fig, "_supxlabel", None), getattr(fig, "_supylabel", None)):
        if lab is not None:
            axis_labels.add(id(lab))
    texts = _text_artists(fig)
    boxes = []
    for t in texts:
        size = t.get_fontsize()
        floor = 14 if id(t) in axis_labels else 16 if id(t) in titles else 12
        if size < floor - 1e-6:
            problems.append(f"font {size} < {floor}: {t.get_text()[:40]!r}")
        bb = mpl.text.Text.get_window_extent(t, rend)     # the text alone, without an annotation's arrow
        if bb.x0 < -0.5 or bb.y0 < -0.5 or bb.x1 > W + 0.5 or bb.y1 > H + 0.5:
            problems.append(f"outside image: {t.get_text()[:40]!r} {bb}")
        boxes.append((t, bb))
    for (t1, b1), (t2, b2) in itertools.combinations(boxes, 2):
        if b1.overlaps(b2):
            ix = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
            iy = min(b1.y1, b2.y1) - max(b1.y0, b2.y0)
            if ix <= 1 or iy <= 1:
                continue
            s1, s2 = t1.get_text(), t2.get_text()
            if any((a in s1 and b in s2) or (a in s2 and b in s1) for a, b in allow_overlap):
                continue
            problems.append(f"overlap: {s1[:30]!r} / {s2[:30]!r}")
    if problems:
        raise ValueError("audit failed:\n  " + "\n  ".join(problems))


def save(fig, name, allow_overlap=()):
    w, h = fig.get_size_inches()
    if abs(w - SLOT_IN) > 1e-6:
        raise ValueError(f"{name}: width {w} in, slot is {SLOT_IN} in")
    try:
        audit(fig, allow_overlap)
    except ValueError:
        import os
        draft = os.environ.get("S43_DRAFT_DIR")      # optional: keep the failing render for inspection
        if draft:
            fig.savefig(Path(draft) / name, dpi=DPI)
        raise
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = FIG_DIR / name
    fig.savefig(path, dpi=DPI)
    print(f"wrote {path} ({w:.2f} x {h:.2f} in)")
    return path


def rel(path):
    """A repository-relative path for Source lines."""
    return Path(path).resolve().relative_to(REPO).as_posix()


def check_close(a, b, what, tol=1e-9):
    if not (math.isclose(a, b, abs_tol=tol)):
        raise ValueError(f"{what}: {a} != {b}")
