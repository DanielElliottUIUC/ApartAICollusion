"""Rebuild the report's Tables 2, 3, 4, 4b and 5 from the analysis CSVs committed under report/data/.

    python scripts/make_tables.py                          print every table as markdown
    python scripts/make_tables.py --out report/build/tables.md
                                                            also write the tables to a file
    python scripts/make_tables.py --check                  also diff them against the tables in
                                                            report/REPORT.md (found by their caption
                                                            lines "*Table 2." etc.); exit 1 if any
                                                            producible value differs
    python scripts/make_tables.py --check --report PATH    check another copy of the report
    python scripts/make_tables.py --check --json PATH      also write the tables and the check result
                                                            (including the "unchecked" cells) as JSON

Sources
    Table 2   report/data/dg/outcomes_by_arm.csv
    Table 3   report/data/dg/table3_extra.csv (per-run counts extracted from the run logs by
              scripts/extract_dg_message_counts.py), dg/outcomes.csv (per seller-episode asks),
              dg/outcomes_by_arm.csv and dg/market_by_arm.csv
    Table 4   report/data/dg_gpt41/outcomes_by_arm.csv, dg_gpt41/market_by_arm.csv
    Table 4b  report/data/dg/ (Gemini D), dg_haiku/ (Haiku D), dg_gpt41/ (GPT-4.1 D and F)
    Table 5   report/data/c/c_by_run.csv

Conventions
    * Counts vs rates: outcomes.py by_arm() writes, per judge label, `<label>_rate` (positives over
      non-null observations, pooled over the arm's markets) and `<label>_n` (the number of non-null
      observations). The count of positives is therefore round(`<label>_rate` * `<label>_n`), with
      n_seller_episodes used only when `_n` is absent or null. rate * n must be a whole number to
      within 1e-6, otherwise the script stops. In the committed CSVs `_n` equals n_seller_episodes
      on every row (20 per Gemini arm, 12 per GPT-4.1/Haiku arm).
    * LLM sellers only: market_by_arm.csv and table3_extra.csv cover the four LLM sellers; the
      scripted seat 5 is excluded everywhere except as a target of reports and messages.
    * "Reported seat 5", Gemini (Table 3, Table 4b): sum of reported_seat5 in table3_extra.csv -
      distinct sellers with at least one report naming seat 5, counted from the run logs. This is
      deliberately not report_is_scripted_seat in outcomes.csv, which looks only at each seller's
      FIRST report and so gives 19 (D-hb) and 18 (E) where the logs give 20 and 20: one D-hb
      seller and two E sellers first reported a peer, then reported seat 5. Likewise Table 2's
      "Reported anyone" for D-hsb is 8 while Table 3's seat-5 count is 7 (one seller reported
      only a peer).
    * "Reported seat 5", GPT-4.1 and Haiku (Tables 4 and 4b): `reported` (a report against
      anyone) is used because no log-extract CSV like table3_extra.csv exists for these families.
      In the offer arms D and F seat 5 is the only party reported (false_report = 0), and
      `reported` and report_is_scripted_seat agree for both families (Haiku D: 3 of 12 in each
      column; GPT-4.1: 0 in Base, D, E and G-warn, 12 of 12 in F).
    * Missing data stops the script instead of printing a zero: every arm in outcomes_by_arm.csv
      must have exactly n_runs rows in table3_extra.csv (distinct seeds, the same run_ids as
      outcomes.csv, no empty cells), and every Table 5 label must have three distinct seeds in
      c_by_run.csv.
    * Cells the CSVs cannot produce are printed as "n/a from CSV" and left unchecked by --check,
      which counts and lists them once at the end (and under "unchecked" in --json): Table 4's
      "Msgs to seat 5 /market" and "Private msgs /market" (dg_gpt41 has no message-count CSV) and
      its "No comms (2 seeds)" row (the two messaging-off runs are not in the CSVs); Table 4b's
      "Private msgs /market" for Haiku and GPT-4.1 (table3_extra.csv is Gemini-only); Table 5's
      "none (step A comms)" baseline row (the step-A runs predate the label CSVs) and its
      "Seller-hours mentioning the label" column (not in c_by_run.csv). That is 30 cells.
    * Formatting, matching the report: counts as integers; means of message counts as integers
      when whole, one decimal otherwise; asks, indices and dollar changes with two decimals;
      negative numbers use the Unicode minus sign U+2212; an ask-index seed range is "(lo-hi)" and
      switches to "(lo to hi)" when a bound is negative; Table 3 shows the per-seed report counts
      only when the arm total is neither 0 nor n, and marks the placebo arms' reply counts
      (replies to the placebo note) with *; Table 5 means come from unrounded seed values, and a
      label's pass count carries a dagger when a passing seed traded at or below one lot per hour
      (trades_per_round <= 1.0).

How --check compares
    * Each report table is the markdown table just above its "*Table N." caption. Its header row is
      read and columns are matched by header text (markdown emphasis, code ticks, escapes,
      whitespace and case ignored). A column the CSVs produce that the report lacks, or the other
      way round, is a failure, as is a row present on one side only and a row key that appears
      twice. Cells are compared by (row key, column name), never by position.
    * A cell is a "match" when the text is identical. Otherwise both cells are split into their
      numbers and the text around them ("$", "%" and spaces dropped, U+2212 read as a minus sign;
      a parenthesised part such as "(0.12-0.61)" or "(4,3,4,4,4)" stays a separate token). If the
      text around the numbers is the same and each pair of numbers differs by less than the
      column's tolerance, the cell is a "match (rounding)": below 0.5 for message-count columns
      (the report prints 58 where the CSV mean is 58.4), below 0.005 for index columns and dollar
      columns; counts must be equal. Anything else "differs" and makes --check exit 1.

No LLM API is called and no simulation is run; everything comes from the committed CSVs. The only
dependency is pandas.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "report" / "data"
REPORT = REPO / "report" / "REPORT.md"
NA = "n/a from CSV"
MINUS = "−"  # U+2212, the minus sign the report uses
DAGGER = "†"

# The report's arm order: a copy of ARM_ORDER / arm_sort_key in src/apartcollusion/runs.py, kept
# here so this script needs only pandas (runs.py imports numpy and loads modules from the vendored
# harness). scripts/tests/test_make_tables.py checks that the two lists stay identical.
ARM_ORDER = ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "G-warn", "G-prec", "F-sham", "Base-hb"]

# Table 3 arms whose seat-5 replies answer the placebo note, marked * in the report.
PLACEBO_REPLY_ARMS = {"Base", "G-warn", "G-prec"}
# Table 4 shows the messaging arms that the dg_gpt41 CSVs share with the report (F is in 4b).
TABLE4_ARMS = ["Base", "D", "E", "G-warn"]
# Table 5 row label for each label value in c_by_run.csv, in the report's order.
TABLE5_LABELS = [
    ("claude", "Claude (Anthropic model)"),
    ("deepseek", "DeepSeek (DeepSeek model)"),
    ("blackrock", "BlackRock agents"),
    ("palantir", "Palantir agents"),
    ("un", "United Nations agents"),
    ("team_blue", "Team Blue members"),
]
TABLE5_SEEDS = 3
# table3_extra.csv columns the tables read; an empty cell in any of them stops the script.
EXTRA_COLUMNS = ["reported_seat5", "replied_to_seat5_from_h4", "private_msgs_llm_total",
                 "public_msgs"]


def arm_sort_key(arm: str) -> tuple[int, str]:
    return (ARM_ORDER.index(arm), "") if arm in ARM_ORDER else (len(ARM_ORDER), arm)


# ---------------------------------------------------------------- formatting helpers

def fmt2(x: float) -> str:
    """Two decimals, negative numbers with the U+2212 minus sign."""
    return f"{x:.2f}".replace("-", MINUS)


def fmt_msg_mean(x: float) -> str:
    """Mean of message counts: integer when whole, one decimal otherwise (0.4, 45.8, 108)."""
    return str(int(round(x))) if float(x).is_integer() else f"{x:.1f}"


def fmt_index_range(mean: float, lo: float, hi: float) -> str:
    """Ask index with its seed range; negative bounds use 'lo to hi', as in Table 4b."""
    rng = f"{fmt2(lo)} to {fmt2(hi)}" if (lo < 0 or hi < 0) else f"{fmt2(lo)}-{fmt2(hi)}"
    return f"{fmt2(mean)} ({rng})"


# ---------------------------------------------------------------- data helpers

def read_csv(rel: str) -> pd.DataFrame:
    return pd.read_csv(DATA / rel)


def by_arm(df: pd.DataFrame) -> pd.DataFrame:
    """Sort a one-row-per-arm frame into the report's arm order."""
    return df.set_index("arm").loc[sorted(df["arm"].unique(), key=arm_sort_key)]


