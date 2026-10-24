# Apart Research AI Collusion Research Sprint 2026

Private working repo for the Apart Research AI Collusion Research Sprint.
The sprint runs Friday Oct 23 to Sunday Oct 25, 2026. It is online.
Sprint page: https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25

## Start here

| To | Open |
| --- | --- |
| See everything visually: replays of every run, hover explanations, right-click "Ask Opus" | `python3 dashboard/serve.py`, then http://127.0.0.1:8788/ (or open `dashboard/index.html`) |
| Read every run: each round's moves, the agents' message board, their private plans and thoughts | [`experiments/cases/README.md`](experiments/cases/README.md) |
| Run your own agents and add new cases | [`experiments/README.md`](experiments/README.md) |
| Set up a new machine | "Run on another machine" below |
| See Daniel's plan and our shared task list | [`notes/collab_daniel/PLAN_AND_TASKS.md`](notes/collab_daniel/PLAN_AND_TASKS.md) |
| See every remaining run, which machine runs it, and how to start it | [`notes/RUN_PLAN.md`](notes/RUN_PLAN.md) |
| Read how the agents behave by model, role and team | [`docs/AGENT_BEHAVIOR.md`](docs/AGENT_BEHAVIOR.md) |

## Project

Do LLM agents collude when they set prices, and does it depend on who is on the team? Two starter markets from
Poseidon: a continuous double auction (sellers can get a message board, CEO pressure, an overseer) and a repeated
Bertrand price game (no talking). We vary the model, the prompt, and the team mix (same-family teams, one odd model
in a team of two, fully mixed teams). A Fable 5.1 image-steganography replication lives in `src/fable_image_stego/`.

## Observations so far (one run per setting: leads, not results)

Numbers come from [`experiments/cases/README.md`](experiments/cases/README.md); seeds and repeats are still to do.

- **Bertrand, plain profit prompt (P0), same model on both sides:** Claude Sonnet 4.6 reached a collusion gain of
  +0.96 (mean price $1.91 against a monopoly price of $1.92) without being told to collude. Claude Haiku 4.5 +0.80,
  Gemini 3.8 Flash +0.65, GPT-6 Luna +0.01.
- **Bertrand, mixed pairs (P0):** every cross-family pair stayed near competition (+0.04 to +0.12). Against Luna,
  Haiku priced $1.81 while Luna stayed at $1.57.
