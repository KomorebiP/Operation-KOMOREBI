#!/usr/bin/env python3
"""Produce final PDF-page mappings and preservation evidence from the built edition."""
from pathlib import Path
import re,json,hashlib,collections,csv
import fitz
ROOT=Path(__file__).resolve().parent;E=ROOT/'evidence'
M=json.loads((E/'ASSEMBLY_MANIFEST.json').read_text())
PDF=ROOT/'Paper_VII_Traditional_Final.pdf';doc=fitz.open(PDF)
names=doc.resolve_names()
def groups(s):
 out=[];level=0;start=None
 for i,c in enumerate(s):
  if c=='{':
   if level==0:start=i+1
   level+=1
  elif c=='}':
   level-=1
   if level==0:out.append(s[start:i])
 return out
labels={}
for line in (ROOT/'build/Paper_VII_Traditional_Final.aux').read_text().splitlines():
 if not line.startswith(r'\newlabel'):continue
 g=groups(line[len(r'\newlabel'):])
 if len(g)!=2 or '@cref' in g[0]:continue
 f=groups(g[1]);key=g[0]
 if len(f)<4:continue
 dest=names.get(f[3],{})
 labels[key]=dict(number=f[0],printed_page=f[1],title=f[2],destination=f[3],physical_page=dest.get('page',-1)+1)
 if labels[key]['physical_page']<1:raise SystemExit('Missing destination '+key)
for r in M['result_records']+M['section_records']:
 r.update(labels[r['label']]);r['page']=r['physical_page']
for r in M['proof_records']:
 r.update(start_page=labels[r['label']]['physical_page'],end_page=labels[r['end_label']]['physical_page'],printed_start_page=labels[r['label']]['printed_page'],printed_end_page=labels[r['end_label']]['printed_page'])
# All core principal result item numbers come from the final TeX counters.
finite=[]
for r in M['result_records']:
 if r['part']=='core' and r['environment'] in ['theorem','corollary','classical']:
  p=next((x for x in M['proof_records'] if x['result_label']==r['label']),None)
  finite.append(dict(item=r['number'].removeprefix('I.'),environment=r['environment'],title=r['title'],number=r['number'],label=r['label'],page=r['physical_page'],printed_page=r['printed_page'],proof_start_page=p['start_page'] if p else None,proof_end_page=p['end_page'] if p else None))
result=dict(pdf=PDF.name,pdf_pages=len(doc),pdf_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),printed_body_page_offset=6,labels=labels,records=M['result_records'],sections=M['section_records'],proofs=M['proof_records'],finite_items=finite,supplement_crosswalk=M['supplement_crosswalk'])
(E/'FINAL_PAGE_MAP.json').write_text(json.dumps(result,indent=2)+'\n')
with (E/'FINAL_THEOREM_MAP.csv').open('w',newline='') as f:
 fields=['part','environment','number','title','label','page','printed_page','source','source_line']
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(M['result_records'])
md=['# Paper VII final theorem and proof crosswalk','','Final PDF: '+str(len(doc))+' physical pages. Physical page 7 is printed page 1.','', '| Original finite item | Final result | Physical page | Proof pages |','|---|---|---:|---|']
for r in finite:md.append(f"| {r['item']} | {r['number']} {r['title']} | {r['page']} | {r['proof_start_page']}–{r['proof_end_page']} |")
md+=['','## Strengthened proof body inventory','','| Final result | Title | Physical page | Proof pages |','|---|---|---:|---|']
for r in M['result_records']:
 if r['part']=='strong' and r['environment'] in ['theorem','proposition','lemma','corollary']:
  p=next(x for x in M['proof_records'] if x['result_label']==r['label'])
  md.append(f"| {r['environment'].title()} {r['number']} | {r['title']} | {r['page']} | {p['start_page']}–{p['end_page']} |")