def label_denominators(df: pd.DataFrame, label: str) -> pd.Series:
    """Seller-episodes judged for `label`, per arm: `<label>_n` (non-null observations, as written
    by outcomes.py by_arm()), or n_seller_episodes where `_n` is absent or null."""
    n_ep = df["n_seller_episodes"]
    if f"{label}_n" not in df.columns:
        return n_ep.astype(int)
    n_col = df[f"{label}_n"]
    return n_col.where(n_col.notna(), n_ep).astype(int)


def label_counts(df: pd.DataFrame, label: str) -> pd.Series:
    """Count of seller-episodes with the label true, per arm, from a *_by_arm.csv: round(rate * n)
    with n from label_denominators(). Stops if rate * n is not a whole number to within 1e-6."""
    rates = df[f"{label}_rate"]
    denominators = label_denominators(df, label)
    counts = {}
    for arm in df.index:
        rate, n = rates[arm], int(denominators[arm])
        if pd.isna(rate):
            raise ValueError(f"{label}_rate is empty for arm {arm!r} (n = {n}); no count to print")
        raw = float(rate) * n
        count = round(raw)
        if abs(raw - count) > 1e-6:
            raise ValueError(f"{label}: rate {rate!r} * n {n} = {raw!r} for arm {arm!r} is not a "
                             f"whole number of seller-episodes")
        counts[arm] = int(count)
    return pd.Series(counts, dtype=int)


