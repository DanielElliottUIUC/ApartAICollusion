"""Shared loaders for the report_ms figures. Every figure reads its input only through these functions.

Inputs (all inside report_ms/data/):
  ms_runs.csv                      our 60 runs, written by scripts/build_ms_runs.py
  ms_prereg.csv                    the 12 runs of the pre-specified Sol opening-price test, same script
  ms_quotes.csv                    the full text of the two Figure 4b messages, same script
  daniel/dg/table3_extra.csv       Daniel's per-market message and report counts (50 Gemini markets)
  daniel/dg/market_by_run.csv      Daniel's per-market joint criterion (same 50 markets)
  daniel/dg/outcomes_by_arm.csv    Daniel's per-arm judge rates, Gemini sellers
  daniel/dg_gpt41/outcomes_by_arm.csv   same, GPT-4.1 sellers
  daniel/dg_haiku/outcomes_by_arm.csv   same, Claude Haiku 5.5 sellers
Daniel's files are copies of ApartAICollusion report/data/ at commit b7cbccd.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]          # report_ms/
DATA = ROOT / "data"
DANIEL = DATA / "daniel"
FIGURES = ROOT / "report" / "figures"

HOURS = list(range(1, 16))
ASK_COLS = [f"ask_h{h}" for h in HOURS]


def ms_runs():
    """Our runs, one row per run, with a 'seller' key (sol, luna, grok, gemini_ms)."""
    df = pd.read_csv(DATA / "ms_runs.csv", float_precision="round_trip")     # exact JSON values
    key = {"gpt-5.6-sol": "sol", "gpt-6-luna": "luna", "grok-4.7": "grok",
           "google/gemini-3.8-flash": "gemini_ms"}
    df["seller"] = df["seller_model"].map(key)
    if df["seller"].isna().any():
        raise ValueError("unknown seller model in ms_runs.csv")
    return df


def ms_prereg():
    """The pre-specified Sol test: 12 runs (seeds 3 to 8, opened at $97.50 and at $90), columns as ms_runs.csv."""
    df = pd.read_csv(DATA / "ms_prereg.csv", float_precision="round_trip")
    if len(df) != 12 or set(df["seller_model"]) != {"gpt-5.6-sol"}:
        raise ValueError("ms_prereg.csv must hold 12 Sol runs")
    return df


def ms_quotes():
    return pd.read_csv(DATA / "ms_quotes.csv")


def daniel_markets():
    """Daniel's 50 Gemini D-G markets: arm, seed, private_msgs_peer, reported_seat5, ask_index, passed."""
    t3 = pd.read_csv(DANIEL / "dg" / "table3_extra.csv")
    mk = pd.read_csv(DANIEL / "dg" / "market_by_run.csv")
    df = t3.merge(mk[["run_id", "ask_index", "trade_index", "trades_per_round", "passed"]],
                  on="run_id", how="inner", validate="one_to_one")
    if len(df) != 50:
        raise ValueError(f"expected 50 Daniel Gemini markets, found {len(df)}")
    df["seller"] = "gemini_dg"
    return df


def daniel_outcomes(family):
    """Per-arm judge rates; family is 'dg' (Gemini), 'dg_gpt41' or 'dg_haiku'."""
    return pd.read_csv(DANIEL / family / "outcomes_by_arm.csv").set_index("arm")


def count(rate, n):
    """Seller count from a rate over n seller-episodes; refuses rates that are not whole counts."""
    c = rate * n
    if abs(c - round(c)) > 1e-6:
        raise ValueError(f"rate {rate} over {n} is not a whole count")
    return int(round(c))
