from __future__ import annotations

import argparse
import json
from pathlib import Path

from komorebi_arc3_offline.lasm_benchmark import run_all_benchmarks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/pr_lasm_benchmark")
    args = parser.parse_args()
    summary = run_all_benchmarks(Path(args.output))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
