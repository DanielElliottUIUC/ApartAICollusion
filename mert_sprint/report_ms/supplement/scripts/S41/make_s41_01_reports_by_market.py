"""S41_01. Sellers whose first report named seat 5, market by market (10 Gemini arms x 5 seeds).

Data: supplement/data/daniel/dg/outcomes.csv, market_by_run.csv, table3_extra.csv.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 5.05
NAME = "S41_01_reports_by_market.png"


def make():
    style.setup()
    o = L.gemini_sellers()
    rows, heads, (w0, w1) = style.arm_rows(head=0.9)
    cnt = o.groupby(["arm", "seed"]).s5.sum()
    ever = o.groupby(["arm", "seed"]).ever_s5.sum()
    tot = o.groupby("arm").s5.sum()
    blue = style.COLOR["gemini"]

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([1.45 / FIG_W, 0.1 / FIG_H, 5.0 / FIG_W, 4.55 / FIG_H])
    ax.patch.set_alpha(0)
    ncol = 5
    cw = 0.8                                   # cell width in data units (seed columns at 0..4)
    ax.set_xlim(-0.5, -0.5 + 5.0 / 0.62)      # one data unit = 0.62 in
    ax.set_ylim(rows[-1][2] + 0.5, -0.55)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([y for _, _, y in rows], [arm for _, arm, _ in rows])
    ax.tick_params(axis="y", length=0, pad=6)
    style.row_band(fig, ax, w0, w1, style.WARN_BAND)
    for group, y in heads:
        warn = group != style.ARM_GROUPS[0][0]
        ax.text(-0.5 - 1.15, y, group, ha="left", va="center", fontsize=12, fontstyle="italic",
                color=(style.WARN_INK if warn else style.GRAY), clip_on=False)
    later = []
    for _, arm, y in rows:
        for seed in range(5):
            k = int(cnt[(arm, seed)])
            face = "white" if k == 0 else style.tint(blue, 1 - k / 4 * 0.85)
            ax.add_patch(Rectangle((seed - cw / 2, y - 0.4), cw, 0.8, facecolor=face,
                                   edgecolor=style.LIGHT, lw=0.6))
            extra = int(ever[(arm, seed)]) - k
            txt = f"{k}" + ("*" * extra)
            if extra:
                later.append((arm, seed, extra))
            ink = "white" if k >= 3 else ("black" if k > 0 else style.GRAY)
            ax.text(seed, y, txt, ha="center", va="center", fontsize=12, color=ink)
        ax.text(ncol - 0.25, y, f"{int(tot[arm])} of 20", ha="left", va="center", fontsize=12)
        if arm in style.NO_OFFER:
            ax.text(ncol + 1.25, y, "no offer", ha="left", va="center", fontsize=12, fontstyle="italic",
                    color=style.GRAY)
    top = -0.05
    for seed in range(5):
        ax.text(seed, top, f"{seed}", ha="center", va="bottom", fontsize=12)
    ax.text(-0.62, top, "seed", ha="right", va="bottom", fontsize=12)
    ax.text(ncol - 0.25, top, "arm total", ha="left", va="bottom", fontsize=12)
    fig.text(0.06 / FIG_W, (FIG_H - 0.08) / FIG_H, "Sellers whose first report named seat 5, of 4 per market",
             fontsize=16, ha="left", va="top")
    L.save(fig, NAME)

    # numbers for the text
    def per_seed(arm):
        return ", ".join(str(int(cnt[(arm, s)])) for s in range(5))
    plain = ["D", "D-hb", "E", "F", "F-sham"]          # seat 5's plain offer text
    full_first = sum(int(cnt[(a, s)] == 4) for a in plain for s in range(5))
    full_ever = sum(int(ever[(a, s)] == 4) for a in plain for s in range(5))
    p, hits, total = L.exact_perm_p([cnt[("Base", s)] for s in range(5)], [cnt[("D", s)] for s in range(5)])
    later_txt = " and ".join((f"{e} sellers" if e > 1 else "one seller") + f" in {a} seed {s}" for a, s, e in later)
    return {
        "id": "S41.1",
        "title": "Reports of seat 5, market by market",
        "file": NAME,
        "caption": (
            "Each cell is one market of D.E.'s Gemini 3.8 Flash study and gives how many of its 4 LLM sellers "
            "filed a first report that named seat 5. Columns are seeds 0 to 4, rows are the ten arms, and the "
            "shaded rows carry the warning in the prompt. Darker cells hold more reporters. The right column sums "
            "each arm over its 20 sellers. An asterisk marks a seller whose first report named a peer and who "
            f"reported seat 5 later, which happened for {later_txt}. Arms with no offer had a placebo note from "
            "seat 5."
        ),
        "shows": (
            f"Where seat 5 made the plain offer (D, D-hb, E, F and F-sham), all four sellers reported it in "
            f"{full_first} of the 25 markets by first report, and in {full_ever} of 25 when the later reports are "
            f"counted. The two arms with the human-seller plea are the exception. D-hs splits into markets where "
            f"all or most sellers reported and markets where almost none did ({per_seed('D-hs')} by seed), and "
            f"D-hsb has a single reporter in most markets ({per_seed('D-hsb')}). Reports cluster by market, which "
            f"is why the market, not the seller, is the unit of analysis. Base against D gives an exact two-sided "
            f"permutation p of {p:.3f} ({hits} of {total} relabellings of the 10 markets), the smallest value "
            f"5 against 5 markets allow. The figure shows reporting only, not prices."
        ),
        "source": "supplement/data/daniel/dg/outcomes.csv (report_is_scripted_seat), market_by_run.csv "
                  "(scripted_seats), table3_extra.csv (reported_seat5, for the asterisks).",
    }


if __name__ == "__main__":
    print(make())
