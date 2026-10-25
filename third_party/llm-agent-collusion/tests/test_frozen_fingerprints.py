"""
Pins the frozen post-hoc judge fingerprints reported with the results (README "Judge": Claude Haiku 5.5, T = 0.1,
judge input version 3). A fingerprint hashes judge kind, model, temperature, template text (LF line endings) and
view, so this needs only the templates and constants: no run directories, no API calls.

If this test fails, the judge changed (model, temperature, a template, JUDGE_INPUT_VERSION or the view) and new
judge outputs would no longer be comparable with the reported ones. Don't update the expected values unless the
judge is deliberately re-frozen and every reported run is re-judged.

From third_party/llm-agent-collusion/:

    uv run python -m unittest tests.test_frozen_fingerprints -v
"""

import sys
import unittest
from pathlib import Path

HARNESS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HARNESS))

from src.continuous_double_auction.evaluation import posthoc_judge  # noqa: E402
from src.continuous_double_auction.evaluation.evaluate import (  # noqa: E402
    DEFAULT_EVAL_MODEL,
    DEFAULT_EVAL_TEMPERATURE,
)
from src.continuous_double_auction.evaluation.judge_fingerprint import JUDGE_INPUT_VERSION  # noqa: E402

FROZEN = {"seller": "837dec878d4f", "threads": "03b09030d699", "dg": "ce1b7e0487c9"}


class FrozenJudgeFingerprints(unittest.TestCase):
    def test_judge_config_is_the_frozen_one(self):
        self.assertEqual(DEFAULT_EVAL_MODEL, "anthropic/claude-haiku-5.5")
        self.assertEqual(DEFAULT_EVAL_TEMPERATURE, 0.1)
        self.assertEqual(JUDGE_INPUT_VERSION, 3)

    def test_seller_judge_messages_view(self):
        self.assertEqual(posthoc_judge.seller_fp("messages"), FROZEN["seller"])

    def test_thread_judge(self):
        self.assertEqual(posthoc_judge.thread_fp(), FROZEN["threads"])

    def test_dg_judge(self):
        self.assertEqual(posthoc_judge.dg_fp(), FROZEN["dg"])


if __name__ == "__main__":
    unittest.main()
