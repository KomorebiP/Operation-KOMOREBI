#!/usr/bin/env python3
"""Build the formal reference twice; LaTeX tooling must already be installed."""
from pathlib import Path
import subprocess
root=Path(__file__).resolve().parent
for _ in range(2):
    subprocess.run(["pdflatex","-interaction=nonstopmode","-halt-on-error","Lean_Verified_Core_Block_01.tex"],cwd=root,check=True)
