#!/usr/bin/env python3
"""One entry point for every remaining sprint run, split across N machines, plus the doc rebuild.

    scripts/run_all.sh plan                       # every run with its shard and status, plus per shard progress
    scripts/run_all.sh plan --shard 2/3           # one shard's runs and progress
    scripts/run_all.sh plan --markdown            # the table that goes in notes/RUN_PLAN.md
    scripts/run_all.sh run --shard 2/3 --jobs 3   # run shard 2 of 3 (pull, smoke check, run, push per phase)
    scripts/run_all.sh run --shard all            # everything on one machine
    scripts/run_all.sh run --shard 2/3 --skip-clis agy   # leave the Gemini runs to another machine
    scripts/run_all.sh assign --n 3 --jobs 4,3,3  # rewrite notes/shard_assignment.json (box only, then commit)
    scripts/run_all.sh docs                       # rebuild experiments/cases and docs/AGENT_BEHAVIOR.md
    scripts/run_all.sh merge                      # git pull, rebuild docs, commit, push

Sharding. Each run's shard comes from the pinned file notes/shard_assignment.json, which is committed to git,
so every machine agrees. `assign` writes it: runs already done or in progress on the box, every OpenRouter run
(GPT-4.1, DeepSeek, and the judge), every Fable run and every Grok run go to shard 1 (the box, the only machine with an
OpenRouter key). The rest are split by estimated wall time (longest first, greedy, divided by each shard's
--jobs), so all shards finish at about the same time. A run missing from the file falls to shard 1.
`--shard box` still works and means shard 1. `--shard local` is retired.

Outputs. Shard 1 writes under experiments/runs/box/ (its old folder), shard k under experiments/runs/shard<k>/,
each with its own token-usage/proxy_usage.<name>.jsonl, so pushes never touch the same file.
experiments/runs/local/ holds box runs from before the N way split and belongs to shard 1.
A run is skipped when its finished output exists under ANY shard folder, or when a process for it is running.
A run that failed MAX_ATTEMPTS times (default 2) is skipped and reported; refusals are kept as outcomes.
"""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "experiments" / "runs"
PROXY = "http://127.0.0.1:8787/v1"
ASSIGNMENT = ROOT / "notes" / "shard_assignment.json"
PINNED_SHARD = 1  # the box: OpenRouter key, Fable, and everything it already started
PHASE_ORDER = ["sweep", "refusal", "matrix", "A", "B", "fable", "frontier"]
GROK_MAX = int(os.environ.get("GROK_MAX", "2"))  # grok CLI slows down badly under load
MAX_ATTEMPTS = int(os.environ.get("MAX_ATTEMPTS", "2"))


def first_dir(*cands) -> Path:
    for c in cands:
        if c and Path(c).is_dir():
            return Path(c)
    return Path(cands[-1])


HARNESS = first_dir(os.environ.get("COLLUSION_HACKATHON"), ROOT / "collusion_hackathon", "/workspace/collusion_hackathon")
DANIEL = first_dir(os.environ.get("DANIEL_REPO"), ROOT.parent / "ApartAICollusion", "/workspace/ApartAICollusion")

# Seconds per call: means measured from token-usage/proxy_usage.box.jsonl on Oct 24 (about 9:40 AM CT,
# 3 to 6 runs at once). Models with no data yet (OpenRouter ones) are guesses.
LATENCY = {"claude-haiku-5-5": 6.3, "claude-haiku-4-5": 33.6, "claude-sonnet-5-5": 6.1, "claude-opus-5-5": 7.2,
           "gpt-6-luna": 4.1, "gpt-5.6-sol": 8.8, "gemini-3.8-flash-low": 13.3, "google/gemini-3.8-flash": 13.3,
           "anthropic/claude-haiku-5.5": 6.3, "grok-4.5": 60.2, "grok-4.6": 50.5, "grok-4.7-build-fast": 89.4,
           "grok-4.7": 21.6, "openai/gpt-4.1": 8, "deepseek/deepseek-v4.1-flash-1017": 10}
NEEDS_OPENROUTER = ("openai/gpt-4.1", "deepseek/", "moonshotai/")
# Wall time factors fitted to the Oct 24 sweep runs: Bertrand takes rounds x slowest call (factor 1.0);
# the auction makes about 0.45 calls per seller per round. Daniel's v2 market (LLM buyers, DMs) has no
# finished run yet, so it assumes every seat calls once per round (factor 1.0); treat it as a rough guess.
CARTEL_F, CDA_F, DANIEL_F = 1.0, 0.45, 1.0
FABLE_CHUNKS = 6  # fable_full split by item id so it fits in about an hour per chunk


