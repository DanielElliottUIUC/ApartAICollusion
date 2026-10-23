#!/usr/bin/env python3
"""Save an anonymised token and cost snapshot into token-usage/ for the dashboard and the usage log.

    python3 scripts/snapshot_usage.py     # run after the shared token logger (/tokenlog, log_token_usage.py)

Reads the cross-vendor ledger the logger maintains (codex-home token-usage/: per-machine latest snapshots and the
global roll-up) plus this repo's proxy call log, and writes:
  token-usage/usage_snapshot.json   totals by engine, model and month; no hostnames, users or paths
  token-usage/USAGE_LOG.md          one appended section per snapshot, with tables
  token-usage/usage_by_model.svg    tokens by model (billions)
  token-usage/usage_by_month.svg    tokens by month and engine (billions)
Costs are API-equivalent list prices from ccusage; the work itself ran on flat subscriptions.
"""

import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "token-usage"
LEDGER = next((p for p in (Path.home() / ".config/codex-home/token-usage", Path.home() / ".codex/token-usage")
               if (p / "global/latest.json").exists()), None)
B = 1e9


def models(rows, cost_key):
    return [{"model": r["model"], "tokens": r["total_tokens"], "cost_usd": round(r.get(cost_key) or 0, 2),
             "output_tokens": r.get("output_tokens"),
             "cached_tokens": r.get("cached_input_tokens") or r.get("cache_read_tokens") or r.get("cached_read_tokens")}
            for r in sorted(rows, key=lambda r: -r["total_tokens"])]


def months(rows, cost_key):
    return [{"month": r["month"], "tokens": r["total_tokens"], "cost_usd": round(r.get(cost_key) or 0, 2)} for r in rows]


def proxy_calls() -> list[dict]:
    """Experiment calls made through the subscription proxy, by the model that actually answered."""
    agg = defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0})
    log = OUT / "proxy_usage.jsonl"
    for line in log.read_text().splitlines() if log.exists() else []:
        d = json.loads(line)
        a = agg[f"{d['cli']}:{d['target_model']}"]
        a["calls"] += 1
        a["prompt_tokens"] += d.get("prompt_tokens") or 0
        a["completion_tokens"] += d.get("completion_tokens") or 0
    return [{"model": k, **v} for k, v in sorted(agg.items(), key=lambda kv: -kv[1]["calls"])]


def bars_svg(path: Path, title: str, rows: list[tuple[str, float, str]], unit: str) -> None:
    """Horizontal bar chart, plain SVG (renders on GitHub)."""
    w, row_h, left = 900, 30, 260
    h = 70 + row_h * len(rows)
    top = max(v for _, v, _ in rows) or 1
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="ui-monospace,Menlo,Consolas,monospace">',
             f'<rect width="{w}" height="{h}" fill="#F7F7F4"/>',
             f'<text x="20" y="34" font-size="20" font-weight="700" fill="#1C232B">{title}</text>']
    for i, (label, v, color) in enumerate(rows):
        y = 56 + i * row_h
        bw = max(2, (w - left - 150) * v / top)
        parts += [f'<text x="{left - 10}" y="{y + 19}" font-size="14" text-anchor="end" fill="#1C232B">{label}</text>',
                  f'<rect x="{left}" y="{y + 4}" width="{bw:.1f}" height="20" rx="3" fill="{color}"/>',
                  f'<text x="{left + bw + 8:.1f}" y="{y + 19}" font-size="14" fill="#46515D">{v:,.3f} {unit}</text>']
    path.write_text("\n".join(parts + ["</svg>"]) + "\n", encoding="utf-8")


