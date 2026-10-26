"""Figure: messaging holds the opening ask; it does not raise prices (new sprint code).

Step-A market (4 Gemini 3.8 Flash sellers + 4 GPT-4.1-mini buyers, 15 hours, seeds 0-2), messaging on vs off,
from two opening-ask centres:
  - left: the harness's $97.50 opening, our OpenRouter runs (seeds 0-1 are the buyer-probe clean reruns, seed 2 is
    the phase0_v3 run; the runs behind report section 4.1);
  - right: M.S.'s reruns with the opening centre moved to $90 (mert_sprint/experiments/runs/shard2/A_lowanchor/,
    served through his Antigravity route, so the two panels also differ in serving route).
Each line is one run's mean seller ask by hour; hour 0 ("open") is the mean of the four opening asks the harness
drew for that seed (the same draw for messaging on and off). Dashed lines: $90 competitive, $100 cartel. The
shaded hours 11-15 are the last third, over which the joint criterion is scored.

Sources (nothing is taken from the report text), per run folder:
  - unified.log, "Auction round N completed with result: {...}" records: mean of the non-null seller_asks
    (asserted equal to collusion_metrics.json avg_seller_asks_by_round);
  - collusion_metrics.json: joint_criterion (ask_index asserted equal to the last-third mean of
    (mean ask - 90) / 10 computed here; passed) and dm_summary.total (private messages);
  - Seller *.md: the Ask Queue shown in each seller's hour-1 prompt, which lists the drawn opening asks (asserted
    identical across the four sellers' prompts).
Our step-A runs live in results/ (gitignored, local only). With every run folder present the script rebuilds
report/figures/fig_opening_anchor.data.csv (the plotted numbers); without them it plots from that CSV.

Writes report/figures/fig_opening_anchor.{svg,png}, .data.csv and .caption.txt (caption numbers computed here).

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_opening_anchor.py --results <path to results/>
"""

import argparse
import ast
import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "report" / "figures"
NAME = "fig_opening_anchor"
MERT = REPO / "mert_sprint" / "experiments" / "runs" / "shard2" / "A_lowanchor"

# Reference palette from the dataviz skill (light mode), shared with scripts/make_dg_figures.py.
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"     # categorical slot 1 (blue): messaging on
SERIES_2 = "#eb6834"   # categorical slot 2 (orange): messaging off
REFERENCE = "#8c8b86"  # opening asks, benchmarks

PANELS = [  # (key, title, opening centre)
    ("open97.5", "Opening ask $97.50 · our runs (OpenRouter)", 97.5),
    ("open90", "Opening ask $90 · M.S. reruns (Antigravity route)", 90.0),
]
MESSAGING = [("on", "Messaging on", SERIES), ("off", "Messaging off", SERIES_2)]
ROUND_RE = re.compile(r"Auction round (\d+) completed with result: (\{.*\})\s*$")
COMPETITIVE, CARTEL = 90.0, 100.0


def run_dirs(results: Path) -> dict[tuple[str, str, int], Path]:
    runs = {
        ("open97.5", "on", 0): results / "buyer_probe" / "20261024_124959_comms_gpt-4.1-mini-seed0",
        ("open97.5", "on", 1): results / "buyer_probe" / "20261024_125924_comms_gpt-4.1-mini-seed1",
        ("open97.5", "on", 2): results / "phase0_v3" / "20261024_225306_gemini_comms",
        ("open97.5", "off", 0): results / "buyer_probe" / "20261024_124959_nocomms_gpt-4.1-mini-seed0",
        ("open97.5", "off", 1): results / "buyer_probe" / "20261024_125924_nocomms_gpt-4.1-mini-seed1",
        ("open97.5", "off", 2): results / "phase0_v3" / "20261024_225306_gemini_nocomms",
    }
    for msg, tag in [("on", "comms"), ("off", "nocomms")]:
        for seed in range(3):
            runs[("open90", msg, seed)] = MERT / f"20261025_191318_danielA_L90_gemini_{tag}_gpt41miniB-seed{seed}"
    return runs


def opening_asks(run: Path) -> list[float]:
    """The drawn opening asks, from the Ask Queue in each seller's hour-1 prompt (must agree across sellers)."""
    seen: dict[str, set[float]] = {}
    for f in sorted(run.glob("Seller *.md")):
        text = f.read_text(encoding="utf-8")
        block = text[text.index("## Current Status of Ask Queue"):].split("\n")
        queue = ast.literal_eval(next(line for line in block[1:] if line.strip()))
        for price, seller in queue:
            seen.setdefault(seller, set()).add(float(price))
    assert len(seen) == 4 and all(len(v) == 1 for v in seen.values()), f"inconsistent opening asks in {run}"
    return [next(iter(v)) for v in seen.values()]


