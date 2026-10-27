#!/usr/bin/env python3
"""Bounded reference-section review for an assembled Realization Calculus PDF."""
from pathlib import Path
import argparse,hashlib,json,re
import fitz
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2]

def sha(data):return hashlib.sha256(data).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--final',action='store_true');ap.add_argument('--render',action='store_true');args=ap.parse_args()
 files={name:(ROOT/name).read_bytes() for name in ['output/Realization_Calculus.pdf','book/build_spec.json','book/page_map.json','book/resolved_link_map.json','editorial/volume_finish/reference_plan.json']}
 spec=json.loads(files['book/build_spec.json']);mapping=json.loads(files['book/page_map.json'])['pages'];links=json.loads(files['book/resolved_link_map.json']);plan=json.loads(files['editorial/volume_finish/reference_plan.json'])
 doc=fitz.open(stream=files['output/Realization_Calculus.pdf'],filetype='pdf');comps={c['id']:c for p in spec['parts'] for c in p['components']};leaves={l['id']:l for l in spec['leaves']};units=[u for u in spec['reading_units'] if u['kind']=='references'];groups={g['id']:g for g in plan['bibliography_groups']}
 failures=[];records=[];pages=[];citation_total=0
 def require(value,message):
  if not value:failures.append(message)
 require(len(doc)==spec['expected_total_pages'],'PDF and build specification page totals differ')
 require(len(units)==15,'Expected15 source groups')
 glossary_end=spec['glossary']['index_start']+spec['glossary']['pages']-1;start=leaves['sources_references']['book_index'];require(start==glossary_end+1,'Sources do not immediately follow glossary')
 require(start+40==len(doc),'Sources and references are not final40 pages')
 for unit in units:
  ident=unit['id'].removeprefix('references_');g=groups[ident];c=comps[g['component_id']];rg=next(x for x in c['reference_groups'] if x['id']==ident);book_indices=[c['book_pages'][str(n)] for n in rg['pages']];text='\n'.join(doc[n].get_text() for n in book_indices);missing=[]
  for key in g['retained_citation_keys']:
   k=re.escape(key);pattern=r'(?m)^\s*(?:\['+k+r'\]|'+k+r'\.(?=\s|$)|'+k+r'(?=\s|$))'
   if not re.search(pattern,text):missing.append(key)
  require(not missing,'Missing source keys '+ident+': '+repr(missing));require(all(n>start for n in book_indices),'References precede source division: '+ident);require(book_indices==list(range(unit['index_start']+1,unit['index_end']+1)),'Noncontiguous reference group '+ident)
  for n,raw in zip(book_indices,rg['pages']):
   mr=mapping[str(n)];require(mr['unit_kind']=='references' and mr['component']==c['id'] and mr['source_index']==raw,'Page map mismatch '+ident)
  citation_total+=len(g['retained_citation_keys']);pages.extend(book_indices)
  records.append({'id':ident,'title':unit['title'],'opening_pdf_page':unit['index_start']+1,'reference_pdf_pages':[n+1 for n in book_indices],'raw_component_pages_1based':[n+1 for n in rg['pages']],'source_keys_expected':g['retained_citation_keys'],'source_keys_found':len(g['retained_citation_keys'])-len(missing),'missing_source_keys':missing})
 require(len(pages)==24 and len(set(pages))==24,'Expected24 distinct reference pages');require(citation_total==309,'Expected309 grouped source keys')
 # Match every recorded reference destination to an actual PDF annotation.
 refset=set(pages);checks=[];mixed=[];cache={}
 for record in links:
  target=record.get('target_book_index')
  if target not in refset or record.get('kind')!='source':continue
  source=record['source_book_index'];actual=cache.setdefault(source,doc[source].get_links());box=fitz.Rect(record['rect']);matches=[l for l in actual if l.get('kind')==fitz.LINK_GOTO and max(abs(a-b) for a,b in zip(l['from'],box))<.05 and l.get('page')==target and max(abs(a-b) for a,b in zip(l['to'],record['target_point']))<.05]
  require(len(matches)==1,'Missing or ambiguous actual reference link at PDF page'+str(source+1));checks.append({'from_pdf_page':source+1,'to_pdf_page':target+1,'reference_routed':record.get('resolution',{}).get('reference_routed',False)})
  if record.get('resolution',{}).get('reference_routed'):mixed.append(checks[-1])
 # Check all exact original names entering split reference regions independently.
 route_rows=[]
 for cid,c in comps.items():
  if not c.get('reference_routes'):continue
  with fitz.open(ROOT/c['path']) as component:
   for route in c['reference_routes']:
    region=fitz.Rect(route['rect']);target=c['book_pages'][str(route['target_source_page'])];hits=[]
    for name,destination in component.resolve_names().items():
     if destination['page']!=route['source_page']:continue
     point=fitz.Point(destination['to'][0],component[route['source_page']].rect.height-destination['to'][1])
     if region.contains(point):hits.append(name)
    require(target in refset,'Split reference target outside backmatter '+cid);require(str(route['source_page']) in c['book_pages'],'Mixed main page omitted '+cid)
    route_rows.append({'component_id':cid,'original_page_1based':route['source_page']+1,'target_page_1based':route['target_source_page']+1,'target_pdf_page':target+1,'named_targets_inside_reference_region':hits,'translation':route['point_offset']})
 require(len(route_rows)==3,'Expectedthree mixed reference routes')
 # A PDF may change while final assembly runs. Explicitly classify this receipt.
 current_hash=sha((ROOT/'output/Realization_Calculus.pdf').read_bytes());unchanged=current_hash==sha(files['output/Realization_Calculus.pdf'])
 if args.final:require(unchanged,'PDF changed during final review')
 out=ROOT/'editorial/volume_finish/reference_section_samples';out.mkdir(exist_ok=True)
 rendered=[]
 if args.render:
  for n in pages:
   path=out/f'reference_pdf_{n+1:04}.png';pix=doc[n].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False);pix.save(path);rendered.append({'pdf_page':n+1,'path':str(path.relative_to(ROOT))})
  for batch in range(0,len(rendered),4):
   sheet=Image.new('RGB',(1224,1640),'#eee8ee');draw=ImageDraw.Draw(sheet)
   for k,row in enumerate(rendered[batch:batch+4]):
    x=(k%2)*612;y=(k//2)*820;im=Image.open(ROOT/row['path']);sheet.paste(im,(x,y+28));draw.text((x+14,y+7),'PDF page '+str(row['pdf_page']),fill='black')
   sheet.save(out/f'contact_{batch//4+1}.png')
  doc[start].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(out/'sources_division.png')
 report={'status':'PASS' if not failures else 'FAIL','classification':'FINAL' if args.final else 'PROBE','scope':'Bounded independent structure, source-key preservation, actual link-annotation and mixed-route review. Visual receipt follows separate image inspection.','book_pages':len(doc),'pages':len(doc),'pdf_sha256':sha(files['output/Realization_Calculus.pdf']),'sources_division_pdf_page':start+1,'glossary_last_pdf_page':glossary_end+1,'groups':records,'groups_count':len(records),'reference_pages':len(pages),'source_keys_found':citation_total-sum(len(x['missing_source_keys']) for x in records),'source_keys_expected':309,'actual_reference_link_annotations_checked':len(checks),'mixed_reference_links_checked':len(mixed),'mixed_routes':route_rows,'files':{k:{'bytes':len(v),'sha256':sha(v)} for k,v in files.items()},'pdf_unchanged_during_review':unchanged,'rendered':rendered,'failures':failures}
 (ROOT/'editorial/volume_finish/reference_section_review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['files','groups','rendered','mixed_routes']},indent=2))
 if failures:raise SystemExit(1)

if __name__=='__main__':main()
