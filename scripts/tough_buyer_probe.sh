#!/usr/bin/env bash
# Tough-buyer probe: do harder-bargaining buyer prompts make buyers competitive while sellers still collude?
# Same market as step A (4 Gemini sellers, 15 rounds), buyers use prompt_templates/buyer_prompt_tough.jinja2.
# Arms: comms + nocomms, seeds 0-1, run 2 at a time (OpenRouter's 20 req/min Gemini limit for new accounts).
# Compare against the existing step A runs with the original buyer prompt (results/phase0_v2, seeds 0-1).
#
#   bash scripts/tough_buyer_probe.sh                          # Haiku buyers (default)
#   BUYER=openai/gpt-4.1-mini bash scripts/tough_buyer_probe.sh
#
# Don't run this at the same time as another Gemini sweep: together they would exceed the rate limit.
set -euo pipefail
export PYTHONUTF8=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/results/tough_buyer_probe"
BUYER="${BUYER:-anthropic/claude-haiku-5.5}"
SHORT=$(echo "$BUYER" | cut -d/ -f2 | cut -d- -f1-3)
mkdir -p "$OUT/logs"
COMMS=(--seller_comms_enabled --seller_dms_enabled --max_dms_per_round 2 --broadcast_history_rounds 4)

run() {  # run <tag> <seed> <extra...>
  local tag="$1" seed="$2"; shift 2
  (cd "$ROOT/third_party/llm-agent-collusion" && uv run python src/continuous_double_auction/simulation.py \
     --sellers 4 --buyers 4 --seller_models google/gemini-3.8-flash --buyer_models "$BUYER" \
     --buyer_prompt_template buyer_prompt_tough.jinja2 --rounds 15 --seeds "$seed" --max_tokens 16000 \
     --log_dir "$OUT" --tag "$tag" -y "$@" > "$OUT/logs/$tag.log" 2>&1)
}

for seed in 0 1; do
  echo "$(date +%H:%M) starting tough $SHORT buyers, seed $seed (comms + nocomms in parallel)"
  run "comms_tough_${SHORT}-seed$seed" "$seed" "${COMMS[@]}" &
  run "nocomms_tough_${SHORT}-seed$seed" "$seed" &
  wait
  grep -h "JOINT CRITERION\|avg trade price\|failed turns\|rate-limit" "$OUT/logs/"*"tough_${SHORT}-seed$seed.log" || true
done
echo "done. Results in $OUT"
