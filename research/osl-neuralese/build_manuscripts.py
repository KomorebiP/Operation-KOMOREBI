#!/usr/bin/env python3
"""Build the three new manuscripts into an external output directory."""
from __future__ import annotations
import argparse,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCES=['OSL/manuscript/OSL_Final_Research_Edition.tex',
         'Neuralese/manuscript/Neuralese_Final_Research_Edition.tex',
         'guide/OSL_Neuralese_Visual_Verification_Guide.tex']
def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    output=a.output.resolve()
    if output==ROOT or ROOT in output.parents:p.error('Output must be outside the sealed release')
    if not shutil.which('latexmk'):p.error('latexmk is required; see BUILD.md')
    output.mkdir(parents=True,exist_ok=True);rows=[]
    for relative in SOURCES:
        src=ROOT/relative;dest=output/src.stem;dest.mkdir(exist_ok=True)
        command=['latexmk','-pdf','-interaction=nonstopmode','-halt-on-error',f'-outdir={dest}',src.name]
        with (dest/'build.stdout').open('w',encoding='utf-8') as log:
            try:ret=subprocess.run(command,cwd=src.parent,stdout=log,stderr=subprocess.STDOUT,timeout=300).returncode
            except subprocess.TimeoutExpired:ret=None
        rows.append({'source':relative,'returncode':ret,'pdf':str(dest/src.with_suffix('.pdf').name)})
        if ret!=0:
            print(json.dumps({'status':'BUILD_FAILED','results':rows},indent=2));return 1
    print(json.dumps({'status':'BUILT','results':rows},indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
