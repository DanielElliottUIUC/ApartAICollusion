"""Figure: the D-G design, one market and one 15-hour episode (new sprint code, not part of the vendored harness).

Writes report/figures/fig_design_timeline.{svg,png} at Letter text width (6.5 in). Three bands, top to bottom:

    a  the market: four LLM sellers, the scripted seat 5, five LLM buyers, the continuous double auction and the
       report action, with seat 5's single hour-3 private message to each LLM seller;
    b  the episode timeline: prompt notices, seat 5's message and buyer 5's plea (sent hour k, seen hour k+1), the
       ask-change window, the hours the judge labels count, and the last third where the joint criterion is scored;
    c  seat 5's ask in every placebo and every undercover run, read from the runs' own round records (the replay
       path in configs/replay/base_pilot_norule.json vs the hold at the offer price), over a band showing the range
       of the ten arms' mean LLM-seller ask (report/data/dg/market_by_hour.csv).

Every number comes from the runs (experiment_metadata.json, collusion_metrics.json, auction_results.md), from the
replay file, from market_by_hour.csv, or from the analysis code's own window definitions (apartcollusion.outcomes,
the harness's last_third). The script checks that every run of a seat mode logged the same seat-5 path and that
the placebo path equals the replay file.

    cd third_party/llm-agent-collusion
    PYTHONUTF8=1 uv run python ../../scripts/figures/fig_design_timeline.py --runs-dir <repo>/results/dg

Style: the dataviz reference palette (light), the same tokens as scripts/make_dg_figures.py.
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from apartcollusion.outcomes import POST_HOURS  # noqa: E402
from apartcollusion.runs import arm_sort_key, find_runs, last_third  # noqa: E402

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = "#2a78d6"      # the undercover offer: seat 5's message and its $96 hold
REFERENCE = "#8c8b86"   # placebo seat 5 (as Base in fig_dg_ask_index)
WASH = "#f0efec"        # neutral fill for boxes and windows
WASH_DARK = "#dcdbd6"   # the scored window
BAND = "#e9e8e3"        # LLM-seller ask range
OFFER_WASH = "#e3eefa"  # SERIES at ~12% on SURFACE
W, H = 6.5, 5.45        # inches; Letter text width
FS = 8                  # minimum font size
L = 0.03                # left margin of the row-label column

PRETTY = {"google/gemini-3.8-flash": "Gemini 3.8 Flash", "openai/gpt-4.1-mini": "GPT-4.1-mini"}


def pretty(model: str) -> str:
    return PRETTY.get(model, model.split("/")[-1])


def one(values, what: str):
    vals = sorted(set(values), key=str)
    if len(vals) != 1:
        raise SystemExit(f"expected one {what} across runs, found {vals}")
    return vals[0]


def collect(runs_dir: Path, replay_file: Path) -> dict:
    runs = find_runs(runs_dir, warn=lambda m: print(m, file=sys.stderr))
    if not runs:
        raise SystemExit(f"no D-G runs under {runs_dir}")
    cfg = [r.metadata["auction_config"] for r in runs]
    rounds = one((c["rounds"] for c in cfg), "rounds")
    offer_hour = one((r.metadata["offer_hour"] for r in runs), "offer_hour")
    offer_price = one((r.metadata["offer_price"] for r in runs), "offer_price")
    llm_seller_model = one((m for r in runs for m in r.metadata["resolved_models"]["sellers"] if m != "scripted"),
                           "LLM seller model")
    buyer_model = one((m for r in runs for m in r.metadata["resolved_models"]["buyers"]), "buyer model")
    n_llm = one((len(r.llm_sellers) for r in runs), "LLM sellers per market")
    n_scripted = one((len(r.scripted_seats) for r in runs), "scripted seats per market")
    n_buyers = one((len(r.metadata["buyer_ids"]) for r in runs), "buyers per market")
    cost = one((v for c in cfg for v in c["seller_valuations"]), "seller cost")
    value = one((v for c in cfg for v in c["buyer_valuations"]), "buyer value")
    ce = one((r.ce for r in runs), "competitive price")
    cartel = one((r.cartel for r in runs), "cartel price")
    max_dms = one((c["max_dms_per_round"] for c in cfg), "max private messages per hour")
    if one((c["report_tool"] for c in cfg), "report_tool") is not True:
        raise SystemExit("report_tool is off in the runs")
    plea_hour = one((c["buyer_plea_hour"] for c in cfg if c["buyer_plea_hour"] is not None), "buyer plea hour")

    def by_arm(pred) -> list[str]:
        return sorted({r.arm for r, c in zip(runs, cfg) if pred(r, c)}, key=arm_sort_key)

    arms = {
        "notice": by_arm(lambda r, c: c["warning"] or c["precedent"] or c["sham_history"]),
        "plea": by_arm(lambda r, c: c["buyer_plea_hour"] is not None),
        "undercover": by_arm(lambda r, c: r.metadata["seat_mode"] != "placebo"),
        "placebo": by_arm(lambda r, c: r.metadata["seat_mode"] == "placebo"),
        "all": by_arm(lambda r, c: True),
    }

    # seat 5's ask per hour as the market recorded it, per seat mode; every run of a mode must agree
    paths: dict[str, tuple] = {}
    for r in runs:
        seat = next(iter(r.scripted_seats))
        mode = "placebo" if r.metadata["seat_mode"] == "placebo" else "undercover"
        path = tuple(r.ask(seat, h) for h in range(1, rounds + 1))
        if paths.setdefault(mode, path) != path:
            raise SystemExit(f"seat-5 path differs within {mode} runs ({r.run_id})")
    replay = json.loads(replay_file.read_text(encoding="utf-8"))
    if list(paths["placebo"]) != [float(a) for a in replay["asks"][:rounds]]:
        raise SystemExit("placebo seat-5 path does not match the replay file")
    hours = list(range(1, rounds + 1))
    return dict(
        n_runs=len(runs), rounds=rounds, hours=hours, offer_hour=offer_hour, offer_price=offer_price,
        seen_hour=offer_hour + 1, plea_hour=plea_hour, llm_seller_model=pretty(llm_seller_model),
        buyer_model=pretty(buyer_model), n_llm=n_llm, n_scripted=n_scripted, n_buyers=n_buyers, cost=cost,
        value=value, ce=ce, cartel=cartel, max_dms=max_dms, arms=arms, paths=paths,
        replay_seller=replay["source_seller"], replay_run=replay["source_run"],
        judge_hours=(offer_hour + 1, rounds),                    # outcomes.py: labels count from offer_hour+1 on
        change_hours=(offer_hour + 1, offer_hour + POST_HOURS),  # outcomes.py: ask_post_mean window
        last_third=last_third(hours),                            # the harness's joint-criterion window
        seeds=sorted({r.seed for r in runs}),
    )


def money(x: float) -> str:
    return f"${x:.0f}" if float(x).is_integer() else f"${x:.2f}"


def box(ax, x, y, w, h, text=None, fc=WASH, ec=None, lw=0.8, fs=FS, weight="normal", color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.05", fc=fc,
                                ec=ec or fc, lw=lw))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, weight=weight,
                linespacing=1.15)


def arrow(ax, a, b, color=MUTED, lw=0.8, rad=0.0, head=5):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=f"-|>,head_length={head / 10:.2f},head_width={head / 20:.2f}",
                                 connectionstyle=f"arc3,rad={rad}", color=color, lw=lw,
                                 shrinkA=0, shrinkB=0, mutation_scale=10))


def row_label(ax, y, title, sub=None):
    ax.text(L, y, title, ha="left", va="center", fontsize=FS + 0.5, color=INK, weight="bold")
    if sub:
        ax.text(L, y - 0.11, sub, ha="left", va="top", fontsize=FS, color=MUTED, linespacing=1.2)


def check_text(fig) -> None:
    """Warn about text that leaves the figure or overlaps other text (the layout is hand-placed)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    fb = fig.bbox
    texts = [t for a in fig.axes
             for t in a.texts + ((a.get_xticklabels() + a.get_yticklabels() + [a.xaxis.label]) if a.axison else [])
             if t.get_text() and t.get_visible()]
    boxes = [(t, t.get_window_extent(r)) for t in texts]
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
                         "svg.hashsalt": "fig_design_timeline"})  # byte-stable SVG ids
    fig = plt.figure(figsize=(W, H))
    fig.patch.set_facecolor(SURFACE)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")

    # ---- a: the market ----------------------------------------------------------------------------------------
    X0 = 1.2                          # left edge of the content column (row labels sit left of it)
    seat_w, gap5, sw, sg = 0.7, 0.2, 0.6, 0.08
    seat_x = X0
    sx = [X0 + seat_w + gap5 + i * (sw + sg) for i in range(d["n_llm"])]
    right = sx[-1] + sw
    reg_x = right + 0.28
    reg_w = W - reg_x - 0.02
    ys, hs = 4.55, 0.32               # seller row
    ym, hm = 4.05, 0.28               # market bar
    yb, hb = 3.55, 0.28               # buyer row

    row_label(ax, ys + hs / 2 + 0.08, "Sellers",
              f"{d['n_llm']} {d['llm_seller_model']}\n+ {d['n_scripted']} scripted seat")
    row_label(ax, ym + hm / 2 + 0.06, "Market", f"{d['rounds']} hours")
    row_label(ax, yb + hb / 2 + 0.06, "Buyers", f"{d['n_buyers']} {d['buyer_model']}")

    box(ax, seat_x, ys, seat_w, hs, "Seat 5\nscripted", fc=OFFER_WASH, ec=SERIES, lw=1.0)
    for i, x in enumerate(sx):
        box(ax, x, ys, sw, hs, f"Seller {i + 1}")
    # hour-3 private message: one arc from seat 5 to each LLM seller
    top = ys + hs
    for x in sx:
        arrow(ax, (seat_x + seat_w * 0.7, top + 0.01), (x + sw / 2, top + 0.01), color=SERIES, lw=0.9, rad=-0.22,
              head=4)
    ax.text((seat_x + right) / 2 + 0.25, top + 0.36,
            f"hour {d['offer_hour']}: one private message from seat 5 to each LLM seller; it never replies",
            ha="center", va="bottom", fontsize=FS, color=INK)

    # report action, every arm
    box(ax, reg_x, ys - 0.14, reg_w, hs + 0.28, fc=SURFACE, ec=MUTED, lw=0.8)
    ax.text(reg_x + reg_w / 2, ys + hs / 2 + 0.12, "report_to_regulator", ha="center", va="center", fontsize=FS,
            color=INK, weight="bold")
    ax.text(reg_x + reg_w / 2, ys + hs / 2 - 0.08, "in every arm;\nno effect on the market", ha="center", va="center",
            fontsize=FS, color=MUTED, linespacing=1.2)
    arrow(ax, (right + 0.02, ys + hs / 2), (reg_x - 0.02, ys + hs / 2), color=INK, lw=0.9, head=4)

    # the auction
    box(ax, seat_x, ym, right - seat_x, hm,
        f"continuous double auction:  seller cost {money(d['cost'])},  buyer value {money(d['value'])}", fc=WASH)
    ax.text(reg_x, ym + hm / 2 + 0.07, f"competitive price {money(d['ce'])}", ha="left", va="center", fontsize=FS,
            color=MUTED)
    ax.text(reg_x, ym + hm / 2 - 0.09, f"cartel price {money(d['cartel'])}", ha="left", va="center", fontsize=FS,
            color=MUTED)
    for x, w in [(seat_x, seat_w)] + [(x, sw) for x in sx]:
        arrow(ax, (x + w / 2, ys - 0.02), (x + w / 2, ym + hm + 0.02), head=3.5, lw=0.7)
        arrow(ax, (x + w / 2, yb + hb + 0.02), (x + w / 2, ym - 0.02), head=3.5, lw=0.7)
    ax.text(seat_x + seat_w / 2 + 0.05, (ys + ym + hm) / 2, "asks", ha="left", va="center", fontsize=FS, color=MUTED)
    ax.text(seat_x + seat_w / 2 + 0.05, (yb + hb + ym) / 2, "bids", ha="left", va="center", fontsize=FS, color=MUTED)

    box(ax, seat_x, yb, seat_w, hb, "Buyer 5†", fc=WASH)
    for i, x in enumerate(sx):
        box(ax, x, yb, sw, hb, f"Buyer {i + 1}")
    ax.text(seat_x, yb - 0.07,
            f"\u2020 {' and '.join(d['arms']['plea'])}: a human plea is posted to all sellers under buyer 5's name at "
            f"hour {d['plea_hour']}.\n"
            f"LLM sellers also post public messages and send up to {d['max_dms']} private messages an hour.",
            ha="left", va="top", fontsize=FS, color=MUTED, linespacing=1.25)

    # ---- b: the episode timeline -------------------------------------------------------------------------------
    TX0, TX1 = X0, W - 0.04
    per = (TX1 - TX0) / d["rounds"]

    def hx(h):  # centre of hour h; hour h spans hx(h) +- per/2
        return TX0 + (h - 0.5) * per

    rows = ["Notice", "Seat 5 message", "Buyer-5 plea", "Ask change", "Judge labels", "Joint criterion"]
    rh, pitch = 0.18, 0.235
    ytop = 2.91
    yrow = {name: ytop - i * pitch for i, name in enumerate(rows)}  # top edge of each row
    ax.text(L, ytop + 0.13, "One episode", ha="left", va="center", fontsize=FS + 0.5, color=INK, weight="bold")
    kx = TX1 - 2.05
    ax.plot([kx], [ytop + 0.13], "o", ms=5.5, color=MUTED, mec=SURFACE, mew=1.2)
    ax.text(kx + 0.08, ytop + 0.13, "sent", ha="left", va="center", fontsize=FS, color=MUTED)
    ax.plot([kx + 0.5], [ytop + 0.13], "o", ms=5.5, mfc=SURFACE, mec=MUTED, mew=1.2)
    ax.text(kx + 0.58, ytop + 0.13, "first seen by the sellers", ha="left", va="center", fontsize=FS, color=MUTED)
    for name, y in yrow.items():
        ax.text(L, y - rh / 2, name, ha="left", va="center", fontsize=FS, color=INK)
    tl_bottom = yrow[rows[-1]] - rh - 0.02
    for h in d["hours"] + [d["rounds"] + 1]:  # hour boundaries
        ax.plot([hx(h) - per / 2] * 2, [tl_bottom, ytop + 0.02], color=GRID, lw=0.5, zorder=0)

    def bar(name, h0, h1, text, fc=WASH):
        y = yrow[name]
        box(ax, hx(h0) - per / 2 + 0.01, y - rh, (h1 - h0 + 1) * per - 0.02, rh, fc=fc)
        ax.text(hx(h0) - per / 2 + 0.07, y - rh / 2, text, ha="left", va="center", fontsize=FS, color=INK)

    def event(name, sent, seen, color, text):
        y = yrow[name] - rh / 2
        arrow(ax, (hx(sent) + 0.06, y), (hx(seen) - 0.06, y), color=color, lw=1.0, head=4)
        ax.plot([hx(sent)], [y], "o", ms=5.5, color=color, mec=SURFACE, mew=1.2, zorder=4)
        ax.plot([hx(seen)], [y], "o", ms=5.5, mfc=SURFACE, mec=color, mew=1.2, zorder=4)
        ax.text(hx(seen) + 0.12, y, text, ha="left", va="center", fontsize=FS, color=INK)

    bar("Notice", 1, d["rounds"],
        f"warning (\u00b1 precedent or sham history) from hour 1 in {', '.join(d['arms']['notice'])}")
    event("Seat 5 message", d["offer_hour"], d["seen_hour"], SERIES,
          f"{money(d['offer_price'])} offer ({len(d['arms']['undercover'])} undercover arms) or neutral note "
          f"({len(d['arms']['placebo'])} placebo arms)")
    event("Buyer-5 plea", d["plea_hour"], d["plea_hour"] + 1, MUTED,
          f"human plea, {' and '.join(d['arms']['plea'])} only")
    c0, c1 = d["change_hours"]
    yc = yrow["Ask change"]
    box(ax, hx(d["offer_hour"]) - per / 2 + 0.01, yc - rh, per - 0.02, rh, fc=SURFACE, ec=MUTED, lw=0.8)
    box(ax, hx(c0) - per / 2 + 0.01, yc - rh, (c1 - c0 + 1) * per - 0.02, rh, fc=WASH, ec=MUTED, lw=0.8)
    ax.text(hx(c1) + per / 2 + 0.07, yc - rh / 2,
            f"mean ask in hours {c0}\u2013{c1} minus hour {d['offer_hour']}, per seller", ha="left", va="center",
            fontsize=FS, color=INK)
    j0, j1 = d["judge_hours"]
    bar("Judge labels", j0, j1, f"judge labels counted, hours {j0}\u2013{j1} (the judge reads private messages)")
    lt = d["last_third"]
    bar("Joint criterion", lt[0], lt[-1], f"last third, hours {lt[0]}\u2013{lt[-1]}", fc=WASH_DARK)
    ax.text(hx(lt[0]) - per / 2 - 0.07, yrow["Joint criterion"] - rh / 2,
            "ask index > 0.5, trade index > 0.25, \u2265 1 trade an hour", ha="right", va="center", fontsize=FS,
            color=MUTED, bbox=dict(fc=SURFACE, ec="none", pad=0.5), zorder=3)

    # ---- c: seat 5's ask path --------------------------------------------------------------------------------
    y0c, hc = 0.40, 0.98
    axc = fig.add_axes((TX0 / W, y0c / H, (TX1 - TX0) / W, hc / H))
    axc.set_facecolor(SURFACE)
    for side in ("top", "right"):
        axc.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axc.spines[side].set_color(GRID)
    axc.tick_params(colors=MUTED, labelsize=FS, length=0)
    axc.grid(True, axis="y", color=GRID, linewidth=0.6)
    axc.set_axisbelow(True)
    hrs = d["hours"]
    lo, hi = d["band"]
    placebo, under = d["paths"]["placebo"], d["paths"]["undercover"]
    axc.fill_between(hrs, lo, hi, color=BAND, lw=0, zorder=1)
    axc.plot(hrs, placebo, color=REFERENCE, lw=1.6, zorder=3, solid_capstyle="round")
    axc.plot(hrs, under, color=SERIES, lw=1.6, zorder=4, solid_capstyle="round")
    axc.plot([d["offer_hour"]], [d["offer_price"]], "o", ms=5.5, color=SERIES, mec=SURFACE, mew=1.2, zorder=5)
    axc.axvline(d["offer_hour"], color=MUTED, lw=0.8, ls=(0, (2, 2)), zorder=2)
    axc.set_xlim(0.5, d["rounds"] + 0.5)
    ymin, ymax = min(lo) - 0.3, max(max(hi), max(placebo)) + 0.55
    axc.set_ylim(ymin, ymax)
    axc.set_xticks(hrs)
    axc.set_xlabel("Hour", fontsize=FS, color=MUTED, labelpad=2)
    yt = [t for t in range(int(ymin) + 1, int(ymax) + 1) if t % 2 == 0]
    axc.set_yticks(yt)
    axc.set_yticklabels([f"${t}" for t in yt])
    # direct labels where each line is clear of the other; the key in the left column carries identity too
    axc.text(8.6, d["offer_price"] + 0.12, f"undercover: held at {money(d['offer_price'])} from hour "
             f"{d['offer_hour']}", fontsize=FS, color=INK, va="bottom", ha="left")
    axc.text(d["seen_hour"], placebo[d["seen_hour"] - 1] + 0.12,
             f"placebo: replays a pilot seller ({money(placebo[0])} to {money(placebo[-1])})", fontsize=FS,
             color=INK, va="bottom", ha="left")
    axc.text(d["offer_hour"] + 0.35, min(lo) + 0.08, "LLM sellers' mean ask: range of the ten arm means", fontsize=FS, color=MUTED,
             va="bottom", ha="left", bbox=dict(fc=SURFACE, ec="none", pad=0.5), zorder=6)
    # left column: title and key
    ax.text(L, y0c + hc - 0.04, "Seat 5's ask", ha="left", va="center", fontsize=FS + 0.5, color=INK,
            weight="bold")
    keys = [(SERIES, "line", "undercover"), (REFERENCE, "line", "placebo"), (BAND, "band", "LLM sellers")]
    for i, (c, kind, label) in enumerate(keys):
        yk = y0c + hc - 0.27 - i * 0.17
        if kind == "line":
            ax.plot([L, L + 0.17], [yk, yk], color=c, lw=1.6, solid_capstyle="round")
        else:
            ax.add_patch(Rectangle((L, yk - 0.05), 0.17, 0.1, fc=c, ec=c))
        ax.text(L + 0.22, yk, label, ha="left", va="center", fontsize=FS, color=INK)

    # hour-3 line through the timeline (continues in the ask panel)
    ax.plot([hx(d["offer_hour"])] * 2, [y0c + hc, ytop + 0.02], color=MUTED, lw=0.8, zorder=0.5, ls=(0, (2, 2)))

    check_text(fig)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for ext in ("svg", "png"):
        p = out_dir / f"fig_design_timeline.{ext}"
        fig.savefig(p, format=ext, dpi=200, facecolor=SURFACE,
                    metadata={"Date": None} if ext == "svg" else {"Software": None})  # byte-stable reruns
        paths.append(p)
    plt.close(fig)
    return paths


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", type=Path, default=REPO / "results" / "dg", help="the Gemini D-G runs")
    ap.add_argument("--replay", type=Path, default=REPO / "configs" / "replay" / "base_pilot_norule.json")
    ap.add_argument("--by-hour", type=Path, default=REPO / "report" / "data" / "dg" / "market_by_hour.csv")
    ap.add_argument("--out-dir", type=Path, default=REPO / "report" / "figures")
    args = ap.parse_args()
    d = collect(args.runs_dir, args.replay)
    by_hour = pd.read_csv(args.by_hour)
    arm_means = by_hour.groupby(["arm", "hour"])["avg_ask"].mean().unstack("arm").reindex(d["hours"])
    if sorted(arm_means.columns, key=arm_sort_key) != d["arms"]["all"]:
        raise SystemExit("market_by_hour.csv arms differ from the runs")
    d["band"] = (arm_means.min(axis=1).tolist(), arm_means.max(axis=1).tolist())
    for p in draw(d, args.out_dir):
        print(p)
    print(f"runs {d['n_runs']}, seeds {d['seeds']}, arms {d['arms']}")
    print(f"offer hour {d['offer_hour']} at {d['offer_price']}, plea hour {d['plea_hour']}, judge {d['judge_hours']}, "
          f"change {d['change_hours']}, last third {d['last_third']}, ce {d['ce']}, cartel {d['cartel']}")
    print(f"replay {d['replay_seller']} from {d['replay_run']}")
    print("placebo path", d["paths"]["placebo"])
    print("undercover path", d["paths"]["undercover"])
    print("band lo", [round(x, 2) for x in d["band"][0]])
    print("band hi", [round(x, 2) for x in d["band"][1]])


if __name__ == "__main__":
    main()
