#!/usr/bin/env python3
"""Build the Machine Societies Modern Monograph PDF with local fonts and figures."""
from pathlib import Path
import re, shutil, subprocess

root=Path(__file__).resolve().parent
engine=shutil.which('xelatex')
if not engine:
    raise SystemExit('XeLaTeX is required. Install TeX Live or MiKTeX with the packages in BUILD_README.txt.')
build=root/'build'
build.mkdir(exist_ok=True)
logs=root.parent/'verification/build_logs'
logs.mkdir(parents=True,exist_ok=True)
for i in range(1,4):
    result=subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error','-file-line-error','-output-directory=build','Machine_Societies_v1.0.0.tex'],cwd=root,text=True,capture_output=True)
    (logs/f'xelatex_pass_{i}.txt').write_text(result.stdout+result.stderr)
    if result.returncode:
        print('\n'.join((result.stdout+result.stderr).splitlines()[-32:]))
        raise SystemExit(f'XeLaTeX pass {i} failed with exit {result.returncode}. See verification/build_logs.')
final=(build/'Machine_Societies_v1.0.0.log').read_text(errors='replace')
issues=[line for line in final.splitlines() if re.search(r'Overfull|undefined references|multiply defined|Missing character|^! ',line)]
if issues:
    print('\n'.join(issues))
    raise SystemExit('Build produced layout or reference diagnostics. See the log before delivery.')
shutil.copy2(build/'Machine_Societies_v1.0.0.pdf',root.parent/'Machine_Societies_v1.0.0.pdf')
shutil.copy2(build/'Machine_Societies_v1.0.0.aux',root.parent/'verification/compiled_cross_references.aux')
print('Built Machine_Societies_v1.0.0.pdf with no overfull boxes, missing glyphs, or unresolved references.')
