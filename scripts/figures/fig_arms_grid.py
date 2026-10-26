"""Figure: the ten Gemini D-G arms as one grid (new sprint code, not part of the vendored harness).

Writes report/figures/fig_arms_grid.{svg,png} at Letter text width (6.5 in). Rows are seat 5's hour-3 message
(placebo note / plain $96 offer / human-plea $96 offer), columns the notice in the seller prompt (none / warning /
warning + precedent / warning + sham history), and the no-notice column splits by buyer 5 (silent / human plea).
Each filled cell names its arm and its seeds.

The grid is built from the runs themselves: every run's experiment_metadata.json gives its arm, seat_mode,
warning / precedent / sham_history flags and buyer_plea_hour, and the script checks that each arm sits in exactly
one cell and each cell holds at most one arm. The one cell that is not read from the runs is the planned Base-hb
arm, which was never run (report Table 1; it is the only arm in apartcollusion.runs.ARM_ORDER with no runs).

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_arms_grid.py --runs-dir <repo>/results/dg

Style: the dataviz reference palette (light), the same tokens as scripts/make_dg_figures.py; categorical slots 1-2
(blue, orange) for the two undercover messages, the reference gray for the placebo seat. Every row also carries its
name, so nothing relies on colour alone.
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from apartcollusion.runs import ARM_ORDER, arm_sort_key, find_runs  # noqa: E402

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"     # slot 1: plain offer
SERIES_2 = "#eb6834"   # slot 2: human-plea offer
REFERENCE = "#8c8b86"  # placebo seat
W, H = 6.5, 2.5
FS = 8
L = 0.03

MODES = [  # (seat_mode in metadata, row title, row subtitle, accent)
    ("placebo", "Seat 5: placebo", "neutral note", REFERENCE),
    ("undercover", "Seat 5: undercover", "plain {price} offer", SERIES),
    ("undercover_human", "Seat 5: undercover", "human-plea {price} offer", SERIES_2),
]
NOTICES = [  # (key, column header)
    ("none", "No notice"),
    ("warning", "Warning"),
    ("precedent", "Warning +\nprecedent"),
    ("sham", "Warning +\nsham history"),
]
PLANNED_NOT_RUN = {("placebo", True, "none"): "Base-hb"}  # report Table 1: "The planned Base-hb arm was not run."
PRETTY = {"google/gemini-3.8-flash": "Gemini 3.8 Flash", "openai/gpt-4.1-mini": "GPT-4.1-mini"}


def wash(hex_color: str, alpha: float) -> str:
    """hex_color at `alpha` opacity over SURFACE, as an opaque hex."""
    c = [int(hex_color[i:i + 2], 16) for i in (1, 3, 5)]
    s = [int(SURFACE[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(alpha * a + (1 - alpha) * b):02x}" for a, b in zip(c, s))


def notice_of(cfg: dict) -> str:
    if cfg["precedent"]:
        return "precedent"
    if cfg["sham_history"]:
        return "sham"
    return "warning" if cfg["warning"] else "none"


def seeds_text(seeds: list[int]) -> str:
    if seeds == list(range(seeds[0], seeds[-1] + 1)) and len(seeds) > 2:
        return f"seeds {seeds[0]}–{seeds[-1]}"
    return "seeds " + ", ".join(map(str, seeds))


def collect(runs_dir: Path) -> dict:
    runs = find_runs(runs_dir, warn=lambda m: print(m, file=sys.stderr))
    if not runs:
        raise SystemExit(f"no D-G runs under {runs_dir}")
    cell_of: dict[str, set] = defaultdict(set)
    seeds: dict[str, set] = defaultdict(set)
    for r in runs:
        c = r.metadata["auction_config"]
        if c["warning"] is False and (c["precedent"] or c["sham_history"]):
            raise SystemExit(f"{r.run_id}: precedent or sham history without the warning")
        cell_of[r.arm].add((r.metadata["seat_mode"], c["buyer_plea_hour"] is not None, notice_of(c)))
        seeds[r.arm].add(r.seed)
    grid = {}
    for arm, cells in cell_of.items():
        if len(cells) != 1:
            raise SystemExit(f"arm {arm} spans several cells: {cells}")
        cell = next(iter(cells))
        if cell in grid:
            raise SystemExit(f"cell {cell} holds {grid[cell]} and {arm}")
        grid[cell] = arm
    not_run = [a for a in ARM_ORDER if a not in cell_of]
    if sorted(not_run) != sorted(PLANNED_NOT_RUN.values()):
        raise SystemExit(f"planned-but-not-run arms changed: {not_run}")
    cfg = [r.metadata["auction_config"] for r in runs]
    common = dict(
        n_llm={len(r.llm_sellers) for r in runs},
        llm_model={m for r in runs for m in r.metadata["resolved_models"]["sellers"] if m != "scripted"},
        buyers={len(r.metadata["buyer_ids"]) for r in runs},
        buyer_model={m for r in runs for m in r.metadata["resolved_models"]["buyers"]},
        rounds={c["rounds"] for c in cfg},
        report_tool={c["report_tool"] for c in cfg},
        prohibition={c["prohibition_notice"] for c in cfg},
        offer_hour={r.metadata["offer_hour"] for r in runs},
        offer_price={r.metadata["offer_price"] for r in runs},
        seller_comms={c["seller_comms_enabled"] and c["seller_dms_enabled"] for c in cfg},
    )
    for k, v in common.items():
        if len(v) != 1:
            raise SystemExit(f"{k} differs across runs: {v}")
    common = {k: next(iter(v)) for k, v in common.items()}
    return dict(grid=grid, seeds={a: sorted(s) for a, s in seeds.items()}, n_runs=len(runs), common=common,
                all_seeds=sorted({r.seed for r in runs}))


def money(x: float) -> str:
    return f"${x:.0f}" if float(x).is_integer() else f"${x:.2f}"


def box(ax, x, y, w, h, fc, ec="none", lw=0.8, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05", fc=fc, ec=ec, lw=lw,
                                ls=ls))


def check_text(fig) -> None:
    """Warn about text that leaves the figure or overlaps other text (the layout is hand-placed)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    fb = fig.bbox
    boxes = [(t, t.get_window_extent(r)) for a in fig.axes for t in a.texts if t.get_text()]
    for t, b in boxes:
        if b.x0 < fb.x0 - 0.5 or b.x1 > fb.x1 + 0.5 or b.y0 < fb.y0 - 0.5 or b.y1 > fb.y1 + 0.5:
            print(f"WARNING text outside figure: {t.get_text()[:60]!r}", file=sys.stderr)
    for i, (t1, b1) in enumerate(boxes):
        for t2, b2 in boxes[i + 1:]:
            inter = b1.intersection(b1, b2)
            if inter is not None and inter.width > 1 and inter.height > 1:
                print(f"WARNING text overlap: {t1.get_text()[:40]!r} / {t2.get_text()[:40]!r}", file=sys.stderr)


