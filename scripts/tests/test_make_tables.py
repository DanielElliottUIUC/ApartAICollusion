"""Unit tests for scripts/make_tables.py: known cells rebuilt from the committed CSVs, and the
--check comparison (header mapping, rounding tolerance, duplicate rows, single-cell changes).

Run from the repo root with a Python that has pandas (e.g. the harness venv):

    python -m unittest discover -s scripts/tests -v
"""

import ast
import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/

import make_tables  # noqa: E402

REPORT_TEXT = make_tables.REPORT.read_text(encoding="utf-8")


def cell(rows, row_key, column):
    col = rows[0].index(column)
    for row in rows[1:]:
        if row[0] == row_key:
            return row[col]
    raise AssertionError(f"row {row_key!r} not found")


def replace_once(text, old, new):
    """Edit a copy of the report; the line being edited must occur exactly once."""
    assert text.count(old) == 1, f"{old!r} occurs {text.count(old)} times in REPORT.md"
    return text.replace(old, new)


# ---------------------------------------------------------------- known cells

class TestTable2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, _skips = make_tables.build_table2()

    def test_arms_in_report_order(self):
        self.assertEqual([r[0] for r in self.rows[1:]],
                         ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "G-warn", "G-prec",
                          "F-sham"])

    def test_d_reported_anyone_is_19(self):
        self.assertEqual(cell(self.rows, "D", "Reported anyone /20"), "19")

    def test_f_suspects_test_is_16(self):
        self.assertEqual(cell(self.rows, "F", "Suspects test /20"), "16")

    def test_gprec_suspects_test_is_14(self):
        self.assertEqual(cell(self.rows, "G-prec", "Suspects test /20"), "14")


class TestTable3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, _skips = make_tables.build_table3()

    def test_d_reported_seat5_with_per_seed_counts(self):
        self.assertEqual(cell(self.rows, "D", "Reported seat 5 /20 (per seed)"), "19 (4,3,4,4,4)")

    def test_gprec_private_msgs_is_0(self):
        self.assertEqual(cell(self.rows, "G-prec", "Private msgs"), "0")

    def test_base_hour3_ask_is_96_47(self):
        self.assertEqual(cell(self.rows, "Base", "Hour-3 ask, $"), "96.47")


class TestTable4(unittest.TestCase):
    def test_gwarn_suspects_test_is_3(self):
        rows, _skips = make_tables.build_table4()
        self.assertEqual(cell(rows, "G-warn", "Suspects test /12"), "3")


class TestTable4b(unittest.TestCase):
    def test_haiku_d_reported_seat5_is_3_of_12(self):
        rows, _skips = make_tables.build_table4b()
        self.assertEqual(cell(rows, "Claude Haiku 5.5, D (3)", "Reported seat 5"), "3/12")


class TestTable5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, _skips = make_tables.build_table5()

    def test_team_blue_restated_is_8(self):
        self.assertEqual(
            cell(self.rows, "Team Blue members", "Restated when asked in context /12"), "8")

    def test_palantir_mean_ask_index_is_0_47(self):
        self.assertEqual(cell(self.rows, "Palantir agents", "Mean"), "0.47")


class TestArmOrder(unittest.TestCase):
    def test_arm_order_is_a_copy_of_runs_py(self):
        """make_tables keeps its own ARM_ORDER (pandas-only); it must equal runs.ARM_ORDER."""
        source = (make_tables.REPO / "src" / "apartcollusion" / "runs.py").read_text(encoding="utf-8")
        for node in ast.parse(source).body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "ARM_ORDER" for t in node.targets):
                self.assertEqual(make_tables.ARM_ORDER, ast.literal_eval(node.value))
                return
        self.fail("ARM_ORDER not found in src/apartcollusion/runs.py")

    def test_script_does_not_import_apartcollusion(self):
        self.assertNotIn("apartcollusion", make_tables.__dict__)
        self.assertNotIn("from apartcollusion", Path(make_tables.__file__).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- label counts

class TestLabelCounts(unittest.TestCase):
    def frame(self, rate, n, n_ep=20):
        return pd.DataFrame({"x_rate": [rate], "x_n": [n], "n_seller_episodes": [n_ep]},
                            index=pd.Index(["D"], name="arm"))

    def test_count_uses_label_n_as_denominator(self):
        # 5 of 10 judged episodes; multiplying by n_seller_episodes (20) would give 10.
        self.assertEqual(make_tables.label_counts(self.frame(0.5, 10), "x")["D"], 5)
        self.assertEqual(make_tables.label_denominators(self.frame(0.5, 10), "x")["D"], 10)

    def test_null_label_n_falls_back_to_n_seller_episodes(self):
        self.assertEqual(make_tables.label_counts(self.frame(0.25, float("nan")), "x")["D"], 5)

    def test_non_integer_count_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "not a whole number"):
            make_tables.label_counts(self.frame(0.33, 20), "x")

    def test_empty_rate_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "x_rate is empty"):
            make_tables.label_counts(self.frame(float("nan"), 0), "x")


# ---------------------------------------------------------------- missing data

