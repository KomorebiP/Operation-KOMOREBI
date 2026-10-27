"""Execute byte-identical archived code copies and copy generated evidence into a bounded run."""
from pathlib import Path
import argparse, runpy, shutil, sys

parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["exact", "numerical40", "numerical70"], required=True)
parser.add_argument("--result", type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
copy = root / "v014_copy"
sys.path.insert(0, str(root / "dependencies"))
if args.mode == "exact":
    script = copy / "checks/exact_checks.py"
    generated = copy / "evidence/exact_results.json"
    sys.argv = [str(script)]
else:
    digits = args.mode.removeprefix("numerical")
    script = copy / "checks/numerical_checks.py"
    generated = copy / f"evidence/numerical_{digits}.json"
    sys.argv = [str(script), "--digits", digits]
runpy.run_path(str(script), run_name="__main__")
shutil.copyfile(generated, args.result)
