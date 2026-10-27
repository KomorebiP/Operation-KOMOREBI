#!/usr/bin/env python3
"""Compile every retained successful concrete vector for Blocks 05--10.

Each file is run in a separate Lean process with warning-as-error and a bounded
per-file timeout, so a partial aggregate run cannot be mistaken for a pass.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

EXAMPLE = re.compile(r"^\s*example\b", re.MULTILINE)


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
    missing = [str(p) for p in files if not p.is_file()]
    if missing:
        raise SystemExit(f"missing vector files: {missing}")

    env = dict(os.environ)
    env["TERM"] = "dumb"
    records: list[dict[str, object]] = []
    passed = True
    total_examples = 0
    start = time.perf_counter()
    for path in files:
        text = path.read_text(encoding="utf-8")
        examples = len(EXAMPLE.findall(text))
        total_examples += examples
        stem = path.stem
        log_path = root / "logs" / f"{stem}_block10_replay.log"
        t0 = time.perf_counter()
        try:
            result = subprocess.run(
                ["lake", "env", "lean", "-DwarningAsError=true", str(path)],
                cwd=root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=240,
                check=False,
            )
            elapsed = time.perf_counter() - t0
            log_path.write_text(result.stdout, encoding="utf-8")
            ok = result.returncode == 0
            records.append({
                "file": str(path.relative_to(root)),
                "examples": examples,
                "exit_code": result.returncode,
                "timed_out": False,
                "elapsed_seconds": elapsed,
                "passed": ok,
                "log": str(log_path.relative_to(root)),
            })
            passed = passed and ok
            print(f"{path.name}: exit={result.returncode} examples={examples} elapsed={elapsed:.3f}s")
        except subprocess.TimeoutExpired as exc:
            elapsed = time.perf_counter() - t0
            output = exc.stdout or ""
            if isinstance(output, bytes):
                output = output.decode(errors="replace")
            log_path.write_text(output + "\nTIMEOUT\n", encoding="utf-8")
            records.append({
                "file": str(path.relative_to(root)),
                "examples": examples,
                "exit_code": None,
                "timed_out": True,
                "elapsed_seconds": elapsed,
                "passed": False,
                "log": str(log_path.relative_to(root)),
            })
            passed = False
            print(f"{path.name}: TIMEOUT examples={examples} elapsed={elapsed:.3f}s")

    report = {
        "schema": "komorebi-padic-block10-lean-vector-replay-v1",
        "status": "PASS" if passed else "FAIL",
        "file_count": len(files),
        "example_count": total_examples,
        "elapsed_seconds": time.perf_counter() - start,
        "failed_files": [r["file"] for r in records if not r["passed"]],
        "records": records,
    }
    out = root / "results" / "lean_vector_replay_block10.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
