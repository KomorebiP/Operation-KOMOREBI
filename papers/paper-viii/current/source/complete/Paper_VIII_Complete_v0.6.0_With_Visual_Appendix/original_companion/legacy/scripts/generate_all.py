from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packet_gpu.experiments import run_all
from packet_gpu.visuals import make_visuals


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/benchmark_results_sanitized.json")
    parser.add_argument("--root", default=None)
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    benchmark = Path(args.benchmark)
    if not benchmark.is_absolute():
        benchmark = root / benchmark
    run_all(benchmark, root)
    figures = make_visuals(benchmark, root / "figures")
    print(f"generated {len(figures)} figure pairs")


if __name__ == "__main__":
    main()
