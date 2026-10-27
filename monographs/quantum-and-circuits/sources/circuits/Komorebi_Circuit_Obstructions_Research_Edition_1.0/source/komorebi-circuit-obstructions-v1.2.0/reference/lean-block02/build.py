#!/usr/bin/env python3
"""Build the Block 02 theorem reference from its retained source."""
from pathlib import Path
import os,subprocess
root=Path(__file__).resolve().parent
env=os.environ.copy();env.setdefault('SOURCE_DATE_EPOCH','1789948800')
for _ in range(2):
    subprocess.run(['pdflatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','Lean_Verified_Bounds_Block_02.tex'],cwd=root,env=env,check=True)
