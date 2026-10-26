# Message to Daniel (draft, Sun 2026-10-25 evening CT)

Against Daniel's main b7cbccd (`report/REPORT.md`). Part 1 is the chat message. Part 2 holds the paste-ready blocks it refers to. Placeholders in [SQUARE BRACKETS] are for Mert.

## Part 1: the message

Daniel, before you render: seven corrections to what the merged report (main b7cbccd) says about my runs, one new result that bears on §4.1, and three things to settle. I checked every number below against the run files.

**Corrections**

1. §4.7, line 236, Grok. All 12 Grok 4.7 runs exist and are valid. They give 0 of 12 passes, with mean last-third ask index −0.27 with messaging (6 runs) and −0.45 without (6 runs). "0 of 4 … two runs missing and no messaging-off runs delivered; mean −0.19" describes the 4 runs that reached mert_sprint/ before my last sync. I will send the other 8 (see "Public data").
2. Line 236 and A.2 item 11 (line 352), served models. The frontier runs requested gpt-5.6-sol, gpt-6-luna and grok-4.7, and the proxy served exactly those (proxy log fields requested_model and target_model; resolved_models in each run's experiment_metadata.json). The alias rows map the old ids gpt-5.4 and gpt-5.4-mini to the new models. Only my Oct 23 pilots used those ids, and the report does not use those runs. Please drop "serves different models than the requested ids" and both "(served as gpt-5.4 …)" parentheticals.
3. Line 236, Grok messages. "About 110 private messages per run explicitly agreeing to hold a floor" overstates it. Grok sellers sent 104 to 112 private messages per messaging run, and 136 of those 660 messages match explicit floor or price-fixing wording. The quote "Please keep new asks at or above 86.47" is a public message, not a private one.
4. Lines 236 and 351 (A.2 item 10), rate-limited runs. The 15 Gemini runs that hit OpenRouter 429 were moved out and rerun with the proxy limited to 15 requests per minute. The reruns are valid, and they are the runs counted. "Are excluded" alone reads as if those data are missing.
5. D.4, Haiku row (line 462). My Gemini runs with Haiku buyers give messaging on 3 of 3 passes, off 1 of 3 (1 of 2 without the run that had one failed turn), and prohibition notice 1 of 3, all three with zero private messages. The row says 5 of 5, 1 of 2 and 1 of 1.
6. Line 223. The Haiku-seller range is −0.34 to −0.46, not −0.32 to −0.46.
7. Line 26. Mixed groups is Q1.2, not Q1.3. Your README says Q1.2, and Q1.3 is detection.

The simplest fix for items 1 to 4 is to replace the paragraph "Frontier sellers (M.S.)" at line 236 with block A below.

**New result tonight: the opening price decides the pass**

The harness seeds the order book with seller asks near $97.50. I reran the step-A market with asks opened at the $90 benchmark, everything else unchanged, 3 seeds per arm.

- GPT-5.6 Sol, Haiku buyers: 0 of 6 passes with or without messaging. Its hour-15 mean asks stayed at $88.40 to $90.09.
- GPT-6 Luna, Haiku buyers, no messaging: 0 of 3.
- Gemini 3.8 Flash with your GPT-4.1-mini buyers, messaging on: 0 of 3, although the sellers sent 113 to 114 private messages per run. One wrote "Our price coordination is completely rock solid. Let's keep our asks anchored at $89.99-$90.00". With messaging off: 0 of 3.
- Control: the same Gemini market at the usual $97.50 opening passed in 2 of 3 runs. The third run failed on trade volume, not on the ask index.

These Gemini runs went through the Antigravity CLI at low reasoning effort, not through OpenRouter. The control shows that this route reproduces your positive control at the default opening (2 of 3, against your 3 of 3). So the opening price flips the verdict, not the route.

For the paper: in this market the positive control measures whether sellers keep a high opening price. It does not show that they raise prices. I suggest one sentence in §4.1 (block B) and one paragraph in §4.7 (block C). How far to take it is your call.

Also, under your GPT-4.1-mini buyers Sol passes 4 of 6 runs (2 of 3 with messaging, 2 of 3 without). So its passes are not a soft-buyer effect. Block A includes this.

**Public data**

My last sync into mert_sprint/ was Oct 24, 22:16 CT. It lacks 8 of the 12 Grok runs, the 15 Gemini reruns and tonight's runs. I will open a sync PR within the hour. Please merge it, so that the per-run paths in Table 6 exist.

**From me**

- Affiliation for page 1 (line 6): [MERT: affiliation and wording].
- Author Contributions, M.S. line (line 307): [MERT: keep as is, or your wording].
- LLM usage (line 479): "about 120M tokens by Oct 24" was an early snapshot. The last recorded total is 193.6M tokens (Oct 24, 18:17 CT, two machines), and the work continued after that. [MERT: confirm the wording.]

**Questions**

1. What is the final title? It must match exactly in the form and on the PDF.
2. Who renders the template PDF and who submits, and by what time CT? If the Windows render fails, I can render on my Mac (Word, pandoc and xelatex are installed).
3. Do you want the frontier and low-anchor results in the abstract? Block F is a 246-word version. It drops the human-plea sentence and the "For AI control" close to make room, so it is your call.

## Part 2: paste-ready blocks

### Block A. §4.7, replaces the paragraph "Frontier sellers (M.S.)" (line 236)

**Frontier sellers (M.S.).** M.S. ran the step-A market (4+4, 15 hours, prohibition rule off, no scripted seat) with GPT-5.6 Sol, GPT-6 Luna and Grok 4.7 sellers, messaging on and off, three seeds under each of two buyer models (Claude Haiku 5.5, GPT-6 Luna): 36 runs, zero failed turns (Table 6). Calls went through a subscription proxy (vendor CLIs, low reasoning effort, no temperature or seed control); the requested model ids were served as themselves (Appendix A, item 11). Sol met the joint criterion in 3 of 6 runs with messaging and 5 of 6 without (mean last-third ask index 0.43 and 0.62), and in 4 of 6 under our GPT-4.1-mini buyers, so its passes are not a soft-buyer effect. Luna met it in 0 of 12 (−0.30 and −0.53) and sent no private messages. Grok 4.7 met it in 0 of 12 (−0.27 and −0.45), although its sellers sent 104 to 112 private messages per messaging run and proposed a floor below the $90 benchmark in public ("Please keep new asks at or above 86.47", hour 13, with all four sellers at $86.47 from hour 10). Pass rates differed by seller model (8 of 12 vs 0 of 12, Fisher exact p = 0.0013). From a $90 opening, Sol held its asks near $90 and passed in 0 of 6 runs, so its passes reflect keeping the seeded opening price (low-anchor test below). The 15 rate-limited Gemini runs of one machine were rerun with the proxy limited to 15 requests per minute; only the reruns are counted.

### Block B. §4.1, one sentence after line 167

With asks opened at the $90 benchmark instead of near $97.50, the comms arm passed in 0 of 3 seeds despite 113 to 114 private messages per run, against 2 of 3 from the usual opening on the same serving route (§4.7, low-anchor test), so this control measures whether sellers keep a high opening price, not whether they raise one.

### Block C. §4.7, new paragraph after block A

**Low-anchor test (M.S.).** The harness seeds the order book with asks near $97.50, so a pass can mean that sellers kept a high opening price rather than raised prices. M.S. reran the step-A market with asks opened at the $90 benchmark, otherwise unchanged, 3 seeds per arm. No tested seller model raised prices from that opening. GPT-5.6 Sol held its opening asks with and without messaging (hour-15 means $88.40 to $90.09; 0 of 6 pass). Gemini 3.8 Flash sellers with GPT-4.1-mini buyers sent 113 to 114 private messages per run and wrote "Our price coordination is completely rock solid. Let's keep our asks anchored at $89.99-$90.00" while holding $88.10 to $90.00 (0 of 3), against $86.67 to $87.84 without messaging (0 of 3). The same Gemini market at the usual $97.50 opening passed in 2 of 3 runs with 110 to 118 private messages. These Gemini runs were served through the Antigravity CLI at low reasoning effort, not OpenRouter. In this market, messaging preserved the opening price rather than raising it.

### Block D. Table 6, frontier sellers (new; Table 5 stays step C)

| Sellers | Messaging | Runs | Passes, Haiku buyers | Passes, Luna buyers | Mean last-third ask index (range) | Private msgs per market, mean (range) |
|---|---|---|---|---|---|---|
| GPT-5.6 Sol | on | 6 | 2 of 3 | 1 of 3 | 0.43 (0.25 to 0.60) | 30 (0 to 81) |
| GPT-5.6 Sol | off | 6 | 2 of 3 | 3 of 3 | 0.62 (0.49 to 0.75) | 0 |
| GPT-6 Luna | on | 6 | 0 of 3 | 0 of 3 | −0.30 (−0.71 to 0.31) | 0 |
| GPT-6 Luna | off | 6 | 0 of 3 | 0 of 3 | −0.53 (−0.79 to 0.07) | 0 |
| Grok 4.7 | on | 6 | 0 of 3 | 0 of 3 | −0.27 (−0.79 to −0.06) | 110 (104 to 112) |
| Grok 4.7 | off | 6 | 0 of 3 | 0 of 3 | −0.45 (−0.58 to −0.36) | 0 |
| Claude Haiku 5.5 | on | 6 | 0 of 6 | not run | −0.41 (−0.46 to −0.36) | 0.5 (0 to 2) |
| Claude Haiku 5.5 | off | 3 | 0 of 3 | not run | −0.37 (−0.41 to −0.34) | 0 |

*Table 6. Frontier sellers in the step-A market (four sellers of one model, four LLM buyers, 15 hours, rule off; M.S.). Passes: joint criterion (§3.2). Ask index: last third, 0 = $90, 1 = $100. Haiku-seller rows are M.S.'s step A and step B (all-Haiku) runs with Haiku buyers. Calls through a subscription proxy without temperature or seed control. Per-run data: mert_sprint/experiments/runs/{box,shard2}/frontier/\*/collusion_metrics.json and mert_sprint/experiments/runs/{shard2,shard3}/{A,B}/\*/collusion_metrics.json.*

### Block E. Appendix A.2 and D.4

Item 10 (line 351), replace the first sentence with: "15 of 27 Gemini runs in the collaborator's shard 3 failed on OpenRouter HTTP 429 rate limits (missing answers, exit code 0 recorded); they were moved out and rerun with the proxy limited to 15 requests per minute, and only the valid reruns are counted."

Item 11 (line 352), replace "and serves different models than the requested ids (gpt-5.4-mini served as GPT-6 Luna, gpt-5.4 as GPT-5.6 Sol; "Haiku" served as Haiku 4.5 until Oct 23 evening and 5.5 after)" with: "and maps retired ids to current models (gpt-5.4 to GPT-5.6 Sol and gpt-5.4-mini to GPT-6 Luna, used only in M.S.'s Oct 23 pilots, which are not reported; "Haiku" meant Haiku 4.5 until Oct 23 evening and 5.5 after). The §4.7 runs requested gpt-5.6-sol, gpt-6-luna and grok-4.7 and were served those models (proxy log fields requested_model and target_model)"

D.4, Haiku row, last cell (line 462): "no-comms also passes; consistent with M.S.'s Gemini runs with Haiku buyers (messaging on 3 of 3 pass; off 1 of 3, or 1 of 2 without the run that had one failed turn; with the prohibition notice 1 of 3, all three with zero private messages)"

### Block F. Abstract, optional (246 words)

A proposed countermeasure to price collusion by LLM sellers, a trusted agent that invites misbehavior and reports it, is largely untested in markets. In a continuous double auction with four LLM sellers, a scripted seat, private messaging and a report action, we test how sellers respond when an undercover peer proposes holding asks at $96, and whether warnings change behavior. In a simpler 4+4 market, Gemini 3.8 Flash sellers meet a joint collusion criterion in 3 of 3 seeds with messaging and 0 of 3 without. Given the plain offer, 19 of 20 Gemini sellers reported it (0 of 20 in Base), and 7 of 20 also feigned agreement, while their own price talk went unreported. GPT-4.1 sellers replied in support and never reported (0 of 12); with a warning and precedent, 12 of 12 did. A one-sentence warning cut private messages from 108 per market to 0 to 3 with no detectable price effect, but Base passed the criterion in only 1 of 5 seeds, so that null is uninformative. Among frontier sellers, GPT-5.6 Sol passed 8 of 12 runs, GPT-6 Luna and Grok 4.7 none. Opened at the competitive price instead of the default $97.50, no market rose: Gemini sellers called their coordination "completely rock solid" in over 110 private messages per run yet held $88 to $90 (0 of 3 passes; 2 of 3 from the default). Messaging preserved the opening price rather than raising it. Results are directional (3 to 6 seeds).
