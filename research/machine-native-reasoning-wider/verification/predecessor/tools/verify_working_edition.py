"""Simple local verifier: source preservation, tests and rendered-PDF structure.
Do not interpret passing as Lean kernel certification or independent peer review.
"""
from pathlib import Path
import subprocess,sys,json,hashlib
import fitz
R=Path(__file__).resolve().parents[1]

def run(cmd,dir):
 p=subprocess.run(cmd,cwd=dir,text=True,capture_output=True)
 return {'command':' '.join(cmd),'exit':p.returncode,'stdout':p.stdout[-900:],'stderr':p.stderr[-900:]}

checks=[run([sys.executable,'formal/check_core83.py'],R),run([sys.executable,'formal/check_joint_contract.py'],R),
 run([sys.executable,'code/check_core.py'],R/'verification/reproduced_core'),
 run([sys.executable,'code/check_admissions.py'],R/'verification/reproduced_core')]
original=(R/'sources/core/src/core.tex').read_text()
recovered=(R/'core_chapters.tex').read_text()
source_span=original[original.index(r'\chapter{From evidence to a reusable state}'):original.index(r'\backmatter')]
assert recovered==source_span, 'Original 9-chapter source span changed'
p=R/'Machine_Native_Reasoning_Working_Edition.pdf'
doc=fitz.open(p)
rect_bad=[]
for i,page in enumerate(doc):
 for b in page.get_text('blocks'):
  if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:
   rect_bad.append(i+1)
assert len(doc)>=50 and not rect_bad
out={'status':'PASS' if all(x['exit']==0 for x in checks) else 'FAIL',
     'pdf_pages':len(doc),'pdf_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
     'toc_entries':len(doc.get_toc()),'source_chapters_verbatim':True,
     'original_proof_environments':source_span.count(r'\begin{theorem}')+source_span.count(r'\begin{proposition}')+source_span.count(r'\begin{corollary}'),
     'out_of_page_text_blocks':len(rect_bad),'checks':checks,
     'no_claim':'PDF and finite checks only. No pinned Lean compilation or external referee certification.'}
(R/'verification/WORKING_EDITION_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))
sys.exit(0 if out['status']=='PASS' else 1)
