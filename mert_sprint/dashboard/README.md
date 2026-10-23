# Agent monitor dashboard

Interactive dashboard for the sprint's market-collusion runs: round-by-round replays, hover meanings on every
line, colour-coded conditions, and a right-click "Ask Opus 5.5" box.

## Run it on any machine

```bash
git pull
python3 dashboard/serve.py            # http://127.0.0.1:8788/  (Python 3.9+, standard library only)
python3 dashboard/serve.py --once     # rescan once, refresh index.html and state.json, exit
```

Or open `dashboard/index.html` directly: it carries the last scan, so it works offline.

## Where the data comes from

`serve.py` reads run files from the first of these that exists:

1. `$COLLUSION_HACKATHON` (a harness clone you point it at),
2. `./collusion_hackathon` (made by `scripts/setup_other_machine.sh`) or `/workspace/collusion_hackathon` (the sprint box),
3. `experiments/snapshot/` in this repo (a snapshot, refreshed with `python3 experiments/sync_runs.py` on the sprint box).

## Asking Opus

- On claude.ai (the published artifact), questions go through the artifact's `sample` capability.
- Served locally, questions go to `POST /api/ask`, which calls the `claude` CLI on your PATH
  (`$CLAUDE_BIN` overrides) with `--model claude-opus-5-5 --effort low`.
- With neither available, the box shows the built-in explanations.

Right-click anything to ask about it. Shift + right-click opens the normal browser menu.
