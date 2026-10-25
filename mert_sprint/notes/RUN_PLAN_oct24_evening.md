# Run plan, Sat Oct 24 evening (from 6 PM CT)

Owner decision at 5:56 PM CT: the remaining runs are split over three machines.
Rules in [AGENTS.md](../AGENTS.md) still apply. The split is pinned in `notes/shard_assignment.json`.
Runs that the owner rules forbid are listed there under `parked` and never start.
Do not run `scripts/run_all.sh assign`, because it would undo this split.

See each shard's list with `bash scripts/run_all.sh plan --shard k/3`.

## Who runs what

| Shard | Machine | Runs | Models |
|---|---|---|---|
| 1 (`box`) | grokbot computer, tmux `frontier` | 18 frontier runs with messaging on, plus the 6 Grok runs with messaging off (24) | grok-4.7, gpt-6-luna, gpt-5.6-sol sellers; Haiku 5.5 or Luna buyers |
| 2 (`shard2`) | MS home server (Windows) | 12 frontier runs with messaging off, Luna and Sol sellers only | gpt-6-luna, gpt-5.6-sol sellers; Haiku 5.5 or Luna buyers |
| 3 (`shard3`) | Mert's Mac | 27 Gemini runs, Gemini served by OpenRouter | google/gemini-3.8-flash, gpt-6-luna; Haiku 5.5 buyers in Daniel's runs |

The 6 Grok runs with messaging off stay on the box. No log or note shows a grok CLI on the MS home server.
At most 2 Grok runs go at once (`GROK_MAX=2`).

### Shard 2 tags (12)

`frontierA_<seller>_nocomms_<buyer>-seed<k>` with seller `gpt6luna` or `gpt56sol`, buyer `haikuB` or `lunaB`, seed 0, 1, 2.

### Shard 3 tags (27)

- Daniel step A, v2 market, Haiku 5.5 buyers: `danielA_gemini_comms-seed0`, `-seed1`, `-seed2`; `danielA_gemini_nocomms-seed0`, `-seed2` (seed 1 is done); `danielA_gemini_notice-seed0`, `-seed1`, `-seed2`.
- Daniel step B: `danielB_GGGG-seed0`, `-seed1`, `-seed2`.
- Our matrix, 3 sellers, ZIP buyers: `het55_GGG_s0..s2`, `het55_OOG_s0..s2`, `het55_GGO_s0..s2`.
- Our Bertrand pairs: `het55_P0_GG_s0..s2`, `het55_P0_OG_s0..s2`.
- Sweep: `sweep_gemini-3_8-flash-low_P0`.

Every Gemini id, including `gemini-3.8-flash-low`, is served as `google/gemini-3.8-flash` with its default thinking.
Note that in the report for the `het55` and sweep runs, which earlier used the low effort setting through agy.

Rough cost: about $1 per Daniel run (his buyer probe cost about $7 for 8 runs), so about $11 for the 11 Daniel runs,
plus a few dollars for the small runs. $10 may not cover everything; $15 is safer.
The runner starts the longest runs first, so the Daniel runs go before the small ones.

## Shard 2: MS home server (Windows)

1. `git pull`.
2. Do the Windows codex check in AGENTS.md first (the "17 + 25 = 42" test). Start the proxy with the codex binary folder first on PATH.
3. `bash scripts/run_all.sh plan --shard 2/3` must list 12 ready `frontierA_*_nocomms_*` runs with `gpt6luna` or `gpt56sol`.
4. `bash scripts/run_all.sh run --shard 2/3 --phases frontier --jobs 3`
   The runner first sends one call per model (Haiku 5.5, Luna, Sol) and stops if any fails.
5. Outputs go to `experiments/runs/shard2/frontier/` and logs to `experiments/runs/shard2/logs/`.
   The runner commits them with `git add -f` and pushes when the phase ends. If that push fails, run
   `git add -f experiments/runs/shard2 token-usage/proxy_usage.shard2.jsonl`, commit and push by hand.

## Shard 3: Mert's Mac (Gemini through OpenRouter)

The Mac has no OpenRouter key yet, and the OpenRouter account has $0 credit right now. Before anything runs:

1. Mert adds about $10 to $15 at https://openrouter.ai/settings/credits.
2. Mert puts `OPENROUTER_API_KEY=...` in the Mac's local `collusion_hackathon/compute.env`. That folder is gitignored. Never commit the key and never print it.

Then the agent (the Mac also needs the codex CLI for Luna and the claude CLI for the Haiku buyers, both signed in):

1. `git pull`. If `collusion_hackathon/` is missing or its venv is broken, run `./scripts/setup_other_machine.sh` first.
2. Start the proxy with Gemini routed to OpenRouter:
   `set -a; . collusion_hackathon/compute.env; set +a; export PROXY_GEMINI_VIA_OPENROUTER=1 PROXY_USAGE_LOG=token-usage/proxy_usage.shard3.jsonl; bash scripts/start_proxy.sh`
3. Test one call and stop on any error:
   `curl -s http://127.0.0.1:8787/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"google/gemini-3.8-flash","messages":[{"role":"user","content":"Reply with exactly: OK"}]}'`
   If the reply says 402 or "Insufficient credits", stop and tell Mert. Do not retry in a loop.
4. `bash scripts/run_all.sh plan --shard 3/3` must list 27 ready runs.
5. `PROXY_GEMINI_VIA_OPENROUTER=1 RESTART_PROXY=1 bash scripts/run_all.sh run --shard 3/3 --jobs 3`
   The runner checks one call per model first and stops on a 402. New OpenRouter accounts allow about 20 Gemini calls per minute, so keep `--jobs 3` or lower.
6. Outputs go to `experiments/runs/shard3/` and the runner pushes them when each phase ends. If a push fails, run
   `git add -f experiments/runs/shard3 token-usage/proxy_usage.shard3.jsonl`, commit and push by hand.
7. If credit runs out midway, runs fail with 402. Stop, tell Mert, and push what finished.

## Shard 1: box

The box keeps running in tmux `frontier`:
`bash scripts/run_all.sh run --shard 1/3 --phases frontier --jobs 4` with `GROK_MAX=2`.
At 5:58 PM CT the first runner was stopped between launches, with its 4 runs left going. The new runner counts runs
already going on the machine toward `--jobs` and `GROK_MAX`, skips tags that are running or done, and runs only shard 1 tags.

A Ctrl C sent into that tmux pane at 5:59 PM CT also stopped 3 box runs before they finished
(`frontierA_gpt56sol_comms_haikuB-seed2`, `frontierA_gpt56sol_comms_lunaB-seed2`, `frontierA_grok47_comms_haikuB-seed1`;
the first try of `frontierA_grok47_comms_haikuB-seed0` too). Their partial folders were moved off the repo, and all of them run again on the box.
Stop a runner with `kill <pid of run_all.py>`, never with Ctrl C in its pane, so its runs keep going.

When all three shards are done, any machine runs `bash scripts/run_all.sh merge`.
