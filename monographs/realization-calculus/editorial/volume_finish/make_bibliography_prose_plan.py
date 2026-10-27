from pathlib import Path
import json,fitz,sys
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');sys.path.insert(0,str(R))
from preserved_pdf_proofread import prepare_region,all_spans,block_text,ismath
D=R/'editorial/volume_finish';S=json.loads((D/'baseline_build_spec.json').read_text());C={c['id']:c for p in S['parts'] for c in p['components']};REF=json.loads((D/'reference_plan.json').read_text());docs={};ops=[]
def block(cid,pn,anchor,new,category='internal_volume_citation',reason='Replace an internal release citation with the corresponding chapter in this volume while preserving its citation key.'):
 if cid not in docs:docs[cid]=fitz.open(R/C[cid]['path'])
 p=docs[cid][pn-1];hits=[b for b in p.get_text('dict')['blocks'] if b.get('type')==0 and anchor in block_text(b)]
 assert len(hits)==1,(cid,pn,anchor,len(hits))
 b=hits[0];old=block_text(b)
 if callable(new):new=new(old)
 assert not any(ismath(s) for s in all_spans(b)),(cid,pn,'Mathematical font present')
 prep=prepare_region(p,b['bbox'],new,all_spans(b),b['lines'])
 ops.append({'component_id':cid,'source_page_1based':pn,'kind':'replace_block','old':old,'new':new,'bbox':list(b['bbox']),'context':old,'category':category,'reason':reason,'native_fit_check':'PASS','native_scale':prep['scale']})
