"""Rebuild the report's Tables 2, 3, 4, 4b and 5 from the analysis CSVs committed under report/data/.

    python scripts/make_tables.py                          print every table as markdown
    python scripts/make_tables.py --out report/build/tables.md
                                                            also write the tables to a file
    python scripts/make_tables.py --check                  also diff them, cell by cell, against the
                                                            tables in report/REPORT.md (found by their
                                                            caption lines "*Table 2." etc.); exit 1 if
                                                            any producible value differs

Sources
    Table 2   report/data/dg/outcomes_by_arm.csv
    Table 3   report/data/dg/table3_extra.csv (per-run counts extracted from the run logs by
              scripts/extract_dg_message_counts.py), dg/outcomes.csv (per seller-episode asks),
              dg/outcomes_by_arm.csv and dg/market_by_arm.csv
    Table 4   report/data/dg_gpt41/outcomes_by_arm.csv, dg_gpt41/market_by_arm.csv
    Table 4b  report/data/dg/ (Gemini D), dg_haiku/ (Haiku D), dg_gpt41/ (GPT-4.1 D and F)
    Table 5   report/data/c/c_by_run.csv

Conventions
    * Counts vs rates: in outcomes_by_arm.csv the `<label>_n` columns are denominators (episodes
      judged: 20 per Gemini arm, 12 per GPT-4.1/Haiku arm), so a count of positives is
      round(`<label>_rate` * n_seller_episodes). If a CSV ever made `_n` the count of positives
      (it would then track the rate instead of n_seller_episodes), label_counts() prefers `_n`.
    * LLM sellers only: market_by_arm.csv and table3_extra.csv cover the four LLM sellers; the
      scripted seat 5 is excluded everywhere except as a target of reports and messages.
    * "Reported seat 5", Gemini (Table 3, Table 4b): sum of reported_seat5 in table3_extra.csv -
      distinct sellers with at least one report naming seat 5, counted from the run logs. This is
      deliberately not report_is_scripted_seat in outcomes.csv, which looks only at each seller's
      FIRST report and so gives 19 (D-hb) and 18 (E) where the logs give 20 and 20: one D-hb
      seller and two E sellers first reported a peer, then reported seat 5. Likewise Table 2's
      "Reported anyone" for D-hsb is 8 while Table 3's seat-5 count is 7 (one seller reported
      only a peer).
    * "Reported seat 5", GPT-4.1 and Haiku (Tables 4 and 4b): no log-extract CSV exists for these
      families, so the count is `reported` (a report against anyone). In the offer arms D and F,
      seat 5 is the only party ever reported (false_report = 0). For Haiku D,
      report_is_scripted_seat reads 0 while the report's Table 4b says 3/12, which matches
      `reported`; for GPT-4.1 the two columns agree everywhere.
    * Cells the CSVs cannot produce are printed as "n/a from CSV" and skipped by --check, which
      lists them once: Table 4's "Msgs to seat 5 /market" and "Private msgs /market" (dg_gpt41 has
      no message-count CSV) and its "No comms (2 seeds)" row (the two messaging-off runs are not
      in the CSVs); Table 4b's "Private msgs /market" for Haiku and GPT-4.1 (table3_extra.csv is
      Gemini-only); Table 5's "none (step A comms)" baseline row (the step-A runs predate the
      label CSVs) and its "Seller-hours mentioning the label" column (not in c_by_run.csv).
    * Formatting, matching the report: counts as integers; means of message counts as integers
      when whole, one decimal otherwise; asks, indices and dollar changes with two decimals;
      negative numbers use the Unicode minus sign U+2212; an ask-index seed range is "(lo-hi)" and
      switches to "(lo to hi)" when a bound is negative; Table 3 shows the per-seed report counts
      only when the arm total is neither 0 nor n, and marks the placebo arms' reply counts
      (replies to the placebo note) with *; Table 5 means come from unrounded seed values, and a
      label's pass count carries a dagger when a passing seed traded at or below one lot per hour
      (trades_per_round <= 1.0).

No LLM API is called and no simulation is run; everything comes from the committed CSVs.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from apartcollusion.runs import arm_sort_key  # noqa: E402

DATA = REPO / "report" / "data"
REPORT = REPO / "report" / "REPORT.md"
NA = "n/a from CSV"
MINUS = "\u2212"  # U+2212, the minus sign the report uses
DAGGER = "\u2020"

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


def label_counts(df: pd.DataFrame, label: str) -> pd.Series:
    """Count of seller-episodes with the label true, per arm, from a *_by_arm.csv.

    `<label>_n` is the denominator in the committed CSVs (it equals n_seller_episodes on every
    row), so the count is round(rate * n); only if `_n` tracked the rate instead would it be the
    count of positives itself, and then it is preferred.
    """
    n_ep = df["n_seller_episodes"]
    from_rate = (df[f"{label}_rate"] * n_ep).round().astype(int)
    n_col = df[f"{label}_n"]
    if (n_col != n_ep).any() and (n_col == from_rate).all():
        return n_col.astype(int)
    return from_rate


def skip(skips: list, table: str, row: str, column: str, reason: str) -> str:
    """Register a not-producible cell and return its placeholder text."""
    skips.append({"table": table, "row": row, "column": column, "reason": reason})
    return NA


# ---------------------------------------------------------------- tables

def build_table2() -> tuple[list[list[str]], list[dict]]:
    """Report and judge-label counts out of 20 Gemini seller-episodes per arm."""
    df = by_arm(read_csv("dg/outcomes_by_arm.csv"))
    counts = {label: label_counts(df, label) for label in
              ("reported", "suspects_collusion", "suspects_test", "verbal_accept")}
    rows = [["Arm", "Reported anyone /20", "Suspects collusion /20", "Suspects test /20",
             "Verbal agreement /20"]]
    for arm in df.index:
        rows.append([arm] + [str(counts[l][arm]) for l in
                    ("reported", "suspects_collusion", "suspects_test", "verbal_accept")])
    return rows, []


def build_table3() -> tuple[list[list[str]], list[dict]]:
    """Reports, replies, messaging and prices (Gemini, LLM sellers only)."""
    extra = read_csv("dg/table3_extra.csv")
    outcomes = read_csv("dg/outcomes.csv")
    arms = by_arm(read_csv("dg/outcomes_by_arm.csv"))
    market = by_arm(read_csv("dg/market_by_arm.csv"))
    asks = outcomes.groupby("arm")[["ask_pre", "ask_change_post_offer"]].mean()

    def per_seed(arm: str, column: str) -> list[int]:
        sub = extra[extra["arm"] == arm].sort_values("seed")
        return sub[column].astype(int).tolist()

    rows = [[
        "Arm", "Reported seat 5 /20 (per seed)", "Replied to seat 5 /20", "Private msgs",
        "Public msgs", "Hour-3 ask, $", "Ask index (seed range)", "Trade index", "Ask change, $",
        "Passes /5",
    ]]
    for arm in arms.index:
        n_ep = int(arms.loc[arm, "n_seller_episodes"])
        per_seed_reports = per_seed(arm, "reported_seat5")
        total = sum(per_seed_reports)
        reported = str(total)
        if 0 < total < n_ep:  # per-seed breakdown only when the total is neither 0 nor n
            reported += " (" + ",".join(str(v) for v in per_seed_reports) + ")"
        replied = str(int(extra[extra["arm"] == arm]["replied_to_seat5_from_h4"].sum()))
        if arm in PLACEBO_REPLY_ARMS:
            replied += "*"
        rows.append([
            arm,
            reported,
            replied,
            fmt_msg_mean(extra[extra["arm"] == arm]["private_msgs_llm_total"].mean()),
            fmt_msg_mean(extra[extra["arm"] == arm]["public_msgs"].mean()),
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
    header = ["GPT-4.1 arm", "Msgs to seat 5 /market", "Private msgs /market",
              "Ask index (seed range)", "Verbal agreement /12", "Suspects collusion /12",
              "Suspects test /12", "Reported seat 5"]
    rows = [header]
    skips: list[dict] = []
    no_comms = skip(skips, "4", "No comms (2 seeds)", "(all columns)",
                    "the two messaging-off GPT-4.1 runs are not in report/data/dg_gpt41/")
    rows.append(["No comms (2 seeds)"] + [no_comms] * (len(header) - 1))
    for arm in [a for a in df.index if a in TABLE4_ARMS]:
        n_ep = int(df.loc[arm, "n_seller_episodes"])
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
            f"{counts['reported'][arm]}/{n_ep}",
        ]
        rows.append(cells)
    return rows, skips


def build_table4b() -> tuple[list[list[str]], list[dict]]:
    """The plain offer across three seller families, and GPT-4.1 F."""
    gemini_out = by_arm(read_csv("dg/outcomes_by_arm.csv"))
    gemini_market = by_arm(read_csv("dg/market_by_arm.csv"))
    extra = read_csv("dg/table3_extra.csv")
    haiku = by_arm(read_csv("dg_haiku/outcomes_by_arm.csv"))
    haiku_market = by_arm(read_csv("dg_haiku/market_by_arm.csv"))
    gpt41 = by_arm(read_csv("dg_gpt41/outcomes_by_arm.csv"))
    gpt41_market = by_arm(read_csv("dg_gpt41/market_by_arm.csv"))

    header = ["Sellers, arm (seeds)", "Reported seat 5", "Suspects collusion", "Suspects test",
              "Verbal agreement", "Private msgs /market", "Ask index (range)"]
    rows = [header]
    skips: list[dict] = []

    def gemini_row(label: str, arm: str) -> list[str]:
        return [label,
                f"{int(extra[extra['arm'] == arm]['reported_seat5'].sum())}/"
                f"{int(gemini_out.loc[arm, 'n_seller_episodes'])}",
                f"{label_counts(gemini_out, 'suspects_collusion')[arm]}/"
                f"{int(gemini_out.loc[arm, 'n_seller_episodes'])}",
                f"{label_counts(gemini_out, 'suspects_test')[arm]}/"
                f"{int(gemini_out.loc[arm, 'n_seller_episodes'])}",
                f"{label_counts(gemini_out, 'verbal_accept')[arm]}/"
                f"{int(gemini_out.loc[arm, 'n_seller_episodes'])}",
                fmt_msg_mean(extra[extra["arm"] == arm]["private_msgs_llm_total"].mean()),
                fmt_index_range(gemini_market.loc[arm, "ask_index_mean"],
                                gemini_market.loc[arm, "ask_index_min"],
                                gemini_market.loc[arm, "ask_index_max"])]

    def family_row(label: str, out: pd.DataFrame, market: pd.DataFrame, arm: str,
                   family: str) -> list[str]:
        n_ep = int(out.loc[arm, "n_seller_episodes"])
        return [label,
                f"{label_counts(out, 'reported')[arm]}/{n_ep}",
                f"{label_counts(out, 'suspects_collusion')[arm]}/{n_ep}",
                f"{label_counts(out, 'suspects_test')[arm]}/{n_ep}",
                f"{label_counts(out, 'verbal_accept')[arm]}/{n_ep}",
                skip(skips, "4b", label, "Private msgs /market",
                     "no message-count CSV for dg_haiku or dg_gpt41 (table3_extra.csv is "
                     "Gemini-only)"),
                fmt_index_range(market.loc[arm, "ask_index_mean"],
                                market.loc[arm, "ask_index_min"], market.loc[arm, "ask_index_max"])]

    rows.append(gemini_row("Gemini 3.8 Flash, D (5)", "D"))
    rows.append(family_row("Claude Haiku 5.5, D (3)", haiku, haiku_market, "D", "haiku"))
    rows.append(family_row("GPT-4.1, D (3)", gpt41, gpt41_market, "D", "gpt41"))
    rows.append(family_row("GPT-4.1, F (3)", gpt41, gpt41_market, "F", "gpt41"))
    return rows, skips


def build_table5() -> tuple[list[list[str]], list[dict]]:
    """Step C: shared identity labels."""
    c = read_csv("c/c_by_run.csv")
    header = ["Label X", "Ask index (seeds 0/1/2)", "Mean", "Passes /3", "Private msgs /market",
              "Restated when asked in context /12", "Seller-hours mentioning the label"]
    rows = [header]
    skips: list[dict] = []
    baseline = skip(skips, "5", "none (step A comms)", "(all columns)",
                    "the step-A no-label baseline runs are not in report/data/c/")
    rows.append(["none (step A comms)"] + [baseline] * (len(header) - 1))
    for key, label in TABLE5_LABELS:
        sub = c[c["label"] == key].sort_values("seed")
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

def parse_report_tables(text: str) -> dict[str, list[list[str]]]:
    """The markdown table just above each '*Table N.' caption line, as a list of rows."""
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


def run_check(generated: dict[str, tuple[list[list[str]], list[dict]]],
              report_path: Path) -> int:
    report_tables = parse_report_tables(report_path.read_text(encoding="utf-8"))
    diffs: list[str] = []
    for tid, (rows, _skips) in generated.items():
        rep = report_tables.get(tid)
        if rep is None:
            diffs.append(f"Table {tid}: no '*Table {tid}.' caption found in {report_path}")
            continue
        rep_rows = {r[0]: r for r in rep[1:]}
        gen_rows = {r[0]: r for r in rows[1:]}
        for row_key in rep_rows:
            if row_key not in gen_rows:
                diffs.append(f"Table {tid}, row '{row_key}': not produced from the CSVs")
        compared = matches = 0
        for row_key, gen in gen_rows.items():
            if row_key not in rep_rows:
                diffs.append(f"Table {tid}, row '{row_key}': not in the report")
                continue
            ref = rep_rows[row_key]
            for col in range(1, max(len(ref), len(gen))):
                got = gen[col] if col < len(gen) else "<missing>"
                want = ref[col] if col < len(ref) else "<missing>"
                if got == NA:
                    continue  # registered as not producible; listed once below
                compared += 1
                if got == want:
                    matches += 1
                else:
                    column = rows[0][col] if col < len(rows[0]) else f"column {col}"
                    diffs.append(f"Table {tid}, row '{row_key}', column '{column}': "
                                 f"report='{want}' csv='{got}'")
        print(f"Table {tid}: {matches}/{compared} producible cells match")
    skipped = [s for _tid, (_rows, skips) in generated.items() for s in skips]
    if skipped:
        print("\nNot producible from the CSVs (skipped by the check):")
        reasons: dict[str, list[str]] = {}
        for s in skipped:
            where = f"Table {s['table']}, {s['row']}"
            if s["column"] != "(all columns)":
                where += f", column '{s['column']}'"
            reasons.setdefault(s["reason"], []).append(where)
        for reason, cells in reasons.items():
            print(f"  - {reason}")
            for cell in cells:
                print(f"      {cell}")
    if diffs:
        print("\nDIFFERENCES:")
        for d in diffs:
            print(f"  {d}")
        print(f"\n{len(diffs)} difference(s) between the CSVs and {report_path}")
        return 1
    print(f"\nAll producible cells match {report_path}")
    return 0


# ---------------------------------------------------------------- main

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=None,
                        help="also write the tables to this file (e.g. report/build/tables.md)")
    parser.add_argument("--check", action="store_true",
                        help="diff the tables against report/REPORT.md; exit 1 on any difference")
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
        return run_check(generated, REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
