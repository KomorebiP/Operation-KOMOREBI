#!/usr/bin/env python3
"""Reproduce the reviewed Paper IX baseline and any included continuation proofs.

Run from the extracted review bundle. No dependencies are downloaded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import zipfile

BASELINE_NAME = "PRSC_IX_v0.11.0_Nishibuchi_Completion"
BASELINE_SHA256 = "1f02400e73da1d9b6c90a06dcdb5a45c6fd20a4e2addca2a9e638db872cbc721"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kit", type=Path, required=True,
                        help="Extracted pinned Linux portable Lean kit")
    parser.add_argument("--output", type=Path, required=True,
                        help="New, nonexistent directory for extraction and logs")
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parent.parent
    archive = bundle / "baseline" / (BASELINE_NAME + ".zip")
    kit = args.kit.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error("--output must not already exist")
    if not (kit / "run.sh").is_file():
        parser.error("--kit is missing run.sh")
    if hashlib.sha256(archive.read_bytes()).hexdigest() != BASELINE_SHA256:
        parser.error("Baseline archive SHA-256 mismatch")
    output.mkdir(parents=True)
    report = {"status": "INCOMPLETE", "baseline_sha256": BASELINE_SHA256,
              "runs": [], "non_claims": ["Mathlib rebuilt", "human peer review"]}
    started = time.monotonic()

    def run(name: str, command: list[str], cwd: Path) -> None:
        start = time.monotonic()
        log = output / (name + ".log")
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=cwd, stdout=stream,
                                    stderr=subprocess.STDOUT)
        report["runs"].append({"name": name, "command": command,
            "cwd": str(cwd), "exit_code": result.returncode,
            "seconds": round(time.monotonic() - start, 3),
            "log": log.name, "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest()})
        print(f"{name}: exit {result.returncode}", flush=True)
        if result.returncode:
            raise RuntimeError(f"{name} failed; inspect {log}")

    try:
        with zipfile.ZipFile(archive) as source:
            if source.testzip() is not None:
                raise RuntimeError("Baseline CRC check failed")
            for entry in source.infolist():
                if not (output / entry.filename).resolve().is_relative_to(output):
                    raise RuntimeError("Unsafe path in baseline archive")
            source.extractall(output)
        baseline = output / BASELINE_NAME
        run("baseline", ["bash", "Run-Portable.sh", str(kit)], baseline)
        # The continuation's own verifier records exact declarations and controls.
        continuation = bundle / "native" / "lean" / "verify_native.py"
        if not continuation.is_file():
            raise RuntimeError("Missing continuation verifier native/lean/verify_native.py")
        run("native", [sys.executable, str(continuation), "--kit", str(kit),
                       "--output", str(output / "native")], bundle)
        report["status"] = "PASS"
    except Exception as error:
        report["status"] = "FAILED"
        report["error"] = str(error)
    finally:
        report["seconds"] = round(time.monotonic() - started, 3)
        (output / "replay_review.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
