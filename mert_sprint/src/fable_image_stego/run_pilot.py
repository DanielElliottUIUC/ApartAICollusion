#!/usr/bin/env python3.13
"""Unified runner for Fable 5.1 image steganography replication experiments."""

import argparse
import datetime
import json
import pathlib
from zoneinfo import ZoneInfo

from decode import run_decode
from encode import run_encode
from grade import grade_item, summarize_graded_items

HERE = pathlib.Path(__file__).resolve().parent
CT_ZONE = ZoneInfo("America/Chicago")


def default_run_dir(mode: str) -> pathlib.Path:
    ts = datetime.datetime.now(CT_ZONE).strftime("%Y%m%d_%H%M%S")
    return HERE / "runs" / f"{mode}_{ts}"


def run_examples_mode(
    run_dir: pathlib.Path,
    model: str,
    effort: str,
    limit: int | None = None,
    ids: list[str] | None = None,
) -> list[dict]:
    manifest = json.loads((HERE / "examples" / "manifest.json").read_text(encoding="utf-8"))
    examples = manifest["examples"]
    if ids:
        id_set = set(ids)
        examples = [ex for ex in examples if ex["id"] in id_set]
    if limit is not None:
        examples = examples[:limit]

    graded_rows = []
    for ex in examples:
        item_id = ex["id"]
        item_dir = run_dir / item_id
        item_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "item_id": item_id,
            "is_benign_control": False,
            "ground_truth": ex["ground_truth"],
            "encoding_family": ex["encoding_family"],
            "source_image_path": ex["image_path"],
            "sha256": ex["sha256"],
        }
        (item_dir / "item_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

        img_path = HERE / ex["image_path"]
        print(f"[run_pilot] Decoding author example {item_id} ({img_path.name}) ...")
        dec = run_decode(
            image_path=img_path,
            output_path=item_dir / "decode_log.json",
            item_id=item_id,
            model=model,
            effort=effort,
        )
        row = grade_item(
            item_id=item_id,
            ground_truth=ex["ground_truth"],
            predicted=dec["final_answer"],
            encoding_family=ex["encoding_family"],
            is_benign_control=False,
            elapsed_encode_sec=None,
            elapsed_decode_sec=dec["elapsed_sec"],
            num_tool_calls=dec["num_tool_calls"],
        )
        graded_rows.append(row)
        print(
            f"[run_pilot] Done {item_id}: truth={ex['ground_truth']!r} "
            f"decoded={dec['final_answer']!r} seq_sim={row['sequence_matcher_ratio']} "
            f"recovered={row['recovered_90pct']}"
        )
    return graded_rows


def run_encode_decode_batch(
    run_dir: pathlib.Path,
    stego_items: list[dict],
    control_items: list[dict],
    model: str,
    effort: str,
) -> list[dict]:
    graded_rows = []

    for item in stego_items:
        item_id = item["id"]
        secret_msg = item["message"]
        item_dir = run_dir / item_id
        item_dir.mkdir(parents=True, exist_ok=True)

        print(f"[run_pilot] Encoding {item_id}: message={secret_msg!r} ...")
        enc = run_encode(
            output_dir=item_dir,
            message=secret_msg,
            item_id=item_id,
            model=model,
            effort=effort,
            ask_method=True,
        )
        print(
            f"[run_pilot] Encoded {item_id} in {enc['elapsed_sec']}s "
            f"(family={enc['encoding_family']}, size={enc['dimensions']}). Decoding ..."
        )

        dec = run_decode(
            image_path=pathlib.Path(enc["png_path"]),
            output_path=item_dir / "decode_log.json",
            item_id=item_id,
            model=model,
            effort=effort,
        )
        row = grade_item(
            item_id=item_id,
            ground_truth=secret_msg,
            predicted=dec["final_answer"],
            encoding_family=enc["encoding_family"],
            is_benign_control=False,
            elapsed_encode_sec=enc["elapsed_sec"],
            elapsed_decode_sec=dec["elapsed_sec"],
            num_tool_calls=dec["num_tool_calls"],
        )
        graded_rows.append(row)
        print(
            f"[run_pilot] Done {item_id}: truth={secret_msg!r} "
            f"decoded={dec['final_answer']!r} seq_sim={row['sequence_matcher_ratio']} "
            f"recovered={row['recovered_90pct']}"
        )

    for ctrl in control_items:
        item_id = ctrl["id"]
        scene = ctrl["scene"]
        item_dir = run_dir / item_id
        item_dir.mkdir(parents=True, exist_ok=True)

        print(f"[run_pilot] Generating benign control {item_id}: scene={scene!r} ...")
        enc = run_encode(
            output_dir=item_dir,
            benign_scene=scene,
            item_id=item_id,
            model=model,
            effort=effort,
            ask_method=False,
        )
        print(f"[run_pilot] Generated {item_id} in {enc['elapsed_sec']}s. Decoding ...")
        dec = run_decode(
            image_path=pathlib.Path(enc["png_path"]),
            output_path=item_dir / "decode_log.json",
            item_id=item_id,
            model=model,
            effort=effort,
        )
        row = grade_item(
            item_id=item_id,
            ground_truth=None,
            predicted=dec["final_answer"],
            encoding_family="benign_control",
            is_benign_control=True,
            elapsed_encode_sec=enc["elapsed_sec"],
            elapsed_decode_sec=dec["elapsed_sec"],
            num_tool_calls=dec["num_tool_calls"],
        )
        graded_rows.append(row)
        print(
            f"[run_pilot] Done control {item_id}: decoded={dec['final_answer']!r} "
            f"false_alarm={row['false_alarm']}"
        )

    return graded_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Fable 5.1 image steganography replication experiments.")
    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["examples", "smoke", "pilot", "full"],
        help="Execution mode: examples (3 author PNGs), smoke (1 fresh encode+decode), pilot (10 messages + 2 controls), full (30 messages + 30 controls).",
    )
    parser.add_argument("--output-dir", type=pathlib.Path, default=None, help="Directory to store run outputs.")
    parser.add_argument("--model", type=str, default="claude-fable-5-1", help="Claude model name.")
    parser.add_argument("--effort", type=str, default="max", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--limit", type=int, default=None, help="Override number of stego items or author examples.")
    parser.add_argument("--num-controls", type=int, default=None, help="Override number of benign control items.")
    parser.add_argument("--ids", type=str, default=None, help="Comma-separated list of item IDs to run.")
    parser.add_argument("--message", type=str, default=None, help="Custom secret message for --mode smoke.")
    args = parser.parse_args()

    run_dir = (args.output_dir or default_run_dir(args.mode)).resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    id_list = [x.strip() for x in args.ids.split(",") if x.strip()] if args.ids else None

    if args.mode == "examples":
        rows = run_examples_mode(
            run_dir=run_dir,
            model=args.model,
            effort=args.effort,
            limit=args.limit,
            ids=id_list,
        )
    else:
        dataset = json.loads((HERE / "data" / "messages.json").read_text(encoding="utf-8"))
        stego_all = dataset["stego_messages"]
        ctrl_all = dataset["benign_controls"]

        if id_list:
            id_set = set(id_list)
            stego_all = [x for x in stego_all if x["id"] in id_set]
            ctrl_all = [x for x in ctrl_all if x["id"] in id_set]

        if args.mode == "smoke":
            if args.message:
                stego_items = [{"id": "smoke_01", "category": "custom", "language": "en", "message": args.message}]
            else:
                stego_items = stego_all[: (args.limit or 1)]
            ctrl_items = ctrl_all[: (args.num_controls or 0)]
        elif args.mode == "pilot":
            n_stego = args.limit if args.limit is not None else 10
            n_ctrl = args.num_controls if args.num_controls is not None else 2
            stego_items = stego_all[:n_stego]
            ctrl_items = ctrl_all[:n_ctrl]
        else:  # full
            n_stego = args.limit if args.limit is not None else len(stego_all)
            n_ctrl = args.num_controls if args.num_controls is not None else len(ctrl_all)
            stego_items = stego_all[:n_stego]
            ctrl_items = ctrl_all[:n_ctrl]

        rows = run_encode_decode_batch(
            run_dir=run_dir,
            stego_items=stego_items,
            control_items=ctrl_items,
            model=args.model,
            effort=args.effort,
        )

    summarize_graded_items(rows, output_dir=run_dir)
    print(f"[run_pilot] Saved summary to {run_dir / 'summary.json'} and {run_dir / 'summary.csv'}")


if __name__ == "__main__":
    main()
