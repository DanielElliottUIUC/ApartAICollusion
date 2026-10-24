#!/usr/bin/env bash
# Model sweep over both markets. Order: Claude 5.5, OpenAI, Gemini, then Grok with every
# pre-4.7 model first and grok-4.7 last (it is slow).
#   ./scripts/run_sweep.sh                  # full sweep
#   MODELS="grok-4.6 grok-4.7" ./scripts/run_sweep.sh   # custom subset
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="${COLLUSION_HACKATHON:-$ROOT/collusion_hackathon}"
ROUNDS="${ROUNDS:-15}"; CDA_ROUNDS="${CDA_ROUNDS:-10}"
DEFAULT_MODELS="claude-haiku-5-5 claude-sonnet-5-5 claude-opus-5-5 gpt-6-luna gpt-5.6-sol gemini-3.8-flash-low grok-4.5 grok-4.6 grok-4.7-build-fast grok-4.7"
MODELS="${MODELS:-$DEFAULT_MODELS}"

curl -s http://127.0.0.1:8787/v1/models >/dev/null || "$ROOT/scripts/start_proxy.sh"
set -a; source "$HARNESS/compute.env"; set +a

for m in $MODELS; do
  tag="$(echo "$m" | tr './' '__')"
  echo "=== $m: Bertrand P0, PC, PC --think ==="
  ( cd "$HARNESS/llm-cartel" && \
    uv run python run_game.py --models "$m" --rounds "$ROUNDS" --seeds 0 --prefix P0 --name "sweep_${tag}_P0" --overwrite -y; \
    uv run python run_game.py --models "$m" --rounds "$ROUNDS" --seeds 0 --prefix PC --name "sweep_${tag}_PC" --overwrite -y; \
    uv run python run_game.py --models "$m" --rounds "$ROUNDS" --seeds 0 --prefix PC --think --name "sweep_${tag}_PC_think" --overwrite -y )
  echo "=== $m: double auction, seller chat + boss pressure ==="
  ( cd "$HARNESS/llm-agent-collusion" && \
    uv run python src/continuous_double_auction/simulation.py --seller_models "$m" "$m" "$m" \
      --buyer_models zip zip zip --rounds "$CDA_ROUNDS" --seller_comms_enabled --boss_pressure --tag "sweep_${tag}_comms_boss" -y )
done

COLLUSION_HACKATHON="$HARNESS" python3 "$ROOT/experiments/sync_runs.py"
"$ROOT/scripts/log_tokens.sh"
