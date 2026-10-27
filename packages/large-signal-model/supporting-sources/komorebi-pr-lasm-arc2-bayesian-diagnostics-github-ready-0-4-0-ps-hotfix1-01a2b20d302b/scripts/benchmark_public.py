from __future__ import annotations
import argparse
from komorebi_arc2.entry import evaluate_split, print_score_report

ap = argparse.ArgumentParser()
ap.add_argument("challenge")
ap.add_argument("solutions")
ap.add_argument("--output", default="results/submission.json")
ap.add_argument("--report", default="results/report.json")
ap.add_argument("--time-limit", type=float, default=0.25)
ap.add_argument("--max-tasks", type=int)
a = ap.parse_args()
report = evaluate_split(a.challenge, a.solutions, a.output, a.report, a.time_limit, False, a.max_tasks)
print_score_report("Public benchmark", report)