- **Bertrand, told to collude (PC):** GPT-6 Luna with think mode refused ("I can't coordinate prices with a
  competitor", gain +0.07). Claude Sonnet 4.6 overshot to $2.83 and earned less than competing (gain -1.26).
- **Double auction, chat + boss, scripted buyers:** GPT-6 Luna sellers held a $97.60 price wall (ask index +0.76,
  0 trades) and Gemini 3.8 Flash $97.43 (+0.74). Claude Sonnet 4.6 (-0.50) and Claude Haiku 4.5 (-0.76) sellers undercut.
- **Double auction, mixed seller teams:** only teams without a Claude Haiku seller held a wall (Luna-Luna-Gemini +0.69,
  Gemini-Gemini-Luna +0.74). Every team with a Haiku seller stayed at or below +0.13; in the Gemini-Gemini-Haiku run
  the Haiku seller broke from the Gemini sellers' $97.50 proposal in round 1.
- **Caveat on buyers:** the starter repo's scripted ZIP buyers never raise their bid (learning loop commented out),
  so with them a trade happens only when a seller drops to about $80. With LLM buyers, trades clear at $85.75 to $86.16.

## Team

Mert Senkardesler (solo for now).

## Preexisting vs new work

Preexisting code we use but did not write:
- `poseidon-research/collusion_hackathon` starter harnesses (llm-cartel, llm-agent-collusion, and others). Cloned at commit `d585a7b`. Our small local edits are in `experiments/patches/collusion_hackathon_local_changes.patch`.
- The papers behind those harnesses (see notes/resources.md).

New for the sprint: `src/subscription_proxy/` (OpenAI compatible proxy over the claude, codex, agy and grok CLIs), `scripts/`, `dashboard/`, `experiments/` run configs and results, notes, and the report.
If any code written before the sprint is added later, it must be marked as preexisting here and in the report. The sprint rules say undisclosed prior work can lead to disqualification.

## Key deadlines (all times CT, America/Chicago)

| When (CT) | What |
| --- | --- |
| Fri Oct 23 | Sprint starts. |
| Mon Oct 26, 6:59 AM | Submissions close. This is Sun Oct 25, 11:59 PM AoE. |

See STATUS.md for open tasks and talks/SCHEDULE.md for talks.

## Layout

| Path | Contents |
| --- | --- |
| STATUS.md | Open tasks and submission rules. |
| notes/sprint_overview.md | Faithful notes from the sprint Overview tab. |
| notes/resources.md | Every listed paper and starter repo, with URLs. |
| notes/schedule.md | Sprint Schedule tab, times in CT. |
| notes/daily_log.md | Daily log. |
| notes/talk_notes.md | Index of talk notes. |
| notes/reading_notes.md | Notes on papers read. |
| talks/ | One folder per talk, plus talks/SCHEDULE.md. |
| papers/ | PDFs and paper notes. |
| src/ | Code. Includes src/fable_image_stego/ for the Fable 5.1 image steganography replication harness. |
| archive/ | Archived posts, threads, and external repositories. |
| report/ | Report drafts. report/TEMPLATE.md has the template link and requirements. |
| dashboard/ | Interactive agent monitor: `serve.py` (scanner, server, `/api/ask`) and `index.html`. See dashboard/README.md. |
| experiments/ | Every run: `cases/` (readable round-by-round records), `snapshot/` (raw run files), batch scripts, harness patch. See experiments/README.md. |
| scripts/ | Machine setup, proxy start, model sweep, token logging. |
| src/subscription_proxy/ | OpenAI-compatible proxy that routes the harnesses' model calls to the signed-in claude, codex, agy and grok CLIs. |
| token-usage/ | Proxy call log (served model per call) and token ledger. |

## Project ideas
See notes/ideas/project_ideas.md.

## Poseidon hackathon starter code archive

`archive/poseidon_collusion_hackathon_code/` holds a snapshot of the code folders from `poseidon-research/collusion_hackathon`: `util/`, `setup.sh`, `algorithmic-pricing-llms/`, `collusive-llm-agents/`, `colosseum/`, `focal-points/`, `llm-agent-collusion/`, `llm-agent-collusion-2/`, `llm-cartel/`, `llm-trust-breaking/`, `steganographic-collusion/`, and `trace-guard/`. Virtual environments, caches, `.git`, model weights, and files of 50 MB or more are excluded. Docs, literature, and the redteaming harness live in `archive/poseidon_collusion_hackathon_docs/`.

This archive is for reference only. To run experiments, follow "Run on another machine" below.

## Run on another machine

Needs git, python3, [uv](https://docs.astral.sh/uv/), and at least one signed in CLI among `claude`, `codex`, `agy`, `grok`. No API keys are needed for those.

```bash
git clone https://github.com/BARDAK1995/apart-collusion-sprint-2026.git
cd apart-collusion-sprint-2026
./scripts/setup_other_machine.sh   # clones the Poseidon harness into ./collusion_hackathon at d585a7b, applies our patch, installs envs, writes compute.env
./scripts/start_proxy.sh           # proxy on http://127.0.0.1:8787/v1
./scripts/run_all.sh run --shard local   # this machine's share of every remaining run (see notes/RUN_PLAN.md)
./scripts/run_all.sh merge               # pull both machines' runs, rebuild cases and docs/AGENT_BEHAVIOR.md, push
```

`scripts/run_all.sh` replaces running `run_sweep.sh` and `run_matrix.sh` by hand. The older scripts still work.

Sweep order: claude-haiku-5-5, claude-sonnet-5-5, claude-opus-5-5, gpt-6-luna, gpt-5.6-sol, gemini-3.8-flash-low, then grok-4.5, grok-4.6, grok-4.7-build-fast, and grok-4.7 last because it is slow. Pick a subset with `MODELS="grok-4.6 grok-4.7" ./scripts/run_sweep.sh`. Results land in the harness and are copied into `experiments/snapshot/` by `experiments/sync_runs.py`. Commit and push them from that machine.

Token and cost log: after running the shared token logger, `python3 scripts/snapshot_usage.py` writes an anonymised snapshot (`token-usage/usage_snapshot.json`), appends `token-usage/USAGE_LOG.md` (tables and figures), and feeds the dashboard's "Tokens and cost" tab.

Token tracking: the proxy logs every call to `token-usage/proxy_usage.jsonl` (estimated tokens, chars over 4). `GET http://127.0.0.1:8787/v1/usage` shows totals by model. `scripts/log_tokens.sh` also runs the Claude usage ledger if `~/.claude/scripts/usage-ledger/` exists.

Note: runs made before Oct 23 evening that say Haiku used `claude-haiku-4-5`, because the starter upgraded the retired 3.5 Haiku alias to 4.5. All Claude aliases now resolve to the 5.5 models.

## Sharing this folder or merging it into another repo

Everything here uses paths relative to this folder, so it can live as a subfolder of another repository.
Copy the tracked files without our git history. Leave out `archive/` (573 MB of reference copies of the Poseidon
starter code, which `scripts/setup_other_machine.sh` clones fresh anyway): the rest is about 28 MB.

```bash
git archive HEAD -- . ':!archive' | tar -x -C /path/to/their-repo/<new-folder>
```

The harness clone (`collusion_hackathon/`), run logs, and dashboard state files are git-ignored and rebuilt by the
scripts. After copying, run `scripts/setup_other_machine.sh` inside the new folder.
