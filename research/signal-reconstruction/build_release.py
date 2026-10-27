#!/usr/bin/env python3
"""Rebuild the three Signal publication PDFs from the editable TeX sources."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
DOCUMENTS = {
    'traditional': ('traditional', 'Signal_Reconstruction_Traditional.tex'),
    'visual': ('visual', 'Signal_Reconstruction_Visual_Guide.tex'),
    'lean': ('lean', 'Signal_Reconstruction_Lean_Guide.tex'),
}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=DOCUMENTS)
    args = parser.parse_args()
    engine = shutil.which('pdflatex')
    if engine is None:
        parser.error('pdfLaTeX is required to rebuild the publication PDFs.')
    environment = dict(os.environ, SOURCE_DATE_EPOCH='1791244800', FORCE_SOURCE_DATE='1')
    for key in ([args.only] if args.only else list(DOCUMENTS)):
        folder, filename = DOCUMENTS[key]
        work = ROOT / folder
        tex = work / filename
        if not tex.is_file():
            raise FileNotFoundError(tex)
        for pass_number in range(1, 4):
            log = work / f'{tex.stem}.build-pass-{pass_number}.log'
            with log.open('wb') as stream:
                result = subprocess.run(
                    [engine, '-interaction=nonstopmode', '-halt-on-error', filename],
                    cwd=work, stdout=stream, stderr=subprocess.STDOUT, env=environment,
                )
            if result.returncode:
                raise RuntimeError(f'{key}: pass {pass_number} failed; see {log}')
        pdf = tex.with_suffix('.pdf')
        if not pdf.is_file() or not pdf.stat().st_size:
            raise RuntimeError(f'{key}: complete PDF not produced')
        print(pdf.relative_to(ROOT))

if __name__ == '__main__':
    main()
