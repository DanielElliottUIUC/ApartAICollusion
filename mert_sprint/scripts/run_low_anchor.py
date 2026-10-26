"""Run Daniel's double-auction harness with the sellers' opening asks centred on ASK_CENTER instead of $97.50.

The low-anchor test (Oct 25): in the step-A market a pass mostly means sellers kept the seeded $97.50 opening ask.
Opening the book at the $90 benchmark asks whether a seller raises prices on its own. The harness has the setting
(ExperimentParams.initial_seller_ask_center) but no command-line flag, so this wrapper runs the harness's own
main() with that one default changed; no harness file is edited. Buyer bids keep their $82.50 centre.

    cd <ApartAICollusion>/third_party/llm-agent-collusion
    ASK_CENTER=90 uv run python <this repo>/scripts/run_low_anchor.py <simulation.py arguments>
"""

import os
import sys

sys.path.insert(0, os.getcwd())  # the harness root, so its src.* imports resolve as they do for simulation.py

from src.continuous_double_auction import simulation  # noqa: E402
from src.continuous_double_auction.cda_types import ExperimentParams  # noqa: E402

CENTER = float(os.environ["ASK_CENTER"])


class LowAnchorParams(ExperimentParams):  # a pydantic model: a subclass may override a field's default
    initial_seller_ask_center: float = CENTER


simulation.ExperimentParams = LowAnchorParams
sys.argv[0] = "simulation.py"
simulation.main()
