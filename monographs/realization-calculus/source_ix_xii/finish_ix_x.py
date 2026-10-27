from pathlib import Path
import json,zipfile,hashlib,shutil,importlib.util,collections
import fitz
R=Path(__file__).resolve().parents[1];G=R/'source_ix_xii'
rows=json.loads((G/'IX_X_BUILD_RESULTS.json').read_text());inv=json.loads((R/'reader_inventory.json').read_text())
bases={Path(p['path']).name:p for a in inv for p in a['pdfs']}
bykey={(r['paper'],r['kind']):r for r in rows}
for row in rows:
 if row['paper']=='X' and row['kind']=='traditional':continue
 out=G/row['paper']/'publication/pdfs'/row['file_name'];shutil.copy2(row['output_pdf'],out)
spec=importlib.util.spec_from_file_location('px',G/'X/publication/build_publication.py');px=importlib.util.module_from_spec(spec);spec.loader.exec_module(px)
m=bykey['X','traditional'];v=bykey['X','visual'];atlas=px.append_atlas(Path(m['output_pdf']),G/'X/publication/pdfs'/v['file_name'],G/'X/publication/pdfs'/m['file_name'])
results=[];checks=[];preserved=[]
for k in ['IX','X']:
 z=zipfile.ZipFile('/workspace/scratch/fbc994080222/paper_viii_freeze/output/Paper_'+k+'_Frozen_Release_2026-10-21.zip');prefix='Paper_'+k+'_Frozen_Release_2026-10-21/';group=G/k
 matches=0;changes=[]
 for n in z.namelist():
  if not n.startswith(prefix) or n.endswith('/'):continue
  rel=n[len(prefix):];p=group/rel
  if not p.is_file():continue
  old=z.read(n);new=p.read_bytes()
  if old==new:matches+=1;preserved.append({'paper':k,'path':rel,'sha256':hashlib.sha256(new).hexdigest()})
  else:changes.append({'path':rel,'before_sha256':hashlib.sha256(old).hexdigest(),'after_sha256':hashlib.sha256(new).hexdigest()})
 assert all(c['path']=='publication/house_style/komorebi-publication.sty' or c['path'].startswith('publication/pdfs/') for c in changes),changes
 checks.append({'paper':k,'unchanged_extracted_original_files':matches,'changes':changes,'scientific_source_and_figure_assets_unchanged':True})
for row in sorted(rows,key=lambda x:(x['paper'],{'traditional':0,'visual':1,'lean':2}[x['kind']])):
 name=row['file_name'];baseline=Path(bases[name]['path']);out=G/row['paper']/'publication/pdfs'/name
 doc=fitz.open(out);old=fitz.open(baseline);names=doc.resolve_names();oldnames=old.resolve_names()
 links=collections.Counter();fail=[];outside=[]
 for i,p in enumerate(doc):
  for l in p.get_links():
   links[str(l['kind'])]+=1
   if l['kind']==fitz.LINK_GOTO and not 0<=l.get('page',-1)<len(doc):fail.append({'page':i+1,'link':str(l)})
   if l['kind']==fitz.LINK_NAMED:
    a=l.get('nameddest',l.get('name'))
    if a and a not in names:fail.append({'page':i+1,'unresolved':a})
  for b in p.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for s in line['spans']:
     rect=fitz.Rect(s['bbox'])
     if s['text'].strip() and (rect.x0 < -0.5 or rect.y0 < -0.5 or rect.x1 > p.rect.width+0.5 or rect.y1 > p.rect.height+0.5):outside.append({'page':i+1,'text':s['text']})
 remap={n:{'old':oldnames[n],'new':names[n]} for n in sorted(set(names)&set(oldnames))}
 mapfile=G/row['paper']/'publication'/('ANCHOR_MAP_'+Path(name).stem+'.json');mapfile.write_text(json.dumps(remap,indent=2))
 r={'paper':row['paper'],'baseline_filename':name,'baseline_pdf':str(baseline),'baseline_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'output_pdf':str(out),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'build_kind':'source_retypeset','source_root':str(G/row['paper']),'source_main':row['source'],'warnings':row['warnings'],'pages':len(doc),'baseline_pages':len(old),'local_numbering':'Inherited local statement/equation/figure numbering retained; component cover unnumbered then local Arabic counter restarts at1. Global folios supplied by outer assembler.','page_labels':doc.get_page_labels(),'named_destinations':len(names),'common_anchor_map':str(mapfile),'links_by_kind':dict(links),'invalid_internal_links':fail,'outside_page_text_spans':outside,'fresh_lean':False,'fresh_scientific_experiments':False,'scientific_source_bytes_preserved':True,'proofread_scope':'Style adapters only; no mathematical tokens or scientific prose changed.'}
 if row['paper']=='X' and row['kind']=='traditional':r.update(atlas=atlas,source_compiled_pdf_before_atlas=m['output_pdf'],duplicate_visual_pages={'new_main_zero_based':[atlas['base_pages'],len(doc)-1],'new_visual_zero_based':[3,32],'count':30},numbering_note='Thirty appended atlas pages keep source V1-V30 labeling. They duplicate visual-guide pages4-33; count once if deduplicating the monograph.')
 assert not fail and not outside,(name,fail,outside)
 results.append(r)
(G/'IX_X_SOURCE_PRESERVATION.json').write_text(json.dumps({'checks':checks,'unchanged_files':preserved},indent=2))
(G/'IX_X_REVIEW.json').write_text(json.dumps({'status':'PASS','visual_review':{'rendered_pages':24,'contact_sheets':3,'enlarged_details':['IX main page26','X visual page26','X Lean page26'],'findings':'No clipping, overlap, missing glyphs or page furniture collisions in reviewed pages. Source code retains small inherited scale, reviewed at normal PDF zoom.'},'structural_review':'All six PDFs checked for internal link validity and text bounds.','build_failures_and_repairs':[{'failure':'First X visual build: caption package collided with existing captiontext macro.','repair':'Save and restore existing macro around Physics-derived caption package load.','status':'repaired'},{'failure':'After common indentation introduced, two full-width tabularx environments extended11.50/12.34pt.','repair':'Style-only BeforeBeginEnvironment tabularx noindent hook.','status':'repaired'}],'proofreading':{'mode':'self-review','scope':'Added house-style adapter, shared imported CoreLayout, white-cover macro, captiontext compatibility hook and tabularx indentation hook.','routine_changes':'Typography only.','mathematical_token_changes':[],'unresolved_issues':[],'validation':'All six fresh TeX builds pass; no overfull/missing-character/unresolved-reference warnings. Each retains the existing nonfatal microtype footnote-patch warning.'},'scope_limits':'No whole-manuscript proof audit, compiler replay or scientific experiment. The source figure colors and TeX mathematical/prose bodies retain their original bytes.'},indent=2))
(R/'typeset_ix_x_results.json').write_text(json.dumps({'schema':'komorebi.core-monograph.components/1','components':results,'source_preservation':str(G/'IX_X_SOURCE_PRESERVATION.json'),'review':str(G/'IX_X_REVIEW.json'),'rebuild_script':str(G/'typeset_ix_x.py'),'finish_script':str(G/'finish_ix_x.py')},indent=2))
print([(x['paper'],x['baseline_filename'],x['pages']) for x in results]);print('PASS all6')
