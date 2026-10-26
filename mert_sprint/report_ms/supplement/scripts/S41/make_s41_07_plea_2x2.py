"""S41_07. The plea 2x2 (seller wording plain or human x buyer plea none or human): reports and replies per market.

Data: supplement/data/daniel/dg/outcomes.csv (report_is_scripted_seat), table3_extra.csv (replied_to_seat5_from_h4).
Exploratory: the pooled wording contrast is not one of D.E.'s planned contrasts.
"""
import sys
from itertools import combinations, product
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 3.9
NAME = "S41_07_plea_2x2.png"
CELL = {("plain", "none"): "D", ("plain", "human"): "D-hb", ("human", "none"): "D-hs", ("human", "human"): "D-hsb"}


def stratified_p(per_market):
    """Exact two-sided test of seller wording, permuting wording labels within each buyer-plea stratum.
    per_market: dict arm -> list of 5 per-market values. Statistic: pooled plain minus pooled human total."""
    dists = []
    obs = 0.0
    for buyer in ("none", "human"):
        a, b = per_market[CELL[("plain", buyer)]], per_market[CELL[("human", buyer)]]
        pool = np.array(a + b, float)
        tot = pool.sum()
        obs += 2 * sum(a) - tot
        dists.append([2 * pool[list(c)].sum() - tot for c in combinations(range(10), 5)])
    hits = total = 0
    for x, y in product(*dists):
        hits += abs(x + y) >= abs(obs) - 1e-9
        total += 1
    return hits / total, hits, total


def make():
    style.setup()
    o = L.gemini_sellers()
    t = L.gemini_markets()
    blue = style.COLOR["gemini"]
    rep = {a: [int(o[(o.arm == a) & (o.seed == s)].s5.sum()) for s in range(5)] for a in CELL.values()}
    rpl = {a: [int(t[(t.arm == a) & (t.seed == s)].replied_to_seat5_from_h4.iloc[0]) for s in range(5)]
           for a in CELL.values()}

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    y0, h = 0.75, FIG_H - 1.55
    axes = [fig.add_axes([0.8 / FIG_W, y0 / FIG_H, 2.0 / FIG_W, h / FIG_H]),
            fig.add_axes([3.65 / FIG_W, y0 / FIG_H, 2.0 / FIG_W, h / FIG_H])]
    rng = np.random.default_rng(1)
    for ax, data, letter, title in ((axes[0], rep, "a", "Reported seat 5"),
                                    (axes[1], rpl, "b", "Wrote back to seat 5")):
        for wording, dx, filled in (("plain", -0.09, True), ("human", 0.09, False)):
            means = []
            for xi, buyer in enumerate(("none", "human")):
                v = np.array(data[CELL[(wording, buyer)]], float)
                jit = rng.uniform(-0.035, 0.035, len(v))
                ax.plot(xi + dx + jit, v + rng.uniform(-0.06, 0.06, len(v)), "o", ms=4.5, color=blue,
                        alpha=0.45, mew=0, zorder=2)
                means.append(v.mean())
            ax.plot([0 + dx, 1 + dx], means, "-", color=blue, lw=1.6, zorder=3)
            for xi, mval in enumerate(means):
                ax.plot(xi + dx, mval, "o", ms=9, mfc=(blue if filled else "white"), mec=blue, mew=1.6, zorder=4)
        ax.set_xlim(-0.35, 1.35)
        ax.set_ylim(-0.3, 4.3)
        ax.set_yticks(range(5))
        ax.set_xticks([0, 1], ["none", "human"])
        ax.set_xlabel("Buyer plea")
        x_in = ax.get_position().x0 * FIG_W
        fig.text((x_in - 0.75) / FIG_W, (FIG_H - 0.2) / FIG_H, letter, fontsize=16, fontweight="bold",
                 ha="left", va="center")
        fig.text((x_in - 0.45) / FIG_W, (FIG_H - 0.2) / FIG_H, title, fontsize=16, ha="left", va="center")
    axes[0].set_ylabel("Sellers per market, of 4")
    L.key_row(fig, 0.8, FIG_H - 0.55, [("marker", dict(marker="o", ms=9, mfc=blue, mec=blue, mew=1.6),
                                        "plain offer (D, D-hb)"),
                                       ("marker", dict(marker="o", ms=9, mfc="white", mec=blue, mew=1.6),
                                        "human-seller plea (D-hs, D-hsb)")], gap_in=0.3)
    L.save(fig, NAME)

    # numbers for the text
    tot = {a: sum(v) for a, v in rep.items()}
    plain = tot["D"] + tot["D-hb"]
    human = tot["D-hs"] + tot["D-hsb"]
    inter = ((tot["D-hsb"] - tot["D-hb"]) - (tot["D-hs"] - tot["D"])) / 20 * 100
    p, hits, total = stratified_p(rep)
    p_r, _, _ = stratified_p(rpl)
    ever = o.groupby("arm").ever_s5.sum()
    plain_ever = int(ever["D"] + ever["D-hb"])
    p_hsb = L.exact_perm_p(rep["D"], rep["D-hsb"])[0]
    p_hs = L.exact_perm_p(rep["D"], rep["D-hs"])[0]
    rt = {a: sum(v) for a, v in rpl.items()}
    return {
        "id": "S41.7",
        "title": "The human-seller plea, not the buyer plea, lowered reporting",
        "file": NAME,
        "caption": (
            "D.E.'s plea arms form a 2 x 2 design. Seat 5's offer was worded plainly or as a human seller's plea, "
            "and a human buyer's plea was or was not posted at hour 3 (D, D-hs, D-hb, D-hsb). Small points are "
            "markets (5 per arm, jittered), large points the arm means, filled for the plain wording and open "
            "for the human-seller plea. (a) Sellers whose first report named seat 5. (b) Sellers who sent seat 5 "
            "at least one private message from hour 4 on. The pooled wording contrast is exploratory, "
            "since it was not a planned test."
        ),
        "shows": (
            f"With the plain wording, {plain} of 40 sellers reported seat 5, against {human} of 40 with the "
            f"human-seller plea ({plain_ever} of 40 plain when later reports are counted). An exact test that "
            f"permutes the wording within each buyer-plea stratum gives p = {p:.4f} ({hits} of {total} "
            f"assignments). The buyer plea alone did not lower reporting (D {tot['D']}, D-hb {tot['D-hb']}), "
            f"and the drop with both pleas exceeds the sum of the two single changes by "
            f"{abs(inter):.0f} percentage points, an interaction that was not tested. Single-arm tests against D give p = "
            f"{p_hs:.2f} for D-hs and {p_hsb:.3f} for D-hsb. Replies did not follow the same pattern (D "
            f"{rt['D']}, D-hs {rt['D-hs']}, D-hb {rt['D-hb']}, D-hsb {rt['D-hsb']} of 20, with a stratified "
            f"p of {p_r:.2f}), so the plea lowered reporting without lowering replies to seat 5. The plea "
            f"also changes the offer's argument, length and tone, so this is not a clean test of human identity."
        ),
        "source": "supplement/data/daniel/dg/outcomes.csv (report_is_scripted_seat, seed), table3_extra.csv "
                  "(replied_to_seat5_from_h4).",
    }


if __name__ == "__main__":
    print(make())
