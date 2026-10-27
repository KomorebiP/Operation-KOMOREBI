"""Build the theoretical atlas using Python figures and an installed XeLaTeX."""
from pathlib import Path
import hashlib,json,subprocess,sys
import fitz
ROOT=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(ROOT/'generate_figures.py')],cwd=ROOT,check=True)
for pass_no in (1,2):
    run=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error','-output-directory=build','-jobname=Realization_Calculus_Large_Signal_Model_Theoretical_Atlas','atlas.tex'],cwd=ROOT,capture_output=True,text=True)
    (ROOT/'build'/f'latex_pass_{pass_no}.log').write_text(run.stdout+'\n'+run.stderr)
    if run.returncode:
        print(run.stdout[-6000:]);raise SystemExit(run.returncode)
pdf=ROOT/'build/Realization_Calculus_Large_Signal_Model_Theoretical_Atlas.pdf'
doc=fitz.open(pdf)
issues=[]
for i,page in enumerate(doc):
    for block in page.get_text('blocks'):
        r=fitz.Rect(block[:4])
        if r.x0<18 or r.y0<14 or r.x1>page.rect.width-18 or r.y1>page.rect.height-14:issues.append({'page':i+1,'bounds':list(r),'text':block[4][:90]})
log=(ROOT/'build/Realization_Calculus_Large_Signal_Model_Theoretical_Atlas.log').read_text()
result={'built':True,'pages':len(doc),'figures':len(list((ROOT/'figures').glob('*.pdf'))),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'out_of_page_text':issues,'overfull_boxes':[line for line in log.splitlines() if 'Overfull' in line],'missing_glyphs':[line for line in log.splitlines() if 'Missing character' in line],'visual_review':'pending','fresh_Lean_execution':False}
(ROOT/'build/BUILD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
