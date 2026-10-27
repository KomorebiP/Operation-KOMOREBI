from pathlib import Path
import json,re,hashlib,shutil,difflib
R=Path(__file__).resolve().parents[2];S=R/'source_i_iv';B=S/'book_revision_before';L=R/'editorial/book_revision/iii_iv_edit_log.json';log=json.loads(L.read_text());IV='IV/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/'
def edit(rel,pairs):
 p=S/rel;b=p.read_text();a=b;ed=[]
 for old,new in pairs:
  n=a.count(old)
  if not n: raise ValueError((rel,old))
  a=a.replace(old,new);ed.append({'old':old,'new':new,'count':n})
 q=B/rel;q.parent.mkdir(parents=True,exist_ok=True)
 if not q.exists():shutil.copy2(p,q)
 p.write_text(a);log['changes'].append({'file':rel,'before_sha256':hashlib.sha256(b.encode()).hexdigest(),'after_sha256':hashlib.sha256(a.encode()).hexdigest(),'edits':ed})
edit('III/manuscript/chapters/02_connections_obstructions.tex',[
 ('the version 1.0.1 contract','the finite algebraic contract'),('the version 1.0.1 completion contract','the finite algebraic completion contract'),('Formalization ledger for version 1.0.1','Finite algebraic formalization ledger'),('This edition does not derive a connection from','The theory does not derive a connection from')])
for rel in ['III/manuscript/visual_atlas.tex','III/guides/visual/source/pages_final.tex']:
 edit(rel,[('The edition used here','Scope of the worked models')])
edit('III/guides/visual/Paper_III_Visual_Guide_Final.tex',[('in the monograph edition','in the main text')])
# Local typography in reviewed mathematical prose; no formulas, symbols, assumptions, or proof steps change.
for rel in ['III/manuscript/chapters/03_nonlinear_coordinates.tex','III/manuscript/chapters/04_correction_transport.tex']:
 pairs=[('Moore Penrose','Moore--Penrose'),('Lyapunov Schmidt','Lyapunov--Schmidt'),('fixed point equations','fixed-point equations'),('first order','first-order')]
 if '03_' in rel:pairs.extend([('higher order','higher-order'),('second order','second-order'),('operator valued maps','operator-valued maps')])
 edit(rel,pairs)
L.write_text(json.dumps(log,indent=2))
files=sorted(set(x['file'] for x in log['changes']));pat=re.compile(r'(?s)(?<!\\)\$\$.*?(?<!\\)\$\$|(?<!\\)\$[^$]*?(?<!\\)\$|(?<!\\)\\\[.*?(?<!\\)\\\]|(?<!\\)\\\(.*?(?<!\\)\\\)|\\begin\{(equation\*?|align\*?|alignat\*?|gather\*?|multline\*?|displaymath|math)\}.*?\\end\{\1\}')
comparison=[];diff=[]
for rel in files:
 p=S/rel;q=B/rel
 if not q.exists():continue
 old=q.read_text();new=p.read_text();m0=[m.group() for m in pat.finditer(old)];m1=[m.group() for m in pat.finditer(new)]
 removed=[x for x in m0 if x not in m1];added=[x for x in m1 if x not in m0]
 decorative=(rel=='III/docs/Paper_III_Section17_Analytic_Closeout.tex' and removed==['$\\cdot$'] and added==[])
 vpat=r'(?s)\\begin\{(?:Verbatim|verbatim)\}.*?\\end\{(?:Verbatim|verbatim)\}'
 v0=re.findall(vpat,old);v1=re.findall(vpat,new);removed_v=[v for v in v0 if v not in v1];added_v=[v for v in v1 if v not in v0]
 listing_ok=(v0==v1 or (rel.endswith('08_replay.tex') and len(removed_v)==2 and not added_v and all('build.py' in v for v in removed_v)))
 labels0=re.findall(r'\\(?:label|hypertarget)\{([^}]+)\}',old);labels1=re.findall(r'\\(?:label|hypertarget)\{([^}]+)\}',new)
 excerpts0=re.findall(r'\\excerpt\{[^}]+\}\{[^}]+\}',old);excerpts1=re.findall(r'\\excerpt\{[^}]+\}\{[^}]+\}',new)
 rec={'file':rel,'source_sha256_before':hashlib.sha256(q.read_bytes()).hexdigest(),'source_sha256_after':hashlib.sha256(p.read_bytes()).hexdigest(),'math_regions_before':len(m0),'math_regions_after':len(m1),'math_regions_identical':m0==m1,'exception':'Removed decorative centered-dot separator from dated title metadata' if decorative else None,'mathematical_content_unchanged':m0==m1 or decorative,'labels_and_target_ids_identical':labels0==labels1,'literal_listing_validation_pass':listing_ok,'removed_document_build_listings':len(removed_v),'exact_source_excerpt_calls_identical':excerpts0==excerpts1}
 comparison.append(rec)
 diff.extend(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='before/'+rel,tofile=rel,n=2))
 if not rec['mathematical_content_unchanged']:print('UNEXPECTED MATH DIFFERENCE',rel,removed[:2],added[:2])
 if not listing_ok:print('UNEXPECTED LISTING DIFFERENCE',rel)
(R/'editorial/book_revision/iii_iv_math_preservation.json').write_text(json.dumps(comparison,indent=2))
(R/'editorial/book_revision/iii_iv_source.diff').write_text(''.join(diff))
print('Files',len(files),'existing',len(comparison),'Math preservation PASS',all(x['mathematical_content_unchanged'] for x in comparison),'listing preservation PASS',all(x['literal_listing_validation_pass'] for x in comparison),'IDs PASS',all(x['labels_and_target_ids_identical'] for x in comparison),'Excerpt calls PASS',all(x['exact_source_excerpt_calls_identical'] for x in comparison))
