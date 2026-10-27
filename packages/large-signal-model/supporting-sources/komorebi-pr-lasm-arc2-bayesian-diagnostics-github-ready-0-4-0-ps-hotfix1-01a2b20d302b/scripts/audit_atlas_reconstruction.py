#!/usr/bin/env python3
from __future__ import annotations

"""Generate a deterministic exact-reconstruction audit for every invertible atlas."""

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_arc2.atlas import ARCAtlasAnalyzer


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT / "benchmarks" / "atlas_reconstruction_audit.json"))
    parser.add_argument("--samples", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20260818)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    analyzer = ARCAtlasAnalyzer()
    maxima: dict[str, float] = {}
    shapes: list[list[int]] = []
    for _ in range(max(1, args.samples)):
        height = int(rng.integers(1, 31))
        width = int(rng.integers(1, 31))
        grid = rng.integers(0, 10, size=(height, width), dtype=np.int16)
        state = analyzer.analyze(grid)
        shapes.append([height, width])
        for name, value in state.reconstruction_residuals.items():
            maxima[name] = max(maxima.get(name, 0.0), float(value))

    report = {
        "solver_version": "0.4.0",
        "samples": max(1, args.samples),
        "seed": args.seed,
        "shapes": shapes,
        "maximum_absolute_residual_by_atlas": maxima,
        "maximum_absolute_residual": max(maxima.values(), default=0.0),
        "passed_1e_minus_10": all(value < 1e-10 for value in maxima.values()),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "shapes"}, indent=2))
    return 0 if report["passed_1e_minus_10"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
