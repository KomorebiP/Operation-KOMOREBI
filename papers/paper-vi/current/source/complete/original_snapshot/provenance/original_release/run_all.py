from pathlib import Path
import csv

from projector_transfer_semigroups.experiments import run_experiments
from projector_transfer_semigroups.visuals import make_visuals

ROOT = Path(__file__).resolve().parent
results = run_experiments(ROOT / "results" / "numerical_results.json")
figures = make_visuals(ROOT / "figures")

rows = []
for section, values in results.items():
    if not isinstance(values, dict):
        continue
    for key, value in values.items():
        if isinstance(value, (int, float)):
            rows.append((section, key, value))
with (ROOT / "tables" / "numerical_summary.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["section", "metric", "value"])
    writer.writerows(rows)

print(f"Generated {len(figures)} figure pairs.")
print(f"Wrote {ROOT / 'results' / 'numerical_results.json'}")
print(f"Wrote {ROOT / 'tables' / 'numerical_summary.csv'}")
