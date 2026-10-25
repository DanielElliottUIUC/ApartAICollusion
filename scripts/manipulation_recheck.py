"""Step C in-context manipulation check (post hoc): re-ask each seller the identity question with its final-hour
prompt attached, and classify the answer with the harness's keyword rule.

    uv run --project third_party/llm-agent-collusion python scripts/manipulation_recheck.py

Reads every run under results/c/*_C-*-seed*, takes the last "## Prompt: Round N" block of each Seller <Name>.md,
appends the question from evaluation/manipulation_check.py and asks for a top-level JSON field "for_the_record",
then writes <run>/manipulation_check_incontext.json with answer, for_the_record, label and class
(repeats / rejects / ignores / error). Costs about $1 for 72 Gemini calls (reasoning tokens). Written Sun Oct 25
because the in-run check asked the bare question without the market prompt and every seller answered as Gemini.
"""
import glob, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, r"C:\Users\danie\Hackathons\ApartAICollusion\third_party\llm-agent-collusion")
os.chdir(r"C:\Users\danie\Hackathons\ApartAICollusion\third_party\llm-agent-collusion")
from src.continuous_double_auction.util.misc import get_client
from src.continuous_double_auction.evaluation.manipulation_check import classify_answer, QUESTION
from src.resources.model_wrappers import Message
ROOT = r"C:\Users\danie\Hackathons\ApartAICollusion"
def last_prompt(md):
    blocks = re.findall(r"## Prompt: Round (\d+)[^\n]*\n+``````\n(.*?)\n``````", md, flags=re.S)
    if not blocks: blocks = re.findall(r"## Prompt: Round (\d+)[^\n]*\n+```+\n(.*?)\n```+", md, flags=re.S)
    return max(blocks, key=lambda b: int(b[0]))[1] if blocks else None
tasks = []
for run in sorted(glob.glob(os.path.join(ROOT, "results", "c", "*_C-*-seed*"))):
    meta = json.load(open(os.path.join(run, "experiment_metadata.json")))
    label = meta["shared_label"]; model = meta["resolved_models"]["sellers"][0]
    for sid in meta["seller_ids"]:
        md = open(os.path.join(run, f"{sid}.md"), encoding="utf-8").read()
        p = last_prompt(md)
        if p: tasks.append((run, label, model, sid, p))
print(len(tasks), "seller prompts found")
client = get_client(model=tasks[0][2], temperature=0.7, max_tokens=16000)
def ask(t):
    run, label, model, sid, prompt = t
    content = prompt + "\n\n---\n" + QUESTION + " Put the answer in a top-level JSON field named \"for_the_record\"."
    try: ans = client.generate(messages=[Message(role="user", content=content)]) or ""
    except Exception as e: ans = ""; print("fail", sid, e)
    import json as _j
    rec = ans
    try:
        d = _j.loads(ans[ans.index("{"):ans.rindex("}")+1]); rec = str(d.get("for_the_record") or ans)
    except Exception: pass
    return run, sid, {"answer": ans, "for_the_record": rec, "label": label, "class": classify_answer(rec, label)}
out = {}
with ThreadPoolExecutor(4) as ex:
    for run, sid, rec in ex.map(ask, tasks): out.setdefault(run, {})[sid] = rec
from collections import Counter
agg = {}
for run, d in out.items():
    json.dump(d, open(os.path.join(run, "manipulation_check_incontext.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    label = next(iter(d.values()))["label"]; agg.setdefault(label, Counter()).update(v["class"] for v in d.values())
for label, c in agg.items(): print(f"{label:10} {dict(c)}")
print("--- samples ---")
for run, d in list(out.items())[::3]:
    sid, v = next(iter(d.items())); print(f"[{v['label']}] {v['for_the_record'][:260]!r}")
