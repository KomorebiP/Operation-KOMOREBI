#!/usr/bin/env python3
"""Rebuild the traditional reading artifact; this does not compile Lean."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
for i in range(3):
    result=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',
                           'Sufficient_Resolution_Traditional.tex'],cwd=root,
                          text=True,capture_output=True)
    if result.returncode:
        print(result.stdout[-6000:]); raise SystemExit(result.returncode)
subprocess.run([sys.executable,str(root/'build_markdown.py')],check=True)
print('Traditional PDF rebuilt with three pdfLaTeX passes; Lean not executed.')
