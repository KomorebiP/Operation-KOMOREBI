#!/usr/bin/env python3
"""Check actual delivered PDF destinations and source preservation. No Lean run."""
from __future__ import annotations
import argparse, collections, hashlib, json, re
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(root=ROOT):
 errors=[];pd=root/'publication/pdfs';raw=root/'predecessor/editable';src=root/'publication/source';record={}
 old=(raw/'traditional/Paper_XII_Traditional_Final.tex').read_text();new=(src/'traditional/Paper_XII_Traditional_Final.tex').read_text()
 proof=lambda t:re.findall(r'\\begin\{proof\}(.*?)\\end\{proof\}',t,re.S)
 statements=lambda t:re.findall(r'\\begin\{(theorem|proposition|lemma|corollary|definition|example|standardfact|remark)\}(.*?)\\end\{\1\}',t,re.S)
 record['proof_bodies']={'count':len(proof(new)),'byte_identical':proof(old)==proof(new)}
 record['statement_bodies']={'count':len(statements(new)),'byte_identical':statements(old)==statements(new)}
 if not record['proof_bodies']['byte_identical'] or not record['statement_bodies']['byte_identical']:errors.append('Main proof or statement changed')
 changed=[];preserved=0
 for p in raw.rglob('*'):
  if not p.is_file() or p.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.pfb','.pfa'}:continue
  rel=p.relative_to(raw);q=src/rel
  if not q.is_file():errors.append('Missing editable predecessor '+str(rel));continue
  if sha(p)==sha(q):preserved+=1
  else:changed.append({'path':str(rel),'before':sha(p),'after':sha(q)})
 record['editable_files']={'preserved':preserved,'changed':changed}
 cat=json.loads((src/'lean_guide/data/source_catalog.json').read_text());module_rows=[]
 for row in cat:
  p=src/'lean_guide/formal_release/lean'/row['source'];ok=sha(p)==row['sha256'];module_rows.append({'module':row['module'],'matches':ok,'sha256':sha(p)})
  if not ok:errors.append('Module mismatch '+row['module'])
 record['production_sources']={'count':len(cat),'all_match':all(x['matches'] for x in module_rows),'sources':module_rows}
 exts=list((raw/'lean_guide/excerpts').rglob('*'));xp=[p for p in exts if p.is_file()]
 record['excerpt_files']={'count':len(xp),'byte_identical':all(sha(p)==sha(src/p.relative_to(raw)) for p in xp)}
 if not record['excerpt_files']['byte_identical']:errors.append('Excerpt changed')
 cited=set()
 for m in re.finditer(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}',new):cited.update(x.strip() for x in m[1].split(','))
 bib=set(re.findall(r'\\bibitem\{([^}]+)\}',(src/'traditional/Paper_XII_Traditional_Final.bbl').read_text()))
 record['bibliography']={'cited_keys':len(cited),'bibitems':len(bib),'missing':sorted(cited-bib)}
 if cited-bib:errors.append('Missing bibliography keys')
 loc=json.loads((root/'evidence/block01/LOCATORS.json').read_text());outputs={r['file']:fitz.open(pd/r['file']) for r in json.loads((root/'evidence/block01/BUILD.json').read_text())['outputs'].values()}
 roles={'traditional':'Paper_XII_Traditional_v1.0.0.pdf','visual_guide':'Paper_XII_Visual_Guide_v1.0.0.pdf','lean_guide':'Paper_XII_Lean_Guide_v1.0.0.pdf'}
 stats=[];remote_seen=[]
 for name,d in outputs.items():
  internal=remote=0;names=d.resolve_names();bad_spans=[];replacement=[]
  for pg in d:
   for line in pg.get_text('dict')['blocks']:
    for ln in line.get('lines',[]):
     for sp in ln['spans']:
      x0,y0,x1,y1=sp['bbox']
      if x0<-.5 or y0<-.5 or x1>pg.rect.width+.5 or y1>pg.rect.height+.5:bad_spans.append({'page':pg.number+1,'text':sp['text'],'bbox':sp['bbox']})
      if '\ufffd' in sp['text']:replacement.append(pg.number+1)
   for li in pg.get_links():
    if li['kind']==fitz.LINK_GOTOR:
     remote+=1;target=li['file'];obj=d.xref_object(li['xref']);ma=re.search(r'/D\s*\[\s*(\d+)\s*/XYZ\s*([\d.+-]+)\s*([\d.+-]+)',obj)
     if target not in outputs or ma is None:errors.append(f'Invalid remote destination {name}:{pg.number+1}');continue
     tp=int(ma[1]);xy=[float(ma[2]),float(ma[3])]
     if tp<0 or tp>=len(outputs[target]):errors.append('Remote page out of range')
     choices=[r for r in loc['routes'] if roles[r['source']]==name and r['source_pdf_page']==pg.number+1 and r['target_file']==target and r['target_pdf_page']==tp+1 and max(abs(x-y) for x,y in zip(r['target_point'],xy))<.02]
     if not choices:errors.append(f'Unexpected remote coordinates {name}:{pg.number+1}:{target}:{tp+1}:{xy}')
     else:
      r=next((c for c in choices if c['id'] not in remote_seen), choices[0]);native=outputs[target].resolve_names()[r['anchor']]
      if native['page']!=tp or max(abs(x-y) for x,y in zip(native['to'],xy))>.02:errors.append('Remote coordinate disagrees with named target '+r['id'])
      remote_seen.append(r['id'])
    elif li['kind'] in [fitz.LINK_GOTO,fitz.LINK_NAMED]:
     internal+=1
     if 'nameddest' in li:
      if li['nameddest'] not in names or not 0<=names[li['nameddest']]['page']<len(d):errors.append('Bad named link '+str(li))
     elif not 0<=li.get('page',-1)<len(d):errors.append('Bad internal link '+str(li))
    elif li['kind']==fitz.LINK_URI:
     if li.get('uri','').startswith('p12-route:'):errors.append('Unresolved route')
    else:errors.append('Unexpected link type '+str(li))
  if bad_spans:errors.append('Out-of-page spans '+name)
  if replacement:errors.append('Replacement glyph '+name)
  stats.append({'file':name,'pages':len(d),'bookmarks':len(d.get_toc()),'internal_links':internal,'companion_links':remote,'out_of_page_spans':bad_spans,'replacement_glyph_pages':replacement,'sha256':sha(pd/name)})
 record['pdfs']=stats;record['total_pages']=sum(x['pages'] for x in stats);record['internal_links']=sum(x['internal_links'] for x in stats);record['companion_links']=sum(x['companion_links'] for x in stats)
 routes=json.loads((root/'evidence/block01/ROUTES.json').read_text())
 if set(remote_seen)!=set(routes):errors.append('Route inventory mismatch')
 record['registered_routes']=len(routes)
 vd=outputs[roles['visual_guide']];vn=vd.resolve_names();vpages=[vn[f'visual{i}.1']['page'] for i in range(1,28)]
 record['visual_lesson_pages']=vpages
 if vpages!=list(range(1,28)) or len(vd)!=28:errors.append('Visual lesson pagination not one lesson per page')
 forms=re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}',new);record['main_figure_references']=forms
 for d in outputs.values():d.close()
 record['errors']=errors;record['status']='PASS' if not errors else 'FAIL';record['fresh_lean']=False
 return record
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();j=check();a.output.write_text(json.dumps(j,indent=2)+'\n');print(json.dumps({k:j[k] for k in ['status','proof_bodies','statement_bodies','total_pages','internal_links','companion_links','registered_routes','errors']},indent=2));raise SystemExit(j['status']!='PASS')
