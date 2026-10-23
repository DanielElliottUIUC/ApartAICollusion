# Local CLI Subscription Proxy (`http://127.0.0.1:8787/v1`)

An OpenAI-compatible HTTP proxy server that routes `/v1/chat/completions`, `/v1/responses`, and `/v1/models` to our signed-in local CLI subscriptions on the box at **$0 API cost**:

| CLI Binary | Auth Status | Native Models | Typical Latency (1-turn) |
|---|---|---|---|
| `/home/box/.local/bin/claude` | Signed in | `claude-sonnet-4-6`, `claude-haiku-4-5`, `claude-fable-5-1` | **1.6s – 2.3s** |
| `/home/box/.local/bin/codex` | Signed in (ChatGPT account) | `gpt-6-luna`, `gpt-5.6-luna`, `gpt-5.6-terra`, `gpt-5.6-sol`, `gpt-6-sol`, `gpt-6.1-sol`, `gpt-6-astra`, `gpt-reserve` | **2.3s – 3.5s** |
| `/home/box/.local/bin/agy` | Signed in | `gemini-3.8-flash-low`, `gemini-4-argon-low`, `claude-sonnet-5-5-low`, `claude-opus-5-5-low`, `gpt-oss-120b-medium` | **4.3s – 5.5s** |
| `/home/box/.local/bin/grok` | Not signed in (`grok login --device-code` needed) | `grok-4.6`, `grok-4.5` | — |

## Key Optimizations
- **Codex (`codex exec`)**: Runs from an empty `/tmp/subproxy_empty` working directory with `--skip-git-repo-check --ephemeral --ignore-user-config --ignore-rules`, disables all plugins/MCP/shell/memory tools (`--disable plugins --disable apps --disable shell_tool --disable shell_snapshot --disable memories --disable multi_agent -c mcp_servers={}`), sets `-c model_reasoning_effort="low"`, and injects the simulation's system prompt via `-c model_instructions_file=...`.
  - Note: ChatGPT-account Codex auth does not serve legacy API names `gpt-5.4-mini` or `gpt-5.4` directly; the proxy automatically maps `gpt-5.4-mini` / `gpt-4.1-mini` / `gpt-4o-mini` -> `gpt-6-luna` (~2.3s) and `gpt-5.4` / `gpt-4.1` -> `gpt-5.6-sol` (~3.0s).
- **Claude (`claude -p`)**: Runs with `CLAUDECODE` unset and `--no-session-persistence --disable-slash-commands --setting-sources "" --strict-mcp-config --effort low --tools "" --system-prompt ...`, cutting per-call latency from ~6.6s down to **1.6s – 2.2s** and replacing the Claude Code coding assistant prompt with the marketplace simulation prompt.
- **JSON Mode (`response_format={"type": "json_object"}`)**: Automatically instructs the CLI to emit raw JSON and strips any markdown fences before returning `choices[0].message.content`.

## Starting / Checking the Server

```bash
# Start in background (already running on 127.0.0.1:8787)
nohup python3 /workspace/apart-collusion-sprint-2026/src/subscription_proxy/server.py > /tmp/subscription_proxy.log 2>&1 &

# Health / models check
curl -s http://127.0.0.1:8787/v1/models | jq .
```

## Configured Integration with `/workspace/collusion_hackathon`
`/workspace/collusion_hackathon/compute.env` is configured with:
```env
LLM_BASE_URL=http://127.0.0.1:8787/v1
LLM_API_KEY=subscription-proxy
```

### Ready-to-Run Marketplace Commands

#### 1. Bertrand Pricing Marketplace (`llm-cartel`)
```bash
cd /workspace/collusion_hackathon/llm-cartel

# Tacit collusion (P0) with Claude Sonnet 4.6 (achieves +0.964 monopoly gain!)
uv run python run_game.py --models claude-sonnet-4-6 --prefix P0 --rounds 15 --overwrite -y

# Explicit collusion (PC) with chain-of-thought (--think)
uv run python run_game.py --models claude-sonnet-4-6 --prefix PC --think --rounds 15 --overwrite -y

# Codex (gpt-5.4-mini -> gpt-6-luna)
uv run python run_game.py --models gpt-5.4-mini --prefix PC --think --rounds 15 --overwrite -y
```

#### 2. Continuous Double Auction Marketplace (`llm-agent-collusion`)
```bash
cd /workspace/collusion_hackathon/llm-agent-collusion

# Codex sellers communicating under CEO boss pressure (passes coordinated-pricing control at +0.76 ask index!)
uv run python src/continuous_double_auction/simulation.py \
  --seller_models gpt-5.4-mini --buyer_models zip \
  --seller_comms_enabled --boss_pressure --rounds 10 -y

# Cross-model marketplace: Claude sellers vs Codex LLM buyers
uv run python src/continuous_double_auction/simulation.py \
  --seller_models claude-sonnet-4-6 --buyer_models gpt-5.4-mini \
  --seller_comms_enabled --boss_pressure --rounds 10 -y
```
