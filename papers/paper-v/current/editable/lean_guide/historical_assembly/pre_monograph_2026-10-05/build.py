#!/usr/bin/env python3
"""Compile supplied PDF guide sources; no data regeneration and no Lean execution."""
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
(HERE/'qa').mkdir(exist_ok=True)
for suffix in ['aux','toc','out']:
    (HERE/f'Paper_V_Lean_Guide_Final.{suffix}').unlink(missing_ok=True)
for i in range(1,5):
    with (HERE/'qa'/f'build_pass{i}.txt').open('w') as log:
        subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','Paper_V_Lean_Guide_Final.tex'],cwd=HERE,stdout=log,stderr=subprocess.STDOUT,check=True)
print(HERE/'Paper_V_Lean_Guide_Final.pdf')
