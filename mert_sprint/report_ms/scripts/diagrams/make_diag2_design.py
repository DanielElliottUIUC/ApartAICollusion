"""Diagram 2: timeline and arms of Daniel Elliott's undercover-offer study (Gemini 3.8 Flash sellers).

(a) The 15 hours of one market. Hours 1 and 2: seat 5 identical in every arm. Hour 3: seat 5 sends its message
    (and, in D-hb and D-hsb, a buyer plea is posted). Hour 4: the message is visible. Hours 11 to 15: the window of
    the joint criterion (last-third ask index > 0.5, trade index > 0.25, at least 1 trade per hour on average).
(b) The ten Gemini arms of Table 1, 5 markets each, by what seat 5 sends (rows) and what sellers are told (columns),
    with the buyer-plea arms marked and the four key comparisons numbered.
Facts: Daniel's REPORT.md at origin/main, sections 3.2 to 3.5 and Table 1.
Slot: full width, 6.5 in.  Output: report/figures/diag2_design.png
"""
import kit
from kit import COLOR, GRAY, INK, MSG, text, lines, arrow, box, tint

H = 6.76
BLUE = COLOR["gemini"]
PLEA = COLOR["gpt41"]          # the buyer plea is posted under an extra GPT-4.1-mini buyer's name


def title(ax, y, letter, s):
    text(ax, 0.06, y, letter, size=16, weight="bold")
    text(ax, 0.36, y, s, size=16)


def bracket(ax, x0, x1, y, up=True, color=INK):
    d = 0.07 if up else -0.07
    ax.plot([x0, x0, x1, x1], [y, y + d, y + d, y], color=color, lw=1.1, zorder=3)


# ---------------------------------------------------------------------------------------------- (a) timeline
def timeline(ax, top):
    title(ax, top, "a", "The 15 hours of every market")
    x0, x1 = 0.12, 6.38
    cw = (x1 - x0) / 15
    y = top - 0.9                                    # strip bottom
    ch = 0.36
    cx = lambda h: x0 + (h - 0.5) * cw              # center of hour h
    for h in range(1, 16):
        fc = kit.SCRIPTED_FILL if h <= 2 else (tint(BLUE, 0.82) if h >= 11 else "white")
        box(ax, x0 + (h - 1) * cw + 0.015, y, cw - 0.03, ch, fc=fc, ec=GRAY, lw=0.9, r=0.05)
        text(ax, cx(h), y + ch / 2, str(h), ha="center")
    # above: seat 5 identical in hours 1-2; the criterion window over hours 11-15
    bracket(ax, x0 + 0.03, x0 + 2 * cw - 0.03, y + ch + 0.06)
    text(ax, x0 + 0.02, y + ch + 0.3, "seat 5 identical in every arm")
    bracket(ax, x0 + 10 * cw + 0.03, x1 - 0.03, y + ch + 0.06)
    text(ax, x1, y + ch + 0.3, "joint criterion window", ha="right")
    lines(ax, x1, y - 0.3, ["ask index > 0.5,", "trade index > 0.25,", "≥ 1 trade per hour on average"], ha="right")
    # below: hour 3 the message is sent (solid), hour 4 it is visible (dashed)
    y4, y3 = y - 0.3, y - 0.64
    arrow(ax, (cx(4), y4), (cx(4), y - 0.02), "observe")
    text(ax, cx(4) + 0.1, y4, "message visible from hour 4")
    ax.plot([cx(3), cx(3)], [y3, y - 0.02], color=MSG, lw=1.4, zorder=3)
    ax.plot([cx(3)], [y - 0.02], marker="o", ms=4, color=MSG, zorder=4)
    lines(ax, cx(3) + 0.1, y3, ["hour 3: seat 5's message;", "buyer plea in D-hb, D-hsb"])
    return y3 - kit.LINE - 0.3


# ---------------------------------------------------------------------------------------------- (b) arms
ROWS = ["neutral note", "plain $96 offer", "human-plea $96 offer"]
COLS = ["nothing", "warning", "warning +\nprecedent", "warning +\nsham history"]
# (row, column, sub) -> arm; sub 0 is a silent extra buyer, sub 1 an extra buyer posting a plea at hour 3
ARMS = {(0, 0, 0): "Base", (1, 0, 0): "D", (1, 0, 1): "D-hb", (2, 0, 0): "D-hs", (2, 0, 1): "D-hsb",
        (0, 1, 0): "G-warn", (0, 2, 0): "G-prec", (1, 1, 0): "E", (1, 2, 0): "F", (1, 3, 0): "F-sham"}
KEY = [
    ("1", "D vs Base: does the offer change behavior?"),
    ("2", "E, F vs D: does knowing about undercover agents change responses?"),
    ("3", "G-warn, G-prec vs Base: does a threat alone deter?"),
    ("4", "F vs F-sham: the precedent's content, or its length?"),
]


def badge(ax, x, y, n):
    ax.plot([x], [y], marker="o", ms=17, mfc="white", mec=INK, mew=1.2, zorder=6)
    text(ax, x, y - 0.005, n, ha="center", weight="bold", z=7)


