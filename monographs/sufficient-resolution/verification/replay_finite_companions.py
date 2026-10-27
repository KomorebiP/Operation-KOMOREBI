"""Serial portable replay of the sixteen fixed finite companion suites.

Requires Python 3.10+ and SymPy 1.14.0. This driver runs trusted bundled code,
never commands taken from evidence manifests. Every suite gets a new private
output tree and a bounded version-2 computation manifest.
"""
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--output", default="verification/local_python_replay")
p.add_argument("--plan-only", action="store_true")
a = p.parse_args()
destination = (root / a.output).resolve()
if not destination.is_relative_to(root):
    p.error("Output must remain inside the release root")
contracts = sorted((root / "verification/contracts").glob("*.json"))
contracts = [path for path in contracts if path.name != "runner_plan.json"]
if a.plan_only:
    print(json.dumps({"suites": [path.stem for path in contracts], "suite_count": len(contracts),
                      "boundary": "Plan only; no mathematical test run."}, indent=2))
    raise SystemExit(0)
if destination.exists():
    p.error("Choose a new output directory; existing evidence is never overwritten")
try:
    import sympy
except ImportError:
    p.error("SymPy is missing; install the pinned formal/requirements-rational-tests.txt first")
if sympy.__version__ != "1.14.0":
    p.error("This replay requires pinned SymPy 1.14.0")
destination.mkdir(parents=True)
for contract in contracts:
    name = contract.stem
    suite_output = destination / name
    relative_output = str(suite_output.relative_to(root))
    record = json.loads(contract.read_text())
    import mpmath
    record["software"] = [{"name": "computation Python", "version": sys.version},
                          {"name": "SymPy", "version": sympy.__version__},
                          {"name": "mpmath", "version": mpmath.__version__},
                          {"name": "platform", "version": platform.platform()}]
    actual_contract = destination / (name + "_contract.json")
    actual_contract.write_text(json.dumps(record, indent=2) + "\n")
    argv = [sys.executable, str(root / "formal/scripts/provenance/run_experiment.py"),
            "--root", str(root), "--contract", str(actual_contract), "--output", relative_output]
    for path in record["execution_artifacts"]:
        argv += ["--input", path]
    argv += ["--result", relative_output + "/scientific_result.json",
             "--result", relative_output + "/suite_stdout.json",
             "--timeout", "600", "--max-output-bytes", "1048576",
             "--max-memory-bytes", "1073741824", "--max-cpu-seconds", "500",
             "--max-cores", "1", "--max-threads", "1", "--", sys.executable,
             "verification/run_python_companion.py", "--formal", "formal", "--suite",
             "check_" + name + ".py", "--output", relative_output]
    subprocess.run(argv, cwd=root, check=True)
    subprocess.run([sys.executable, str(root / "formal/scripts/provenance/validate_manifest.py"),
                    str(suite_output / "manifest.json"), "--root", str(root)], cwd=root, check=True)
print("PASS: sixteen finite companion runs recorded; no Lean proof verification is implied.")
