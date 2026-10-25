"""
ApartAICollusion sprint code (new work, Oct 2026; not part of the vendored harness).

D-G analysis layer:
    runs.py            read finished harness run directories (metadata, round records, metrics)
    market_indices.py  market-level ask / trade-price indices over LLM sellers only (scripted seats dropped)
    outcomes.py        one row per (run, LLM seller): offer acceptance, suspicion, reports; per-arm rates with
                       cluster-bootstrap CIs

Run from the repo root with the harness venv, e.g.

    PYTHONPATH=src uv run --project third_party/llm-agent-collusion python -m apartcollusion.outcomes --help
"""
