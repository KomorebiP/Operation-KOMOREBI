#!/usr/bin/env python3
"""Validate per-file Block 10 Lean-vector replay receipts."""
from __future__ import annotations

import json
import re
from pathlib import Path

EXAMPLE = re.compile(r"^\s*example\b", re.MULTILINE)
FIELD = re.compile(r"^(elapsed_seconds|max_rss_kb|exit_code)=(.+)$", re.MULTILINE)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    verification = root / "verification"
    files: list[Path] = [
        verification / "LeanCompilerVector.lean",
        verification / "LeanSuffixWindowVector.lean",
        verification / "LeanBoundaryVector.lean",
    ]
    files += sorted(verification.glob("LeanComplexityVector_[0-9][0-9].lean"))
    files += sorted(verification.glob("LeanClosedFormVector_[0-9][0-9].lean"))

    records: list[dict[str, object]] = []
    failures: list[str] = []
    example_count = 0
    elapsed_total = 0.0
    max_rss = 0
    for source in files:
        stem = source.stem
        log = root / "logs" / f"{stem}_block10_replay.log"
        receipt = root / "logs" / f"{stem}_block10_replay.time"
        examples = len(EXAMPLE.findall(source.read_text(encoding="utf-8")))
        example_count += examples
        fields = dict(FIELD.findall(receipt.read_text(encoding="utf-8"))) if receipt.is_file() else {}
        exit_code = int(fields["exit_code"]) if "exit_code" in fields else None
        elapsed = float(fields.get("elapsed_seconds", "nan"))
        rss = int(fields.get("max_rss_kb", "0"))
        if elapsed == elapsed:
            elapsed_total += elapsed
        max_rss = max(max_rss, rss)
        passed = source.is_file() and log.is_file() and receipt.is_file() and exit_code == 0
        if not passed:
            failures.append(str(source.relative_to(root)))
        records.append({
            "file": str(source.relative_to(root)),
            "examples": examples,
            "exit_code": exit_code,
            "elapsed_seconds": elapsed,
            "max_rss_kb": rss,
            "log": str(log.relative_to(root)),
            "receipt": str(receipt.relative_to(root)),
            "passed": passed,
        })
    passed = not failures and len(files) == 45 and example_count == 5918
    report = {
        "schema": "komorebi-padic-block10-lean-vector-replay-v2",
        "status": "PASS" if passed else "FAIL",
        "file_count": len(files),
        "example_count": example_count,
        "sum_elapsed_seconds": elapsed_total,
        "max_single_process_rss_kb": max_rss,
        "failed_files": failures,
        "records": records,
        "execution_note": (
            "The first monolithic replay process exceeded its outer command window after nine files. "
            "Every vector was subsequently rerun in bounded batches, and this report validates the "
            "individual zero-exit receipts rather than the incomplete aggregate attempt."
        ),
    }
    (root / "results" / "lean_vector_replay_block10.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