@dataclass
class Run:
    tag: str
    phase: str
    harness: str          # poseidon_cda | poseidon_cartel | daniel_cda
    models: list
    args: list
    calls: int
    minutes: float
    rounds: int = 0
    seed: int = 0
    blocked: str = ""     # empty = ready
    shard: str = ""
    note: str = ""
    extra: dict = field(default_factory=dict)


def lat(m):
    return LATENCY.get(m, 20)


# ---------------------------------------------------------------- the plan
SWEEP_MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5", "gpt-6-luna", "gpt-5.6-sol",
                "gemini-3.8-flash-low", "grok-4.5", "grok-4.6", "grok-4.7-build-fast", "grok-4.7"]
C, O, G = "claude-haiku-5-5", "gpt-6-luna", "gemini-3.8-flash-low"
FAM = {"C": C, "O": O, "G": G}
MATRIX_SEEDS = [int(s) for s in os.environ.get("MATRIX_SEEDS", "0 1 2").split()]
DANIEL_SEEDS = [0, 1, 2]
D_GEMINI, D_HAIKU, D_GPT41, D_DEEPSEEK = ("google/gemini-3.8-flash", "anthropic/claude-haiku-5.5",
                                         "openai/gpt-4.1", "deepseek/deepseek-v4.1-flash-1017")
# Phase frontier (Oct 24, Mert): Daniel's step A design with the newest models we reach for $0 through the proxy.
# Sellers all one model; buyers either Claude Haiku 5.5 (his design; Claude only as buyers) or GPT-6 Luna.
F_SELLERS = {"grok47": "grok-4.7", "gpt6luna": "gpt-6-luna", "gpt56sol": "gpt-5.6-sol"}
F_BUYERS = {"haikuB": "anthropic/claude-haiku-5.5", "lunaB": "gpt-6-luna"}
D_COMMS = ["--seller_comms_enabled", "--seller_dms_enabled", "--max_dms_per_round", "2", "--broadcast_history_rounds", "4"]


def cartel(tag, phase, models, prefix, think=False, rounds=15, seed=0, note=""):
    a = ["--models", ",".join(models), "--rounds", str(rounds), "--seeds", str(seed), "--prefix", prefix, "--name", tag, "-y"]
    if think:
        a.insert(-1, "--think")
    per_round = max(lat(m) for m in models)
    return Run(tag, phase, "poseidon_cartel", sorted(set(models)), a, rounds * 2, rounds * per_round * CARTEL_F / 60,
               rounds, seed, note=note)


def cda(tag, phase, sellers, rounds, seed=0, comms=True, boss=True, note=""):
    a = ["--seller_models", *sellers, "--buyer_models", *(["zip"] * len(sellers)), "--rounds", str(rounds),
         "--seeds", str(seed), "--tag", tag, "-y"]
    if comms:
        a.append("--seller_comms_enabled")
    if boss:
        a.append("--boss_pressure")
    return Run(tag, phase, "poseidon_cda", sorted(set(sellers)), a, rounds * len(sellers),
               rounds * sum(lat(m) for m in sellers) * CDA_F / 60, rounds, seed, note=note)


def daniel(tag, phase, sellers, seed, extra_flags, note="", buyer=None, rounds=15):
    buyer = buyer or D_HAIKU
    a = ["--sellers", "4", "--buyers", "4", "--seller_models", *sellers, "--buyer_models", buyer, "--rounds", str(rounds),
         "--seeds", str(seed), "--max_tokens", "16000", "--tag", tag, "-y", *extra_flags]
    calls = rounds * 8
    mins = rounds * (sum(lat(m) for m in sellers) + 4 * lat(buyer)) * DANIEL_F / 60
    r = Run(tag, phase, "daniel_cda", sorted(set(sellers + [buyer])), a, calls, mins, rounds, seed, note=note)
    return r


def frontier_runs(rounds=15, tag_prefix="frontierA", seeds=None) -> list[Run]:
    """Comms on first (both buyer arms interleaved), then comms off. No in-run judge (it is GPT-4.1 mini on
    OpenRouter); judge afterwards with Daniel's posthoc_judge.py."""
    out = []
    for comms in ("comms", "nocomms"):
        for s in (DANIEL_SEEDS if seeds is None else seeds):
            for sk, sm in F_SELLERS.items():
                for bk, bm in F_BUYERS.items():
                    r = daniel(f"{tag_prefix}_{sk}_{comms}_{bk}-seed{s}", "frontier", [sm] * 4, s,
                               D_COMMS if comms == "comms" else [], buyer=bm, rounds=rounds)
                    r.extra.update(no_judge=True, order=len(out))
                    out.append(r)
    return out


