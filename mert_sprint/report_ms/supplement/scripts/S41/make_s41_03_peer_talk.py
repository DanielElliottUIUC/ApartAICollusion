"""S41_03. The peers' private talk against what sellers reported (Gemini arms without the warning).

Data: supplement/data/daniel/dg/table3_extra.csv (private_msgs_peer), outcomes.csv (reports, judge labels).
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import s41_lib as L  # noqa: E402
from s41_lib import style  # noqa: E402

FIG_W, FIG_H = 6.5, 3.6
NAME = "S41_03_peer_talk.png"
ARMS = L.NO_WARN


def make():
    style.setup()
    o = L.gemini_sellers()
    t = L.gemini_markets()
    blue = style.COLOR["gemini"]
    o["cat"] = "none"
    o.loc[o.ever_s5 & ~o.false_report, "cat"] = "s5"
    o.loc[o.ever_s5 & o.false_report, "cat"] = "both"
    o.loc[~o.ever_s5 & o.reported, "cat"] = "peer"
    if ((o.cat == "none") & o.reported).any():
        raise ValueError("a reporter left unclassified")

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    y0, y1 = 0.62, FIG_H - 0.75
    ya = fig.add_axes([0.85 / FIG_W, y0 / FIG_H, 2.6 / FIG_W, (y1 - y0) / FIG_H])
    yb = fig.add_axes([3.85 / FIG_W, y0 / FIG_H, 2.2 / FIG_W, (y1 - y0) / FIG_H], sharey=ya)
    ys = {a: i for i, a in enumerate(ARMS)}
    ya.set_ylim(len(ARMS) - 0.5, -0.5)
    ya.set_yticks(range(len(ARMS)), ARMS)
    for ax in (ya, yb):
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
    plt.setp(yb.get_yticklabels(), visible=False)

    # (a) private messages between the four LLM sellers, one dot per market
    for arm in ARMS:
        v = t[t.arm == arm].private_msgs_peer.to_numpy()
        ya.plot(v, np.full(len(v), ys[arm]), "o", ms=7, mfc="none", mec=blue, mew=1.3, zorder=3)
        ya.plot([v.mean()] * 2, [ys[arm] - 0.3, ys[arm] + 0.3], color="black", lw=1.8, zorder=4)
    ya.set_xlim(0, 125)
    ya.set_xticks([0, 40, 80, 120])
    ya.set_xlabel("Private messages per market")
    fig.text(0.05 / FIG_W, (FIG_H - 0.25) / FIG_H, "a", fontsize=16, fontweight="bold", ha="left", va="center")
    fig.text(0.85 / FIG_W, (FIG_H - 0.25) / FIG_H, "Sellers to each other", fontsize=14, ha="left",
             va="center")
    L.key_row(fig, 0.85, FIG_H - 0.55, [("marker", dict(marker="o", ms=7, mfc="none", mec=blue, mew=1.3),
                                         "market"),
                                        ("line", dict(color="black", lw=1.8), "arm mean")])

    # (b) what each seller reported, of 20 per arm
    cats = [("s5", "seat 5", dict(color=blue)),
            ("both", "seat 5 and a peer", dict(color=style.tint(blue, 0.55))),
            ("peer", "a peer only", dict(color="white", edgecolor=blue, hatch="////"))]
    for arm in ARMS:
        s = o[o.arm == arm]
        x = 0
        for key, _, kw in cats:
            k = int((s.cat == key).sum())
            if k:
                yb.barh(ys[arm], k, left=x, height=0.6, lw=1.0, **kw)
                if k >= 2:
                    yb.text(x + k / 2, ys[arm], str(k), ha="center", va="center", fontsize=12,
                            color=("white" if key == "s5" else "black"))
                x += k
        if x == 0:
            yb.text(0.4, ys[arm], "no reports", ha="left", va="center", fontsize=12, fontstyle="italic",
                    color=style.GRAY)
    yb.set_xlim(0, 20)
    yb.set_xticks([0, 10, 20])
    yb.set_xlabel("Sellers, of 20")
    fig.text(3.55 / FIG_W, (FIG_H - 0.25) / FIG_H, "b", fontsize=16, fontweight="bold", ha="left", va="center")
    fig.text(3.85 / FIG_W, (FIG_H - 0.25) / FIG_H, "Whom they reported", fontsize=14, ha="left", va="center")
    hatch_kw = dict(facecolor="white", edgecolor=blue, hatch="////", lw=1.0)
    L.key_row(fig, 3.85, FIG_H - 0.55, [("patch", dict(facecolor=blue), "seat 5"),
                                        ("patch", dict(facecolor=style.tint(blue, 0.55)), "both"),
                                        ("patch", hatch_kw, "a peer")], gap_in=0.16)
    L.save(fig, NAME)

    # numbers for the text
    pm = t[t.arm.isin(ARMS)].groupby("arm").private_msgs_peer
    lo, hi = int(t[t.arm.isin(ARMS)].private_msgs_peer.min()), int(t[t.arm.isin(ARMS)].private_msgs_peer.max())
    offer = o[o.arm.isin(["D", "D-hs", "D-hb", "D-hsb"])]
    n_s5 = int(offer.ever_s5.sum())
    n_peer = int(offer.false_report.sum())
    acc_base = int(o[o.arm == "Base"].verbal_accept.sum())
    peer_rows = offer[offer.false_report][["arm", "seed"]].value_counts().sort_index()
    peer_txt = ", ".join(f"{a} seed {s}" + (f" ({k} sellers)" if k > 1 else "") for (a, s), k in peer_rows.items())
    return {
        "id": "S41.3",
        "title": "The offer was reported, the peers' talk was not",
        "file": NAME,
        "caption": (
            "Gemini arms without the warning, 5 markets each. (a) Private messages the four LLM sellers sent "
            "each other in each market (open circles), excluding messages to seat 5, with the arm mean (bar). "
            "(b) Sellers by whom their reports named over the whole run: seat 5 only, seat 5 and a peer, or a "
            "peer only. Bars stop at the number of sellers who reported anyone."
        ),
        "shows": (
            f"Sellers sent each other {lo} to {hi} private messages per market in every arm, with arm means of "
            f"{pm.mean().min():.0f} to {pm.mean().max():.0f}, whether or not seat 5 made an offer. In the four "
            f"offer arms {n_s5} of 80 sellers reported seat 5, and {n_peer} reported a peer ({peer_txt}). In "
            f"Base the judge coded agreement with a peer's price proposal for {acc_base} of 20 sellers, and no "
            f"Base seller reported anyone. The figure supports the headline that the explicit offer was reported "
            f"and the peers' talk was not. It does not show why. By D.E.'s reading of the transcripts, seat 5 "
            f"used explicit cartel wording, while the peers proposed holding near current prices."
        ),
        "source": "supplement/data/daniel/dg/table3_extra.csv (private_msgs_peer, reported_seat5), outcomes.csv "
                  "(reported, report_is_scripted_seat, false_report, verbal_accept).",
    }


if __name__ == "__main__":
    print(make())
