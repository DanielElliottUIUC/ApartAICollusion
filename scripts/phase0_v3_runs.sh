#!/usr/bin/env bash
# Step A completion with gpt-4.1-mini buyers (Sat Oct 24 evening): comms + no-comms at seed 2, and the comms arm
# with the prohibition rule ("notice") at seeds 0-2. Seeds 0-1 of comms / no-comms came from scripts/buyer_probe.sh
# (results/buyer_probe/*_{comms,nocomms}_gpt-4.1-mini-seed{0,1}). 4 Gemini 3.8 Flash sellers, 4 gpt-4.1-mini buyers,
# 15 hours. Two runs at a time (Gemini rate limit). Writes results/phase0_v3/.
#
#   bash scripts/phase0_v3_runs.sh   # about 5 runs, ~$5 (OpenRouter); check with Daniel first
#
# Committed from the ad hoc copy that produced the reported runs, with two changes:
#   - ROOT is derived from this script's location instead of a pinned path;
#   - the --tag now carries the seed. In the original, notice seeds 0 and 1 started in the same second with the
#     same tag and so wrote into ONE run directory (results/phase0_v3/20261024_230119_gemini_notice: 8 seller
#     files, metadata of seed 1). Seed 0's numbers (ask index 0.44) survive only in logs/gemini_notice-seed0.log.
set -u; export PYTHONUTF8=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; OUT=$ROOT/results/phase0_v3; mkdir -p "$OUT/logs"
COMMS=(--seller_comms_enabled --seller_dms_enabled --max_dms_per_round 2 --broadcast_history_rounds 4)
run(){ local tag=$1 seed=$2; shift 2
  (cd "$ROOT/third_party/llm-agent-collusion" && uv run python src/continuous_double_auction/simulation.py \
    --sellers 4 --buyers 4 --seller_models google/gemini-3.8-flash --buyer_models openai/gpt-4.1-mini \
    --rounds 15 --seeds "$seed" --max_tokens 16000 --log_dir "$OUT" --tag "$tag-seed$seed" -y "$@" > "$OUT/logs/$tag-seed$seed.log" 2>&1)
  echo "$(date +%H:%M) finished $tag seed $seed (exit $?)"; }
echo "$(date +%H:%M) start pair 1: comms + nocomms seed 2"
run gemini_comms 2 "${COMMS[@]}" & run gemini_nocomms 2 & wait
echo "$(date +%H:%M) start pair 2: notice seeds 0,1"
run gemini_notice 0 "${COMMS[@]}" --prohibition_notice & run gemini_notice 1 "${COMMS[@]}" --prohibition_notice & wait
echo "$(date +%H:%M) start notice seed 2"
run gemini_notice 2 "${COMMS[@]}" --prohibition_notice
echo "=== summary ==="; grep -H -E "JOINT CRITERION|failed turns|rate.limit" "$OUT"/logs/*.log
