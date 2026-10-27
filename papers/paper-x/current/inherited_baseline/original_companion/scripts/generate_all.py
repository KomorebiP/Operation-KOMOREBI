from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from projector_seed_residuals.experiments import run_experiments
from projector_seed_residuals.visuals import make_visuals


def main() -> None:
    results = run_experiments(ROOT / "results")
    figures = make_visuals(ROOT / "figures", ROOT / "results" / "residual_seed_results.json")
    print(f"generated {len(figures)} figure pairs")
    print(f"transport source components: {results['transport']['minimum_count']}")
    print(f"companion primes tested: {len(results['companion_forests_x2_plus_1'])}")


if __name__ == "__main__":
    main()
