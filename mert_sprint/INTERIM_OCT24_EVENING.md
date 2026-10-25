# Interim drop, Sat Oct 24 2026 evening

> **Warning: 15 of the 27 shard 3 Gemini runs in this drop are invalid. Do not use them or their judge scores.**
>
> Gemini was served through OpenRouter, which limited the account to 20 requests per minute per model.
> Calls that hit the limit (HTTP 429) failed after 3 retries, so rounds ran with missing model answers.
> The runner still recorded exit code 0. Each of the 15 run logs has 3 to 88 lines "Failed after 3 attempts".
> The 15 runs: `danielA_gemini_comms` seeds 0, 1, 2; `danielA_gemini_nocomms` seeds 0, 2; `danielA_gemini_notice` seeds 0, 1, 2;
> `danielB_GGGG` seeds 0, 1, 2; `het55_GGG_s0`, `_s1`, `_s2`; `het55_GGO_s0`.
> They are moved to `experiments/invalid_429_shard3/` (see its README for failed calls per run).
> The Grok 4.7 judge files for 11 of them moved with them. Do not use those scores.
> The other 12 shard 3 Gemini runs have no failed calls in their logs and stay in `experiments/runs/shard3/`.
> `experiments/runs/shard3/status.jsonl` and `run_all.log` still list the 15 with exit code 0. Ignore those lines.
> The dashboard copy here was built before these runs landed and does not show them.
> Valid reruns, with the proxy limited to 15 requests per minute (`OPENROUTER_RPM=15`), are in progress and will come in a later PR.

This drop copies Mert's sprint repo at commit `aaa95e3` into `mert_sprint/`.
It builds on PR #15. Only finished runs are included.
Nothing outside `mert_sprint/` is changed. Daniel's code is untouched.

## What is new since PR #15

| What | Where | Count |
| --- | --- | --- |
| Gemini runs, Gemini 3.8 Flash served through OpenRouter (shard 3) | `experiments/runs/shard3/` (matrix, sweep) | 27 runs ran. 12 are valid. 15 are invalid and moved to `experiments/invalid_429_shard3/` |
| Frontier runs with messaging off, GPT 6 Luna and GPT 5.6 Sol sellers (shard 2) | `experiments/runs/shard2/frontier/` | 12 runs, all exit code 0 |
| Frontier runs with messaging on (box, shard 1) | `experiments/runs/box/frontier/` | 16 of 24 runs: 6 Luna, 6 Sol, 4 Grok 4.7 (`grok47_comms_lunaB-seed2` added in the follow up PR) |
| Reruns of the het55 CCO, OOC and OOO auctions with working Luna seats | `experiments/runs/shard2/matrix/`, `experiments/runs/shard3/matrix/` | 9 runs (5 and 4) |
| Grok 4.7 post hoc judge outputs | `judge_grok-4.7_summary.json` and `llm_eval_grok-4.7.json` in each scored run folder | 23 runs: the 12 shard 2 frontier runs (valid) and 11 shard 3 Gemini runs (Daniel step A and B, all 11 invalid, now in `experiments/invalid_429_shard3/`) |
| Judge script | `scripts/judge_with_grok.py` | 1 |
| New case pages | `experiments/cases/double_auction/` | 21 (12 frontier, 9 het55 reruns) |
| Run plan for the three machines | `notes/RUN_PLAN_oct24_evening.md` | 1 |

Notes, status, the behaviour report, the dashboard and the token usage files are refreshed to the same commit.
The 16 box frontier runs have no case pages and no judge scores yet.

## Still running

8 Grok 4.7 frontier runs on the box are not done. They are the 2 messaging on runs left
(`grok47_comms_haikuB-seed0`, `grok47_comms_lunaB-seed1`) and the 6 messaging off runs.
They will come in a later PR.

## The Grok 4.7 judge

The judge runs after the market closes. It does not change any run.
`scripts/judge_with_grok.py` imports Daniel's seller judge prompt and parser from
`src/continuous_double_auction/evaluation/evaluate.py` and only swaps the model in memory, to Grok 4.7.
It writes its own files and never overwrites Daniel's `llm_eval_full.json`.
It is separate from Daniel's gpt-4.1-mini in-run judge and from his post hoc judges in PR #12.
Grok 4.7 scores and gpt-4.1-mini scores are not directly comparable.

## Preexisting code

The double auction harness is Daniel's (`third_party/llm-agent-collusion` and `src/`), at origin/main `4fe4637`.
The Bertrand harness is the Poseidon `llm-cartel` starter. Both come from the Poseidon `collusion_hackathon` starter repo.
The subscription proxy, the run scripts, the judge script, the dashboard and the notes were written during the sprint.

## Proxy change

`src/subscription_proxy/server.py` now has an optional `OPENROUTER_RPM` limit. It spaces OpenRouter calls per model so no more than that many go out in 60 seconds. Unset or 0 means no limit.

## Left out of this copy

`AGENTS.md`, `CLAUDE.md`, `archive/`, the private ledger and every key file stay in the private repo.
`notes/CREDITS.md` keeps its shortened public version. Home folder paths in logs are replaced by `~` or `%USERPROFILE%`.
Event page links in the dashboard data are blanked.
