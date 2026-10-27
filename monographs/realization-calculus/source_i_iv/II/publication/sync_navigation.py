#!/usr/bin/env python3
"""Refresh current Paper II navigation from the actual built traditional PDF and AUX."""
from pathlib import Path
import hashlib,json,re,shutil
import fitz
ROOT=Path(__file__).resolve().parents[1]
STEM='Paper_II_Traditional_Final';BUILD=ROOT/'publication/build'/STEM
pdf=BUILD/(STEM+'.pdf');aux=BUILD/(STEM+'.aux')
if not pdf.is_file() or not aux.is_file():raise SystemExit('Build the traditional PDF first')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
HISTORY=ROOT/'publication/history/2026-10-08';HISTORY.mkdir(parents=True,exist_ok=True)
for rel in ['CURRENT_PUBLICATION_LOCATORS.json','publication/CURRENT_PUBLICATION_MANIFEST.json']:
 src=ROOT/rel;dst=HISTORY/Path(rel).name
 if src.exists() and not dst.exists():shutil.copy2(src,dst)
old=json.loads((HISTORY/'CURRENT_PUBLICATION_LOCATORS.json').read_text())['labels']

def braced(s,p):
 if s[p]!='{':raise ValueError((p,s[p:p+40]))
 start=p+1;depth=1;p+=1
 while depth:
  if s[p]=='{':depth+=1
  elif s[p]=='}':depth-=1
  p+=1
 return s[start:p-1],p
with fitz.open(pdf) as doc:
 destinations=doc.resolve_names();pages=len(doc)
labels={}
for line in aux.read_text().splitlines():
 if not line.startswith(r'\newlabel{'):continue
 name,pos=braced(line,len(r'\newlabel'))
 if name.endswith('@cref'):continue
 vals,_=braced(line,pos);fields=[];pos=0
 while pos<len(vals) and vals[pos]=='{':v,pos=braced(vals,pos);fields.append(v)
 if len(fields)<4:continue
 number,page,title,dest=fields[:4]
 physical=destinations.get('page.'+page,{}).get('page',-1)+1
 target=destinations.get(dest,{}).get('page',-1)+1
 if physical<=0 or target<=0:raise SystemExit('Unresolved current PDF destination: '+name)
 prior=old.get(name,{})
 labels[name]={'label':name,'number':number,'printed_page':page,'physical_page':physical,
  'title':title,'kind':prior.get('kind',dest.split('.')[0]),'pdf_destination':dest,
  'pdf_destination_physical_page':target}
 if name=='eq:smith-inversion':
  labels[name]['inherited_aux_number']=number;labels[name]['number']=None
  labels[name]['locator_kind']='unnumbered_display_in_section'
current={'schema':'paper-ii-current-publication-locators/2','file_name':pdf.name,'pdf_sha256':sha(pdf),'pdf_pages':pages,'labels':labels,'source_aux_sha256':sha(aux)}
(ROOT/'CURRENT_PUBLICATION_LOCATORS.json').write_text(json.dumps(current,indent=2)+'\n')
# Update headers via stable labels, never by guessing new display numbers.
refs=json.loads((ROOT/'publication/visual_reference_map.json').read_text())['plates']
headers={}
for entry in refs:
 texts=[]
 for ref in entry['references']:
  x=labels[ref['label']]
  if ref['smith_identity']:
   sec=labels['sec:smith-realization']['number'];text=f'Section {sec}, Smith-phase identity (p. {x["printed_page"]})'
  else:text=f'{ref["kind"]} {x["number"]} (p. {x["printed_page"]})'
  texts.append(text)
 headers[entry['plate']]='Traditional paper: '+', '.join(texts)
changed=[]
for rel in ['editable/traditional/visual_atlas.tex','editable/visual_guide/source/pages_final.tex']:
 p=ROOT/rel;s=p.read_text();new=[]
 for line in s.splitlines(True):
  m=re.match(r'\\vpage\{(\d+)\}',line)
  if m and int(m[1]) in headers:
   start=line.rfind('{Traditional paper: ')
   if start<0:raise SystemExit('Missing plate reference group: '+line)
   line=line[:start]+'{'+headers[int(m[1])]+'}\n'
  new.append(line)
 text=''.join(new)
 if text!=s:p.write_text(text);changed.append(rel)
# Keep original canonical/source crosswalk metadata intact; current navigation is separate.
base=json.loads((ROOT/'editable/traditional/canonical_label_to_final.json').read_text());cross={}
for key,record in base.items():
 x=labels[record['final_label']];v=dict(record)
 v.update({'number':x['number'],'page':x['printed_page'],'physical_pdf_page':x['physical_page'],'title':x['title'],'destination':x['pdf_destination'],'pdf_destination_physical_page':x['pdf_destination_physical_page']})
 if key=='eq:smith-inversion':v['locator_text']='Section '+labels['sec:smith-realization']['number']+', Smith-phase identity'
 cross[key]=v
(ROOT/'publication/CURRENT_CANONICAL_CROSSWALK.json').write_text(json.dumps(cross,indent=2)+'\n')
template=(ROOT/'editable/lean_guide/generated/traditional_crosswalk.tex').read_text();out=[]
for line in template.splitlines(True):
 m=re.search(r'\\code\{([^}]+)\}',line)
 if m and m[1] in cross:
  v=cross[m[1]];loc=v.get('locator_text') if v['number'] is None else 'Statement '+v['number']
  line=line.split(' & ')[0]+' & '+r'\code{'+m[1]+'} & '+loc+', p.~'+v['page']+r' \\ \addlinespace'+'\n'
 out.append(line)
(ROOT/'editable/lean_guide/generated/current_traditional_crosswalk.tex').write_text(''.join(out))
report={'schema':'paper-ii-current-navigation-refresh/1','traditional_pdf_sha256':sha(pdf),'labels':len(labels),'page_count':pages,'updated_plate_sources':changed,'destination_page_mismatches':[k for k,x in labels.items() if x['physical_page']!=x['pdf_destination_physical_page']],'historical_navigation_preserved':True}
(ROOT/'publication/CURRENT_NAVIGATION_BUILD.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
