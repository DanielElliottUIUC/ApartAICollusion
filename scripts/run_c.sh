#!/usr/bin/env bash
# Step C (README "C — Shared identity labels", as run Sun Oct 25): 6 shared labels x seeds 0-2 = 18 runs.
# 4 Gemini 3.8 Flash sellers + 4 gpt-4.1-mini buyers, 15 hours, public + private messaging, prohibition rule off,
# no scripted seat, no report action. The no-label baseline is the step-A comms arm (same config, seeds 0-2).
# Each run also writes manipulation_check.json (the bare in-run question); the in-context recheck the report uses
# is scripts/manipulation_recheck.py (on the report branch), run afterwards.
#
#   bash scripts/run_c.sh            # from anywhere; writes results/c/<ts>_C-<label>-seed<k>/, 2 runs at a time
#   JOBS=1 bash scripts/run_c.sh     # one at a time
#
# Resumable: a run whose collusion_metrics.json exists is skipped. Costs money (OpenRouter), about $10 for all 18.
# Check with Daniel before running.
#
# Committed from the copy that produced the reported runs. Changes from that copy: paths are relative to this
# repo (the original ran from a worktree of the wp4-shared-labels branch and waited for the F-sham sweep to
# finish first); the harness commands and flags are unchanged.
set -u; export PYTHONUTF8=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="$ROOT/third_party/llm-agent-collusion"
OUT="$ROOT/results/c"; mkdir -p "$OUT/logs"; JOBS="${JOBS:-2}"
if grep -qE '^\s*LLM_MODEL\s*=\s*\S' "$ROOT/compute.env" 2>/dev/null; then
  echo "LLM_MODEL is set in compute.env. That forces one model into every seat. Remove it first." >&2; exit 1
fi
run(){ local label=$1 seed=$2 tag="C-$1-seed$2"
  (cd "$HARNESS" && uv run python src/continuous_double_auction/simulation.py --sellers 4 --buyers 4 --seller_models google/gemini-3.8-flash --buyer_models openai/gpt-4.1-mini --rounds 15 --max_tokens 16000 --seller_comms_enabled --seller_dms_enabled --max_dms_per_round 2 --broadcast_history_rounds 4 --shared_label "$label" --seeds "$seed" --tag "$tag" --log_dir "$OUT" -y > "$OUT/logs/$tag.log" 2>&1) || true
  echo "$(date +%H:%M) done $tag: $(grep -h -E 'JOINT CRITERION|ask index' "$OUT/logs/$tag.log" | tail -2 | tr '\n' ' ' | tr -s ' ')"; }
for seed in 0 1 2; do for label in claude deepseek blackrock palantir un team_blue; do
  tag="C-$label-seed$seed"; if compgen -G "$OUT/*_$tag/collusion_metrics.json" >/dev/null; then echo "skip $tag"; continue; fi
  while (( $(jobs -rp | wc -l) >= JOBS )); do wait -n; done
  echo "$(date +%H:%M) start $tag"; run "$label" "$seed" &
done; done; wait; echo "$(date +%H:%M) C finished"
