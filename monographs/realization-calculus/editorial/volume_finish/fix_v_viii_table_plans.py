from pathlib import Path
import json,zipfile,fitz,sys
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');D=R/'editorial/volume_finish';sys.path.insert(0,str(R))
from preserved_pdf_proofread import block_text,all_spans,prepare_region,prepare_table
S=json.loads((D/'baseline_build_spec.json').read_text());C={c['id']:c for p in S['parts'] for c in p['components']};Z=zipfile.ZipFile('/workspace/scratch/fbc994080222/komorebi_core_monograph_delivery/Realization_Calculus_Publication_Package.zip');DOC={}
def pg(cid,pn):
 if cid not in DOC:DOC[cid]=fitz.open(stream=Z.read('Realization_Calculus_Publication_Package/'+C[cid]['path']),filetype='pdf')
 return DOC[cid][pn-1]
def exact(cid,pn,old,new,reason):
 p=pg(cid,pn);hit=[l for b in p.get_text('dict')['blocks'] if b.get('type')==0 for l in b['lines'] if ''.join(s['text'] for s in l['spans'])==old];assert len(hit)==1,(cid,pn,old,len(hit));l=hit[0]
 prep=prepare_region(p,l['bbox'],new,l['spans'],[l],kind='line',allow_line_reflow=False)
 return {'component_id':cid,'source_page_1based':pn,'kind':'exact_lines','old':old,'new':new,'bbox':list(l['bbox']),'context':old,'reason':reason,'category':'publication_prose','native_fit_check':'PASS','native_scale':prep.get('scale',1)}
p=D/'v_viii_plan.json';J=json.loads(p.read_text());out=[]
for o in J['operations']:
 cid=o['component_id'];pn=o['source_page_1based'];old=o['old']
 if cid=='V_lean' and pn==3 and old.startswith('The September 6 UTC release'):
  o['kind']='replace_table_cells'
 elif cid=='VII_traditional' and pn==89 and old=='Milestone':
  o['kind']='replace_table_cells'
 elif cid=='VIII_lean' and pn==42 and old=='are outside this release.':
  o['kind']='replace_table_cells'
 elif cid=='VI_traditional' and pn==47 and old=='The inherited fourth block proves':
  out.append(exact(cid,pn,'The inherited fourth block proves the scalar beta normalization, the','The formalization proves the scalar beta normalization, the','Run-in bold heading is not a table. Edit its adjacent pure-prose physical line only, preserving the heading and all remaining analytical prose.'));continue
 elif cid=='VI_traditional' and pn==47 and old.startswith('Verification and numerical evidence.'):
  replacements=[
   ('The September 6 release records that the full pinned build,','The saved records report the full pinned build,'),
   ('project-wide axiom audit, all 54 companion tests and six verifier controls passed. No fresh Lean build','project-wide axiom audit, all 54 companion tests and six verifier controls passed.'),
   ('is asserted for this October edition. The 54 tests comprise the original 37 and 17 added boundary and','The 54 tests comprise the original 37 tests and 17 boundary and validation cases.'),
   ('validation cases. The 19 numerical figure pairs are unchanged. The earlier 79-field numerical compari-','The numerical records identify the 19 figure pairs and the separate 79-field comparison.'),
   ('son remains historical evidence, not a rerun in that September 6 block. The September 12 visual release','The numerical comparison and the visual replay have separate execution records.'),
   ('subsequently records a numerical replay. Current October checks are reported separately in the final','Source contracts, exact theorem targets, full logs and checked ledgers accompany the source files.'),
   ('package. Machine-readable source contracts, exact theorem targets, full logs and previous checked','Numerical tests are finite regressions. They are not substitutes for the Lean proofs.'),
   ('ledgers accompany the source archive. Numerical tests are finite regressions and are not substitutes',''),
   ('for the Lean proofs.','')]
  out.extend(exact(cid,pn,a,z,'Preserve the run-in bold heading and native physical prose lines. Remove production dates and edition history without altering counts, evidence distinctions or any mathematical statement.') for a,z in replacements);continue
 out.append(o)
# Preserve the left evidence-table cell as well as its right descriptive cell.
b=next(b for b in pg('V_lean',3).get_text('dict')['blocks'] if b.get('type')==0 and 'Historical Lean execution' in block_text(b))
out.append({'component_id':'V_lean','source_page_1based':3,'kind':'replace_table_cells','old':'Historical Lean execution','new':'Recorded Lean execution','bbox':list(b['bbox']),'context':block_text(b),'reason':'Final-volume evidence-table label; preserve the two-column geometry.','category':'publication_prose'})
# A scoped line edit in a different table row than the 5.5 cell edit above.
out.append(exact('VIII_lean',42,'Local error inequalities are supplied to exact normed-','Local error inequalities are supplied to exact normed','Remove the line-final hyphen so the unchanged following line begins ring propagation. This preserves the supplied-input boundary and yields normed ring rather than the concatenated normedring. The region is disjoint from row5.5’s table-cell edit.'))
J['operations']=out;J['status']='FROZEN_FOR_ROOT_APPLICATION';J['table_layout_review']={'true_tables':['V_lean3','VII_traditional89','VIII_lean42'],'false_positive_run_in_headings':['VI_traditional47 fractional results','VI_traditional47 verification and numerical evidence'],'preservation':'True tables use bounded cell edits. Both run-in prose paragraphs now use exact physical lines, preserving bold headings. VIII42 normed ring has a separate disjoint physical-line correction.','baseline':'Immutable preceding ZIP, not current compiled files.'};p.write_text(json.dumps(J,indent=2,ensure_ascii=False)+'\n')
# Keep the bibliography key and author/title positions at IV52 unchanged.
p=D/'bibliography_prose_plan.json';B=json.loads(p.read_text());ops=[]
for o in B['operations']:
 if o['component_id']=='IV_traditional' and o['source_page_1based']==52 and '[P.26c]' in o['old']:
  ops.append(exact('IV_traditional',52,'obstruction packets, 2026. Version 1.0.1.','obstruction packets. Chapter III of this volume.','Preserve the complete [P.26c] citation key and its hanging author/title layout. Replace only the second pure-prose physical line containing the internal release date/version.'));continue
 ops.append(o)
B['operations']=ops;B['status']='FROZEN_FOR_ROOT_APPLICATION';B['table_layout_review']='IV52[P.26c] is one hanging bibliography entry, not a merged table. Its key and first author/title line stay exactly in place; only the second pure-prose physical line changes.';p.write_text(json.dumps(B,indent=2,ensure_ascii=False)+'\n')
# Validate native cells from their immutable baseline.
checks=[]
for cid,pn in [('V_lean',3),('VII_traditional',89),('VIII_lean',42)]:
 pp=pg(cid,pn);OO=[o for o in J['operations'] if o['component_id']==cid and o['source_page_1based']==pn and o['kind']=='replace_table_cells']
 for b in pp.get_text('dict')['blocks']:
  if b.get('type')!=0:continue
  these=[o for o in OO if o['old'] in block_text(b)]
  if these:
   prepared=prepare_table(pp,b,[(o['old'],o['new']) for o in these]);checks.append({'component_id':cid,'page':pn,'bounded_cells':len(prepared),'status':'PASS'})
(D/'v_viii_table_layout_review.json').write_text(json.dumps({'status':'PASS','native_cell_checks':checks,'physical_line_checks':'All exact line edits fit at native sizes; no PDF writes performed.','immutable_baseline_used':True},indent=2)+'\n')
print(json.dumps({'v_viii_operations':len(J['operations']),'bibliography_operations':len(B['operations']),'cell_checks':checks},indent=2))
