#!/usr/bin/env python3
from __future__ import annotations

"""Print a compact posterior ledger for a deterministic synthetic ARC task."""

import json

from komorebi_arc2 import entry


def main() -> int:
    task, expected = entry.synthetic_task("recolor_largest", 8)
    diagnostics: dict[str, object] = {}
    predictions = entry.solve_task(task, time_limit=0.25, diagnostics=diagnostics)
    report = {
        "solver_version": entry.SOLVER_VERSION,
        "expected": expected,
        "prediction": predictions[0],
        "mode": diagnostics.get("mode"),
        "calibration_version": diagnostics.get("calibration_version"),
        "candidate_count": diagnostics.get("candidate_count"),
        "posterior_entropy": diagnostics.get("posterior_entropy"),
        "model_disagreement": diagnostics.get("model_disagreement"),
        "posterior_family_probabilities": diagnostics.get("posterior_family_probabilities"),
        "posterior_atlas_probabilities": diagnostics.get("posterior_atlas_probabilities"),
        "top_programs": diagnostics.get("top_programs"),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
