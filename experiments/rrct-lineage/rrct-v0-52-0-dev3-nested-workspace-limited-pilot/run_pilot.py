#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path
from nested_workspace_pilot import analyze, aggregate

ROOT = Path(__file__).resolve().parent
SEEDS = [392208712, 743448271, 793186123, 445719542]

def main() -> int:
    results = [analyze(seed, ROOT / "models" / f"seed_{seed}.pt") for seed in SEEDS]
    summary = aggregate(results)
    analysis = {"schema": "rrct.v052.dev3.holdout.v1", "seed_results": results, "summary": summary}
    (ROOT / "results" / "analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n")
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    with (ROOT / "results" / "modes.csv").open("w", newline="") as f:
        writer = csv.writer(f); writer.writerow(["seed", "mode", "local_a", "local_b", "global", "mean_action", "mean_private"])
        for r in results:
            for mode, m in r["modes"].items(): writer.writerow([r["seed"], mode, m["local_a"], m["local_b"], m["global"], m["mean_action"], m["mean_private"]])
    print(summary["status"]); print(f"endpoints={sum(summary['endpoints'].values())}/{len(summary['endpoints'])}"); print(f"digest={summary['digest']}")
    return 0 if summary["all_endpoints_met"] else 1

if __name__ == "__main__": raise SystemExit(main())
