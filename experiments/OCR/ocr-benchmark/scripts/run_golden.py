#!/usr/bin/env python3
"""Golden runner: run the golden corpus through an engine adapter,
score against verified ground truth (CER/WER), and emit a reproducible
report used as the regression baseline.

Examples:
  python scripts/run_golden.py --list-engines
  python scripts/run_golden.py --engine mock --limit 3
  python scripts/run_golden.py --engine mock --sample-id custom_arabic_scanned_001
  python scripts/run_golden.py --engine ENGINE --compare data/processed/runs/RUN_ID/results.json

Per ADR-0001: pure stdlib here; engines live behind adapters in their
own environments. Results land in data/processed/runs/<run_id>/ (gitignored).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ocrbench.adapters.base import available_engines, get_adapter  # noqa: E402
from ocrbench.core.metrics import cer, wer  # noqa: E402

MANIFEST_PATH = ROOT / "data" / "raw" / "custom" / "manifest.json"
RAW_ROOT = ROOT / "data" / "raw" / "custom"
GT_ROOT = ROOT / "data" / "ground_truth" / "custom"
RUNS_ROOT = ROOT / "data" / "processed" / "runs"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Golden corpus runner (ocrbench)")
    p.add_argument("--engine", default="mock",
                   help="engine adapter name (default: mock)")
    p.add_argument("--limit", type=int, default=None,
                   help="run only the first N samples (smoke test)")
    p.add_argument("--per-category", type=int, default=None,
                   help="run at most N samples per category (stratified subset)")
    p.add_argument("--sample-id", action="append", default=[],
                   help="run a specific sample_id (repeatable)")
    p.add_argument("--category", action="append", default=[],
                   help="only samples carrying this category (repeatable)")
    p.add_argument("--tier", choices=["all", "core", "extended"], default="all",
                   help="evaluation tier filter (default: all)")
    p.add_argument("--compare", type=Path, default=None,
                   help="baseline results.json to compare against")
    p.add_argument("--tolerance", type=float, default=0.0,
                   help="allowed CER increase before flagging a regression")
    p.add_argument("--list-engines", action="store_true",
                   help="print available engines and exit")
    return p.parse_args()


def select_samples(args: argparse.Namespace) -> list:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    docs = manifest["documents"]
    if args.sample_id:
        wanted = set(args.sample_id)
        docs = [d for d in docs if d["sample_id"] in wanted]
    if args.category:
        cats = set(args.category)
        docs = [d for d in docs if cats & set(d.get("categories", []))]
    if args.tier == "core":
        docs = [d for d in docs if d.get("evaluation", {}).get("core")]
    elif args.tier == "extended":
        docs = [d for d in docs if d.get("evaluation", {}).get("extended", True)]
    if args.per_category:
        grouped = {}
        for d in docs:
            for c in (sorted(d.get("categories", [])) or ["(uncategorized)"]):
                grouped.setdefault(c, []).append(d)
        picked, seen = [], set()
        for c in sorted(grouped):
            for d in grouped[c][: args.per_category]:
                if d["sample_id"] not in seen:
                    seen.add(d["sample_id"])
                    picked.append(d)
        docs = picked
    if args.limit:
        docs = docs[: args.limit]
    return docs


def run_samples(docs: list, adapter) -> list:
    records = []
    for doc in docs:
        sample_id = doc["sample_id"]
        rec = {
            "sample_id": sample_id,
            "path": doc["path"],
            "languages": doc.get("language", []),
            "categories": doc.get("categories", []),
            "status": "ok",
            "error": None,
            "duration_s": None,
            "cer": None,
            "wer": None,
        }
        try:
            raw_path = RAW_ROOT / doc["path"]
            gt_path = GT_ROOT / f"{sample_id}.txt"
            if not raw_path.exists():
                raise FileNotFoundError(f"raw file missing: {raw_path}")
            if not gt_path.exists():
                raise FileNotFoundError(f"ground truth missing: {gt_path}")
            t0 = time.perf_counter()
            hypothesis = adapter.run(raw_path, rec["languages"])
            duration = time.perf_counter() - t0
            reference = gt_path.read_text(encoding="utf-8")
            rec["duration_s"] = round(duration, 4)
            rec["cer"] = round(cer(reference, hypothesis), 6)
            rec["wer"] = round(wer(reference, hypothesis), 6)
        except Exception as exc:  # noqa: BLE001
            rec["status"] = "error"
            rec["error"] = str(exc)
        records.append(rec)
        state = "OK " if rec["status"] == "ok" else "ERR"
        c = "-" if rec["cer"] is None else f"{rec['cer']:.4f}"
        print(f"[{state}] {sample_id:<55} CER={c}")
    return records


def _mean(values) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def aggregate(records: list) -> dict:
    ok = [r for r in records if r["status"] == "ok"]
    errors = [r for r in records if r["status"] != "ok"]
    by_cat, by_lang = defaultdict(list), defaultdict(list)
    for r in ok:
        for c in r["categories"]:
            by_cat[c].append(r["cer"])
        for l in r["languages"]:
            by_lang[l].append(r["cer"])
    return {
        "overall": {
            "samples": len(records),
            "ok": len(ok),
            "errors": len(errors),
            "mean_cer": _mean([r["cer"] for r in ok]),
            "mean_wer": _mean([r["wer"] for r in ok]),
        },
        "by_category": {c: _mean(v) for c, v in sorted(by_cat.items())},
        "by_language": {l: _mean(v) for l, v in sorted(by_lang.items())},
    }


def write_report(run_dir: Path, engine: str, records: list, agg: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    results = {
        "schema": "ocrbench-run-results",
        "run_id": run_dir.name,
        "engine": engine,
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "aggregate": agg,
        "records": records,
    }
    (run_dir / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    o = agg["overall"]
    lines = [
        f"# Golden run - {run_dir.name}",
        "",
        f"- engine: `{engine}`",
        f"- samples: {o['samples']} (ok: {o['ok']}, errors: {o['errors']})",
        f"- mean CER: {o['mean_cer']}",
        f"- mean WER: {o['mean_wer']}",
        "",
        "## CER by category",
        "",
        "| category | mean CER |",
        "|---|---|",
    ]
    for cat, v in agg["by_category"].items():
        lines.append(f"| {cat} | {v} |")
    lines += ["", "## CER by language", ""]
    for lang, v in agg["by_language"].items():
        lines.append(f"- {lang}: {v}")
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def compare_with_baseline(baseline: Path, records: list,
                          tolerance: float) -> list:
    base = json.loads(baseline.read_text(encoding="utf-8"))
    old_cer = {r["sample_id"]: r.get("cer") for r in base.get("records", [])}
    regressions = []
    for r in records:
        old = old_cer.get(r["sample_id"])
        if r["status"] != "ok":
            regressions.append({"sample_id": r["sample_id"],
                                "kind": "now-erroring",
                                "old_cer": old, "new_cer": None})
        elif old is not None and r["cer"] is not None and r["cer"] > old + tolerance:
            regressions.append({"sample_id": r["sample_id"],
                                "kind": "cer-worse",
                                "old_cer": old, "new_cer": r["cer"]})
    return regressions


def main() -> int:
    args = parse_args()

    if args.list_engines:
        import ocrbench.adapters.backend_chain  # noqa: F401
        import ocrbench.adapters.mock  # noqa: F401
        print("available engines:", ", ".join(available_engines()))
        return 0

    if not MANIFEST_PATH.exists():
        print(f"manifest not found: {MANIFEST_PATH}", file=sys.stderr)
        return 2

    docs = select_samples(args)
    if not docs:
        print("no samples selected - check your filters", file=sys.stderr)
        return 2

    try:
        adapter = get_adapter(args.engine)
    except KeyError as exc:
        print(exc, file=sys.stderr)
        return 2

    print(f"engine={args.engine}  samples={len(docs)}  tier={args.tier}")
    records = run_samples(docs, adapter)
    agg = aggregate(records)

    run_dir = RUNS_ROOT / time.strftime("%Y%m%d_%H%M%S")
    write_report(run_dir, args.engine, records, agg)

    o = agg["overall"]
    print("\n=== summary ===")
    print(f"ok={o['ok']}/{o['samples']}  errors={o['errors']}  "
          f"mean CER={o['mean_cer']}  mean WER={o['mean_wer']}")
    print(f"report : {run_dir / 'results.json'}")
    print(f"summary: {run_dir / 'summary.md'}")

    if args.compare:
        regs = compare_with_baseline(args.compare, records, args.tolerance)
        if regs:
            print(f"\nREGRESSIONS ({len(regs)}):")
            for r in regs:
                print(f"  - {r['sample_id']}: {r['kind']} "
                      f"old={r['old_cer']} new={r['new_cer']}")
            return 1
        print("\nno regressions vs baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
