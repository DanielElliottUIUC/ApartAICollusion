# Run plan: every remaining run, split across 3 machines

Written Sat Oct 24, 2026, about 9:50 AM CT. Goal: finish in about 3 hours on the box plus Mert's machines m1 and m2.
The split is pinned in `notes/shard_assignment.json` (committed), so every machine agrees on who runs what.
Rerun `scripts/run_all.sh plan` for live progress per shard. It reads the run folders after a `git pull`.

## Who runs what

| Shard | Machine | Folder | Runs left | Phases | Models | CLIs that must be signed in | Est. wall time |
|---|---|---|---|---|---|---|---|
| 1/3 | Grok Bot box | `experiments/runs/box/` (plus old `local/`) | 29 (5 were already running at the switch) | Grok sweep (11), Daniel A GPT-4.1 arms (6), Daniel B DeepSeek mixes (6), Fable full in 6 parts (6) | grok-4.5, grok-4.6, grok-4.7-build-fast, grok-4.7, openai/gpt-4.1, deepseek v4.1 flash, Gemini 3.8 Flash, Haiku 5.5, Fable 5.1 | claude, agy, grok, plus OpenRouter key | about 2 h at `--jobs 6` |
| 2/3 | m1 | `experiments/runs/shard2/` | 39 | refusal (1), matrix (26), Daniel A (7), Daniel B (5) | claude-haiku-5-5, claude-haiku-4-5, gpt-6-luna, gemini-3.8-flash-low (Daniel's names map to the same) | claude, codex, agy | about 1.4 h at `--jobs 3` |
| 3/3 | m2 | `experiments/runs/shard3/` | 39 | sweep Gemini P0 retry (1), refusal (1), matrix (25), Daniel A (8), Daniel B (4) | same as m1 | claude, codex, agy | about 1.4 h at `--jobs 3` |

Pinned to the box: runs already done or running there, every OpenRouter run (only the box has a key; this also
covers Daniel's judge), every Fable run, and every Grok run (so m1 and m2 do not need the grok CLI, and Grok calls,
which already time out at 120 s under load, are not tripled). The rest is split longest first by estimated
minutes divided by each shard's `--jobs`.

The estimates use mean call latencies measured on the box this morning. Daniel's v2 market has no finished run yet,
so its estimate (about 20 min per run) is a guess. If it runs 2x slower, m1 and m2 still finish in about 3 h.

## Commands

**m1** (shard 2):

```bash
git clone https://github.com/BARDAK1995/apart-collusion-sprint-2026.git 2>/dev/null || true
cd apart-collusion-sprint-2026 && git pull --rebase --autostash
[ -d collusion_hackathon ] || ./scripts/setup_other_machine.sh
tmux new -d -s shard2 'scripts/run_all.sh run --shard 2/3 --jobs 3 2>&1 | tee -a run_all_shard2.out'
```

**m2** (shard 3): the same, with `3/3`, session `shard3` and `run_all_shard3.out`.

```bash
git clone https://github.com/BARDAK1995/apart-collusion-sprint-2026.git 2>/dev/null || true
cd apart-collusion-sprint-2026 && git pull --rebase --autostash
[ -d collusion_hackathon ] || ./scripts/setup_other_machine.sh
tmux new -d -s shard3 'scripts/run_all.sh run --shard 3/3 --jobs 3 2>&1 | tee -a run_all_shard3.out'
```

**Box** (shard 1, already running in tmux session `shard1`, log `/tmp/run_all_shard1.out`):

```bash
scripts/run_all.sh run --shard 1/3 --jobs 6 --no-smoke
```

Check progress anywhere: `git pull && scripts/run_all.sh plan --shard 2/3` (or no `--shard` for all three).
When all shards finish, on any machine: `scripts/run_all.sh merge`.

Before starting m1 or m2, run `claude`, `codex` and `agy` once by hand and make sure each is signed in. A clone of
the private repo needs GitHub access on that machine. `uv` must be installed. `run_all.sh` clones Daniel's repo
next to ours at commit `788092c` (the one the box uses) if it is missing.

## What `run --shard k/3` does

1. `git pull --rebase --autostash`, then reads `notes/shard_assignment.json`. It stops if the file is for a different N.
2. Starts the subscription proxy if it is not running with strict routing and this shard's usage log
   (`token-usage/proxy_usage.shard<k>.jsonl`; the box keeps `proxy_usage.box.jsonl`).
3. Smoke check: one short call to every model the shard needs, and a check that the harness folders exist.
   If any fails, it prints which CLI to sign in to and exits with code 2. Nothing runs.
4. Runs the shard's runs, `--jobs` at a time, longest first, in one pool (no idle time between phases).
   It skips a run whose finished output exists in any shard folder, a run with a live process on this machine,
   and a run that already failed twice. Refusals count as outcomes.
5. When the last run of a phase finishes, it commits only this shard's folder and usage log, then pulls with
   rebase and pushes, up to 5 tries. It pushes once more at the end.
6. Stop with `tmux kill-session -t shard<k>`. Starting again resumes. A run killed midway has no finished output,
   so it is not counted as done and runs again.

## Rate limits

All machines share the same claude, codex, agy and grok subscriptions. Up to about 12 runs will call them at once.
As of 9:45 AM CT there is no 429 or rate limit message in `/tmp/subscription_proxy.log` or in any run log.
The only errors are 4 Grok calls that timed out at 120 s (grok-4.5 three times, grok-4.6 once), and one Gemini
Bertrand run that got an empty reply 4 times in a row (`sweep_gemini-3_8-flash-low_P0`, now on m2 for a retry).
If 429s appear, restart that shard with `--jobs 2`.

## Changes from the two machine plan

- `--shard box` and `--shard local` are replaced by `--shard k/N`. `box` still means shard 1. `local` exits with a message.
- The Fable pilot is dropped. The full run (30 messages + 30 controls, about 6 h in one process) is split by item id
  into 6 parts of 5 messages and 5 controls, about 1 h each. The parts include the pilot's items.
- Run estimates now use this morning's measured latencies instead of Oct 23 values times 1.5.
- B still runs even though Daniel gates B on A passing. Read B only after A passes.

## Still blocked

- Step C (36 runs) needs Daniel's label code. Steps D to G (45 runs) need the undercover seat, report tool, persona,
  warning and precedent texts.
- The proxy drops temperature and seed for CLI models, so seeds change agent names and order but not sampling.

## Full run table

Status as of the switch to 3 shards. Shard 0 or n/a means blocked.

| Phase | Case | Models | Seeds | Runs | Est. calls | Est. min | Shard | Status |
|---|---|---|---|---|---|---|---|---|
| sweep | `sweep_claude-haiku-5-5_P0` | claude-haiku-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-haiku-5-5_PC` | claude-haiku-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-haiku-5-5_PC_think` | claude-haiku-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-haiku-5-5_comms_boss` | claude-haiku-5-5 | 0 | 1 | 30 | 1 | 1 | done |
| sweep | `sweep_claude-sonnet-5-5_P0` | claude-sonnet-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-sonnet-5-5_PC` | claude-sonnet-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-sonnet-5-5_PC_think` | claude-sonnet-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-sonnet-5-5_comms_boss` | claude-sonnet-5-5 | 0 | 1 | 30 | 1 | 1 | done |
| sweep | `sweep_claude-opus-5-5_P0` | claude-opus-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-opus-5-5_PC` | claude-opus-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-opus-5-5_PC_think` | claude-opus-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_claude-opus-5-5_comms_boss` | claude-opus-5-5 | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_gpt-6-luna_P0` | gpt-6-luna | 0 | 1 | 30 | 1 | 1 | done |
| sweep | `sweep_gpt-6-luna_PC` | gpt-6-luna | 0 | 1 | 30 | 1 | 1 | done |
| sweep | `sweep_gpt-6-luna_PC_think` | gpt-6-luna | 0 | 1 | 30 | 1 | 1 | done |
| sweep | `sweep_gpt-6-luna_comms_boss` | gpt-6-luna | 0 | 1 | 30 | 1 | 1 | done |
| sweep | `sweep_gpt-5_6-sol_P0` | gpt-5.6-sol | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_gpt-5_6-sol_PC` | gpt-5.6-sol | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_gpt-5_6-sol_PC_think` | gpt-5.6-sol | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_gpt-5_6-sol_comms_boss` | gpt-5.6-sol | 0 | 1 | 30 | 2 | 1 | done |
| sweep | `sweep_gemini-3_8-flash-low_P0` | gemini-3.8-flash-low | 0 | 1 | 30 | 3 | 3 | ready |
| sweep | `sweep_gemini-3_8-flash-low_PC` | gemini-3.8-flash-low | 0 | 1 | 30 | 3 | 1 | done |
| sweep | `sweep_gemini-3_8-flash-low_PC_think` | gemini-3.8-flash-low | 0 | 1 | 30 | 3 | 1 | done |
| sweep | `sweep_gemini-3_8-flash-low_comms_boss` | gemini-3.8-flash-low | 0 | 1 | 30 | 3 | 1 | done |
| sweep | `sweep_grok-4_5_P0` | grok-4.5 | 0 | 1 | 30 | 15 | 1 | ready |
| sweep | `sweep_grok-4_5_PC` | grok-4.5 | 0 | 1 | 30 | 15 | 1 | ready |
| sweep | `sweep_grok-4_5_PC_think` | grok-4.5 | 0 | 1 | 30 | 15 | 1 | ready |
| sweep | `sweep_grok-4_5_comms_boss` | grok-4.5 | 0 | 1 | 30 | 14 | 1 | done |
| sweep | `sweep_grok-4_6_P0` | grok-4.6 | 0 | 1 | 30 | 13 | 1 | done |
| sweep | `sweep_grok-4_6_PC` | grok-4.6 | 0 | 1 | 30 | 13 | 1 | ready |
| sweep | `sweep_grok-4_6_PC_think` | grok-4.6 | 0 | 1 | 30 | 13 | 1 | done |
| sweep | `sweep_grok-4_6_comms_boss` | grok-4.6 | 0 | 1 | 30 | 11 | 1 | done |
| sweep | `sweep_grok-4_7-build-fast_P0` | grok-4.7-build-fast | 0 | 1 | 30 | 22 | 1 | ready |
| sweep | `sweep_grok-4_7-build-fast_PC` | grok-4.7-build-fast | 0 | 1 | 30 | 22 | 1 | ready |
| sweep | `sweep_grok-4_7-build-fast_PC_think` | grok-4.7-build-fast | 0 | 1 | 30 | 22 | 1 | ready |
| sweep | `sweep_grok-4_7-build-fast_comms_boss` | grok-4.7-build-fast | 0 | 1 | 30 | 20 | 1 | ready |
| sweep | `sweep_grok-4_7_P0` | grok-4.7 | 0 | 1 | 30 | 5 | 1 | ready |
| sweep | `sweep_grok-4_7_PC` | grok-4.7 | 0 | 1 | 30 | 5 | 1 | done |
| sweep | `sweep_grok-4_7_PC_think` | grok-4.7 | 0 | 1 | 30 | 5 | 1 | ready |
| sweep | `sweep_grok-4_7_comms_boss` | grok-4.7 | 0 | 1 | 30 | 5 | 1 | ready |
| refusal | `refusal_claude-haiku-4-5_PC` | claude-haiku-4-5 | 0 | 1 | 30 | 8 | 3 | ready (Oct 23 run aborted after 4 attempts; this keeps the log) |
| refusal | `refusal_claude-haiku-4-5_PC_think` | claude-haiku-4-5 | 0 | 1 | 30 | 8 | 2 | ready |
| matrix | `het55_CCC` | claude-haiku-5-5 | 0, 2 | 2 | 48 | 2 | 2 | ready |
| matrix | `het55_CCC` | claude-haiku-5-5 | 1 | 1 | 24 | 1 | 3 | ready |
| matrix | `het55_OOO` | gpt-6-luna | 0, 2 | 2 | 48 | 1 | 2 | ready |
| matrix | `het55_OOO` | gpt-6-luna | 1 | 1 | 24 | 1 | 3 | ready |
| matrix | `het55_GGG` | gemini-3.8-flash-low | 0, 1 | 2 | 48 | 5 | 2 | ready |
| matrix | `het55_GGG` | gemini-3.8-flash-low | 2 | 1 | 24 | 2 | 3 | ready |
| matrix | `het55_CCO` | claude-haiku-5-5, gpt-6-luna | 0, 2 | 2 | 48 | 2 | 2 | ready |
| matrix | `het55_CCO` | claude-haiku-5-5, gpt-6-luna | 1 | 1 | 24 | 1 | 3 | ready |
| matrix | `het55_CCG` | claude-haiku-5-5, gemini-3.8-flash-low | 0, 2 | 2 | 48 | 3 | 2 | ready |
| matrix | `het55_CCG` | claude-haiku-5-5, gemini-3.8-flash-low | 1 | 1 | 24 | 2 | 3 | ready |
| matrix | `het55_OOC` | claude-haiku-5-5, gpt-6-luna | 0, 2 | 2 | 48 | 2 | 3 | ready |
| matrix | `het55_OOC` | claude-haiku-5-5, gpt-6-luna | 1 | 1 | 24 | 1 | 2 | ready |
| matrix | `het55_OOG` | gemini-3.8-flash-low, gpt-6-luna | 0, 2 | 2 | 48 | 3 | 3 | ready |
| matrix | `het55_OOG` | gemini-3.8-flash-low, gpt-6-luna | 1 | 1 | 24 | 1 | 2 | ready |
| matrix | `het55_GGC` | claude-haiku-5-5, gemini-3.8-flash-low | 0, 2 | 2 | 48 | 4 | 2 | ready |
| matrix | `het55_GGC` | claude-haiku-5-5, gemini-3.8-flash-low | 1 | 1 | 24 | 2 | 3 | ready |
| matrix | `het55_GGO` | gemini-3.8-flash-low, gpt-6-luna | 0, 2 | 2 | 48 | 4 | 3 | ready |
| matrix | `het55_GGO` | gemini-3.8-flash-low, gpt-6-luna | 1 | 1 | 24 | 2 | 2 | ready |
| matrix | `het55_COG` | claude-haiku-5-5, gemini-3.8-flash-low, gpt-6-luna | 0, 2 | 2 | 48 | 3 | 3 | ready |
| matrix | `het55_COG` | claude-haiku-5-5, gemini-3.8-flash-low, gpt-6-luna | 1 | 1 | 24 | 1 | 2 | ready |
| matrix | `het55_OGC` | claude-haiku-5-5, gemini-3.8-flash-low, gpt-6-luna | 0, 2 | 2 | 48 | 3 | 2 | ready |
| matrix | `het55_OGC` | claude-haiku-5-5, gemini-3.8-flash-low, gpt-6-luna | 1 | 1 | 24 | 1 | 3 | ready |
| matrix | `het55_P0_CO` | claude-haiku-5-5, gpt-6-luna | 0, 2 | 2 | 60 | 3 | 3 | ready |
| matrix | `het55_P0_CO` | claude-haiku-5-5, gpt-6-luna | 1 | 1 | 30 | 2 | 2 | ready |
| matrix | `het55_P0_CG` | claude-haiku-5-5, gemini-3.8-flash-low | 0, 1 | 2 | 60 | 7 | 3 | ready |
| matrix | `het55_P0_CG` | claude-haiku-5-5, gemini-3.8-flash-low | 2 | 1 | 30 | 3 | 2 | ready |
| matrix | `het55_P0_OG` | gemini-3.8-flash-low, gpt-6-luna | 0, 2 | 2 | 60 | 7 | 2 | ready |
| matrix | `het55_P0_OG` | gemini-3.8-flash-low, gpt-6-luna | 1 | 1 | 30 | 3 | 3 | ready |
| matrix | `het55_P0_GG` | gemini-3.8-flash-low | 0, 2 | 2 | 60 | 7 | 3 | ready |
| matrix | `het55_P0_GG` | gemini-3.8-flash-low | 1 | 1 | 30 | 3 | 2 | ready |
| matrix | `het55_P0_CC` | claude-haiku-5-5 | 0, 2 | 2 | 60 | 3 | 2 | ready |
| matrix | `het55_P0_CC` | claude-haiku-5-5 | 1 | 1 | 30 | 2 | 3 | ready |
| matrix | `het55_P0_OO` | gpt-6-luna | 0, 2 | 2 | 60 | 2 | 3 | ready |
| matrix | `het55_P0_OO` | gpt-6-luna | 1 | 1 | 30 | 1 | 2 | ready |
| A | `danielA_gemini_comms` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 0, 2 | 2 | 240 | 39 | 2 | ready |
| A | `danielA_gemini_comms` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 1 | 1 | 120 | 20 | 3 | ready |
| A | `danielA_gemini_nocomms` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 0, 2 | 2 | 240 | 39 | 3 | ready |
| A | `danielA_gemini_nocomms` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 1 | 1 | 120 | 20 | 2 | ready |
| A | `danielA_gemini_notice` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 0, 2 | 2 | 240 | 39 | 2 | ready |
| A | `danielA_gemini_notice` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 1 | 1 | 120 | 20 | 3 | ready |
| A | `danielA_haiku_comms` | anthropic/claude-haiku-5.5 | 0, 1 | 2 | 240 | 25 | 3 | ready |
| A | `danielA_haiku_comms` | anthropic/claude-haiku-5.5 | 2 | 1 | 120 | 13 | 2 | ready |
| A | `danielA_haiku_nocomms` | anthropic/claude-haiku-5.5 | 0, 2 | 2 | 240 | 25 | 3 | ready |
| A | `danielA_haiku_nocomms` | anthropic/claude-haiku-5.5 | 1 | 1 | 120 | 13 | 2 | ready |
| A | `danielA_gpt41_comms` | anthropic/claude-haiku-5.5, openai/gpt-4.1 | 0, 1, 2 | 3 | 360 | 43 | 1 | ready (only needed if the Gemini arm fails the gate) |
| A | `danielA_gpt41_nocomms` | anthropic/claude-haiku-5.5, openai/gpt-4.1 | 0, 1, 2 | 3 | 360 | 43 | 1 | ready (only needed if the Gemini arm fails the gate) |
| B | `danielB_GGGG` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 0, 2 | 2 | 240 | 39 | 3 | ready (Daniel gates B on A passing) |
| B | `danielB_GGGG` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 1 | 1 | 120 | 20 | 2 | ready (Daniel gates B on A passing) |
| B | `danielB_GGCC` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 0, 2 | 2 | 240 | 32 | 2 | ready (Daniel gates B on A passing) |
| B | `danielB_GGCC` | anthropic/claude-haiku-5.5, google/gemini-3.8-flash | 1 | 1 | 120 | 16 | 3 | ready (Daniel gates B on A passing) |
| B | `danielB_GGDD` | anthropic/claude-haiku-5.5, deepseek/deepseek-v4.1-flash-1017, google/gemini-3.8-flash | 0, 1, 2 | 3 | 360 | 54 | 1 | ready (Daniel gates B on A passing) |
| B | `danielB_GCCD` | anthropic/claude-haiku-5.5, deepseek/deepseek-v4.1-flash-1017, google/gemini-3.8-flash | 0, 1, 2 | 3 | 360 | 46 | 1 | ready (Daniel gates B on A passing) |
| B | `danielB_CCCC` | anthropic/claude-haiku-5.5 | 0, 2 | 2 | 240 | 25 | 2 | ready (Daniel gates B on A passing) |
| B | `danielB_CCCC` | anthropic/claude-haiku-5.5 | 1 | 1 | 120 | 13 | 3 | ready (Daniel gates B on A passing) |
| fable | `fable_full_part1` | claude-fable-5-1 | 0 | 1 | 20 | 60 | 1 | ready (5 messages + 5 controls, about 3 min per encode or decode) |
| fable | `fable_full_part2` | claude-fable-5-1 | 0 | 1 | 20 | 60 | 1 | ready (5 messages + 5 controls, about 3 min per encode or decode) |
| fable | `fable_full_part3` | claude-fable-5-1 | 0 | 1 | 20 | 60 | 1 | ready (5 messages + 5 controls, about 3 min per encode or decode) |
| fable | `fable_full_part4` | claude-fable-5-1 | 0 | 1 | 20 | 60 | 1 | ready (5 messages + 5 controls, about 3 min per encode or decode) |
| fable | `fable_full_part5` | claude-fable-5-1 | 0 | 1 | 20 | 60 | 1 | ready (5 messages + 5 controls, about 3 min per encode or decode) |
| fable | `fable_full_part6` | claude-fable-5-1 | 0 | 1 | 20 | 60 | 1 | ready (5 messages + 5 controls, about 3 min per encode or decode) |
| C | `label x mix cells` | n/a | 0 | 36 | 4320 | 1440 | n/a | blocked: no label code in Daniel's repo (6 labels x 2 mixes x 3 seeds) |
| D to G | `undercover, warning, precedent arms` | n/a | 0 | 45 | 5400 | 1800 | n/a | blocked: no undercover seat, report tool, persona, warning or precedent code yet (9 must run arms x 5 seeds) |
