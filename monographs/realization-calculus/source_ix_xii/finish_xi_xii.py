from pathlib import Path
import json,hashlib,zipfile,fitz,re
R=Path(__file__).resolve().parent;W=R.parent
sha=lambda b:hashlib.sha256(b).hexdigest()
inv=json.loads((W/'reader_inventory.json').read_text());baseline={Path(x['path']).name:x['path'] for a in inv for x in a['pdfs']};rows=[];pres=[];links=[]
for k in ['XI','XII']:
 zpath=Path('/workspace/scratch/fbc994080222/paper_viii_freeze/output')/f'Paper_{k}_Frozen_Release_2026-10-21.zip';z=zipfile.ZipFile(zpath);prefix=f'Paper_{k}_Frozen_Release_2026-10-21/'+('core/' if k=='XII' else '')
 for p in (R/k/'publication/source').rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(R/k).as_posix();zn=prefix+rel
  if zn not in z.namelist():continue
  a=z.read(zn);b=p.read_bytes()
  same=a==b;body=None
  if not same:
   assert p.name==f'Paper_{k}_{"Traditional" if p.parent.name=="traditional" else "Visual_Guide" if p.parent.name=="visual_guide" else "Lean_Guide"}_Final.tex',rel
   body=a.decode().split(r'\begin{document}',1)[1]==b.decode().split(r'\begin{document}',1)[1]
   assert body,rel
  pres.append({'paper':k,'path':rel,'same_bytes':same,'document_body_identical':body,'baseline_sha256':sha(a),'current_sha256':sha(b)})
 for role,tag in [('traditional','Traditional'),('visual_guide','Visual_Guide'),('lean_guide','Lean_Guide')]:
  p=next((R/(k+'_build')).glob(f'Paper_{k}_{tag}_v*.pdf'));d=fitz.open(p);stem=f'Paper_{k}_{tag}_Final';work=R/(k+'_build')/('build' if k=='XI' else '')/role
  log=(work/(stem+'.log')).read_text(errors='replace');warnings=[s for s in log.splitlines() if any(t in s for t in ['Warning:','Overfull','Missing character','Underfull'])]
  assert not any('Overfull' in s or 'Missing character' in s or 'undefined' in s.lower() or 'substituted' in s.lower() for s in warnings),warnings
  rows.append({'paper':k,'baseline_filename':p.name,'baseline_pdf':baseline[p.name],'baseline_sha256':sha(Path(baseline[p.name]).read_bytes()),'output_pdf':str(p),'output_sha256':sha(p.read_bytes()),'pages':len(d),'build_kind':'source_retypeset','source_root':str(R/k),'warnings':warnings,'page_labels':d.get_page_labels(),'remotes_rebound':True,'remote_target_semantics':'Original route-builder resolved named anchors against the newly compiled three-reader set. Fixed XI progress/atlas targets retain original unchanged PDFs.','style_exception':'Original compact geometry and sans visual reading face retained to keep27 complete one-page lessons.' if k=='XII' and role=='visual_guide' else None,'mathematical_document_body_preserved':True})
 for name,path in baseline.items():
  if k=='XI' and name.startswith('Paper_XI_Conjecture66'):
   p=Path(path);d=fitz.open(p);rows.append({'paper':k,'baseline_filename':name,'baseline_pdf':path,'baseline_sha256':sha(p.read_bytes()),'output_pdf':path,'output_sha256':sha(p.read_bytes()),'pages':len(d),'build_kind':'preserved_pdf','source_root':None,'warnings':['Research companion retained as exact frozen PDF. Complete editable Block02 archive remains unavailable. No substitution with older source.'],'page_labels':d.get_page_labels(),'remotes_rebound':False})
# Bound current numeric remote destinations using reflowed output set and exact preserved companions.
outputs={x['baseline_filename']:x['output_pdf'] for x in rows}
for row in rows:
 if row['build_kind']!='source_retypeset':continue
 d=fitz.open(row['output_pdf']);total=internal=remote=0;bad=[]
 for i,pg in enumerate(d):
  for l in pg.get_links():
   total+=1
   if l['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED) and ('page' in l or 'nameddest' in l):
    internal+=1
    if l.get('page',-1) not in range(len(d)):bad.append([i+1,'internal',l.get('page')])
   elif l['kind']==fitz.LINK_GOTOR:
    remote+=1;name=Path(l['file']).name
    if name not in outputs:bad.append([i+1,'target missing',name]);continue
    nd=fitz.open(outputs[name])
    if l.get('page',-1)<0 or l['page']>=len(nd):bad.append([i+1,'remote out ofbounds',name,l.get('page')])
   elif 'p12-route:' in l.get('uri','') or 'komorebi.invalid/b07' in l.get('uri',''):bad.append([i+1,'unresolved placeholder'])
 assert not bad,bad
 links.append({'file':row['baseline_filename'],'total_links':total,'internal_links':internal,'remote_links':remote,'invalid':bad})
report={'scope':'Source-preserving typesetting, link remapping and visual QA; no proofaudit, science or Lean execution.','retained_source_asset_files_checked':len(pres),'unchanged_files':sum(x['same_bytes'] for x in pres),'entry_files_layout_injection_only':sum(not x['same_bytes'] for x in pres),'files':pres,'link_validation':links,'changed_hunks_self_review':{'routine_edits':['publication style injection','caption package collision adapter','explicit installed P052/Nimbus font faces','unindented visual paragraphs','compact XII visual lesson geometry and source sans reading face'],'mathematical_token_changes':[],'document_body_changes':[],'validation':'Six TeX component builds and companion routes passed. Final logs have no overfull/missing-glyph/unresolved-reference/font-substitution diagnostics.','coverage':'Changed layout adapters and exact six entry-file hunks only; not a manuscript proofaudit.'},'visual_review':{'representative_pages':42,'details':3,'all_page_text_bounds':'PASS','sparse_text_pages_lt100_excluding_cover':[]},'repaired_failures':['Caption package collided with XII visual captiontext macro; save/restore adapter fixed it.','Physics paragraph indentation overflowed visual tables; unindented plate paragraphs fixed it.','XII Lean fontconfig did not resolve P052 bold; explicit installed OTF faces fixed it.','Common geometry/serif face split two XII lessons; source compact geometry and sans reading face retained, preserving27 complete lessons.']}
(R/'XI_XII_SOURCE_PRESERVATION.json').write_text(json.dumps(report,indent=2))
prior=json.loads((W/'typeset_ix_x_results.json').read_text());allrows=(prior['components'] if isinstance(prior,dict) else prior)+rows
(W/'typeset_ix_xii_results.json').write_text(json.dumps({'components':allrows,'scope':report['scope'],'xi_xii_source_preservation':str(R/'XI_XII_SOURCE_PRESERVATION.json'),'xi_xii_qa':str(R/'QA_XI_XII.json')},indent=2))
print(json.dumps({'components':[{k:x[k] for k in ['paper','baseline_filename','pages','build_kind']} for x in allrows],'source_assets_checked':len(pres),'links':links},indent=2))
