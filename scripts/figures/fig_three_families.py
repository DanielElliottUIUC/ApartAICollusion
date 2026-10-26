"""Figure: the plain undercover offer across three seller families, plus GPT-4.1 with warning + precedent (new
sprint code; matches report Table 4b).

Rows: Gemini 3.8 Flash D (5 markets, 20 seller-episodes), Claude Haiku 5.5 D (3 markets, 12), GPT-4.1 D (3, 12),
GPT-4.1 F (3, 12). Columns: seller-episodes that reported seat 5, were judge-coded as suspecting collusion, as
verbally agreeing to a peer's price proposal, and as verbally rejecting one (each a count out of n, drawn as a
meter: the light track is n), then private messages per market split into messages between LLM sellers and
messages to seat 5.

Sources (nothing is taken from the report text):
  - outcome counts: report/data/{dg,dg_haiku,dg_gpt41}/outcomes_by_arm.csv, rate x n_seller_episodes for
    report_is_scripted_seat, suspects_collusion, verbal_accept, verbal_reject. The reported-seat-5 count is
    cross-checked against the distinct reporters naming seat 5 in each run's collusion_metrics.json when the raw
    runs are available.
  - Gemini private messages: report/data/dg/table3_extra.csv (private_msgs_peer, private_msgs_to_seat5).
  - GPT-4.1 and Haiku private messages: counted from each run's unified.log ("Auction round N completed with
    result: {...}" lines, field seller_dms; messages sent by the scripted seat are excluded). The runs are the
    ones listed in report/data/{dg_gpt41,dg_haiku}/market_by_run.csv. The raw logs are local (results/ is
    gitignored); without them the script falls back to the committed fig_three_families.data.csv.

Writes report/figures/fig_three_families.{svg,png} and fig_three_families.data.csv (the plotted numbers).

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_three_families.py --results <path to results/>
"""

import argparse
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "report" / "data"
OUT = REPO / "report" / "figures"
NAME = "fig_three_families"

# Reference palette from the dataviz skill (light mode), shared with scripts/make_dg_figures.py.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"     # categorical slot 1 (blue): counts; private messages between LLM sellers
SERIES_2 = "#eb6834"   # categorical slot 2 (orange): private messages to seat 5
TRACK = "#cde2fb"      # blue ramp step 100: the meter track (n seller-episodes)

# (label, sub-label, analysis folder, arm)
CONDITIONS = [
    ("Gemini 3.8 Flash, D", "plain offer · 5 markets", "dg", "D"),
    ("Claude Haiku 5.5, D", "plain offer · 3 markets", "dg_haiku", "D"),
    ("GPT-4.1, D", "plain offer · 3 markets", "dg_gpt41", "D"),
    ("GPT-4.1, F", "offer + warning + precedent · 3 markets", "dg_gpt41", "F"),
]
OUTCOMES = [  # (column stem in outcomes_by_arm.csv, panel title)
    ("report_is_scripted_seat", "Reported seat 5"),
    ("suspects_collusion", "Suspects collusion"),
    ("verbal_accept", "Verbal agreement"),
    ("verbal_reject", "Verbal rejection"),
]
ROUND_RE = re.compile(r"Auction round (\d+) completed with result: (\{.*\})\s*$")


def count_messages(run_dir: Path) -> tuple[int, int]:
    """(private messages between LLM sellers, private messages from LLM sellers to the scripted seat)."""
    meta = json.load(open(next(run_dir.rglob("experiment_metadata.json")), encoding="utf-8"))
    s5 = meta["scripted_seats"][0]
    peer = to5 = 0
    for line in open(run_dir / "unified.log", encoding="utf-8"):
        m = ROUND_RE.search(line)
        if not m:
            continue
        for dm in json.loads(m.group(2)).get("seller_dms") or []:
            if dm["sender"] == s5:
                continue
            if dm["recipient"] == s5:
                to5 += 1
            else:
                peer += 1
    return peer, to5


def reporters_of_seat5(run_dir: Path) -> int:
    meta = json.load(open(next(run_dir.rglob("experiment_metadata.json")), encoding="utf-8"))
    metrics = json.load(open(next(run_dir.rglob("collusion_metrics.json")), encoding="utf-8"))
    s5 = meta["scripted_seats"][0]
    return len({r["from"] for r in metrics.get("regulator_reports") or [] if r["about"] == s5})


