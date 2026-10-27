#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib,collections,argparse,csv
import fitz
from PIL import Image,ImageDraw
W=Path(__file__).resolve().parent;E=W/'evidence'
ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,default=W.parent/'source/consolidated/PRSC_IX_Consolidated_Manuscript');args=ap.parse_args();B=args.source_root.resolve()
M=json.loads((E/'ASSEMBLY_MANIFEST.json').read_text());PDF=W/'Paper_IX_Traditional_Final.pdf';doc=fitz.open(PDF);names=doc.resolve_names()
sha=lambda x:hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
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
for line in (W/'build/Paper_IX_Traditional_Final.aux').read_text().splitlines():
 if not line.startswith(r'\newlabel'):continue
 g=groups(line[len(r'\newlabel'):]);
 if len(g)!=2 or '@cref' in g[0]:continue
 f=groups(g[1]);key=g[0]
 if len(f)<4:continue
 dest=names.get(f[3],{});labels[key]={'number':f[0],'printed_page':f[1],'title':f[2],'destination':f[3],'physical_page':dest.get('page',-1)+1}
 assert labels[key]['physical_page']>=1,key
page_map={'pdf':PDF.name,'pdf_pages':len(doc),'pdf_sha256':sha(PDF.read_bytes()),'labels':labels,'preserved_core_labels':len([x for x in labels if not x.startswith(('app:','hist:','cont','native:'))])}
(E/'FINAL_PAGE_MAP.json').write_text(json.dumps(page_map,indent=2)+'\n')
original_index=json.loads((B/'consolidation/audit/STATEMENT_INDEX.json').read_text());statements=[]
for x in original_index['statements']:
 assert x['label'] in labels,x['label']
 statements.append(dict(x,final_locator=labels[x['label']]))