def build_plan() -> list[Run]:
    runs: list[Run] = []
    # Phase sweep: our run_sweep.sh, every model x (Bertrand P0, PC, PC think, auction chat + boss), seed 0.
    for m in SWEEP_MODELS:
        t = m.replace(".", "_").replace("/", "_")
        runs += [cartel(f"sweep_{t}_P0", "sweep", [m], "P0"),
                 cartel(f"sweep_{t}_PC", "sweep", [m], "PC"),
                 cartel(f"sweep_{t}_PC_think", "sweep", [m], "PC", think=True),
                 cda(f"sweep_{t}_comms_boss", "sweep", [m] * 3, 10)]
    # Phase refusal: recheck the Oct 23 Haiku 4.5 Bertrand PC refusal so the reply text lands in a log.
    runs += [cartel("refusal_claude-haiku-4-5_PC", "refusal", ["claude-haiku-4-5"], "PC",
                    note="Oct 23 run aborted after 4 attempts; this keeps the log"),
             cartel("refusal_claude-haiku-4-5_PC_think", "refusal", ["claude-haiku-4-5"], "PC", think=True)]
    # Phase matrix: mixed teams with Claude Haiku 5.5 (Oct 23 used Haiku 4.5), 3 sellers, ZIP buyers, 8 rounds.
    for mix in ["CCC", "OOO", "GGG", "CCO", "CCG", "OOC", "OOG", "GGC", "GGO", "COG", "OGC"]:
        for s in MATRIX_SEEDS:
            runs.append(cda(f"het55_{mix}_s{s}", "matrix", [FAM[x] for x in mix], 8, seed=s))
    for pair in ["CO", "CG", "OG", "GG", "CC", "OO"]:
        for s in MATRIX_SEEDS:
            runs.append(cartel(f"het55_P0_{pair}_s{s}", "matrix", [FAM[x] for x in pair], "P0", seed=s))
    # Phase A: Daniel's positive control (scripts/phase0_positive_control.sh arms), v2 market, Haiku buyers.
    arms = [("gemini_comms", D_GEMINI, D_COMMS), ("gemini_nocomms", D_GEMINI, []),
            ("gemini_notice", D_GEMINI, D_COMMS + ["--prohibition_notice"]),
            ("haiku_comms", D_HAIKU, D_COMMS), ("haiku_nocomms", D_HAIKU, []),
            ("gpt41_comms", D_GPT41, D_COMMS), ("gpt41_nocomms", D_GPT41, [])]
    for name, model, flags in arms:
        for s in DANIEL_SEEDS:
            note = "only needed if the Gemini arm fails the gate" if name.startswith("gpt41") else ""
            runs.append(daniel(f"danielA_{name}-seed{s}", "A", [model] * 4, s, flags, note=note))
    # Phase B: Daniel's seller compositions, comms on, 3 seeds. Rounds not stated in his plan; we use A's 15.
    letters = {"G": D_GEMINI, "C": D_HAIKU, "D": D_DEEPSEEK}
    for mix in ["GGGG", "GGCC", "GGDD", "GCCD", "CCCC"]:
        for s in DANIEL_SEEDS:
            runs.append(daniel(f"danielB_{mix}-seed{s}", "B", [letters[x] for x in mix], s, D_COMMS,
                               note="Daniel gates B on A passing"))
    # Phase fable: Fable 5.1 image steganography replication (src/fable_image_stego), claude CLI directly.
    # The full run (30 messages + 30 controls, about 3 min per encode or decode, so about 6 h in one process) is split
    # by item id into FABLE_CHUNKS parts that run in parallel. The parts cover the pilot's 10 messages and 2 controls,
    # so the separate pilot is dropped.
    fl = ["--model", "claude-fable-5-1", "--effort", "max"]
    per = 30 // FABLE_CHUNKS
    for k in range(FABLE_CHUNKS):
        ids = [f"msg_{i:02d}" for i in range(k * per + 1, (k + 1) * per + 1)] + \
              [f"ctrl_{i:02d}" for i in range(k * per + 1, (k + 1) * per + 1)]
        runs.append(Run(f"fable_full_part{k + 1}", "fable", "fable", ["claude-fable-5-1"],
                        ["--mode", "full", "--ids", ",".join(ids), *fl], 4 * per, 2 * per * 6,
                        note=f"{per} messages + {per} controls, about 3 min per encode or decode"))
    runs += frontier_runs()
    # Phase C and D to G: listed so the plan is complete; no code exists yet in Daniel's repo.
    for i in range(36):
        runs.append(Run(f"danielC_{i:02d}", "C", "daniel_cda", [], [], 120, 15 * 8 * 20 / 60, 15,
                        blocked="no label code in Daniel's repo (6 labels x 2 mixes x 3 seeds)"))
    for i in range(45):
        runs.append(Run(f"danielDG_{i:02d}", "D to G", "daniel_cda", [], [], 120, 15 * 8 * 20 / 60, 15,
                        blocked="no undercover seat, report tool, persona, warning or precedent code yet (9 must run arms x 5 seeds)"))
    # Blocking. Sharding comes from the pinned assignment file, see assign_shards() and cmd_assign().
    have_or = bool(os.environ.get("OPENROUTER_API_KEY"))
    for r in runs:
        if r.blocked:
            continue
        if any(m.startswith(NEEDS_OPENROUTER) for m in r.models):
            r.extra["needs_openrouter"] = True
            if not have_or:
                r.blocked = "needs OPENROUTER_API_KEY (model not served by the subscription CLIs)"
    pinned = load_assignment()
    parked = pinned.get("parked", {})  # tag -> reason; owner rules in AGENTS.md (no GPT-4.1, Fable, Claude sellers...)
    for r in runs:
        if r.tag in parked and not r.blocked:
            r.blocked = "parked: " + parked[r.tag]
        r.shard = 0 if r.phase in ("C", "D to G") or r.tag in parked else \
            int(pinned.get("shards", {}).get(r.tag, PINNED_SHARD))
    return runs