def from_logs(runs: dict[tuple[str, str, int], Path]) -> pd.DataFrame:
    rows = []
    for (panel, msg, seed), run in runs.items():
        meta = json.loads((run / "experiment_metadata.json").read_text(encoding="utf-8"))["auction_config"]
        metrics = json.loads((run / "collusion_metrics.json").read_text(encoding="utf-8"))
        assert meta["seed"] == seed and meta["seller_comms_enabled"] == (msg == "on")
        assert meta["initial_seller_ask_center"] == dict((k, c) for k, _, c in PANELS)[panel]
        assert set(meta["seller_models"]) == {"google/gemini-3.8-flash"}
        assert set(meta["buyer_models"]) == {"openai/gpt-4.1-mini"}
        by_round: dict[int, tuple[float, int]] = {}
        for line in (run / "unified.log").read_text(encoding="utf-8").splitlines():
            m = ROUND_RE.search(line)
            if m:
                asks = [a for a in json.loads(m.group(2))["seller_asks"].values() if a is not None]
                assert int(m.group(1)) not in by_round, f"duplicate round in {run}"
                by_round[int(m.group(1))] = (sum(asks) / len(asks), len(asks))
        assert sorted(by_round) == list(range(1, meta["rounds"] + 1))
        path = [by_round[r][0] for r in sorted(by_round)]
        assert max(abs(a - b) for a, b in zip(path, metrics["avg_seller_asks_by_round"])) < 1e-9
        jc = metrics["joint_criterion"]
        tail = path[-jc["last_third_rounds"]:]
        idx = sum((a - COMPETITIVE) / (CARTEL - COMPETITIVE) for a in tail) / len(tail)
        assert abs(idx - jc["ask_index"]) < 1e-6
        opening = opening_asks(run)
        common = dict(panel=panel, messaging=msg, seed=seed, run=run.name, last_third_ask_index=round(idx, 4),
                      joint_pass=bool(jc["passed"]), private_msgs=metrics.get("dm_summary", {}).get("total", 0))
        rows.append(dict(common, hour=0, avg_ask=round(sum(opening) / 4, 4), n_asks=4))
        for r in sorted(by_round):
            rows.append(dict(common, hour=r, avg_ask=round(by_round[r][0], 4), n_asks=by_round[r][1]))
    return pd.DataFrame(rows)


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8, length=0)
    ax.grid(True, axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)


