#!/usr/bin/env python3
"""Rebuild the three publication PDFs from the bundled editable TeX sources."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
DOCUMENTS = {
    'traditional': ('traditional', 'Sufficient_Resolution_Traditional.tex'),
    'visual': ('visual', 'Sufficient_Resolution_Visual_Guide.tex'),
    'lean': ('lean', 'Sufficient_Resolution_Lean_Guide.tex'),
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=DOCUMENTS)
    args = parser.parse_args()
    engine = shutil.which('pdflatex')
    if engine is None:
        parser.error('pdfLaTeX is required; install a TeX distribution before rebuilding.')
    selected = [args.only] if args.only else list(DOCUMENTS)
    build_environment = dict(os.environ)
    build_environment['SOURCE_DATE_EPOCH'] = '1791244800'
    build_environment['FORCE_SOURCE_DATE'] = '1'
    for key in selected:
        folder, name = DOCUMENTS[key]
        work = ROOT / folder
        tex = work / name
        if not tex.is_file():
            raise FileNotFoundError(tex)
        for pass_number in range(1, 4):
            log = work / f'{tex.stem}.build-pass-{pass_number}.log'
            with log.open('wb') as stream:
                result = subprocess.run(
                    [engine, '-interaction=nonstopmode', '-halt-on-error', name],
                    cwd=work, stdout=stream, stderr=subprocess.STDOUT,
                    env=build_environment,
                )
            if result.returncode:
                raise RuntimeError(f'{key}: pdfLaTeX pass {pass_number} failed; see {log}')
        pdf = tex.with_suffix('.pdf')
        if not pdf.is_file() or pdf.stat().st_size == 0:
            raise RuntimeError(f'{key}: no complete PDF was produced')
        print(pdf.relative_to(ROOT))

if __name__ == '__main__':
    main()