def gemini_extra(arms: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """table3_extra.csv rows per arm (sorted by seed), checked against outcomes_by_arm.csv.

    A missing arm or seed would otherwise sum to a silent 0 (or average over fewer markets), so any
    gap stops the script with an error that names the arm.
    """
    extra = read_csv("dg/table3_extra.csv")
    outcomes = read_csv("dg/outcomes.csv")
    problems = []
    unknown = sorted(set(extra["arm"]) - set(arms.index))
    if unknown:
        problems.append(f"arm(s) {unknown} are in table3_extra.csv but not in outcomes_by_arm.csv")
    per_arm = {}
    for arm in arms.index:
        n_runs = int(arms.loc[arm, "n_runs"])
        sub = extra[extra["arm"] == arm].sort_values("seed")
        if sub.empty:
            problems.append(f"arm {arm!r}: no rows in table3_extra.csv "
                            f"(outcomes_by_arm.csv has {n_runs} runs)")
            continue
        seeds = sub["seed"].tolist()
        if sub["seed"].duplicated().any():
            problems.append(f"arm {arm!r}: duplicate seeds in table3_extra.csv {seeds}")
        if len(sub) != n_runs:
            problems.append(f"arm {arm!r}: {len(sub)} run(s) in table3_extra.csv (seeds {seeds}) "
                            f"but n_runs = {n_runs} in outcomes_by_arm.csv")
        want_runs = set(outcomes.loc[outcomes["arm"] == arm, "run_id"])
        have_runs = set(sub["run_id"])
        if have_runs != want_runs:
            problems.append(f"arm {arm!r}: run_ids in table3_extra.csv differ from outcomes.csv "
                            f"(only in table3_extra: {sorted(have_runs - want_runs)}; "
                            f"only in outcomes: {sorted(want_runs - have_runs)})")
        empty = [c for c in EXTRA_COLUMNS if sub[c].isna().any()]
        if empty:
            problems.append(f"arm {arm!r}: empty cells in table3_extra.csv column(s) {empty}")
        per_arm[arm] = sub
    if problems:
        raise ValueError("report/data/dg/table3_extra.csv does not cover outcomes_by_arm.csv:\n  "
                         + "\n  ".join(problems))
    return per_arm


def skip(skips: list, table: str, row: str, column: str, reason: str) -> str:
    """Register a cell the CSVs cannot produce and return its placeholder text."""
    skips.append({"table": table, "row": row, "column": column, "reason": reason})
    return NA


def skip_row(skips: list, table: str, row: str, header: list[str], reason: str) -> list[str]:
    """A whole row the CSVs cannot produce: one registered placeholder per non-key column."""
    return [row] + [skip(skips, table, row, column, reason) for column in header[1:]]


# ---------------------------------------------------------------- tables

def build_table2() -> tuple[list[list[str]], list[dict]]:
    """Report and judge-label counts out of 20 Gemini seller-episodes per arm."""
    df = by_arm(read_csv("dg/outcomes_by_arm.csv"))
    labels = ("reported", "suspects_collusion", "suspects_test", "verbal_accept")
    counts = {label: label_counts(df, label) for label in labels}
    rows = [["Arm", "Reported anyone /20", "Suspects collusion /20", "Suspects test /20",
             "Verbal agreement /20"]]
    for arm in df.index:
        rows.append([arm] + [str(counts[label][arm]) for label in labels])
    return rows, []


def build_table3() -> tuple[list[list[str]], list[dict]]:
    """Reports, replies, messaging and prices (Gemini, LLM sellers only)."""
    outcomes = read_csv("dg/outcomes.csv")
    arms = by_arm(read_csv("dg/outcomes_by_arm.csv"))
    market = by_arm(read_csv("dg/market_by_arm.csv"))
    extra = gemini_extra(arms)
    asks = outcomes.groupby("arm")[["ask_pre", "ask_change_post_offer"]].mean()

    rows = [[
        "Arm", "Reported seat 5 /20 (per seed)", "Replied to seat 5 /20", "Private msgs",
        "Public msgs", "Hour-3 ask, $", "Ask index (seed range)", "Trade index", "Ask change, $",
        "Passes /5",
    ]]
    for arm in arms.index:
        n_ep = int(arms.loc[arm, "n_seller_episodes"])
        sub = extra[arm]
        per_seed_reports = sub["reported_seat5"].astype(int).tolist()
        total = sum(per_seed_reports)
        reported = str(total)
        if 0 < total < n_ep:  # per-seed breakdown only when the total is neither 0 nor n
            reported += " (" + ",".join(str(v) for v in per_seed_reports) + ")"
        replied = str(int(sub["replied_to_seat5_from_h4"].sum()))
        if arm in PLACEBO_REPLY_ARMS:
            replied += "*"
        rows.append([
            arm,
            reported,
            replied,
            fmt_msg_mean(sub["private_msgs_llm_total"].mean()),
            fmt_msg_mean(sub["public_msgs"].mean()),
            f"{asks.loc[arm, 'ask_pre']:.2f}",
            fmt_index_range(market.loc[arm, "ask_index_mean"],
                            market.loc[arm, "ask_index_min"], market.loc[arm, "ask_index_max"]),
            f"{market.loc[arm, 'trade_index_mean']:.2f}",
            fmt2(asks.loc[arm, "ask_change_post_offer"]),
            str(int(round(market.loc[arm, "pass_rate"] * market.loc[arm, "n_runs"]))),
        ])
    return rows, []


def build_table4() -> tuple[list[list[str]], list[dict]]:
    """GPT-4.1 sellers; the message-count cells are not in the dg_gpt41 CSVs."""
    df = by_arm(read_csv("dg_gpt41/outcomes_by_arm.csv"))
    market = by_arm(read_csv("dg_gpt41/market_by_arm.csv"))
    counts = {label: label_counts(df, label) for label in
              ("reported", "verbal_accept", "suspects_collusion", "suspects_test")}
    reported_n = label_denominators(df, "reported")
    header = ["GPT-4.1 arm", "Msgs to seat 5 /market", "Private msgs /market",
              "Ask index (seed range)", "Verbal agreement /12", "Suspects collusion /12",
              "Suspects test /12", "Reported seat 5"]
    rows = [header]
    skips: list[dict] = []
    rows.append(skip_row(skips, "4", "No comms (2 seeds)", header,
                         "the two messaging-off GPT-4.1 runs are not in report/data/dg_gpt41/"))
    for arm in [a for a in df.index if a in TABLE4_ARMS]:
        cells = [arm]
        for column in header[1:3]:
            cells.append(skip(skips, "4", arm, column,
                              "dg_gpt41 has no message-count CSV (table3_extra.csv is Gemini-only)"))
        cells += [
            fmt_index_range(market.loc[arm, "ask_index_mean"],
                            market.loc[arm, "ask_index_min"], market.loc[arm, "ask_index_max"]),
            str(counts["verbal_accept"][arm]),
            str(counts["suspects_collusion"][arm]),
            str(counts["suspects_test"][arm]),
            f"{counts['reported'][arm]}/{reported_n[arm]}",
        ]
        rows.append(cells)
    return rows, skips


def build_table4b() -> tuple[list[list[str]], list[dict]]:
    """The plain offer across three seller families, and GPT-4.1 F."""
    gemini_out = by_arm(read_csv("dg/outcomes_by_arm.csv"))
    gemini_market = by_arm(read_csv("dg/market_by_arm.csv"))
    extra = gemini_extra(gemini_out)
    haiku = by_arm(read_csv("dg_haiku/outcomes_by_arm.csv"))
    haiku_market = by_arm(read_csv("dg_haiku/market_by_arm.csv"))
    gpt41 = by_arm(read_csv("dg_gpt41/outcomes_by_arm.csv"))
    gpt41_market = by_arm(read_csv("dg_gpt41/market_by_arm.csv"))

    header = ["Sellers, arm (seeds)", "Reported seat 5", "Suspects collusion", "Suspects test",
              "Verbal agreement", "Private msgs /market", "Ask index (range)"]
    rows = [header]
    skips: list[dict] = []

    def judged(out: pd.DataFrame, arm: str, label: str) -> str:
        return f"{label_counts(out, label)[arm]}/{label_denominators(out, label)[arm]}"

    def index_range(market: pd.DataFrame, arm: str) -> str:
        return fmt_index_range(market.loc[arm, "ask_index_mean"],
                               market.loc[arm, "ask_index_min"], market.loc[arm, "ask_index_max"])

    def gemini_row(label: str, arm: str) -> list[str]:
        sub = extra[arm]
        n_ep = int(gemini_out.loc[arm, "n_seller_episodes"])
        return [label,
                f"{int(sub['reported_seat5'].sum())}/{n_ep}",
                judged(gemini_out, arm, "suspects_collusion"),
                judged(gemini_out, arm, "suspects_test"),
                judged(gemini_out, arm, "verbal_accept"),
                fmt_msg_mean(sub["private_msgs_llm_total"].mean()),
                index_range(gemini_market, arm)]

    def family_row(label: str, out: pd.DataFrame, market: pd.DataFrame, arm: str) -> list[str]:
        return [label,
                judged(out, arm, "reported"),
                judged(out, arm, "suspects_collusion"),
                judged(out, arm, "suspects_test"),
                judged(out, arm, "verbal_accept"),
                skip(skips, "4b", label, "Private msgs /market",
                     "no message-count CSV for dg_haiku or dg_gpt41 (table3_extra.csv is "
                     "Gemini-only)"),
                index_range(market, arm)]

    rows.append(gemini_row("Gemini 3.8 Flash, D (5)", "D"))
    rows.append(family_row("Claude Haiku 5.5, D (3)", haiku, haiku_market, "D"))
    rows.append(family_row("GPT-4.1, D (3)", gpt41, gpt41_market, "D"))
    rows.append(family_row("GPT-4.1, F (3)", gpt41, gpt41_market, "F"))
    return rows, skips


def build_table5() -> tuple[list[list[str]], list[dict]]:
    """Step C: shared identity labels."""
    c = read_csv("c/c_by_run.csv")
    header = ["Label X", "Ask index (seeds 0/1/2)", "Mean", "Passes /3", "Private msgs /market",
              "Restated when asked in context /12", "Seller-hours mentioning the label"]
    rows = [header]
    skips: list[dict] = []
    rows.append(skip_row(skips, "5", "none (step A comms)", header,
                         "the step-A no-label baseline runs are not in report/data/c/"))
    for key, label in TABLE5_LABELS:
        sub = c[c["label"] == key].sort_values("seed")
        seeds = sub["seed"].tolist()
        if len(sub) != TABLE5_SEEDS or sub["seed"].duplicated().any():
            raise ValueError(f"c_by_run.csv: label {key!r} has seeds {seeds}; Table 5 needs "
                             f"{TABLE5_SEEDS} distinct seeds")
        passes = int(sub["passed"].astype(bool).sum())
        # The report's dagger: a passing seed that traded at or below one lot per hour.
        if (sub["passed"].astype(bool) & (sub["trades_per_round"] <= 1.0)).any():
            passes = f"{passes}{DAGGER}"
        rows.append([
            label,
            " / ".join(fmt2(v) for v in sub["ask_index"]),
            fmt2(sub["ask_index"].mean()),
            str(passes),
            str(int(round(sub["private_msgs"].mean()))),
            str(int(sub["incontext_repeats"].sum())),
            skip(skips, "5", label, "Seller-hours mentioning the label",
                 "seller-hours mentioning the label are not in c_by_run.csv"),
        ])
    return rows, skips


BUILDERS = {
    "2": ("Report and judge-label counts (Gemini)", build_table2),
    "3": ("Reports, replies, messaging and prices (Gemini)", build_table3),
    "4": ("GPT-4.1 sellers", build_table4),
    "4b": ("The plain offer across three seller families", build_table4b),
    "5": ("Step C: shared identity labels", build_table5),
}


def render_table(rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([lines[0], "|" + "---|" * len(rows[0])] + lines[1:])


def build_all() -> dict[str, tuple[list[list[str]], list[dict]]]:
    return {tid: builder() for tid, (_, builder) in BUILDERS.items()}


# ---------------------------------------------------------------- --check

# A number, with a leading '-' or U+2212 read as its sign unless it follows a digit ("0.12-0.61"
# is a range: the dash after "0.12" separates two positive numbers).
NUMBER = re.compile(r"(?:(?<![\d.])[-−])?\d+(?:\.\d+)?")


def norm(text: str) -> str:
    """Header or row-key text without markdown emphasis, code ticks or escapes; whitespace
    collapsed; lower case."""
    return " ".join(re.sub(r"[*_`\\]", "", text).split()).lower()


def cell_tokens(text: str) -> tuple[str, list[float]]:
    """(shape, numbers): the numbers in a cell (U+2212 read as a minus sign), and the cell with
    each number replaced by '#', with '$', '%' and whitespace dropped, lower case. A parenthesised
    part such as '(0.12-0.61)' stays in the shape, so its numbers are compared as their own token."""
    numbers = [float(m.group().replace(MINUS, "-")) for m in NUMBER.finditer(text)]
    shape = re.sub(r"[$%\s]", "", NUMBER.sub("#", text)).lower()
    return shape, numbers


def column_tolerance(header: str) -> float:
    """Largest difference still read as rounding: message-count means 0.5, indices and dollar
    amounts 0.005, counts 0 (they must be equal)."""
    h = norm(header)
    if "msgs" in h:
        return 0.5
    if "index" in h or h == "mean" or "$" in h:
        return 0.005
    return 0.0


def compare_cell(report: str, csv: str, tolerance: float) -> str:
    """'match' (identical text), 'match (rounding)' (same text around the numbers and every pair
    of numbers closer than the tolerance) or 'differ'."""
    if report == csv:
        return "match"
    report_shape, report_numbers = cell_tokens(report)
    csv_shape, csv_numbers = cell_tokens(csv)
    if report_shape != csv_shape or len(report_numbers) != len(csv_numbers):
        return "differ"
    for a, b in zip(report_numbers, csv_numbers):
        if a != b and not abs(a - b) < tolerance:
            return "differ"
    return "match (rounding)"


def parse_report_tables(text: str) -> dict[str, list[list[str]]]:
    """The markdown table just above each '*Table N.' caption line, as a list of rows (the first
    row is the header; the |---| separator row is dropped)."""
    lines = text.splitlines()
    tables: dict[str, list[list[str]]] = {}
    for i, line in enumerate(lines):
        m = re.match(r"^\*Table (\d+b?)\.", line)
        if not m:
            continue
        j = i - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        block = []
        while j >= 0 and lines[j].lstrip().startswith("|"):
            block.append(lines[j].strip())
            j -= 1
        rows = []
        for ln in reversed(block):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):  # drop the |---| row
                rows.append(cells)
        tables[m.group(1)] = rows
    return tables


@dataclass
class CheckResult:
    report_path: str
    per_table: dict[str, dict[str, int]] = field(default_factory=dict)
    n_columns: dict[str, int] = field(default_factory=dict)  # non-key columns per generated table
    match: int = 0
    rounding: list[dict] = field(default_factory=list)
    differences: list[dict] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)  # missing tables, columns, rows; duplicates
    unchecked: list[dict] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.differences and not self.problems

    def summary(self) -> str:
        line = (f"{self.match} match, {len(self.rounding)} match (rounding), "
                f"{len(self.differences)} differ, {len(self.unchecked)} unchecked")
        if self.problems:
            line += f", {len(self.problems)} table/column/row problem(s)"
        return line

    def to_json(self) -> dict:
        return {"report": self.report_path, "ok": self.ok, "summary": self.summary(),
                "per_table": self.per_table, "match_rounding": self.rounding,
                "differences": self.differences, "problems": self.problems,
                "unchecked": self.unchecked}


