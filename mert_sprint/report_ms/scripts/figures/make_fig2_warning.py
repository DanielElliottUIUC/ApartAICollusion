"""Figure 2: private and public messages and the ask index by arm, with and without the warning
(Daniel's 50 Gemini markets).

One row per arm, in the shared arm order of Figure 1a; the five arms whose seller prompt carries the warning
sit on the warning band.
(a) Messages per market, mean over the arm's 5 markets, in two columns on one scale:
    Private: messages between sellers, table3_extra.csv private_msgs_peer, which excludes messages to the
             scripted seat 5 (dark bars).
    Public:  the sellers' public messages, table3_extra.csv public_msgs (seller-hours with a public message,
             at most 4 sellers x 15 hours = 60) (light bars).
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

FIG_W, FIG_H = style.SLOT_IN, 5.08
LAB_X = 0.86                      # right edge of the arm labels, inches
A_X0, A_W, A_GAP = 0.98, 1.00, 0.30   # panel (a): left edge, width of each column, gap between them, inches
B_X0, B_X1 = 3.62, 6.36           # panel (b), inches
Y0, Y1 = 0.78, 3.98               # bottom and top of both panels, inches
SEED_DY = 0.12                    # vertical offset between seeds in (b), row units
BAR_H = 0.62
X_LABEL_Y = 0.06                  # baseline of both x-axis labels, inches
MSG_MAX = 112                     # x range of both message columns
TALK = [("private_msgs_peer", "Private", style.COLOR["gemini"], "white"),
        ("public_msgs", "Public", style.tint(style.COLOR["gemini"], 0.55), "black")]


def main():
    style.setup()
    mk = load.daniel_markets()
    rows, heads, (w0, w1) = style.arm_rows()
    blue = style.COLOR["gemini"]

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    h = (Y1 - Y0) / FIG_H
    ax_a = [fig.add_axes([(A_X0 + i * (A_W + A_GAP)) / FIG_W, Y0 / FIG_H, A_W / FIG_W, h]) for i in range(2)]
    ax_b = fig.add_axes([B_X0 / FIG_W, Y0 / FIG_H, (B_X1 - B_X0) / FIG_W, h], sharey=ax_a[0])
    ax_a[1].sharey(ax_a[0])
    y_bottom = rows[-1][2] + 0.5
    ax_a[0].set_ylim(y_bottom, 0.0)
    for ax in (*ax_a, ax_b):
        ax.patch.set_alpha(0.0)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    style.row_band(fig, ax_a[0], w0, w1, style.WARN_BAND, x0=0.0, x1=1.0)

    # arm labels and group headers, shared by all three axes
    ax_a[0].set_yticks([y for _, _, y in rows], [arm for _, arm, _ in rows])
    ax_a[0].tick_params(axis="y", pad=(A_X0 - LAB_X) * 72)
    lab_tr = blended_transform_factory(fig.transFigure, ax_a[0].transData)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        ax_a[0].text(0.06 / FIG_W, y, group, transform=lab_tr, ha="left", va="center", fontsize=12,
                     fontstyle="italic", color=(style.WARN_INK if warn else style.GRAY))
    for ax in (ax_a[1], ax_b):
        plt.setp(ax.get_yticklabels(), visible=False)

    # (a) messages per market, mean over the arm's 5 markets: private between sellers, then public
    for ax, (col, head, color, ink) in zip(ax_a, TALK):
        mean_msgs = mk.groupby("arm")[col].mean()
        for _, arm, y in rows:
            m = mean_msgs[arm]
            ax.barh(y, m, height=BAR_H, color=color, lw=0, zorder=2)
            if m > 0:
                ax.text(m - 3, y, f"{m:.1f}", ha="right", va="center", fontsize=12, color=ink, zorder=3)
            else:
                ax.text(3, y, "0", ha="left", va="center", fontsize=12, color="black", zorder=3)
        ax.set_xlim(0, MSG_MAX)
        ax.set_xticks([0, 50, 100])
        ax.text(0.0, 1.0, head, transform=ax.transAxes, ha="left", va="bottom", fontsize=14)
    fig.text((A_X0 + A_W + A_GAP / 2) / FIG_W, X_LABEL_Y / FIG_H, "Messages per market", ha="center",
             va="bottom", fontsize=14)

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
    fig.text((B_X0 + B_X1) / 2 / FIG_W, X_LABEL_Y / FIG_H, "Ask index, hours 11 to 15", ha="center",
             va="bottom", fontsize=14)
    ax_b.text(base.min() + 0.012, heads[0][1], "Base range", ha="left", va="center",
              fontsize=12, color=style.GRAY)

    # panel letters and titles, one baseline above the column headers
    y_t = (Y1 + 0.36) / FIG_H
    for letter, x_in, title, x_title in (("a", 0.06, "Talk", (A_X0 + A_W + A_GAP / 2)),
                                         ("b", B_X0 - 0.30, "Price", (B_X0 + B_X1) / 2)):
        fig.text(x_in / FIG_W, y_t, letter, fontsize=16, fontweight="bold", ha="left", va="bottom")
        fig.text(x_title / FIG_W, y_t, title, fontsize=16, ha="center", va="bottom")

    handles = [Line2D([], [], ls="none", marker="o", ms=6.5, mew=1.3, mec=blue, mfc=blue),
               Line2D([], [], ls="none", marker="o", ms=6.5, mew=1.3, mec=blue, mfc="white"),
               Line2D([], [], ls="none", marker="|", ms=11, mew=2.0, color="black")]
    fig.legend(handles, ["Meets the criterion", "Does not", "Mean of 5 markets"], loc="upper center",
               ncol=3, frameon=False, bbox_to_anchor=(0.5, 1 - 0.04 / FIG_H), handletextpad=0.25,
               columnspacing=1.2)
    style.save(fig, "fig2_warning.png")


if __name__ == "__main__":
    main()
