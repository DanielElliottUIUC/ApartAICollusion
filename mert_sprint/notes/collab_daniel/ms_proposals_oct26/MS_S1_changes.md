# Set 1: proposed changes to Report v2 (60c34d4)

Proposed by M.S. for D.E. to accept or decline (content is frozen on D.E.'s side, so every change is a suggestion). MS_S1.diff applies with `git apply` to report/REPORT.md at 60c34d4; MS_S1_tracked.pdf shows every change in place (red struck = removed, blue = added, grey Cn = change id). C83, C84 and C86 to C90 carry Mert's rulings (Appendix B cut to four sentences, Tables D2a/D2b, Table 1 and Author Contributions removed, Code and Data shortened, section 3.3 shortened to measures and statistics); C85 is his request (Related Work as one paragraph).

## C1 (line 14, phrasing)

"Takes the bait" is a figure of speech; "accepts" states the act.

Before:

> reports whoever takes the bait. We test it

After:

> reports whoever accepts. We test it

## C2 (line 14, consistency)

The same sentence writes its other counts as digits.

Before:

> yet 7 also wrote back agreeing, six stating an aim

After:

> yet 7 also wrote back agreeing, 6 stating an aim

## C3 (line 14, consistency)

The colon hung an explanation rather than a list (R22), the agreed wording names the criterion, and the abstract writes its other counts as digits.

Before:

> Price evidence is weak by construction: the baseline met our price criterion in one of five seeds

After:

> Price evidence is weak by construction. The baseline met the joint high-price and trade criterion in 1 of 5 seeds

## C4 (line 14, consistency)

The abstract never defines "honeypot" and calls it the undercover offer everywhere else, which also keeps the claim to this study.

Before:

> A honeypot offer exposed double-dealing

After:

> The undercover offer exposed double-dealing

## C5 (line 18, phrasing)

Same figure of speech as in the abstract, replaced the same way.

Before:

> and reports whoever takes the bait [Hammond et al., 2025; Wehner and Kraprayoon, 2026]

After:

> and reports whoever accepts [Hammond et al., 2025; Wehner and Kraprayoon, 2026]

## C6 (line 22, reader)

Figure 1 is where the reader first meets seat 5, so the caption says what it is.

Before:

> Four LLM sellers, scripted seat 5 and five LLM buyers trade for 15 hours

After:

> Four LLM sellers, a scripted fifth seller (seat 5) and five LLM buyers trade for 15 hours

## C7 (line 22, reader)

A reader does not know the initials, and figure credit is already in Author Contributions.

Before:

> with no effect in the run. (Figure: M.S.)

After:

> with no effect in the run.

## C85 (line 28, owner request)

Owner request: the three related-work paragraphs become one connected paragraph, with the bold run-ins kept as signposts; every citation and claim stays, and C8's fix to the Patil and Hoze sentence is folded in.

Before:

> **Collusion, offers and monitoring.** LLM pricing agents collude without instruction [Fish et al., 2026], DeepSeek-R1 reasoning agents in a pricing duopoly price above the competitive level even when told not to collude [Riemer et al., 2026], heterogeneity in patience or data access makes collusion fragile while model-size differences stabilize it [Keppo et al., 2026], and mixing models does not by itself reduce it [Lee, 2026]. Most agents accept secret collusion tools they call unfair [Zeng and Rudzicz, 2026], whistleblowing varies by model family and prompt [Agrawal et al., 2026], Wehner and Kraprayoon [2026] list fake collusion proposals as honeypots and cite an industry study in which honeypot warnings cut successful attacks from 20% to 3%, and announced monitoring halved Gemini's sabotage success [Radev et al., 2026].
> 
> **Text against price.** Text and action evidence diverge [Nakamura et al., 2026], price-level audits can be blind by construction [Xu et al., 2026], an LLM screen flags collusive content in firms' communications without measuring price effects [Azevedo et al., 2026], LLM double auctions anchor on the first offer [Struski et al., 2026] or a reference price [Hantel, 2026], and telling enforced collusion from high prices that no one enforces needs a forced-deviation test [Tran and Yu, 2026].
> 
> **Concurrent entries in this sprint** (not peer reviewed). In this harness, Douglas [2026] finds with a scripted undercover seller and a unique competitive price that the opening book, not chat, sets trade prices, and Patil and Hoze [2026] that GPT-4.1 sellers' first ask predicts the session price; in a Bertrand game, Adlakha and Adlakha [2026] find agents that report an undercover firm while fixing prices with their peer.

After:

> **Collusion and its countermeasures.** LLM pricing agents collude without being told to [Fish et al., 2026], and DeepSeek-R1 reasoning agents in a pricing duopoly price above the competitive level even when told not to [Riemer et al., 2026]. Differences in patience or data access make such collusion fragile, differences in model size stabilize it [Keppo et al., 2026], and mixing models does not by itself reduce it [Lee, 2026]. How these agents respond to offers and oversight varies as much. Most accept secret collusion tools that they themselves call unfair [Zeng and Rudzicz, 2026], and whether they blow the whistle depends on the model family and the prompt [Agrawal et al., 2026]. Wehner and Kraprayoon [2026] list fake collusion proposals among honeypots and cite an industry study in which honeypot warnings cut successful attacks from 20% to 3%, and announced monitoring halved Gemini's sabotage success [Radev et al., 2026]. **What counts as evidence.** Whether such measures work depends on what one measures. Text and action evidence diverge [Nakamura et al., 2026], audits of price levels can be blind by construction [Xu et al., 2026], and an LLM screen that flags collusive content in firms' communications does not measure price effects [Azevedo et al., 2026]. Prices also depend on where trading starts, since LLM double auctions anchor on the first offer [Struski et al., 2026] or on a reference price [Hantel, 2026], and telling enforced collusion from high prices that no one enforces needs a forced-deviation test [Tran and Yu, 2026]. **Concurrent sprint entries** (not peer reviewed) bear directly on our design. In this harness, Douglas [2026] finds, with a scripted undercover seller and a unique competitive price, that the opening book rather than chat sets trade prices, and Patil and Hoze [2026] find that GPT-4.1 sellers' first ask predicts the session price. In a Bertrand game, Adlakha and Adlakha [2026] find agents that report an undercover firm while fixing prices with their peer.

## C9 (line 38, reader)

Some runs used Claude Haiku 5.5 or GPT-6 Luna buyers (Table 1, Appendix D.4), and "vendored" is software jargon the reader does not need.

Before:

> Buyers are GPT-4.1-mini agents, as the vendored rule-based buyer always bids about $80

After:

> Buyers are GPT-4.1-mini agents unless stated otherwise, because the harness's own rule-based buyer always bids about $80

## C10 (line 42, phrasing)

Gives the caption sentence a verb instead of a fragment hung off a colon.

Before:

> Every arm: four Gemini 3.8 Flash sellers and scripted seat 5,

After:

> Every arm has four Gemini 3.8 Flash sellers and scripted seat 5,

## C11 (line 42, consistency)

Right after "no prohibition notice", "the notice" reads as the prohibition notice; the figure's row label is "Prompt notice".

Before:

> The notice is in every seller's prompt from hour 1

After:

> The prompt notice is in every seller's prompt from hour 1

## C12 (line 44, reader)

This is the first use of "prohibition notice" and the body never says what it is; "did not survive" is a figure of speech.

Before:

> and no prohibition notice, since collusion did not survive it in pilots (Appendix D.8)

After:

> and no prohibition notice (a prompt statement that coordinating prices is prohibited; Appendix C), since pilot markets did not collude under it (Appendix D.8)

## C13 (line 44, phrasing)

The colon hangs two clauses, not a list (R22).

Before:

> Figure 2 lays out the ten arms: Base gets the placebo note

After:

> Figure 2 lays out the ten arms. Base gets the placebo note

## C91 (line 46, owner)

Owner ruling: the heading says what the section now holds.

Before:

> ### 3.3 Other runs, outcomes and statistics

After:

> ### 3.3 Measures and statistics

## C88 (line 48, owner)

Owner ruling: section 3.3 keeps what the results need (the two markets, the measures, the judge, the statistics) at about half the length; Appendix D lists every batch and A.2 carries the proxy note.

Before:

> Table 1 lists the runs behind Section 4 (shared-label, buyer-probe, pilot and 30-hour runs: Appendices D.1, D.7, D.8). A **report** names seat 5 in the report action; a **reply** is a private message to seat 5 from hour 4 on, hand-coded as agreeing to or declining the offered price; **feigned agreement** is a report plus an agreeing reply. A frozen post-hoc judge, Claude Haiku 5.5, labels each seller-hour, private messages included, for verbal agreement (agreeing with or echoing any peer's price proposal, so Base reaches 20 of 20), verbal rejection, suspected collusion and suspected test (blind second-model agreement κ = 0.70 to 1.0; Appendix A.2, item 9). Contrasts are exact permutation tests over markets, and none survives Holm correction, so every result is directional (Appendix A.2, item 1).

After:

> Section 4 draws on two markets. Besides the undercover market of Figure 1, we ran a 4+4 market with no scripted seat and no report action, from the default $97.50 opening, from a $90 opening and with the competitive price pinned at $90. Every run lasts 15 hours, and Appendix D lists every batch with its seeds. A **report** names seat 5 in the report action, a **reply** is a private message to seat 5 from hour 4 on, hand-coded as agreeing to or declining the offered price, and **feigned agreement** is a report plus an agreeing reply. A frozen post-hoc judge, Claude Haiku 5.5, labels each seller-hour, private messages included, for verbal agreement (echoing any peer's price, so Base reaches 20 of 20), verbal rejection, suspected collusion and suspected test, with blind second-model agreement of κ = 0.70 to 1.0. Contrasts are exact permutation tests over markets. None survives Holm correction, so every result is directional (Appendix A.2, items 1 and 9).

## C87 (line 50, owner)

Owner ruling, agreed with D.E.: Table 1 goes; the figures and Appendix D carry the runs, and C88 keeps the market definitions and the proxy note from its caption.

Before:

> | Sellers | Market | Arms (seeds per arm) | By |
> |---------------------------|-----------------|------------------------------------------------|--------|
> | Gemini 3.8 Flash | Undercover | The ten arms (5); D with the offer at $99 (5) | D.E. |
> | GPT-4.1 | Undercover | Base, D, E, G-warn, F (3); D with the offer at $99 (3); messaging off with five LLM sellers (2) | D.E. |
> | Claude Haiku 5.5 | Undercover | D (3) | D.E. |
> | Gemini 3.8 Flash | 4+4 | Messaging on, off, on with the prohibition notice, on with the warning (3) | D.E. |
> | GPT-5.6 Sol, GPT-6 Luna, Grok 4.7, Claude Haiku 5.5 | 4+4 | Messaging on, off (3 to 6; Table D6) | M.S. |
> | GPT-5.6 Sol, GPT-6 Luna, Gemini 3.8 Flash | 4+4 opened at $90 | Messaging on, off (3; Luna off only; Gemini also on from $97.50); pre-specified test of Sol from $97.50 against $90 (6 pairs) | M.S. |
> | Gemini 3.8 Flash; GPT-4.1 (4+4 only) | 4+4 and undercover, $90 pinned | 4+4: messaging on, off; undercover: Base, D, G-warn, messaging off with five LLM sellers (3) | D.E. |
> | GPT-5.6 Sol, GPT-6 Luna, Gemini 3.8 Flash | 4+4, $90 pinned | Messaging on, off (3) | M.S. |
> 
> *Table 1. Runs, 15 hours each. Undercover: the 5+5 market of Figure 1; 4+4: no scripted seat or report action; pinned: one seller's cost and one buyer's value at $90 (two each in 5+5). M.S.'s runs used a proxy that sets no temperature or seed, some with Claude Haiku 5.5 or GPT-6 Luna buyers, and a second serving route for Gemini (Appendix A.2, items 12 to 14; Tables D6 to D9).*

After:

> (removed)

## C16 (line 69, reader)

The reader cannot tell that Mia is the scripted seat 5.

Before:

> I undercut both Raj and Mia". We read this

After:

> I undercut both Raj and Mia" (Mia is seat 5). We read this

## C17 (line 73, phrasing)

The colon hung a conclusion, not a list (R22).

Before:

> none raised its ask by $1 or more: reporting did not depend

After:

> none raised its ask by $1 or more. Reporting therefore did not depend

## C18 (line 79, consistency)

Elsewhere replies count sellers (Table D3: 7 of 12 wrote at $99), so "10 replies" reads as 10 sellers.

Before:

> At $99 all 10 replies declined

After:

> At $99 all 10 messages to seat 5, from 7 sellers, declined

## C19 (line 79, consistency)

Every other range runs from low to high, as Table D3 gives this one.

Before:

> (ask index −0.21 to −0.53)

After:

> (ask index −0.53 to −0.21)

## C20 (line 81, reader)

A reader does not know the initials, and figure credit is already in Author Contributions.

Before:

> checked by a second model. (Figure: M.S.)

After:

> checked by a second model.

## C21 (line 85, consistency)

The count is of sellers, and the paper counts reports separately (115 at $96).

Before:

> drew 12 of 20 reports (p = 0.29 against D)

After:

> drew reports from 12 of 20 sellers (p = 0.29 against D)

## C22 (line 85, consistency)

D-hb has the plain offer plus the buyer plea (Table D1), so "the buyer's plea alone" misdescribes the arm.

Before:

> a human buyer's plea alone 20 of 20, and both 7 of 20

After:

> the plain offer with a human buyer's plea 20 of 20, and both pleas 7 of 20

## C23 (line 85, consistency)

The authors chose the any-report count for the pooled plea test (39 of 40 against 19 of 40, p = 0.002), the definition Appendix D.1 and Figure 4a already use.

Before:

> pooled, first reports naming seat 5 fell from 38 of 40 to 19 of 40 with the seller plea (exact stratified p = 0.003; exploratory)

After:

> pooled, sellers reporting seat 5 fell from 39 of 40 to 19 of 40 with the seller plea (exact stratified p = 0.002; exploratory)

## C24 (line 91, consistency)

American spelling.

Before:

> Base's seed range (grey,

After:

> Base's seed range (gray,

## C25 (line 93, phrasing)

Without the comma the clause first reads as "offer reporting".

Before:

> and with the offer reporting stayed at 20 of 20.

After:

> and with the offer, reporting stayed at 20 of 20.

## C26 (line 99, phrasing)

The colon hung a reason, not a list (R22).

Before:

> could hardly have shown it: they hold or fall from the opening ask

After:

> could hardly have shown it, because they hold or fall from the opening ask

## C27 (line 99, reader)

The runs are named by model and route, not by author, and "our" includes both authors.

Before:

> only M.S.'s Sol sellers and his Gemini sellers on a second route separated with messaging (3 of 3 passes against 1 of 3), and 4 of our 9 pinned undercover markets

After:

> only GPT-5.6 Sol sellers and Gemini sellers on the second serving route separated with messaging (3 of 3 passes against 1 of 3), and 4 of the 9 pinned undercover markets

## C28 (line 103, consistency)

Talk did coordinate prices at $90 (Gemini) and below $90 (Grok), so the agreed framing puts the divergence between talk and the criterion; Figure D5 is otherwise never cited.

Before:

> Talk and price diverged throughout.

After:

> Talk and the joint criterion diverged throughout (Figure D5).

## C89 (line 111, owner)

Owner ruling: everything will sit in one repository, so the section needs four sentences, not directory listings; the prereg timing and the quote sources stay, and the info-hazard note moves to A.4 (C90).

Before:

> - **Code repository:** https://github.com/DanielElliottUIUC/ApartAICollusion. It holds the vendored harness, the sprint modifications (Appendix B), the undercover-market code, the frozen texts in `configs/texts/`, the seat-5 replay paths in `configs/replay/`, the analysis code in `src/apartcollusion/` and `scripts/`, and the run viewer in `viewer/`.
> - **Data.** Summary CSVs behind every number: the Gemini undercover market in `report/data/dg/` (`outcomes.csv`, `outcomes_by_arm.csv`, `market_by_run.csv`, `market_by_hour.csv`, `market_by_arm.csv`, `table3_extra.csv`, `permutation_tests.csv`, `fig_report_and_feign_cells.csv`, `judge_vs_price.csv`, `market_structure.csv`), the GPT-4.1 and Haiku replications in `report/data/dg_gpt41/` and `report/data/dg_haiku/`, the $99 offers in `report/data/dg_gemini_99/` and `report/data/dg_gpt41_99/`, the warning in the 4+4 market in `report/data/a_warn/runs.csv`, the pinned-price markets in `report/data/pinned/` (`pinned_a_runs.csv`, `pinned_a_gpt41_runs.csv`, `pinned_dg_runs.csv` and the shut-out tables beside them), the positive control, prohibition-notice and buyer-probe runs in `report/data/a/step_a_and_probes.csv`, the shared-label markets in `report/data/c/`, and the judge agreement check in `report/data/dg/judge_handcheck.md`. The READMEs in `report/data/a_warn/`, `dg_gpt41_99/`, `dg_gemini_99/` and `pinned/` give run commands and definitions. Raw run logs of our runs are not in the repository; Table D11 names the run folder and hour of every quote.
> - **M.S.'s runs and figures.** His run folders, each with `collusion_metrics.json`, `unified.log` and one file per agent, are under `mert_sprint/experiments/runs/` (the pinned-price runs in `box/pinned90/` and, for Gemini, `shard2/pinned90/`, summarised in `mert_sprint/notes/pinned90_results.md` and `pinned90_results_gemini.md`; the pre-specified test in `shard2/prereg_anchor/`), with his proxy and run scripts. The pre-specified protocol, its result and the result script are `mert_sprint/report_ms/prereg_sol_anchor.md`, `mert_sprint/report_ms/prereg_result.md` and `mert_sprint/report_ms/scripts/prereg_result.py`; the protocol was first committed in M.S.'s private repository (commit c5a14aa) before the runs, and the copy here was committed after them. Figures 1, 4 and 5 are his designs, redrawn at print size by adapted copies of his scripts in `scripts/figures/ms/` (each crediting him and naming its source in `mert_sprint/report_ms/scripts/`; Figure 4b adds his GPT-4.1 precedent and $99 rows); Figures D4 and D5 are his (`report/figures/ms_*.png`, made by the scripts in `mert_sprint/report_ms/scripts/`); and his supplement, with about 30 further figures, is `mert_sprint/report_ms/supplement/build/supplement.pdf`.
> - **Figures.** Figures 2 and 3 and Figures D1 to D3 are made by `scripts/figures/`, with provenance in `report/figures/README.md` and the `.caption.txt` file beside each figure.
> - **Preexisting code** is marked in Appendix B and in the repository README.
> - **Info-hazard note.** The plain offer, the warning, the precedent, the sham history and the placebo note are reproduced in Appendix C. The human-persona seller plea and the human buyer's plea model how to manipulate an agent with fabricated human distress; this report describes them without quoting them, so that their wording is not easy to reuse from it; the run files are in `configs/texts/` of the repository. We report counts and representative examples, not an optimized playbook, and we did not iterate any wording to raise acceptance.

After:

> All code, the frozen prompt texts, the summary data behind every number and the scripts for every figure are public at https://github.com/DanielElliottUIUC/ApartAICollusion, with the run folders of the frontier-model, opening-price and pinned-price experiments. Raw logs of the undercover-market runs are not public, and Table D11 names the run and hour of every quote. The pre-specified protocol was committed in a private repository before its runs (commit c5a14aa), and its public copy was added afterwards. Appendix B marks the preexisting code, and the two plea texts are described but not quoted, for the reason given in Appendix A.4.

## C86 (line 118, owner)

Owner ruling: the title footnote already states equal contribution, so the Author Contributions section is not needed; it frees counted space for results.

Before:

> ## Author Contributions
> 
> Both authors contributed equally.
> 
> - **D.E.:** research question; design of the positive control, the undercover market and its arms, the replications, the $99 offers, the warning in the 4+4 market and the pinned-price markets; orchestration of the coding agents; the OpenRouter positive-control, buyer-probe, shared-label, undercover, GPT-4.1, Haiku, $99, warning and pinned-price runs; the post-hoc judge and the agreement check; the re-analyses of §4.5 and Appendix D.9; analysis; Figures 2 and 3 and Figures D1 to D3; this report.
> - **M.S.:** the subscription proxy; the frontier-model runs (GPT-5.6 Sol, GPT-6 Luna, Grok 4.7), including Sol under GPT-4.1-mini buyers, Sol and Luna from a $90 opening, and Sol, Luna and Gemini with a pinned competitive price; the Haiku-buyer Gemini and Haiku-seller runs; the low-opening rerun of the Gemini market and its route control; the pre-specified opening-price test and its protocol; the Grok 4.7 judge for his runs; the audit and rerun of the rate-limited runs; a fix for Luna prompt truncation on Windows; the Bertrand duopoly matrix; the designs of Figures 1, 4 and 5, Figures D4 and D5 and his supplement; the report skeleton, its statistics paragraph and its bibliography. D.E. declined M.S.'s offer to build components of the undercover market, so no code of that market is his.

After:

> (removed)

## C36 (line 162, consistency)

Matches the any-report plea test chosen for the whole report.

Before:

> the pooled plea test (p = 0.003)

After:

> the pooled plea test (p = 0.002)

## C37 (line 168, phrasing)

Two independent clauses were joined by a comma alone.

Before:

> No seller in a market is untreated, sellers can discuss the offer with each other, so

After:

> No seller in a market is untreated, and sellers can discuss the offer with each other, so

## C38 (line 169, reader)

"Communication gate" is internal shorthand; the parenthesis already gives the evidence.

Before:

> GPT-4.1 has no communication gate in this market

After:

> GPT-4.1 sellers met the criterion in this market without messaging

## C39 (line 170, consistency)

American spelling.

Before:

> explicit pretence in one

After:

> explicit pretense in one

## C40 (line 172, consistency)

American spelling.

Before:

> this buyer's behaviour

After:

> this buyer's behavior

## C41 (line 172, reader)

Names the runs by the table that holds them instead of by author.

Before:

> M.S.'s frontier runs used Haiku or Luna buyers

After:

> The frontier runs of Table D6 used Haiku or Luna buyers

## C42 (line 173, reader)

Names the runs by the label Table 1 gives them instead of by author.

Before:

> **M.S.'s proxy changes settings.** His runs send every seat

After:

> **The subscription proxy changes settings.** The proxy runs (Table 1) send every seat

## C43 (line 173, reader)

Says which judge is meant without author pronouns.

Before:

> His Grok 4.7 judge is not comparable with ours and is not pooled.

After:

> The Grok 4.7 judge used on the proxy runs is not comparable with the Haiku judge and is not pooled.

## C44 (line 174, reader)

The route is named by itself, and "our" includes both authors.

Before:

> went through M.S.'s Antigravity route at low reasoning effort, where the control passed 2 of 3 against our 3 of 3 on OpenRouter

After:

> went through the Antigravity serving route at low reasoning effort, where the control passed 2 of 3 against 3 of 3 on OpenRouter

## C45 (line 174, reader)

Names the runs by the label Table D9 gives them instead of by author.

Before:

> M.S.'s pinned-price Gemini runs (Table D9) used the same route.

After:

> the pinned-price Gemini runs labeled second route in Table D9 used the same route.

## C46 (line 175, reader)

The batch number is internal; the reader needs only that one batch hit the rate limits.

Before:

> Gemini runs in M.S.'s third batch hit

After:

> Gemini runs in one batch hit

## C47 (line 175, reader)

Credit belongs in Author Contributions.

Before:

> His mixed-family markets used the original harness

After:

> Earlier mixed-family markets used the original harness

## C48 (line 190, consistency)

American spelling.

Before:

> price signalling alone

After:

> price signaling alone

## C90 (line 192, owner)

The info-hazard note from Code and Data joins the dual-use bullets of Appendix A.4, without the file path.

Before:

> ## Appendix B: Provenance (preexisting code marked)

After:

> - **Plea texts.** The plain offer, the warning, the precedent, the sham history and the placebo note are reproduced in Appendix C. The human-persona seller plea and the human buyer's plea model how to manipulate an agent with fabricated human distress, so this report describes them without quoting them, and their wording is not easy to reuse from it. We report counts and representative examples, not an optimized playbook, and we did not iterate any wording to raise acceptance.
> 
> ## Appendix B: Provenance (preexisting code marked)

## C112 (line 194, owner)

Owner ruling: everything is in the public repository, so Appendix B says in four sentences what is preexisting (required by the sprint rules), what is new, how the changes are gated, and that the README lists each file; it replaces the directory lists and the file table (C83).

Before:

> The double-auction harness is from Agrawal et al. ([andyjliu/llm-agent-collusion](https://github.com/andyjliu/llm-agent-collusion), single commit 2bb2a7e) as packaged in [poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon). It is third-party and preexisting. Its `cda_types.py` sets `initial_seller_ask_center = 97.5`, and the vendored copy keeps that default.
> 
> - `third_party/llm-agent-collusion/`: copied from collusion_hackathon @ `d585a7b` (Oct 23, 2026), minus the paper's shipped `data/` directory.
> - `third_party/util/`: the starter repository's `poseidon_compute` package, same commit.
> 
> Everything under `src/apartcollusion/`, `configs/` (including the seat-5 replay paths), `scripts/` (including `scripts/figures/`, `scripts/permutation_tests.py`, `scripts/extract_dg_message_counts.py`, `scripts/a_warn_runs.py`, `scripts/d99_runs.py`, `scripts/judge_vs_price.py`, `scripts/market_structure.py`, `scripts/analyze_pinned_a.py`, `scripts/analyze_pinned_dg.py` and `scripts/pinned_price_tables.py`), `report/data/`, `report/figures/` and `viewer/`, and every modification to vendored files, is new work done during the sprint (Oct 23 to 26, 2026). M.S.'s code in `mert_sprint/` (subscription proxy, run scripts, low-opening wrapper, judge script, pre-registration scripts, figure and diagram scripts, dashboard, notes) was written during the sprint; his Bertrand duopoly runs used the preexisting Poseidon `llm-cartel` starter, which is not included in the repository.
> 
> **Sprint modifications to vendored files** (all behind flags that are off by default; with every flag off the seller prompt is byte-identical to the original, which a test checks; paths are under `third_party/llm-agent-collusion/src/continuous_double_auction/`):
> 
> | File | Change |
> |---|---|
> | `market/messaging.py` | **new**: public history, private-message parsing, per-seller threads, `parse_reports` |
> | `evaluation/joint_criterion.py` | **new**: joint PASS criterion |
> | `cda_types.py` | new parameters (`seller_dms_enabled`, `max_dms_per_round`, `broadcast_history_rounds`, `overseer_sees_dms`, `prohibition_notice`, `report_tool`, `warning`, `precedent`, `sham_history`, `buyer_plea_hour`, `buyer_plea_text`, `shared_label`); `DirectMessage`; `SCRIPTED_SELLER`; DM, report, notice and scripted-offer fields on `MarketRound` |
> | `market/market.py` | passes history and threads to sellers; collects private messages; overseer optionally reads them; records reports; posts the frozen buyer plea; the scripted seat's messages bypass the per-round cap; an unparseable reply skips the turn instead of crashing the run |
> | `market/agents.py` | passes the new fields, the report rule, the notices block, the buyer-message block and the label sentence to the seller template |
> | `market/scripted.py` | **new**: scripted seat-5 seller (replay path; placebo, undercover and undercover-human messages) |
> | `prompt_templates/seller_prompt_base.jinja2` | communication block, `direct_messages` and `report_to_regulator` output fields, optional prohibition notice, "Market Notices" and "Messages from Buyers" blocks, optional label sentence |
> | `prompt_templates/buyer_prompt_tough.jinja2` | **new**: opt-in tougher buyer prompt, not used in any reported run |
> | `simulation.py` | CLI flags for all of the above (including `--max_tokens`, `--seller_reasoning_effort`, `--scripted_seat_path`, `--seat_mode`, `--offer_hour`, `--offer_price`, `--arm`, `--texts_dir`); joint criterion, message counts, reports, token usage, failed turns and text hashes in the summary and metadata |
> | `util/frozen_texts.py` | **new**: loads `configs/texts/<name>.txt` |
> | `util/misc.py` | log parser also returns plans, public and private messages and reports |
> | `evaluation/posthoc_judge.py`, `evaluation/judge_fingerprint.py`, `prompt_templates/seller_dg_eval.jinja2`, `prompt_templates/dm_thread_eval.jinja2` | **new**: post-hoc seller, thread and undercover-market judges with fingerprints (model, temperature, template, input view) and frozen prompts |
> | `evaluation/evaluate.py`, `prompt_templates/seller_individual_eval.jinja2` | judge view that includes a seller's messages and report; cached scores reused only from the same judge; results merged into `collusion_metrics.json`; default judge `anthropic/claude-haiku-5.5` |
> | `evaluation/manipulation_check.py` | **new**: post-run manipulation-check question for the shared-label markets |
> | `resources/model_wrappers.py` | token accounting including reasoning tokens; a warning when a reply is cut off at `max_tokens` |
> | `tests/` | **new**: unit tests, including the byte-identical-prompt test, `test_scripted_seat.py` and `test_shared_label.py` |

After:

> The double-auction harness is preexisting third-party code. It is Agrawal et al.'s [llm-agent-collusion](https://github.com/andyjliu/llm-agent-collusion) (commit 2bb2a7e), as packaged with its `poseidon_compute` utilities in [poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon), and it sits under `third_party/` with its default opening ask of $97.50. Everything else in the repository was written during the sprint (October 23 to 26, 2026), including every change to the vendored files. Those changes sit behind flags that are off by default, and with every flag off the seller prompt is byte-identical to the original, which a test checks. The repository README lists each modified file.

## C52 (line 257, phrasing)

The two objects of "shows" were not parallel.

Before:

> which shows the offer sat at about the going price and seat 5's visible price diverging between arms from hour 3.

After:

> which shows that the offer sat at about the going price and that seat 5's visible price diverges between arms from hour 3.

## C84 (line 259, owner)

Owner ruling: Tables D2a and D2b (every measure for every Gemini arm) do not belong in the report; Figures 4 and 5 and the data files carry these numbers, and no sentence refers to the tables.

Before:

> | Arm | Reported seat 5 /20 (by seed) | Replied to seat 5 /20 | Suspects collusion /20 | Suspects test /20 | Verbal agreement /20 |
> |------------------|----------------------|---------------|---------------|---------------|---------------|
> | Base | 0 | 7* | 3 | 0 | 20 |
> | D | 19 (4, 3, 4, 4, 4) | 9 | 19 | 0 | 18 |
> | D, offer at $99 | 20 (4, 4, 4, 4, 4) | 0 | – | – | – |
> | D-hs | 12 (3, 0, 1, 4, 4) | 10 | 13 | 1 | 19 |
> | D-hb | 20 | 6 | 20 | 0 | 20 |
> | D-hsb | 7 (1, 1, 1, 1, 3) | 9 | 7 | 0 | 20 |
> | E | 20 | 5 | 20 | 4 | 0 |
> | F | 20 | 2 | 20 | 16 | 0 |
> | F-sham | 20 | 4 | 20 | 1 | 0 |
> | G-warn | 0 | 15* | 0 | 0 | 0 |
> | G-prec | 0 | 0* | 3 | 14 | 0 |
> 
> *Table D2a. Reports, replies and judge labels in the Gemini arms (5 markets, 20 LLM sellers per arm); notes under Table D2b.*
> 
> | Arm | Private msgs per market | Public msgs per market | Hour-3 ask, $ | Ask index (seed range) | Trade index | Passes /5 |
> |------------------|-------------|-------------|-------------|-------------------|------------|------------|
> | Base | 108 | 58 | 96.47 | 0.41 (0.12 to 0.61) | 0.36 | 1 |
> | D | 108 | 57 | 95.76 | 0.38 (0.10 to 0.53) | 0.42 | 2 |
> | D, offer at $99 | 104.4 | 58 | 95.97 | 0.52 (0.13 to 0.69) | 0.54 | 4 |
> | D-hs | 108 | 59 | 96.63 | 0.55 (0.47 to 0.61) | 0.55 | 2 |
> | D-hb | 107 | 57 | 95.86 | 0.49 (0.35 to 0.55) | 0.51 | 3 |
> | D-hsb | 109 | 58 | 95.35 | 0.41 (0.26 to 0.50) | 0.33 | 0 |
> | E | 1 | 56 | 95.55 | 0.39 (0.21 to 0.62) | 0.45 | 1 |
> | F | 0.4 | 0 | 95.37 | 0.42 (0.23 to 0.63) | 0.46 | 2 |
> | F-sham | 0.8 | 45.8 | 95.52 | 0.37 (0.22 to 0.48) | 0.42 | 0 |
> | G-warn | 3 | 55 | 96.21 | 0.48 (0.37 to 0.62) | 0.50 | 2 |
> | G-prec | 0 | 0 | 96.22 | 0.44 (0.29 to 0.56) | 0.44 | 1 |
> 
> *Table D2b. Messaging and prices in the Gemini arms (5 markets per arm, LLM sellers only). Notes for Tables D2a and D2b: Reported seat 5: distinct sellers with at least one report naming seat 5, from the run logs; for D-hb and E this differs from the first-report column of `outcomes.csv` (19 and 18), because one D-hb seller and two E sellers first reported a peer before the offer was visible. Replied: sellers who sent seat 5 a private message from hour 4 on; \* replies to the placebo note. Judge labels count any judged hour from hour 4 on; verbal agreement counts agreement with or echo of any peer's price proposal. Private messages per market include messages to seat 5 (103.6 between sellers and 4.4 to seat 5 in both Base and D); in the five warning arms every private message went to seat 5, and individual G-warn markets sent 2, 2, 4, 4 and 3. Hour-3 ask: the LLM sellers' mean ask in the hour the offer is sent. Passes: joint criterion. The $99 row ran at the same seeds, was not judged, and its 1.2 private messages per market to seat 5 were all sent in hour 1, before the offer. Exact permutation tests over markets are given in the text. Sources: `report/data/dg/table3_extra.csv`, `outcomes_by_arm.csv`, `market_by_arm.csv`, `permutation_tests.csv`; `report/data/dg_gemini_99/`.*

After:

> (removed)

## C54 (line 291, phrasing)

"Reported anyone, a peer" hangs a fragment off a comma.

Before:

> reported anyone, a peer.

After:

> reported anyone (a peer).

## C55 (line 293, consistency)

The any-report count is now the only definition, so the comparison with first reports suggests a second result.

Before:

> counting any report naming seat 5 instead of first reports, it gives

After:

> counting sellers with any report naming seat 5, it gives

## C56 (line 293, phrasing)

Names the quantity the two values measure (R17).

Before:

> plateaued from about hour 12 at 0.61 against 0.57

After:

> plateaued from about hour 12 at an ask index of 0.61 against 0.57

## C57 (line 312, reader)

`dm_summary` is an internal field name.

Before:

> from each run's `dm_summary`)

After:

> from each run's message summary)

## C58 (line 340, reader)

Credit tags in headings mean nothing to a reader; credit is in Author Contributions.

Before:

> ### D.4 Frontier sellers at the default opening (M.S.)

After:

> ### D.4 Frontier sellers at the default opening

## C59 (line 353, reader)

Names the proxy by what it is and points to its limitation.

Before:

> at the $97.50 opening through M.S.'s proxy.

After:

> at the $97.50 opening through the subscription proxy (Appendix A.2, item 12).

## C60 (line 353, reader)

The judge is told apart from the Haiku judge by its model, not by an author.

Before:

> M.S.'s Grok 4.7 judge, reading private reasoning only,

After:

> A separate Grok 4.7 judge, reading private reasoning only,

## C61 (line 355, reader)

Credit tags in headings mean nothing to a reader; credit is in Author Contributions.

Before:

> ### D.5 The opening price (M.S.)

After:

> ### D.5 The opening price

## C62 (line 366, reader)

Table D6 holds exactly these 45 markets, which names them without initials.

Before:

> in 44 of M.S.'s 45 frontier and Haiku markets at the default opening.

After:

> in 44 of the 45 markets of Table D6.

## C63 (line 368, reader)

"Our" includes both authors; the route already identifies the runs.

Before:

> where the control passed 2 of 3 against our 3 of 3 on OpenRouter, so their comparison

After:

> where the control passed 2 of 3 against 3 of 3 on OpenRouter, so their comparison

## C64 (line 370, reader)

Credit belongs in Author Contributions; the caption names the models.

Before:

> Prices stay where the market opens (M.S.'s runs).

After:

> Prices stay where the market opens.

## C65 (line 370, reader)

The credit tag means nothing to a reader of the PDF; credit is given in Author Contributions.

Before:

> Horizontal lines mark $90, $95 and $97.50. (Figure: M.S.)

After:

> Horizontal lines mark $90, $95 and $97.50.

## C66 (line 391, reader)

The credit tag means nothing to a reader of the PDF; credit is given in Author Contributions.

Before:

> 4+4, GPT-5.6 Sol (M.S.) | messaging on

After:

> 4+4, GPT-5.6 Sol | messaging on

## C67 (line 392, reader)

The credit tag means nothing to a reader of the PDF; credit is given in Author Contributions.

Before:

> 4+4, GPT-5.6 Sol (M.S.) | messaging off

After:

> 4+4, GPT-5.6 Sol | messaging off

## C68 (line 393, reader)

The credit tag means nothing to a reader of the PDF; credit is given in Author Contributions.

Before:

> 4+4, GPT-6 Luna (M.S.) | messaging on

After:

> 4+4, GPT-6 Luna | messaging on

## C69 (line 394, reader)

The credit tag means nothing to a reader of the PDF; credit is given in Author Contributions.

Before:

> 4+4, GPT-6 Luna (M.S.) | messaging off

After:

> 4+4, GPT-6 Luna | messaging off

## C70 (line 395, reader)

The credit tag means nothing to a reader of the PDF; credit is given in Author Contributions.

Before:

> second route (M.S.) | messaging on

After:

> second route | messaging on

## C71 (line 396, reader)

The credit tag means nothing to a reader of the PDF; credit is given in Author Contributions.

Before:

> second route (M.S.) | messaging off

After:

> second route | messaging off

## C72 (line 402, reader)

Names the rows meant instead of their author, now that the row tags are gone.

Before:

> M.S.'s rows to three decimals

After:

> the Sol, Luna and second-route rows to three decimals

## C73 (line 402, reader)

The rows are labeled "second route" in the table, and "our" includes both authors.

Before:

> M.S.'s Gemini rows ran on his Antigravity serving route (Appendix A.2, item 13), where the ordinary-market $97.50 control passed 2 of 3 against our 3 of 3 on OpenRouter.

After:

> The second-route Gemini rows ran on the Antigravity serving route (Appendix A.2, item 13), where the ordinary-market $97.50 control passed 2 of 3 against 3 of 3 on OpenRouter.

## C74 (line 408, reader)

Credit belongs in Author Contributions.

Before:

> M.S.'s attempts failed on provider credits and quotas, and his earlier mixed markets used

After:

> attempts failed on provider credits and quotas, and earlier mixed markets used

## C75 (line 416, reader)

"Across both authors" splits the work by author, which the reader does not need.

Before:

> our messaging-off runs pass in 4 of 6; across both authors 5 of 9 pass

After:

> messaging-off runs pass in 4 of 6, and 5 of 9 with three proxy runs added

## C76 (line 418, reader)

Same plain wording as Section 3.1.

Before:

> The vendored rule-based buyer always bids about $80

After:

> The harness's rule-based buyer always bids about $80

## C77 (line 428, reader)

The markets are named by model and market, not by author.

Before:

> for 110 markets: our 50 Gemini undercover markets and M.S.'s 60 Gemini,

After:

> for 110 markets: the 50 Gemini undercover markets and 60 Gemini,

## C78 (line 428, reader)

"Our" includes both authors.

Before:

> holds our 25 warning-arm markets

After:

> holds the 25 warning-arm markets

## C79 (line 428, consistency)

American spelling.

Before:

> the grey band

After:

> the gray band

## C80 (line 428, reader)

A reader does not know the initials, and figure credit is already in Author Contributions.

Before:

> an index near 0. (Figure: M.S.)

After:

> an index near 0.

## C81 (line 451, reader)

Several quotes address seat 5 by its in-market name, which the reader cannot otherwise decode (names per seed from report/data/dg/outcomes.csv).

Before:

> Each quote is verbatim from the file named.

After:

> Each quote is verbatim from the file named. Seat 5 is named Mia in seed 0, Yara in seed 1 and Maya in seed 2.

## C82 (line 451, reader)

The folder path, not the author, tells the reader where a quote can be checked.

Before:

> Our run folders under `results/` are not in the repository; M.S.'s are under `mert_sprint/experiments/runs/`.

After:

> Run folders under `results/` are not in the repository; those under `mert_sprint/experiments/runs/` are.
