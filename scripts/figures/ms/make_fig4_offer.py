"""Body Figure 4: responses to the undercover offer.

Adapted from M.S.'s fig1_offer variant with two GPT-4.1 rows (ref origin/mert_fig1_offer_gpt41, commit 44dcdcc:
mert_sprint/figures_extra/fig1_offer_gpt41/make_fig1_offer_gpt41.py) and its base script
mert_sprint/report_ms/scripts/figures/make_fig1_offer.py with lib/style.py and lib/load.py (ref
origin/mert_sprint_sync_oct25), all by M.S. Same panels, measures, rows, colors and bar-label rule; re-laid for
print at 6.5 x 3.8 in with panels a and b side by side and every text at least 8 pt (his figure was 6.5 x 7.3 in at
12 to 16 pt). Changes: shorter panel titles and headers ("(judge)" for his "(judge label)"), the GPT-4.1 precedent
row of panel b sits on the warning band like the warning arms of panel a, and the data are read from the committed
CSVs under report/data/ (his copies are identical apart from line endings).

(a) Per Gemini arm, sellers out of 20 who reported seat 5 (distinct sellers: table3_extra.csv reported_seat5 summed
    over the arm's 5 markets) and who were judge-coded as echoing any peer's price proposal (outcomes_by_arm.csv
    verbal_accept_rate x 20). The judge label is not specific to seat 5, so Base reaches 20 with no offer. The five
    arms with the warning sit on the warning band.
(b) The plain $96 offer (arm D) to three seller families, plus two GPT-4.1 variants: reported seat 5
    (report_is_scripted_seat_rate), echoed a peer's price (verbal_accept_rate) and rejected a proposal
    (verbal_reject_rate), each as a count of sellers; the last two are judge labels.
      Gemini D: report/data/dg/outcomes_by_arm.csv row D (n = 20)
      GPT-4.1 D: report/data/dg_gpt41/outcomes_by_arm.csv row D (n = 12)
      GPT-4.1 under warning and precedent: same file, row F (n = 12)
      GPT-4.1 offered $99: report/data/dg_gpt41_99/outcomes.csv rows arm == D99 (n = 12): reported_seat5; the judge
        was not run on D99, so its two judge columns show the hand read instead, in italics: rose_ge_1 (sellers who
        raised their ask by $1 or more in hours 4 to 6; 3 seed-0 sellers posted $99 placeholder asks in hours 11
        to 15, so the label names the threshold and the hours) and tone_all_msgs (hand-coded tone of every message
        to seat 5)
      Claude Haiku 5.5 D: report/data/dg_haiku/outcomes_by_arm.csv row D (n = 12)
    Bar length is the share of sellers.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/ms/make_fig4_offer.py
Output: report/figures/fig4_offer.png (6.5 x 3.8 in, 300 dpi)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

import load  # noqa: E402
import style  # noqa: E402

FIG_W, FIG_H = style.SLOT_IN, 3.8
Y0, Y1 = 0.06, 3.0                 # bottom and top of the bar columns of both panels, inches
Y_TITLE = 3.66                     # center of the panel titles
# panel (a): arm labels end at A_LAB, two columns from A_X0 to A_X1
A_LAB, A_X0, A_X1, A_GAP = 0.60, 0.68, 2.92, 0.22
# panel (b): row labels end at B_LAB, three columns from B_X0 to B_X1
B_LEFT, B_LAB, B_X0, B_X1, B_GAP = 3.16, 3.80, 3.88, 6.44, 0.13
BAR_A, BAR_B = 0.62, 0.40          # bar heights, row units
FULL_COLOR = "#D9D9D9"             # the faint line at 100 % of sellers
HEAD_A = {"reported": "Reported seat 5", "agreed": "Echoed a peer's\nprice (judge)"}
HEAD_B = {"reported": "Reported\nseat 5", "agreed": "Echoed a\npeer's price\n(judge)",
          "rejected": "Rejected a\nproposal\n(judge)"}


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


def _judge_row(folder, arm, family, label):
    o = load.daniel_outcomes(folder).loc[arm]
    n = int(o["n_seller_episodes"])
    return {"family": family, "label": label, "n": n, "key": f"{folder}:{arm}",
            "reported": load.count(o["report_is_scripted_seat_rate"], n),
            "agreed": load.count(o["verbal_accept_rate"], n),
            "rejected": load.count(o["verbal_reject_rate"], n)}


def panel_b_data():
    d = load.gpt41_99()
    return [
        _judge_row("dg", "D", "gemini", "Gemini\nn = 20"),
        _judge_row("dg_gpt41", "D", "gpt41", "GPT-4.1\nn = 12"),
        dict(_judge_row("dg_gpt41", "F", "gpt41", "GPT-4.1,\nprecedent"), warn=True),
        {"family": "gpt41", "label": "GPT-4.1,\noffer $99", "n": d["n"], "key": "dg_gpt41_99:D99",
         "reported": d["reported"], "d99": d},
        _judge_row("dg_haiku", "D", "haiku", "Haiku 5.5\nn = 12"),
    ]


def columns(fig, k, x0, x1, gap, spans):
    """k equal bar columns between x0 and x1 (inches), each an axes on the share-of-sellers scale 0 to 1, with a
    zero line and a faint 100 % line over each (top, bottom) data span. M.S.'s helper, positions in inches."""
    w = (x1 - x0 - gap * (k - 1)) / k
    axes = []
    for i in range(k):
        ax = fig.add_axes([(x0 + i * (w + gap)) / FIG_W, Y0 / FIG_H, w / FIG_W, (Y1 - Y0) / FIG_H],
                          sharey=(axes[0] if axes else None))
        ax.patch.set_alpha(0.0)
        ax.set_xlim(0, 1.0)
        ax.set_xticks([])
        for side in ("left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.tick_params(axis="y", length=0)
        for top, bottom in spans:
            ax.plot([0, 0], [top, bottom], color="black", lw=0.7, zorder=1, solid_capstyle="butt")
            ax.plot([1, 1], [top, bottom], color=FULL_COLOR, lw=0.7, zorder=0.5, solid_capstyle="butt")
        axes.append(ax)
    for ax in axes[1:]:
        plt.setp(ax.get_yticklabels(), visible=False)
    return axes, w


def bar(ax, w_in, y, count, n, color, text, height):
    """One bar of length count/n, labelled with text: inside when it fits, else just outside (M.S.'s rule,
    scaled to 8.5 pt)."""
    share = count / n
    ax.barh(y, share, height=height, color=color, lw=0, zorder=2)
    fits = share * w_in > 0.054 * len(text) + 0.08
    pad = 0.03 / w_in
    if fits:
        ax.text(share - pad, y, text, ha="right", va="center", fontsize=style.FS, color=style.ink_on(color),
                zorder=3)
    else:
        ax.text(share + pad, y, text, ha="left", va="center", fontsize=style.FS, color="black", zorder=3)


def head(ax, text):
    ax.text(0.0, 1.0, text, transform=ax.transAxes, ha="left", va="bottom", fontsize=style.FS,
            linespacing=1.1)


def build():
    style.setup()
    a_data, b_rows = panel_a_data(), panel_b_data()
    rows, heads, (w0, w1) = style.arm_rows()
    blue = style.COLOR["gemini"]
    printed = {}
    fig = plt.figure(figsize=(FIG_W, FIG_H))

    # (a) Gemini arms, two measures
    spans = []
    for group, _ in style.ARM_GROUPS:
        ys = [y for g, _, y in rows if g == group]
        spans.append((ys[0] - 0.5, ys[-1] + 0.5))
    axa, wa = columns(fig, 2, A_X0, A_X1, A_GAP, spans)
    axa[0].set_ylim(rows[-1][2] + 0.5, 0.0)
    style.row_band(fig, axa[0], w0, w1, style.WARN_BAND, x0=0.0, x1=(A_X1 + 0.08) / FIG_W)
    axa[0].set_yticks([y for _, _, y in rows], [arm for _, arm, _ in rows])
    axa[0].tick_params(axis="y", pad=(A_X0 - A_LAB) * 72)
    lab_tr = blended_transform_factory(fig.transFigure, axa[0].transData)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        axa[0].text(0.05 / FIG_W, y, group, transform=lab_tr, ha="left", va="center", fontsize=style.FS,
                    fontstyle="italic", color=(style.WARN_INK if warn else style.GRAY))
    for ax, kind in zip(axa, ("reported", "agreed")):
        for _, arm, y in rows:
            d = a_data[arm]
            bar(ax, wa, y, d[kind], d["n"], blue, str(d[kind]), BAR_A)
            printed[f"a {kind} {arm}"] = f"{d[kind]} of {d['n']}"
            if kind == "reported" and arm in style.NO_OFFER:
                ax.text(0.17, y, "no offer", ha="left", va="center", fontsize=style.FS, fontstyle="italic",
                        color=style.GRAY)
        head(ax, HEAD_A[kind])
    fig.text(0.05 / FIG_W, Y_TITLE / FIG_H, "a", fontsize=style.FS_TITLE, fontweight="bold", ha="left",
             va="center")
    fig.text(0.25 / FIG_W, Y_TITLE / FIG_H, "Gemini sellers by arm, of 20", fontsize=style.FS_TITLE, ha="left",
             va="center")

    # (b) the plain offer to three seller families, and two GPT-4.1 variants
    nb = len(b_rows)
    axb, wb = columns(fig, 3, B_X0, B_X1, B_GAP, [(0.0, float(nb))])
    yb = [i + 0.5 for i in range(nb)]
    axb[0].set_ylim(float(nb), 0.0)
    axb[0].set_yticks(yb, [r["label"] for r in b_rows])
    axb[0].tick_params(axis="y", pad=(B_X0 - B_LAB) * 72)
    plt.setp(axb[0].get_yticklabels(), linespacing=1.1)
    for r, y in zip(b_rows, yb):
        if r.get("warn"):
            tr = blended_transform_factory(fig.transFigure, axb[0].transData)
            fig.patches.append(Rectangle((B_LEFT / FIG_W, y - 0.5), (B_X1 + 0.05 - B_LEFT) / FIG_W, 1.0,
                                         transform=tr, facecolor=style.WARN_BAND, edgecolor="none", zorder=-1))
    for ax, kind in zip(axb, ("reported", "agreed", "rejected")):
        for r, y in zip(b_rows, yb):
            if "d99" in r and kind != "reported":
                d = r["d99"]
                text = (f"{d['rose']} of {d['n']}\nraised ≥ $1\nin hours 4-6\n(hand read)" if kind == "agreed"
                        else f"{d['declining']} of {d['msgs']}\ndeclined\n(hand read)")
                ax.text(0.04, y, text, ha="left", va="center", fontsize=style.FS, fontstyle="italic",
                        color="black", linespacing=1.1)
                printed[f"b {kind} {r['key']}"] = text.replace("\n", " ")
                continue
            bar(ax, wb, y, r[kind], r["n"], style.COLOR[r["family"]], f"{r[kind]} of {r['n']}", BAR_B)
            printed[f"b {kind} {r['key']}"] = f"{r[kind]} of {r['n']}"
        head(ax, HEAD_B[kind])
    fig.text((B_LEFT) / FIG_W, Y_TITLE / FIG_H, "b", fontsize=style.FS_TITLE, fontweight="bold", ha="left",
             va="center")
    fig.text((B_LEFT + 0.2) / FIG_W, Y_TITLE / FIG_H, "The offer to three seller families",
             fontsize=style.FS_TITLE, ha="left", va="center")
    return fig, printed


def main():
    fig, printed = build()
    style.save(fig, "fig4_offer.png", max_h_in=3.8)
    for k, v in printed.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