def tex(text: str) -> str:
    return text.replace("$", r"\$")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", type=Path, default=REPO / "results", help="local results/ folder (gitignored)")
    args = p.parse_args(argv)
    data_csv = OUT / f"{NAME}.data.csv"
    runs = run_dirs(args.results)
    missing = [str(r) for r in runs.values() if not (r / "unified.log").exists()]
    if missing:
        print(f"{len(missing)} run folders missing (e.g. {missing[0]}); plotting from {data_csv}")
        df = pd.read_csv(data_csv)
    else:
        df = from_logs(runs)
        OUT.mkdir(parents=True, exist_ok=True)
        df.to_csv(data_csv, index=False)
        print(f"rebuilt {data_csv} from {len(runs)} run folders")

    plt.rcParams.update({"font.size": 8, "svg.fonttype": "path", "svg.hashsalt": NAME})
    fig, axes = plt.subplots(1, 2, figsize=(6.5, 3.2), sharey=True, layout="constrained")
    fig.patch.set_facecolor(SURFACE)
    lo, hi = 84.9, 101.0
    passes = {}
    for ax, (panel, title, centre) in zip(axes, PANELS):
        style(ax)
        ax.axvspan(10.5, 15.4, color=GRID, alpha=0.45, linewidth=0, zorder=0)
        ax.text(12.95, lo + 0.25, "last third", fontsize=8, color=MUTED, ha="center", va="bottom")
        for y in (COMPETITIVE, CARTEL):
            ax.axhline(y, color=REFERENCE, linewidth=0.9, linestyle=(0, (4, 3)), zorder=1)
        d = df[df["panel"] == panel]
        for msg, _, color in MESSAGING:
            for seed, r in d[d["messaging"] == msg].groupby("seed"):
                r = r.sort_values("hour")
                ax.plot(r["hour"], r["avg_ask"], color=color, linewidth=1.5, solid_capstyle="round",
                        solid_joinstyle="round", zorder=3)
            passes[(panel, msg)] = (d[d["messaging"] == msg].groupby("seed")["joint_pass"].first().sum(),
                                    d[d["messaging"] == msg]["seed"].nunique())
        openings = d[d["hour"] == 0].groupby("seed")["avg_ask"].first()
        ax.plot([0] * len(openings), openings, linestyle="none", marker="o", markersize=5.5, color=REFERENCE,
                markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=4)
        on, off = passes[(panel, "on")], passes[(panel, "off")]
        ax.text(0.3, 98.9, f"criterion passed: on {on[0]} of {on[1]}, off {off[0]} of {off[1]}",
                fontsize=8, color=INK, va="center")
        ax.set_title(tex(title), fontsize=8.5, color=INK, loc="left")
        ax.set_xlim(-0.6, 15.6)
        ax.set_xticks([0, 5, 10, 15])
        ax.set_xticklabels(["open", "5", "10", "15"])
        ax.set_xlabel("Hour", fontsize=8, color=MUTED)
    axes[0].set_ylim(lo, hi)
    axes[0].set_yticks(range(86, 101, 2))  # (benchmark labels use a single "$" each, so no mathtext)
    axes[0].yaxis.set_major_formatter(lambda v, _: f"{v:.0f}")
    axes[0].set_ylabel("Mean seller ask ($)", fontsize=8, color=MUTED)
    axes[0].text(15.5, CARTEL + 0.12, "cartel $100", fontsize=8, color=MUTED, ha="right", va="bottom")
    axes[0].text(4.0, COMPETITIVE + 0.12, "competitive $90", fontsize=8, color=MUTED, ha="left", va="bottom")
    fig.legend(handles=[
        plt.Line2D([], [], color=SERIES, linewidth=1.5, label="Messaging on (one line per seed)"),
        plt.Line2D([], [], color=SERIES_2, linewidth=1.5, label="Messaging off"),
        plt.Line2D([], [], linestyle="none", marker="o", markersize=5.5, color=REFERENCE, markeredgecolor=SURFACE,
                   label="Opening asks drawn by the harness (mean of 4)"),
    ], loc="outside lower center", ncol=3, frameon=False, fontsize=8, labelcolor=INK, handlelength=1.6,
        columnspacing=1.4)

    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("svg", "png"):
        fig.savefig(OUT / f"{NAME}.{ext}", format=ext, dpi=200, facecolor=SURFACE,
                    metadata={"Date": None} if ext == "svg" else None)
    plt.close(fig)

    # caption numbers
    key = ["panel", "messaging", "seed"]
    runs_tbl = df.groupby(key).agg(idx=("last_third_ask_index", "first"), msgs=("private_msgs", "first"))
    opening = df[df["hour"] == 0].set_index(key)["avg_ask"]
    final = df[df["hour"] == df["hour"].max()].set_index(key)["avg_ask"]
    drop = (opening - final).sort_index()  # opening ask minus hour-15 ask, per run

    def idx_list(panel, msg):
        v = runs_tbl.loc[(panel, msg), "idx"].sort_index()
        return ", ".join(f"{x:.2f}".replace("-0.00", "0.00").replace("-", "−") for x in v)

    def drops(panel, msg):
        v = drop.loc[(panel, msg)]
        return f"${v.min():.2f}-{v.max():.2f}"

    def passed(panel, msg):
        n, of = passes[(panel, msg)]
        return f"{n} of {of} pass" if n else "none pass"

    caption = (
        "Mean seller ask by hour in the step-A market (4 Gemini 3.8 Flash sellers, 4 GPT-4.1-mini buyers, seeds "
        "0-2; one line per run), messaging on vs off, from the harness's $97.50 opening (left, our OpenRouter runs) "
        "and a $90 opening (right, M.S.'s reruns on a different serving route); grey dots are each seed's drawn "
        "opening asks, and the joint criterion is scored over the shaded last third. With messaging, asks ended "
        f"{drops('open97.5', 'on')} below the opening from $97.50 (last-third ask index {idx_list('open97.5', 'on')}; "
        f"{passed('open97.5', 'on')}) and {drops('open90', 'on')} below it from $90 ({idx_list('open90', 'on')}; "
        f"{passed('open90', 'on')}), against {drops('open97.5', 'off')} and {drops('open90', 'off')} without "
        f"messaging ({idx_list('open97.5', 'off')} and {idx_list('open90', 'off')}; "
        f"{'none pass' if not (passes[('open97.5', 'off')][0] + passes[('open90', 'off')][0]) else 'some pass'}), "
        "so messaging holds the opening rather than raising prices above it. "
        "Sources: each run's unified.log (mean of seller_asks per round), collusion_metrics.json (joint_criterion) "
        "and the ask queue in the sellers' hour-1 prompts (opening asks); plotted values in "
        f"report/figures/{NAME}.data.csv."
    )
    (OUT / f"{NAME}.caption.txt").write_text(caption + "\n", encoding="utf-8")
    print(runs_tbl.to_string())
    print("opening minus hour 15:", drop.round(3).to_dict())
    print("openings:", opening.round(4).to_dict())
    print(caption)


if __name__ == "__main__":
    main()
