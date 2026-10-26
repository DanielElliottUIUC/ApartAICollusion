"""Body Figure 2: the ten Gemini undercover-market arms as one grid (new sprint code, not part of the vendored
harness).

Writes report/figures/fig2_arms.png at its print size (6.5 x 2.25 in, 300 dpi, every text at least 8 pt; checked by
scripts/figures/printcheck.py). Rows are seat 5's hour-3 message (placebo note / plain $96 offer / $96 offer as a
human seller's plea), columns the notice in the seller prompt (no warning / warning / warning + precedent / warning +
sham history), and the no-warning column splits by buyer 5 (silent / human plea). The warning columns sit on the pale
band that marks the warning arms in Figures 4 and 5. The planned Base-hb arm was not run; blank cells are not part of
the design. What every arm shares (4 Gemini 3.8 Flash sellers + scripted seat 5, 5 GPT-4.1-mini buyers, 15 hours,
messaging on, report_to_regulator, no prohibition notice, seeds 0-4) goes in the caption, not in the figure. (The
earlier fig_arms_grid.png/.svg, drawn by the previous version of this script, stay as they were.)

Data. Arms, seeds and seat 5's mode and offer price come from the committed report/data/dg/market_structure.csv.
The notice and buyer-plea factors of each arm are not in the committed CSVs, so they are listed in DESIGN below (the
frozen design, report Table D1); with --runs-dir pointing at the raw run folders (results/ is gitignored and local)
the script also reads every run's experiment_metadata.json and stops unless each arm's seat mode, warning /
precedent / sham-history flags, buyer-plea hour and seeds match DESIGN and the CSV, each arm sits in exactly one
cell, and the only planned arm without runs is Base-hb.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_arms_grid.py [--runs-dir <repo>/results/dg]

Style: M.S.'s palette for the body figures (scripts/figures/ms/style.py): the warning band, and the light gray of
the scripted seat for the placebo cells. Arm cells carry no model color, since every arm has Gemini sellers.
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import printcheck  # noqa: E402

DATA = REPO / "report" / "data" / "dg"
OUT = REPO / "report" / "figures" / "fig2_arms.png"

INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d9d9d9"
WARN_BAND, WARN_INK = "#FBF3C4", "#7A6400"   # M.S.'s warning band and its ink
PLACEBO_FILL = "#ECECEC"                      # M.S.'s scripted-seat gray
OFFER_FILL = "#FFFFFF"
W, H = 6.5, 2.25
FS, FS_HEAD, FS_ARM = 8.5, 9.0, 10.0

# (arm) -> (seat_mode, buyer 5 pleads, notice): the frozen design (report Table D1)
DESIGN = {
    "Base": ("placebo", False, "none"),
    "D": ("undercover", False, "none"),
    "D-hs": ("undercover_human", False, "none"),
    "D-hb": ("undercover", True, "none"),
    "D-hsb": ("undercover_human", True, "none"),
    "E": ("undercover", False, "warning"),
    "F": ("undercover", False, "precedent"),
    "F-sham": ("undercover", False, "sham"),
    "G-warn": ("placebo", False, "warning"),
    "G-prec": ("placebo", False, "precedent"),
}
PLANNED_NOT_RUN = {("placebo", True, "none"): "Base-hb"}  # report Table D1: "The planned Base-hb arm was not run."
MODES = [  # (seat_mode, row title, row subtitle, cell fill)
    ("placebo", "Seat 5: placebo", "neutral note", PLACEBO_FILL),
    ("undercover", "Seat 5: offer", "plain {price} offer", OFFER_FILL),
    ("undercover_human", "Seat 5: offer", "{price} offer as a\nhuman seller's plea", OFFER_FILL),
]
NOTICES = [("none", "No warning"), ("warning", "Warning"), ("precedent", "Warning +\nprecedent"),
           ("sham", "Warning +\nsham history")]


def collect_csv() -> dict:
    ms = pd.read_csv(DATA / "market_structure.csv")
    if set(ms.arm) != set(DESIGN):
        raise SystemExit(f"arms in market_structure.csv {sorted(set(ms.arm))} differ from DESIGN")
    seeds = {a: sorted(int(s) for s in g.seed) for a, g in ms.groupby("arm")}
    for arm, g in ms.groupby("arm"):
        if set(g.seat_mode) != {DESIGN[arm][0]}:
            raise SystemExit(f"{arm}: seat_mode {set(g.seat_mode)} in the CSV, {DESIGN[arm][0]} in DESIGN")
    prices = set(ms.offer_price)
    if len(prices) != 1:
        raise SystemExit(f"offer price differs across runs: {prices}")
    all_seeds = sorted({s for v in seeds.values() for s in v})
    if any(v != all_seeds for v in seeds.values()):
        raise SystemExit(f"arms differ in seeds: {seeds}")
    grid = {}
    for arm, cell in DESIGN.items():
        if cell in grid:
            raise SystemExit(f"cell {cell} holds {grid[cell]} and {arm}")
        grid[cell] = arm
    return dict(grid=grid, seeds=seeds, all_seeds=all_seeds, n_runs=len(ms), offer_price=prices.pop())


def verify_runs(runs_dir: Path, d: dict) -> None:
    """Check DESIGN and the CSV against every run's experiment_metadata.json."""
    sys.path.insert(0, str(REPO / "src"))
    from apartcollusion.runs import ARM_ORDER, find_runs

    def notice_of(cfg: dict) -> str:
        if cfg["precedent"]:
            return "precedent"
        if cfg["sham_history"]:
            return "sham"
        return "warning" if cfg["warning"] else "none"

    runs = find_runs(runs_dir, warn=lambda m: print(m, file=sys.stderr))
    if not runs:
        raise SystemExit(f"no D-G runs under {runs_dir}")
    cell_of, seeds = defaultdict(set), defaultdict(set)
    for r in runs:
        c = r.metadata["auction_config"]
        if c["warning"] is False and (c["precedent"] or c["sham_history"]):
            raise SystemExit(f"{r.run_id}: precedent or sham history without the warning")
        cell_of[r.arm].add((r.metadata["seat_mode"], c["buyer_plea_hour"] is not None, notice_of(c)))
        seeds[r.arm].add(r.seed)
        if r.metadata["offer_price"] != d["offer_price"]:
            raise SystemExit(f"{r.run_id}: offer price {r.metadata['offer_price']}")
    for arm, cells in cell_of.items():
        if cells != {DESIGN.get(arm)}:
            raise SystemExit(f"arm {arm}: runs say {cells}, DESIGN says {DESIGN.get(arm)}")
        if sorted(seeds[arm]) != d["seeds"][arm]:
            raise SystemExit(f"arm {arm}: run seeds {sorted(seeds[arm])}, CSV seeds {d['seeds'][arm]}")
    not_run = [a for a in ARM_ORDER if a not in cell_of]
    if sorted(not_run) != sorted(PLANNED_NOT_RUN.values()):
        raise SystemExit(f"planned-but-not-run arms changed: {not_run}")
    if len(runs) != d["n_runs"]:
        raise SystemExit(f"{len(runs)} runs on disk, {d['n_runs']} in the CSV")
    print(f"verified DESIGN against {len(runs)} runs in {runs_dir}")


