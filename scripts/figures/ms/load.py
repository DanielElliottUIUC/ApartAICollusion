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
  dg_gpt41_99/outcomes.csv       GPT-4.1 sellers offered $99 (arm D99), one row per seller-episode, plus the GPT-4.1 D
                                 and Base comparators (hand-coded tone of the first message to seat 5 for D)
  dg/fig_report_and_feign_cells.csv  every Gemini D and Base seller: reports of seat 5 and the hand-coded stance of
                                 the first reply to seat 5
  dg_gemini_99/outcomes.csv      Gemini sellers offered $99 (arm D99), one row per seller-episode. This folder is on
                                 the extension-runs-oct25 branch; until it is merged, `committed_csv` reads it from
                                 that branch with `git show` (new sprint code, not M.S.'s).
"""
import subprocess
from io import StringIO
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


# New sprint code (not M.S.'s): per-seller loaders for the hand-coded columns of Figure 4b.

EXTENSION_REF = "origin/extension-runs-oct25"


def committed_csv(rel):
    """report/data/<rel> from this checkout, or, while the folder is not merged yet, the same path on
    EXTENSION_REF (read with `git show`, so only committed bytes are used)."""
    path = DATA / rel
    if path.exists():
        return pd.read_csv(path)
    spec = f"{EXTENSION_REF}:report/data/{rel}"
    out = subprocess.run(["git", "show", spec], cwd=REPO, capture_output=True, check=True)
    print(f"  note: report/data/{rel} is not in this checkout; read from {spec}")
    return pd.read_csv(StringIO(out.stdout.decode("utf-8")))


def gemini_d_cells():
    """The 20 Gemini D sellers: reported_seat5 and reply_stance (agrees / declines / empty when no reply)."""
    c = pd.read_csv(DATA / "dg" / "fig_report_and_feign_cells.csv")
    return c[c["arm"] == "D"]


def d99_rows(family):
    """Per-seller rows of the $99 extension and its comparators; family is 'gemini' or 'gpt41'."""
    return committed_csv(f"dg_{family}_99/outcomes.csv")


def judge_rows(folder, arm):
    """Per-seller judge and report rows of one arm; folder is 'dg', 'dg_gpt41' or 'dg_haiku'."""
    o = pd.read_csv(DATA / folder / "outcomes.csv")
    return o[o["arm"] == arm]
