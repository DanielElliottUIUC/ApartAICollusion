"""Body Figure 5: private and public messages and the ask index by arm, with and without the warning
(the 50 Gemini undercover-market runs).

Adapted from M.S.'s mert_sprint/report_ms/scripts/figures/make_fig2_warning.py (ref origin/mert_sprint_sync_oct25),
by M.S.: same panels, data and encodings, re-laid for print at 6.5 x 3.3 in with every text at least 8 pt (his
figure was 6.5 x 5.08 in at 12 to 16 pt and printed at about half width). Changes: the panel titles carry the axis
names (no x-axis labels), the legend sits over panel b, flush with its right edge, the dots are smaller.

One row per arm, in the arm order of Figure 4a; the five arms whose seller prompt carries the warning sit on the
warning band.
(a) Messages per market, mean over the arm's 5 markets, in two columns on one scale:
    Private, seller to seller: messages between sellers, table3_extra.csv private_msgs_peer, which excludes
             messages to the scripted seat 5 (dark bars).
    Public:  the sellers' public messages, table3_extra.csv public_msgs (seller-hours with a public message,
             at most 4 sellers x 15 hours = 60) (light bars).
(b) Last-third ask index per market (market_by_run.csv ask_index), one dot per seed (offset vertically by
    seed), filled when the market passes the joint criterion (market_by_run.csv passed); a vertical bar marks
    the arm mean. The gray band is Base's seed range. Reference lines: index 0 ($90) dashed, 0.5 ($95, the
    ask condition of the criterion) dotted and labelled "criterion", 0.75 ($97.50 opening) thin solid and labelled
    "opening ask".

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/ms/make_fig5_warning.py
Output: report/figures/fig5_warning.png (6.5 x 3.3 in, 300 dpi)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

import load  # noqa: E402
import style  # noqa: E402

FIG_W, FIG_H = style.SLOT_IN, 3.3
LAB_X = 0.60                      # right edge of the arm labels, inches
A_X0, A_W, A_GAP = 0.68, 0.94, 0.20   # panel (a): left edge, width of each column, gap between them, inches
B_X0, B_X1 = 3.18, 6.40           # panel (b), inches
Y0, Y1 = 0.36, 2.84               # bottom and top of both panels, inches
Y_TITLE, Y_HEAD = 3.18, 2.97      # centers of the panel titles and of the column headers / legend
SEED_DY = 0.12                    # vertical offset between seeds in (b), row units
BAR_H = 0.62
MSG_MAX = 112                     # x range of both message columns
MS = 4.6                          # dot size, points
TALK = [("private_msgs_peer", "Private, seller to seller", style.COLOR["gemini"], "white"),
        ("public_msgs", "Public", style.tint(style.COLOR["gemini"], 0.55), "black")]


def build():
    style.setup()
    mk = load.daniel_markets()
    rows, heads, (w0, w1) = style.arm_rows()
    blue = style.COLOR["gemini"]
    printed = {}

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    h = (Y1 - Y0) / FIG_H
    ax_a = [fig.add_axes([(A_X0 + i * (A_W + A_GAP)) / FIG_W, Y0 / FIG_H, A_W / FIG_W, h]) for i in range(2)]
    ax_b = fig.add_axes([B_X0 / FIG_W, Y0 / FIG_H, (B_X1 - B_X0) / FIG_W, h], sharey=ax_a[0])
    ax_a[1].sharey(ax_a[0])
    ax_a[0].set_ylim(rows[-1][2] + 0.5, 0.0)
    for ax in (*ax_a, ax_b):
        ax.patch.set_alpha(0.0)
        ax.tick_params(axis="y", length=0)
        ax.tick_params(axis="x", pad=2)
        ax.spines["left"].set_visible(False)
    style.row_band(fig, ax_a[0], w0, w1, style.WARN_BAND)

    # arm labels and group headers, shared by all three axes
    ax_a[0].set_yticks([y for _, _, y in rows], [arm for _, arm, _ in rows])
    ax_a[0].tick_params(axis="y", pad=(A_X0 - LAB_X) * 72)
    lab_tr = blended_transform_factory(fig.transFigure, ax_a[0].transData)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        ax_a[0].text(0.05 / FIG_W, y, group, transform=lab_tr, ha="left", va="center", fontsize=style.FS,
                     fontstyle="italic", color=(style.WARN_INK if warn else style.GRAY))
    for ax in (ax_a[1], ax_b):
        plt.setp(ax.get_yticklabels(), visible=False)

    # (a) messages per market, mean over the arm's 5 markets: private between sellers, then public
    for ax, (col, head, color, ink) in zip(ax_a, TALK):
        mean_msgs = mk.groupby("arm")[col].mean()
        for _, arm, y in rows:
            m = mean_msgs[arm]
            ax.barh(y, m, height=BAR_H, color=color, lw=0, zorder=2)
            label = f"{m:.1f}" if m > 0 else "0"
            printed[f"{head} {arm}"] = label
            if m > 0:
                ax.text(m - 3, y, label, ha="right", va="center", fontsize=style.FS, color=ink, zorder=3)
            else:
                ax.text(3, y, label, ha="left", va="center", fontsize=style.FS, color="black", zorder=3)
        ax.set_xlim(0, MSG_MAX)
        ax.set_xticks([0, 50, 100])
        fig.text((A_X0 + A_W / 2 + (A_W + A_GAP) * (head == "Public")) / FIG_W, Y_HEAD / FIG_H, head,
                 ha="center", va="center", fontsize=style.FS_HEAD)

    # (b) last-third ask index per market
    base = mk.query("arm == 'Base'")["ask_index"]
    ax_b.axvspan(base.min(), base.max(), color=style.BASE_BAND, alpha=style.BASE_BAND_ALPHA, lw=0, zorder=0.2)
    printed["Base range"] = (round(base.min(), 2), round(base.max(), 2))
    for r in style.REF_LINES:
        ax_b.axvline(r["index"], color=style.GRAY, ls=r["ls"], lw=r["lw"], zorder=0.5)
        if "label" in r:        # at the line's top end, just left of it, in the row of the "Base range" label
            ax_b.text(r["index"] - 0.012, heads[0][1], r["label"], ha="right", va="center", fontsize=style.FS,
                      color=style.GRAY)
    for _, arm, y in rows:
        sub = mk[mk["arm"] == arm].sort_values("seed")
        if list(sub["seed"]) != [0, 1, 2, 3, 4]:
            raise ValueError(f"{arm}: expected seeds 0 to 4")
        for _, r in sub.iterrows():
            yy = y + (r["seed"] - 2) * SEED_DY
            ax_b.plot([r["ask_index"]], [yy], ls="none", marker="o", ms=MS, mew=1.0, mec=blue,
                      mfc=(blue if r["passed"] else "white"), zorder=3)
        ax_b.plot([sub["ask_index"].mean()] * 2, [y - 0.4, y + 0.4], color="black", lw=1.6,
                  solid_capstyle="butt", zorder=4)
        printed[f"ask mean {arm}"] = round(sub["ask_index"].mean(), 3)
        printed[f"passed {arm}"] = int(sub["passed"].sum())
    ax_b.set_xlim(-0.04, 0.83)
    ax_b.set_xticks([0, 0.25, 0.5, 0.75], ["0\n$90", "0.25", "0.5\n$95", "0.75\n$97.50"])
    ax_b.text(base.min() + 0.012, heads[0][1], "Base range", ha="left", va="center", fontsize=style.FS,
              color=style.GRAY)

    # panel letters and titles
    for letter, x_in, title in (("a", 0.05, "Messages per market"), ("b", B_X0 - 0.30, "Ask index, hours 11 to 15")):
        fig.text(x_in / FIG_W, Y_TITLE / FIG_H, letter, fontsize=style.FS_TITLE, fontweight="bold", ha="left",
                 va="center")
        fig.text((x_in + 0.2) / FIG_W, Y_TITLE / FIG_H, title, fontsize=style.FS_TITLE, ha="left", va="center")

    handles = [Line2D([], [], ls="none", marker="o", ms=MS, mew=1.0, mec=blue, mfc=blue),
               Line2D([], [], ls="none", marker="o", ms=MS, mew=1.0, mec=blue, mfc="white"),
               Line2D([], [], ls="none", marker="|", ms=8, mew=1.6, color="black")]
    fig.legend(handles, ["Meets the criterion", "Does not meet it", "Arm mean"], loc="center right",
               ncol=3, frameon=False, bbox_to_anchor=(B_X1 / FIG_W, Y_HEAD / FIG_H),
               handletextpad=0.2, columnspacing=1.0, handlelength=1.2, borderpad=0, borderaxespad=0)
    return fig, printed


def main():
    fig, printed = build()
    style.save(fig, "fig5_warning.png", max_h_in=3.3)
    for k, v in printed.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