def main() -> None:
    if LEDGER is None:
        raise SystemExit("No token ledger found: run the shared token logger first (/tokenlog).")
    g = json.loads((LEDGER / "global/latest.json").read_text())
    a = g["agent_usage"]
    claude = a["claude_code_reconciled"] if (a.get("claude_code_reconciled") or {}).get("available") else a["claude_code"]
    empty = {"totals": {"total_tokens": 0, "cost_usd": 0}, "models": [], "monthly": []}
    grok = a["grok"] if (a.get("grok") or {}).get("available") else empty
    # Older Claude Code state: newer ledgers report it as an orphan-run lower bound.
    leg = a.get("claude_code_legacy_state") or {}
    legacy = leg.get("totals") or (leg.get("orphan_last_run") or {}).get("totals") or {}
    snaps = sorted(m["created_at_utc"][:10] for m in g["source"].get("machines", []))
    this = max((LEDGER / "latest").glob("*.json"), key=lambda p: p.stat().st_mtime)
    t = json.loads(this.read_text())["agent_usage"]
    snap = {
        "created_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "ledger_created_at": g["created_at_local"],
        "cost_basis": "API-equivalent list price (ccusage; Grok as reported by its CLI). Codex fast-adjusted = standard x 2.5. Work ran on flat subscriptions.",
        "whole_lab": {
            "machines": g["source"].get("machine_count"),
            "snapshot_dates": [snaps[0], snaps[-1]] if snaps else None,
            "codex": {"tokens": a["codex"]["totals"]["total_tokens"], "standard_cost_usd": round(a["codex"]["totals"]["standard_cost_usd"], 2),
                      "fast_adjusted_cost_usd": round(a["codex"]["totals"]["fast_adjusted_cost_usd"], 2),
                      "models": models(a["codex"]["models"], "standard_cost_usd"), "monthly": months(a["codex"]["monthly"], "standard_cost_usd")},
            # Claude: the logger's reconciled view (never add overlapping collectors); months come from ccusage.
            "claude": {"tokens": claude["totals"]["total_tokens"], "cost_usd": round(claude["totals"]["cost_usd"], 2),
                       "models": models(claude["models"], "cost_usd"), "monthly": months(a["claude_code"]["monthly"], "cost_usd")},
            "grok": {"tokens": grok["totals"]["total_tokens"], "cost_usd": round(grok["totals"]["cost_usd"], 2),
                     "models": models(grok.get("models") or [], "cost_usd"), "monthly": months(grok.get("monthly") or [], "cost_usd")},
            "claude_legacy": {"tokens": legacy.get("total_tokens", 0), "cost_usd": round(legacy.get("cost_usd") or 0, 2),
                              "note": "Older Claude Code state, kept separate from the ccusage totals (never added to them)."},
        },
        "sprint_box": {
            "claude": {"tokens": t["claude_code"]["totals"]["total_tokens"], "cost_usd": round(t["claude_code"]["totals"]["cost_usd"], 2),
                       "models": models(t["claude_code"]["models"], "cost_usd")},
            "codex": {"tokens": t["codex"]["totals"]["total_tokens"], "standard_cost_usd": round(t["codex"]["totals"]["standard_cost_usd"], 2)},
            "experiment_proxy_calls": proxy_calls(),
        },
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "usage_snapshot.json").write_text(json.dumps(snap, indent=1), encoding="utf-8")

    wl = snap["whole_lab"]
    bars_svg(OUT / "usage_by_model.svg", "Tokens by model, whole lab (billions)",
             sorted([(m["model"], m["tokens"] / B, "#2158A8") for m in wl["codex"]["models"]] +
                    [(m["model"], m["tokens"] / B, "#C0571F") for m in wl["claude"]["models"]] +
                    [(m["model"], m["tokens"] / B, "#1FA187") for m in wl["grok"]["models"]], key=lambda r: -r[1])[:24], "B")
    by_month = defaultdict(float)
    for m in wl["codex"]["monthly"] + wl["claude"]["monthly"] + wl["grok"]["monthly"]:
        by_month[m["month"]] += m["tokens"] / B
    bars_svg(OUT / "usage_by_month.svg", "Tokens by month, Codex + Claude + Grok (billions)",
             [(k, v, "#1FA187") for k, v in sorted(by_month.items())], "B")

    total_b = (wl["codex"]["tokens"] + wl["claude"]["tokens"] + wl["grok"]["tokens"]) / B
    list_cost = wl["codex"]["standard_cost_usd"] + wl["claude"]["cost_usd"] + wl["grok"]["cost_usd"]
    lines = [f"## Snapshot {snap['created_at'][:16].replace('T', ' ')}", "",
             f"Whole lab ({wl['machines']} machines; machine snapshots dated {wl['snapshot_dates'][0]} to {wl['snapshot_dates'][1]}): "
             f"**{total_b:.2f} B tokens**, **${list_cost:,.0f}** at API list prices "
             f"(with Codex fast-adjusted: ${list_cost - wl['codex']['standard_cost_usd'] + wl['codex']['fast_adjusted_cost_usd']:,.0f}).", "",
             "| Engine | Tokens (B) | Cost (USD, list) |", "|---|---|---|",
             f"| Codex | {wl['codex']['tokens'] / B:.3f} | {wl['codex']['standard_cost_usd']:,.2f} (fast-adjusted {wl['codex']['fast_adjusted_cost_usd']:,.2f}) |",
             f"| Claude Code (reconciled) | {wl['claude']['tokens'] / B:.3f} | {wl['claude']['cost_usd']:,.2f} |",
             f"| Grok | {wl['grok']['tokens'] / B:.3f} | {wl['grok']['cost_usd']:,.2f} |",
             f"| Claude Code, older state (separate) | {wl['claude_legacy']['tokens'] / B:.3f} | {wl['claude_legacy']['cost_usd']:,.2f} |", "",
             "| Model | Tokens (B) | Cost (USD, list) |", "|---|---|---|"]
    lines += [f"| {m['model']} | {m['tokens'] / B:.3f} | {m['cost_usd']:,.2f} |"
              for m in sorted(wl["codex"]["models"] + wl["claude"]["models"] + wl["grok"]["models"], key=lambda m: -m["tokens"])]
    sb = snap["sprint_box"]
    lines += ["", f"Sprint box: Claude Code {sb['claude']['tokens'] / 1e6:.1f} M tokens (${sb['claude']['cost_usd']:,.2f}), "
              f"Codex {sb['codex']['tokens'] / 1e6:.1f} M tokens (${sb['codex']['standard_cost_usd']:,.2f}). "
              f"Experiment calls through the proxy: {sum(p['calls'] for p in sb['experiment_proxy_calls'])} logged.", "",
              "![Tokens by model](usage_by_model.svg)", "", "![Tokens by month](usage_by_month.svg)", ""]
    log = OUT / "USAGE_LOG.md"
    head = "" if log.exists() else ("# Token and cost log\n\nAppend-only. Each section is one snapshot written by "
                                    "`scripts/snapshot_usage.py` from the cross-vendor token ledger. Costs are API-equivalent "
                                    "list prices; the work ran on flat subscriptions.\n\n")
    with open(log, "a", encoding="utf-8") as f:
        f.write(head + "\n".join(lines) + "\n")
    print(f"[usage] whole lab {total_b:.2f} B tokens, ${list_cost:,.0f} list; "
          f"sprint box Claude {sb['claude']['tokens'] / 1e6:.1f} M tokens -> {OUT}")


if __name__ == "__main__":
    main()
