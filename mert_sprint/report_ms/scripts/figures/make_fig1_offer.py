"""Figure 1: responses to the undercover offer (Daniel's study).

(a) Per Gemini arm, sellers out of 20 who reported seat 5 (distinct sellers, from his run logs:
    table3_extra.csv reported_seat5 summed over the 5 markets) and who were judge-coded as echoing any
    peer's price proposal (outcomes_by_arm.csv verbal_accept_rate x 20). The judge label is not specific to
    seat 5, so Base reaches 20 with no offer. Rows in the shared arm order of Figure 2; the five arms with the
    warning sit on the warning band.
(b) The same plain offer (arm D) to three seller families: reported seat 5 (report_is_scripted_seat_rate),
    echoed a peer's price (verbal_accept_rate) and rejected a proposal (verbal_reject_rate), each as a count
    of sellers. The last two are judge labels, and both headers say so. Gemini n = 20, GPT-4.1 n = 12,
    Claude Haiku 5.5 n = 12. Bar length is the share of sellers.
One column per measure, so no legend is needed; every bar carries its count.
Slot: full width, 6.5 in.  Output: report/figures/fig1_offer.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

import load
import style

FAMILIES = [("gemini", "dg", "Gemini"), ("gpt41", "dg_gpt41", "GPT-4.1"), ("haiku", "dg_haiku", "Haiku 5.5")]
JUDGE = "(judge label)"
HEAD = {"reported": "Reported seat 5", "agreed": f"Echoed a peer's price\n{JUDGE}"}
HEAD_B = {"reported": "Reported\nseat 5", "agreed": f"Echoed a\npeer's price\n{JUDGE}",   # (b) has three
          "rejected": f"Rejected a\nproposal\n{JUDGE}"}                             # columns, so headers wrap

FIG_W, FIG_H = style.SLOT_IN, 6.43
LAB_X = 0.92                                   # right edge of the row labels, inches
X0, X1 = 1.06, 6.40                            # left and right edge of the bar columns, inches
GAP = 0.34                                     # gap between columns, inches
A_Y0, A_Y1 = 2.79, 5.51                       # panel (a), inches from the bottom
B_Y0, B_Y1 = 0.10, 1.42                        # panel (b)
BAR_H = 0.64
FULL_COLOR = "#D9D9D9"                         # the faint line at 100 % of sellers


def panel_a_data():
    mk = load.daniel_markets()
    reported = mk.groupby("arm")["reported_seat5"].sum()
    out = load.daniel_outcomes("dg")
    data = {}
    for _, arm, _ in style.arm_rows()[0]:
        n = int(out.loc[arm, "n_seller_episodes"])
        data[arm] = {"n": n, "reported": int(reported[arm]),
                     "agreed": load.count(out.loc[arm, "verbal_accept_rate"], n)}
    return data


def panel_b_data():
    rows = []
    for fam, folder, short in FAMILIES:
        o = load.daniel_outcomes(folder).loc["D"]
        n = int(o["n_seller_episodes"])
        rows.append({"family": fam, "short": short, "n": n,
                     "reported": load.count(o["report_is_scripted_seat_rate"], n),
                     "agreed": load.count(o["verbal_accept_rate"], n),
                     "rejected": load.count(o["verbal_reject_rate"], n)})
    return rows


def columns(fig, k, y0, y1, spans):
    """k equal bar columns between X0 and X1 (inches), each an axes on the share-of-sellers scale 0 to 1.
    The zero line and the faint 100 % line are drawn over each (top, bottom) data span in spans only,
    so group headers between spans stay clear."""
    w = (X1 - X0 - GAP * (k - 1)) / k
    axes = []
    for i in range(k):
        ax = fig.add_axes([(X0 + i * (w + GAP)) / FIG_W, y0 / FIG_H, w / FIG_W, (y1 - y0) / FIG_H],
                          sharey=(axes[0] if axes else None))
        ax.patch.set_alpha(0.0)
        ax.set_xlim(0, 1.0)
        ax.set_xticks([])
        for side in ("left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="y", length=0)
        for top, bottom in spans:
            ax.plot([0, 0], [top, bottom], color="black", lw=0.9, zorder=1, solid_capstyle="butt")
            ax.plot([1, 1], [top, bottom], color=FULL_COLOR, lw=0.9, zorder=0.5, solid_capstyle="butt")
        axes.append(ax)
    for ax in axes[1:]:
        plt.setp(ax.get_yticklabels(), visible=False)
    return axes, w


def ink_on(color):
    """White text on dark bars, black on light ones (relative luminance above 0.3)."""
    r, g, b = (c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in mpl.colors.to_rgb(color))
    return "black" if 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.3 else "white"


def bar(ax, w_in, y, count, n, color, text):
    """One bar of length count/n, labelled with text: inside when it fits, else just outside."""
    share = count / n
    ax.barh(y, share, height=BAR_H, color=color, lw=0, zorder=2)
    fits = share * w_in > 0.075 * len(text) + 0.12
    if fits:
        ax.text(share - 0.03, y, text, ha="right", va="center", fontsize=12, color=ink_on(color), zorder=3)
    else:
        ax.text(share + 0.03, y, text, ha="left", va="center", fontsize=12, color="black", zorder=3)


def head(ax, text):
    ax.text(0.0, 1.0, text, transform=ax.transAxes, ha="left", va="bottom", fontsize=14)


def main():
    style.setup()
    a_data, b_rows = panel_a_data(), panel_b_data()
    rows, heads, (w0, w1) = style.arm_rows()
    blue = style.COLOR["gemini"]

    fig = plt.figure(figsize=(FIG_W, FIG_H))

    # (a) Gemini arms, two measures
    spans = []
    for group, _ in style.ARM_GROUPS:
        ys = [y for g, _, y in rows if g == group]
        spans.append((ys[0] - 0.5, ys[-1] + 0.5))
    axa, wa = columns(fig, 2, A_Y0, A_Y1, spans)
    axa[0].set_ylim(rows[-1][2] + 0.5, 0.0)
    style.row_band(fig, axa[0], w0, w1, style.WARN_BAND)
    axa[0].set_yticks([y for _, _, y in rows], [arm for _, arm, _ in rows])
    axa[0].tick_params(axis="y", pad=(X0 - LAB_X) * 72)
    lab_tr = blended_transform_factory(fig.transFigure, axa[0].transData)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        axa[0].text(0.06 / FIG_W, y, group, transform=lab_tr, ha="left", va="center", fontsize=12,
                    fontstyle="italic", color=(style.WARN_INK if warn else style.GRAY))
    for ax, kind in zip(axa, ("reported", "agreed")):
        for _, arm, y in rows:
            d = a_data[arm]
            bar(ax, wa, y, d[kind], d["n"], blue, str(d[kind]))
            if kind == "reported" and arm in style.NO_OFFER:
                ax.text(0.11, y, "no offer", ha="left", va="center", fontsize=12, fontstyle="italic",
                        color=style.GRAY)
        head(ax, HEAD[kind])
    fig.text(0.06 / FIG_W, (A_Y1 + 0.64) / FIG_H, "a", fontsize=16, fontweight="bold", ha="left",
             va="bottom")
    fig.text(0.40 / FIG_W, (A_Y1 + 0.64) / FIG_H, "Gemini 3.8 Flash sellers by arm, of 20", fontsize=16,
             ha="left", va="bottom")

    # (b) the plain offer to three seller families, three measures
    axb, wb = columns(fig, 3, B_Y0, B_Y1, [(0.0, 3.0)])
    yb = [0.5, 1.5, 2.5]
    axb[0].set_ylim(3.0, 0.0)
    axb[0].set_yticks(yb, [f"{r['short']}\nn = {r['n']}" for r in b_rows])
    axb[0].tick_params(axis="y", pad=(X0 - LAB_X) * 72)
    for ax, kind in zip(axb, ("reported", "agreed", "rejected")):
        for r, y in zip(b_rows, yb):
            bar(ax, wb, y, r[kind], r["n"], style.COLOR[r["family"]], f"{r[kind]} of {r['n']}")
        head(ax, HEAD_B[kind])
    fig.text(0.06 / FIG_W, (B_Y1 + 0.90) / FIG_H, "b", fontsize=16, fontweight="bold", ha="left",
             va="bottom")
    fig.text(0.40 / FIG_W, (B_Y1 + 0.90) / FIG_H, "Plain offer (arm D) to three seller families",
             fontsize=16, ha="left", va="bottom")
    style.save(fig, "fig1_offer.png")


if __name__ == "__main__":
    main()
