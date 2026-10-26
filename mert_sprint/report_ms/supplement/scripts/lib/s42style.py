"""Frozen copy of report_ms/scripts/lib/style.py taken on 2026-10-25 for the S4.2 supplement figures.

The main report's style file is being edited while the report is written, so the S4.2 scripts read this copy
and do not change when that file changes. Only the module docstring differs from the source.
"""
import matplotlib as mpl

SLOT_IN = 6.5          # full text width, inches
DPI = 300

COLOR = {
    "gemini": "#0072B2",   # Gemini 3.8 Flash (both Daniel's and our markets)
    "sol": "#D55E00",      # GPT-5.6 Sol
    "luna": "#009E73",     # GPT-6 Luna
    "grok": "#CC79A7",     # Grok 4.7
    "gpt41": "#E69F00",    # GPT-4.1
    "haiku": "#56B4E9",    # Claude Haiku 5.5
}
NAME = {
    "gemini": "Gemini 3.8 Flash", "sol": "GPT-5.6 Sol", "luna": "GPT-6 Luna", "grok": "Grok 4.7",
    "gpt41": "GPT-4.1", "haiku": "Claude Haiku 5.5",
}
GRAY = "#555555"
LIGHT = "#BBBBBB"
# Daniel's Base seed range of ask index (Figures 2b and 3). See-through, so the warning band shows where the two
# cross; on white it reads as #E9E9E9.
BASE_BAND, BASE_BAND_ALPHA = "#B2B2B2", 0.28

# Arms whose seller prompt carries the warning (E, F, F-sham, G-warn, G-prec): a pale band behind their rows
# and dark text for their group label (Figures 1 and 2). Okabe-Ito yellow, which no seller model uses.
WARN_BAND = "#FBF3C4"
WARN_INK = "#7A6400"

# Reference prices and their line styles, used in every figure ($ and ask-index units).
# $90 competitive (index 0): dashed. $95 (index 0.5, the ask condition of the criterion): dotted.
# $97.50 harness opening (index 0.75): thin solid.
REF_LINES = [
    {"price": 90.0, "index": 0.0, "ls": (0, (5, 3)), "lw": 1.2},
    {"price": 95.0, "index": 0.5, "ls": (0, (1, 2)), "lw": 1.6},
    {"price": 97.5, "index": 0.75, "ls": "-", "lw": 0.7},
]

# Messaging on and off (Figure 4): solid and dash-dot, so neither matches a reference style.
MSG_LS = {"on": "-", "off": (0, (7, 2.5, 1.5, 2.5))}


def setup():
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.labelsize": 14,
        "axes.titlesize": 16,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "legend.title_fontsize": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.9,
        "xtick.major.width": 0.9,
        "ytick.major.width": 0.9,
        "savefig.dpi": DPI,
        "figure.dpi": 100,
        "text.parse_math": False,   # dollar signs in labels are prices, not math
    })


def ref_lines(ax, unit="price", **kw):
    """Draw the three reference lines across an axis, in $ ('price') or ask-index ('index') units."""
    for r in REF_LINES:
        ax.axhline(r[unit], color=GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5, **kw)


def panel_letter(ax, letter, x=-0.02, y=1.02):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=16, fontweight="bold",
            ha="right", va="bottom")


def tint(hex_color, amount=0.55):
    """Blend a color with white; amount 0 gives the color, 1 gives white."""
    r, g, b = mpl.colors.to_rgb(hex_color)
    return (r + (1 - r) * amount, g + (1 - g) * amount, b + (1 - b) * amount)


def save(fig, name):
    from load import FIGURES
    FIGURES.mkdir(parents=True, exist_ok=True)
    w, h = fig.get_size_inches()
    if abs(w - SLOT_IN) > 1e-6:
        raise ValueError(f"{name}: width {w} in, slot is {SLOT_IN} in")
    path = FIGURES / name
    fig.savefig(path, dpi=DPI)
    print(f"wrote {path} ({w:.2f} x {h:.2f} in)")


def end_labels(ax, items, x, gap_in=0.2, **kw):
    """Label line ends at data x, in each line's color, spreading labels apart by at least gap_in inches.
    items: list of (y, text, color). A thin leader joins a label to its line end when the label moved."""
    fig = ax.figure
    h_in = ax.get_position().height * fig.get_size_inches()[1]
    lo, hi = ax.get_ylim()
    gap = gap_in * (hi - lo) / h_in
    items = sorted(items, key=lambda t: t[0])
    pos = [it[0] for it in items]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    shift = (sum(it[0] for it in items) - sum(pos)) / len(pos)     # re-center the stack on the line ends
    pos = [p + shift for p in pos]
    for i in range(1, len(pos)):
        pos[i] = max(pos[i], pos[i - 1] + gap)
    x_end = ax.get_xlim()[1]
    for (y, text, color), py in zip(items, pos):
        ax.text(x, py, text, ha="left", va="center", fontsize=12, color=color, clip_on=False, **kw)
        if abs(py - y) > gap * 0.15:
            ax.plot([x_end - 0.25, x - 0.1], [y, py], color=color, lw=0.8, clip_on=False)



# The ten Gemini arms of Daniel's study, in the row order of Figures 1a and 2: the five arms without the warning,
# then the five with it (offer arms first, then the two placebo arms that have no offer).
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
