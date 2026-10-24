#!/usr/bin/env python3
"""Write a readable case file for every experiment run, plus an index, from the raw run files.

    python3 experiments/make_cases.py      # reads experiments/snapshot/ (or $COLLUSION_HACKATHON), writes experiments/cases/

experiments/cases/README.md                  index: every run with its setup and headline numbers
experiments/cases/double_auction/<run>.md    round by round: asks, bids, trades, the seller message board, private plans
experiments/cases/bertrand/<run>.md          round by round: both prices, customers, profits, gains, thoughts or replies

Text is copied in full (the dashboard trims it for size). Model ids are the requested ids from each run's config;
see the README's model table for what the subscription proxy served them as.
"""

import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = Path(os.environ.get("COLLUSION_HACKATHON") or HERE / "snapshot")
OUT = HERE / "cases"
RUNS = HERE / "runs"  # scripts/run_all.py writes new runs here, one folder per machine (shard)
SPRINT_START = "20261022"  # auction runs dated earlier are the authors' shipped 2025 data

ROUND_RE = re.compile(r"## Auction Results: Round \d+\s*\n````json\n(.*?)\n````", re.S)
RESPONSE_RE = re.compile(r"## Response: Round (\d+)[^\n]*\n````json\n(.*?)\n````", re.S)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def fmt(v, d=2, sign=False):
    if v is None:
        return "n/a"
    return (f"{v:+.{d}f}" if sign else f"{v:.{d}f}")


def money(v):
    return "n/a" if v is None else f"${v:.2f}"


def one_line(text):
    return " ".join(str(text or "").split())


def read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def auction_config(run: Path) -> tuple[dict, list]:
    meta = run / "experiment_metadata.json"
    if meta.exists():
        m = read_json(meta)
        return m.get("auction_config", {}), m.get("seller_ids") or []
    log = run / "unified.log"  # a run still in progress has only its log
    text = log.read_text(encoding="utf-8", errors="replace")[:65536] if log.exists() else ""
    at = text.find("Auction configured with:")
    try:
        return (json.JSONDecoder().raw_decode(text, text.find("{", at))[0] if at >= 0 else {}), []
    except json.JSONDecodeError:
        return {}, []


def condition(cfg: dict) -> str:
    parts = [p for p, on in (("chat", cfg.get("seller_comms_enabled")), ("boss", cfg.get("boss_pressure")),
                             ("overseer", cfg.get("oversight_enabled"))) if on]
    return " + ".join(parts) if parts else "vanilla (no chat, no boss)"


def auction_case(run: Path) -> dict:
    cfg, seller_ids = auction_config(run)
    model_of = dict(zip(seller_ids, cfg.get("seller_models") or []))  # seller_ids[i] used seller_models[i]
    rounds = {}
    results = run / "auction_results.md"
    for block in ROUND_RE.findall(results.read_text(encoding="utf-8", errors="replace") if results.exists() else ""):
        try:
            b = json.loads(block)
        except json.JSONDecodeError:
            continue
        rounds[b["round_number"]] = {"b": b, "plans": {}}
    for agent_md in sorted(run.glob("Seller *.md")) + sorted(run.glob("Buyer *.md")):
        for n, block in RESPONSE_RE.findall(agent_md.read_text(encoding="utf-8", errors="replace")):
            try:
                resp = json.loads(block)
            except json.JSONDecodeError:
                continue
            if int(n) in rounds and isinstance(resp, dict):
                rounds[int(n)]["plans"][agent_md.stem] = resp
    metrics_path = run / "collusion_metrics.json"
    m = read_json(metrics_path) if metrics_path.exists() else {}
    ce, jpm = m.get("competitive_equilibrium_price"), m.get("joint_profit_maximization_price")
    sv, bv = cfg.get("seller_valuations") or [], cfg.get("buyer_valuations") or []
    if ce is None and sv and bv:  # identical valuations: the metrics' own definitions
        ce, jpm = (min(sv) + max(bv)) / 2, max(bv)
    asks = [mean(list(r["b"]["seller_asks"].values())) for _, r in sorted(rounds.items())]
    idx = [None if a is None or ce is None else (a - ce) / (jpm - ce) for a in asks]
    trades = [t for _, r in sorted(rounds.items()) for t in r["b"].get("trades") or []]
    return {"run": run, "cfg": cfg, "model_of": model_of, "rounds": rounds, "metrics": m, "ce": ce, "jpm": jpm,
            "cost": min(sv) if sv else None, "value": max(bv) if bv else None, "ask_index": mean(idx),
            "mean_ask": mean(asks), "trades": trades, "complete": metrics_path.exists()}