def build_table(results: Path | None) -> pd.DataFrame:
    fallback = OUT / f"{NAME}.data.csv"
    rows = []
    for label, sub, folder, arm in CONDITIONS:
        by_arm = pd.read_csv(DATA / folder / "outcomes_by_arm.csv").set_index("arm").loc[arm]
        n = int(by_arm["n_seller_episodes"])
        row = dict(condition=label, family_folder=folder, arm=arm, n_seller_episodes=n, n_markets=int(by_arm["n_runs"]))
        for col, _ in OUTCOMES:
            row[col] = int(round(by_arm[f"{col}_rate"] * n))
        runs = pd.read_csv(DATA / folder / "market_by_run.csv")
        run_ids = list(runs.loc[runs["arm"] == arm, "run_id"])
        if folder == "dg":  # Gemini: the committed per-run message counts
            t3 = pd.read_csv(DATA / "dg" / "table3_extra.csv").set_index("run_id").loc[run_ids]
            row["private_between_sellers"] = t3["private_msgs_peer"].mean()
            row["private_to_seat5"] = t3["private_msgs_to_seat5"].mean()
            row["message_source"] = "report/data/dg/table3_extra.csv"
            log_reporters = int(t3["reported_seat5"].sum())
        elif results is not None and (results / folder).is_dir():
            counts = [count_messages(results / folder / r) for r in run_ids]
            row["private_between_sellers"] = sum(c[0] for c in counts) / len(counts)
            row["private_to_seat5"] = sum(c[1] for c in counts) / len(counts)
            row["message_source"] = f"results/{folder}/<run>/unified.log"
            log_reporters = sum(reporters_of_seat5(results / folder / r) for r in run_ids)
        else:
            old = pd.read_csv(fallback).set_index("condition").loc[label]
            row["private_between_sellers"] = old["private_between_sellers"]
            row["private_to_seat5"] = old["private_to_seat5"]
            row["message_source"] = old["message_source"]
            log_reporters = None
        if log_reporters is not None and log_reporters != row["report_is_scripted_seat"]:
            raise SystemExit(f"{label}: outcomes_by_arm gives {row['report_is_scripted_seat']} reporters of seat 5, "
                             f"the run logs {log_reporters}")
        row["private_total"] = row["private_between_sellers"] + row["private_to_seat5"]
        rows.append(row)
    return pd.DataFrame(rows)


# ---- marks ---------------------------------------------------------------------------------------------------

def _per_point(ax) -> tuple[float, float]:
    """Data units per typographic point along x and y (axis limits and position must be final)."""
    inv = ax.transData.inverted()
    px = ax.figure.dpi / 72.0
    (x0, y0), (x1, y1) = inv.transform([(0, 0), (px, px)])
    return abs(x1 - x0), abs(y1 - y0)


def hbar(ax, y, left, width, height, color, round_end=True, r_pt=2.2, zorder=2):
    """Horizontal bar, square at its left (baseline) end, rounded at its data end."""
    if width <= 0:
        return
    ux, uy = _per_point(ax)
    r, ry = r_pt * ux, min(r_pt * uy, height / 2)
    if round_end and width > 2 * r:
        ax.add_patch(FancyBboxPatch((left, y - height / 2), width, height, boxstyle=f"round,pad=0,rounding_size={r}",
                                    mutation_aspect=ry / r, fc=color, ec="none", zorder=zorder))
        ax.add_patch(Rectangle((left, y - height / 2), width - r, height, fc=color, ec="none", zorder=zorder))
    else:
        ax.add_patch(Rectangle((left, y - height / 2), width, height, fc=color, ec="none", zorder=zorder))


def fmt_msgs(v: float) -> str:
    return f"{v:.0f}" if v >= 10 else f"{v:.1f}"


