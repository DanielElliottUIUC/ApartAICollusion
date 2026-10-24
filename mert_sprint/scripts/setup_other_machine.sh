#!/usr/bin/env bash
# One-command setup on a fresh machine (Linux or macOS).
#   git clone https://github.com/BARDAK1995/apart-collusion-sprint-2026.git
#   cd apart-collusion-sprint-2026 && ./scripts/setup_other_machine.sh
# Needs: git, python3, uv (https://docs.astral.sh/uv/). Uses whatever of codex, claude, agy, grok
# CLIs are installed and signed in on this machine; no API keys are required for those.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS="${COLLUSION_HACKATHON:-$ROOT/collusion_hackathon}"
PIN="d585a7b"   # Poseidon starter commit our runs used

command -v uv >/dev/null || { echo "Install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }

if [ ! -d "$HARNESS/.git" ]; then
  git clone https://github.com/poseidon-research/collusion_hackathon.git "$HARNESS"
  git -C "$HARNESS" checkout -q "$PIN"
  git -C "$HARNESS" apply "$ROOT/experiments/patches/collusion_hackathon_local_changes.patch"
  echo "Cloned Poseidon starter at $PIN and applied our patch."
else
  echo "Harness already at $HARNESS (left as is)."
fi

( cd "$HARNESS" && ./setup.sh )

ENV="$HARNESS/compute.env"
if [ ! -f "$ENV" ]; then
  cp "$HARNESS/compute.env.example" "$ENV" 2>/dev/null || touch "$ENV"
  {
    echo "LLM_BASE_URL=http://127.0.0.1:8787/v1"
    echo "LLM_API_KEY=subscription-proxy"
  } >> "$ENV"
  echo "Wrote $ENV pointing at the local subscription proxy. Add OPENROUTER_API_KEY there only if you want OpenRouter."
fi

echo; echo "CLI check (each needs to be signed in on this machine):"
for c in claude codex agy grok; do
  if command -v "$c" >/dev/null; then echo "  $c: $($c --version 2>&1 | head -n1)"; else echo "  $c: not installed"; fi
done
echo; echo "Next: ./scripts/start_proxy.sh   then   ./scripts/run_sweep.sh"
