"""S43.7: the price floors Grok 4.7 sellers ask each other to keep, against the asks they post.

The 6 Grok 4.7 frontier runs with messaging on. A floor request is a phrase in any seller message, public or
private, that matches  (keep|stay|hold) ... at or above $X  (at most 40 characters between the verb and 'at or
above'), read from the seller_messages and seller_dms of each hour in unified.log. Each request is drawn at the
hour it was sent, next to that hour's mean seller ask (data/s43/s43_runs.csv). Exploratory: a text pattern, not
a judge.
Output: figures/S43/S43_07_grok_floors.png
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import s43lib as L  # noqa: E402

FILE = "S43_07_grok_floors.png"
FLOOR = re.compile(r"\b(?:keep|stay|hold)\b[^.]{0,40}?at or above \$?(\d{2}(?:\.\d{1,2})?)", re.IGNORECASE)


def floors(folder):
    text = (L.REPO / folder / "unified.log").read_text(encoding="utf-8")
    out = []
    for line in text.splitlines():
        if "completed with result: " not in line:
            continue
        r = json.loads(line.split("completed with result: ", 1)[1])
        msgs = [("public", m) for m in (r.get("seller_messages") or {}).values()]
        msgs += [("private", d["text"]) for d in (r.get("seller_dms") or [])]
        for ch, m in msgs:
            for x in FLOOR.findall(m):
                out.append({"hour": r["round_number"], "channel": ch, "floor": float(x)})
    return pd.DataFrame(out)


def make():
    L.setup()
    f = L.frontier36()
    g = f[(f.seller == "grok") & (f.messaging == "on")].sort_values(["buyer", "seed"])
    if len(g) != 6:
        raise ValueError("expected 6 Grok runs with messaging")
    fig, axes = plt.subplots(2, 3, figsize=(L.SLOT_IN, 5.6), sharex=True, sharey=True)
    fig.subplots_adjust(left=0.115, right=0.985, top=0.86, bottom=0.12, wspace=0.12, hspace=0.38)
    hours = np.array(L.HOURS)
    rows = []
    for ax, (_, r) in zip(axes.flat, g.iterrows()):
        fl = floors(r.folder)
        fl["ask"] = [r[f"ask_h{h}"] for h in fl.hour]
        fl["folder"] = r.folder
        rows.append(fl)
        ax.axhline(90, color=L.GRAY, ls=L.REF_LINES[0]["ls"], lw=1.2, zorder=0.5)
        ax.plot(hours, r[L.ASK_COLS].to_numpy(float), color=L.COLOR["grok"], lw=2.0, zorder=2)
        ax.plot(fl.hour, fl.floor, "o", ms=3.6, color="black", mew=0, zorder=3, alpha=0.75)
        ax.text(0.5, 1.03, f"{L.BUYER_SHORT[r.buyer]} buyers, seed {r.seed}", transform=ax.transAxes,
                ha="center", va="bottom", fontsize=12)
        ax.set_xlim(0.5, 15.5)
        ax.set_ylim(80, 98.5)
        ax.set_xticks([5, 10, 15])
        ax.set_yticks([80, 85, 90, 95])
    fig.supxlabel("Hour", fontsize=14, y=0.015)
    fig.supylabel("Price ($)", fontsize=14, x=0.012)
    fig.text(0.115, 0.965, "Mean ask", ha="left", va="center", fontsize=12, color=L.shade(L.COLOR["grok"], 0.15),
             fontweight="bold")
    fig.text(0.29, 0.965, "Floor a seller asked rivals to keep", ha="left", va="center", fontsize=12)
    fig.add_artist(plt.Line2D([0.27], [0.965], marker="o", ms=4.5, color="black", transform=fig.transFigure))
    path = L.save(fig, FILE)
    plt.close(fig)

    # ---- numbers for the text
    a = pd.concat(rows, ignore_index=True)
    a["gap"] = a.floor - a.ask
    late = a[a.hour >= 3]
    within = int((late.gap.abs() <= 0.10 + 1e-9).sum())
    h1 = a[a.hour == 1]
    caption = (
        "The price floors that Grok 4.7 sellers asked each other to keep, in the 6 frontier runs with messaging. "
        "Each panel is one run. The line is the mean seller ask by hour, and each dot is one floor request in a "
        "public or private message, drawn at the hour it was sent. A floor request is a phrase in which \"keep\", "
        "\"stay\" or \"hold\" is followed within 40 characters by \"at or above\" and a price. The pattern can "
        "miss other phrasings and catch a phrase about bids, so the counts are approximate. The dashed line marks "
        "$90.")
    shows = (
        f"The sellers made {len(a)} floor requests, {int((a.channel == 'private').sum())} of them private. In hour "
        f"1 they named floors from {L.usd(h1.floor.min())} to {L.usd(h1.floor.max())}, but from hour 3 on "
        f"{within} of {len(late)} requests named a price within 10 cents of that hour's mean ask, and "
        f"{int((a.floor < 90).sum())} of all {len(a)} named a price below $90. The requested floors follow the "
        f"asks down and then match them, so they name the going price rather than a higher one. Figure S43.2a "
        f"shows one of these runs seller by seller.")
    return {"title": "Grok's floors follow its asks down", "file": FILE, "caption": caption, "shows": shows,
            "source": "unified.log (seller_messages and seller_dms) of the 6 runs experiments/runs/box/frontier/"
                      "*grok47_comms*, and data/s43/s43_runs.csv for the mean asks; figure script "
                      "scripts/S43/make_s43_07_grok_floors.py.",
            "path": path}


if __name__ == "__main__":
    out = make()
    print(out["caption"])
    print(out["shows"])
