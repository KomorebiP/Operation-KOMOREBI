#!/usr/bin/env python3
"""Render the current machine companion from the reviewed release inventory."""
from pathlib import Path
import argparse, subprocess, sys
here=Path(__file__).resolve().parent
publication=here.parents[1]
a=argparse.ArgumentParser()
a.add_argument('--coverage',type=Path,default=publication/'formal/coverage/COVERAGE_108.json')
a.add_argument('--metadata',type=Path,default=publication/'verification/COMPANION_EVIDENCE.json')
a.add_argument('--data-script',type=Path,default=publication/'scripts/build_release_companion_data.py')
args=a.parse_args()
cmd=[sys.executable,str(args.data_script),'--coverage',str(args.coverage),'--publication-root',str(publication)]
if args.metadata and args.metadata.exists(): cmd += ['--metadata',str(args.metadata)]
subprocess.run(cmd,check=True)
for n in range(3):
    p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Paper_I_Machine_Native_Final.tex'],cwd=here,capture_output=True,text=True)
    (here/f'build_pass{n+1}.txt').write_text(p.stdout+p.stderr)
    if p.returncode: raise SystemExit(p.stdout[-4000:])
print(here/'Paper_I_Machine_Native_Final.pdf')
