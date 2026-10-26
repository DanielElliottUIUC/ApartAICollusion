"""S41_09. Asks around the offer hour: Base against D by hour, and the ask change after hour 3 in every arm.

Data: supplement/data/daniel/dg/market_by_hour.csv (avg_ask = mean ask of the four LLM sellers),
outcomes.csv (ask_change_post_offer = mean ask in hours 4 to 6 minus the ask at hour 3, per seller).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 4.6
NAME = "S41_09_ask_change.png"
HOURS = list(range(1, 9))


def make():
    style.setup()
    o = L.gemini_sellers()
    hr = L.gemini_hours()
    blue = style.COLOR["gemini"]
    wide = hr.pivot_table(index=["arm", "seed"], columns="hour", values="avg_ask")

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    y0, y1 = 0.62, FIG_H - 0.55
    ax = fig.add_axes([0.8 / FIG_W, y0 / FIG_H, 2.0 / FIG_W, (y1 - y0) / FIG_H])
    bx = fig.add_axes([4.3 / FIG_W, y0 / FIG_H, 2.1 / FIG_W, (y1 - y0) / FIG_H])
    bx.patch.set_alpha(0)

    # (a) mean LLM ask by hour, Base and D
    style.ref_lines(ax, "price")
    ax.axvspan(3.5, 6.5, color="#EDEDED", lw=0, zorder=0)
    ax.axvline(3, color=style.GRAY, lw=0.8, zorder=0.6)
    ax.text(3.08, 91.15, "offer\nsent", ha="left", va="bottom", fontsize=12, color=style.GRAY, linespacing=1.0)
    ax.text(5.0, 97.95, "hours 4 to 6", ha="center", va="bottom", fontsize=12, color=style.GRAY)
    for arm, col in (("Base", style.GRAY), ("D", blue)):
        w = wide.loc[arm][HOURS]
        for _, row in w.iterrows():
            ax.plot(HOURS, row.values, color=col, lw=0.8, alpha=0.45, zorder=2)
        ax.plot(HOURS, w.mean().values, color=col, lw=2.4, zorder=3)
        ax.text(8.2, w.mean().values[-1], arm, ha="left", va="center", fontsize=12, color=col,
                fontweight="bold")
    ax.set_xlim(0.7, 8.0)
    ax.set_ylim(91.0, 97.9)
    ax.set_xticks([1, 2, 3, 4, 5, 6, 7, 8])
    ax.set_xlabel("Hour")
    ax.set_ylabel("Mean ask of 4 sellers ($)")
    fig.text(0.05 / FIG_W, (FIG_H - 0.2) / FIG_H, "a", fontsize=16, fontweight="bold", ha="left", va="center")
    fig.text(0.3 / FIG_W, (FIG_H - 0.2) / FIG_H, "Base and D, by market", fontsize=16, ha="left", va="center")

    # (b) ask change, hours 4 to 6 minus hour 3, market means by arm
    rows, heads, (w0, w1) = style.arm_rows(head=0.6)
    mm = o.groupby(["arm", "seed"]).ask_change_post_offer.mean()
    base_mean = mm["Base"].mean()
    bx.set_ylim(rows[-1][2] + 0.5, 0.0)
    style.row_band(fig, bx, w0, w1, style.WARN_BAND, x0=3.5 / FIG_W)
    bx.axvline(0, color="black", lw=0.8, zorder=0.6)
    bx.axvline(base_mean, color=style.GRAY, lw=1.0, ls=(0, (1, 2)), zorder=0.6)
    for _, arm, y in rows:
        v = mm[arm].to_numpy()
        bx.plot(v, np.full(len(v), y), "o", ms=5.5, mfc="none", mec=blue, mew=1.2, zorder=3)
        bx.plot([v.mean()] * 2, [y - 0.32, y + 0.32], color="black", lw=1.8, zorder=4)
    bx.set_yticks([y for _, _, y in rows], [a for _, a, _ in rows])
    bx.tick_params(axis="y", length=0)
    bx.spines["left"].set_visible(False)
    bx.set_xlim(-1.6, 0.4)
    bx.set_xticks([-1.5, -1.0, -0.5, 0.0])
    bx.set_xticklabels(["−1.5", "−1", "−0.5", "0"])
    bx.set_xlabel("Ask change ($)")
    fig.text(3.55 / FIG_W, (FIG_H - 0.2) / FIG_H, "b", fontsize=16, fontweight="bold", ha="left", va="center")
    fig.text(3.8 / FIG_W, (FIG_H - 0.2) / FIG_H, "After the offer, all arms", fontsize=16, ha="left",
             va="center")
    L.save(fig, NAME)

    # numbers for the text
    def step(h_from, h_to):
        d = wide[h_to] - wide[h_from]
        a, b = d.loc["D"].to_numpy(), d.loc["Base"].to_numpy()
        p, hits, total = L.exact_perm_p(a, b)
        return a.mean() - b.mean(), p
    s12, s23, s34 = step(1, 2), step(2, 3), step(3, 4)
    p_ch = L.exact_perm_p(mm["D"], mm["Base"])[0]
    h3 = wide[3].groupby("arm").mean()
    nw = ["Base", "D", "D-hs", "D-hb", "D-hsb"]
    spread = h3[nw].max() - h3[nw].min()
    arm_means = mm.groupby("arm").mean()

    def usd(v):
        return ("−" if v < 0 else "+") + f"${abs(v):.2f}"
    return {
        "id": "S41.9",
        "title": "Asks fell after the offer, and they were already falling",
        "file": NAME,
        "caption": (
            "Gemini 3.8 Flash sellers. (a) Mean ask of the four LLM sellers in each market over hours 1 to 8, Base (gray) "
            "and D (blue). Thin lines are the 5 markets and thick lines the arm means. Seat 5 sent its note at hour "
            "3, and in D its own ask dropped to $96 at that hour. The gray area marks hours 4 to 6, the window of "
            "the ask-change measure. The dotted line is $95 and the thin line the $97.50 opening. (b) Ask change, the mean ask "
            "in hours 4 to 6 minus the ask at hour 3, averaged over the 4 sellers of each market (open circles), "
            "with the arm mean (bar). The dotted vertical line is the Base mean. Shaded rows carry the warning."
        ),
        "shows": (
            f"From hour 3 to hours 4 to 6 the mean ask changed by {usd(arm_means['D'])} in D and by "
            f"{usd(arm_means['Base'])} in Base (exact p = {p_ch:.2f} over markets). Panel (a) shows that D was "
            f"already falling faster than Base before the offer could be read, by point estimate. The hourly "
            f"step of the D mean ask minus that of Base was {usd(s12[0])} from hour 1 to 2 (p = {s12[1]:.2f}), "
            f"{usd(s23[0])} from hour 2 to 3 (p = {s23[1]:.2f}) and {usd(s34[0])} from hour 3 to 4 (p = "
            f"{s34[1]:.3f}). Panel (b) shows the noise floor. An arm with no offer (G-warn) and two arms with "
            f"the warning (E, F-sham) also fell more than Base (G-warn "
            f"{usd(arm_means['G-warn'])}, E {usd(arm_means['E'])}, F-sham {usd(arm_means['F-sham'])}), and the "
            f"hour-3 mean asks of the five arms whose prompts were identical through hour 3 spread over "
            f"${spread:.2f}. The "
            f"drop in D is also a package with seat 5's own cut to $96, so it is weak evidence of a response "
            f"to the offer."
        ),
        "source": "supplement/data/daniel/dg/market_by_hour.csv (avg_ask), outcomes.csv (ask_change_post_offer).",
    }


if __name__ == "__main__":
    print(make())