class TestMissingTable3Extra(unittest.TestCase):
    """A gap in table3_extra.csv must stop the script, not print a zero."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.data = Path(self.tmp.name) / "data"
        shutil.copytree(make_tables.DATA, self.data)
        self.extra_path = self.data / "dg" / "table3_extra.csv"
        self.extra = pd.read_csv(self.extra_path)

    def tearDown(self):
        self.tmp.cleanup()

    def build_with(self, extra):
        extra.to_csv(self.extra_path, index=False)
        with mock.patch.object(make_tables, "DATA", self.data):
            return make_tables.build_table3()

    def test_missing_seed_is_an_error(self):
        drop = (self.extra["arm"] == "G-prec") & (self.extra["seed"] == 4)
        with self.assertRaisesRegex(ValueError, r"arm 'G-prec': 4 run\(s\)"):
            self.build_with(self.extra[~drop])

    def test_missing_arm_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "arm 'F-sham': no rows"):
            self.build_with(self.extra[self.extra["arm"] != "F-sham"])

    def test_missing_arm_also_stops_table4b(self):
        self.extra[self.extra["arm"] != "D"].to_csv(self.extra_path, index=False)
        with mock.patch.object(make_tables, "DATA", self.data):
            with self.assertRaisesRegex(ValueError, "arm 'D': no rows"):
                make_tables.build_table4b()

    def test_empty_cell_is_an_error(self):
        extra = self.extra.copy()
        extra.loc[extra["arm"] == "E", "public_msgs"] = None
        with self.assertRaisesRegex(ValueError, r"arm 'E': empty cells .*public_msgs"):
            self.build_with(extra)


# ---------------------------------------------------------------- --check

class TestCompareCell(unittest.TestCase):
    def test_message_count_rounding(self):
        self.assertEqual(make_tables.compare_cell("58", "58.4", 0.5), "match (rounding)")
        self.assertEqual(make_tables.compare_cell("59", "58.8", 0.5), "match (rounding)")
        self.assertEqual(make_tables.compare_cell("59", "58.4", 0.5), "differ")

    def test_counts_must_be_equal(self):
        self.assertEqual(make_tables.compare_cell("19", "19", 0.0), "match")
        self.assertEqual(make_tables.compare_cell("18", "19", 0.0), "differ")

    def test_range_is_a_separate_token(self):
        self.assertEqual(make_tables.compare_cell("0.41 (0.12-0.61)", "0.41 (0.12-0.62)", 0.005),
                         "differ")
        self.assertEqual(make_tables.compare_cell("19 (4,3,4,4,4)", "19", 0.0), "differ")
        self.assertEqual(make_tables.compare_cell("19 (4,3,4,4,4)", "19 (4,4,3,4,4)", 0.0),
                         "differ")

    def test_unicode_minus_and_markers(self):
        self.assertEqual(make_tables.compare_cell("−0.41 (−0.53 to −0.21)",
                                                  "-0.41 (-0.53 to -0.21)", 0.005),
                         "match (rounding)")
        self.assertEqual(make_tables.compare_cell("−0.41", "0.41", 0.005), "differ")
        self.assertEqual(make_tables.compare_cell("7*", "7", 0.0), "differ")


class TestCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generated = make_tables.build_all()

    def check(self, text):
        return make_tables.check_tables(self.generated, text)

    def run_check_on(self, text):
        """run_check on a temporary copy of the report: (exit code, printed output)."""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "REPORT.md"
            path.write_text(text, encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = make_tables.run_check(self.generated, path)
        return code, out.getvalue()

    def test_committed_report_passes(self):
        result = self.check(REPORT_TEXT)
        self.assertEqual(result.problems, [])
        self.assertEqual(result.differences, [])
        self.assertEqual(len(result.rounding), 9)
        self.assertEqual(len(result.unchecked), 30)
        code, out = self.run_check_on(REPORT_TEXT)
        self.assertEqual(code, 0)
        self.assertIn("match (rounding), 0 differ, 30 unchecked", out)

    def test_swapped_headers_fail_naming_the_header(self):
        header = ("| Arm | Reported anyone /20 | Suspects collusion /20 | Suspects test /20 | "
                  "Verbal agreement /20 |")
        swapped = ("| Arm | Reported anyone /20 | Suspects test /20 | Suspects collusion /20 | "
                   "Verbal agreement /20 |")
        code, out = self.run_check_on(replace_once(REPORT_TEXT, header, swapped))
        self.assertEqual(code, 1)
        self.assertIn("column 'Suspects test /20'", out)
        self.assertIn("column 'Suspects collusion /20'", out)
        result = self.check(replace_once(REPORT_TEXT, header, swapped))
        self.assertTrue(result.differences)
        self.assertEqual({(d["table"], d["column"]) for d in result.differences},
                         {("2", "Suspects test /20"), ("2", "Suspects collusion /20")})

    def test_renamed_header_fails_naming_both_headers(self):
        old = ("| Arm | Reported seat 5 /20 (per seed) | Replied to seat 5 /20 | Private msgs | "
               "Public msgs | Hour-3 ask, $ | Ask index (seed range) | Trade index |")
        result = self.check(replace_once(REPORT_TEXT, old, old.replace("Trade index", "Trade idx")))
        self.assertFalse(result.ok)
        self.assertTrue(any("'Trade index' is produced from the CSVs but is not in the report"
                            in p for p in result.problems), result.problems)
        self.assertTrue(any("'Trade idx' is in the report's header but is not produced"
                            in p for p in result.problems), result.problems)

    def test_one_cell_change_is_the_only_difference(self):
        result = self.check(replace_once(REPORT_TEXT, "| D | 19 | 19 | 0 | 18 |",
                                         "| D | 18 | 19 | 0 | 18 |"))
        self.assertEqual(result.problems, [])
        self.assertEqual(result.differences, [{"table": "2", "row": "D",
                                               "column": "Reported anyone /20",
                                               "report": "18", "csv": "19"}])

    def test_duplicate_row_is_an_error_naming_the_key(self):
        row = "| D | 19 | 19 | 0 | 18 |"
        code, out = self.run_check_on(replace_once(REPORT_TEXT, row, row + "\n" + row))
        self.assertEqual(code, 1)
        self.assertIn("Table 2: row 'D' appears 2 times", out)


if __name__ == "__main__":
    unittest.main()
