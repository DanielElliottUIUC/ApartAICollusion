#!/usr/bin/env bash
# Start the OpenAI-compatible subscription proxy on http://127.0.0.1:8787/v1 (background).
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${TMPDIR:-/tmp}/subscription_proxy.log"
pkill -f "src/subscription_proxy/server.py" 2>/dev/null || true
nohup python3 "$ROOT/src/subscription_proxy/server.py" > "$LOG" 2>&1 &
sleep 2
curl -s http://127.0.0.1:8787/v1/models >/dev/null && echo "Proxy up on :8787 (log $LOG)" || { echo "Proxy failed, see $LOG"; exit 1; }
