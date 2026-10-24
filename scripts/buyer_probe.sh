#!/usr/bin/env bash
# Buyer probe: which buyer model is the most competitive while Gemini sellers still collude with messaging on?
# 2 buyers x {comms, nocomms} x seeds 0-1 = 8 runs, run 2 at a time (comms + nocomms of the same buyer/seed).
#
# Why 2 at a time: new OpenRouter accounts are limited to 20 requests/minute on Gemini 3.8 Flash. One run makes
# ~8 Gemini calls/minute, so 2 parallel runs fit; 8 parallel runs got rate-limited and sellers skipped turns.
#
#   bash scripts/buyer_probe.sh            # from the repo root; ~30-40 min, ~$7
set -euo pipefail
export PYTHONUTF8=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/results/buyer_probe"
mkdir -p "$OUT/logs"
COMMS=(--seller_comms_enabled --seller_dms_enabled --max_dms_per_round 2 --broadcast_history_rounds 4)

run() {  # run <tag> <buyer> <seed> <extra...>
  local tag="$1" buyer="$2" seed="$3"; shift 3
  (cd "$ROOT/third_party/llm-agent-collusion" && uv run python src/continuous_double_auction/simulation.py \
     --sellers 4 --buyers 4 --seller_models google/gemini-3.8-flash --buyer_models "$buyer" --rounds 15 \
     --seeds "$seed" --max_tokens 16000 --llm_eval --log_dir "$OUT" --tag "$tag" -y "$@" \
     > "$OUT/logs/$tag.log" 2>&1)
}

for buyer in openai/gpt-4.1-mini deepseek/deepseek-v4.1-flash-1017; do
  short=$(echo "$buyer" | cut -d/ -f2 | cut -d- -f1-3)
  for seed in 0 1; do
    echo "$(date +%H:%M) starting $short seed $seed (comms + nocomms in parallel)"
    run "comms_${short}-seed$seed" "$buyer" "$seed" "${COMMS[@]}" &
    run "nocomms_${short}-seed$seed" "$buyer" "$seed" &
    wait
    grep -h "JOINT CRITERION\|failed turns\|rate-limit" "$OUT/logs/"*"${short}-seed$seed.log" || true
  done
done
echo "done. Results in $OUT"
