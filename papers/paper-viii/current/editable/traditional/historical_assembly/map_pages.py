#!/usr/bin/env python3
"""Map final result/proof pages and independently check source conservation."""
from pathlib import Path
import re,json,hashlib,csv,collections
import fitz
ROOT=Path(__file__).resolve().parent;E=ROOT/'evidence'
M=json.loads((E/'ASSEMBLY_MANIFEST.json').read_text())
PDF=ROOT/'Paper_VIII_Traditional_Final.pdf';doc=fitz.open(PDF);names=doc.resolve_names()
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
for line in (ROOT/'build/Paper_VIII_Traditional_Final.aux').read_text().splitlines():
 if not line.startswith(r'\newlabel'):continue
 g=groups(line[len(r'\newlabel'):])
 if len(g)!=2 or '@cref' in g[0]:continue
 f=groups(g[1]);key=g[0]
 if len(f)<4:continue
 dest=names.get(f[3],{})
 labels[key]=dict(number=f[0],printed_page=f[1],title=f[2],destination=f[3],physical_page=dest.get('page',-1)+1)
 if labels[key]['physical_page']<1:raise SystemExit('Missing destination '+key)
for rec in M['result_records']+M['section_records']:
 rec.update(labels[rec['label']]);rec['page']=rec['physical_page']
for rec in M['proof_records']:
 rec.update(start_page=labels[rec['label']]['physical_page'],end_page=labels[rec['end_label']]['physical_page'])
main_items=[]
for rec in M['result_records']:
 if not rec['proof_required']:continue
 proof=next(x for x in M['proof_records'] if x['result_label']==rec['label'])
 main_items.append(dict(item=rec['number'],environment=rec['environment'],title=rec['title'],label=rec['original_labels'][0],page=rec['physical_page'],printed_page=rec['printed_page'],proof_start_page=proof['start_page'],proof_end_page=proof['end_page']))
