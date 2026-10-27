"""Run one unchanged upstream verifier, preserving its scientific outputs.

The subprocess executes the documented script from its manuscript directory.
This wrapper only removes stale replay outputs and copies freshly produced files
into the bounded runner's result directory. It does not alter any assertions.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument("--block", choices=("15", "16", "17"), required=True)
p.add_argument("--replay", required=True)
p.add_argument("--output", required=True)
a = p.parse_args()
replay = Path(a.replay).resolve()
output = Path(a.output).resolve()
script, result = {
    "15": ("verify_block15_lane_transport.py", "block15_lane_transport_validation.json"),
    "16": ("verify_block16_holonomy_lane_transport.py", "block16_holonomy_lane_transport_validation.json"),
    "17": ("verify_block17_semantic_extension.py", "block17_semantic_extension_validation.json"),
}[a.block]
scientific_files = [replay / "results" / result,
                    replay / "generated" / f"block{a.block}_counts.tex",
                    replay / "generated" / f"block{a.block}_validation_table.tex"]
for source in scientific_files:
    source.unlink(missing_ok=True)
completed = subprocess.run([sys.executable, str(replay / script)], cwd=replay, check=False)
for source in scientific_files:
    if source.is_file():
        shutil.copy2(source, output / source.name)
if completed.returncode == 0:
    actual = json.loads((output / result).read_text(encoding="utf-8"))
    if actual.get("status") != "PASS":
        raise SystemExit("Verifier returned success without a fresh PASS record")
raise SystemExit(completed.returncode)
