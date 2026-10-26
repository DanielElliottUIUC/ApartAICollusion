# Figures: provenance

Every figure is drawn by a script in `scripts/figures/` from the committed CSVs under `report/data/`, except where a script notes that it also reads the raw run folders under `results/` (local, gitignored) and cross-checks its counts against the committed CSVs. Each `<name>.caption.txt` holds the figure's working caption and the method used to compute its numbers; the paper captions are in `report/REPORT.md`.

| File | Used in the report | Script | Data | Notes |
|---|---|---|---|---|
| `fig_design_timeline.png/.svg` | Figure 1 | `scripts/figures/fig_design_timeline.py` | each run's `experiment_metadata.json`, `collusion_metrics.json` and `auction_results.md` in `results/dg`; `report/data/dg/market_by_hour.csv` | seat 5's ask path is the same in every run of a seat mode; the placebo path equals `configs/replay/base_pilot_norule.json` |
| `fig_report_and_feign.png/.svg` | Figure 2 | `scripts/figures/fig_report_and_feign.py` | `report/data/dg/fig_report_and_feign_cells.csv` (one row per seller-episode in arms D and Base, extracted from `results/dg` and checked against `table3_extra.csv` and `outcomes.csv`) | reply stance is hand-coded; `states_intent` flags reasoning sentences naming seat 5 with pretend, feign, deceptive, placate, pacify, appease, reassure or anchor; the legend reads "reported and wrote back agreeing" |
| `fig_reporting_by_arm.png/.svg` | Figure 3 | `scripts/figures/fig_reporting_by_arm.py` | `report/data/dg/table3_extra.csv`, `report/data/dg/permutation_tests.csv` | per-arm private-message means: Base 108.0, D 108.0, D-hs 108.0, D-hb 107.4, D-hsb 109.4, E 1.0, F 0.4, F-sham 0.8, G-warn 3.0, G-prec 0.0 |
| `fig_three_families.png/.svg` | not used (Table 2 instead) | `scripts/figures/fig_three_families.py` | `report/data/{dg,dg_haiku,dg_gpt41}/outcomes_by_arm.csv`, `table3_extra.csv`, raw `unified.log` files for the GPT-4.1 and Haiku message counts | plotted values in `fig_three_families.data.csv` |
| `fig_arms_grid.png/.svg` | not used (Table 1 instead) | `scripts/figures/fig_arms_grid.py` | each run's `experiment_metadata.json` in `results/dg` | |
| `fig_channels_by_arm.png/.svg` | not used | `scripts/figures/fig_channels_by_arm.py` | `report/data/dg/table3_extra.csv`; per-hour counts from `results/dg/*/unified.log` | plotted values in `fig_channels_by_arm.data.csv` |
| `fig_pretrend.png/.svg` | not used | `scripts/figures/fig_pretrend.py` | `report/data/dg/market_by_hour.csv` | |
| `fig_aa_noise.png/.svg` | not used | `scripts/figures/fig_aa_noise.py` | `report/data/dg/market_by_hour.csv`, `outcomes.csv` | |
| `fig_opening_anchor.png/.svg` | not used | `scripts/figures/fig_opening_anchor.py` | our step-A `unified.log` files and M.S.'s low-opening run folders | plotted values in `fig_opening_anchor.data.csv` |
| `fig_dg_ask_index.png/.svg`, `fig_dg_outcomes.png/.svg` | not used | `scripts/make_dg_figures.py` | `report/data/dg/` | earlier draft figures |

To regenerate a figure, run its script from `third_party/llm-agent-collusion` with `PYTHONUTF8=1 uv run python ../../scripts/figures/<name>.py`; scripts that need the raw runs take `--results-dir` and fall back to the committed CSV when the folder is absent.
