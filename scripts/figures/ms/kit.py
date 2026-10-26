"""Drawing kit for the market diagram (body Figure 1).

Adapted from M.S.'s mert_sprint/report_ms/scripts/diagrams/kit.py (ref origin/mert_sprint_sync_oct25), by M.S.;
the arrow and fill grammar are his. Changes for print: the font floor is 8 pt (his was 12 pt on a 6.5 in slot that
the report printed at about 2.7 in), the line pitch, line widths and arrow heads are scaled to match, and saving goes
through scripts/figures/printcheck.py.

The axes span the whole figure in inches (origin bottom left), so every position is a printed position and every
font size is the printed size.

Arrow grammar:
  message      solid, dark gray
  observation  dashed, gray (what an agent sees)
  report       solid, crimson (the report_to_regulator action)
  order        solid, in the color of the agent that posts it (asks, bids)
Fill grammar: an LLM agent is tinted with its model color; a scripted agent is light gray; the warning text sits
on the pale yellow of the data figures (style.WARN_BAND).
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import style
from style import COLOR, GRAY, WARN_BAND, WARN_INK, tint  # noqa: F401  (re-exported for the diagram)

INK = "#222222"
MSG = "#333333"
OBS = GRAY
REPORT = "#B2182B"          # crimson, used only for the report action
SCRIPTED_FILL = "#ECECEC"
MONO = "DejaVu Sans Mono"
FLOOR = 8.0                 # font floor, points
LINE = 0.148                # line pitch of 8.5 pt text, inches
DASH = (0, (3.5, 2.2))
ARROW = {
    "message": dict(color=MSG, ls="-", lw=1.1),
    "observe": dict(color=OBS, ls=DASH, lw=1.0),
    "report": dict(color=REPORT, ls="-", lw=1.4),
}


def figure(height):
    style.setup()
    fig = plt.figure(figsize=(style.SLOT_IN, height))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, style.SLOT_IN)
    ax.set_ylim(0, height)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, fc="white", ec=GRAY, lw=0.9, r=0.06, ls="-", z=1):
    """Rounded box with its lower left corner at (x, y)."""
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls,
                       zorder=z)
    ax.add_patch(p)
    return p


def llm_box(ax, x, y, w, h, model, **kw):
    return box(ax, x, y, w, h, fc=tint(COLOR[model], 0.86), ec=COLOR[model], lw=1.1, **kw)


def scripted_box(ax, x, y, w, h, **kw):
    return box(ax, x, y, w, h, fc=SCRIPTED_FILL, ec=GRAY, lw=1.1, **kw)


def text(ax, x, y, s, size=style.FS, ha="left", va="center", color=INK, weight="normal", z=5, **kw):
    if size < FLOOR:
        raise ValueError(f"font floor: {size} pt < {FLOOR} pt for {s!r}")
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


def _patch(ax, p0, p1, style_, st, ls, head, rad, z):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style_, mutation_scale=head, connectionstyle=f"arc3,rad={rad}",
                                 color=st["color"], lw=st["lw"], ls=ls, shrinkA=0, shrinkB=0, zorder=z,
                                 joinstyle="miter", capstyle="butt"))


def arrow(ax, p0, p1, kind="message", color=None, lw=None, rad=0.0, both=False, z=4, head=8):
    """Arrow from p0 to p1 (inches). A dashed arrow gets a dashed shaft and a solid head, so the head stays crisp."""
    st = dict(ARROW.get(kind, ARROW["message"]))
    if color is not None:
        st["color"] = color
    if lw is not None:
        st["lw"] = lw
    style_ = "<|-|>" if both else "-|>"
    if st["ls"] == "-":
        _patch(ax, p0, p1, style_, st, "-", head, rad, z)
        return
    (x0, y0), (x1, y1) = p0, p1
    n = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
    ux, uy = (x1 - x0) / n, (y1 - y0) / n
    tip = 0.09                                    # length of the solid head segment, inches
    _patch(ax, p0, (x1 - ux * tip, y1 - uy * tip), "-", st, st["ls"], head, 0, z)
    _patch(ax, (x1 - ux * tip, y1 - uy * tip), p1, "-|>", st, "-", head, 0, z)


def save(fig, name, max_h_in):
    m = style.save(fig, name, max_h_in)
    plt.close(fig)
    return m