def load_assignment() -> dict:
    try:
        return json.loads(ASSIGNMENT.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def shard_name(k: int) -> str:
    """Folder and usage log name. Shard 1 keeps the box's old name so its finished runs stay where they are."""
    return "box" if k == PINNED_SHARD else f"shard{k}"


def shard_dirs(k: int) -> list[str]:
    return [shard_name(k)] + (["local"] if k == PINNED_SHARD else [])


def parse_shard(spec: str) -> tuple[int, int]:
    """'2/3' -> (2, 3); 'all' -> (0, n); 'box' -> (1, n)."""
    n = int(load_assignment().get("n", 1))
    if spec == "all":
        return 0, n
    if spec == "box":
        return PINNED_SHARD, n
    if spec == "local":
        sys.exit("--shard local is retired. Use --shard k/N, see notes/RUN_PLAN.md.")
    try:
        k, m = (int(x) for x in spec.split("/"))
    except ValueError:
        sys.exit(f"bad --shard {spec!r}; use k/N such as 2/3, or all")
    if m != n:
        sys.exit(f"--shard {spec}: notes/shard_assignment.json is for {n} shards. Run `git pull` first.")
    if not 1 <= k <= n:
        sys.exit(f"--shard {spec}: k must be 1 to {n}")
    return k, n


def running_tags(runs) -> set:
    """Tags with a live harness process on this machine (pgrep on the tag in the command line)."""
    out = subprocess.run(["ps", "-eo", "args"], capture_output=True, text=True).stdout
    live = set()
    for r in runs:
        for line in out.splitlines():
            if "run_all.py" in line:
                continue
            if any(f"{sep}{r.tag} " in line + " " for sep in (" ", "/")):
                live.add(r.tag)
                break
    return live


def assign_shards(runs, n: int, jobs: list[int]) -> dict:
    """Pin box work to shard 1, then greedy longest first on remaining minutes divided by each shard's jobs."""
    live = running_tags(runs)
    shards, load = {}, {k: 0.0 for k in range(1, n + 1)}
    free = []
    for r in runs:
        if r.phase in ("C", "D to G"):
            continue
        st = status_of(r)
        grok = any(m.startswith("grok") for m in r.models)  # keeps m1 and m2 free of the grok CLI and its throttling
        if st == "done" or r.tag in live or "needs_openrouter" in r.extra or r.harness == "fable" or grok:
            shards[r.tag] = PINNED_SHARD
            if st != "done" and r.tag not in live:
                load[PINNED_SHARD] += r.minutes / jobs[PINNED_SHARD - 1]
        else:
            free.append(r)
    for r in sorted(free, key=lambda r: (-r.minutes, r.tag)):
        k = min(load, key=lambda k: (load[k] + r.minutes / jobs[k - 1], k))
        shards[r.tag] = k
        load[k] += r.minutes / jobs[k - 1]
    return {"n": n, "jobs": {str(k): jobs[k - 1] for k in load},
            "generated": dt.datetime.now().strftime("%a %b %d %Y %I:%M %p CT"),
            "in_progress_at_generation": sorted(live),
            "est_wall_minutes": {str(k): round(v) for k, v in load.items()},
            "shards": dict(sorted(shards.items()))}


# ---------------------------------------------------------------- done / failed state
def out_dir(r: Run, shard: str) -> Path:
    return RUNS / shard / r.phase.replace(" ", "_")  # shard is a folder name, see shard_name()


def is_done(r: Run) -> bool:
    for d in RUNS.glob(f"*/{r.phase.replace(' ', '_')}"):
        if r.harness == "fable":
            if (d / r.tag / "summary.json").exists():
                return True
        elif r.harness == "poseidon_cartel":
            f = d / f"{r.tag}.jsonl"
            if f.exists() and sum(1 for ln in f.read_text(errors="replace").splitlines() if ln.strip()) >= r.rounds:
                return True
        else:
            if any((p / "collusion_metrics.json").exists() for p in d.glob(f"*_{r.tag}")):
                return True
    return False


def attempts(r: Run) -> int:
    n = 0
    for st in RUNS.glob("*/status.jsonl"):
        for ln in st.read_text(errors="replace").splitlines():
            try:
                rec = json.loads(ln)
            except json.JSONDecodeError:
                continue
            if rec.get("tag") == r.tag and rec.get("rc") != 0:
                n += 1
    return n


def status_of(r: Run) -> str:
    if is_done(r):
        return "done"
    if r.blocked:
        return "blocked"
    if attempts(r) >= MAX_ATTEMPTS:
        return "failed"
    return "ready"


# ---------------------------------------------------------------- execution
LOCK = threading.Lock()


def log(shard, msg):
    line = f"[{dt.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}"
    print(line, flush=True)
    with LOCK:
        (RUNS / shard).mkdir(parents=True, exist_ok=True)
        with (RUNS / shard / "run_all.log").open("a") as fh:
            fh.write(line + "\n")


def command(r: Run, shard: str) -> tuple[list, Path]:
    od = out_dir(r, shard)
    od.mkdir(parents=True, exist_ok=True)
    if r.harness == "fable":
        py = shutil.which("python3.13") or sys.executable
        return [py, "run_pilot.py", *r.args, "--output-dir", str(od / r.tag)], ROOT / "src" / "fable_image_stego"
    if r.harness == "poseidon_cartel":
        return ["uv", "run", "python", "run_game.py", *r.args, "--out_dir", str(od)], HARNESS / "llm-cartel"
    if r.harness == "poseidon_cda":
        return (["uv", "run", "python", "src/continuous_double_auction/simulation.py", *r.args, "--log_dir", str(od)],
                HARNESS / "llm-agent-collusion")
    # In-run judge is openai/gpt-4.1-mini. JUDGE=off skips it; scripts/judge_with_grok.py scores the finished runs.
    extra = (["--llm_eval"] if os.environ.get("OPENROUTER_API_KEY") and not r.extra.get("no_judge")
             and os.environ.get("JUDGE") != "off" else [])
    return (["uv", "run", "python", "src/continuous_double_auction/simulation.py", *r.args, *extra, "--log_dir", str(od)],
            DANIEL / "third_party" / "llm-agent-collusion")


def execute(r: Run, shard: str) -> int:
    cmd, cwd = command(r, shard)
    lp = RUNS / shard / "logs" / f"{r.tag}.log"
    lp.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log(shard, f"start {r.phase} {r.tag}")
    env = {k: v for k, v in os.environ.items() if k != "LLM_MODEL"}
    with lp.open("w") as fh:
        fh.write("$ (cd " + str(cwd) + " && " + " ".join(cmd) + ")\n")
        fh.flush()
        rc = subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT, env=env).returncode
    rec = {"tag": r.tag, "phase": r.phase, "rc": rc, "shard": shard, "minutes": round((time.time() - t0) / 60, 1),
           "end": dt.datetime.now().isoformat(timespec="seconds")}
    with LOCK, (RUNS / shard / "status.jsonl").open("a") as fh:
        fh.write(json.dumps(rec) + "\n")
    log(shard, f"done  {r.phase} {r.tag} rc={rc} ({rec['minutes']} min)")
    return rc