def draw(d: dict, out_dir: Path) -> list[Path]:
    plt.rcParams.update({"font.size": FS, "svg.fonttype": "path", "text.parse_math": False,
                         "svg.hashsalt": "fig_arms_grid"})  # byte-stable SVG ids
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    price = money(d["common"]["offer_price"])

    # columns: (notice, buyer plea); the no-notice column splits by buyer 5
    cols = [("none", False), ("none", True), ("warning", False), ("precedent", False), ("sham", False)]
    X0, GAP = 1.55, 0.04                      # row-header column, then the cells; a thin surface gap between cells
    cw = (W - 0.02 - X0) / len(cols)
    rh = 0.36
    y_head1, y_head2 = H - 0.2, H - 0.5       # centres of the two header rows
    y_rows = [y_head2 - 0.38 - i * rh for i in range(len(MODES))]  # centre of each row

    # header row 1: notice in the seller prompt (from hour 1)
    ax.text(L, y_head1, "Prompt notice \u2192", ha="left", va="center", fontsize=FS, color=MUTED)
    spans = [("none", 0, 2), ("warning", 2, 1), ("precedent", 3, 1), ("sham", 4, 1)]
    head = dict(NOTICES)
    for key, c0, n in spans:
        x = X0 + c0 * cw
        ax.text(x + n * cw / 2, y_head1, head[key], ha="center", va="center", fontsize=FS + 0.5, color=INK,
                weight="bold", linespacing=1.1)
        ax.plot([x + GAP, x + n * cw - GAP], [y_head1 - 0.19] * 2, color=GRID, lw=0.8)
    # header row 2: buyer 5
    ax.text(L, y_head2, "Buyer 5 \u2192", ha="left", va="center", fontsize=FS, color=MUTED)
    ax.text(X0 + cw / 2, y_head2, "silent", ha="center", va="center", fontsize=FS, color=INK)
    ax.text(X0 + 1.5 * cw, y_head2, "human plea", ha="center", va="center", fontsize=FS, color=INK)
    ax.text(X0 + 3.5 * cw, y_head2, "silent", ha="center", va="center", fontsize=FS, color=INK)

    # rows
    common_seeds = d["all_seeds"]
    for (mode, title, sub, accent), yc in zip(MODES, y_rows):
        ax.add_patch(Rectangle((L, yc - rh / 2 + GAP), 0.05, rh - 2 * GAP, fc=accent, ec="none"))
        ax.text(L + 0.12, yc + 0.07, title, ha="left", va="center", fontsize=FS + 0.5, color=INK, weight="bold")
        ax.text(L + 0.12, yc - 0.09, sub.format(price=price), ha="left", va="center", fontsize=FS, color=MUTED)
        for i, (notice, plea) in enumerate(cols):
            x, y = X0 + i * cw + GAP / 2, yc - rh / 2 + GAP / 2
            w, h = cw - GAP, rh - GAP
            arm = d["grid"].get((mode, plea, notice))
            planned = PLANNED_NOT_RUN.get((mode, plea, notice))
            if arm:
                box(ax, x, y, w, h, fc=wash(accent, 0.14))
                odd = d["seeds"][arm] != common_seeds  # name the seeds only where an arm differs
                ax.text(x + w / 2, y + h / 2 + (0.07 if odd else 0), arm, ha="center", va="center",
                        fontsize=FS + 1.5, color=INK, weight="bold")
                if odd:
                    ax.text(x + w / 2, y + h / 2 - 0.1, seeds_text(d["seeds"][arm]), ha="center", va="center",
                            fontsize=FS, color=MUTED)
            elif planned:
                box(ax, x, y, w, h, fc=SURFACE, ec=REFERENCE, lw=0.7, ls=(0, (3, 2)))
                ax.text(x + w / 2, y + h / 2, f"{planned}\nnot run", ha="center", va="center", fontsize=FS,
                        linespacing=1.1, color=MUTED)
            else:
                box(ax, x, y, w, h, fc=SURFACE, ec=GRID, lw=0.6)

    # the 2x2 of pleas: D, D-hb, D-hs, D-hsb
    yb0 = y_rows[2] - rh / 2 - 0.015
    box(ax, X0 - 0.015, yb0, 2 * cw + 0.03, 2 * rh + 0.03, fc="none", ec=MUTED, lw=1.0)
    ax.text(X0 + cw, yb0 - 0.05, "2 \u00d7 2: seller plea \u00d7 buyer plea", ha="center", va="top",
            fontsize=FS, color=MUTED)

    c = d["common"]
    n_arms = len(d["grid"])
    ax.text(X0 + 3.5 * cw, yb0 - 0.05, "blank cells: not part of the design", ha="center", va="top", fontsize=FS,
            color=MUTED)
    ax.text(L, yb0 - 0.3,
            f"Every arm: {c['n_llm']} {PRETTY.get(c['llm_model'], c['llm_model'])} sellers + scripted seat 5, "
            f"{c['buyers']} {PRETTY.get(c['buyer_model'], c['buyer_model'])} buyers, {c['rounds']} hours, "
            f"messaging on,\nreport_to_regulator, no prohibition notice; {seeds_text(common_seeds)} in every arm "
            f"({n_arms} arms \u00d7 {len(common_seeds)} seeds = {d['n_runs']} markets).",
            ha="left", va="top", fontsize=FS, color=MUTED, linespacing=1.25)
    if not (c["report_tool"] and c["seller_comms"] and not c["prohibition"]):
        raise SystemExit("the footer's common settings do not hold for every run")

    check_text(fig)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("svg", "png"):
        p = out_dir / f"fig_arms_grid.{ext}"
        fig.savefig(p, format=ext, dpi=200, facecolor=SURFACE,
                    metadata={"Date": None} if ext == "svg" else {"Software": None})  # byte-stable reruns
        paths.append(p)
    plt.close(fig)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", type=Path, default=REPO / "results" / "dg", help="the Gemini D-G runs")
    ap.add_argument("--out-dir", type=Path, default=REPO / "report" / "figures")
    args = ap.parse_args()
    d = collect(args.runs_dir)
    for p in draw(d, args.out_dir):
        print(p)
    for cell, arm in sorted(d["grid"].items(), key=lambda kv: arm_sort_key(kv[1])):
        print(f"{arm:7s} seat_mode={cell[0]:17s} buyer_plea={cell[1]!s:5s} notice={cell[2]:9s} seeds={d['seeds'][arm]}")
    print(f"{d['n_runs']} runs; common: {d['common']}")


if __name__ == "__main__":
    main()
