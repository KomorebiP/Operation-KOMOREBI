#!/usr/bin/env python3
"""Rebuild the three publication PDFs from the final edition's editable sources."""
from pathlib import Path
import argparse
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
DOCS = {
    'traditional': 'Quadratic_Form_KCOS_Traditional',
    'visual': 'Quadratic_Form_KCOS_Visual_Guide',
    'lean': 'Quadratic_Form_KCOS_Lean_Guide',
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=list(DOCS))
    args = parser.parse_args()
    compiler = shutil.which('pdflatex')
    if compiler is None:
        raise SystemExit('pdflatex is required; install a TeX distribution before rebuilding.')
    logdir = ROOT / 'verification' / 'publication'
    logdir.mkdir(parents=True, exist_ok=True)
    targets = [args.only] if args.only else list(DOCS)
    for folder in targets:
        stem = DOCS[folder]
        cwd = ROOT / folder
        for pass_id in range(1, 4):
            command = [compiler, '-halt-on-error', '-interaction=nonstopmode', stem + '.tex']
            with (logdir / f'{folder}_pass_{pass_id}.log').open('wb') as stream:
                result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
            if result.returncode:
                raise SystemExit(f'{folder} build failed on pass {pass_id}; see verification/publication.')
        print(cwd / (stem + '.pdf'))

if __name__ == '__main__':
    main()
