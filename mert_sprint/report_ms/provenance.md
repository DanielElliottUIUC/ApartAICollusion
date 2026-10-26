# Provenance check: does the original Agrawal et al. harness seed a high opening?

VERDICT: YES. The original harness seeds a high opening. The defaults `initial_seller_ask_center = 97.5` and `initial_condition = True` are in the upstream code, and the sprint did not add them. The paper describes the same seeding, and its Figure 3 ask curves start near $96 to $97.

**Evidence**

1. **Daniel's provenance appendix and git history.**
   - REPORT.md Appendix B says `third_party/llm-agent-collusion/` was "copied from collusion_hackathon @ `d585a7b`". Its row on sprint changes to `cda_types.py` lists only the messaging/DM params, `DirectMessage`, the DM fields and the `SCRIPTED_SELLER` placeholder. It names no initial-condition fields.
   - The vendoring commit `3807b25` (2026-10-23) already holds `cda_types.py` lines 50-54, with `initial_seller_ask_center: float = 97.5`, `initial_seller_ask_spread: float = 2.5`, `initial_buyer_bid_center: float = 82.5`, `initial_buyer_bid_spread: float = 2.5` and `initial_condition: bool = True`. In the same commit, `simulation.py` lines 148-159 call `initialize_market` and then `market.set_initial_orders`.
   - On origin/main these lines sit at `cda_types.py` 54-58 and `simulation.py` 211-218, unchanged. `git log -L` on those lines returns only `3807b25`.

2. **Upstream repository (github.com/andyjliu/llm-agent-collusion, main).**
   - The repository has a single commit, `2bb2a7e22860160d1fddb5d2e5cb460cc6ec6aff`, "Initial commit", dated 2025-07-08 (api.github.com/repos/andyjliu/llm-agent-collusion/commits).
   - https://raw.githubusercontent.com/andyjliu/llm-agent-collusion/main/src/continuous_double_auction/cda_types.py, lines 33-37, has the same five defaults: ask center 97.5, spread 2.5, bid center 82.5, spread 2.5, `initial_condition = True`.
   - https://raw.githubusercontent.com/andyjliu/llm-agent-collusion/main/src/continuous_double_auction/simulation.py, lines 88-104, seeds the order book with these asks before round 1.
   - `util/misc.py`, lines 29-49, draws each ask from uniform(center − spread/2, center + spread/2). With the defaults that is $96.25 to $98.75. The vendored `initialize_market` is byte-identical to upstream (diff empty).
   - Neither the upstream nor the vendored `simulation.py` has a CLI flag that overrides these values.

3. **The paper (agrawal25.txt).**
   - Lines 93-101 read: "We observed that the bids/asks placed in the first round can significantly influence the trajectory of a trading session. … We controlled for this by generating a uniformly random bid (between $80 and $85) for each buyer and a uniformly random ask (between $95 and $100) for each seller at the start of each session. Then, we presented the pre-populated bid and ask queues to the agents in their prompts for the first round."
   - Appendix D, lines 940-952, shows a GPT-4.1 seller in hour 1 that sees an "ask queue … tightly clustered between $96.44 and $97.78", with "highest bid … $83.66", and that asks $97.56.
   - Figure 3, rendered from the upstream asset https://raw.githubusercontent.com/andyjliu/llm-agent-collusion/main/assets/avg_seller_ask.pdf, has round-1 average asks of about $96.5 to $97 for both communication arms, GPT-4.1 and all pressure arms. Two arms start lower, Mixed at about $96 and Claude-3.7-Sonnet at about $94.5. The competitive line is dashed at $90.

4. **One discrepancy to keep the report sentence exact.** The paper text gives the ask interval as $95 to $100 (spread 5). The shipped code defaults give $96.25 to $98.75 (spread 2.5). Both are centred on $97.50.

**Sentence for the report**

"The original harness of Agrawal et al. seeds the opening order book with seller asks centred on $97.50 (`cda_types.py` defaults, upstream commit 2bb2a7e). Their paper states that each seller's first ask is drawn uniformly from $95 to $100, and their Figure 3 ask curves start near $97, so their reported collusion also descends from a high opening price."

Files are in the session scratch folder (local, not in the repo):
- `cda_types.py`, `simulation.py` and `misc.py` (upstream copies)
- `misc_vendored.py` (vendored copy)
- `avg_seller_ask.pdf` (the upstream Figure 3 asset)
- `fig3-1.png` (its render)