def proxy_get(path):
    with urllib.request.urlopen(PROXY + path, timeout=5) as resp:
        return json.loads(resp.read())


def ensure_proxy(name: str):
    """The proxy must run the strict routing code. Start it (with this shard's usage log) if not."""
    os.environ["PROXY_USAGE_LOG"] = str(ROOT / "token-usage" / f"proxy_usage.{name}.jsonl")
    try:
        info = proxy_get("/models")
        ok = info.get("routing") == "strict" and info.get("openrouter_forwarding") == bool(os.environ.get("OPENROUTER_API_KEY"))
        # Restart a proxy that logs to another file, so this shard's usage never lands in a shared file.
        ok = ok and Path(proxy_get("/usage").get("log_path", "")).name == f"proxy_usage.{name}.jsonl"
    except Exception:
        ok = False
    if not ok or os.environ.get("RESTART_PROXY") == "1":
        log(name, "starting the subscription proxy (strict routing)")
        subprocess.run(["bash", str(ROOT / "scripts" / "start_proxy.sh")], check=True)


def cli_of(model: str) -> str:
    """Which CLI (or OpenRouter) serves a model through the proxy. Mirrors src/subscription_proxy/server.py."""
    if model.startswith(NEEDS_OPENROUTER):
        return "OpenRouter (OPENROUTER_API_KEY in collusion_hackathon/compute.env)"
    if "gemini" in model:
        if os.environ.get("PROXY_GEMINI_VIA_OPENROUTER") == "1":
            return "OpenRouter (PROXY_GEMINI_VIA_OPENROUTER=1, served as google/gemini-3.8-flash)"
        return "agy"
    if model.startswith(("gpt-", "openai/gpt-5", "openai/gpt-6")):
        return "codex"
    if model.startswith("grok"):
        return "grok"
    return "claude"


