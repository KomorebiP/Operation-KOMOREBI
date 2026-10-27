#!/usr/bin/env python3
"""Portable XeLaTeX guide build; uses only files beneath this directory."""
from pathlib import Path
import os, shutil, subprocess, tempfile
HERE=Path(__file__).resolve().parent
STEM='Paper_VII_Lean_Guide_Final'
qa=HERE/'qa';qa.mkdir(exist_ok=True)
env=dict(os.environ,SOURCE_DATE_EPOCH='1791244800',FORCE_SOURCE_DATE='1',TZ='UTC')
with tempfile.TemporaryDirectory(prefix='paper-vii-guide-') as tmp:
    stage=Path(tmp)
    for name in (STEM+'.tex','preamble.tex'):shutil.copy2(HERE/name,stage/name)
    for name in ('chapters','generated','excerpts'):shutil.copytree(HERE/name,stage/name)
    for n in range(1,5):
        p=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',STEM+'.tex'],cwd=stage,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (qa/f'build_pass{n}.txt').write_text(p.stdout)
        if p.returncode:raise SystemExit(f'Build failed on pass {n}: qa/build_pass{n}.txt')
    for suffix in ('pdf','log','aux','toc','out'):
        p=stage/f'{STEM}.{suffix}'
        if p.exists():shutil.copy2(p,HERE/p.name)
print(HERE/(STEM+'.pdf'))
