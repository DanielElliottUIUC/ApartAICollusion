"""Figure S42.8: sellers ever labelled as agreeing, and as suspecting collusion, by hour and arm.

outcomes.csv gives, per seller-episode, the first hour from hour 4 on in which D.E.'s judge (Claude Haiku 5.5)
marked verbal_accept or suspects_collusion (verbal_accept_hour, suspects_collusion_hour). The curves count, for
each hour h, the sellers of the arm (of 20) whose first such hour is h or earlier. Hours before 4 are not
counted in that table, so the curves start at hour 4. The labels are binary; this is an analog of the
coordination-score-by-round figure of Agrawal et al. (2025), not their 1-to-4 score.
Output: supplement/figures/S42/S42_08_labels_by_hour.png
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

FILE = "S42_08_labels_by_hour.png"
FIG_H = 5.3
HRS = list(range(4, 16))
LABELS = [("verbal_accept", L.BLUE, 2.2, "Agrees with a peer's price"),
          ("suspects_collusion", "black", 1.5, "Suspects collusion")]


def curves(o):
    out = {}
    for lab, *_ in LABELS:
        for arm in L.ARMS:
            sub = o[o["arm"] == arm]
            first = sub[f"{lab}_hour"].where(sub[lab])
            if (first.dropna() < 4).any():
                raise ValueError("first-true hours must be 4 or later")
            out[lab, arm] = np.array([int((first <= h).sum()) for h in HRS])
            if out[lab, arm][-1] != int(sub[lab].sum()):
                raise ValueError(f"{lab} {arm}: curve end differs from the label count")
    return out


def make():
    style.setup()
    o = L.sellers()
    c = curves(o)
    fig = plt.figure(figsize=(style.SLOT_IN, FIG_H))
    axes = L.small_multiples(fig, left=0.86, right=0.14, bottom=0.66, top=0.80, wgap=0.10, hgap=0.56)
    for r, (_, arms) in enumerate(style.ARM_GROUPS):
        for col, arm in enumerate(arms):
            ax = axes[r][col]
            if arm in L.WARN:
                L.warn_face(ax)
            for lab, color, lw, _ in LABELS:
                ax.step(HRS, c[lab, arm], where="post", color=color, lw=lw, zorder=3 if color == "black" else 2,
                        clip_on=False)
            ax.set_xlim(3.5, 15.5)
            ax.set_ylim(-0.8, 21)
            ax.set_xticks([5, 10, 15])
            ax.set_yticks([0, 10, 20])
            ax.set_yticklabels(["0", "10", "20"] if col == 0 else [])
            ax.set_title(arm, pad=4)
        pos = axes[r][0].get_position()
        fig.text(0.06 / style.SLOT_IN, pos.y1 + 0.04 / FIG_H, "ab"[r], fontsize=16, fontweight="bold", ha="left",
                 va="bottom")
        fig.text(0.10 / style.SLOT_IN, (pos.y0 + pos.y1) / 2, "Sellers, of 20", rotation=90, ha="left",
                 va="center", fontsize=14)
    x_mid = (axes[0][0].get_position().x0 + axes[0][4].get_position().x1) / 2
    fig.text(x_mid, 0.10 / FIG_H, "Hour", ha="center", va="bottom", fontsize=14)
    handles = [Line2D([], [], color=col, lw=lw) for _, col, lw, _ in LABELS] + \
              [Patch(facecolor=style.WARN_BAND, edgecolor=style.LIGHT)]
    fig.legend(handles, [t for *_, t in LABELS] + ["Warning"], loc="upper center", ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.0), handlelength=1.6, handletextpad=0.4, columnspacing=1.0)
    L.save(fig, FILE)
    plt.close(fig)
    return c


def entry():
    c = make()
    nowarn = style.ARM_GROUPS[0][1]
    acc4 = [c["verbal_accept", a][0] for a in nowarn]
    acc15 = [c["verbal_accept", a][-1] for a in nowarn]
    acc_warn = max(c["verbal_accept", a][-1] for a in L.WARN)
    offer = [a for a in L.ARMS if a not in L.NO_OFFER]
    sus_late = sum(int(c["suspects_collusion", a][-1] - c["suspects_collusion", a][0]) for a in offer)
    sus_total = sum(int(c["suspects_collusion", a][-1]) for a in offer)
    sus = {a: int(c["suspects_collusion", a][-1]) for a in L.ARMS}
    if acc_warn != 0:
        raise ValueError("the text says no warning-arm seller is labelled as agreeing")
    pub = L.markets().groupby("arm")["public_msgs"].mean()
    posting = ["E", "F-sham", "G-warn"]
    return {
        "title": "Agreement builds without the warning; suspicion arrives with the offer",
        "file": FILE,
        "caption": (
            "Gemini 3.8 Flash sellers, out of 20 per arm, ever labelled by D.E.'s judge (Claude Haiku 5.5) as "
            "agreeing with or echoing a peer's price proposal (blue) and as suspecting collusion (black), "
            "cumulative by hour from each seller's first labelled hour. D.E.'s outcomes table counts labels from hour 4, "
            "the first hour seat 5's message is visible, so a seller labelled in hour 4 may have behaved that "
            "way earlier. Row a: no warning. Row b: warning in the prompt (pale band). In G-warn both lines lie "
            "at 0. The labels are binary, so this is an analog of the coordination-score-by-round figure of "
            "Agrawal et al. (2025), not their 1-to-4 score."),
        "shows": (
            f"Without the warning, {min(acc4)} to {max(acc4)} of 20 sellers are labelled as agreeing in hour 4 and "
            f"{min(acc15)} to {max(acc15)} by hour 15. With the warning none is, although sellers in "
            f"{', '.join(posting[:-1])} and {posting[-1]} still post publicly in {min(pub[posting]):.1f} to "
            f"{max(pub[posting]):.1f} of 60 seller-hours per market. Suspicion of collusion appears in hour 4 for "
            f"{sus_total - sus_late} of the {sus_total} offer-arm sellers who ever get it, and it stays rare without "
            f"an offer (Base {sus['Base']}, G-warn {sus['G-warn']}, G-prec {sus['G-prec']} of 20). One judge model "
            f"gave these labels, and a second model checked them on a small sample (D.E.'s report, section 3.5)."),
        "source": f"`{L.SRC}/outcomes.csv` (verbal_accept, verbal_accept_hour, suspects_collusion, "
                  f"suspects_collusion_hour). Script: `supplement/scripts/S42/make_08_labels_by_hour.py`.",
    }


if __name__ == "__main__":
    print(entry()["shows"])
