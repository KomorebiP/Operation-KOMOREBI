from pathlib import Path

from projector_quantum_calculus.experiments import run_experiments
from projector_quantum_calculus.visuals import make_visuals

ROOT = Path(__file__).resolve().parent
results = run_experiments(
    ROOT / "results" / "numerical_results.json",
    ROOT / "tables" / "numerical_summary.csv",
)
figures = make_visuals(ROOT / "results" / "numerical_results.json", ROOT / "figures")
print(f"Wrote {len(figures)} figure pairs")
print(ROOT / "results" / "numerical_results.json")
