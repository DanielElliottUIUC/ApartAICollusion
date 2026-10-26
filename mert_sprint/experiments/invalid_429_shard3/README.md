# Invalid shard 3 runs (OpenRouter rate limit), 2026-10-24

These 15 Gemini runs are NOT valid results. Gemini was served through OpenRouter (`google/gemini-3.8-flash`), and the
account was limited to 20 requests per minute per model. Calls that failed 3 retries returned no reply
("Failed after 3 attempts", HTTP 429), so rounds ran with missing model answers. The runner still recorded rc=0.

Failed calls per run: danielA_gemini_notice-seed2 88, danielA_gemini_nocomms-seed2 70, danielA_gemini_notice-seed1 59,
danielB_GGGG-seed0 52, danielA_gemini_notice-seed0 44, danielA_gemini_comms-seed1 31, danielA_gemini_nocomms-seed0 28,
danielB_GGGG-seed1 24, danielB_GGGG-seed2 20, het55_GGG_s1 13, het55_GGG_s2 12, danielA_gemini_comms-seed0 8,
danielA_gemini_comms-seed2 8, het55_GGG_s0 4, het55_GGO_s0 3.

The Grok 4.7 judge files in the Daniel run folders here score runs that have these gaps. Do not use them.
The runs were repeated with the proxy limited to 15 requests per minute (`OPENROUTER_RPM=15`). The valid reruns
are in `experiments/runs/shard3/`. Kept for the record, moved out of `experiments/runs/` so the runner does not count them as done.
