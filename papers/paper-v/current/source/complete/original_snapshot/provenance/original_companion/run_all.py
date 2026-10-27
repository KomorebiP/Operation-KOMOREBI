from pathlib import Path
import json
from projector_signal.experiments import run_experiments
from projector_signal.visuals import make_figures
ROOT=Path(__file__).resolve().parent
results=run_experiments(ROOT)
figures=make_figures(ROOT)
summary={"author":"Komorebi P.","paper":"Projector-Resolved Seed Calculus V","figure_file_count":len(figures),"figures":figures,"results":results}
(ROOT/"results"/"run_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
print(f"Generated {len(figures)//2} figure pairs")
print(Path('results') / 'numerical_results.json')
