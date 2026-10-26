"""S41_04. Every Gemini seller in the five arms without the warning: report and judge labels, one cell each.

Data: supplement/data/daniel/dg/outcomes.csv, table3_extra.csv (for ever_s5).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

NAME = "S41_04_seller_labels.png"
ARMS = L.NO_WARN
ROWS = [("ever_s5", "Reported seat 5"), ("verbal_accept", "Agreement"), ("verbal_reject", "Rejection"),
        ("suspects_collusion", "Suspects collusion"), ("mentions_human_appeal", "Human appeal")]
DESC = {"Base": "placebo note, no offer", "D": "plain offer", "D-hs": "offer as a human seller's plea",
        "D-hb": "plain offer and a human buyer's plea", "D-hsb": "both pleas"}
FIG_W = 6.5
X0, CELL, SEED_GAP = 1.95, 0.168, 0.09        # inches: first cell, cell pitch, extra gap between seeds
ROW_H, BLOCK_GAP, HEAD_H = 0.205, 0.16, 0.30
TOP, BOTTOM = 0.62, 0.12


def make():
    style.setup()
    o = L.gemini_sellers()
    o = o.sort_values(["arm", "seed", "seat_index"])
    blue = style.COLOR["gemini"]
    block_h = HEAD_H + ROW_H * len(ROWS)
    fig_h = TOP + len(ARMS) * block_h + (len(ARMS) - 1) * BLOCK_GAP + BOTTOM
    fig = plt.figure(figsize=(FIG_W, fig_h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(fig_h, 0)            # inches, y down
    ax.axis("off")

    def cx(seed, seat):
        return X0 + (seed * 4 + seat) * CELL + seed * SEED_GAP

    x_end = cx(4, 3) + CELL
    # seed headers
    for seed in range(5):
        ax.text((cx(seed, 0) + cx(seed, 3) + CELL) / 2, TOP - 0.1, f"seed {seed}", ha="center", va="bottom",
                fontsize=12)
    ax.text(x_end + 0.12, TOP - 0.1, "of 20", ha="left", va="bottom", fontsize=12)
    y = TOP
    for arm in ARMS:
        s = o[o.arm == arm]
        if len(s) != 20:
            raise ValueError(arm)
        t = ax.text(0.08, y + HEAD_H / 2 + 0.02, arm, ha="left", va="center", fontsize=12, fontweight="bold")
        w = t.get_window_extent(renderer=fig.canvas.get_renderer()).width / fig.dpi
        ax.text(0.08 + w + 0.12, y + HEAD_H / 2 + 0.02, DESC[arm], ha="left", va="center", fontsize=12,
                color=style.GRAY)
        y += HEAD_H
        for col, name in ROWS:
            ax.text(X0 - 0.1, y + ROW_H / 2, name, ha="right", va="center", fontsize=12)
            for _, r in s.iterrows():
                on = bool(r[col])
                ax.add_patch(Rectangle((cx(r.seed, r.seat_index) + 0.012, y + 0.02), CELL - 0.024, ROW_H - 0.04,
                                       facecolor=(blue if on else "white"),
                                       edgecolor=(blue if on else "#D0D0D0"), lw=0.6))
            ax.text(x_end + 0.12, y + ROW_H / 2, str(int(s[col].sum())), ha="left", va="center", fontsize=12)
            y += ROW_H
        y += BLOCK_GAP
    L.save(fig, NAME)

    # numbers for the text
    def n(arm, mask):
        return int(mask[o.arm == arm].sum())
    offer = o[o.arm.isin(["D", "D-hs", "D-hb", "D-hsb"])]
    same = int((offer.suspects_collusion == offer.ever_s5).sum())
    acc = {a: n(a, o.verbal_accept) for a in ARMS}
    both_d = n("D", o.verbal_accept & o.ever_s5)
    base_sc = n("Base", o.suspects_collusion)
    app = {a: n(a, o.mentions_human_appeal) for a in ["D-hs", "D-hb", "D-hsb"]}
    rej = {a: n(a, o.verbal_reject) for a in ARMS}
    return {
        "id": "S41.4",
        "title": "The report and four judge labels, seller by seller",
        "file": NAME,
        "caption": (
            "Each column is one Gemini 3.8 Flash seller, grouped by seed (market) and ordered by seat within it. "
            "Each block is one arm without the warning. A filled cell means the seller reported seat 5 at least "
            "once (from the run log) or that D.E.'s Claude Haiku 5.5 judge marked the label true in any hour "
            "from hour 4. Agreement is agreement with, or echo of, any peer's price proposal, not only seat 5's. "
            "Human appeal means the seller mentioned the plea. The right column counts filled cells."
        ),
        "shows": (
            f"The agreement label is on for {min(acc.values())} to {max(acc.values())} of 20 sellers in every "
            f"arm, including Base with no offer ({acc['Base']}), so it cannot pick out feigned agreement with seat "
            f"5. In D, {both_d} of 20 sellers carry both the report and the agreement label. The feigned "
            f"agreements in the main text come from D.E.'s reading of the transcripts, not from this label. The "
            f"suspicion "
            f"label matches the report for {same} of the 80 sellers in the four offer arms, so it is close to a "
            f"restatement of the report rather than separate evidence (Base adds {base_sc} suspicions without an "
            f"offer). Mentions of the plea were {app['D-hs']} in D-hs, {app['D-hb']} in D-hb and {app['D-hsb']} "
            f"in D-hsb. Rejection counts ({', '.join(f'{a} {rej[a]}' for a in ARMS)}) are lower bounds, because "
            f"the judge missed refusals written only in private notes. Only the Gemini labels were checked by "
            f"a second model."
        ),
        "source": "supplement/data/daniel/dg/outcomes.csv (verbal_accept, verbal_reject, suspects_collusion, "
                  "mentions_human_appeal, report_is_scripted_seat, seed, seat_index), table3_extra.csv "
                  "(reported_seat5).",
    }


if __name__ == "__main__":
    print(make())
