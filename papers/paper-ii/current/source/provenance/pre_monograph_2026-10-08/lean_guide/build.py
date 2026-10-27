#!/usr/bin/env python3
"""Compile the supplied guide sources without regenerating any data or running Lean."""
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
for i in (1,2,3,4):
    with (HERE/f'build_pass{i}.txt').open('w') as log:
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','Paper_II_Lean_Guide_Final.tex'],cwd=HERE,stdout=log,stderr=subprocess.STDOUT,check=True)
print(HERE/'Paper_II_Lean_Guide_Final.pdf')
