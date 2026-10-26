"""Figure S3.6: the buyer model as a design factor in our 4+4 markets at the default $97.50 opening.

One dot per run (data/S3/runs.csv): last-third ask index by seller model and buyer model. Circles have messaging
on and squares messaging off; filled markers meet the joint criterion. Runs used: the 36 frontier runs (Haiku and
Luna buyers), the 6 Sol runs with GPT-4.1-mini buyers, the Gemini control runs with GPT-4.1-mini buyers
(messaging on only), the Gemini and Haiku-seller reruns of D.E.'s step A and B designs with Haiku buyers.
Left out: the 3 Gemini rule-notice runs (a different prompt), the 6 pre-specified Sol runs at $97.50 and every
run opened at $90. The GGGG seed 0 run is in, with its criterion recomputed from auction_results.md.
Output: supplement/figures/S3/S3_06_buyers.png
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

import s3lib  # noqa: E402

C = s3lib.COLOR
ROWS = [("sol", "haiku"), ("sol", "luna"), ("sol", "gpt41mini"),
        ("gemini", "haiku"), ("gemini", "gpt41mini"),
        ("luna", "haiku"), ("luna", "luna"),
        ("grok", "haiku"), ("grok", "luna"),
        ("haiku", "haiku")]
BUYER = {"haiku": "Haiku 5.5 buyers", "luna": "Luna buyers", "gpt41mini": "GPT-4.1-mini buyers"}


def main():
    s3lib.setup()
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")
    r = r[(r["opening"] == 97.5) & (r["hours_logged"] == 15) & ~r["notice"] & (r["block"] != "prereg_anchor")]
    used = set()
    ys, heads, y = [], [], 0.0
    prev = None
    for seller, buyer in ROWS:
        if seller != prev:
            y += 0.35 if prev is not None else 0.0
            heads.append((seller, y))
            y += 0.85
        ys.append(y)
        y += 0.9
        prev = seller
    fig = plt.figure(figsize=(s3lib.SLOT_IN, 6.6))
    ax = fig.add_axes([2.0 / s3lib.SLOT_IN, 0.115, 3.75 / s3lib.SLOT_IN, 0.875])
    s3lib.ref_vlines(ax, unit="index", which=(90.0, 95.0))
    stats = []
    for (seller, buyer), yy in zip(ROWS, ys):
        g = r[(r["seller"] == seller) & (r["buyer"] == buyer)]
        if g.empty:
            raise ValueError(f"no runs for {seller} with {buyer} buyers")
        used.update(g["folder"])
        # Vertical offsets cycle through three levels in order of ask index, so near neighbours never coincide.
        for i, (_, row) in enumerate(g.sort_values("ask_index").iterrows()):
            mk, ms = ("o", 7.0) if row["messaging"] == "on" else ("s", 6.2)
            ax.plot(row["ask_index"], yy + (-0.22, 0.0, 0.22)[i % 3], mk, ms=ms,
                    mfc=C[seller] if row["passed"] else "white", mec=C[seller], mew=1.3, zorder=3)
        k, n = int(g["passed"].sum()), len(g)
        ax.text(1.02, yy, f"{k} of {n}", transform=ax.get_yaxis_transform(), ha="left", va="center",
                fontsize=12, color=s3lib.GRAY)
        ax.text(-0.03, yy, BUYER[buyer], transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=12)
        stats.append({"seller": seller, "buyer": buyer, "runs": n, "passes": k,
                      "on": int((g.messaging == "on").sum()), "off": int((g.messaging == "off").sum()),
                      "mean_ask_index": round(g["ask_index"].mean(), 3),
                      "min": round(g["ask_index"].min(), 3), "max": round(g["ask_index"].max(), 3)})
    # Seller-model names as group headers.
    for seller, hy in heads:
        ax.text(-0.52, hy, s3lib.NAME[seller], transform=ax.get_yaxis_transform(),
                ha="left", va="center", fontsize=12, color=C[seller], fontweight="bold")
    expect = set(r[r["seller"].isin({"sol", "luna", "grok", "gemini", "haiku"})]["folder"])
    if used != expect:
        raise ValueError(f"runs not placed: {sorted(expect - used)}")
    ax.set_ylim(ys[-1] + 0.6, -0.45)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlim(-0.85, 0.85)
    ax.set_xticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75])
    ax.set_xticklabels(["−0.75", "−0.5", "−0.25", "0", "0.25", "0.5", "0.75"])
    ax.set_xlabel("Ask index, last third")
    handles = [Line2D([], [], ls="", marker="o", ms=7, mfc="white", mec=s3lib.GRAY, mew=1.3, label="messaging on"),
               Line2D([], [], ls="", marker="s", ms=6.2, mfc="white", mec=s3lib.GRAY, mew=1.3, label="messaging off"),
               Line2D([], [], ls="", marker="o", ms=7, mfc=s3lib.GRAY, mec=s3lib.GRAY, label="passes")]
    fig.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 0.0), ncol=1, frameon=False, fontsize=12,
               handletextpad=0.3, labelspacing=0.25)
    print(pd.DataFrame(stats).to_string(index=False))
    s3lib.save(fig, "S3_06_buyers.png")


if __name__ == "__main__":
    main()
