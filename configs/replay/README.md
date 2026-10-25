# Replay files for the D–G scripted seat.

- `base_pilot_norule.json` (default): seat 5 (Seller Mia) of the no-rule Base pilot `results/dg_pilot/20261025_001547_pilot-norule-seed0` (report action on, prohibition rule off). Used by every D–G arm and seed.
- `base_pilot_rule.json`: seat 5 of the rule-on pilot `20261024_232352_pilot-seed0`; use with `RULE=1 REPLAY_NAME=base_pilot_rule` for the rule-on contrast (the two rule-on runs live in `results/dg_rule/`).

Written by `bash scripts/run_dg_arms.sh extract <pilot_run_dir>` (seat 5 = last seller).
