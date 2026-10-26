"""Figure S42.5: the hour-3 ask as a noise floor and as a predictor of the last third.

(a) Mean ask of the four LLM sellers in hour 3 (market_by_hour.csv avg_ask), one dot per market, arm rows as in
    the main report. Base, D, D-hs, D-hb and D-hsb have identical seller prompts through hour 3 (seat 5's message
    is visible from hour 4), so the gray band, the range of their five arm means, is a run-to-run noise floor.
(b) Last-third ask index (market_by_run.csv) against the hour-3 mean ask, all 50 markets. Circles: no warning;
    diamonds: warning. Filled: meets the joint criterion.
Output: supplement/figures/S42/S42_05_hour3.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import s42lib as L
from s42lib import style

FILE = "S42_05_hour3.png"
FIG_H = 5.5
AA_ARMS = style.ARM_GROUPS[0][1]          # identical seller prompts through hour 3


def make():
    style.setup()
    m = L.markets()
    W = style.SLOT_IN
    fig = plt.figure(figsize=(W, FIG_H))
    y0, y1 = 0.98, FIG_H - 1.05
    a_x0, a_x1, b_x0, b_x1 = 0.98, 3.05, 3.92, 6.36
    ax_a = fig.add_axes([a_x0 / W, y0 / FIG_H, (a_x1 - a_x0) / W, (y1 - y0) / FIG_H])
    ax_b = fig.add_axes([b_x0 / W, y0 / FIG_H, (b_x1 - b_x0) / W, (y1 - y0) / FIG_H])
    rows = L.setup_arm_axes(fig, [ax_a], band_x1=(a_x1 + 0.12) / W)

    # (a) hour-3 ask per market, with the range of the five identical arms' means
    arm_mean = m.groupby("arm")["ask_h3"].mean()
    aa_lo, aa_hi = arm_mean[AA_ARMS].min(), arm_mean[AA_ARMS].max()
    ax_a.axvspan(aa_lo, aa_hi, color=style.BASE_BAND, alpha=style.BASE_BAND_ALPHA, lw=0, zorder=0.2)
    for r in style.REF_LINES:
        ax_a.axvline(r["price"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
    L.draw_arm_dots(ax_a, m[["arm", "seed", "passed"]].assign(value=m["ask_h3"]), rows, ci=False)
    ax_a.set_xlim(93.3, 97.7)
    ax_a.set_xticks([94, 95, 96, 97], ["$94", "$95", "$96", "$97"])
    ax_a.set_xlabel("Mean ask in hour 3")
    ax_a.set_title("Hour 3", pad=6)

    # (b) last-third ask index against hour-3 ask
    for r in style.REF_LINES:
        ax_b.axhline(r["index"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
    for _, r in m.iterrows():
        ax_b.plot([r["ask_h3"]], [r["ask_index"]], ls="none", marker=("D" if r["warn"] else "o"),
                  ms=(5.5 if r["warn"] else 6.5), mew=1.2, mec=L.BLUE, mfc=(L.BLUE if r["passed"] else "white"),
                  zorder=3)
    slope, icpt = np.polyfit(m["ask_h3"], m["ask_index"], 1)
    xs = np.array([m["ask_h3"].min(), m["ask_h3"].max()])
    ax_b.plot(xs, icpt + slope * xs, color="black", lw=1.0, zorder=2)
    r_b = L.pearson(m["ask_h3"], m["ask_index"])
    ax_b.set_xlim(93.3, 97.7)
    ax_b.set_xticks([94, 95, 96, 97], ["$94", "$95", "$96", "$97"])
    ax_b.set_ylim(-0.03, 0.8)
    ax_b.set_yticks([0, 0.25, 0.5, 0.75], ["0", "0.25", "0.5", "0.75"])
    ax_b.set_xlabel("Mean ask in hour 3")
    ax_b.set_ylabel("Ask index, hours 11 to 15")
    ax_b.set_title("Start and end", pad=6)
    ax_b.text(97.6, 0.08, f"r = {r_b:.2f}", ha="right", va="center", fontsize=12)
    fig.text(0.06 / W, (y1 + 0.08) / FIG_H, "a", fontsize=16, fontweight="bold", ha="left", va="bottom")
    fig.text((b_x0 - 0.75) / W, (y1 + 0.08) / FIG_H, "b", fontsize=16, fontweight="bold", ha="left",
             va="bottom")
    L.dots_legend(fig, ci=False)
    fig.legend([Line2D([], [], ls="none", marker="D", ms=5.5, mew=1.2, mec=L.BLUE, mfc="white"),
                Patch(color=style.BASE_BAND, alpha=style.BASE_BAND_ALPHA)],
               ["Warning arm (b)", "Range of the 5 identical arms (a)"], loc="upper center", ncol=2,
               frameon=False, bbox_to_anchor=(0.5, 1.0 - 0.30 / FIG_H), handletextpad=0.3, columnspacing=1.2,
               handlelength=1.2)
    L.save(fig, FILE)
    plt.close(fig)
    h = L.hours()
    w = h.pivot(index="run_id", columns="hour", values="avg_ask")
    idx = m.set_index("run_id").loc[w.index, "ask_index"]
    return {"aa_lo": aa_lo, "aa_hi": aa_hi, "arm_mean": arm_mean, "r3": r_b, "slope": slope,
            "r1": L.pearson(w[1], idx), "mk_lo": m["ask_h3"].min(), "mk_hi": m["ask_h3"].max(),
            "warn_lo": arm_mean[sorted(L.WARN)].min(), "warn_hi": arm_mean[sorted(L.WARN)].max()}


def entry():
    n = make()
    return {
        "title": "The hour-3 ask: a $1.28 noise floor and a predictor of where a market ends",
        "file": FILE,
        "caption": (
            "(a) Mean ask of the four Gemini 3.8 Flash sellers in hour 3, one dot per market, filled when the "
            "market meets the joint criterion, with a black bar at the arm mean. Base, D, D-hs, D-hb and D-hsb "
            "have identical seller prompts through hour 3, because seat 5's message is visible only from hour 4, "
            "and the gray band spans their five arm means. (b) Last-third ask index against the hour-3 mean ask "
            "for all 50 markets, with a least-squares line. Circles: arms without the warning. Diamonds: arms "
            "with it. Reference lines: $90 or index 0 (dashed), $95 or 0.5 (dotted), $97.50 or 0.75 (thin)."),
        "shows": (
            f"Five arms that were identical up to hour 3 already differ by ${n['aa_hi'] - n['aa_lo']:.2f} in "
            f"their hour-3 means (${n['aa_lo']:.2f} to ${n['aa_hi']:.2f}), and single markets span "
            f"${n['mk_lo']:.2f} to ${n['mk_hi']:.2f}. The warning arms, whose prompts differ from hour 1, have "
            f"hour-3 means of ${n['warn_lo']:.2f} to ${n['warn_hi']:.2f}, inside that noise. Where a market stood in "
            f"hour 3 predicts its last third (r = {n['r3']:.2f}; r = {n['r1']:.2f} already for hour 1, before any "
            f"message can be read), so early drift that no arm controls carries through to the criterion."),
        "source": f"`{L.SRC}/market_by_hour.csv` (avg_ask), `{L.SRC}/market_by_run.csv` (ask_index, passed). "
                  f"Script: `supplement/scripts/S42/make_05_hour3.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
