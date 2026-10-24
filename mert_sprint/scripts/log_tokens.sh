#!/usr/bin/env bash
# Append a sprint token snapshot to token-usage/LEDGER.md.
# Uses the Claude usage-ledger (~/.claude/scripts/usage-ledger/usage_report.py) for Claude Code,
# Codex and Grok sessions in this project, plus the proxy's own per-call log for experiment calls.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LEDGER="$ROOT/token-usage/LEDGER.md"; mkdir -p "$ROOT/token-usage"
SINCE="${SINCE:-2026-10-22}"
{
  echo; echo "## $(date '+%Y-%m-%d %H:%M %Z') on $(hostname -s)"
  if [ -f "$HOME/.claude/scripts/usage-ledger/usage_report.py" ]; then
    ( cd "$ROOT" && python3 "$HOME/.claude/scripts/usage-ledger/usage_report.py" --since "$SINCE" )
  else
    echo "(usage_report.py not found on this machine)"
  fi
  echo; echo "Experiment proxy calls (estimated tokens, chars/4):"
  python3 - "$ROOT/token-usage/proxy_usage.jsonl" << 'PY'
import json, sys, collections, os
p = sys.argv[1]
agg = collections.defaultdict(lambda: [0, 0, 0])
if os.path.exists(p):
    for line in open(p):
        try: r = json.loads(line)
        except Exception: continue
        a = agg[f"{r['cli']}:{r['target_model']}"]
        a[0] += 1; a[1] += r.get("prompt_tokens", 0); a[2] += r.get("completion_tokens", 0)
print("| backend:model | calls | prompt tok | completion tok |")
print("|---|---|---|---|")
for k, (n, pi, co) in sorted(agg.items()):
    print(f"| {k} | {n} | {pi:,} | {co:,} |")
tot = [sum(v[i] for v in agg.values()) for i in range(3)]
print(f"| **total** | {tot[0]} | {tot[1]:,} | {tot[2]:,} |")
PY
} >> "$LEDGER"
tail -n 25 "$LEDGER"
