# Dashboard Page: "Daniel's experiment, explained visually"

This folder is a copy of the interactive Page we built during the sprint to explain Daniel Elliott's undercover collusion test.
All of the experiment design and the D to G results are Daniel's work.
Mert's own frontier runs appear only in the evidence and moments sections, labeled as Mert's.

## Files

* `daniel_experiment_explained.html`: a standalone static copy. Open it in any browser. It needs no server and no network.
* `daniel_experiment_explained.canvas.tsx`: the original Page source, exactly as written for the Grok Bot canvas runtime (it imports from `grok/canvas`).
* `build/`: the script that turns the source into the standalone HTML.
  * `build/grok-canvas-shim.tsx` is a small stand in for the `grok/canvas` component library, written for this copy. It approximates the original look. It is not the original library, so spacing and styling differ slightly from the live Page.
  * `build/build.sh` bundles the source with React 18 and esbuild into one HTML file.

## What it shows

1. The double auction market from Agrawal et al. 2025 (arXiv 2507.01413), animated.
2. The ask index and the pass rule.
3. How sellers talk: public board, private messages, one hour delay.
4. Step A, and what the prohibition rule is.
5. The ten D to G arms with plain names, the exact texts seat 5 and buyer 5 send, and each arm's results.
6. An hour by hour replay of the mean ask index per arm.
7. Other seller models and identity labels.
8. How reliable the judge's labels are (Opus versus Haiku agreement, 20 items per label).
9. Findings, an evidence card per case, surprises, and 15 notable messages and moments with verbatim quotes.

## Data sources

* Daniel's repo, origin/main at b7cbccd and PR #28: `report/REPORT.md`, `report/data/dg/*.csv` (market_by_arm, outcomes_by_arm, market_by_hour, table3_extra, permutation_tests), `report/data/dg/judge_handcheck.md`, `report/data/dg_gpt41/`, `report/data/dg_haiku/`, `report/data/c/c_by_run.csv`, and `configs/texts/*.txt`.
* Mert's frontier runs in `experiments/runs/` of our sprint repo. Those runs used Claude Haiku 5.5 or GPT 6 Luna buyers, not GPT 4.1 mini.

## Caveats

* The animated market in section 1 uses made up example prices. It shows the mechanics, not run data. The page says so under the animation.
* Section 10, Fun interactions, replays five real episodes hour by hour. Messages appear one at a time, and a highlight marks the key phrase in some messages without changing any words. Four come from full run logs (unified.log and seller files). The fifth, Daniel's D seed 0, is reconstructed from his CSVs and quoted excerpts, because his raw logs are not in the repo. The page says which is which.
* Every quote is verbatim from the file named under it. Daniel's raw run logs were not available to us, so his quotes come from his report and judge check file.
