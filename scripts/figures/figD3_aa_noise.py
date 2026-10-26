"""Appendix Figure D4: run-to-run noise at hour 3, an A/A check (new sprint code).

A print-size redraw of scripts/figures/fig_aa_noise.py (6.5 x 3.0 in, 300 dpi, every text at least 8 pt). Change:
the second bracket of that figure, which set the spread of arm means in hour-3 ask *levels* beside the largest
arm-vs-Base gap in post-offer ask *change*, is gone, because the two are different quantities; the ask-change gap
moves to the caption with that caveat. In its place a bracket shows the largest same-seed range across the arms.

Base, D, D-hs, D-hb and D-hsb give the Gemini sellers identical prompts through hour 3 (the offer or placebo note
is sent at hour 3 and visible from hour 4), so any difference in their hour-3 asks is noise. One dot per market
(seed) at the mean hour-3 ask of its four LLM sellers; within each arm the seeds sit on fixed sub-rows (seed 0 on
top), so the same seed can be followed across arms, and the seed with the largest range across arms is drawn with
a dark ring; a black tick marks the arm mean.

Sources (nothing is taken from the report text):
  - report/data/dg/market_by_hour.csv, hour 3, column avg_ask (mean ask of the four LLM sellers; seat 5 excluded);
    cross-checked against report/data/dg/outcomes.csv ask_pre averaged per run (asserted equal).
  - report/data/dg/outcomes.csv, ask_change_post_offer (per seller-episode), for the caption's ask-change gap.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/figD3_aa_noise.py

Writes report/figures/figD3_aa_noise.png and figD3_aa_noise.caption.txt (caption numbers computed here).
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import printcheck  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "report" / "data" / "dg"
OUT = REPO / "report" / "figures"
NAME = "figD3_aa_noise"
W, H = printcheck.TEXT_WIDTH_IN, 3.0
FS = 8.0

# Reference palette from the dataviz skill (light mode), as in fig_aa_noise.py.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"     # one market (seed)
REFERENCE = "#8c8b86"  # within-arm range

ARMS = ["Base", "D", "D-hs", "D-hb", "D-hsb"]   # identical seller prompts through hour 3
ARM_NOTE = {"Base": "placebo note", "D": "plain offer", "D-hs": "seller plea", "D-hb": "buyer plea",
            "D-hsb": "both pleas"}
HOUR = 3
SEEDS = range(5)
SUB = 0.15  # vertical step between seed sub-rows (row pitch = 1)


def money(x: float) -> str:
    return f"${x:.2f}"


def main() -> None:
    mbh = pd.read_csv(DATA / "market_by_hour.csv")
    h3 = mbh[(mbh["hour"] == HOUR) & mbh["arm"].isin(ARMS)].set_index(["arm", "seed"])["avg_ask"].sort_index()
    out = pd.read_csv(DATA / "outcomes.csv")
    pre = out[out["arm"].isin(ARMS)].groupby(["arm", "seed"])["ask_pre"].mean().sort_index()
    assert len(h3) == 25 and (h3 - pre).abs().max() < 1e-9, "hour-3 asks disagree between the two CSVs"

    arm_mean = h3.groupby("arm").mean().reindex(ARMS)
    arm_min, arm_max = h3.groupby("arm").min().reindex(ARMS), h3.groupby("arm").max().reindex(ARMS)
    spread = arm_mean.max() - arm_mean.min()
    by_seed = h3.unstack("arm")[ARMS]
    seed_range = by_seed.max(axis=1) - by_seed.min(axis=1)
    worst = int(seed_range.idxmax())

    change = out.groupby("arm")["ask_change_post_offer"].mean()
    diff_vs_base = change.drop("Base") - change["Base"]
    biggest_arm = diff_vs_base.abs().idxmax()
    biggest = diff_vs_base[biggest_arm]

    plt.rcParams.update({"font.size": FS, "text.parse_math": False, "font.family": "DejaVu Sans"})
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes((1.62 / W, 0.42 / H, (5.18 - 1.62) / W, (2.92 - 0.42) / H))
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=FS, length=0)
    ax.grid(True, axis="x", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)

    rows = {arm: len(ARMS) - 1 - i for i, arm in enumerate(ARMS)}  # Base on top
    for arm, y in rows.items():
        ax.plot([arm_min[arm], arm_max[arm]], [y, y], color=REFERENCE, linewidth=0.9, zorder=1)
        ax.plot([arm_mean[arm]] * 2, [y - 0.36, y + 0.36], color=INK, linewidth=1.6, solid_capstyle="butt",
                zorder=2)
        for s in SEEDS:
            ring = s == worst
            ax.plot(h3[(arm, s)], y + (2 - s) * SUB, linestyle="none", marker="o", markersize=5.6, color=SERIES,
                    markeredgecolor=(INK if ring else SURFACE), markeredgewidth=(1.1 if ring else 1.2), zorder=3)
        ax.text(1.02, y, f"{money(arm_mean[arm])}  ({money(arm_max[arm] - arm_min[arm])})", fontsize=FS,
                color=INK, va="center", ha="left", transform=ax.get_yaxis_transform())

    head = len(ARMS) - 0.38
    ax.text(93.65, head, f"in each arm, seeds 0 to 4 top to bottom; ringed: seed {worst}",
            fontsize=FS, color=MUTED, va="center", ha="left")
    ax.text(1.02, head, "arm mean (range)", fontsize=FS, color=MUTED, va="center", ha="left",
            transform=ax.get_yaxis_transform())

    # brackets at their true positions: the spread of the arm means, and the largest same-seed range across arms
    lo_m, hi_m = arm_mean.min(), arm_mean.max()
    lo_s, hi_s = by_seed.loc[worst].min(), by_seed.loc[worst].max()
    for yb, x0, x1, color, left, right in [
        (-0.75, lo_m, hi_m, INK, "spread of arm means", money(spread)),
        (-1.25, lo_s, hi_s, INK, f"seed {worst} across arms", money(seed_range[worst])),
    ]:
        ax.plot([x0, x0, x1, x1], [yb + 0.12, yb, yb, yb + 0.12], color=color, linewidth=0.9)
        ax.text(x1 + 0.08, yb + 0.04, f"{left}: {right}", fontsize=FS, color=INK, ha="left", va="center")

    ax.set_yticks(list(rows.values()))
    ax.set_yticklabels([f"{a} ({ARM_NOTE[a]})" for a in rows], fontsize=FS, color=INK)
    ax.set_ylim(-1.5, len(ARMS) - 0.15)
    ax.set_xlim(93.6, 97.75)
    ax.set_xticks([94, 95, 96, 97])
    ax.xaxis.set_major_formatter(lambda v, _: f"${v:.0f}")
    ax.set_xlabel(f"Mean ask of the four LLM sellers at hour {HOUR} (one dot per market)", fontsize=FS, color=MUTED)
    m = printcheck.save(fig, OUT / f"{NAME}.png", max_h_in=H)
    plt.close(fig)

    lo_arm, hi_arm = arm_mean.idxmin(), arm_mean.idxmax()
    caption = (
        "Figure D4. Hour-3 mean ask of the four LLM sellers in each market (dots, one per seed; black tick: arm "
        "mean) in the five Gemini arms whose prompts are identical through hour 3. The arm means span "
        f"{money(spread)} ({money(arm_mean[lo_arm])} in {lo_arm} to {money(arm_mean[hi_arm])} in {hi_arm}), and the "
        f"same seed differs across these arms by up to {money(seed_range[worst])} (seed {worst}, ringed), so "
        "differences of this size are run-to-run noise. For scale only: the largest arm-against-Base difference "
        f"in post-offer ask change (mean ask in hours 4 to 6 minus hour 3) is {money(abs(biggest))} ({biggest_arm}); "
        "that is a change within a market, not a level, so it is not directly comparable with the spread of "
        "hour-3 levels."
    )
    details = (
        f"Made by scripts/figures/{NAME}.py (new sprint code; a redraw of fig_aa_noise.py without its level-against-"
        f"change bracket), at print size {m['width_in']} x {m['height_in']} in, 300 dpi ({m['px'][0]} x {m['px'][1]} "
        f"px), smallest text {m['min_font_pt']} pt. Appendix D.1, replacing fig_aa_noise.png as Figure D4.\n"
        "Numbers printed, checked (report/data/dg/market_by_hour.csv, hour 3, avg_ask, asserted equal to the per-run "
        "mean of outcomes.csv ask_pre): arm mean (range) "
        + "; ".join(f"{a} {money(arm_mean[a])} ({money(arm_max[a] - arm_min[a])})" for a in ARMS)
        + f", matching Table D2b's hour-3 column; spread of arm means {money(spread)}; seed {worst} across the five "
        f"arms {money(by_seed.loc[worst].min())} to {money(by_seed.loc[worst].max())} = {money(seed_range[worst])} "
        "(other seeds: "
        + ", ".join(f"{k} {money(seed_range[k])}" for k in SEEDS if k != worst)
        + f"). Caption only: the largest |arm minus Base| in mean ask_change_post_offer over the ten Gemini arms is "
        f"{money(abs(biggest))} ({biggest_arm}). Section 4.5's '$1.28 in hour-3 mean asks' matches.\n"
        "Regenerate: cd third_party/llm-agent-collusion && PYTHONUTF8=1 uv run python "
        "../../scripts/figures/figD3_aa_noise.py"
    )
    (OUT / f"{NAME}.caption.txt").write_text(caption + "\n\n" + details + "\n", encoding="utf-8")
    print(by_seed.round(4).to_string())
    print(pd.DataFrame({"mean": arm_mean, "min": arm_min, "max": arm_max}).round(4).to_string())
    print("seed range across arms:", seed_range.round(4).to_dict())
    print("ask change minus Base:", diff_vs_base.round(4).to_dict())
    print(caption)
    print(m)


if __name__ == "__main__":
    main()