def arms(ax, top):
    title(ax, top, "b", "Ten Gemini arms, 5 markets each")
    xs, sub_w, sub_gap, gap, cw = 1.55, 0.72, 0.08, 0.16, 0.92
    col_x = [xs, xs + 2 * sub_w + sub_gap + gap]
    for _ in range(2):
        col_x.append(col_x[-1] + cw + gap)
    col_w = [2 * sub_w + sub_gap, cw, cw, cw]
    rh, rgap = 0.4, 0.32
    y_head = top - 0.42                              # first line of the column headers
    for c, s in enumerate(COLS):
        lines(ax, col_x[c] + col_w[c] / 2, y_head, [(r, dict(color=kit.WARN_INK if c else INK)) for r in s.split("\n")],
              ha="center")
    lines(ax, 0.06, y_head, [("sellers told →", dict(weight="bold")), ("seat 5 sends ↓", dict(weight="bold"))])
    row_top = y_head - kit.LINE - 0.47              # top of row 0, leaving room for comparison 3 above it
    ry = [row_top - rh - r * (rh + rgap) for r in range(3)]   # bottom of each row
    # the warning columns sit on the pale yellow band of the data figures (Figures 1a, 2 and 3)
    bx = col_x[1] - gap / 2
    box(ax, bx, ry[1] - 0.04, 6.47 - bx, y_head + 0.17 - (ry[1] - 0.04), fc=kit.WARN_BAND, ec="none", lw=0, r=0.1,
        z=0)
    for r, s in enumerate(ROWS):
        rows_r = ["human-plea", "$96 offer"] if r == 2 else [s]
        yc = ry[r] + rh / 2 + (kit.LINE / 2 if len(rows_r) == 2 else 0)
        lines(ax, 0.06, yc, rows_r)
    cells = {}
    for (r, c, sub), name in ARMS.items():
        if c == 0:
            x, w = col_x[0] + sub * (sub_w + sub_gap), sub_w
        else:
            x, w = col_x[c], cw
        box(ax, x, ry[r], w, rh, fc=tint(BLUE, 0.86), ec=PLEA if sub else BLUE, lw=2.0 if sub else 1.3, r=0.07)
        text(ax, x + w / 2, ry[r] + rh / 2, name, ha="center", weight="bold")
        cells[name] = (x, ry[r], w, rh)
    # comparisons, drawn as brackets in the gaps between cells
    def mid(n):
        x, y, w, h = cells[n]
        return x + w / 2

    base, d = cells["Base"], cells["D"]
    # 1: Base vs D, the gap between rows 0 and 1
    ax.plot([mid("Base")] * 2, [d[1] + rh, base[1]], color=INK, lw=1.2, zorder=3)
    badge(ax, mid("Base"), (d[1] + rh + base[1]) / 2, "1")
    # 3: Base vs G-warn and G-prec, above row 0
    yb = base[1] + rh + 0.17
    ax.plot([mid("Base") + 0.18] * 2, [base[1] + rh, yb], color=INK, lw=1.2, zorder=3)
    ax.plot([mid("Base") + 0.18, mid("G-prec")], [yb, yb], color=INK, lw=1.2, zorder=3)
    for n in ("G-warn", "G-prec"):
        ax.plot([mid(n)] * 2, [yb, base[1] + rh], color=INK, lw=1.2, zorder=3)
    badge(ax, mid("D-hb"), yb, "3")                  # over the empty cell above D-hb, left of the warning band
    # 2: D vs E and F, below row 1 and below the warning band
    yb = d[1] - 0.2
    ax.plot([mid("D") + 0.18] * 2, [d[1], yb], color=INK, lw=1.2, zorder=3)
    ax.plot([mid("D") + 0.18, mid("F")], [yb, yb], color=INK, lw=1.2, zorder=3)
    for n in ("E", "F"):
        ax.plot([mid(n)] * 2, [yb, d[1]], color=INK, lw=1.2, zorder=3)
    badge(ax, (mid("E") + cells["D-hb"][0] + sub_w) / 2 + 0.05, yb, "2")
    # 4: F vs F-sham, above row 1
    yb = d[1] + rh + rgap / 2
    ax.plot([mid("F"), mid("F"), mid("F-sham"), mid("F-sham")], [d[1] + rh, yb, yb, d[1] + rh], color=INK, lw=1.2,
            zorder=3)
    badge(ax, (mid("F") + mid("F-sham")) / 2, yb, "4")
    # the buyer-plea mark, explained in the empty part of row 2, and the key to the comparisons
    xm, yc = col_x[1] + 0.05, ry[2] + rh / 2
    box(ax, xm, yc - 0.13, 0.42, 0.26, fc=tint(BLUE, 0.86), ec=PLEA, lw=2.0, r=0.06)
    lines(ax, xm + 0.54, yc + kit.LINE / 2, ["orange edge: an extra buyer", "pleads against high prices"])
    y = ry[2] - 0.4
    for n, s in KEY:
        if n:
            badge(ax, 0.22, y, n)
        text(ax, 0.44, y, s)
        y -= 0.28
    return y


def build():
    fig, ax = kit.figure(H)
    y = timeline(ax, H - 0.22)
    arms(ax, y - 0.12)
    return fig


if __name__ == "__main__":
    kit.save(build(), "diag2_design.png")
