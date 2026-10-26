"""Shared style for the body figures adapted from M.S.'s report figures.

Adapted from M.S.'s mert_sprint/report_ms/scripts/lib/style.py (ref origin/mert_sprint_sync_oct25), by M.S.;
the colors, reference lines, arm order and row helpers are his. Changes for print: every figure is drawn at its
printed size (6.5 in wide) with fonts of 8 to 10 pt (his were 12 to 16 pt at a 6.5 in slot that the report printed
at about 3 in), and `save` goes through scripts/figures/printcheck.py, which refuses text under 8 pt, text outside
the figure or overlapping text.
"""
import sys
from pathlib import Path

import matplotlib as mpl

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import printcheck  # noqa: E402

SLOT_IN = printcheck.TEXT_WIDTH_IN      # full text width, inches
DPI = printcheck.DPI
REPO = Path(__file__).resolve().parents[3]
FIGURES = REPO / "report" / "figures"

# Print sizes, points
FS = 8.5          # body text, tick labels, bar labels
FS_HEAD = 9       # column headers
FS_TITLE = 10     # panel titles and letters

COLOR = {
    "gemini": "#0072B2",   # Gemini 3.8 Flash
    "sol": "#D55E00",      # GPT-5.6 Sol
    "luna": "#009E73",     # GPT-6 Luna
    "grok": "#CC79A7",     # Grok 4.7
    "gpt41": "#E69F00",    # GPT-4.1
    "haiku": "#56B4E9",    # Claude Haiku 5.5
}
GRAY = "#555555"
LIGHT = "#BBBBBB"
BASE_BAND, BASE_BAND_ALPHA = "#B2B2B2", 0.28

# Arms whose seller prompt carries the warning: a pale band behind their rows, dark text for their group label.
WARN_BAND = "#FBF3C4"
WARN_INK = "#7A6400"

# $90 competitive (index 0): dashed. $95 (index 0.5, the ask condition of the criterion): dotted.
# $97.50 harness opening (index 0.75): thin solid. A label is printed at the line's top end.
REF_LINES = [
    {"price": 90.0, "index": 0.0, "ls": (0, (5, 3)), "lw": 1.0},
    {"price": 95.0, "index": 0.5, "ls": (0, (1, 2)), "lw": 1.3, "label": "criterion"},
    {"price": 97.5, "index": 0.75, "ls": "-", "lw": 0.6, "label": "opening ask"},
]


def setup():
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": FS,
        "axes.labelsize": FS_HEAD,
        "axes.titlesize": FS_TITLE,
        "xtick.labelsize": FS,
        "ytick.labelsize": FS,
        "legend.fontsize": FS,
        "legend.title_fontsize": FS,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.7,
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 3,
        "savefig.dpi": DPI,
        "figure.dpi": 100,
        "text.parse_math": False,   # dollar signs in labels are prices, not math
    })


def tint(hex_color, amount=0.55):
    """Blend a color with white; amount 0 gives the color, 1 gives white."""
    r, g, b = mpl.colors.to_rgb(hex_color)
    return (r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount)


def ink_on(color):
    """White text on dark bars, black on light ones (relative luminance above 0.3). M.S.'s rule."""
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in mpl.colors.to_rgb(color))
    return "black" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.3 else "white"


def save(fig, name, max_h_in, **kw):
    return printcheck.save(fig, FIGURES / name, max_h_in, **kw)


# The ten Gemini arms in the row order of the offer and warning figures: the five arms without the warning, then the
# five with it (offer arms first, then the two placebo arms that have no offer).
ARM_GROUPS = [("No warning", ["Base", "D", "D-hs", "D-hb", "D-hsb"]),
              ("Warning in the prompt", ["E", "F", "F-sham", "G-warn", "G-prec"])]
NO_OFFER = {"Base", "G-warn", "G-prec"}     # placebo seat 5: no undercover offer is made


def arm_rows(head=0.75):
    """Row positions (y grows downward) for the ten arms. Each group opens with a header slot of height head.
    Returns rows [(group, arm, y)], heads [(group, y of the header center)] and the y span (top, bottom)
    of the warning group, header included."""
    rows, heads, y = [], [], 0.0
    for group, arms in ARM_GROUPS:
        heads.append((group, y + head / 2))
        warn_top = y
        y += head
        for arm in arms:
            y += 0.5
            rows.append((group, arm, y))
            y += 0.5
    return rows, heads, (warn_top, y)


def row_band(fig, ax, y0, y1, color, x0=0.0, x1=1.0):
    """A band behind every axes of fig, from figure x0 to x1 and between data y0 and y1 of ax.
    Axes backgrounds must be transparent for it to show."""
    from matplotlib.patches import Rectangle
    from matplotlib.transforms import blended_transform_factory
    tr = blended_transform_factory(fig.transFigure, ax.transData)
    fig.patches.append(Rectangle((x0, y0), x1 - x0, y1 - y0, transform=tr, facecolor=color, edgecolor="none",
                                 zorder=-1))
