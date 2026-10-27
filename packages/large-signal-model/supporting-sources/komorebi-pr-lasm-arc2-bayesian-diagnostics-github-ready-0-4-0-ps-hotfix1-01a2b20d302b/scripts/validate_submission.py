from __future__ import annotations
import argparse, json
from komorebi_arc2.entry import load_tasks_from_path, validate_submission

ap = argparse.ArgumentParser()
ap.add_argument("challenge")
ap.add_argument("submission")
a = ap.parse_args()
tasks = load_tasks_from_path(a.challenge)
submission = json.load(open(a.submission))
errors = validate_submission(submission, tasks)
print(json.dumps({"tasks": len(tasks), "valid": not errors, "errors": errors[:25]}, indent=2))
raise SystemExit(1 if errors else 0)
