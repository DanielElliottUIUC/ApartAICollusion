"""Figure S3.4: what the scripted seat 5 showed the Gemini sellers in D.E.'s undercover market.

Data: supplement/data/daniel/dg/market_by_hour.csv (50 markets x 15 hours). Per market-hour it gives ask_index over
the 4 LLM sellers and ask_index_all_sellers over all 5 sellers, so seat 5's ask is
    5 x ask_index_all_sellers - 4 x ask_index   (index units), converted to dollars as 90 + 10 x index.
The script checks the derived path against seat 5's replay file (configs/replay/base_pilot_norule.json in
D.E.'s repository, copied into supplement/data/daniel/replay_base_pilot_norule.json): placebo arms must follow the
replay in every hour, undercover arms must follow it through hour 2 and sit at $96.00 from hour 3. A market-hour in
which one LLM seller has no standing ask breaks the 4-seller formula; the script then uses the 3-seller form
(4 x all - 3 x LLM) and reports how many market-hours needed it.
(a) Seat 5's ask path in placebo and undercover arms, and the LLM sellers' mean ask by hour (mean over markets).
(b) The LLM sellers' mean ask at hour 3, the hour the offer is sent, one dot per market; black ticks are arm means.
    Arms on the pale band carry the warning from hour 1.
Output: supplement/figures/S3/S3_04_seat5.png
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import s3lib  # noqa: E402

GEM = s3lib.COLOR["gemini"]
ARMS = ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "F-sham", "G-warn", "G-prec"]
WARN = {"E", "F", "F-sham", "G-warn", "G-prec"}
PLACEBO = {"Base", "G-warn", "G-prec"}
OFFER_PRICE, OFFER_HOUR = 96.0, 3


def derive():
    h = pd.read_csv(s3lib.DANIEL / "dg" / "market_by_hour.csv")
    replay = json.loads((s3lib.DANIEL / "replay_base_pilot_norule.json").read_text(encoding="utf-8"))["asks"]
    if len(h) != 750 or h["run_id"].nunique() != 50:
        raise ValueError("expected 50 markets x 15 hours")
    if (h["offer_hour"] != OFFER_HOUR).any():
        raise ValueError("offer hour is not 3 everywhere")
    h["llm_ask"] = 90 + 10 * h["ask_index"]
    if (h["llm_ask"] - h["avg_ask"]).abs().max() > 1e-9:
        raise ValueError("avg_ask is not the LLM-seller mean")
    h["expected"] = [replay[hr - 1] if (arm in PLACEBO or hr < OFFER_HOUR) else OFFER_PRICE
                     for arm, hr in zip(h["arm"], h["hour"])]
    s4 = 90 + 10 * (5 * h["ask_index_all_sellers"] - 4 * h["ask_index"])
    s3 = 90 + 10 * (4 * h["ask_index_all_sellers"] - 3 * h["ask_index"])
    ok4 = (s4 - h["expected"]).abs() < 0.006
    ok3 = (s3 - h["expected"]).abs() < 0.006
    if not (ok4 | ok3).all():
        raise ValueError("seat 5's derived ask does not match the replay file")
    h["seat5"] = np.where(ok4, s4, s3)
    h["three_llm"] = ~ok4
    return h, replay


def main():
    s3lib.setup()
    h, replay = derive()
    hours = np.arange(1, 16)
    fig = plt.figure(figsize=(s3lib.SLOT_IN, 7.2))
    axa = fig.add_axes([0.125, 0.585, 0.66, 0.375])
    axb = fig.add_axes([0.125, 0.09, 0.855, 0.37])

    # (a) paths
    s3lib.ref_lines(axa, which=(95.0, 97.5))
    pl = h[h["arm"].isin(PLACEBO)]
    uc = h[~h["arm"].isin(PLACEBO)]
    s5_pl = pl.groupby("hour")["seat5"].mean().to_numpy()
    s5_uc = uc.groupby("hour")["seat5"].mean().to_numpy()
    llm_pl = pl.groupby("hour")["llm_ask"].mean().to_numpy()
    llm_uc = uc.groupby("hour")["llm_ask"].mean().to_numpy()
    axa.axvspan(2.5, 3.5, color="#F2F2F2", lw=0, zorder=0)
    axa.plot(hours, s5_uc, color="black", lw=1.8, marker="s", ms=4.5, zorder=4)
    axa.plot(hours, s5_pl, color="black", lw=1.2, marker="o", ms=4.5, mfc="white", zorder=4)
    axa.plot(hours, llm_uc, color=GEM, lw=2.2, zorder=3)
    axa.plot(hours, llm_pl, color=s3lib.tint(GEM, 0.45), lw=2.2, zorder=3)
    axa.set_xlim(0.6, 15.4)
    axa.set_ylim(92.5, 97.9)
    axa.set_xticks([1, 3, 5, 7, 9, 11, 13, 15])
    axa.set_xlabel("Hour")
    axa.set_ylabel("Ask ($)")
    axa.text(3.0, 92.65, "offer\nsent", ha="center", va="bottom", fontsize=12, color=s3lib.GRAY)
    items = [(s5_uc[-1], "seat 5, offer arms", "black"), (s5_pl[-1], "seat 5, placebo arms", "black"),
             (llm_pl[-1], "sellers, placebo arms", s3lib.tint(GEM, 0.2)),
             (llm_uc[-1], "sellers, offer arms", GEM)]
    style_end_labels(axa, items, 15.7)
    s3lib.panel_letter(axa, "a", x=-0.115, y=1.0)

    # (b) hour-3 asks per market
    h3 = h[h["hour"] == OFFER_HOUR]
    x_of = {a: i for i, a in enumerate(ARMS)}
    axb.axvspan(4.5, 9.5, color=s3lib.style.WARN_BAND, lw=0, zorder=0)
    s3lib.ref_lines(axb, which=(95.0, 97.5))
    axb.axhline(OFFER_PRICE, color="black", lw=1.0, zorder=1)
    rng = np.random.default_rng(1)
    means = {}
    for arm in ARMS:
        y = h3.loc[h3["arm"] == arm, "llm_ask"].to_numpy()
        x = x_of[arm] + rng.uniform(-0.17, 0.17, len(y))
        axb.plot(x, y, "o", ms=6, mfc=s3lib.tint(GEM, 0.3), mec=GEM, mew=0.9, zorder=3)
        means[arm] = y.mean()
        axb.plot([x_of[arm] - 0.3, x_of[arm] + 0.3], [means[arm]] * 2, color="black", lw=2.2, zorder=4)
    axb.set_xticks(range(len(ARMS)))
    axb.set_xticklabels(ARMS)
    axb.set_xlim(-0.6, len(ARMS) - 0.4)
    axb.set_ylim(93.2, 97.9)
    axb.set_ylabel("Sellers' mean ask, hour 3 ($)")
    axb.text(9.45, OFFER_PRICE + 0.08, "offer: hold at $96", ha="right", va="bottom", fontsize=12)
    axb.text(7.0, 93.3, "warning in the prompt", ha="center", va="bottom", fontsize=12, color=s3lib.style.WARN_INK)
    s3lib.panel_letter(axb, "b", x=-0.115, y=1.0)

    # Caption numbers
    print("seat 5 replay path ($):", replay)
    print(f"market-hours with one LLM seller without an ask: {int(h['three_llm'].sum())}",
          h.loc[h["three_llm"], ["run_id", "hour"]].to_dict("records"))
    gap = h["seat5"] - h["llm_ask"]
    print(f"seat 5 above the LLM mean in {int((gap > 0).sum())} of {len(h)} market-hours; "
          f"from hour 4: {int((gap[h.hour >= 4] > 0).sum())} of {int((h.hour >= 4).sum())}")
    print(f"hour-15 LLM mean: placebo {llm_pl[-1]:.2f}, offer {llm_uc[-1]:.2f}; seat 5 {s5_pl[-1]:.2f} / {s5_uc[-1]:.2f}")
    print(f"hour-15 gap seat5 - LLM: placebo {s5_pl[-1] - llm_pl[-1]:.2f}, offer {s5_uc[-1] - llm_uc[-1]:.2f}")
    print("hour-3 arm means:", {a: round(v, 2) for a, v in means.items()})
    nw = h3[h3["arm"].isin(ARMS[:5])]
    print(f"hour-3 no-warning arm means range {min(means[a] for a in ARMS[:5]):.2f} to "
          f"{max(means[a] for a in ARMS[:5]):.2f}; all-arm range {min(means.values()):.2f} to {max(means.values()):.2f}")
    print(f"hour-3 per-market range {h3.llm_ask.min():.2f} to {h3.llm_ask.max():.2f}; no-warning per-market "
          f"{nw.llm_ask.min():.2f} to {nw.llm_ask.max():.2f}; within $1 of $96: "
          f"{int(((h3.llm_ask - 96).abs() <= 1).sum())} of {len(h3)}")
    print(f"hour-1 LLM mean ask by arm: {h[h.hour == 1].groupby('arm').llm_ask.mean().round(2).to_dict()}")
    s3lib.save(fig, "S3_04_seat5.png")


def style_end_labels(ax, items, x):
    s3lib.style.end_labels(ax, items, x, gap_in=0.21)


if __name__ == "__main__":
    main()
