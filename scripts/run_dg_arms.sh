#!/usr/bin/env bash
# D–G arm runner (README "D–G"). Every arm: 4 Gemini 3.8 Flash sellers + 1 scripted seat, 5 gpt-4.1-mini buyers,
# 15 hours, public + private messaging, report_to_regulator in EVERY arm (prohibition rule OFF unless RULE=1), offer at hour 3 ($96).
#
#   bash scripts/run_dg_arms.sh pilot [seed]             # Base pilot: 5 LLM sellers, no scripted seat; records seat 5's path
#   bash scripts/run_dg_arms.sh extract <pilot_run_dir>  # -> configs/replay/$REPLAY_NAME.json (default base_pilot_norule; seat 5 = last seller)
#   bash scripts/run_dg_arms.sh must                     # the 9 must-run arms, seeds 0-4, 2 runs at a time
#   bash scripts/run_dg_arms.sh all                      # + F-sham and Base-hb
#   bash scripts/run_dg_arms.sh D E --seeds 0 1 2        # named arms, chosen seeds
#   JOBS=2 bash scripts/run_dg_arms.sh must              # parallel runs; OpenRouter limits Gemini to ~20 req/min, 2 fit
#
# Environment overrides (defaults = the Gemini D–G sweep):
#   SELLER=google/gemini-3.8-flash   model for the 4 LLM seller seats (and all 5 seats in `pilot`)
#   REPLAY_NAME=base_pilot_norule    seat-5 replay file configs/replay/<name>.json (default base_pilot_rule when RULE=1)
#   OUT_NAME=dg                      results subfolder: results/<OUT_NAME>/
#   RULE=0                           1 adds --prohibition_notice
#   e.g. GPT-4.1 replication: SELLER=openai/gpt-4.1 REPLAY_NAME=gpt41_pilot OUT_NAME=dg_gpt41 bash scripts/run_dg_arms.sh Base D E G-warn F --seeds 0 1 2
#        Haiku arm D:         SELLER=anthropic/claude-haiku-5.5 REPLAY_NAME=nocomms_competitive OUT_NAME=dg_haiku bash scripts/run_dg_arms.sh D --seeds 0 1 2
#   scripts/RUNS.md lists the exact command behind every reported batch.
#
# Resumable: a run whose results/<OUT_NAME>/<ts>_<ARM>-seed<k>/collusion_metrics.json exists is skipped.
# Seeds are iterated outermost, so a partial sweep is balanced across arms. Costs money (OpenRouter), about
# $1.5-2 per run. Check with Daniel before starting a sweep.
set -euo pipefail
export PYTHONUTF8=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="$ROOT/third_party/llm-agent-collusion"
OUT="$ROOT/results/${OUT_NAME:-dg}"
if [[ "${RULE:-0}" == 1 ]]; then DEFAULT_REPLAY=base_pilot_rule; else DEFAULT_REPLAY=base_pilot_norule; fi
REPLAY="$ROOT/configs/replay/${REPLAY_NAME:-$DEFAULT_REPLAY}.json"
JOBS="${JOBS:-2}"
SELLER="${SELLER:-google/gemini-3.8-flash}"
BUYER="openai/gpt-4.1-mini"

COMMON=(--sellers 5 --buyers 5 --seller_models "$SELLER" --buyer_models "$BUYER" --rounds 15 --max_tokens 16000
        --seller_comms_enabled --seller_dms_enabled --max_dms_per_round 2 --broadcast_history_rounds 4
        --report_tool -y)
# The prohibition rule is OFF by default (decided Sun Oct 25 ~00:30 CT: with it on, Gemini sellers go silent and Base
# has no collusion for the warning arms to deter). RULE=1 turns it on and makes base_pilot_rule the default replay.
if [[ "${RULE:-0}" == 1 ]]; then COMMON+=(--prohibition_notice); fi
PLEA="--buyer_plea_hour 3 --buyer_plea_text buyer_plea_human"