block('III_traditional',99,'[13] Komorebi P.','[13] Komorebi P. Projector-Resolved Seed Calculus I: Typed seeds, operator grammars, and exact reconstruction. Chapter I of this volume.')
block('III_traditional',99,'[14] Komorebi P.','[14] Komorebi P. Projector-Resolved Seed Calculus II: Polyphase refinement, weighted transfer, and dyadic–odd resolution. Chapter II of this volume.')
block('IV_traditional',52,'[P.26a]','[P.26a] Komorebi P. Projector-Resolved Seed Calculus I: Typed seeds, operator grammars, and exact reconstruction. Chapter I of this volume.')
block('IV_traditional',52,'[P.26b]','[P.26b] Komorebi P. Projector-Resolved Seed Calculus II: Polyphase refinement, weighted transfer, and dyadic–odd resolution. Chapter II of this volume.')
block('IV_traditional',52,'[P.26c]','[P.26c] Komorebi P. Projector-Resolved Seed Calculus III: Typed edge operators, connection defects, and obstruction packets. Chapter III of this volume.')
block('IX_traditional',238,'[5] Komorebi P.','[5] Komorebi P. Euler Congruences. Chapter IX and its formal companion in this volume. The accompanying source collection preserves the manuscript, formal supplements and continuation records.')
block('XI_research_progress',34,'[1] Komorebi P.','[1] Komorebi P. Tame and Wild Packet Geometry. Chapter XI of this volume, Sections 16 and 19 and construction appendices.')
block('XI_research_progress',34,'[2] Komorebi P.','[2] Komorebi P. Formal companion to Chapter XI of this volume, Chapters 1, 13–14 and source catalogue.')
block('XI_research_progress',34,'[11] Proof166.','[11] Proof166. Direct trace-zero realization in arbitrary odd-prime length. Ordinary proof synthesis.',category='internal_source_record',reason='Retain the stable Proof166 source identity and ordinary-proof classification while removing the source-production date.')
block('XI_research_progress',35,'[15] Proof167.','[15] Proof167. Weighted dyadic realization and low-rank enlargement.',category='internal_source_record',reason='Retain stable Proof167 source identity and mathematical subject without final-stage production wording.')
block('XI_research_progress',54,'Actual Monomial Local Global, v0.45.0.','M45\nActual Monomial Local Global. Lean source, source-lineage and claim-classification notes, a preliminary preservation record and two incomplete build logs. The terminal successful receipt was not recovered.',category='internal_source_record',reason='Keep stable source ID M45 and every evidence limitation. Remove the redundant v0.45.0 release label and production adjective, without implying a completed build.')
# The remaining four edits concern production commentary appended to genuine
# external source identities. All source titles, publication metadata, arXiv IDs,
# exact dependency pins and relevant result locators remain untouched.
block('IX_traditional',238,'[1] Yuta Nishibuchi,',lambda old:old.split('The comparison to')[0].rstrip()+' Comparison: Conjecture 3.9.',category='external_citation_prose_only',reason='Preserve external author/title/arXiv:2605.10677v2/date/URL and Conjecture3.9 locator. Remove the book-production sentence about a fixed-version review record.')
block('IX_traditional',238,'[2] Ira M. Gessel,',lambda old:old.split('The normalization and quantifiers')[0].rstrip(),category='external_citation_prose_only',reason='Preserve all external source identity and Section9/Theorem9.2 locators. Remove only the strengthening-checkpoint production sentence.')
block('IX_traditional',238,'[3] NIST Digital Library',lambda old:old.split('The official primary entry')[0].rstrip()+' Used for the positive even-index denominator specialization.',category='external_citation_prose_only',reason='Preserve exact DLMF section/equation/URL and the named specialization. Remove edition-dependent source-review commentary.')
block('IX_traditional',238,'[4] The Mathlib Community,',lambda old:old.replace('accompany the release.','accompany the source files.'),category='external_citation_prose_only',reason='Preserve genuine external Mathlib revision, Lean compiler version and Section11 source correspondence. Replace only the project-release reference.')
block('IX_traditional',238,'Recovered historical references.','References for Appendix D. These sources support Appendix D’s citations. Its mathematical hypotheses and formal coverage remain as stated there.',category='bibliography_transition',reason='Replace recovery and repair history with a final-volume source heading, preserving the stated mathematical and formal scope boundary.')
# Remove a historical adjective from the source-register note while retaining
# its explicit warning against reading source titles as completion claims.
block('XI_research_progress',54,'The machine-readable source map gives','The machine-readable source map gives package-relative paths, SHA-256 hashes and selected locators. The short labels below identify the sources cited in the text. A source title containing “completion” does not override its actual hypotheses or verification status.',category='source_register_introduction',reason='Keep stable source-map semantics and the actual-hypothesis boundary, with final-volume prose rather than a historical-stage description.')
review=[]
for g in REF['bibliography_groups']:
 these=[o for o in ops if o['component_id']==g['component_id'] and o['source_page_1based'] in g['pages_1based']]
 review.append({'group_id':g['id'],'component_id':g['component_id'],'source_pages_1based':g['pages_1based'],'checked':'All group text and relevant actual PDF blocks','operations':len(these),'external_metadata':'Preserved exactly, including scholarly editions, publication years, arXiv identifiers/version suffixes and technical dependency identities.','stable_citation_keys':'Preserved exactly.'})
result={'schema':'volume-finish.bibliography-prose/1','status':'FROZEN_FOR_ROOT_APPLICATION','scope':'All15 bibliography/source-register groups in reference_plan.json, checked against current compiled PDF blocks. No source or PDF mutations.','operations':ops,'whole_page_exclusions':[],'reviewed_groups':review,'mathematical_token_changes':[],'validation':{'native_prose_fit':'PASS for all17operations','all_native_scale_one':all(o['native_scale']==1 for o in ops),'scholarly_source_identity':'No external bibliographic data changed. Four edits remove or recast only book-production commentary after those identities.','stable_internal_ids':'Citation keys including [P.26a/b/c], Proof166, Proof167 and M45 retained. M45 still records two incomplete logs and the unrecovered terminal receipt.','edits_to_other_plans':'None'}}
(D/'bibliography_prose_plan.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'operations':len(ops),'groups':len(review),'fit_scale_counts':{str(z):sum(o['native_scale']==z for o in ops) for z in sorted(set(o['native_scale'] for o in ops))}},indent=2))
