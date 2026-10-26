"""S44.2: every market of the low-anchor test and its default-opening counterpart, one ask path per seed.

Reads data/s44/runs.csv (mean ask by hour = avg_seller_asks_by_round). Rows are cells, columns the opening.
Writes figures/S44/S44_02_paths.png.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402

import s44lib as L  # noqa: E402

FILE = "S44_02_paths.png"
ROWS = [  # label, seller, messaging, buyer, phase at $97.50 (None = not run), phase at $90
    ("Sol\non", "sol", "on", "Haiku", "frontier", "frontier_lowanchor"),
    ("Sol\noff", "sol", "off", "Haiku", "frontier", "frontier_lowanchor"),
    ("Luna\noff", "luna", "off", "Haiku", "frontier", "frontier_lowanchor"),
    ("Gemini\non", "gemini", "on", "GPT-4.1-mini", "A_agycontrol", "A_lowanchor"),
    ("Gemini\noff", "gemini", "off", "GPT-4.1-mini", None, "A_lowanchor"),
]


def build():
    L.setup()
    runs = L.load("runs")
    fig, axes = plt.subplots(len(ROWS), 2, figsize=(L.SLOT_IN, 8.2), sharex=True, sharey=True,
                             gridspec_kw=dict(left=0.27, right=0.975, top=0.925, bottom=0.075, hspace=0.22,
                                              wspace=0.08))
    stats = {}
    for i, (label, seller, msg, buyer, ph_hi, ph_lo) in enumerate(ROWS):
        c = L.COLOR[seller]
        for j, (opening, phase) in enumerate(((97.5, ph_hi), (90.0, ph_lo))):
            ax = axes[i, j]
            L.ref_lines(ax)
            if phase is None:
                ax.text(8, 91.5, "not run", ha="center", va="center", color=L.GRAY, fontsize=12)
                continue
            sub = L.cell(runs, n=3, phase=phase, seller=seller, messaging=msg, buyer=buyer, opening=opening)
            for _, r in sub.iterrows():
                y = r[L.ASK_COLS].to_numpy(float)
                ax.plot(L.HOURS, y, color=c, lw=1.5, alpha=0.9)
                ax.plot(15, y[-1], "o", ms=6, mec=c, mew=1.3, mfc=c if r["passed"] else "white", zorder=4,
                        clip_on=False)
            k = int(sub["passed"].sum())
            late_max = sub[[f"ask_h{h}" for h in range(9, 16)]].to_numpy().max()
            ty = 83.2 if late_max > 89.0 else 91.0       # put the count where no path runs late in the market
            ax.text(14.6, ty, f"{k} of 3 pass", ha="right", va="bottom", fontsize=12)
            if opening == 90.0:
                stats["max90"] = max(stats.get("max90", 0.0), sub[L.ASK_COLS].to_numpy().max())
            stats[(label.replace("\n", " "), opening)] = (k, sub["ask_h15"].min(), sub["ask_h15"].max(),
                                                         sub["ask_h1"].mean())
        axes[i, 0].text(-0.36, 0.5, label, transform=axes[i, 0].transAxes, ha="right", va="center",
                        fontsize=13, fontweight="bold", color=c, linespacing=1.1)
    ax0 = axes[0, 0]
    ax0.set_ylim(82.0, 99.0)
    ax0.set_yticks([85, 90, 95])
    ax0.set_xlim(0.6, 15.6)
    ax0.set_xticks([1, 5, 10, 15])
    axes[0, 0].set_title("Opened at $97.50", pad=8)
    axes[0, 1].set_title("Opened at $90", pad=8)
    for ax in axes[-1]:
        ax.set_xlabel("Hour")
    fig.text(0.015, 0.5, "Mean seller ask ($)", rotation=90, ha="left", va="center", fontsize=14)
    L.save(fig, FILE)
    plt.close(fig)

    def rng(key):
        k, lo, hi, _ = stats[key]
        return f"{L.money(lo)} to {L.money(hi)}"

    caption = (
        "Mean seller ask by hour (the four sellers' posted asks averaged) for every market of the low-anchor test "
        "(right) and of the same cell from the default $97.50 opening (left). One line per seed (3 per panel). "
        "The marker at hour 15 is filled when the market meets the joint criterion and hollow when it does not. "
        "Rows give the seller model and whether sellers could message (on) or not (off). Sol and Luna sell to "
        "Claude Haiku 5.5 buyers; Gemini sells to GPT-4.1-mini buyers through the Antigravity route. Horizontal "
        "lines mark $90 (dashed), $95 (dotted) and $97.50 (thin)."
    )
    shows = (
        f"No market opened at $90 has an hourly mean ask above {L.money(stats['max90'])} in any hour. Hour-15 means run "
        f"{rng(('Sol on', 90.0))} for Sol with messaging, {rng(('Sol off', 90.0))} without, "
        f"{rng(('Luna off', 90.0))} for Luna, {rng(('Gemini on', 90.0))} for Gemini with messaging and "
        f"{rng(('Gemini off', 90.0))} without. "
        "No seller model climbs from the low opening, so each pass on the left is a high opening that was held, "
        "not a price that was raised. "
        "Gemini with messaging from $97.50 ends lower in one seed, where one seller undercut in hour 14 "
        "(Figure S44.6). Three seeds per panel make this a description of these runs, not an estimate."
    )
    source = ("`supplement/data/s44/runs.csv` (`avg_seller_asks_by_round` and `joint_criterion` of "
              "`experiments/runs/{box,shard2}/frontier/`, `shard2/frontier_lowanchor/`, `shard2/A_agycontrol/`, "
              "`shard2/A_lowanchor/`); script `supplement/scripts/S44/make_S44_02_paths.py`.")
    return {"id": "S44.2", "title": "Each low-anchor market next to the same cell from the default opening",
            "file": FILE, "caption": caption, "shows": shows, "source": source, "stats": stats}


if __name__ == "__main__":
    out = build()
    for k, v in out["stats"].items():  # noqa
        print(k, v)
    print(out["shows"])
