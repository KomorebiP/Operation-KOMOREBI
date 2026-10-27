#!/usr/bin/env python3
"""Rebuild the singular-Amice supplement. Requires pdflatex; does not run Lean."""
from pathlib import Path
import shutil,subprocess,tempfile,re,sys
root=Path(__file__).resolve().parents[1]
name='Paper_IX_Singular_Amice_Supplement'
with tempfile.TemporaryDirectory(prefix='ix-amice-pdf-') as tmp:
    wd=Path(tmp);shutil.copy2(root/'docs'/f'{name}.tex',wd)
    for _ in range(2):
        run=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',name+'.tex'],cwd=wd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
        if run.returncode:print(run.stdout);sys.exit(run.returncode)
    log=(wd/(name+'.log')).read_text()
    if re.search(r'Overfull|Underfull|Warning|undefined references',log):
        print(log);raise SystemExit('PDF diagnostics require review')
    shutil.copy2(wd/(name+'.pdf'),root/'docs'/(name+'.pdf'))
print('PDF rebuilt; render and visually inspect before release.')
