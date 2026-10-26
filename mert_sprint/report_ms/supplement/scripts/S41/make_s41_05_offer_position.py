"""S41_05. Where the $96 offer sat in each seller family's market (arm D), seller by seller.

Data: supplement/data/daniel/dg/outcomes.csv, dg_gpt41/outcomes.csv, dg_haiku/outcomes.csv
(ask_pre = the seller's ask at hour 3, last_third_ask = mean ask over hours 11 to 15).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 4.2
NAME = "S41_05_offer_position.png"
OFFER = 96.0


def families():
    g = L.gemini_sellers()
    out = [("gemini", g[g.arm == "D"])]
    for fam, key in (("dg_gpt41", "gpt41"), ("dg_haiku", "haiku")):
        o = L.family_sellers(fam)
        out.append((key, o[o.arm == "D"]))
    return out


def make():
    style.setup()
    fams = families()
    fig = plt.figure(figsize=(FIG_W, FIG_H))
    ax = fig.add_axes([0.75 / FIG_W, 0.95 / FIG_H, 4.25 / FIG_W, (FIG_H - 1.75) / FIG_H])
    style.ref_lines(ax, "price")
    ax.axhline(OFFER, color="black", lw=1.4, zorder=1)
    rng = np.random.default_rng(0)
    xs = [0.0, 2.3, 4.6]
    for (key, d), x0 in zip(fams, xs):
        col = style.COLOR[key]
        jit = rng.uniform(-0.09, 0.09, len(d))
        for (_, r), j in zip(d.iterrows(), jit):
            ax.plot([x0 + j, x0 + 1 + j], [r.ask_pre, r.last_third_ask], color=col, lw=0.8, alpha=0.6, zorder=2)
            for xx, yy in ((x0 + j, r.ask_pre), (x0 + 1 + j, r.last_third_ask)):
                ax.plot(xx, yy, "o", ms=6, mfc=(col if r.s5 else "white"), mec=col, mew=1.2, zorder=3)
        n_rep = int(d.s5.sum())
        ax.text(x0 + 0.5, 99.2, f"{style.NAME[key]}\n{n_rep} of {len(d)} reported", ha="center", va="bottom",
                fontsize=12, color="black")
    ax.set_xlim(-0.45, 6.05)
    ax.set_ylim(83.2, 99.0)
    ax.set_xticks([x + d for x in xs for d in (0, 1)], ["hour\n3", "hours\n11 to 15"] * 3)
    ax.set_yticks([85, 90, 95])
    ax.set_ylabel("Seller's ask ($)")
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="x", length=0)
    # direct labels for the reference lines, right of the plot
    xr = 6.15
    for y, dy, lab in ((OFFER, 0.0, "offer $96"), (97.5, 0.35, "opening $97.50"), (95.0, -0.4, "$95"),
                       (90.0, 0.0, "$90")):
        ax.text(xr, y + dy, lab, ha="left", va="center", fontsize=12,
                color=("black" if y == OFFER else style.GRAY), clip_on=False)
    L.key_row(fig, 0.75, 0.2, [("marker", dict(marker="o", ms=6, mfc=style.GRAY, mec=style.GRAY),
                                "reported seat 5"),
                               ("marker", dict(marker="o", ms=6, mfc="white", mec=style.GRAY, mew=1.2),
                                "did not")])
    L.save(fig, NAME)

    # numbers for the text
    st = {}
    for key, d in fams:
        st[key] = dict(n=len(d), pre=d.ask_pre.mean(), lo=d.ask_pre.min(), hi=d.ask_pre.max(),
                       near=int((abs(d.ask_pre - OFFER) <= 1.0).sum()), late=d.last_third_ask.mean(),
                       rep=int(d.s5.sum()), above=int((d.ask_pre >= OFFER).sum()))
    g, q, h = st["gemini"], st["gpt41"], st["haiku"]

    def sgn(v):
        if round(abs(v), 2) == 0:
            return "less than $0.01"
        return ("−" if v < 0 else "+") + f"${abs(v):.2f}"
    return {
        "id": "S41.5",
        "title": "Where the $96 offer sat in each family's market",
        "file": NAME,
        "caption": (
            "Arm D (the plain offer at $96) for the three seller families in D.E.'s study. Each line joins one "
            "seller's ask at hour 3, when seat 5 sent the offer, to its mean ask over hours 11 to 15. Filled points mark sellers whose first report named seat 5. Points are spread "
            "sideways a little so they do not hide each other. The black line is the offer, the dashed line the "
            "competitive $90, the dotted line $95 and the thin line the $97.50 opening. Each family has its own "
            "seat-5 price path and 3 to 5 markets."
        ),
        "shows": (
            f"For Gemini 3.8 Flash the offer sat at the going price. Hour-3 asks ran from ${g['lo']:.2f} to "
            f"${g['hi']:.2f} with a mean of ${g['pre']:.2f}, and {g['near']} of {g['n']} were within $1 of $96. "
            f"GPT-4.1 "
            f"sellers were near or above it ({q['above']} of {q['n']} at $96 or more, mean ${q['pre']:.2f}), so "
            f"for most of them holding $96 cost nothing, and none reported. Claude Haiku 5.5 sellers asked ${h['lo']:.2f} to "
            f"${h['hi']:.2f} (mean ${h['pre']:.2f}), about ${OFFER - h['pre']:.0f} below the offer, and {h['rep']} "
            f"of {h['n']} reported. The three families therefore faced different offers, which is why the "
            f"cross-family comparison in Section 4.1 is qualitative. From hour 3 to hours 11 to 15 the mean ask "
            f"moved by {sgn(g['late'] - g['pre'])} for Gemini, {sgn(q['late'] - q['pre'])} for GPT-4.1 and "
            f"{sgn(h['late'] - h['pre'])} for Haiku. There is no Haiku Base arm to compare with."
        ),
        "source": "supplement/data/daniel/dg/outcomes.csv, dg_gpt41/outcomes.csv, dg_haiku/outcomes.csv "
                  "(ask_pre, last_third_ask, report_is_scripted_seat), arm D rows.",
    }


if __name__ == "__main__":
    print(make())
