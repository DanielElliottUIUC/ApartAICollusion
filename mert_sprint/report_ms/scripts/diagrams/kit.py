"""Drawing kit shared by the three explanatory diagrams (make_diag1_market.py, make_diag2_design.py,
make_diag3_our_tests.py). Colors and fonts come from scripts/lib/style.py, so the diagrams match the data figures.

The axes span the whole figure in inches (origin bottom left), so every position below is a printed position and
every font size is the printed size. Font floor (owner rule): every text >= 12 pt, titles >= 16 pt.

Arrow grammar, the same in every diagram:
  message      solid, dark gray
  observation  dashed, gray (what an agent sees)
  report       solid, crimson (the report_to_regulator action)
  order        solid, in the color of the agent that posts it (asks, bids)
Fill grammar: an LLM agent is tinted with its model color; a scripted agent is light gray; the warning text and
the warning arms sit on the pale yellow of the data figures (style.WARN_BAND).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import style
from style import COLOR, GRAY, LIGHT, WARN_BAND, WARN_INK, tint

INK = "#222222"
MSG = "#333333"
OBS = GRAY
REPORT = "#B2182B"          # crimson, used only for the report action
SCRIPTED_FILL = "#ECECEC"
MONO = "DejaVu Sans Mono"
LINE = 0.215                # line pitch of 12 pt text, inches
DASH = (0, (4, 2.5))
ARROW = {
    "message": dict(color=MSG, ls="-", lw=1.4),
    "observe": dict(color=OBS, ls=DASH, lw=1.3),
    "report": dict(color=REPORT, ls="-", lw=1.8),
}


def figure(height):
    style.setup()
    fig = plt.figure(figsize=(style.SLOT_IN, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, style.SLOT_IN)
    ax.set_ylim(0, height)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, fc="white", ec=GRAY, lw=1.1, r=0.09, ls="-", z=1):
    """Rounded box with its lower left corner at (x, y)."""
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls,
                       zorder=z)
    ax.add_patch(p)
    return p


def llm_box(ax, x, y, w, h, model, **kw):
    return box(ax, x, y, w, h, fc=tint(COLOR[model], 0.86), ec=COLOR[model], lw=1.4, **kw)


def scripted_box(ax, x, y, w, h, **kw):
    return box(ax, x, y, w, h, fc=SCRIPTED_FILL, ec=GRAY, lw=1.4, **kw)


def text(ax, x, y, s, size=12, ha="left", va="center", color=INK, weight="normal", z=5, **kw):
    if size < 12:
        raise ValueError(f"font floor: {size} pt < 12 pt for {s!r}")
    return ax.text(x, y, s, fontsize=size, ha=ha, va=va, color=color, fontweight=weight, zorder=z, **kw)


def runs(ax, x, y, parts):
    """One left-aligned line built from (string, options) runs, each placed after the measured end of the last."""
    r = ax.figure.canvas.get_renderer()
    dpi = ax.figure.dpi
    for s, opt in parts:
        t = text(ax, x, y, s, **opt)
        x += t.get_window_extent(r).width / dpi
    return x


def lines(ax, x, y_top, rows, ha="left", pitch=LINE):
    """Stack text rows downward from y_top (center of the first row). A row is a string or (string, options)."""
    for i, row in enumerate(rows):
        s, opt = (row, {}) if isinstance(row, str) else row
        text(ax, x, y_top - i * pitch, s, ha=ha, **opt)
    return y_top - (len(rows) - 1) * pitch


def _patch(ax, p0, p1, style, st, ls, head, rad, z):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=head, connectionstyle=f"arc3,rad={rad}",
                                 color=st["color"], lw=st["lw"], ls=ls, shrinkA=0, shrinkB=0, zorder=z,
                                 joinstyle="miter", capstyle="butt"))


def arrow(ax, p0, p1, kind="message", color=None, lw=None, rad=0.0, both=False, z=4, head=11):
    """Arrow from p0 to p1 (inches). A dashed arrow gets a dashed shaft and a solid head, so the head stays crisp."""
    st = dict(ARROW.get(kind, ARROW["message"]))
    if color is not None:
        st["color"] = color
    if lw is not None:
        st["lw"] = lw
    style = "<|-|>" if both else "-|>"
    if st["ls"] == "-":
        _patch(ax, p0, p1, style, st, "-", head, rad, z)
        return
    (x0, y0), (x1, y1) = p0, p1
    n = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    tip = 0.13                                    # length of the solid head segment, inches
    _patch(ax, p0, (x1 - ux * tip, y1 - uy * tip), "-", st, st["ls"], head, 0, z)
    _patch(ax, (x1 - ux * tip, y1 - uy * tip), p1, "-|>", st, "-", head, 0, z)


def chevron(ax, x, y, w=0.26, h=0.36, color=LIGHT):
    """A filled workflow chevron pointing right, its left edge at x, centered vertically on y."""
    d = min(h / 2, w * 0.6)                       # depth of the point and of the notch
    ax.fill([x, x + w - d, x + w, x + w - d, x, x + d], [y + h / 2, y + h / 2, y, y - h / 2, y - h / 2, y],
            color=color, lw=0, zorder=2)


def save(fig, name):
    style.save(fig, name)
    plt.close(fig)
