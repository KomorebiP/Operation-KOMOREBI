from pathlib import Path

from projector_seed_residuals.experiments import run_experiments
from projector_seed_residuals.visuals import make_visuals

ROOT = Path(__file__).resolve().parent
results = run_experiments(ROOT / "results")
figures = make_visuals(ROOT / "figures", ROOT / "results" / "residual_seed_results.json")
print(f"generated {len(figures)} figure pairs")
print(f"minimum directed seed count: {results['transport']['minimum_count']}")
print(f"finite occupancy ranks: {results['finite_occupancy']['ranks']}")
