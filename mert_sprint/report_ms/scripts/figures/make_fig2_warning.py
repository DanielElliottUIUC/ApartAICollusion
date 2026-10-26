"""Figure 2: the warning silences talk between sellers, not prices (Daniel's 50 Gemini markets).

One row per arm, in the shared arm order of Figure 1a; the five arms whose seller prompt carries the warning
sit on the warning band.
(a) Private messages between sellers per market, mean over the arm's 5 markets (bars).
    table3_extra.csv private_msgs_peer, which excludes messages to the scripted seat 5.
(b) Last-third ask index per market (market_by_run.csv ask_index), one dot per seed (offset vertically by
    seed), filled when the market passes the joint criterion (market_by_run.csv passed); a vertical bar marks
    the arm mean. The gray band is Base's seed range. Reference lines: index 0 ($90) dashed, 0.5 ($95, the
    ask condition of the criterion) dotted, 0.75 ($97.50 opening) thin solid.
Slot: full width, 6.5 in.  Output: report/figures/fig2_warning.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory

import load
import style

FIG_W, FIG_H = style.SLOT_IN, 5.0
LAB_X = 0.86                      # right edge of the arm labels, inches
A_X0, A_X1 = 0.98, 2.62           # panel (a), inches
B_X0, B_X1 = 2.98, 6.36           # panel (b), inches
Y0, Y1 = 0.98, 4.18               # bottom and top of both panels, inches
SEED_DY = 0.12                    # vertical offset between seeds in (b), row units
BAR_H = 0.62


def main():
    style.setup()
    mk = load.daniel_markets()
    rows, heads, (w0, w1) = style.arm_rows()
    blue = style.COLOR["gemini"]

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax_a = fig.add_axes([A_X0 / FIG_W, Y0 / FIG_H, (A_X1 - A_X0) / FIG_W, (Y1 - Y0) / FIG_H])
    ax_b = fig.add_axes([B_X0 / FIG_W, Y0 / FIG_H, (B_X1 - B_X0) / FIG_W, (Y1 - Y0) / FIG_H], sharey=ax_a)
    y_bottom = rows[-1][2] + 0.5
    ax_a.set_ylim(y_bottom, 0.0)
    for ax in (ax_a, ax_b):
        ax.patch.set_alpha(0.0)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    style.row_band(fig, ax_a, w0, w1, style.WARN_BAND, x0=0.0, x1=1.0)

    # arm labels and group headers, shared by both panels
    ax_a.set_yticks([y for _, _, y in rows], [arm for _, arm, _ in rows])
    ax_a.tick_params(axis="y", pad=(A_X0 - LAB_X) * 72)
    lab_tr = blended_transform_factory(fig.transFigure, ax_a.transData)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        ax_a.text(0.06 / FIG_W, y, group, transform=lab_tr, ha="left", va="center", fontsize=12,
                  fontstyle="italic", color=(style.WARN_INK if warn else style.GRAY))
    plt.setp(ax_b.get_yticklabels(), visible=False)

    # (a) private messages between sellers, mean per market
    msgs = mk.groupby("arm")["private_msgs_peer"]
    mean_msgs = msgs.mean()
    for _, arm, y in rows:
        m = mean_msgs[arm]
        ax_a.barh(y, m, height=BAR_H, color=blue, lw=0, zorder=2)
        if m > 0:
            ax_a.text(m - 3, y, f"{m:.1f}", ha="right", va="center", fontsize=12, color="white", zorder=3)
        else:
            ax_a.text(3, y, "0", ha="left", va="center", fontsize=12, color="black", zorder=3)
    ax_a.set_xlim(0, 118)
    ax_a.set_xticks([0, 50, 100])
    ax_a.set_xlabel("Private messages\nper market")
    ax_a.set_title("Talk", pad=8)

    # (b) last-third ask index per market
    base = mk.query("arm == 'Base'")["ask_index"]
    ax_b.axvspan(base.min(), base.max(), color=style.BASE_BAND, alpha=style.BASE_BAND_ALPHA, lw=0,
                 zorder=0.2)
    for r in style.REF_LINES:
        ax_b.axvline(r["index"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
    for _, arm, y in rows:
        sub = mk[mk["arm"] == arm].sort_values("seed")
        if list(sub["seed"]) != [0, 1, 2, 3, 4]:
            raise ValueError(f"{arm}: expected seeds 0 to 4")
        for _, r in sub.iterrows():
            yy = y + (r["seed"] - 2) * SEED_DY
            ax_b.plot([r["ask_index"]], [yy], ls="none", marker="o", ms=6.5, mew=1.3, mec=blue,
                      mfc=(blue if r["passed"] else "white"), zorder=3)
        ax_b.plot([sub["ask_index"].mean()] * 2, [y - 0.38, y + 0.38], color="black", lw=2.0,
                  solid_capstyle="butt", zorder=4)
    ax_b.set_xlim(-0.04, 0.83)
    ax_b.set_xticks([0, 0.25, 0.5, 0.75], ["0\n$90", "0.25", "0.5\n$95", "0.75\n$97.50"])
    ax_b.set_xlabel("Ask index, hours 11 to 15")
    ax_b.text(base.min() + 0.012, heads[0][1], "Base range", ha="left", va="center",
              fontsize=12, color=style.GRAY)
    ax_b.set_title("Price", pad=8)

    for ax, letter, x_in in ((ax_a, "a", 0.06), (ax_b, "b", B_X0 - 0.30)):
        fig.text(x_in / FIG_W, (Y1 + 0.10) / FIG_H, letter, fontsize=16, fontweight="bold", ha="left",
                 va="bottom")

    handles = [Line2D([], [], ls="none", marker="o", ms=6.5, mew=1.3, mec=blue, mfc=blue),
               Line2D([], [], ls="none", marker="o", ms=6.5, mew=1.3, mec=blue, mfc="white"),
               Line2D([], [], ls="none", marker="|", ms=11, mew=2.0, color="black")]
    fig.legend(handles, ["Meets the criterion", "Does not", "Mean of 5 markets"], loc="upper center",
               ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.0), handletextpad=0.25, columnspacing=1.2)
    style.save(fig, "fig2_warning.png")


if __name__ == "__main__":
    main()
