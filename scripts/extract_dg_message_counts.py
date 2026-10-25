"""Per-run message, reply and report counts for the D-G Gemini runs (report Table 3).

Parses each LLM seller's `Seller <name>.md` log (one JSON response per hour) and the
run's collusion_metrics.json (regulator reports, dm_summary). The run logs are local
and gitignored; the output CSV is committed as report/data/dg/table3_extra.csv.

Columns: public_msgs (hours with a public message), private_msgs_peer (private messages
between LLM sellers), private_msgs_to_seat5, private_msgs_llm_total, dm_summary_llm_total
(the harness's own count, as a cross-check), replied_to_seat5_from_h4 (distinct sellers
who messaged seat 5 from hour 4 on), msgs_to_seat5_from_h4, reported_seat5 (distinct
sellers with any report naming seat 5), reported_anyone, reports_total (with repeats).

Usage: python scripts/extract_dg_message_counts.py <results/dg> <out.csv>
"""
import csv
import json
import re
import sys
from pathlib import Path


def main(root: Path, out: Path) -> None:
    rows = []
    for d in sorted(root.glob('2026*-seed*')):
        arm, seed = d.name.split('_', 2)[2].rsplit('-seed', 1)
        meta = json.load(open(next(d.rglob('experiment_metadata.json')), encoding='utf-8'))
        metrics = json.load(open(next(d.rglob('collusion_metrics.json')), encoding='utf-8'))
        s5 = meta['scripted_seats'][0]
        pub = priv_peer = priv_to5 = priv_to5_h4 = 0
        repliers, rep5, rep_any = set(), set(), set()
        for f in sorted(d.glob('Seller *.md')):
            name = f.stem
            if name == s5:
                continue
            text = f.read_text(encoding='utf-8')
            resp = {}
            for m in re.finditer(r'## Response: Round (\d+)[^\n]*\n````json\n(.*?)\n````', text, re.S):
                try:
                    resp[int(m.group(1))] = json.loads(m.group(2))  # last parsed response per hour wins
                except json.JSONDecodeError:
                    pass
            for hour, o in resp.items():
                if o.get('message_to_sellers'):
                    pub += 1
                for dm in (o.get('direct_messages') or []):
                    if not isinstance(dm, dict) or not dm.get('to'):
                        continue
                    if dm['to'] == s5:
                        priv_to5 += 1
                        if hour >= 4:
                            priv_to5_h4 += 1
                            repliers.add(name)
                    else:
                        priv_peer += 1
        reports = metrics.get('regulator_reports') or []
        for rep in reports:
            rep_any.add(rep['from'])
            if rep['about'] == s5:
                rep5.add(rep['from'])
        dms = metrics['dm_summary']
        rows.append(dict(run_id=d.name, arm=arm, seed=int(seed), scripted_seat=s5,
                         public_msgs=pub, private_msgs_peer=priv_peer, private_msgs_to_seat5=priv_to5,
                         private_msgs_llm_total=priv_peer + priv_to5,
                         dm_summary_llm_total=dms['total'] - dms['by_sender'].get(s5, 0),
                         replied_to_seat5_from_h4=len(repliers), msgs_to_seat5_from_h4=priv_to5_h4,
                         reported_seat5=len(rep5), reported_anyone=len(rep_any), reports_total=len(reports)))
    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), 'runs ->', out)


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