def draw(df: pd.DataFrame, out_dir: Path) -> list[Path]:
    plt.rcParams.update({"font.size": 8, "svg.fonttype": "path", "svg.hashsalt": NAME})  # stable SVG ids
    fig = plt.figure(figsize=(6.5, 2.75), facecolor=SURFACE)
    gs = fig.add_gridspec(1, 5, width_ratios=[1, 1, 1, 1, 1.45], left=0.225, right=0.985, top=0.745, bottom=0.19,
                          wspace=0.12)
    axes = [fig.add_subplot(gs[0, i]) for i in range(5)]
    # rows: the plain offer in three families (arm D), then GPT-4.1 with warning + precedent (arm F)
    ys = [3.55, 2.65, 1.75, 0.0]
    header_y = {4.25: "Plain offer (arm D)", 0.7: "Offer + warning + precedent (arm F)"}
    bar_h = 0.40
    ylim = (-0.45, 4.45)

    for ax in axes:
        ax.set_facecolor(SURFACE)
        ax.set_ylim(*ylim)
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.set_yticks([])
        ax.tick_params(colors=MUTED, labelsize=8, length=0)

    # outcome meters: count / n, the light track is n
    titles = {"report_is_scripted_seat": "Reported\nseat 5", "suspects_collusion": "Suspects\ncollusion",
              "verbal_accept": "Verbal\nagreement", "verbal_reject": "Verbal\nrejection"}
    for ax, (col, _) in zip(axes[:4], OUTCOMES):
        ax.set_xlim(0, 1.75)
        ax.set_xticks([])
        ax.set_title(titles[col], fontsize=8.5, color=INK, loc="left", pad=4)
        for y, (_, r) in zip(ys, df.iterrows()):
            n, k = r["n_seller_episodes"], r[col]
            hbar(ax, y, 0, 1.0, bar_h, TRACK, zorder=1)
            hbar(ax, y, 0, k / n, bar_h, SERIES, zorder=2)
            ax.text(1.07, y, f"{k}/{n}", fontsize=8, color=INK, va="center", ha="left")

    # private messages per market, stacked: between LLM sellers, then to seat 5
    ax = axes[4]
    ax.set_xlim(0, 150)
    ax.set_title("Private messages\nper market", fontsize=8.5, color=INK, loc="left", pad=4)
    ax.spines["bottom"].set_visible(True)
    ax.spines["bottom"].set_color(GRID)
    ax.set_xticks([0, 50, 100])
    ax.tick_params(axis="x", labelsize=8, colors=MUTED, pad=2)
    for xv in (50, 100):
        ax.axvline(xv, color=GRID, linewidth=0.6, zorder=0)
    ux, _ = _per_point(ax)
    gap = 1.2 * ux
    for y, (_, r) in zip(ys, df.iterrows()):
        a, b = r["private_between_sellers"], r["private_to_seat5"]
        if b > 0 and a > 0:
            hbar(ax, y, 0, max(a - gap / 2, 0), bar_h, SERIES, round_end=False)
            hbar(ax, y, a + gap / 2, max(b - gap / 2, 0), bar_h, SERIES_2)
        elif a > 0:
            hbar(ax, y, 0, a, bar_h, SERIES)
        else:
            hbar(ax, y, 0, b, bar_h, SERIES_2)
        ax.text(r["private_total"] + 3, y, fmt_msgs(r["private_total"]), fontsize=8, color=INK, va="center",
                ha="left")
    handles = [Rectangle((0, 0), 1, 1, fc=SERIES, ec="none"), Rectangle((0, 0), 1, 1, fc=SERIES_2, ec="none")]
    ax.legend(handles, ["between LLM sellers", "to seat 5"], loc="upper right", bbox_to_anchor=(1.0, -0.17),
              ncol=2, frameon=False, fontsize=8, handlelength=0.9, handleheight=0.9, columnspacing=1.0,
              handletextpad=0.4, labelcolor=INK, borderaxespad=0)

    # source headers over the panels
    def span(a, b, frac_b=1.0):
        pa, pb = axes[a].get_position(), axes[b].get_position()
        return pa.x0, pb.x0 + pb.width * frac_b
    yh = axes[0].get_position().y1 + 0.13
    for (a, b, frac), text in [((0, 0, 1 / 1.75), "Run logs"),
                               ((1, 3, 1 / 1.75), "Judge-coded (Claude Haiku 5.5)"),
                               ((4, 4, 108 / 150), "Run logs")]:
        x0, x1 = span(a, b, frac)
        fig.add_artist(plt.Line2D([x0, x1], [yh - 0.018] * 2, color=GRID, linewidth=0.8, transform=fig.transFigure))
        fig.text(x0, yh, text, fontsize=8, color=MUTED, ha="left", va="bottom")

    # group headers and row labels (condition in ink, size in muted ink)
    to_fig = lambda y: (axes[0].transData.transform((0, y))[1]) / fig.bbox.height  # noqa: E731
    for yv, text in header_y.items():
        fig.text(0.012, to_fig(yv), text, fontsize=8, color=MUTED, ha="left", va="center", style="italic")
    fig.add_artist(plt.Line2D([0.012, 0.985], [to_fig(0.98)] * 2, color=GRID, linewidth=0.6,
                              transform=fig.transFigure))
    for y, (label, _, _, _), (_, r) in zip(ys, CONDITIONS, df.iterrows()):
        name = label.split(",")[0]
        fig.text(0.024, to_fig(y + 0.13), name, fontsize=8.5, color=INK, ha="left", va="center")
        fig.text(0.024, to_fig(y - 0.22), f"{r['n_seller_episodes']} sellers, {r['n_markets']} markets", fontsize=8,
                 color=MUTED, ha="left", va="center")

    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("svg", "png"):
        p = out_dir / f"{NAME}.{ext}"
        fig.savefig(p, format=ext, dpi=200, facecolor=SURFACE,
                    metadata={"Date": None} if ext == "svg" else {"Software": None})  # byte-stable reruns
        paths.append(p)
    plt.close(fig)
    return paths


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", type=Path, default=REPO / "results",
                   help="local results/ folder with dg_gpt41/ and dg_haiku/ run folders (gitignored)")
    p.add_argument("--out-dir", type=Path, default=OUT)
    args = p.parse_args(argv)
    results = args.results if args.results.is_dir() else None
    df = build_table(results).round(3)  # the committed data CSV holds the same rounded values
    df.round(3).to_csv(args.out_dir / f"{NAME}.data.csv", index=False)
    for path in draw(df, args.out_dir):
        print("wrote", path)
    print(df.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