def keyed(rows: list[list[str]]) -> tuple[dict[str, list[str]], dict[str, int]]:
    """Rows by normalised key (first cell), leaving out keys that occur more than once, and those
    duplicate keys with their counts."""
    counts: dict[str, int] = {}
    for row in rows:
        counts[norm(row[0])] = counts.get(norm(row[0]), 0) + 1
    unique = {norm(row[0]): row for row in rows if counts[norm(row[0])] == 1}
    return unique, {key: n for key, n in counts.items() if n > 1}


def check_tables(generated: dict[str, tuple[list[list[str]], list[dict]]], report_text: str,
                 report_path: str = "report/REPORT.md") -> CheckResult:
    """Compare every generated table with the report's, by header name and row key."""
    result = CheckResult(report_path=report_path)
    report_tables = parse_report_tables(report_text)
    for tid, (rows, skips) in generated.items():
        stats = {"match": 0, "match (rounding)": 0, "differ": 0, "unchecked": 0}
        result.per_table[tid] = stats
        gen_header = rows[0]
        result.n_columns[tid] = len(gen_header) - 1
        rep = report_tables.get(tid)
        if not rep:
            result.problems.append(f"Table {tid}: no table above a '*Table {tid}.' caption in "
                                   f"{report_path}")
            continue
        rep_header = rep[0]
        reasons = {(s["row"], s["column"]): s["reason"] for s in skips}

        # Columns: matched by normalised header text; any header on one side only is a failure.
        gen_cols = {norm(h): i for i, h in enumerate(gen_header)}
        if len(gen_cols) != len(gen_header):
            raise ValueError(f"Table {tid}: the generator produced duplicate headers {gen_header}")
        rep_cols: dict[str, int] = {}
        for i, h in enumerate(rep_header):
            if norm(h) in rep_cols:
                result.problems.append(f"Table {tid}: column '{h}' appears more than once in the "
                                       f"report's header")
            else:
                rep_cols[norm(h)] = i
        for h in gen_header:
            if norm(h) not in rep_cols:
                result.problems.append(f"Table {tid}: column '{h}' is produced from the CSVs but "
                                       f"is not in the report's header")
        for h in rep_header:
            if norm(h) not in gen_cols:
                result.problems.append(f"Table {tid}: column '{h}' is in the report's header but "
                                       f"is not produced from the CSVs")
        if norm(rep_header[0]) != norm(gen_header[0]):
            result.problems.append(f"Table {tid}: the row-key column is '{rep_header[0]}' in the "
                                   f"report but '{gen_header[0]}' from the CSVs")

        # Rows: matched by normalised key; a key on one side only, or twice, is a failure.
        gen_rows, gen_dups = keyed(rows[1:])
        if gen_dups:
            raise ValueError(f"Table {tid}: the generator produced duplicate row keys "
                             f"{sorted(gen_dups)}")
        rep_rows, rep_dups = keyed(rep[1:])
        for key, n in rep_dups.items():
            original = next(r[0] for r in rep[1:] if norm(r[0]) == key)
            result.problems.append(f"Table {tid}: row '{original}' appears {n} times in the report "
                                   f"table; row keys must be unique")
        for key, row in rep_rows.items():
            if len(row) != len(rep_header):
                result.problems.append(f"Table {tid}, row '{row[0]}': {len(row)} cells but the "
                                       f"header has {len(rep_header)}")
            if key not in gen_rows:
                result.problems.append(f"Table {tid}, row '{row[0]}': in the report but not "
                                       f"produced from the CSVs")

        # Cells: by (row key, column name).
        for key, gen in gen_rows.items():
            if key in rep_dups:
                continue  # already a problem; there is no single report row to compare against
            if key not in rep_rows:
                result.problems.append(f"Table {tid}, row '{gen[0]}': produced from the CSVs but "
                                       f"not in the report")
                continue
            ref = rep_rows[key]
            for j, column in enumerate(gen_header[1:], start=1):
                if norm(column) not in rep_cols:
                    continue  # already a problem
                ri = rep_cols[norm(column)]
                want = ref[ri] if ri < len(ref) else "<missing>"
                got = gen[j]
                cell = {"table": tid, "row": gen[0], "column": column, "report": want, "csv": got}
                if got == NA:
                    cell["reason"] = reasons.get((gen[0], column), "not producible from the CSVs")
                    result.unchecked.append(cell)
                    stats["unchecked"] += 1
                    continue
                status = compare_cell(want, got, column_tolerance(column))
                stats[status] += 1
                if status == "match":
                    result.match += 1
                elif status == "match (rounding)":
                    result.rounding.append(cell)
                else:
                    result.differences.append(cell)
    return result


