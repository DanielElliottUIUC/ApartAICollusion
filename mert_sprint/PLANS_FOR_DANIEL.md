# Mert's side: plans and run split (Sat Oct 24, 5:15 PM CT)

This note only lives in `mert_sprint/`. It changes none of your code, configs or runs.

## What we are running now

Frontier positive control on your market (your Phase A design), on the grokbot computer:

* Sellers: all Grok 4.7, all GPT 6 Luna, all GPT 5.6 Sol.
* Messaging on and off, seeds 0, 1, 2.
* Two buyer arms with the same buyer prompt: Claude Haiku 5.5 buyers (your design) and GPT 6 Luna buyers.
* 36 runs, 120 calls each, through our subscription proxy, so no OpenRouter spend.
* Results will come to you as a pull request under `mert_sprint/experiments/`.

## What we leave to you

* Every mix with DeepSeek (GGDD, GCCD, DDDD, GGGD). We will not run them.

## What we dropped on our side

* GPT 4.1 runs. We want the newest frontier models instead.
* Fable runs, paused for now.
* Gemini runs are paused: our Gemini quota is out until about Oct 30 and our OpenRouter balance is empty.

## Next on our side

1. Frontier mixed teams after the positive control: Grok with Luna, Grok with Sol, and all three families together, 3 seeds each.
2. A first draft of the report and its Limitations and Dual Use appendix.

## Open questions for you

* Do you want us to build any of the D to G pieces (undercover or placebo seat, `report_to_regulator`, warning and precedent texts, `outcomes.py`)? We will not start until you say which ones, so we do not duplicate work.
* Which judge model should score runs? `models.toml` lists `openai/gpt-4.1-mini`. We could point it at GPT 6 Luna through the proxy.
* Should frontier runs use the tough buyer prompt from PR #14 once it merges?
