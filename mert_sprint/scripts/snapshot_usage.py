#!/usr/bin/env python3
"""Save the sprint's token and cost snapshot into token-usage/ for the dashboard and the usage log. Sprint only:
nothing from other projects on the same machines.

    python3 scripts/snapshot_usage.py     # on each machine that works on the sprint, then commit token-usage/

Two sources, both limited to this project:
  agent work      Claude Code sessions whose transcripts sit in this project's folder under ~/.claude/projects/,
                  priced by ccusage (pinned below). Each machine writes its own token-usage/sprint_agents/<id>.json,
                  <id> an anonymous hash of the host name; the snapshot sums every machine's file in the repo.
  experiment      every model call the market agents made through the subscription proxy: all
                  token-usage/proxy_usage*.jsonl logs (one per machine or shard). Their token counts are estimates.
Writes:
  token-usage/sprint_agents/<id>.json        this machine's sprint agent usage
  token-usage/usage_snapshot.json            sprint totals by model and machine; no hostnames, users or paths
  token-usage/USAGE_LOG.md                   one appended section per snapshot, with tables
  token-usage/usage_by_model.svg             sprint agent tokens by model (millions)
  token-usage/usage_experiment_calls.svg     experiment calls by served model
Costs are API-equivalent list prices from ccusage; the work itself ran on flat subscriptions.
"""

import datetime as dt
import hashlib
import json
import os
import shutil
import socket
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "token-usage"
AGENTS = OUT / "sprint_agents"
CCUSAGE = "ccusage@20.0.43"
M = 1e6


def machine_id() -> str:
    # The sprint box keeps the name the runner gives it (SPRINT_MACHINE=box), so its file replaces box.json.
    return os.environ.get("SPRINT_MACHINE") or "m-" + hashlib.sha1(socket.gethostname().lower().encode()).hexdigest()[:6]


def claude_sessions() -> set[str]:
    """Session ids of every Claude Code transcript in this project's folder (the folder name ends with the repo name)."""
    roots = [p for p in (Path.home() / ".claude" / "projects").glob(f"*{REPO.name}") if p.is_dir()]
    return {f.stem for root in roots for f in root.rglob("*.jsonl")}


def measure_this_machine() -> dict:
    """Sum ccusage's per-session report over this project's sessions (subagent usage is filed under its parent)."""
    npx = shutil.which("npx")
    if not npx:
        raise SystemExit("npx not found: install Node.js to price Claude Code sessions with ccusage.")
    out = subprocess.run([npx, "-y", CCUSAGE, "session", "--json", "--offline"], capture_output=True, text=True,
                         encoding="utf-8", check=True).stdout
    ids = claude_sessions()
    by_model = defaultdict(lambda: {"tokens": 0, "cost_usd": 0.0, "output_tokens": 0, "cached_tokens": 0})
    n = 0
    for s in json.loads(out)["session"]:
        if s.get("agent") != "claude" or s["period"].split("/")[-1] not in ids:
            continue
        n += 1
        for b in s.get("modelBreakdowns") or []:
            m = by_model[b["modelName"]]
            m["tokens"] += b["inputTokens"] + b["outputTokens"] + b["cacheCreationTokens"] + b["cacheReadTokens"]
            m["cost_usd"] += b["cost"]
            m["output_tokens"] += b["outputTokens"]
            m["cached_tokens"] += b["cacheReadTokens"]
    models = [{"model": k, **v, "cost_usd": round(v["cost_usd"], 2)} for k, v in sorted(by_model.items(), key=lambda kv: -kv[1]["tokens"])]
    return {"machine": machine_id(), "measured_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "method": f"Claude Code sessions in this project's folder ({n} sessions), priced by {CCUSAGE}",
            "claude": {"tokens": sum(m["tokens"] for m in models), "cost_usd": round(sum(m["cost_usd"] for m in models), 2),
                       "models": models},
            "codex": {"tokens": 0, "standard_cost_usd": 0.0}}


def proxy_calls() -> tuple[list[dict], list[dict]]:
    """Experiment calls through the subscription proxy, by the model that answered and by log file (machine or shard)."""
    agg = defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0})
    per_log = []
    for log in sorted(OUT.glob("proxy_usage*.jsonl")):
        n = 0
        for line in log.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            d = json.loads(line)
            a = agg[f"{d['cli']}:{d['target_model']}"]
            a["calls"] += 1
            a["prompt_tokens"] += d.get("prompt_tokens") or 0
            a["completion_tokens"] += d.get("completion_tokens") or 0
            n += 1
        per_log.append({"log": log.name, "calls": n})
    return [{"model": k, **v} for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["calls"])], per_log


def bars_svg(path: Path, title: str, rows: list[tuple[str, float, str]], unit: str) -> None:
    """Horizontal bar chart, plain SVG (renders on GitHub)."""
    w, row_h, left = 900, 30, 260
    h = 70 + row_h * len(rows)
    top = max((v for _, v, _ in rows), default=0) or 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="ui-monospace,Menlo,Consolas,monospace">',
             f'<rect width="{w}" height="{h}" fill="#F7F7F4"/>',
             f'<text x="20" y="34" font-size="20" font-weight="700" fill="#1C232B">{title}</text>']
    for i, (label, v, color) in enumerate(rows):
        y = 56 + i * row_h
        bw = max(2, (w - left - 150) * v / top)
        parts += [f'<text x="{left - 10}" y="{y + 19}" font-size="14" text-anchor="end" fill="#1C232B">{label}</text>',
                  f'<rect x="{left}" y="{y + 4}" width="{bw:.1f}" height="20" rx="3" fill="{color}"/>',
                  f'<text x="{left + bw + 8:.1f}" y="{y + 19}" font-size="14" fill="#46515D">{v:,.1f} {unit}</text>']
    path.write_text("\n".join(parts + ["</svg>"]) + "\n", encoding="utf-8")


