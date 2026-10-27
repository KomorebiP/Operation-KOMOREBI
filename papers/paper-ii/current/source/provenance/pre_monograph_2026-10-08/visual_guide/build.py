#!/usr/bin/env python3
"""Compile the editable Paper II visual guide. Python packages are not needed."""
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parent
env = dict(os.environ, SOURCE_DATE_EPOCH='1791158400', FORCE_SOURCE_DATE='1')
for pass_number in range(1, 4):
    result = subprocess.run(
        ['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'Paper_II_Visual_Guide_Final.tex'],
        cwd=root, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (root / f'build_pass_{pass_number}.txt').write_text(result.stdout)
    if result.returncode:
        raise SystemExit(f'Build failed on pass {pass_number}; see build_pass_{pass_number}.txt')
print(root / 'Paper_II_Visual_Guide_Final.pdf')