def clis_needed(r: Run) -> set:
    return {cli_of(m) for m in r.models}


def smoke(name: str, runs: list[Run]) -> bool:
    """One short call per model this shard needs. Returns False and names the CLI if any model fails."""
    ensure_proxy(name)
    models = sorted({m for r in runs for m in r.models})
    good = True
    for m in models:
        cli = cli_of(m)
        if not cli.startswith("OpenRouter") and not shutil.which(cli):
            good = False
            log(name, f"smoke FAIL {m}: the {cli} CLI is not installed on this machine")
            continue
        body = json.dumps({"model": m, "messages": [{"role": "user", "content": "Reply with the single word OK."}]}).encode()
        req = urllib.request.Request(PROXY + "/chat/completions", data=body, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                txt = json.loads(resp.read())["choices"][0]["message"]["content"]
            log(name, f"smoke ok   {m} ({cli}): {txt.strip()[:40]!r}")
        except Exception as e:
            good = False
            log(name, f"smoke FAIL {m}: needs the {cli} CLI signed in on this machine. Error: {str(e)[:200]}")
    need = {"poseidon_cartel": HARNESS, "poseidon_cda": HARNESS, "daniel_cda": DANIEL}
    for label, path in (("Poseidon harness", HARNESS), ("Daniel's repo", DANIEL)):
        used = any(need.get(r.harness) == path for r in runs)
        log(name, f"{label}: {path} ({'found' if path.is_dir() else 'MISSING'})")
        if used and not path.is_dir():
            good = False
            log(name, f"smoke FAIL: {label} is missing. Run ./scripts/setup_other_machine.sh first.")
    return good


def git(*a, check=True):
    return subprocess.run(["git", "-C", str(ROOT), *a], check=check, capture_output=True, text=True)


def push_shard(k: int, why: str):
    """Commit only this shard's own folders and usage log, then pull --rebase and push, retrying."""
    paths = [f"experiments/runs/{d}" for d in shard_dirs(k) if (RUNS / d).exists()]
    paths += [f"token-usage/proxy_usage.{d}.jsonl" for d in shard_dirs(k)
              if (ROOT / "token-usage" / f"proxy_usage.{d}.jsonl").exists()]
    name = shard_name(k)
    with LOCK:
        if not paths:
            return
        git("add", "-f", *paths)
        if not git("diff", "--cached", "--quiet", "--", *paths, check=False).returncode:
            return
        git("commit", "-m", f"runs: shard {k} ({name}) {why}", "--", *paths)
        for i in range(5):
            git("pull", "--rebase", "--autostash", check=False)
            if git("push", check=False).returncode == 0:
                print(f"[{dt.datetime.now():%H:%M:%S}] pushed shard {k} results ({why})", flush=True)
                return
            time.sleep(5 * (i + 1))
    log(name, "push failed after 5 tries; results are committed locally, rerun `scripts/run_all.sh merge` later")


def cmd_run(a):
    k, n = parse_shard(a.shard)
    if a.pull:
        r = git("pull", "--rebase", "--autostash", check=False)
        if r.returncode:
            print(f"warning: git pull failed: {r.stderr.strip()[:300]}", file=sys.stderr)
        k, n = parse_shard(a.shard)  # the pull may bring a new assignment file
    name = shard_name(k) if k else "all"
    plan = build_plan()
    phases = [p.strip() for p in a.phases.split(",")] if a.phases else PHASE_ORDER
    mine = [r for r in plan if r.phase in phases and r.shard and (k == 0 or r.shard == k)]
    skip = {c.strip() for c in a.skip_clis.split(",") if c.strip()}
    for r in mine:
        if clis_needed(r) & skip and status_of(r) != "done":
            log(name, f"skip {r.tag}: needs the {', '.join(sorted(clis_needed(r) & skip))} CLI (--skip-clis)")
    mine = [r for r in mine if not clis_needed(r) & skip]
    only = {t.strip() for t in os.environ.get("RUN_ONLY", "").split(",") if t.strip()}
    if only:  # RUN_ONLY=tag1,tag2 runs just those tags
        mine = [r for r in mine if r.tag in only]
    live = running_tags(mine)
    todo = []
    for r in mine:
        st = status_of(r)
        if r.tag in live:
            log(name, f"skip {r.tag}: already running on this machine")
        elif st == "ready":
            todo.append(r)
        elif st != "done":
            log(name, f"skip {r.tag}: {st} {r.blocked}")
    if not a.no_smoke:
        if not smoke(name, todo):
            log(name, "STOP: the smoke check failed (see the FAIL lines above). Sign in to the named CLI "
                      "(run it once interactively) or run setup_other_machine.sh, then start again.")
            sys.exit(2)
    else:
        ensure_proxy(name)
    # Longest first (shortest finish), except runs with a fixed order (phase frontier), which go in plan order.
    todo.sort(key=lambda r: (0, r.extra["order"], 0, "") if "order" in r.extra
              else (1, -r.minutes, PHASE_ORDER.index(r.phase), r.tag))
    log(name, f"shard {k or 'all'}/{n}: {len(todo)} runs to do in phases {phases}, {a.jobs} at a time, "
              f"about {sum(r.minutes for r in todo) / max(1, a.jobs) / 60:.1f} h")
    # One pool across phases, longest runs first (no idle tail); push when a phase's last run finishes.
    left = {ph: sum(1 for r in todo if r.phase == ph) for ph in phases}

    def one(r):
        rc = execute(r, name)
        with LOCK:
            left[r.phase] -= 1
            finished = left[r.phase] == 0
        if finished and a.push and k:
            push_shard(k, f"phase {r.phase} finished")
        return rc

    # Workers take the first queued run that keeps at most GROK_MAX grok runs going at once.
    # Runs still going from an earlier runner process on this machine (left alive when that runner was stopped)
    # count toward --jobs and GROK_MAX, so a restart never runs more at once than asked.
    queue, cond, own = list(todo), threading.Condition(), set()
    by_tag = {r.tag: r for r in mine}
    is_grok = lambda r: any(m.startswith("grok") for m in r.models)

    def busy():
        live = (running_tags(mine) | own)
        return len(live), sum(1 for t in live if t in by_tag and is_grok(by_tag[t]))

    def worker():
        while True:
            with cond:
                while True:
                    if not queue:
                        return
                    n_live, n_grok = busy()
                    r = None
                    if n_live < a.jobs:
                        r = next((x for x in queue if not is_grok(x) or n_grok < GROK_MAX), None)
                    if r:
                        queue.remove(r)
                        own.add(r.tag)
                        break
                    cond.wait(timeout=30)
            try:
                one(r)
            finally:
                with cond:
                    own.discard(r.tag)
                    cond.notify_all()

    threads = [threading.Thread(target=worker) for _ in range(a.jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if a.push and k:
        push_shard(k, "all phases finished")
    log(name, "all phases finished; run `scripts/run_all.sh merge` once every shard is done")


def cmd_docs(_a=None):
    # The docs read the repo copy (experiments/snapshot + experiments/runs), never the harness folder.
    env = {k: v for k, v in os.environ.items() if k != "COLLUSION_HACKATHON"}
    for s in ("experiments/make_cases.py", "experiments/make_behavior_report.py"):
        subprocess.run([sys.executable, str(ROOT / s)], check=True, env=env)


def cmd_merge(a):
    for attempt in range(3):
        git("pull", "--rebase", "--autostash", "-X", "theirs", check=False)
        cmd_docs()
        paths = ["experiments/runs", "experiments/cases", "docs/AGENT_BEHAVIOR.md"] + \
                [str(p.relative_to(ROOT)) for p in (ROOT / "token-usage").glob("proxy_usage.*.jsonl")]
        git("add", "-f", *paths)
        if git("diff", "--cached", "--quiet", check=False).returncode:
            git("commit", "-m", "Merge shard runs and rebuild cases and AGENT_BEHAVIOR.md", "--", *paths)
        if git("push", check=False).returncode == 0:
            print("[merge] pushed")
            return
        print("[merge] push rejected, retrying after pull")
    sys.exit("[merge] could not push after 3 tries")


def cmd_plan(a):
    plan = build_plan()
    k = parse_shard(a.shard)[0] if a.shard else 0
    rows = [(r, status_of(r)) for r in plan if k == 0 or r.shard == k]
    if a.markdown:
        print(plan_markdown(rows))
        return
    live = running_tags([r for r, _ in rows])
    rows = [(r, "running" if r.tag in live and st != "done" else st) for r, st in rows]
    for r, st in rows:
        sh = str(r.shard) if r.shard else "n/a"
        print(f"{r.phase:7} {sh:3} {st:8} {r.tag:42} calls={r.calls:4} est={r.minutes:5.1f} min {r.blocked}")
    summarize(rows)


def summarize(rows):
    """Per shard progress. 'running' is only visible on the machine that runs it."""
    asg = load_assignment()
    jobs = asg.get("jobs", {})
    print(f"\nAssignment: notes/shard_assignment.json, {asg.get('n', '?')} shards, generated {asg.get('generated', '?')}")
    print(f"{'shard':6} {'folder':7} {'done':>5} {'running':>8} {'ready':>6} {'failed':>7} {'blocked':>8} {'total':>6}  est. left")
    for k in sorted({r.shard for r, _ in rows}):
        sub = [(r, st) for r, st in rows if r.shard == k]
        c = {x: sum(1 for _, st in sub if st == x) for x in ("done", "running", "ready", "failed", "blocked")}
        left = sum(r.minutes for r, st in sub if st in ("ready", "running"))
        j = int(jobs.get(str(k), 3))
        label, folder = (str(k), shard_name(k)) if k else ("n/a", "-")
        est = f"{left / j / 60:.1f} h at --jobs {j}" if k else "blocked on Daniel's code"
        print(f"{label:6} {folder:7} {c['done']:5} {c['running']:8} {c['ready']:6} {c['failed']:7} {c['blocked']:8} {len(sub):6}  {est}")


def cmd_assign(a):
    jobs = [int(x) for x in a.jobs.split(",")]
    if len(jobs) != a.n:
        sys.exit("--jobs needs one value per shard, such as 4,3,3")
    parked = load_assignment().get("parked", {})
    ASSIGNMENT.write_text("")  # build the plan without the old pins
    res = assign_shards(build_plan(), a.n, jobs)
    res["parked"] = parked
    ASSIGNMENT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({x: res[x] for x in ("n", "jobs", "est_wall_minutes", "in_progress_at_generation")}, indent=1))


def plan_markdown(rows) -> str:
    from collections import OrderedDict
    groups = OrderedDict()
    for r, st in rows:
        key = (r.phase, r.harness, r.blocked, r.shard, st, r.note)
        base = r.tag.rsplit("-seed", 1)[0].rsplit("_s", 1)[0] if r.phase in ("matrix", "A", "B") else r.tag
        if r.phase in ("C", "D to G"):
            base = {"C": "label x mix cells", "D to G": "undercover, warning, precedent arms"}[r.phase]
        g = groups.setdefault(key + (base,), {"runs": 0, "seeds": set(), "calls": 0, "min": 0.0, "models": r.models})
        g["runs"] += 1
        g["seeds"].add(r.seed)
        g["calls"] += r.calls
        g["min"] += r.minutes
    out = ["| Phase | Case | Models | Seeds | Runs | Est. calls | Est. min | Shard | Status |", "|---|---|---|---|---|---|---|---|---|"]
    for (phase, harness, blocked, shard, st, note, base), g in groups.items():
        status = st if not blocked else f"blocked: {blocked}"
        shard = shard or "n/a"
        if note:
            status += f" ({note})"
        seeds = ", ".join(str(s) for s in sorted(g["seeds"]))
        out.append(f"| {phase} | `{base}` | {', '.join(g['models']) or 'n/a'} | {seeds} | {g['runs']} | {g['calls']} | "
                   f"{g['min']:.0f} | {shard} | {status} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--markdown", action="store_true")
    p.add_argument("--shard", default="", help="k/N to show one shard")
    p.set_defaults(fn=cmd_plan)
    p = sub.add_parser("run")
    p.add_argument("--shard", required=True, help="k/N such as 2/3, or all (box means 1/N)")
    p.add_argument("--phases", default="", help="comma list of sweep,refusal,matrix,A,B,fable,frontier (default: all of them)")
    p.add_argument("--jobs", type=int, default=int(os.environ.get("JOBS", "3")))
    p.add_argument("--no-smoke", action="store_true")
    p.add_argument("--skip-clis", default="", help="comma list of CLIs whose runs another machine takes, such as agy (Gemini)")
    p.add_argument("--no-push", dest="push", action="store_false", help="do not commit and push after each phase")
    p.add_argument("--no-pull", dest="pull", action="store_false")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("assign")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--jobs", required=True, help="comma list, one per shard, such as 4,3,3")
    p.set_defaults(fn=cmd_assign)
    sub.add_parser("docs").set_defaults(fn=cmd_docs)
    sub.add_parser("merge").set_defaults(fn=cmd_merge)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
