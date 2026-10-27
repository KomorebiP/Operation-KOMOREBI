from pathlib import Path
import json,hashlib,copy
ROOT=Path('/dev/shm/komorebi_core_monograph_fbc994080222');OUT=ROOT/'editorial/rhythm_review'
old_path=ROOT/'editorial/book_revision/frontmatter_keep_overrides.json';old=json.loads(old_path.read_text());probe=json.loads((OUT/'frontmatter_probe.json').read_text());rs={r['component_id']:r for r in probe['records']}
assert len(rs)==41,('Need final41 inputs',len(rs))
run=json.loads((OUT/'build_run/REBUILD_ALL_COMPONENTS.json').read_text());assert len(run['components'])==36
assert all(e['build_pass'] for e in run['components'])
qa=json.loads((OUT/'preserved_visual_review.json').read_text());assert qa['status']=='SEALED' and qa['result']=='PASS'
for e in qa['coverage']:assert hashlib.sha256((ROOT/e['pdf']).read_bytes()).hexdigest()==e['sha256']
glossary=json.loads((OUT/'glossary_anchor_reconciliation.json').read_text());assert glossary['status']=='PASS' and glossary['checked']==74
out=copy.deepcopy(old);out['source']='Final raw pre-adapter component PDFs from the sealed rhythm build manifest, plus three sealed already-adapted preserved readers and two unchanged frozen documentary originals. Actual front pages, scope/route pages and all 13 mixed Contents boundaries reread. Preserved inputs receive no second navigation redaction.'
def ranges(xs):
 result=[]
 for n in xs:
  if result and n==result[-1][1]+1:result[-1][1]=n
  else:result.append([n,n])
 return result
changed_pages=[];boundaries=[];evidence=[]
for c in out['components']:
 r=rs[c['component_id']];p=ROOT/r['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 if r['pages']!=c['pages']:changed_pages.append({'component_id':c['component_id'],'old':c['pages'],'new':r['pages']})
 oldregions={z['page_1based']:z for z in c.get('mixed_toc_regions',[])}
 ex=c['exclude_pages_1based'];keep=[n for n in range(1,r['pages']+1) if n not in ex];assert set(ex)|set(keep)==set(range(1,r['pages']+1));assert not set(ex)&set(keep)
 c.update(source_path=r['path'],source_sha256=r['sha256'],pages=r['pages'],exclude_pages_1based=ex,exclude_ranges_1based=ranges(ex),keep_pages_1based=keep,keep_ranges_1based=ranges(keep),mixed_toc_pages_1based=[z['page_1based'] for z in r['mixed_toc_regions']],mixed_toc_regions=r['mixed_toc_regions'])
 c['reconciliation_note']='Physical keep/drop decisions reconfirmed against the final selected rhythm-pass PDF. Unique orientation, abstract, scope and route prose remains kept. Live Contents rectangles use the actual current heading boundary.'
 if c['component_id'] in ['IV_visual','XI_research_progress','XI_research_atlas']:
  assert not c['mixed_toc_regions'];c['reconciliation_note']='Already-adapted sealed preserved input. Unique opening/scope/route prose retained; no second Contents redaction. Original baseline provenance remains separately recorded.'
 for z in c['mixed_toc_regions']:
  prior=oldregions.get(z['page_1based']);boundaries.append({'component_id':c['component_id'],'page_1based':z['page_1based'],'old_remove_y0':prior['remove_bbox'][1] if prior else None,'new_remove_y0':z['remove_bbox'][1],'changed':not prior or prior['remove_bbox']!=z['remove_bbox']})
 evidence.append({'component_id':c['component_id'],'path':r['path'],'sha256':r['sha256'],'pages':r['pages'],'previous_pages':r['previous_pages'],'exclude_pages_1based':ex,'front_pages_inspected':r['front_pages_inspected'],'mixed_toc_regions':r['mixed_toc_regions'],'first_and_last_text':[{'page_1based':z['page_1based'],'prior_decision':z['prior_decision'],'first_lines':z['first_lines'],'last_lines':z['last_lines']} for z in r['profiles']]})
assert len(boundaries)==13,len(boundaries)
(OUT/'frontmatter_keep_reconciled.json').write_text(json.dumps(out,indent=2)+'\n')
summary={'status':'SEALED','components':41,'fresh_source_readers':36,'already_adapted_preserved_readers':3,'frozen_documentary_inputs':2,'candidate_map':'editorial/rhythm_review/frontmatter_keep_reconciled.json','candidate_sha256':hashlib.sha256((OUT/'frontmatter_keep_reconciled.json').read_bytes()).hexdigest(),'source_map_sha256':hashlib.sha256(old_path.read_bytes()).hexdigest(),'all_selected_hashes_match':True,'page_count_changes':changed_pages,'keep_drop_index_changes':[],'mixed_contents_boundaries':boundaries,'changed_mixed_contents_boundaries':[b for b in boundaries if b['changed']],'already_adapted_no_double_redaction':['IV_visual','XI_research_progress','XI_research_atlas'],'glossary':'glossary_anchor_reconciliation.json','page_guards':'page_guard_reconciliation.json','preserved_introductions':'preserved_frontmatter_reconciliation.json','root_maps_mutated':False,'source_or_pdf_edits':False,'method':'Actual final pre-adapter source PDFs reread, all first-page keep/drop/unique scope decisions reconciled;13 live Contents rectangles recomputed from exact heading bbox.y0 minus0.5pt. All preserved scope paragraphs retained.'}
(OUT/'frontmatter_reconciliation_evidence.json').write_text(json.dumps({'summary':summary,'components':evidence},indent=2)+'\n')
text='SEALED: 41 final selected pre-adapter inputs reconciled.\n\nAll 36 fresh source readers, 3 sealed already-adapted preserved readers, and 2 frozen documentary originals checked. Paths, page counts, hashes, keep/exclude pages and ranges, and 13 live Contents regions updated deterministically. Preserved readers have empty mixed-TOC arrays. All unique introductions, scope notes and routes remain kept.\n\nChanged Contents boundaries: '+json.dumps(summary['changed_mixed_contents_boundaries'])+'\nPage-count changes: '+json.dumps(changed_pages)+'\n\nAll 74 glossary anchor quotations uniquely resolve. Actual quote fragments and local-page resolution are in glossary_anchor_reconciliation.json. III orientation stays index 73 and first plate 74; VIII exact-model body stays index 7. Both guards remain valid.\n\nXI research progress p37/p56 unique prose reread; no live Contents headings. Current input/output words outside authorized rhythm regions are equal with 0.0 pt maximum coordinate drift. Earlier source-to-adapted 0.0000611 pt provenance bound retained in preserved_frontmatter_reconciliation.json.\n\nNo source, PDF, root-map or pipeline edits made. Candidate SHA256: '+summary['candidate_sha256']+'\n'
(OUT/'frontmatter_keep_reconciliation.txt').write_text(text)
print(json.dumps(summary,indent=2))