def money(x: float) -> str:
    return f"${x:.0f}" if float(x).is_integer() else f"${x:.2f}"


def box(ax, x, y, w, h, fc, ec="none", lw=0.8, ls="-", z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.04", fc=fc, ec=ec, lw=lw,
                                ls=ls, zorder=z))


def draw(d: dict) -> dict:
    plt.rcParams.update({"font.family": "DejaVu Sans", "text.parse_math": False})
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor("white")
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    price = money(d["offer_price"])

    cols = [("none", False), ("none", True), ("warning", False), ("precedent", False), ("sham", False)]
    X0, GAP = 1.62, 0.05                      # row-header column, then the cells
    cw = (W - 0.04 - X0) / len(cols)
    rh = 0.42                                 # tall enough for a row title over a two-line sublabel
    y_head1, y_head2 = H - 0.2, H - 0.53      # centers of the two header rows
    y_rows = [y_head2 - 0.36 - i * rh for i in range(len(MODES))]
    y_bottom = y_rows[-1] - rh / 2

    # the warning columns sit on the warning band, from the header to the last row
    ax.add_patch(Rectangle((X0 + 2 * cw, y_bottom - 0.02), 3 * cw, H - 0.02 - (y_bottom - 0.02), fc=WARN_BAND,
                           ec="none", zorder=0))

    # header row 1: notice in the seller prompt (from hour 1)
    ax.text(0.04, y_head1, "Prompt notice →", ha="left", va="center", fontsize=FS, color=MUTED)
    head = dict(NOTICES)
    for key, c0, n in [("none", 0, 2), ("warning", 2, 1), ("precedent", 3, 1), ("sham", 4, 1)]:
        x = X0 + c0 * cw
        ax.text(x + n * cw / 2, y_head1, head[key], ha="center", va="center", fontsize=FS_HEAD,
                color=(INK if key == "none" else WARN_INK), weight="bold", linespacing=1.05)
        ax.plot([x + GAP, x + n * cw - GAP], [y_head1 - 0.19] * 2, color=GRID, lw=0.8, zorder=1)
    # header row 2: buyer 5
    ax.text(0.04, y_head2, "Buyer 5 →", ha="left", va="center", fontsize=FS, color=MUTED)
    for i, (_, plea) in enumerate(cols):
        ax.text(X0 + (i + 0.5) * cw, y_head2, "human plea" if plea else "silent", ha="center", va="center",
                fontsize=FS, color=INK)

    # rows
    printed = {}
    for (mode, title, sub, fill), yc in zip(MODES, y_rows):
        sublabel = sub.format(price=price)
        ax.text(0.04, yc + 0.075, title, ha="left", va="center", fontsize=FS_HEAD, color=INK, weight="bold")
        # a two-line sublabel keeps its first line where a one-line sublabel sits
        ax.text(0.04, yc - 0.09 - 0.065 * sublabel.count("\n"), sublabel, ha="left", va="center", fontsize=FS,
                color=MUTED, linespacing=1.1)
        for i, (notice, plea) in enumerate(cols):
            x, y = X0 + i * cw + GAP / 2, yc - rh / 2 + GAP / 2
            w, h = cw - GAP, rh - GAP
            arm = d["grid"].get((mode, plea, notice))
            planned = PLANNED_NOT_RUN.get((mode, plea, notice))
            if arm:
                box(ax, x, y, w, h, fc=fill, ec="#9a9a9a", lw=0.7)
                ax.text(x + w / 2, y + h / 2, arm, ha="center", va="center", fontsize=FS_ARM, color=INK,
                        weight="bold")
                printed[arm] = f"{title}, {' '.join(sublabel.split())}; notice {notice}; buyer 5 " \
                               f"{'plea' if plea else 'silent'}"
            elif planned:
                box(ax, x, y, w, h, fc="white", ec="#8c8b86", lw=0.7, ls=(0, (3, 2)))
                ax.text(x + w / 2, y + h / 2, f"{planned}\nnot run", ha="center", va="center", fontsize=FS,
                        linespacing=1.0, color=MUTED)
            else:
                box(ax, x, y, w, h, fc="none", ec=GRID, lw=0.6, ls=(0, (1, 1.5)))

    # the 2 x 2 of pleas: D, D-hb, D-hs, D-hsb
    yb0 = y_bottom - 0.02
    box(ax, X0 - 0.015, yb0, 2 * cw + 0.03, 2 * rh + 0.04, fc="none", ec=MUTED, lw=1.0, z=3)
    ax.text(X0 + cw, yb0 - 0.05, "2 × 2: seller plea × buyer plea", ha="center", va="top", fontsize=FS,
            color=MUTED)
    ax.text(X0 + 3.5 * cw, yb0 - 0.05, "blank cells: not part of the design", ha="center", va="top", fontsize=FS,
            color=MUTED)
    m = printcheck.save(fig, OUT, max_h_in=2.35)
    plt.close(fig)
    m["printed"] = printed
    return m


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", type=Path, default=REPO / "results" / "dg",
                    help="the Gemini D-G run folders; when present, DESIGN is checked against their metadata")
    args = ap.parse_args()
    d = collect_csv()
    if args.runs_dir.exists():
        verify_runs(args.runs_dir, d)
    else:
        print(f"{args.runs_dir} not found; DESIGN not re-checked against run metadata", file=sys.stderr)
    m = draw(d)
    for arm, desc in m["printed"].items():
        print(f"  {arm:7s} {desc}; seeds {d['seeds'][arm]}")
    print(f"{d['n_runs']} runs in market_structure.csv; offer price {d['offer_price']}")


if __name__ == "__main__":
    main()