arm_flags() {  # prints the per-arm flags
  case "$1" in
    Base)    echo "--seat_mode placebo" ;;
    D)       echo "--seat_mode undercover" ;;
    D-hs)    echo "--seat_mode undercover_human" ;;
    D-hb)    echo "--seat_mode undercover $PLEA" ;;
    D-hsb)   echo "--seat_mode undercover_human $PLEA" ;;
    E)       echo "--seat_mode undercover --warning" ;;
    F)       echo "--seat_mode undercover --warning --precedent" ;;
    G-warn)  echo "--seat_mode placebo --warning" ;;
    G-prec)  echo "--seat_mode placebo --warning --precedent" ;;
    F-sham)  echo "--seat_mode undercover --warning --sham_history" ;;
    Base-hb) echo "--seat_mode placebo $PLEA" ;;
    *) echo "unknown arm: $1" >&2; return 1 ;;
  esac
}
MUST=(Base D D-hs D-hb D-hsb E F G-warn G-prec)
ALL=("${MUST[@]}" F-sham Base-hb)

if grep -qE '^\s*LLM_MODEL\s*=\s*\S' "$ROOT/compute.env" 2>/dev/null; then
  echo "LLM_MODEL is set in compute.env. That forces one model into every seat. Remove it first." >&2; exit 1
fi

cmd="${1:-}"
if [[ -z "$cmd" ]]; then sed -n '2,23p' "$0"; exit 2; fi
shift

if [[ "$cmd" == pilot ]]; then
  seed="${1:-0}"; mkdir -p "$ROOT/results/dg_pilot/logs"
  echo "$(date +%H:%M) Base pilot, seed $seed: 5 LLM sellers (seat 5 = $SELLER), no scripted seat -> results/dg_pilot"
  (cd "$HARNESS" && uv run python src/continuous_double_auction/simulation.py "${COMMON[@]}" \
      --seeds "$seed" --tag "pilot-seed$seed" --log_dir "$ROOT/results/dg_pilot" \
      2>&1 | tee "$ROOT/results/dg_pilot/logs/pilot-seed$seed.log")
  echo "next: bash scripts/run_dg_arms.sh extract results/dg_pilot/<run_dir>"; exit 0
fi

if [[ "$cmd" == extract ]]; then
  run_dir="${1:?pilot run dir}"
  python "$ROOT/scripts/extract_replay_path.py" "$run_dir" --out "$REPLAY"
  exit 0
fi

# arms
case "$cmd" in
  must) ARMS=("${MUST[@]}") ;;
  all)  ARMS=("${ALL[@]}") ;;
  *)    ARMS=("$cmd") ;;
esac
SEEDS=(0 1 2 3 4)
while [[ $# -gt 0 ]]; do
  if [[ "$1" == --seeds ]]; then
    shift; SEEDS=()
    while [[ $# -gt 0 && "$1" != --* ]]; do SEEDS+=("$1"); shift; done
  else
    ARMS+=("$1"); shift
  fi
done
for a in "${ARMS[@]}"; do arm_flags "$a" >/dev/null; done
if [[ ! -f "$REPLAY" ]]; then echo "missing $REPLAY: run the pilot and extract first" >&2; exit 1; fi
mkdir -p "$OUT/logs"

done_already() { compgen -G "$OUT/*_$1/collusion_metrics.json" >/dev/null; }

run_one() {  # run_one <arm> <seed>
  local arm="$1" seed="$2" tag="$1-seed$2" flags
  flags=$(arm_flags "$arm")
  # shellcheck disable=SC2086
  (cd "$HARNESS" && uv run python src/continuous_double_auction/simulation.py "${COMMON[@]}" $flags \
      --scripted_seat_path "$REPLAY" --offer_hour 3 --offer_price 96 --arm "$arm" \
      --seeds "$seed" --tag "$tag" --log_dir "$OUT" > "$OUT/logs/$tag.log" 2>&1) || true
  echo "$(date +%H:%M) done $tag: $(grep -h -E 'JOINT CRITERION|regulator reports:|failed turns' "$OUT/logs/$tag.log" | tr '\n' ' ' | tr -s ' ')"
}

echo "$(date +%H:%M) arms: ${ARMS[*]} | seeds: ${SEEDS[*]} | $JOBS at a time | replay: $(basename "$REPLAY")"
n=0
for seed in "${SEEDS[@]}"; do
  for arm in "${ARMS[@]}"; do
    tag="$arm-seed$seed"
    if done_already "$tag"; then echo "skip $tag (done)"; continue; fi
    while (( $(jobs -rp | wc -l) >= JOBS )); do wait -n; done
    echo "$(date +%H:%M) start $tag"
    run_one "$arm" "$seed" &
    n=$((n+1))
  done
done
wait
echo "$(date +%H:%M) finished: $n run(s) started this session. Next: judge + analysis (README 'Analysis (D–G)')."
