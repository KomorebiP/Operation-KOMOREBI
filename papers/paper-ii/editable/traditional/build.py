#!/usr/bin/env python3
"""Build the integrated traditional edition using local TeX assets only."""
from pathlib import Path
import os,subprocess,sys
R=Path(__file__).resolve().parent
if '--assemble' in sys.argv:subprocess.run([sys.executable,'assemble.py'],cwd=R,check=True)
env=dict(os.environ);env['SOURCE_DATE_EPOCH']='1791158400'
subprocess.run(['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error','Paper_II_Traditional_Final.tex'],cwd=R,env=env,check=True)
