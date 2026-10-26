"""Figure: which message channels Gemini sellers used in each D-G arm (new sprint code).

(a) Private and public messages per market for all ten Gemini arms (mean of 5 markets), private split into
    messages between LLM sellers and messages to seat 5, with Base's value as a reference line.
(b) Private messages per hour (mean of 5 markets) for Base, D, E and G-warn, so it is visible that in the warning
    arms messaging between sellers never started (the warning is in the prompt from hour 1), rather than stopping
    after the offer. Base's hourly total is drawn as a reference in the other panels; the dashed line is the cap of
    2 private messages per seller per hour (8 per market-hour for 4 LLM sellers).

Sources (nothing is taken from the report text):
  - (a) report/data/dg/table3_extra.csv: private_msgs_peer, private_msgs_to_seat5, public_msgs (public_msgs counts
    seller-hours with a public message), averaged over the 5 runs of each arm.
  - (b) each run's unified.log under results/dg/ ("Auction round N completed with result: {...}" lines; seller_dms
    entries by round_number, excluding messages the scripted seat sent; seller_messages for public). The per-run
    sums are checked against table3_extra.csv. The raw logs are local (results/ is gitignored); without them the
    script falls back to the committed fig_channels_by_arm.data.csv.

Writes report/figures/fig_channels_by_arm.{svg,png} and fig_channels_by_arm.data.csv (per arm and hour, all ten
arms).

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_channels_by_arm.py --results <path to results/>
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
NAME = "fig_channels_by_arm"

# Reference palette from the dataviz skill (light mode), shared with scripts/make_dg_figures.py.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
REFERENCE = "#8c8b86"  # Base, the cap
C_PEER = "#2a78d6"     # categorical slot 1 (blue): private, between LLM sellers
C_SEAT5 = "#eb6834"    # slot 2 (orange): private, to seat 5
C_PUBLIC = "#1baf7a"   # slot 3 (aqua): public (sub-3:1 on the surface, so every bar carries a value label)

ARMS = ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "G-warn", "G-prec", "F-sham"]  # src/apartcollusion/runs.py
WARNING_ARMS = ["E", "F", "G-warn", "G-prec", "F-sham"]
DESCRIPTION = {
    "Base": "placebo note", "D": "offer", "D-hs": "offer as a human-seller plea", "D-hb": "offer + human-buyer plea",
    "D-hsb": "both pleas", "E": "offer + warning", "F": "offer + warning + precedent", "G-warn": "warning only",
    "G-prec": "warning + precedent", "F-sham": "offer + warning + sham history",
}
HOURLY_ARMS = ["Base", "D", "E", "G-warn"]
CAP_PER_HOUR = 8  # 2 private messages per seller per hour x 4 LLM sellers
OFFER_HOUR = 3
ROUND_RE = re.compile(r"Auction round (\d+) completed with result: (\{.*\})\s*$")


def hourly_counts(results: Path, t3: pd.DataFrame) -> pd.DataFrame:
    """Per run and hour: private messages between LLM sellers, to seat 5, and public messages (LLM sellers only)."""
    rows = []
    for run_id, r in t3.iterrows():
        d = results / run_id
        s5 = r["scripted_seat"]
        for line in open(d / "unified.log", encoding="utf-8"):
            m = ROUND_RE.search(line)
            if not m:
                continue
            hour, res = int(m.group(1)), json.loads(m.group(2))
            peer = to5 = 0
            for dm in res.get("seller_dms") or []:
                if dm["sender"] == s5:
                    continue
                assert int(dm["round_number"]) == hour, (run_id, hour)
                if dm["recipient"] == s5:
                    to5 += 1
                else:
                    peer += 1
            pub = sum(1 for k, v in (res.get("seller_messages") or {}).items() if v and k != s5)
            rows.append(dict(run_id=run_id, arm=r["arm"], seed=r["seed"], hour=hour, private_between_sellers=peer,
                             private_to_seat5=to5, public=pub))
    per_run = pd.DataFrame(rows)
    sums = per_run.groupby("run_id")[["private_between_sellers", "private_to_seat5", "public"]].sum()
    check = sums.join(t3[["private_msgs_peer", "private_msgs_to_seat5", "public_msgs"]])
    bad = check[(check["private_between_sellers"] != check["private_msgs_peer"])
                | (check["private_to_seat5"] != check["private_msgs_to_seat5"])
                | (check["public"] != check["public_msgs"])]
    if len(bad):
        raise SystemExit(f"unified.log counts disagree with table3_extra.csv:\n{bad}")
    by_hour = (per_run.groupby(["arm", "hour"])[["private_between_sellers", "private_to_seat5", "public"]]
               .agg(["mean", "max"]))
    by_hour.columns = [f"{a}_{b}" for a, b in by_hour.columns]
    by_hour = by_hour.reset_index()
    by_hour["n_runs"] = by_hour["arm"].map(per_run.groupby("arm")["run_id"].nunique())
    return by_hour


# ---- marks ---------------------------------------------------------------------------------------------------

def _per_point(ax) -> tuple[float, float]:
    inv = ax.transData.inverted()
    px = ax.figure.dpi / 72.0
    (x0, y0), (x1, y1) = inv.transform([(0, 0), (px, px)])
    return abs(x1 - x0), abs(y1 - y0)


def hbar(ax, y, left, width, height, color, round_end=True, r_pt=2.2):
    """Horizontal bar, square at the baseline, rounded at the data end."""
    if width <= 0:
        return
    ux, uy = _per_point(ax)
    r, ry = r_pt * ux, min(r_pt * uy, height / 2)
    if round_end and width > 2 * r:
        ax.add_patch(FancyBboxPatch((left, y - height / 2), width, height, boxstyle=f"round,pad=0,rounding_size={r}",
                                    mutation_aspect=ry / r, fc=color, ec="none", zorder=2))
        ax.add_patch(Rectangle((left, y - height / 2), width - r, height, fc=color, ec="none", zorder=2))
    else:
        ax.add_patch(Rectangle((left, y - height / 2), width, height, fc=color, ec="none", zorder=2))


def vbar(ax, x, bottom, height, width, color, round_end=True, r_pt=1.6):
    """Column, square at the baseline, rounded at the top."""
    if height <= 0:
        return
    ux, uy = _per_point(ax)
    ry, rx = r_pt * uy, min(r_pt * ux, width / 2)
    if round_end and height > 2 * ry:
        ax.add_patch(FancyBboxPatch((x - width / 2, bottom), width, height, boxstyle=f"round,pad=0,rounding_size={rx}",
                                    mutation_aspect=ry / rx, fc=color, ec="none", zorder=2))
        ax.add_patch(Rectangle((x - width / 2, bottom), width, height - ry, fc=color, ec="none", zorder=2))
    else:
        ax.add_patch(Rectangle((x - width / 2, bottom), width, height, fc=color, ec="none", zorder=2))


LABEL_BOX = dict(boxstyle="square,pad=0.1", fc=SURFACE, ec="none")


def header(fig, y: float, bold: str, note: str) -> None:
    """Panel header: bold label, then a muted note set just after it."""
    t = fig.text(0.012, y, bold, fontsize=9, color=INK, ha="left", va="top", weight="bold")
    x1 = t.get_window_extent(renderer=fig.canvas.get_renderer()).x1 / fig.bbox.width
    fig.text(x1 + 0.012, y - 0.002, note, fontsize=8, color=MUTED, ha="left", va="top")


def fmt(v: float) -> str:
    if v == 0:
        return "0"
    return f"{v:.0f}" if v >= 10 else f"{v:.1f}"


def draw(per_arm: pd.DataFrame, by_hour: pd.DataFrame, out_dir: Path) -> list[Path]:
    plt.rcParams.update({"font.size": 8, "svg.fonttype": "path", "svg.hashsalt": NAME})  # stable SVG ids
    fig = plt.figure(figsize=(6.5, 5.8), facecolor=SURFACE)
    left = 0.39
    gs_a = fig.add_gridspec(1, 2, left=left, right=0.985, top=0.882, bottom=0.455, wspace=0.10)
    gs_b = fig.add_gridspec(1, 4, left=0.085, right=0.985, top=0.295, bottom=0.072, wspace=0.10)
    ax_priv, ax_pub = fig.add_subplot(gs_a[0, 0]), fig.add_subplot(gs_a[0, 1])
    axes_b = [fig.add_subplot(gs_b[0, i]) for i in range(4)]

    # ---- (a) per market, all ten arms ----
    n = len(ARMS)
    ys = [n - 1 - i - (0.9 if a in WARNING_ARMS else 0) for i, a in enumerate(ARMS)]  # gap before the warning arms
    ylim = (min(ys) - 0.6, max(ys) + 1.0)
    xmax = 135
    base = per_arm.loc["Base"]
    for ax, title in ((ax_priv, "Private messages per market"), (ax_pub, "Public messages per market")):
        ax.set_facecolor(SURFACE)
        ax.set_xlim(0, xmax)
        ax.set_ylim(*ylim)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.set_yticks([])
        ax.set_xticks([0, 50, 100])
        ax.tick_params(axis="x", labelsize=8, colors=MUTED, length=0, pad=2)
        for xv in (50, 100):
            ax.axvline(xv, color=GRID, linewidth=0.6, zorder=0)
        ax.set_title(title, fontsize=8.5, color=INK, loc="left", pad=4)
    bar_h = 0.56
    ux, _ = _per_point(ax_priv)
    gap = 1.2 * ux
    for y, arm in zip(ys, ARMS):
        r = per_arm.loc[arm]
        a, b = r["private_between_sellers"], r["private_to_seat5"]
        if a > 0 and b > 0:
            hbar(ax_priv, y, 0, a - gap / 2, bar_h, C_PEER, round_end=False)
            hbar(ax_priv, y, a + gap / 2, b - gap / 2, bar_h, C_SEAT5)
        elif b > 0:
            hbar(ax_priv, y, 0, b, bar_h, C_SEAT5)
        else:
            hbar(ax_priv, y, 0, a, bar_h, C_PEER)
        label = fmt(a + b)
        if a == 0 and b > 0:
            label += ", all to seat 5"
        ax_priv.text(a + b + 2.5, y, label, fontsize=8, color=INK, va="center", ha="left", zorder=4,
                     bbox=LABEL_BOX)
        hbar(ax_pub, y, 0, r["public"], bar_h, C_PUBLIC)
        ax_pub.text(r["public"] + 2.5, y, fmt(r["public"]), fontsize=8, color=INK, va="center", ha="left",
                    zorder=4, bbox=LABEL_BOX)
    for ax, v in ((ax_priv, base["private_between_sellers"] + base["private_to_seat5"]), (ax_pub, base["public"])):
        ax.plot([v, v], [ylim[0], ys[0] + 0.45], color=REFERENCE, linewidth=1.2, zorder=1)
        ax.text(v, ys[0] + 0.55, "Base", fontsize=8, color=MUTED, ha="center", va="bottom")

    # row labels: arm in ink, design in muted ink; group headers
    to_fig = lambda y: ax_priv.transData.transform((0, y))[1] / fig.bbox.height  # noqa: E731
    for y, arm in zip(ys, ARMS):
        fig.text(0.024, to_fig(y), arm, fontsize=8.5, color=INK, ha="left", va="center")
        fig.text(0.10, to_fig(y), DESCRIPTION[arm], fontsize=8, color=MUTED, ha="left", va="center")
    y_split = (ys[ARMS.index("D-hsb")] + ys[ARMS.index("E")]) / 2
    fig.add_artist(plt.Line2D([0.012, 0.985], [to_fig(y_split)] * 2, color=GRID, linewidth=0.6,
                              transform=fig.transFigure))
    fig.text(0.012, to_fig(y_split - 0.12), "Warning in the seller prompt from hour 1", fontsize=8, color=MUTED,
             ha="left", va="center", style="italic")
    fig.text(0.012, to_fig(ys[0] + 0.62), "No warning", fontsize=8, color=MUTED, ha="left", va="center",
             style="italic")
    header(fig, 0.978, "a   Messages per market, by arm", "mean of 5 markets, Gemini 3.8 Flash sellers")

    # ---- (b) private messages per hour, four arms ----
    hours = sorted(by_hour["hour"].unique())
    bh = by_hour.set_index(["arm", "hour"])
    base_total = [bh.loc[("Base", h), "private_between_sellers_mean"] + bh.loc[("Base", h), "private_to_seat5_mean"]
                  for h in hours]
    for i, (ax, arm) in enumerate(zip(axes_b, HOURLY_ARMS)):
        ax.set_facecolor(SURFACE)
        ax.set_xlim(0.4, max(hours) + 0.6)
        ax.set_ylim(0, 9.2)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
        ax.tick_params(colors=MUTED, labelsize=8, length=0, pad=2)
        ax.set_xticks([1, 3, 5, 10, 15])
        ax.set_yticks([0, 4, 8])
        if i:
            ax.set_yticklabels([])
        ax.grid(True, axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_title(f"{arm}  ({DESCRIPTION[arm]})", fontsize=8.5, color=INK, loc="left", pad=4)
        ax.axhline(CAP_PER_HOUR, color=REFERENCE, linewidth=0.8, linestyle=(0, (3, 2)), zorder=1)
        ax.axvline(OFFER_HOUR, color=MUTED, linewidth=0.8, zorder=1)
        ux, uy = _per_point(ax)
        gap_y = 1.2 * uy
        width = 1 - 1.4 * ux
        for h in hours:
            a = bh.loc[(arm, h), "private_between_sellers_mean"]
            b = bh.loc[(arm, h), "private_to_seat5_mean"]
            if a > 0 and b > 0:
                vbar(ax, h, 0, a - gap_y / 2, width, C_PEER, round_end=False)
                vbar(ax, h, a + gap_y / 2, b - gap_y / 2, width, C_SEAT5)
            elif b > 0:
                vbar(ax, h, 0, b, width, C_SEAT5)
            else:
                vbar(ax, h, 0, a, width, C_PEER)
        if arm != "Base":
            ax.stairs(base_total, [h - 0.5 for h in hours] + [hours[-1] + 0.5], color=REFERENCE, linewidth=1.2,
                      zorder=3, baseline=None)
        if arm in WARNING_ARMS:
            peer_max = by_hour.loc[by_hour["arm"] == arm, "private_between_sellers_max"].max()
            note = "none between\nsellers, in any\nhour or market" if peer_max == 0 else ""
            ax.text(14.0, 5.0, note, fontsize=8, color=INK, ha="right", va="center")
            b4 = bh.loc[(arm, OFFER_HOUR + 1), "private_to_seat5_mean"]
            ax.annotate(f"{fmt(b4)} to seat 5,\nhour 4", xy=(OFFER_HOUR + 1.45, min(b4, 1.6)), xytext=(6.0, 1.7),
                        fontsize=8, color=INK, ha="left", va="center",
                        arrowprops=dict(arrowstyle="-", color=MUTED, linewidth=0.7, shrinkA=1, shrinkB=1))
        ax.set_xlabel("Hour", fontsize=8, color=MUTED, labelpad=2)
    axes_b[0].set_ylabel("Private messages\nper hour", fontsize=8, color=MUTED, labelpad=3)
    axes_b[0].text(15.4, CAP_PER_HOUR + 0.2, "cap", fontsize=8, color=MUTED, ha="right", va="bottom")
    header(fig, 0.385, "b   Private messages per hour",
           "mean of 5 markets; grey line: Base; vertical line: seat 5's hour-3 message")

    # shared legend, top right
    handles = [Rectangle((0, 0), 1, 1, fc=C_PEER, ec="none"), Rectangle((0, 0), 1, 1, fc=C_SEAT5, ec="none"),
               Rectangle((0, 0), 1, 1, fc=C_PUBLIC, ec="none"),
               plt.Line2D([], [], color=REFERENCE, linewidth=1.2)]
    fig.legend(handles, ["private, between LLM sellers", "private, to seat 5", "public", "Base"],
               loc="upper left", bbox_to_anchor=(0.012, 0.952), ncol=4, frameon=False, fontsize=8,
               handlelength=1.1, handleheight=0.9, columnspacing=1.2, handletextpad=0.4, labelcolor=INK,
               borderaxespad=0)

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
                   help="local results/ folder with the dg/ run folders (gitignored)")
    p.add_argument("--out-dir", type=Path, default=OUT)
    args = p.parse_args(argv)
    t3 = pd.read_csv(DATA / "dg" / "table3_extra.csv").set_index("run_id")
    per_arm = t3.groupby("arm").agg(private_between_sellers=("private_msgs_peer", "mean"),
                                    private_to_seat5=("private_msgs_to_seat5", "mean"),
                                    public=("public_msgs", "mean"), n_runs=("seed", "size")).loc[ARMS]
    data_csv = args.out_dir / f"{NAME}.data.csv"
    if (args.results / "dg").is_dir():
        by_hour = hourly_counts(args.results / "dg", t3)
        by_hour.round(3).to_csv(data_csv, index=False)
    else:
        committed = OUT / f"{NAME}.data.csv"
        print(f"no raw runs under {args.results / 'dg'}; using {committed}")
        by_hour = pd.read_csv(committed)
    for path in draw(per_arm, by_hour, args.out_dir):
        print("wrote", path)
    print(per_arm.round(2).to_string())


if __name__ == "__main__":
    main()
