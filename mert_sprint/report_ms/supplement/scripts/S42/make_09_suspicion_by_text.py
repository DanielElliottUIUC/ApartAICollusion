"""Figure S42.9: suspicion of collusion follows the offer; suspicion of a test follows the precedent text.

Sellers (of 20 per arm) whose episode D.E.'s judge labelled suspects_collusion (a) and suspects_test (b), from
outcomes.csv (true if any judged hour from hour 4 on is true). Arms are grouped by the text in the seller prompt
(nothing, the warning, the warning with an unrelated history of the same length, the warning with the precedent).
Solid bars: seat 5 makes an offer at hour 3. Pale bars: seat 5 sends a placebo note.
Output: supplement/figures/S42/S42_09_suspicion_by_text.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.transforms import blended_transform_factory

import s42lib as L
from s42lib import style

FILE = "S42_09_suspicion_by_text.png"
FIG_H = 5.0
GROUPS = [("No warning", ["Base", "D", "D-hs", "D-hb", "D-hsb"]),
          ("Warning", ["G-warn", "E"]),
          ("Warning and sham history", ["F-sham"]),
          ("Warning and precedent", ["G-prec", "F"])]
PANELS = [("suspects_collusion", "Suspects collusion"), ("suspects_test", "Suspects a test")]


def rows(head=0.8):
    out, heads, y = [], [], 0.0
    for g, arms in GROUPS:
        heads.append((g, y + head / 2))
        y += head
        for a in arms:
            out.append((g, a, y + 0.5))
            y += 1.0
    return out, heads, y


def make():
    style.setup()
    o = L.sellers()
    counts = {lab: o.groupby("arm")[lab].sum().astype(int) for lab, _ in PANELS}
    W = style.SLOT_IN
    fig = plt.figure(figsize=(W, FIG_H))
    y0, y1 = 0.80, FIG_H - 0.80
    xs = [(1.02, 3.40), (3.92, 6.30)]
    axes = [fig.add_axes([a / W, y0 / FIG_H, (b - a) / W, (y1 - y0) / FIG_H]) for a, b in xs]
    rr, heads, y_end = rows()
    for i, (ax, (lab, title)) in enumerate(zip(axes, PANELS)):
        ax.patch.set_alpha(0.0)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        for _, arm, y in rr:
            n = counts[lab][arm]
            offer = arm not in L.NO_OFFER
            ax.barh(y, n, height=0.66, color=(L.BLUE if offer else style.tint(L.BLUE, 0.75)),
                    edgecolor=L.BLUE, lw=(1.0 if n else 0), zorder=2)
            ax.text(n + 0.5, y, str(n), ha="left", va="center", fontsize=12, zorder=3)
        ax.set_ylim(y_end + 0.1, 0.0)
        ax.set_xlim(0, 23)
        ax.set_xticks([0, 10, 20])
        ax.set_xlabel("Sellers, of 20")
        ax.set_title(title, pad=6)
        ax.set_yticks([y for *_, y in rr], ([a for _, a, _ in rr] if i == 0 else []))
        fig.text((xs[i][0] - (0.96 if i == 0 else 0.30)) / W, (y1 + 0.08) / FIG_H, "ab"[i], fontsize=16,
                 fontweight="bold", ha="left", va="bottom")
    tr = blended_transform_factory(fig.transFigure, axes[0].transData)
    for g, y in heads:
        warn = g != "No warning"
        axes[0].text(0.06 / W, y, g, transform=tr, ha="left", va="center", fontsize=12, fontstyle="italic",
                     color=(style.WARN_INK if warn else style.GRAY))
    # warning band behind every group but the first
    first_warn = [y for g, y in heads if g != "No warning"][0] - 0.4
    style.row_band(fig, axes[0], first_warn, y_end + 0.1, style.WARN_BAND)
    fig.legend([Patch(facecolor=L.BLUE, edgecolor=L.BLUE), Patch(facecolor=style.tint(L.BLUE, 0.75),
                                                                 edgecolor=L.BLUE)],
               ["Offer at hour 3", "Placebo note"], loc="upper center", ncol=2, frameon=False,
               bbox_to_anchor=(0.5, 1.0), handletextpad=0.4, columnspacing=1.5)
    L.save(fig, FILE)
    plt.close(fig)
    return counts


def entry():
    c = make()
    o = L.sellers()
    per_mkt = {lab: o.groupby(["arm", "run_id"])[lab].sum() for lab, _ in PANELS}

    def p(lab, a, b):
        return L.fmt_p(L.perm_p(per_mkt[lab][a].values, per_mkt[lab][b].values))

    def both(p1, p2):
        return f"p = {p1} for both" if p1 == p2 else f"p = {p1} and {p2}"

    sc, st = c["suspects_collusion"], c["suspects_test"]
    return {
        "title": "Suspicion of collusion follows the offer; suspicion of a test follows the precedent text",
        "file": FILE,
        "caption": (
            "Gemini 3.8 Flash sellers, out of 20 per arm, whose episode D.E.'s judge labelled as (a) suspecting "
            "collusion and (b) suspecting a test or trap, at any hour from hour 4 on. Arms are grouped by the text "
            "added to the seller prompt from hour 1, which is nothing, the warning, the warning with an unrelated "
            "history of the same length (sham), or the warning with the precedent. Solid bars: seat 5 offers to "
            "hold asks at $96 at hour 3. Pale bars: seat 5 sends a placebo note. The pale band marks the arms "
            "with the warning."),
        "shows": (
            f"Within each text group, suspicion of collusion goes with the offer (E {sc['E']} against G-warn "
            f"{sc['G-warn']}, F {sc['F']} against G-prec {sc['G-prec']}, {both(p('suspects_collusion', 'E', 'G-warn'), p('suspects_collusion', 'F', 'G-prec'))}). Suspicion of a test goes with the precedent instead. "
            f"It reaches {st['G-prec']} of 20 in G-prec and {st['F']} in F, against {st['F-sham']} in F-sham, "
            f"{st['E']} in E and {st['G-warn']} in G-warn (F against F-sham and G-prec against G-warn, "
            f"{both(p('suspects_test', 'F', 'F-sham'), p('suspects_test', 'G-prec', 'G-warn'))}, exact permutation "
            f"over 5 against 5 markets). The test label therefore measures vigilance prompted by the precedent text, not "
            f"detection of seat 5."),
        "source": f"`{L.SRC}/outcomes.csv` (suspects_collusion, suspects_test). "
                  f"Script: `supplement/scripts/S42/make_09_suspicion_by_text.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
