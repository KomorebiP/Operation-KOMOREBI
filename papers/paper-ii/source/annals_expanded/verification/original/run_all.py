from pathlib import Path

from seed_refinement.experiments import run_experiments
from seed_refinement.visuals import make_visuals

ROOT = Path(__file__).resolve().parent
results = run_experiments(ROOT / "results" / "numerical_results.json")
figures = make_visuals(ROOT / "figures")
print(f"generated {len(figures)} figure pairs")
print(f"path-zeta coefficient match: {results['path_zeta']['match']}")