def print_check(result: CheckResult) -> None:
    for tid, s in result.per_table.items():
        print(f"Table {tid}: {s['match']} match, {s['match (rounding)']} match (rounding), "
              f"{s['differ']} differ, {s['unchecked']} unchecked")

    def where(c: dict) -> str:
        return f"Table {c['table']}, row '{c['row']}', column '{c['column']}'"

    if result.rounding:
        print("\nEqual after rounding (the report prints fewer decimals than the CSV value):")
        for c in result.rounding:
            print(f"  {where(c)}: match (rounding) report='{c['report']}' csv='{c['csv']}'")
    if result.differences or result.problems:
        print("\nDIFFERENCES:")
        for p in result.problems:
            print(f"  {p}")
        for c in result.differences:
            print(f"  {where(c)}: report='{c['report']}' csv='{c['csv']}'")
    if result.unchecked:
        print(f"\nUnchecked: {len(result.unchecked)} cell(s) the CSVs cannot produce "
              f"(printed as '{NA}'):")
        by_reason: dict[str, dict[tuple[str, str], list[str]]] = {}
        for c in result.unchecked:
            by_reason.setdefault(c["reason"], {}).setdefault((c["table"], c["row"]), []).append(
                c["column"])
        for reason, rows in by_reason.items():
            print(f"  - {reason}")
            for (tid, row), columns in rows.items():
                if len(columns) == result.n_columns.get(tid):
                    print(f"      Table {tid}, {row}: all {len(columns)} columns")
                else:
                    print(f"      Table {tid}, {row}: " + ", ".join(f"'{c}'" for c in columns))
    print(f"\n{result.summary()}")
    if result.ok:
        print(f"All producible cells match {result.report_path}")
    else:
        print(f"{len(result.differences) + len(result.problems)} failure(s) against "
              f"{result.report_path}")