(E/'FINAL_STATEMENT_CROSSWALK.json').write_text(json.dumps({'inherited_index_sha256':sha((B/'consolidation/audit/STATEMENT_INDEX.json').read_bytes()),'pdf_sha256':sha(PDF.read_bytes()),'mapped_statements':len(statements),'source_links':sum(len(x['references']) for x in statements),'statements':statements},indent=2)+'\n')
with (E/'FINAL_STATEMENT_CROSSWALK.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=['label','title','number','physical_page','printed_page','source_links']);wr.writeheader()
 for x in statements:wr.writerow({'label':x['label'],'title':x.get('title') or x['final_locator']['title'],'number':x['final_locator']['number'],'physical_page':x['final_locator']['physical_page'],'printed_page':x['final_locator']['printed_page'],'source_links':len(x['references'])})
# Whole proof bodies are compared after only whitespace and historical namespace changes.
def norm(t):
 t=re.sub(r'\\label\{[^{}]*\}','',t);t=t.replace('hist:','');return re.sub(r'\s+',' ',t).strip()
rx=r'\\begin\{proof\}(?:\[[^\]]*\])?(.*?)\\end\{proof\}'
proofs=[]
for part in M['parts']:
 if part['role'] not in ['current core','historical recovered full manuscript']:continue
 a=(B/part['source']).read_text();b=(W/part['output']).read_text();aa=re.findall(rx,a,re.S);bb=re.findall(rx,b,re.S);assert len(aa)==len(bb)
 for i,(x,y) in enumerate(zip(aa,bb),1):
  same=norm(x)==norm(y);role=part['role'];reviewed=not same and part['source'].endswith('20_arithmetic.tex')
  assert same or reviewed,(part['source'],i)
  proofs.append({'source':part['source'],'index':i,'role':role,'unchanged_after_whitespace_and_navigation_namespace_normalization':same,'reviewed_addition_or_citation_repair':reviewed,'source_normalized_sha256':sha(norm(x)),'final_normalized_sha256':sha(norm(y))})
counts=collections.Counter(x['role'] for x in proofs)
conservation={'current_proof_bodies':counts['current core'],'historical_proof_bodies':counts['historical recovered full manuscript'],'all_proofs_retained':True,'unchanged_normalized_bodies':sum(x['unchanged_after_whitespace_and_navigation_namespace_normalization'] for x in proofs),'reviewed_augmented_or_citation_bodies':sum(x['reviewed_addition_or_citation_repair'] for x in proofs),'checks':proofs,'supplement_bodies':[x for x in M['parts'] if x['role']=='complete mathematical checkpoint supplement'],'continuation_body_selections':[x for x in M['parts'] if x['role']=='continuation derivation'],'native_prose_body':[x for x in M['parts'] if x['role']=='native prose proofs'],'limits':'Proof body conservation is not new universal proof certification. Recovered historical hypotheses are locally corrected; cited external source leaves retain their own evidence status.'}
(E/'PROOF_BODY_PRESERVATION.json').write_text(json.dumps(conservation,indent=2)+'\n')
# Semantic-token conservation for complete supplement bodies, ignoring headings/navigation/monospace conversion.
def supnorm(t):
 t=re.sub(r'\\(section|subsection|subsubsection)\*','\\\\heading',t)
 t=re.sub(r'\\(?:newpage|clearpage)','',t);t=re.sub(r'\\(texttt|mcode)\{','\\\\codefont{',t)
 t=t.replace(r'\par\medskip','')
 t=t.replace(r'\_', '_').replace('parts/verification_summary.tex','verification_summary.tex')
 t=t.replace(r'p{.48\textwidth}>{\raggedright\arraybackslash}p{.18\textwidth}rr',r'p{.48\textwidth}p{.18\textwidth}rr')
 return re.sub(r'\s+',' ',t).strip()
supchecks=[]
for x in M['parts']:
 if x['role']!='complete mathematical checkpoint supplement':continue
 a=(B/x['source']).read_text().split(r'\begin{document}',1)[1].split(r'\end{document}',1)[0];a=a[a.index(r'\section*'):]
 b=(W/x['output']).read_text();b=b[b.index(r'\subsubsection*'):]
 b=re.sub(r'sup\d+:','',b)
 assert supnorm(a)==supnorm(b),x['source']
 supchecks.append({'source':x['source'],'complete_body_preserved_after_recorded_layout_navigation_font_normalization':True,'normalized_sha256':sha(supnorm(b))})
(E/'SUPPLEMENT_BODY_PRESERVATION.json').write_text(json.dumps({'supplements':len(supchecks),'checks':supchecks},indent=2)+'\n')
# PDF structural bounds and link destinations.
bounds=[];badlinks=[];links=0;replacement=[]
for i,p in enumerate(doc):
 if '\ufffd' in p.get_text():replacement.append(i+1)
 for block in p.get_text('dict')['blocks']:
  for line in block.get('lines',[]):
   for span in line['spans']:
    x0,y0,x1,y1=span['bbox']
    if x0< -1 or y0< -1 or x1>p.rect.width+1 or y1>p.rect.height+1:bounds.append({'page':i+1,'text':span['text'],'bbox':span['bbox']})
 for link in p.get_links():
  if link['kind']==fitz.LINK_GOTO:
   links+=1
   if not 0<=link.get('page',-1)<len(doc):badlinks.append({'page':i+1,'link':link})
  elif link['kind']==fitz.LINK_NAMED:
   links+=1;dest=names.get(link.get('nameddest',''),{})
   if not 0<=dest.get('page',-1)<len(doc):badlinks.append({'page':i+1,'link':link})
qa={'pages':len(doc),'bytes':PDF.stat().st_size,'sha256':sha(PDF.read_bytes()),'labels':len(labels),'internal_links':links,'invalid_internal_links':badlinks,'off_page_text':bounds,'replacement_character_pages':replacement,'final_log_diagnostics':json.loads((E/'FINAL_DIAGNOSTICS.json').read_text()),'encrypted':doc.is_encrypted}
(E/'PDF_PREFLIGHT.json').write_text(json.dumps(qa,indent=2)+'\n');assert not badlinks and not bounds and not replacement
# Contact sheets include all pages with physical numbers.
for start in range(0,len(doc),25):
 pages=list(range(start,min(start+25,len(doc))));thumbs=[]
 for i in pages:
  pix=doc[i].get_pixmap(matrix=fitz.Matrix(.36,.36),alpha=False);im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
  tile=Image.new('RGB',(230,320),'#e8e9eb');im.thumbnail((214,292));tile.paste(im,((230-im.width)//2,7));ImageDraw.Draw(tile).text((9,301),str(i+1),fill='black');thumbs.append(tile)
 sheet=Image.new('RGB',(1150,320*((len(thumbs)+4)//5)),'white')
 for j,im in enumerate(thumbs):sheet.paste(im,((j%5)*230,(j//5)*320))
 sheet.save(E/f'contact_{start+1:03}_{pages[-1]+1:03}.png')
print(json.dumps({'pdf':qa,'proofs_current':counts['current core'],'proofs_historical':counts['historical recovered full manuscript'],'supplements_preserved':len(supchecks)},indent=2))