def main() -> None:
    AGENTS.mkdir(parents=True, exist_ok=True)
    mine = measure_this_machine()
    (AGENTS / f"{mine['machine']}.json").write_text(json.dumps(mine, indent=1) + "\n", encoding="utf-8")
    machines = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(AGENTS.glob("*.json"))]

    by_model = defaultdict(lambda: {"tokens": 0, "cost_usd": 0.0, "output_tokens": 0, "cached_tokens": 0})
    for mc in machines:
        for m in mc["claude"]["models"]:
            t = by_model[m["model"]]
            for k in t:
                t[k] += m.get(k) or 0
    calls, per_log = proxy_calls()
    snap = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "cost_basis": f"API-equivalent list price ({CCUSAGE}). Work ran on flat subscriptions. Sprint project only.",
        "sprint": {
            "machines": [{k: mc[k] for k in ("machine", "measured_at", "method")} | {
                "claude_tokens": mc["claude"]["tokens"], "claude_cost_usd": mc["claude"]["cost_usd"],
                "codex_tokens": mc["codex"]["tokens"], "codex_cost_usd": mc["codex"]["standard_cost_usd"]} for mc in machines],
            "claude": {"tokens": sum(mc["claude"]["tokens"] for mc in machines),
                       "cost_usd": round(sum(mc["claude"]["cost_usd"] for mc in machines), 2),
                       "models": [{"model": k, **v, "cost_usd": round(v["cost_usd"], 2)}
                                  for k, v in sorted(by_model.items(), key=lambda kv: -kv[1]["tokens"])]},
            "codex": {"tokens": sum(mc["codex"]["tokens"] for mc in machines),
                      "standard_cost_usd": round(sum(mc["codex"]["standard_cost_usd"] for mc in machines), 2)},
            "experiment_proxy_calls": calls,
            "experiment_logs": per_log,
        },
    }
    (OUT / "usage_snapshot.json").write_text(json.dumps(snap, indent=1), encoding="utf-8")

    sp = snap["sprint"]
    bars_svg(OUT / "usage_by_model.svg", "Sprint agent tokens by model (millions)",
             [(m["model"], m["tokens"] / M, "#C0571F") for m in sp["claude"]["models"]]
             + ([("codex (all models)", sp["codex"]["tokens"] / M, "#2158A8")] if sp["codex"]["tokens"] else []), "M")
    bars_svg(OUT / "usage_experiment_calls.svg", "Experiment calls by served model",
             [(p["model"], p["calls"], "#1FA187") for p in calls], "calls")

    n_calls = sum(p["calls"] for p in calls)
    lines = [f"## Snapshot {snap['created_at'][:16].replace('T', ' ')}", "",
             f"Sprint agent work: **{(sp['claude']['tokens'] + sp['codex']['tokens']) / M:.1f} M tokens**, "
             f"**${sp['claude']['cost_usd'] + sp['codex']['standard_cost_usd']:,.2f}** at API list prices, "
             f"from {len(machines)} machines. Experiment calls through the proxy: **{n_calls}**.", "",
             "| Machine (anonymous) | Measured | Claude Code (M tokens) | Codex (M tokens) | Cost (USD, list) | Method |",
             "|---|---|---|---|---|---|"]
    lines += [f"| {m['machine']} | {m['measured_at'][:16].replace('T', ' ')} | {m['claude_tokens'] / M:.1f} | {m['codex_tokens'] / M:.1f} | "
              f"{m['claude_cost_usd'] + m['codex_cost_usd']:,.2f} | {m['method']} |" for m in sp["machines"]]
    lines += ["", "| Model | Tokens (M) | Cost (USD, list) |", "|---|---|---|"]
    lines += [f"| {m['model']} | {m['tokens'] / M:.1f} | {m['cost_usd']:,.2f} |" for m in sp["claude"]["models"]]
    lines += ["", "| Experiment calls, served model | Calls | Tokens (estimated) |", "|---|---|---|"]
    lines += [f"| {p['model']} | {p['calls']} | {p['prompt_tokens'] + p['completion_tokens']:,} |" for p in calls]
    lines += ["", "![Sprint agent tokens by model](usage_by_model.svg)", "", "![Experiment calls](usage_experiment_calls.svg)", ""]
    log = OUT / "USAGE_LOG.md"
    head = "" if log.exists() else ("# Sprint token and cost log\n\nAppend-only. Each section is one snapshot written by "
                                    "`scripts/snapshot_usage.py`. Sprint project only: agent sessions in this project and the "
                                    "market agents' calls through the proxy. Costs are API-equivalent list prices; the work ran "
                                    "on flat subscriptions.\n\n")
    with open(log, "a", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")
    print(f"[usage] sprint agents {(sp['claude']['tokens'] + sp['codex']['tokens']) / M:.1f} M tokens from {len(machines)} machines, "
          f"{n_calls} experiment calls -> {OUT}")


if __name__ == "__main__":
    main()
