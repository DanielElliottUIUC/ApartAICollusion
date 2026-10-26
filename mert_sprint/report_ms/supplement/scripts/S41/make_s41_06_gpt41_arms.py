"""S41_06. GPT-4.1 sellers in five arms: reports, judge labels and the market ask index.

Data: supplement/data/daniel/dg_gpt41/outcomes.csv, market_by_run.csv.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 4.65
NAME = "S41_06_gpt41_arms.png"
ARMS = ["Base", "D", "E", "F", "G-warn"]
DESC = {"Base": "placebo", "D": "offer", "E": "offer,\nwarning", "F": "E and\nprecedent",
        "G-warn": "warning,\nno offer"}
WARN = {"E", "F", "G-warn"}
ROWS = [("s5", "Reported seat 5"), ("verbal_accept", "Agreement"), ("verbal_reject", "Rejection"),
        ("suspects_collusion", "Suspects collusion"), ("suspects_test", "Suspects a test")]
X0, PITCH = 2.2, 0.9                     # inches: first column center, column pitch
TILE_W, ROW_H = 0.78, 0.36
TOP_HEAD, A_TOP = 0.3, 0.95              # inches from the top: arm headers, first tile row


def make():
    style.setup()
    o = L.family_sellers("dg_gpt41")
    m = o.drop_duplicates("run_id")[["run_id", "arm", "seed", "ask_index"]]
    if sorted(o.arm.unique()) != sorted(ARMS) or (o.groupby("arm").size() != 12).any():
        raise ValueError("expected 12 GPT-4.1 sellers in each of the five arms")
    orange = style.COLOR["gpt41"]

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    can = fig.add_axes([0, 0, 1, 1], zorder=-2)
    can.set_xlim(0, FIG_W)
    can.set_ylim(FIG_H, 0)                # inches, y down
    can.axis("off")
    xc = {a: X0 + i * PITCH for i, a in enumerate(ARMS)}
    # warning band behind the warning columns, through both panels
    wx = [xc[a] for a in ARMS if a in WARN]
    can.add_patch(Rectangle((min(wx) - PITCH / 2, TOP_HEAD - 0.12), max(wx) - min(wx) + PITCH,
                            FIG_H - TOP_HEAD - 0.23, facecolor=style.WARN_BAND, lw=0, zorder=-1))
    for a in ARMS:
        can.text(xc[a], TOP_HEAD, a, ha="center", va="top", fontsize=12, fontweight="bold")
        can.text(xc[a], TOP_HEAD + 0.22, DESC[a], ha="center", va="top", fontsize=12, color=style.GRAY,
                 linespacing=1.0)
    can.text(0.05, 0.08, "a", ha="left", va="top", fontsize=16, fontweight="bold")
    can.text(0.3, 0.1, "Sellers, of 12", ha="left", va="top", fontsize=16)
    for i, (col, lab) in enumerate(ROWS):
        y = A_TOP + i * ROW_H
        can.text(X0 - PITCH / 2 - 0.02, y + ROW_H / 2, lab, ha="right", va="center", fontsize=12)
        for a in ARMS:
            k = int(o[o.arm == a][col].sum())
            face = "white" if k == 0 else style.tint(orange, 1 - 0.15 - 0.85 * k / 12)
            can.add_patch(Rectangle((xc[a] - TILE_W / 2, y + 0.03), TILE_W, ROW_H - 0.06, facecolor=face,
                                    edgecolor=style.LIGHT, lw=0.6))
            can.text(xc[a], y + ROW_H / 2, str(k), ha="center", va="center", fontsize=12,
                     color=("white" if k >= 9 else ("black" if k else style.GRAY)))

    # (b) market ask index, one dot per market, columns aligned with panel a
    b_top = A_TOP + len(ROWS) * ROW_H + 0.3
    b_bot = 0.35
    bx = fig.add_axes([(X0 - PITCH / 2) / FIG_W, b_bot / FIG_H, len(ARMS) * PITCH / FIG_W,
                       (FIG_H - b_top - b_bot) / FIG_H])
    bx.patch.set_alpha(0)
    for r in style.REF_LINES:
        if 0.15 <= r["index"] <= 0.85:
            bx.axhline(r["index"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
    for i, a in enumerate(ARMS):
        v = m[m.arm == a].ask_index.to_numpy()
        bx.plot(np.full(len(v), i), v, "o", ms=7, mfc="none", mec=orange, mew=1.3, zorder=3)
        bx.plot([i - 0.25, i + 0.25], [v.mean()] * 2, color="black", lw=1.8, zorder=4)
    bx.set_xlim(-0.5, len(ARMS) - 0.5)
    bx.set_ylim(0.2, 0.8)
    bx.set_yticks([0.25, 0.5, 0.75], ["0.25", "0.5", "0.75"])
    bx.set_xticks([])
    bx.spines["bottom"].set_visible(False)
    bx.set_ylabel("Ask index")
    can.text(0.05, b_top - 0.1, "b", ha="left", va="top", fontsize=16, fontweight="bold")
    can.text(0.3, b_top - 0.08, "Markets", ha="left", va="top", fontsize=16)
    L.save(fig, NAME)

    # numbers for the text
    c = o.groupby("arm")[[k for k, _ in ROWS]].sum().astype(int)
    ai = m.groupby("arm").ask_index.mean()
    p_ai = L.exact_perm_p(m[m.arm == "Base"].ask_index, m[m.arm == "D"].ask_index)
    return {
        "id": "S41.6",
        "title": "GPT-4.1 sellers reported only under the precedent",
        "file": NAME,
        "caption": (
            "GPT-4.1 sellers in D.E.'s undercover market, 3 markets and 12 sellers per arm. Shaded columns carry "
            "the warning, and F adds the precedent. (a) Sellers whose first report named seat 5, and sellers with "
            "each judge label true in any hour from hour 4. Darker tiles hold more sellers. (b) Each market's ask "
            "index over the last third (open circles, where 0 is $90 and 1 is $100) with the arm mean (bar). The dotted line "
            "is 0.5, the ask condition of the joint criterion, and the thin line 0.75, the $97.50 opening. Seat 5 "
            "replays a GPT-4.1 pilot seller's asks."
        ),
        "shows": (
            f"With the plain offer, {c.loc['D', 's5']} of 12 GPT-4.1 sellers reported and "
            f"{c.loc['D', 'verbal_accept']} of 12 were coded as agreeing with a peer's proposal, as in Base "
            f"({c.loc['Base', 'verbal_accept']}). With the warning (E) the counts were {c.loc['E', 's5']} and "
            f"{c.loc['E', 'verbal_accept']}. Adding the precedent (F) turned both "
            f"around, with {c.loc['F', 's5']} of 12 reporting, {c.loc['F', 'suspects_collusion']} suspecting "
            f"collusion and {c.loc['F', 'verbal_accept']} agreeing. The F precedent describes almost exactly this offer, so "
            f"F tests a stated rule applied to a matching case. Market ask indices stayed between "
            f"{m.ask_index.min():.2f} and {m.ask_index.max():.2f} across all 15 markets. D against Base gives "
            f"{ai['D']:.2f} against {ai['Base']:.2f} (exact p = {p_ai[0]:.2f} over {p_ai[2]} relabellings of 3 "
            f"against 3 markets, where the smallest possible p is {2 / p_ai[2]:.2f}). The judge labels for "
            f"GPT-4.1 were not checked by a second model."
        ),
        "source": "supplement/data/daniel/dg_gpt41/outcomes.csv (report_is_scripted_seat, verbal_accept, "
                  "verbal_reject, suspects_collusion, suspects_test), market_by_run.csv (ask_index).",
    }


if __name__ == "__main__":
    print(make())