md+=['','## Supplement-to-final crosswalk','','Each selected range includes all substantive mathematical sections. Historical compiler/release material remains in the unchanged raw corpus and is explained in the Lean/evidence guide.','']
for sw in M['supplement_crosswalk']:
 md+=['### '+Path(sw['source']).name,'','Selected source lines: '+', '.join(str(a)+'–'+str(b) for a,b in sw['selected_line_ranges'])+'.','', '| Final section | Title | Physical page |','|---|---|---:|']
 for r in M['section_records']:
  if r['part']==sw['prefix']:md.append(f"| {r['number']} | {r['title']} | {r['page']} |")
 md+=['']
(E/'FINAL_THEOREM_AND_SUPPLEMENT_CROSSWALK.md').write_text('\n'.join(md)+'\n')
# Verify retained proof bodies independently of layout, source namespace, and navigation anchors.
def norm(s):
 s=re.sub(r'\\label\{[^{}]*\}|\\phantomsection','',s)
 s=re.sub(r'(core|strong|supp[1-6]):(?=[A-Za-z])','',s)
 return re.sub(r'\s+',' ',s).strip()
proof_checks=[]
for prefix,file,source in [('core','01_finite_core.tex',ROOT.parent/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/related_editorial_v0.5.1/Paper_VII_Proofread_Integrated.tex'),('strong','02_strengthened.tex',ROOT.parent/'source/strengthened/PSC_Paper_VII_Strengthened_Annals_Edition_Final/PSC_Paper_VII_Strengthened_Annals_Edition.tex'),('supp1','03_supplement_01.tex',ROOT.parent/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot/manuscript/Paper_VII_First_Lean_Block_Supplement.tex'),('supp2','03_supplement_02.tex',ROOT.parent/'source/complete/Paper_VII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot/manuscript/Paper_VII_Second_Lean_Block_Supplement.tex')]:
 raw=re.findall(r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}',source.read_text(),re.S)
 final=re.findall(r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}',(ROOT/'parts'/file).read_text(),re.S)
 if len(raw)!=len(final):raise SystemExit('Proof count mismatch '+prefix)
 for i,(a,b) in enumerate(zip(raw,final),1):
  same=norm(a)==norm(b)
  proof_checks.append(dict(part=prefix,index=i,identical_after_anchor_namespace_whitespace_normalization=same,normalized_sha256=hashlib.sha256(norm(b).encode()).hexdigest()))
  if not same:raise SystemExit('Proof changed '+prefix+str(i))
(E/'PROOF_BODY_PRESERVATION.json').write_text(json.dumps(dict(checks=proof_checks,passed=len(proof_checks),explicit_alternative_derivations=3),indent=2)+'\n')
# Proportionate PDF preflight: no off-page text and every internal link destination in range.
bounds=[];badlinks=[];linkcount=0
for i,p in enumerate(doc):
 for block in p.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox']
    if x0 < -1 or y0 < -1 or x1 > p.rect.width+1 or y1 > p.rect.height+1:bounds.append(dict(page=i+1,text=span['text'],bbox=span['bbox']))
 for link in p.get_links():
  if link['kind']==fitz.LINK_GOTO:
   linkcount+=1
   if not 0<=link.get('page',-1)<len(doc):badlinks.append(dict(page=i+1,link=link))
counts={p:dict(collections.Counter(x['environment'] for x in M['result_records'] if x['part']==p)) for p in ['core','strong','supp1','supp2']}
preflight=dict(pdf_pages=len(doc),pdf_bytes=PDF.stat().st_size,page_labels=doc.get_page_labels(),named_destinations=len(names),internal_links=linkcount,invalid_internal_links=badlinks,off_page_text=bounds,encrypted=doc.is_encrypted,result_counts=counts,explicit_proof_environments=len(M['proof_records']),normalized_preserved_source_proof_bodies=len(proof_checks),final_log_diagnostics=json.loads((E/'FINAL_DIAGNOSTICS.json').read_text()))
(E/'PDF_PREFLIGHT.json').write_text(json.dumps(preflight,indent=2)+'\n')
print(json.dumps(dict(pdf_pages=len(doc),finite_items=len(finite),strengthened_results=sum(r['part']=='strong' and r['proof_required'] for r in M['result_records']),proofs=len(M['proof_records']),proofs_unchanged=len(proof_checks),labels=len(labels),invalid_links=len(badlinks),off_page_text=len(bounds)),indent=2))
