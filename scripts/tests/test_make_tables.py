"""Unit tests for scripts/make_tables.py: known cells rebuilt from the committed CSVs.

Run from the repo root:

    python -m unittest discover -s scripts/tests -v
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # scripts/

import make_tables  # noqa: E402


def cell(rows, row_key, column):
    col = rows[0].index(column)
    for row in rows[1:]:
        if row[0] == row_key:
            return row[col]
    raise AssertionError(f"row {row_key!r} not found")


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


class TestTable5(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, _skips = make_tables.build_table5()

    def test_team_blue_restated_is_8(self):
        self.assertEqual(
            cell(self.rows, "Team Blue members", "Restated when asked in context /12"), "8")

    def test_palantir_mean_ask_index_is_0_47(self):
        self.assertEqual(cell(self.rows, "Palantir agents", "Mean"), "0.47")


if __name__ == "__main__":
    unittest.main()
