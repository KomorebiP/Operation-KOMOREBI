#!/usr/bin/env python3
"""Build the K-COS monograph from editable LaTeX sources."""
from pathlib import Path
import shutil, subprocess
ROOT=Path(__file__).resolve().parent

def main() -> None:
    compiler=shutil.which('pdflatex')
    if not compiler:
        raise SystemExit('pdflatex is required. Install a TeX distribution with the packages named in book/monograph.sty.')
    logs=ROOT/'verification'/'typesetting'
    logs.mkdir(parents=True,exist_ok=True)
    for i in range(1,4):
        with (logs/f'pass_{i}.txt').open('wb') as f:
            result=subprocess.run([compiler,'-interaction=nonstopmode','-halt-on-error','-file-line-error','K_COS_Monograph.tex'],cwd=ROOT/'book',stdout=f,stderr=subprocess.STDOUT)
        if result.returncode:
            raise SystemExit(f'LaTeX failed on pass {i}. See verification/typesetting/pass_{i}.txt.')
    shutil.copy2(ROOT/'book/K_COS_Monograph.pdf',ROOT/'K_COS_Monograph.pdf')
    print(ROOT/'K_COS_Monograph.pdf')
if __name__=='__main__': main()