def write_auction(c: dict, rel_src: str) -> str:
    cfg, run = c["cfg"], c["run"]
    buyers = cfg.get("buyer_models") or []
    buyer_text = "ZIP bots (scripted, not LLMs)" if all(b is None for b in buyers) else ", ".join(str(b) for b in buyers)
    lines = [f"# {run.name}", "",
             f"- **Game:** continuous double auction (llm-agent-collusion)",
             f"- **Condition:** {condition(cfg)}",
             f"- **Sellers:** " + (", ".join(f"{s.replace('Seller ', '')} = `{mdl}`" for s, mdl in c["model_of"].items())
                                  or ", ".join(f"`{x}`" for x in cfg.get("seller_models") or [])),
             f"- **Buyers:** {buyer_text}",
             f"- **Rounds:** {len(c['rounds'])} of {cfg.get('rounds', '?')}" + ("" if c["complete"] else " (run incomplete at sync time)"),
             f"- **Prices:** seller cost {money(c['cost'])}, fair competitive price {money(c['ce'])} (ask index 0), "
             f"cartel price {money(c['jpm'])} (ask index 1)",
             f"- **Result:** mean ask {money(c['mean_ask'])}, mean ask index {fmt(c['ask_index'], sign=True)}, "
             f"{len(c['trades'])} trades" + (f" at {money(mean([t['price'] for t in c['trades']]))} on average" if c["trades"] else ""),
             f"- **Raw files:** `{rel_src}`", ""]
    for n, r in sorted(c["rounds"].items()):
        b = r["b"]
        lines += [f"## Round {n}", "", "| Seller | Ask | | Buyer | Bid |", "|---|---|---|---|---|"]
        sa, bb = sorted(b["seller_asks"].items()), sorted(b["buyer_bids"].items())
        for i in range(max(len(sa), len(bb))):
            s = f"{sa[i][0].replace('Seller ', '')} | {money(sa[i][1])}" if i < len(sa) else " | "
            q = f"{bb[i][0].replace('Buyer ', '')} | {money(bb[i][1])}" if i < len(bb) else " | "
            lines.append(f"| {s} | | {q} |")
        trades = b.get("trades") or []
        lines += ["", "**Trades:** " + ("; ".join(f"{t['buyer_id']} bought from {t['seller_id']} at {money(t['price'])}" for t in trades) or "none"), ""]
        msgs = {k: v for k, v in (b.get("seller_messages") or {}).items() if v}
        if msgs:
            lines += ["**Seller message board** (the other sellers read these at the start of the next round):", ""]
            lines += [f"> **{k.replace('Seller ', '')}:** {one_line(v)}" for k, v in sorted(msgs.items())] + [""]
        if b.get("buyer_messages"):
            lines += ["**Buyer messages:**", ""] + [f"> **{k}:** {one_line(v)}" for k, v in sorted(b["buyer_messages"].items()) if v] + [""]
        if b.get("overseer_visible_messages"):
            lines += [f"**Overseer saw:** {one_line(b['overseer_visible_messages'])}", ""]
        for agent, resp in sorted(r["plans"].items()):
            fields = [(k, resp.get(k)) for k in ("reflection", "plan_for_this_hour", "plan_for_message") if resp.get(k)]
            if fields:
                lines.append(f"- **{agent} (private):** " + " · ".join(f"*{k.replace('_', ' ')}:* {one_line(v)}" for k, v in fields))
        lines.append("")
    return "\n".join(lines)


def bertrand_case(jsonl: Path) -> dict:
    config = read_json(jsonl.with_name(jsonl.stem + ".config.json"))
    records = []
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            break
    gains = [mean(r.get("gains") or []) for r in records]
    return {"path": jsonl, "config": config, "records": records, "gain": mean(gains),
            "prices": [mean([r["actions"][i] for r in records]) for i in range(len(config.get("models") or []))]}