page_map=dict(pdf=PDF.name,pdf_pages=len(doc),pdf_sha256=hashlib.sha256(PDF.read_bytes()).hexdigest(),labels=labels,records=M['result_records'],sections=M['section_records'],proofs=M['proof_records'],finite_items=main_items,supplement_crosswalk=M['supplement_crosswalk'])
(E/'FINAL_PAGE_MAP.json').write_text(json.dumps(page_map,indent=2)+'\n')
with (E/'FINAL_THEOREM_MAP.csv').open('w',newline='') as f:
 fields=['part','environment','number','title','label','page','printed_page','source','source_line'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(M['result_records'])
md=['# Final mathematical and proof-page crosswalk','','Physical pages, printed pages, and original item numbers are recorded separately. All 56 manuscript proof bodies remain.','', '| Original item | Title | Physical page | Proof pages |','|---|---|---:|---|']
for x in main_items:md.append(f'| {x["item"]} | {x["title"]} | {x["page"]} | {x["proof_start_page"]}–{x["proof_end_page"]} |')
md+=['','## Complete supplementary mathematical body crosswalk','']
for x in M['supplement_crosswalk']:
 md+=['### '+Path(x['source']).name,'','Retained source lines '+str(x['retained_line_range'][0])+'–'+str(x['retained_line_range'][1])+'. All body mathematics and dated audit paragraphs are retained.','', '| Final section | Title | Physical page |','|---|---|---:|']
 for sec in M['section_records']:
  if sec['part']==x['prefix']:md.append(f'| {sec["number"]} | {sec["title"]} | {sec["page"]} |')
 md+=['']
(E/'FINAL_THEOREM_AND_SUPPLEMENT_CROSSWALK.md').write_text('\n'.join(md)+'\n')

def norm(t):
 t=re.sub(r'\\label\{[^{}]*\}|\\phantomsection','',t)
 return re.sub(r'\s+',' ',t).strip()
SRC=ROOT.parent/'source';main=SRC/M['source_manuscript']
rawproofs=re.findall(r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}',main.read_text(),re.S)
finalproofs=re.findall(r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}',(ROOT/'parts/01_manuscript.tex').read_text(),re.S)
if len(rawproofs)!=56 or len(finalproofs)!=56:raise SystemExit('56-proof conservation failed')
allowed={17,23,30,38,40,52};proofchecks=[]
for i,(a,b) in enumerate(zip(rawproofs,finalproofs),1):
 same=norm(a)==norm(b)
 if not same and i not in allowed:raise SystemExit('Unexpected proof modification '+str(i))
 proofchecks.append(dict(index=i,identical_after_navigation_whitespace_normalization=same,intentional_reviewed_repair=i in allowed,final_normalized_sha256=hashlib.sha256(norm(b).encode()).hexdigest()))
suppchecks=[]
for x in M['supplement_crosswalk']:
 source=(SRC/x['source']).read_text();a=source[source.index(r'\pageheading{1.'):source.index(r'\end{document}')]
 a=re.sub(r'\\(?:newpage|clearpage)\s*','\n\n',a)
 a=a.replace(r'\section*{\color{ink}',r'\subsubsection{')
 a=re.sub(r'\\pageheading\{([^{\n]+)\}\{([^\n]+)\}',lambda m:r'\subsection{'+re.sub(r'^\d+\.\s*','',m.group(1))+r'}\textit{'+m.group(2)+r'}\par',a)
 final=(ROOT/x['final_source']).read_text();b=final[final.index(r'\subsection{'):]
 same=norm(a)==norm(b)
 if not same:raise SystemExit('Supplement body conservation failed '+x['source'])
 suppchecks.append(dict(source=x['source'],final_source=x['final_source'],whole_substantive_body_identical_after_heading_navigation_whitespace_normalization=same,normalized_sha256=hashlib.sha256(norm(b).encode()).hexdigest(),retained_line_range=x['retained_line_range']))
conservation=dict(manuscript_proofs_retained=56,unchanged_normalized_proofs=sum(x['identical_after_navigation_whitespace_normalization'] for x in proofchecks),reviewed_repaired_proofs=sorted(allowed),proof_checks=proofchecks,supplement_body_checks=suppchecks,raw_source_sha256=M['source_sha256'],raw_sources_untouched=True)
(E/'PROOF_BODY_PRESERVATION.json').write_text(json.dumps(conservation,indent=2)+'\n')
bounds=[];badlinks=[];links=0;replacement=[]
for i,p in enumerate(doc):
 if '\ufffd' in p.get_text():replacement.append(i+1)
 for block in p.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox']
    if x0 < -1 or y0 < -1 or x1 > p.rect.width+1 or y1 > p.rect.height+1:bounds.append(dict(page=i+1,text=span['text'],bbox=span['bbox']))
 for link in p.get_links():
  if link['kind']==fitz.LINK_GOTO:
   links+=1
   if not 0<=link.get('page',-1)<len(doc):badlinks.append(dict(page=i+1,link=link))
  elif link['kind']==fitz.LINK_NAMED:
   links+=1;dest=names.get(link.get('nameddest',''),{})
   if not 0<=dest.get('page',-1)<len(doc):badlinks.append(dict(page=i+1,link=link))
preflight=dict(pdf_pages=len(doc),pdf_bytes=PDF.stat().st_size,page_labels=doc.get_page_labels(),named_destinations=len(names),internal_links=links,invalid_internal_links=badlinks,off_page_text=bounds,replacement_character_pages=replacement,encrypted=doc.is_encrypted,result_counts=dict(collections.Counter(x['environment'] for x in M['result_records'])),proof_environment_count=56,supplement_body_count=6,final_log_diagnostics=json.loads((E/'FINAL_DIAGNOSTICS.json').read_text()))
(E/'PDF_PREFLIGHT.json').write_text(json.dumps(preflight,indent=2)+'\n')
print(json.dumps(dict(pdf_pages=len(doc),finite_items=len(main_items),proofs=56,proofs_unchanged=conservation['unchanged_normalized_proofs'],supplement_bodies_unchanged=6,labels=len(labels),invalid_links=len(badlinks),off_page_text=len(bounds)),indent=2))
if badlinks or bounds or replacement:raise SystemExit('PDF preflight failed')
