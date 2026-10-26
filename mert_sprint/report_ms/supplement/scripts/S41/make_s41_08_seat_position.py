"""S41_08. Seat-position diagnostic: which seat reported seat 5 in the plea arms, and the D-hsb pattern.

Data: supplement/data/daniel/dg/outcomes.csv (seat_index, seller_id, report_is_scripted_seat).
Exploratory and post hoc: D-hsb was singled out after the data were seen.
"""
import sys
from itertools import combinations, product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 3.0
NAME = "S41_08_seat_position.png"
ARMS = ["D", "D-hs", "D-hb", "D-hsb"]
CW, RH = 0.52, 0.42           # inches: cell width (panel a), row height
TOP = 1.05                    # inches from the top to the first row


def seat_perm_p(s):
    """Within-market seat-label permutation for one arm: each market keeps its number of reporters, placed on a
    uniformly random set of seats. Returns P(some seat reaches the observed maximum count over markets)."""
    sizes = s.groupby("seed").s5.sum().astype(int).tolist()
    obs = int(s.groupby("seat_index").s5.sum().max())
    opts = [list(combinations(range(4), k)) for k in sizes]
    hits = total = 0
    for cfg in product(*opts):
        cnt = np.zeros(4, int)
        for sub in cfg:
            cnt[list(sub)] += 1
        hits += cnt.max() >= obs
        total += 1
    return hits / total, hits, total, sizes, obs


def make():
    style.setup()
    o = L.gemini_sellers()
    blue = style.COLOR["gemini"]
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    can = fig.add_axes([0, 0, 1, 1])
    can.set_xlim(0, FIG_W)
    can.set_ylim(FIG_H, 0)
    can.axis("off")

    # (a) arms x seat index, reporters of 5 markets
    ax0 = 0.85
    can.text(0.05, 0.22, "a", ha="left", va="center", fontsize=16, fontweight="bold")
    can.text(0.3, 0.22, "Reporters by seat, of 5", ha="left", va="center", fontsize=16)
    for j in range(4):
        can.text(ax0 + (j + 0.5) * CW, TOP - 0.12, str(j), ha="center", va="bottom", fontsize=12)
    can.text(ax0 - 0.1, TOP - 0.12, "seat", ha="right", va="bottom", fontsize=12)
    for i, arm in enumerate(ARMS):
        y = TOP + i * RH
        can.text(ax0 - 0.1, y + RH / 2, arm, ha="right", va="center", fontsize=12)
        tab = o[o.arm == arm].groupby("seat_index").s5.sum()
        for j in range(4):
            k = int(tab.get(j, 0))
            face = "white" if k == 0 else style.tint(blue, 1 - 0.15 - 0.85 * k / 5)
            can.add_patch(Rectangle((ax0 + j * CW + 0.02, y + 0.03), CW - 0.04, RH - 0.06, facecolor=face,
                                    edgecolor=style.LIGHT, lw=0.6))
            can.text(ax0 + (j + 0.5) * CW, y + RH / 2, str(k), ha="center", va="center", fontsize=12,
                     color=("white" if k >= 4 else "black"))

    # (b) D-hsb, seed x seat, seller names
    bx0 = 4.0
    CWB = 0.6
    can.text(3.5, 0.22, "b", ha="left", va="center", fontsize=16, fontweight="bold")
    can.text(3.75, 0.22, "D-hsb seller by seller", ha="left", va="center", fontsize=16)
    for j in range(4):
        can.text(bx0 + (j + 0.5) * CWB, TOP - 0.12, str(j), ha="center", va="bottom", fontsize=12)
    can.text(bx0 - 0.1, TOP - 0.12, "seat", ha="right", va="bottom", fontsize=12)
    s = o[o.arm == "D-hsb"]
    rh_b = RH * 4 / 5
    for seed in range(5):
        y = TOP + seed * rh_b
        can.text(bx0 - 0.1, y + rh_b / 2, f"seed {seed}", ha="right", va="center", fontsize=12)
        for _, r in s[s.seed == seed].iterrows():
            j = int(r.seat_index)
            on = bool(r.s5)
            can.add_patch(Rectangle((bx0 + j * CWB + 0.02, y + 0.025), CWB - 0.04, rh_b - 0.05,
                                    facecolor=(blue if on else "white"), edgecolor=(blue if on else style.LIGHT),
                                    lw=0.6))
            can.text(bx0 + (j + 0.5) * CWB, y + rh_b / 2, r.seller_id.replace("Seller ", ""), ha="center",
                     va="center", fontsize=12, color=("white" if on else style.GRAY))
    L.key_row(fig, bx0, FIG_H - 0.55, [("patch", dict(facecolor=blue), "first report named seat 5")])
    L.save(fig, NAME)

    # numbers for the text
    p, hits, total, sizes, obs = seat_perm_p(s)
    seat1 = s[s.seat_index == 1]
    rest = s[s.seat_index != 1]
    nm = seat1.seller_id.str.replace("Seller ", "").value_counts().sort_index()
    names = ", ".join(f"{n} in {k} markets" if k > 1 else n for n, k in nm.items())
    by_seat = {a: o[o.arm == a].groupby("seat_index").s5.sum().astype(int) for a in ["D", "D-hb", "D-hs"]}
    dhb_rep = int(o[o.arm.isin(["D", "D-hb"])].s5.sum())
    hs1 = int(by_seat["D-hs"][1])
    hs_lowest = hs1 == int(by_seat["D-hs"].min())
    return {
        "id": "S41.8",
        "title": "In D-hsb the lone reporter always sat in seat 1",
        "file": NAME,
        "caption": (
            "This analysis is exploratory and post hoc. (a) For each arm without the warning that carried the offer, how many of its "
            "5 markets had the seller in each seat position (0 to 3) file a first report that named seat 5. "
            "(b) The 20 D-hsb sellers by seed and seat, with their names. Filled cells are the reporters. "
            "The seat index is the seller's position in the market's seller list. Names change with the seed."
        ),
        "shows": (
            f"In D-hsb the seat-1 seller reported in {int(seat1.s5.sum())} of 5 markets, against "
            f"{int(rest.s5.sum())} of {len(rest)} sellers in the other seats. In the {sum(1 for k in sizes if k == 1)}"
            f" markets with a single reporter, it was always seat 1. The seat-1 sellers had {len(nm)} different "
            f"names ({names}), so a persona name does not explain it. In D and D-hb almost every seat reported "
            f"({dhb_rep} of 40), and in D-hs seat 1 reported in {hs1} of 5 markets"
            f"{', the fewest of any seat' if hs_lowest else ''}. Shuffling seat labels within each "
            f"D-hsb market, some seat reaches {obs} of 5 with probability {p:.3f} ({hits} of {total}). This is "
            f"one arm of four, chosen after looking, so it is a lead to check (prompt order and seat placement), "
            f"not a finding."
        ),
        "source": "supplement/data/daniel/dg/outcomes.csv (seat_index, seller_id, report_is_scripted_seat).",
    }


if __name__ == "__main__":
    print(make())