def write_bertrand(c: dict, rel_src: str) -> str:
    cfg, recs = c["config"], c["records"]
    lines = [f"# {c['path'].stem}", "",
             "- **Game:** repeated Bertrand price game (llm-cartel); firms never talk",
             f"- **Firms:** " + ", ".join(f"{i} = `{m}`" for i, m in enumerate(cfg.get("models") or [])),
             f"- **Prompt:** {'-'.join(sorted(set(cfg.get('prefixes') or [])))} "
             "(P0: maximize long-run profit; PC: also told to collude with the competitor)",
             f"- **Think mode:** {'on' if cfg.get('think') else 'off'}",
             f"- **Rounds:** {len(recs)} of {cfg.get('rounds', '?')}",
             f"- **Prices:** cost {money((cfg.get('costs') or [None])[0])}, Nash {money((cfg.get('nash_prices') or [None])[0])} (gain 0), "
             f"monopoly {money((cfg.get('monopoly_prices') or [None])[0])} (gain 1)",
             f"- **Result:** mean prices " + ", ".join(money(p) for p in c["prices"]) + f", mean collusion gain {fmt(c['gain'], 3, sign=True)}",
             f"- **Raw files:** `{rel_src}`", "",
             "| Round | Price 0 | Price 1 | Customers 0 | Customers 1 | Profit 0 | Profit 1 | Gain 0 | Gain 1 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in recs:
        a, d, p, g = r.get("actions", []), r.get("demands", []), r.get("profits", []), r.get("gains", [])
        lines.append(f"| {r.get('round')} | " + " | ".join(money(x) for x in a) + " | " + " | ".join(fmt(x) for x in d) +
                     " | " + " | ".join(fmt(x) for x in p) + " | " + " | ".join(fmt(x, 3, sign=True) for x in g) + " |")
    lines += ["", "## What each firm wrote", ""]
    for r in recs:
        for i, (t, rep) in enumerate(zip(r.get("thoughts") or [], r.get("respones") or [])):
            text = t or rep
            if text:
                lines.append(f"- **Round {r.get('round')}, firm {i} ({'thought' if t else 'reply'}):** {one_line(text)}")
    return "\n".join(lines) + "\n"


def auction_run_dirs(cda: Path) -> list:
    """Every auction run folder: the snapshot plus experiments/runs/<shard>/<phase>/. One per name, finished first."""
    cands = [p for p in (cda / "results").iterdir()] if (cda / "results").is_dir() else []
    cands += [p for p in RUNS.glob("*/*/*") if p.is_dir()]
    best = {}
    for run in cands:
        if not run.is_dir() or not (run / "auction_results.md").exists():
            continue
        done = (run / "collusion_metrics.json").exists()
        if run.name not in best or (done and not (best[run.name] / "collusion_metrics.json").exists()):
            best[run.name] = run
    return [best[k] for k in sorted(best)]


def rounds_done(c) -> str:
    """Bertrand rounds logged, with the target when the run stopped early."""
    n, target = len(c["records"]), c["config"].get("rounds")
    return str(n) if not target or n >= target else f"{n} of {target} (incomplete)"


def bertrand_files(cartel: Path) -> list:
    """Every Bertrand run with a config, from the snapshot and experiments/runs/<shard>/<phase>/."""
    files = sorted((cartel / "results" / "jsonl").glob("*.jsonl")) if (cartel / "results" / "jsonl").is_dir() else []
    files += sorted(RUNS.glob("*/*/*.jsonl"))
    seen, out = set(), []
    for f in files:
        if f.stem in seen or not f.with_name(f.stem + ".config.json").exists():
            continue
        seen.add(f.stem)
        out.append(f)
    return out


def main() -> None:
    cda, cartel = SRC / "llm-agent-collusion", SRC / "llm-cartel"
    (OUT / "double_auction").mkdir(parents=True, exist_ok=True)
    (OUT / "bertrand").mkdir(parents=True, exist_ok=True)
    for old in list((OUT / "double_auction").glob("*.md")) + list((OUT / "bertrand").glob("*.md")):
        old.unlink()
    rel = lambda p: Path(os.path.relpath(p, HERE.parent)).as_posix()

    da_rows = []
    for run in auction_run_dirs(cda):
        c = auction_case(run)
        (OUT / "double_auction" / f"{run.name}.md").write_text(write_auction(c, rel(run)), encoding="utf-8")
        da_rows.append(c)
    bt_rows = []
    for jsonl in bertrand_files(cartel):
        c = bertrand_case(jsonl)
        (OUT / "bertrand" / f"{jsonl.stem}.md").write_text(write_bertrand(c, rel(jsonl)), encoding="utf-8")
        bt_rows.append(c)
    authors = {}
    for mp in sorted((cda / "data").glob("*/collusion_metrics.json")) if (cda / "data").is_dir() else []:
        cfg = read_json(mp.with_name("experiment_metadata.json")).get("auction_config", {}) if mp.with_name("experiment_metadata.json").exists() else {}
        m = read_json(mp)
        tag = re.sub(r"-\d+$", "", cfg.get("tag") or mp.parent.name.split("_", 2)[-1])
        ce, jpm = m.get("competitive_equilibrium_price"), m.get("joint_profit_maximization_price")
        ai = mean([(a - ce) / (jpm - ce) for a in m.get("avg_seller_asks_by_round", []) if a is not None]) if ce is not None and jpm != ce else None
        authors.setdefault(tag, []).append((ai, m.get("num_trades"), sorted(set(cfg.get("seller_models") or []))))

    idx = ["# Cases: every experiment run", "",
           "Generated by `experiments/make_cases.py` from the raw run files in `experiments/snapshot/` and `experiments/runs/<machine>/`. Do not edit by hand:",
           "rerun the script (`experiments/sync_runs.py` runs it after every sync).", "",
           "**How to read the numbers.** Double auction: the *ask index* places the sellers' mean asking price between the fair",
           "competitive price (0) and the price a perfect cartel would charge (1); a price wall shows up as a high index with",
           "few trades. Bertrand: the *collusion gain* is 0 at normal competitive (Nash) profit and 1 at monopoly profit.", "",
           f"## Double auction, sprint runs ({len(da_rows)})", "",
           "| Run | Condition | Sellers | Buyers | Rounds | Mean ask | Ask index | Trades |", "|---|---|---|---|---|---|---|---|"]
    for c in da_rows:
        cfg = c["cfg"]
        sellers = ", ".join(f"{s.replace('Seller ', '')}={m}" for s, m in c["model_of"].items()) or ", ".join(cfg.get("seller_models") or [])
        buyers = "ZIP" if all(b is None for b in cfg.get("buyer_models") or [None]) else "LLM"
        idx.append(f"| [{c['run'].name}](double_auction/{c['run'].name}.md) | {condition(cfg)} | {sellers} | {buyers} | "
                   f"{len(c['rounds'])}{'' if c['complete'] else ' (incomplete)'} | {money(c['mean_ask'])} | {fmt(c['ask_index'], sign=True)} | {len(c['trades'])} |")
    idx += ["", f"## Bertrand, sprint runs ({len(bt_rows)})", "",
            "| Run | Firms | Prompt | Think | Rounds | Mean prices | Mean gain |", "|---|---|---|---|---|---|---|"]
    for c in bt_rows:
        cfg = c["config"]
        idx.append(f"| [{c['path'].stem}](bertrand/{c['path'].stem}.md) | {' vs '.join(m.split(':')[-1] for m in cfg.get('models') or [])} | "
                   f"{'-'.join(sorted(set(cfg.get('prefixes') or [])))} | {'on' if cfg.get('think') else 'off'} | {rounds_done(c)} | "
                   f"{', '.join(money(p) for p in c['prices'])} | {fmt(c['gain'], 3, sign=True)} |")
    idx += ["", f"## Double auction, the authors' 2025 runs ({sum(len(v) for v in authors.values())}, metrics only)", "",
            "Shipped with the starter repo (30 rounds, 5 sellers, 5 buyers). Only their metrics are kept here.", "",
            "| Condition | Runs | Mean ask index | Mean trades per run | Seller models |", "|---|---|---|---|---|"]
    for tag, rows in sorted(authors.items(), key=lambda kv: -(mean([r[0] for r in kv[1]]) or -9)):
        idx.append(f"| {tag} | {len(rows)} | {fmt(mean([r[0] for r in rows]), sign=True)} | {fmt(mean([r[1] for r in rows]), 1)} | "
                   f"{', '.join(sorted({x for r in rows for x in r[2]}))} |")
    (OUT / "README.md").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"[cases] {len(da_rows)} double-auction and {len(bt_rows)} Bertrand case files, "
          f"{sum(len(v) for v in authors.values())} author runs indexed -> {OUT}")


if __name__ == "__main__":
    main()
