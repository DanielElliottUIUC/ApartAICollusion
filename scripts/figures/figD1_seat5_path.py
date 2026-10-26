"""Appendix Figure D1: seat 5's visible ask by hour in the Gemini undercover market (new sprint code).

The bottom panel of scripts/figures/fig_design_timeline.py on its own, at print size (6.5 x 2.0 in, 300 dpi, every
text at least 8 pt). The market schematic and the analysis windows of that figure are left out: Figure 1 and
Section 3 carry them.

Seat 5's ask in every offer-arm run and every placebo-arm run, read from the runs' own round records by
fig_design_timeline.collect, which also checks that every run of a seat mode logged the same path and that the
placebo path equals configs/replay/base_pilot_norule.json. The band is the lowest to highest of the ten arms' mean
LLM-seller ask in each hour (report/data/dg/market_by_hour.csv, avg_ask averaged over each arm's five markets).

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/figD1_seat5_path.py --runs-dir <repo>/results/dg

Writes report/figures/figD1_seat5_path.png and figD1_seat5_path.caption.txt (caption numbers computed here).
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fig_design_timeline as tl  # noqa: E402  (collect() and the palette)
import printcheck  # noqa: E402
from apartcollusion.runs import arm_sort_key  # noqa: E402  (on sys.path through fig_design_timeline)

REPO = tl.REPO
NAME = "figD1_seat5_path"
W, H = printcheck.TEXT_WIDTH_IN, 2.0
FS = 8.0
AX = (0.50, 0.36, 6.38, 1.92)    # axes left, bottom, right, top, inches


def money(x: float) -> str:
    return f"${x:.2f}"


def band(by_hour_csv: Path, hours: list[int], arms_all: list[str]):
    by_hour = pd.read_csv(by_hour_csv)
    arm_means = by_hour.groupby(["arm", "hour"])["avg_ask"].mean().unstack("arm").reindex(hours)
    if sorted(arm_means.columns, key=arm_sort_key) != arms_all:
        raise SystemExit("market_by_hour.csv arms differ from the runs")
    return arm_means.min(axis=1).tolist(), arm_means.max(axis=1).tolist(), arm_means


def draw(d: dict, lo: list, hi: list, out: Path) -> dict:
    plt.rcParams.update({"font.size": FS, "text.parse_math": False, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(tl.SURFACE)
    x0, y0, x1, y1 = AX
    ax = fig.add_axes((x0 / W, y0 / H, (x1 - x0) / W, (y1 - y0) / H))
    ax.set_facecolor(tl.SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(tl.GRID)
    ax.tick_params(colors=tl.MUTED, labelsize=FS, length=0)
    ax.grid(True, axis="y", color=tl.GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    hrs = d["hours"]
    oh, op = d["offer_hour"], d["offer_price"]
    placebo, offer = d["paths"]["placebo"], d["paths"]["undercover"]
    ax.fill_between(hrs, lo, hi, color=tl.BAND, lw=0, zorder=1)
    ax.plot(hrs, placebo, color=tl.REFERENCE, lw=1.6, zorder=3, solid_capstyle="round")
    ax.plot(hrs, offer, color=tl.SERIES, lw=1.6, zorder=4, solid_capstyle="round")
    ax.plot([oh], [op], "o", ms=5, color=tl.SERIES, mec=tl.SURFACE, mew=1.1, zorder=5)
    ax.axvline(oh, color=tl.MUTED, lw=0.8, ls=(0, (2, 2)), zorder=2)

    ax.set_xlim(0.5, d["rounds"] + 0.5)
    ax.set_ylim(92.0, 98.6)
    ax.set_xticks(hrs)
    ax.set_yticks([92, 94, 96, 98])
    ax.set_yticklabels([f"${t}" for t in (92, 94, 96, 98)])
    ax.set_xlabel("Hour", fontsize=FS, color=tl.MUTED, labelpad=2)

    # direct labels, each in a clear part of the panel
    ax.text(oh + 0.12, 98.5, f"hour {oh}: seat 5 privately sends the {money(op)} offer or a neutral note",
            ha="left", va="top", fontsize=FS, color=tl.MUTED)
    ax.text(oh + 1.3, 97.0, f"placebo arms ({len(d['arms']['placebo'])}): seat 5 replays a pilot seller, "
            f"{money(placebo[0])} to {money(placebo[-1])}", ha="left", va="bottom", fontsize=FS, color=tl.INK)
    ax.text(d["rounds"] + 0.35, op + 0.16, f"offer arms ({len(d['arms']['undercover'])}): seat 5 holds "
            f"{money(op)} from hour {oh}", ha="right", va="bottom", fontsize=FS, color=tl.SERIES)
    ax.text(oh + 0.3, 92.9, "band: LLM sellers' mean ask, lowest to highest of the ten arm means",
            ha="left", va="center", fontsize=FS, color=tl.MUTED)
    out.parent.mkdir(parents=True, exist_ok=True)
    m = printcheck.save(fig, out, max_h_in=H)
    plt.close(fig)
    return m


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", type=Path, default=REPO / "results" / "dg", help="the Gemini D-G runs")
    ap.add_argument("--replay", type=Path, default=REPO / "configs" / "replay" / "base_pilot_norule.json")
    ap.add_argument("--by-hour", type=Path, default=REPO / "report" / "data" / "dg" / "market_by_hour.csv")
    ap.add_argument("--out-dir", type=Path, default=REPO / "report" / "figures")
    args = ap.parse_args()
    d = tl.collect(args.runs_dir, args.replay)
    lo, hi, arm_means = band(args.by_hour, d["hours"], d["arms"]["all"])
    oh = d["offer_hour"]
    h3 = arm_means.loc[oh]
    m = draw(d, lo, hi, args.out_dir / f"{NAME}.png")

    placebo = d["paths"]["placebo"]
    caption = (
        f"Figure D1. Seat 5's visible ask by hour in the {d['n_runs']} Gemini undercover markets. In the "
        f"{len(d['arms']['placebo'])} placebo arms seat 5 replays a pilot seller's asks ({money(placebo[0])} to "
        f"{money(placebo[-1])}); in the {len(d['arms']['undercover'])} offer arms it asks the same "
        f"{money(placebo[0])} in hours 1 and 2 and a flat {money(d['offer_price'])} from hour {oh}, when it sends "
        f"the offer (sellers see it from hour {d['seen_hour']}). Every run of each kind logged the same path. "
        f"The band spans the ten arms' mean ask of the four LLM sellers ({money(h3.min())} in {h3.idxmin()} to "
        f"{money(h3.max())} in {h3.idxmax()} at hour {oh}), so the offer sat at about the going price, and from "
        f"hour {oh} offer arms differ from the placebo in seat 5's visible price as well as in its message."
    )
    details = (
        f"Made by scripts/figures/{NAME}.py (new sprint code; the bottom panel of fig_design_timeline.py, reusing its "
        f"collect()), at print size {m['width_in']} x {m['height_in']} in, 300 dpi ({m['px'][0]} x {m['px'][1]} px), "
        f"smallest text {m['min_font_pt']} pt. Appendix D.1, replacing fig_design_timeline.png as Figure D1.\n"
        f"Numbers printed, checked: seat 5's paths are read from the round records of all {d['n_runs']} runs in "
        f"--runs-dir; every run of a seat mode logged the same path, and the placebo path equals "
        f"configs/replay/base_pilot_norule.json (both asserted): placebo {money(placebo[0])} at hour 1 to "
        f"{money(placebo[-1])} at hour 15; offer arms {money(d['paths']['undercover'][0])} in hours 1 and 2 and "
        f"{money(d['offer_price'])} from hour {oh} (offer_price and offer_hour from experiment_metadata.json, one "
        f"value across runs); {len(d['arms']['placebo'])} placebo arms ({', '.join(d['arms']['placebo'])}) and "
        f"{len(d['arms']['undercover'])} offer arms ({', '.join(d['arms']['undercover'])}) from seat_mode. The band "
        f"is the per-hour min and max over the ten arms of the seed-mean avg_ask in report/data/dg/market_by_hour.csv; "
        f"at hour {oh}: {money(h3.min())} to {money(h3.max())}, matching Table D2b's hour-3 column. Otherwise axis "
        f"ticks only.\n"
        "Regenerate: cd third_party/llm-agent-collusion && PYTHONUTF8=1 uv run python "
        "../../scripts/figures/figD1_seat5_path.py --runs-dir C:/Users/danie/Hackathons/ApartAICollusion/results/dg"
    )
    (args.out_dir / f"{NAME}.caption.txt").write_text(caption + "\n\n" + details + "\n", encoding="utf-8")
    print(caption)
    print("placebo path", placebo)
    print("offer path", d["paths"]["undercover"])
    print("band lo", [round(x, 3) for x in lo])
    print("band hi", [round(x, 3) for x in hi])
    print(f"hour-{oh} arm means:", h3.round(3).to_dict())
    print(m)


if __name__ == "__main__":
    main()
