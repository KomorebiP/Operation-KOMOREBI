#!/usr/bin/env python3
"""Publication checks only: source concordance, equation parity, PDF layout."""
from pathlib import Path
import importlib.util,re,json,hashlib,fitz
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('signal_author',HERE/'assemble_traditional.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
tex='\n'.join(mod.parts);md=(HERE/'Signal_Reconstruction_Traditional.md').read_text()
tex_equations=[]
for a in re.finditer(r'\\\[(.*?)\\\]|\\begin\{align\*\}(.*?)\\end\{align\*\}',tex,re.S):
 tex_equations.append(a[1] if a[1] is not None else '\\begin{aligned}'+a[2]+'\\end{aligned}')
md_equations=re.findall(r'\$\$(.*?)\$\$',md,re.S)
norm=lambda x:re.sub(r'\s+','',x)
assert len(tex_equations)==len(md_equations)
assert all(norm(a)==norm(b) for a,b in zip(tex_equations,md_equations))
rows=json.loads((HERE/'Claim_Concordance.json').read_text())['claims']
assert len(re.findall(r'^### SG-\d+',md,re.M))==len(rows)==46
assert md.count('**Proof.**')==len(rows)
for p in [HERE/'Signal_Reconstruction_Traditional.tex',HERE/'Signal_Reconstruction_Traditional.md']:
 assert not any(v<32 and v!=10 for v in p.read_bytes()),f'control bytes: {p}'
anchors=0
for row in rows:
 for a in row['source_anchors']:
  assert hashlib.sha256((HERE.parent/a['file']).read_bytes()).hexdigest()==a['source_sha256'];anchors+=1
log=(HERE/'Signal_Reconstruction_Traditional.log').read_text()
warnings=[x for x in log.splitlines() if any(y in x for y in ['Warning','Overfull','Underfull','Missing character'])]
assert not warnings,warnings
pdf=HERE/'Signal_Reconstruction_Traditional.pdf';doc=fitz.open(pdf);out=[]
for i,page in enumerate(doc):
 for block in page.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    r=fitz.Rect(span['bbox'])
    if r.x0<35 or r.y0<25 or r.x1>page.rect.width-35 or r.y1>page.rect.height-25:
     out.append({'page':i+1,'text':span['text'],'bbox':list(r)})
assert not out,out
pages=[1,5,9,16,17,20,22,25,27,28,30,31]
qa_dir=HERE/'qa';qa_dir.mkdir(exist_ok=True)
for n in pages:doc[n-1].get_pixmap(matrix=fitz.Matrix(1.15,1.15)).save(qa_dir/f'page_{n:02}.png')
qa={'schema':'komorebi.signal_traditional_publication_qa.v1','status':'PASS','pdf_pages':len(doc),'claims':len(rows),'source_anchors':anchors,'md_tex_display_equations':len(tex_equations),'equation_parity':'exact modulo whitespace; align* wrapped as aligned for Markdown','md_proof_count':md.count('**Proof.**'),'warnings':warnings,'text_bound_outliers':out,'rendered_pages':pages,'fresh_Lean':'not claimed','hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [HERE/'Signal_Reconstruction_Traditional.tex',HERE/'Signal_Reconstruction_Traditional.md',pdf,HERE/'Claim_Concordance.json',HERE/'Claim_Concordance.csv']}}
(HERE/'PUBLICATION_QA.json').write_text(json.dumps(qa,indent=2)+'\n')
print(json.dumps(qa))
