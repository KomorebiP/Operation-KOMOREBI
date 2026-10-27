"""Run one unchanged finite companion inside a private output project.

This wrapper creates a copy of script dependencies and input examples, invokes
the original documented check script, and normalizes its JSON stdout. It adds
no mathematical assertion and never turns inherited example outputs into fresh
results. The outer bounded runner records limits, argv, hashes and logs.
"""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument("--formal", type=Path, required=True)
p.add_argument("--suite", required=True)
p.add_argument("--output", type=Path, required=True)
a = p.parse_args()
formal, output = a.formal.resolve(), a.output.resolve()
if not a.suite.startswith("check_") or not a.suite.endswith(".py") or Path(a.suite).name != a.suite:
    p.error("Expected a simple check_*.py filename")
if not (formal / "scripts" / a.suite).is_file():
    p.error("Suite not found")
private = output / "isolated_project"
shutil.copytree(formal / "scripts", private / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
(private / "examples").mkdir()
for source in (formal / "examples").glob("*input.json"):
    shutil.copy2(source, private / "examples" / source.name)
raw = output / "suite_stdout.json"
with raw.open("w", encoding="utf-8") as stream:
    completed = subprocess.run([sys.executable, str(private / "scripts" / a.suite)],
                               cwd=private, stdout=stream, check=False)
record = {"suite": a.suite, "exit_status": completed.returncode,
          "boundary": "Finite exact implementation checks; not a universal theorem or Lean verification."}
try:
    native = json.loads(raw.read_text(encoding="utf-8"))
except (ValueError, OSError) as exc:
    record.update(status="FAIL", error=f"Suite did not emit its expected JSON: {exc}")
else:
    record["native_result"] = native
    record["status"] = "PASS" if completed.returncode == 0 and native.get("passed") is True else "FAIL"
    counters = [key for key in ("assertions", "exact_assertions", "individual_assertions") if key in native]
    if len(counters) == 1:
        record["reported_assertion_count"] = native[counters[0]]
        record["count_source"] = counters[0]
    elif a.suite == "check_examples.py":
        record["reported_fixed_check_groups"] = len(native["checks"])
        record["main_mathematical_assert_statements"] = 6
        record["count_source"] = "Five named sanity groups; six main source assert statements. Helper shape assertions are excluded."
    else:
        record.update(status="FAIL", error="Missing or ambiguous assertion counter")
(output / "scientific_result.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"suite": a.suite, "status": record["status"],
                  "assertions": record.get("reported_assertion_count"),
                  "fixed_check_groups": record.get("reported_fixed_check_groups")}))
raise SystemExit(0 if record["status"] == "PASS" else (completed.returncode or 1))
