"""Loaders for the body figures adapted from M.S.'s report figures.

Adapted from M.S.'s mert_sprint/report_ms/scripts/lib/load.py (ref origin/mert_sprint_sync_oct25), by M.S.
Change: his figures read copies of this repo's report/data (his report_ms/data/daniel/, copied at b7cbccd); these
read the committed CSVs directly. The copies are identical to the committed files apart from line endings.

Inputs (all under report/data/):
  dg/table3_extra.csv            per-market message and report counts (50 Gemini markets)
  dg/market_by_run.csv           per-market ask index and joint criterion (same 50 markets)
  dg/outcomes_by_arm.csv         per-arm judge and report rates, Gemini sellers
  dg_gpt41/outcomes_by_arm.csv   same, GPT-4.1 sellers
  dg_haiku/outcomes_by_arm.csv   same, Claude Haiku 5.5 sellers
  dg_gpt41_99/outcomes.csv       GPT-4.1 sellers offered $99 (arm D99), one row per seller-episode
"""
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
DATA = REPO / "report" / "data"


def daniel_markets():
    """The 50 Gemini undercover-market runs: arm, seed, private_msgs_peer, public_msgs, reported_seat5,
    ask_index, passed."""
    t3 = pd.read_csv(DATA / "dg" / "table3_extra.csv")
    mk = pd.read_csv(DATA / "dg" / "market_by_run.csv")
    df = t3.merge(mk[["run_id", "ask_index", "trade_index", "trades_per_round", "passed"]],
                  on="run_id", how="inner", validate="one_to_one")
    if len(df) != 50:
        raise ValueError(f"expected 50 Gemini markets, found {len(df)}")
    return df


def daniel_outcomes(family):
    """Per-arm judge rates; family is 'dg' (Gemini), 'dg_gpt41' or 'dg_haiku'."""
    return pd.read_csv(DATA / family / "outcomes_by_arm.csv").set_index("arm")


def gpt41_99():
    """GPT-4.1 sellers offered $99 (arm D99): sellers who reported seat 5, sellers who raised their ask by $1 or
    more in hours 4 to 6, and the hand-coded tone of every message to seat 5."""
    d = pd.read_csv(DATA / "dg_gpt41_99" / "outcomes.csv")
    e = d[d["arm"] == "D99"]
    tones = [t for cell in e["tone_all_msgs"].dropna() for t in str(cell).split(";")]
    return {"n": len(e), "reported": int(e["reported_seat5"].sum()), "rose": int(e["rose_ge_1"].sum()),
            "declining": sum(t == "declining" for t in tones), "msgs": len(tones)}


def count(rate, n):
    """Seller count from a rate over n seller-episodes; refuses rates that are not whole counts."""
    c = rate * n
    if abs(c - round(c)) > 1e-6:
        raise ValueError(f"rate {rate} over {n} is not a whole count")
    return int(round(c))
