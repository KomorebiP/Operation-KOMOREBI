#!/usr/bin/env python3
"""Build the independently editable Block 03 continuation with XeLaTeX."""
import argparse,os,shutil,subprocess
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();root=Path(__file__).resolve().parents[1];out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
if not shutil.which('xelatex'):raise SystemExit('XeLaTeX is required. See BUILD.md for system-font dependencies.')
src=root/'publication/source';env=dict(os.environ,TEXINPUTS=str(src)+os.pathsep,SOURCE_DATE_EPOCH='1791648000',FORCE_SOURCE_DATE='1')
for i in range(1,4):
 r=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory='+str(out),str(src/'Paper_XI_Conjecture66_Block03.tex')],cwd=src,env=env,capture_output=True,text=True)
 (out/f'build_pass_{i}.txt').write_text(r.stdout+r.stderr)
 if r.returncode:raise SystemExit(f'Build pass {i} failed. See {out}/build_pass_{i}.txt')
print(out/'Paper_XI_Conjecture66_Block03.pdf')
