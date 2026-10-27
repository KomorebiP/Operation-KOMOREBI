#!/usr/bin/env python3
"""Three-pass local PDF build with portable full-math Markdown export."""
from pathlib import Path
import subprocess,sys,shutil,json,hashlib,re
B=Path(__file__).resolve().parent
NAME='H12_Cubic_Divisor_Traditional'
if not shutil.which('pdflatex'):raise SystemExit('pdflatex required')
for i in range(1,4):
 with (B/f'build_pass{i}.log').open('w') as f:
  subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','-file-line-error',NAME+'.tex'],cwd=B,stdout=f,stderr=subprocess.STDOUT,check=True)
log=(B/'build_pass3.log').read_text()
fail=[s for s in ['Overfull','undefined references','undefined citations','multiply defined'] if s in log]
if fail:raise SystemExit('Final typesetting preflight failed: '+', '.join(fail))
if '--skip-markdown' not in sys.argv:
 subprocess.run([sys.executable,str(B/'export_markdown.py')],cwd=B,check=True)
report={'source':NAME+'.tex','source_sha256':hashlib.sha256((B/(NAME+'.tex')).read_bytes()).hexdigest(),'pdf':NAME+'.pdf','pdf_sha256':hashlib.sha256((B/(NAME+'.pdf')).read_bytes()).hexdigest(),'passes':3,'typesetting_preflight':'PASS','visual_page_review':'pending final raster inspection'}
report['all_tex_sources']={str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(B.glob('sections/*.tex'))+[B/(NAME+'.tex')]}
report['figure_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((B/'figures').glob('*.png'))}
try:
 import fitz
 with fitz.open(B/(NAME+'.pdf')) as d:report['pages']=len(d)
except ImportError:pass
(B/'MANUSCRIPT_BUILD_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
print(NAME+'.pdf')