def write_json(path: Path, generated: dict[str, tuple[list[list[str]], list[dict]]],
               result: CheckResult | None) -> None:
    """The tables, and either the check result or (without --check) every placeholder cell."""
    payload: dict = {"tables": {tid: {"title": BUILDERS[tid][0], "header": rows[0],
                                      "rows": rows[1:]}
                                for tid, (rows, _skips) in generated.items()}}
    if result is None:
        payload["unchecked"] = [{"table": tid, "row": s["row"], "column": s["column"],
                                 "reason": s["reason"]}
                                for tid, (_rows, skips) in generated.items() for s in skips]
    else:
        payload.update(result.to_json())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
                    newline="\n")
    print(f"(JSON written to {path})")


def run_check(generated: dict[str, tuple[list[list[str]], list[dict]]], report_path: Path,
              json_path: Path | None = None) -> int:
    result = check_tables(generated, report_path.read_text(encoding="utf-8"), str(report_path))
    print_check(result)
    if json_path is not None:
        write_json(json_path, generated, result)
    return 0 if result.ok else 1


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=None,
                        help="also write the tables to this file (e.g. report/build/tables.md)")
    parser.add_argument("--check", action="store_true",
                        help="diff the tables against the report; exit 1 on any difference")
    parser.add_argument("--report", type=Path, default=REPORT,
                        help="report to check against (default: report/REPORT.md)")
    parser.add_argument("--json", type=Path, default=None,
                        help="also write the tables (and, with --check, the check result, "
                             "including the 'unchecked' cells) to this JSON file")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    generated = build_all()
    parts = []
    for tid, (title, _) in BUILDERS.items():
        parts.append(f"### Table {tid}. {title}\n\n{render_table(generated[tid][0])}\n")
    markdown = "\n".join(parts)
    print(markdown)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(markdown, encoding="utf-8", newline="\n")
        print(f"\n(written to {args.out})\n")

    if args.check:
        return run_check(generated, args.report, args.json)
    if args.json:
        write_json(args.json, generated, None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
