"""Build the Strong Artin monograph and its companion visual guide."""
from pathlib import Path
import argparse
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--figures', action='store_true')
parser.add_argument('--only', choices=['paper', 'visual'])
args = parser.parse_args()
if args.figures:
    subprocess.run([sys.executable, str(ROOT / 'visual/figures.py')], check=True)
names = {
    'paper': 'Komorebi_Strong_Artin_Conjecture_Piece_v1.0.pdf',
    'visual': 'Komorebi_Strong_Artin_Visual_Guide_v1.0.pdf',
}
(ROOT / 'pdf').mkdir(exist_ok=True)
for project in ([args.only] if args.only else names):
    folder = ROOT / project
    for pass_index in range(5):
        proc = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'],
            cwd=folder, text=True, capture_output=True,
        )
        (folder / 'build_stdout.log').write_text(proc.stdout + proc.stderr)
        if proc.returncode:
            print(proc.stdout[-7000:], file=sys.stderr)
            raise SystemExit(proc.returncode)
        log = (folder / 'main.log').read_text(errors='replace')
        needs_another_pass = ('Label(s) may have changed' in log or
                              'Rerun to get' in log or
                              'Please rerun' in log)
        if pass_index >= 1 and not needs_another_pass:
            break
    else:
        raise SystemExit(f'References did not stabilize after five passes: {project}')
    target = ROOT / 'pdf' / names[project]
    shutil.copyfile(folder / 'main.pdf', target)
    print(target)
