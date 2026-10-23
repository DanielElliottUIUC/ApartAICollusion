# Token and cost log

Append-only. Each section is one snapshot written by `scripts/snapshot_usage.py` from the cross-vendor token ledger. Costs are API-equivalent list prices; the work ran on flat subscriptions.

## Snapshot 2026-10-23 18:46

Whole lab (7 machines; machine snapshots dated 2026-06-07 to 2026-10-23): **11.89 B tokens**, **$6,902** at API list prices (Codex fast-adjusted: $16,310).

| Engine | Tokens (B) | Cost (USD, list) |
|---|---|---|
| Codex | 10.971 | 6,272.18 (fast-adjusted 15,680.45) |
| Claude Code | 0.916 | 629.55 |
| Claude Code, older state (separate) | 0.218 | 194.23 |

| Model | Tokens (B) | Cost (USD, list) |
|---|---|---|
| gpt-5.4 | 5.526 | 2,594.56 |
| gpt-5.5 | 3.644 | 3,147.03 |
| gpt-5.3-codex | 1.460 | 434.78 |
| gpt-5.2-codex | 0.251 | 66.56 |
| gpt-5-codex | 0.040 | 16.57 |
| gpt-5.4-mini | 0.028 | 3.12 |
| gpt-5.1-codex | 0.012 | 3.72 |
| gpt-5.6-sol | 0.008 | 4.92 |
| gpt-5 | 0.000 | 0.93 |
| claude-opus-4-6 | 0.627 | 460.18 |
| claude-opus-4-8 | 0.112 | 96.69 |
| claude-haiku-4-5-20251001 | 0.088 | 17.89 |
| claude-opus-5-5 | 0.059 | 23.93 |
| claude-opus-4-5-20251101 | 0.026 | 22.07 |
| claude-opus-4-7 | 0.002 | 2.01 |
| claude-sonnet-4-5-20250929 | 0.001 | 0.66 |
| claude-fable-5 | 0.001 | 4.18 |
| claude-sonnet-4-6 | 0.000 | 0.61 |
| claude-opus-5 | 0.000 | 0.68 |
| claude-fable-5-1 | 0.000 | 0.65 |

Sprint box: Claude Code 59.9 M tokens ($29.44), Codex 8.2 M tokens ($4.92). Experiment calls through the proxy: 160 logged.

![Tokens by model](usage_by_model.svg)

![Tokens by month](usage_by_month.svg)

## Snapshot 2026-10-23 18:55

Whole lab (11 machines; machine snapshots dated 2026-08-27 to 2026-10-23): **100.46 B tokens**, **$79,683** at API list prices (with Codex fast-adjusted: $124,615).

| Engine | Tokens (B) | Cost (USD, list) |
|---|---|---|
| Codex | 35.370 | 29,954.80 (fast-adjusted 74,886.99) |
| Claude Code (reconciled) | 63.497 | 49,059.41 |
| Grok | 1.595 | 668.44 |
| Claude Code, older state (separate) | 0.350 | 327.45 |

| Model | Tokens (B) | Cost (USD, list) |
|---|---|---|
| claude-opus-5-5 | 38.376 | 17,831.11 |
| gpt-5.6-sol | 17.998 | 13,271.55 |
| claude-fable-5 | 8.744 | 16,988.80 |
| claude-opus-5 | 7.479 | 6,661.32 |
| gpt-5.5 | 7.012 | 7,173.19 |
| gpt-5.4 | 4.699 | 2,662.89 |
| gpt-6-astra | 3.678 | 6,231.07 |
| claude-fable-5-1 | 3.579 | 3,210.26 |
| claude-opus-4-8 | 2.880 | 2,920.59 |
| gpt-5.3-codex | 1.276 | 400.50 |
| claude-sonnet-5 | 1.081 | 597.18 |
| grok-4.7-build | 0.704 | 330.44 |
| claude-opus-4-6 | 0.627 | 488.47 |
| grok-4.6-build | 0.528 | 123.42 |
| claude-sonnet-5-5 | 0.474 | 270.98 |
| grok-4.7-build-fast | 0.312 | 193.76 |
| gpt-5.2-codex | 0.252 | 67.02 |
| claude-haiku-4-5-20251001 | 0.205 | 51.09 |
| gpt-5.6-luna | 0.155 | 7.40 |
| gpt-5-codex | 0.042 | 17.24 |
| gpt-5 | 0.037 | 11.75 |
| grok-4.5-build | 0.028 | 13.85 |
| gpt-5.4-mini | 0.026 | 2.97 |
| claude-opus-4-5-20251101 | 0.026 | 23.38 |
| gpt-5.1-codex | 0.007 | 2.35 |
| claude-haiku-5-5 | 0.007 | 1.06 |
| gpt-6.1-sol | 0.002 | 0.62 |
| claude-opus-4-7 | 0.002 | 2.01 |
| gpt-5.2 | 0.001 | 1.34 |
| claude-sonnet-4-5-20250929 | 0.001 | 0.92 |
| claude-sonnet-4-6 | 0.000 | 0.61 |
| gpt-5.6-terra | 0.000 | 0.01 |

Sprint box: Claude Code 69.3 M tokens ($32.08), Codex 8.2 M tokens ($4.92). Experiment calls through the proxy: 160 logged.

![Tokens by model](usage_by_model.svg)

![Tokens by month](usage_by_month.svg)

