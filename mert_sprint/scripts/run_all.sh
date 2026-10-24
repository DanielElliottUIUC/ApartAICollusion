#!/usr/bin/env bash
# One entry point for every remaining run, split across N machines. See scripts/run_all.py and notes/RUN_PLAN.md.
#   scripts/run_all.sh plan [--shard 2/3]           # every run, its shard and status, per shard progress
#   scripts/run_all.sh run --shard 1/3 --jobs 6     # the Grok Bot box
#   scripts/run_all.sh run --shard 2/3 --jobs 3     # Mert's machine m1
#   scripts/run_all.sh run --shard 3/3 --jobs 3     # Mert's machine m2
#   scripts/run_all.sh merge                        # pull, rebuild docs, commit, push
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="${COLLUSION_HACKATHON:-}"
for h in "$HARNESS" "$ROOT/collusion_hackathon" /workspace/collusion_hackathon; do
  if [ -n "$h" ] && [ -f "$h/compute.env" ]; then set -a; source "$h/compute.env"; set +a; export COLLUSION_HACKATHON="$h"; break; fi
done
unset LLM_MODEL  # forces one model into every seat in Daniel's harness
export LLM_BASE_URL="${LLM_BASE_URL:-http://127.0.0.1:8787/v1}" LLM_API_KEY="${LLM_API_KEY:-subscription-proxy}"
if [ "${1:-}" = "run" ] && [ ! -d "${DANIEL_REPO:-$ROOT/../ApartAICollusion}" ] && [ ! -d /workspace/ApartAICollusion ]; then
  # Pinned to the commit the box runs (Daniel's main on Oct 24, with our merged PR #9), so every shard runs the same code.
  git clone https://github.com/DanielElliottUIUC/ApartAICollusion "$ROOT/../ApartAICollusion" \
    && git -C "$ROOT/../ApartAICollusion" checkout -q 788092c \
    || echo "could not clone Daniel's repo; phases A and B will fail"
fi
exec python3 "$ROOT/scripts/run_all.py" "$@"
