"""Figure S3.3: which part of the joint criterion decides each market.

The joint criterion (report section 3.1): over the last third of hours, ask index > 0.5, trade-price index > 0.25
and at least 1 trade per hour. All 178 markets with a computable criterion from both halves:
  D.E.: data/daniel/dg/market_by_run.csv (50 Gemini undercover markets), dg_gpt41/market_by_run.csv (15),
        dg_haiku/market_by_run.csv (3), c/c_by_run.csv (18 step C markets); indices over the LLM sellers.
  M.S.: data/S3/runs.csv, every run with 15 logged hours (92 of 93; the broken-log GGGG seed 0 run is left out).
(a) Ask index against trade index per market. Filled markers pass; a black cross marks markets with fewer than
    1 trade per hour (legend: low volume). (b) Number of markets in each outcome, split by half.
The script checks that the stored pass flags equal the recomputed criterion and prints every caption number.
Output: supplement/figures/S3/S3_03_criterion.png
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
COLS = ["market", "seller", "half", "ask_index", "trade_index", "trades_per_round", "passed"]
HALF_SHADE = {"D.E.": "#4D4D4D", "M.S.": "#A9A9A9"}


def load():
    parts = []
    for fam, seller in (("dg", "gemini"), ("dg_gpt41", "gpt41"), ("dg_haiku", "haiku")):
        x = pd.read_csv(s3lib.DANIEL / fam / "market_by_run.csv")
        parts.append(x.assign(market=x["run_id"], seller=seller, half="D.E.")[COLS])
    c = pd.read_csv(s3lib.DANIEL / "c" / "c_by_run.csv")
    parts.append(c.assign(market=c["run_id"], seller="gemini", half="D.E.")[COLS])
    r = pd.read_csv(s3lib.S3DATA / "runs.csv")
    r = r[r["hours_logged"] == 15]
    parts.append(r.assign(market=r["folder"], half="M.S.")[COLS])
    a = pd.concat(parts, ignore_index=True)
    a["ok_ask"] = a["ask_index"] > 0.5
    a["ok_trade"] = a["trade_index"] > 0.25
    a["ok_vol"] = a["trades_per_round"] >= 1
    if not ((a["ok_ask"] & a["ok_trade"] & a["ok_vol"]) == a["passed"].astype(bool)).all():
        raise ValueError("stored pass flags differ from the recomputed criterion")
    return a


def outcome(row):
    if row.passed:
        return "passes"
    if not row.ok_vol and row.ok_ask and row.ok_trade:
        return "fails on volume only"
    if not row.ok_vol:
        return "fails on volume and price"
    if not row.ok_trade:
        return "fails on ask and trade price"
    return "fails on ask only"


ORDER = ["passes", "fails on ask only", "fails on ask and trade price", "fails on volume only",
         "fails on volume and price"]


def main():
    s3lib.setup()
    a = load()
    a["outcome"] = [outcome(r) for r in a.itertuples()]
    if set(a["outcome"]) - set(ORDER):
        raise ValueError("unexpected outcome")
    fig = plt.figure(figsize=(s3lib.SLOT_IN, 7.0))
    axa = fig.add_axes([0.135, 0.43, 0.845, 0.53])
    axb = fig.add_axes([0.445, 0.075, 0.43, 0.25])

    # (a) scatter
    axa.add_patch(plt.Rectangle((0.5, 0.25), 0.4, 0.65, facecolor="#EFEFEF", edgecolor="none", zorder=0))
    axa.plot([-0.9, 0.9], [-0.9, 0.9], color=s3lib.LIGHT, lw=0.8, zorder=0.5)
    axa.axvline(0.5, color=s3lib.GRAY, ls=(0, (1, 2)), lw=1.6, zorder=0.6)
    axa.plot([0.5, 0.9], [0.25, 0.25], color=s3lib.GRAY, ls=(0, (1, 2)), lw=1.0, zorder=0.6)
    for half, mk in (("D.E.", "o"), ("M.S.", "s")):
        for seller in ["gemini", "gpt41", "haiku", "sol", "luna", "grok"]:
            g = a[(a["half"] == half) & (a["seller"] == seller)]
            if g.empty:
                continue
            for passed, sub in g.groupby("passed"):
                axa.plot(sub["ask_index"], sub["trade_index"], mk, ms=6.3 if mk == "o" else 5.6,
                         mfc=C[seller] if passed else "white", mec=C[seller], mew=1.1, alpha=0.9, zorder=3)
    vol = a[~a["ok_vol"]]
    axa.plot(vol["ask_index"], vol["trade_index"], "x", ms=6.5, mew=1.4, color="black", zorder=4)
    axa.set_xlim(-0.9, 0.9)
    axa.set_ylim(-0.9, 0.9)
    axa.set_xticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75])
    axa.set_yticks([-0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75])
    axa.set_xlabel("Ask index, last third")
    axa.set_ylabel("Trade-price index, last third")
    axa.text(0.52, 0.86, "pass region", fontsize=12, ha="left", va="top", color=s3lib.GRAY)
    # Legend in the empty upper-left corner: seller colors as text, half as marker shape.
    sellers = [("gemini", "Gemini 3.8 Flash"), ("gpt41", "GPT-4.1"), ("haiku", "Claude Haiku 5.5"),
               ("sol", "GPT-5.6 Sol"), ("luna", "GPT-6 Luna"), ("grok", "Grok 4.7")]
    for i, (k, nm) in enumerate(sellers):
        axa.text(-0.86, 0.84 - i * 0.115, nm, color=C[k], fontsize=12, ha="left", va="top")
    handles = [Line2D([], [], ls="", marker="o", ms=6.3, mfc="white", mec=s3lib.GRAY, mew=1.1, label="D.E.'s markets"),
               Line2D([], [], ls="", marker="s", ms=5.6, mfc="white", mec=s3lib.GRAY, mew=1.1, label="M.S.'s markets"),
               Line2D([], [], ls="", marker="o", ms=6.3, mfc=s3lib.GRAY, mec=s3lib.GRAY, label="passes"),
               Line2D([], [], ls="", marker="x", ms=6.5, mew=1.4, color="black", label="low volume")]
    axa.legend(handles=handles, loc="lower right", bbox_to_anchor=(0.765, 0.0), frameon=False, fontsize=12,
               handletextpad=0.3, borderaxespad=0.3, labelspacing=0.25)
    s3lib.panel_letter(axa, "a", x=-0.13, y=1.0)

    # (b) outcome counts by half
    counts = a.groupby(["outcome", "half"]).size().unstack(fill_value=0).reindex(ORDER).fillna(0).astype(int)
    y = np.arange(len(ORDER))[::-1]
    left = np.zeros(len(ORDER))
    for half in ["D.E.", "M.S."]:
        v = counts[half].to_numpy()
        axb.barh(y, v, left=left, height=0.62, color=HALF_SHADE[half], edgecolor="white", lw=0.6)
        left += v
    for yi, tot in zip(y, left):
        axb.text(tot + 2, yi, f"{int(tot)}", va="center", ha="left", fontsize=12)
    axb.set_yticks(y)
    axb.set_yticklabels(ORDER)
    axb.set_xlabel("Markets")
    axb.set_xlim(0, max(left) * 1.12)
    axb.tick_params(axis="y", length=0)
    from matplotlib.patches import Patch
    axb.legend(handles=[Patch(facecolor=HALF_SHADE[h], label=f"{h}'s markets") for h in ("D.E.", "M.S.")],
               loc="lower right", frameon=False, fontsize=12, handlelength=1.0, handletextpad=0.4)
    s3lib.panel_letter(axb, "b", x=-0.73, y=1.0)

    # Caption numbers
    n = len(a)
    print(f"markets {n}: D.E. {int((a.half == 'D.E.').sum())}, M.S. {int((a.half == 'M.S.').sum())}; "
          f"passing {int(a.passed.sum())}")
    print(counts.assign(total=counts.sum(axis=1)).to_string())
    fail = a[~a["passed"]]
    print(f"failing {len(fail)}; failing the ask condition {int((~fail.ok_ask).sum())}; "
          f"failing trade without ask {int(((~fail.ok_trade) & fail.ok_ask).sum())}")
    print(f"ask condition met {int(a.ok_ask.sum())}, of which fail {int((a.ok_ask & ~a.passed).sum())}")
    print(f"correlation ask/trade {np.corrcoef(a.ask_index, a.trade_index)[0, 1]:.3f}; "
          f"median |trade - ask| {np.median(np.abs(a.trade_index - a.ask_index)):.4f}")
    near_lo = a[(a.ask_index > 0.45) & (a.ask_index <= 0.5)]
    near_hi = a[(a.ask_index > 0.5) & (a.ask_index <= 0.55)]
    print(f"ask index in (0.45, 0.50]: {len(near_lo)} (D.E. {int((near_lo.half == 'D.E.').sum())}); "
          f"in (0.50, 0.55]: {len(near_hi)}")
    s3lib.save(fig, "S3_03_criterion.png")


if __name__ == "__main__":
    main()
