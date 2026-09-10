"""OpenLearn AI — Eval Harness CLI.

Usage::

    python -m app.eval run dummy --dataset tests/data/dummy.json

Exit codes:
    0  All entries passed evaluation.
    1  One or more entries failed, or an error occurred (missing file,
       bad JSON, unknown evaluator, etc.).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from app.eval.evaluators import REGISTRY


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.eval",
        description="OpenLearn AI evaluation harness.",
    )
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="Run an evaluator against a dataset.")
    run_parser.add_argument(
        "evaluator",
        choices=list(REGISTRY.keys()),
        help="Name of the evaluator to run.",
    )
    run_parser.add_argument(
        "--dataset",
        required=True,
        type=str,
        help="Path to the JSON dataset file.",
    )

    return parser


def _run(evaluator_name: str, dataset_path: str) -> int:
    """Run the named evaluator against the dataset. Returns exit code."""

    # --- Validate dataset file -------------------------------------------
    path = Path(dataset_path)
    if not path.exists():
        print(f"❌ Dataset file not found: {path}", file=sys.stderr)
        return 1

    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"❌ Invalid JSON in {path}: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, list):
        print(f"❌ Dataset must be a JSON array, got {type(data).__name__}", file=sys.stderr)
        return 1

    if len(data) == 0:
        print("❌ Dataset is empty — nothing to evaluate.", file=sys.stderr)
        return 1

    # --- Instantiate evaluator -------------------------------------------
    evaluator_cls = REGISTRY.get(evaluator_name)
    if evaluator_cls is None:
        print(f"❌ Unknown evaluator: {evaluator_name!r}", file=sys.stderr)
        return 1

    evaluator = evaluator_cls()
    print(f"▶ Running evaluator '{evaluator_name}' on {len(data)} entries from {path}")

    # --- Evaluate each entry ---------------------------------------------
    passed = 0
    failed = 0

    for idx, entry in enumerate(data):
        try:
            result = evaluator.evaluate(entry)
        except Exception as exc:
            print(f"  [{idx}] ERROR: {exc}", file=sys.stderr)
            failed += 1
            continue

        if result:
            passed += 1
        else:
            print(f"  [{idx}] FAIL: {entry}")
            failed += 1

    # --- Summary ---------------------------------------------------------
    total = passed + failed
    print(f"\n{'='*40}")
    print(f"Results: {passed}/{total} passed, {failed}/{total} failed")

    if failed > 0:
        print("❌ Evaluation FAILED")
        return 1

    print("✅ Evaluation PASSED")
    return 0


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        sys.exit(_run(args.evaluator, args.dataset))


if __name__ == "__main__":
    main()
else:
    # Supports `python -m app.eval ...`
    main()
