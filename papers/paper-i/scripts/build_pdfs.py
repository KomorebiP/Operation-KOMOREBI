#!/usr/bin/env python3
"""Compile the three supplied final LaTeX companions from a portable package."""
from pathlib import Path
import argparse
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--check-only', action='store_true', help='Keep rebuilt PDFs in build/ without replacing papers/.')
args = parser.parse_args()
for engine in ['pdflatex', 'xelatex']:
    if not shutil.which(engine):
        raise SystemExit(f'{engine} is required; install a TeX distribution first.')
volumes = {
    'traditional': 'Paper_I_Traditional_Final',
    'lean_guide': 'Paper_I_Lean_Guide_Final',
    'machine': 'Paper_I_Machine_Native_Final',
}
for component, stem in volumes.items():
    source = root / 'editable' / component
    build = root / 'build' / component
    build.mkdir(parents=True, exist_ok=True)
    engine = 'xelatex' if component == 'lean_guide' else 'pdflatex'
    for iteration in range(1, 4):
        result = subprocess.run(
            [engine, '-interaction=nonstopmode', '-halt-on-error',
             '-file-line-error', f'-output-directory={build}', f'{stem}.tex'],
            cwd=source, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (build / f'pass_{iteration}.txt').write_text(result.stdout)
        if result.returncode:
            raise SystemExit(f'{component} build failed; see {build / f"pass_{iteration}.txt"}')
    (root / 'papers').mkdir(exist_ok=True)
    if not args.check_only:
        shutil.copy2(build / f'{stem}.pdf', root / 'papers' / f'{stem}.pdf')
    print(f'Built {component}/{stem}.pdf')
