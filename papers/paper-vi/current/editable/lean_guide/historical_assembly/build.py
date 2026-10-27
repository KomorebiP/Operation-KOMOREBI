#!/usr/bin/env python3
"""Compile the supplied guide in isolation; no data regeneration or Lean run."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
STEM = 'Paper_VI_Lean_Guide_Final'
qa = HERE / 'qa'
qa.mkdir(exist_ok=True)
env = dict(os.environ, SOURCE_DATE_EPOCH='1791158400', FORCE_SOURCE_DATE='1')
with tempfile.TemporaryDirectory(prefix='paper-vi-lean-guide-') as temp:
    stage = Path(temp)
    for name in (STEM + '.tex', 'preamble.tex'):
        shutil.copy2(HERE / name, stage / name)
    for name in ('chapters', 'generated', 'excerpts'):
        shutil.copytree(HERE / name, stage / name)
    for number in range(1, 5):
        result = subprocess.run(
            ['xelatex', '-interaction=nonstopmode', '-halt-on-error', STEM + '.tex'],
            cwd=stage, env=env, text=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        (qa / f'build_pass{number}.txt').write_text(result.stdout)
        if result.returncode:
            raise SystemExit(f'Build failed on pass {number}; see qa/build_pass{number}.txt')
    for suffix in ('pdf', 'log', 'aux', 'toc', 'out'):
        p = stage / f'{STEM}.{suffix}'
        if p.exists():
            shutil.copy2(p, HERE / p.name)
print(HERE / (STEM + '.pdf'))
