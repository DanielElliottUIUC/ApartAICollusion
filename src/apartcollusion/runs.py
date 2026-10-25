"""
Reading finished harness runs for the D-G analysis (new sprint code).

A run directory holds experiment_metadata.json, auction_results.md (one JSON block per round), unified.log and
collusion_metrics.json. D-G runs add to the metadata `arm`, `scripted_seats`, `seat_mode`, `offer_hour` and
`offer_price`, and to each round record `scripted_offers`, `reports` and `buyer_notices` (README "D-G").
"""

import importlib.util
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

import numpy as np

REPO = Path(__file__).resolve().parents[2]
HARNESS = REPO / "third_party" / "llm-agent-collusion"

# Canonical arm order for tables and figures (README "D-G"); arms not listed here sort after these, by name.
ARM_ORDER = ["Base", "D", "D-hs", "D-hb", "D-hsb", "E", "F", "G-warn", "G-prec", "F-sham", "Base-hb"]


def _load_harness_module(name: str, rel: str):
    """Import one stdlib-only harness module by path (the harness's own package is named `src`, which clashes)."""
    spec = importlib.util.spec_from_file_location(name, HARNESS / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


# The harness's joint criterion (thresholds and last-third window), reused so D-G numbers can't drift from it.
joint_criterion_mod = _load_harness_module(
    "_harness_joint_criterion", "src/continuous_double_auction/evaluation/joint_criterion.py"
)
last_third = joint_criterion_mod.last_third
joint_criterion = joint_criterion_mod.joint_criterion


@dataclass
class Run:
    run_dir: Path
    metadata: dict[str, Any]
    metrics: dict[str, Any]
    rounds: list[dict[str, Any]]  # round records in round order

    @property
    def run_id(self) -> str:
        return self.run_dir.name

    @property
    def arm(self) -> Optional[str]:
        return self.metadata.get("arm")

    @property
    def seed(self) -> Optional[int]:
        return self.metadata.get("auction_config", {}).get("seed")

    @property
    def seller_ids(self) -> list[str]:
        return list(self.metadata.get("seller_ids", []))

    @property
    def scripted_seats(self) -> set[str]:
        return set(self.metadata.get("scripted_seats") or [])

    @property
    def llm_sellers(self) -> list[str]:
        return [s for s in self.seller_ids if s not in self.scripted_seats]

    @property
    def ce(self) -> float:
        return self.metrics["competitive_equilibrium_price"]

    @property
    def cartel(self) -> float:
        return self.metrics["joint_profit_maximization_price"]

    @property
    def hours(self) -> list[int]:
        return [r["round_number"] for r in self.rounds]

    def model_of(self, seller_id: str) -> Optional[str]:
        models = (self.metadata.get("resolved_models") or {}).get("sellers") or \
            self.metadata.get("auction_config", {}).get("seller_models", [])
        i = self.seller_ids.index(seller_id)
        return models[i] if i < len(models) else None

    def ask(self, seller_id: str, hour: int) -> Optional[float]:
        for r in self.rounds:
            if r["round_number"] == hour:
                v = r.get("seller_asks", {}).get(seller_id)
                return float(v) if is_num(v) else None
        return None

    def index(self, price: Optional[float]) -> Optional[float]:
        """Price -> 0 (competitive equilibrium) .. 1 (cartel price), the harness's scale."""
        span = self.cartel - self.ce
        return (price - self.ce) / span if is_num(price) and span else None


def is_num(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and not math.isnan(x)


def mean(xs: Sequence[Any]) -> Optional[float]:
    xs = [float(x) for x in xs if is_num(x)]
    return sum(xs) / len(xs) if xs else None


def load_rounds(run_dir: Path) -> list[dict[str, Any]]:
    """Round records from auction_results.md (same reader as posthoc_judge.load_rounds)."""
    text = (run_dir / "auction_results.md").read_text(encoding="utf-8")
    rounds = [json.loads(b) for b in re.findall(r"````json\n(.*?)\n````", text.replace("\r\n", "\n"), flags=re.S)]
    return sorted(rounds, key=lambda r: r.get("round_number", 0))


def load_run(run_dir: Path) -> Run:
    return Run(
        run_dir=run_dir,
        metadata=json.loads((run_dir / "experiment_metadata.json").read_text(encoding="utf-8")),
        metrics=json.loads((run_dir / "collusion_metrics.json").read_text(encoding="utf-8")),
        rounds=load_rounds(run_dir),
    )


def find_runs(results_dir: Path, warn: Callable[[str], None] = print) -> list[Run]:
    """Every finished run under results_dir that has an `arm` in its metadata (i.e. a D-G run)."""
    runs = []
    for meta in sorted(Path(results_dir).rglob("experiment_metadata.json")):
        run_dir = meta.parent
        missing = [f for f in ("auction_results.md", "collusion_metrics.json") if not (run_dir / f).is_file()]
        if missing:
            warn(f"skip {run_dir.name}: missing {', '.join(missing)} (run unfinished?)")
            continue
        run = load_run(run_dir)
        if not run.arm:
            warn(f"skip {run_dir.name}: no `arm` in experiment_metadata.json (not a D-G run)")
            continue
        runs.append(run)
    return runs


def arm_sort_key(arm: str) -> tuple[int, str]:
    return (ARM_ORDER.index(arm), "") if arm in ARM_ORDER else (len(ARM_ORDER), arm)


def cluster_bootstrap(
    clusters: Sequence[Sequence[float]], n_boot: int = 2000, seed: int = 0, level: float = 0.95
) -> tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Pooled mean over all observations, with a percentile CI from resampling whole clusters (runs = markets) with
    replacement. Sellers in one market talk to each other, so they are not independent (README "Design rules").
    Returns (estimate, lo, hi); (None, None, None) if there are no observations.
    """
    clusters = [np.asarray([float(v) for v in c], dtype=float) for c in clusters]
    clusters = [c for c in clusters if c.size]
    if not clusters:
        return None, None, None
    sums = np.array([c.sum() for c in clusters])
    counts = np.array([c.size for c in clusters])
    estimate = float(sums.sum() / counts.sum())
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(clusters), size=(n_boot, len(clusters)))
    boot = sums[idx].sum(axis=1) / counts[idx].sum(axis=1)
    alpha = (1 - level) / 2
    return estimate, float(np.quantile(boot, alpha)), float(np.quantile(boot, 1 - alpha))
