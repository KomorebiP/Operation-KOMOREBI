#!/usr/bin/env python3
"""Replay frozen exact validators in an isolated directory; keep inherited records intact."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
SUITES = {
    "15": ("verify_block15_lane_transport.py", "block15_lane_transport_validation.json"),
    "16": ("verify_block16_holonomy_lane_transport.py", "block16_holonomy_lane_transport_validation.json"),
    "17": ("verify_block17_semantic_extension.py", "block17_semantic_extension_validation.json"),
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", choices=["all", *SUITES], default="all")
    args = parser.parse_args()
    selected = SUITES if args.suite == "all" else {args.suite: SUITES[args.suite]}
    if "17" in selected:
        try:
            import sympy
        except ImportError:
            raise SystemExit("Block 17 requires SymPy; install requirements.txt in your chosen Python environment.")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = ROOT / "user_replays" / stamp
    destination.mkdir(parents=True, exist_ok=False)
    summary = {"created_utc": stamp, "interpretation": "Bounded implementation regression, not a universal proof or Lean certificate.", "suites": []}
    frozen = ROOT / "verification" / "execution_inputs" / "manuscript"
    with tempfile.TemporaryDirectory(prefix="stratified-replay-") as temporary:
        work = Path(temporary) / "manuscript"
        shutil.copytree(frozen, work)
        for number, (script, report) in selected.items():
            started = time.perf_counter()
            with (destination / f"block{number}.log").open("wb") as log:
                result = subprocess.run([sys.executable, script], cwd=work, stdout=log, stderr=subprocess.STDOUT)
            row = {"suite": number, "exit_code": result.returncode, "runtime_seconds": round(time.perf_counter()-started, 3), "script_sha256": hashlib.sha256((work/script).read_bytes()).hexdigest()}
            output = work / "results" / report
            if output.exists():
                shutil.copy2(output, destination / report)
                row["report_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
                row["scientific_result"] = json.loads(output.read_text())
            summary["suites"].append(row)
            (destination / "SUMMARY.json").write_text(json.dumps(summary, indent=2)+"\n")
            if result.returncode:
                raise SystemExit(f"Block {number} failed; inspect {destination}.")
            print(f"Block {number}: execution completed; scientific result saved in {destination.relative_to(ROOT)}.")
    print("The replay pins frozen implementation inputs, rather than certifying the final prose amendments.")

if __name__ == "__main__":
    main()
