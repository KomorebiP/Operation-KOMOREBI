from pathlib import Path
import json,fitz,re,collections
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222')
S=json.loads((R/'book/build_spec.json').read_text());C={c['id']:c for p in S['parts'] for c in p['components']}
D={};ops=[];ex=[]
def page(cid,pn):
 if cid not in D:D[cid]=fitz.open(R/C[cid]['path'])
 return D[cid][pn-1]
def blocks(cid,pn):return [b for b in page(cid,pn).get_text('blocks') if b[6]==0]
def block(cid,pn,anchor,new,reason='Replace production or edition framing with final-volume prose.'):
 hits=[b for b in blocks(cid,pn) if anchor in b[4]]
 if len(hits)!=1:raise ValueError((cid,pn,anchor,len(hits)))
 b=hits[0];ops.append({'component_id':cid,'source_page_1based':pn,'kind':'replace_block' if new else 'omit_block','old':b[4],'new':new,'bbox':list(b[:4]),'context':b[4],'reason':reason,'category':'publication_prose','recommended_source_root':f"source_v_viii/{cid.split('_')[0]}/editable/"+('traditional' if cid.endswith('traditional') else 'visual_guide' if cid.endswith('visual') else 'lean_guide')})
def phrase(cid,pn,old,new,reason='Remove a release or edition label while preserving the mathematical scope.'):
 hits=[b for b in blocks(cid,pn) if old in b[4]]
 if len(hits)!=1:raise ValueError((cid,pn,old,len(hits)))
 b=hits[0];ops.append({'component_id':cid,'source_page_1based':pn,'kind':'replace_phrase','old':old,'new':new,'bbox':list(b[:4]),'context':b[4],'reason':reason,'category':'publication_prose'})
def omitregion(cid,pn,y0,y1,reason):
 t=page(cid,pn).get_text(clip=fitz.Rect(0,y0,612,y1))
 ops.append({'component_id':cid,'source_page_1based':pn,'kind':'omit_region','old':t,'new':'','bbox':[59,y0,554,y1],'context':t,'reason':reason,'category':'source_package_only'})
def exclude(cid,pages,reason,math_review):
 ex.append({'component_id':cid,'source_pages_1based':pages,'action':'omit_from_reading_book_preserve_in_source_package','reason':reason,'mathematical_review':math_review})
# Chapter V. No mathematical alternative called a 'version' is changed.
phrase('V_traditional',40,'The September 2026 release records recovery and rerunning of the original companion source: its','The recorded companion run reports that its')
# The top of this page is a reproducibility record; the open mathematical boundary below remains.
omitregion('V_traditional',47,64,530,'D.5 consists solely of compiler pins, dependency identities, reproduction commands, TeX build details and a runtime adapter. Preserve it exactly in the source package.')
block('V_traditional',47,'The September 2026 finite theorem scope','All twenty scoped theorem-like statements have reviewed, accepted formal counterparts. The two edge-recovery conjectures remain open research directions. No universal segmentation theorem, infinite-tree consistency result, minimax rate, or optimal Smith sampling theorem is inferred from the finite results. Classical Smith-grid and transmission-line formulas provide application context. Those physical and historical assertions are not additional Lean-certified theorem rows.')
block('V_traditional',47,'Historical cross-paper declaration counts','The formal scope consists of the twenty Part I results. Supporting declarations, reused results and proofs in the broader written development have distinct roles.')
phrase('V_traditional',117,'The checker for the source release','The recorded checker')
phrase('V_visual',2,'monograph traditional edition','mathematical text')
phrase('V_lean',2,'The full traditional edition','The mathematical text')
phrase('V_lean',2,'This edition preserves','This guide preserves')
block('V_lean',3,'The selected release,','The formal contract covers twenty scoped theorem-like manuscript results with explicit proofs and 225 supporting theorem targets. The saved namespace audit reports 827 declarations. These are different denominators: 827 includes definitions and compiler-generated declarations, while 225 includes supporting results rather than 225 independent new mathematical claims.')
phrase('V_lean',3,'final traditional edition','mathematical text')
phrase('V_lean',3,'Evidence available in this edition','Verification evidence')
# Table entry only, not the rest of the evidence table.
phrase('V_lean',3,'The September 6 UTC release records the pinned build and namespace','The saved compiler record reports the pinned build and namespace')
block('V_lean',28,'8.2 The two dates of evidence','8.2 Recorded verification')
block('V_lean',28,"The release’s raw kernel verification timestamp",'The saved compiler transcript identifies the checked sources and their pinned dependencies. The accompanying reports distinguish that kernel execution from the source checks and finite computations described here.')
exclude('V_lean',[29,30],'Reproduction logs, recovery gaps, build commands, runtime-adapter details and guide-build instructions belong with exact source records.','No theorem or proof is present. The missing-artifact limitations and no-new-kernel-execution distinction remain exact in the source package and are stated in this guide’s opening evidence boundary. Do not relabel these commands or claim they were executed.')
omitregion('V_lean',31,64,184,'Continuation of guide-build instructions and rendering provenance only. Keep the application checklist at y200 onward unchanged.')
phrase('V_lean',38,'The final traditional edition','The mathematical text')
phrase('V_lean',42,'frozen candidate_contract.json','saved candidate_contract.json')
exclude('V_lean',[58],'Compiler and dependency pin appendix only.','Exact hashes and compiler identity remain in the source package. No mathematical hypotheses or results are on this page.')
# Chapter VI.
phrase('VI_traditional',2,'Distinct retained results from the earlier human edition','Complementary results')
phrase('VI_traditional',8,'accompany this reviewed edition. The\ninherited September 6 release records five checked Lean blocks covering all 33 scoped theorem-like','accompany the text. The saved Lean verification covers all 33 scoped theorem-like')
phrase('VI_traditional',41,'The September 6 release records the following automated-test','The recorded automated test suite reports the following')
block('VI_traditional',46,'Fifth checked block, 6 September 2026.','The formal development contains 341 explicit Lean theorem declarations across 47 proof modules. The saved compiler record reports a successful build and namespace audit under the pinned toolchain. The audit inspects 782 declarations, including definitions and generated auxiliaries. Only propext, Classical.choice and Quot.sound are allowed. These are different counting units from Part I’s 33 theorem-like results.')
phrase('VI_traditional',47,'The inherited fourth block proves','The formalization proves')
block('VI_traditional',47,'Verification and numerical evidence.','Verification and numerical evidence. The saved records report a successful pinned build and project-wide axiom audit, 54 passing companion tests and six passing verifier controls. The 54 tests comprise 37 original tests and 17 boundary and validation cases. The numerical records separately identify the 79-field comparison and the visual replay. Source contracts, exact theorem targets, logs and checked ledgers accompany the source files. Numerical tests are finite regressions and are not substitutes for the Lean proofs.')
block('VI_traditional',109,'R6 Earlier exact examples','R6 Additional exact examples')
block('VI_traditional',109,'These five short examples are retained','These five examples use numerical parameters distinct from the visual studies.')
phrase('VI_traditional',138,'The formal release keeps three original research questions separate','The formal contract keeps three research questions separate')
block('VI_traditional',139,'The first 28 pages retain','Plates VI.1–VI.28 develop the finite worked models corresponding to Part I. The references beneath their titles use Part I’s theorem numbers. Plates VI.29–VI.42 address the broader results in Part II.')
block('VI_traditional',139,'The chosen release records','The formal contract covers 33 scoped results, with 341 supporting theorem declarations in 47 proof modules and a saved audit of 782 namespace declarations. These counts describe the recorded formal development rather than independent new mathematical discoveries. The three conjectures retain their stated status.')
# Text is a single paragraph, so preserve counts and the exact finite-scope boundary while removing dates.
block('VI_traditional',139,'The visual-appendix tree contains','The accompanying files contain the mathematical models, drawing generator and exact-example verifier, with execution instructions. The recorded symbolic suite passed 204 exact or symbolic assertions and rejected 11 deliberately false controls. Its separate execution record is identified on Plate VI.42 and names every check and its finite scope.')
phrase('VI_traditional',153,'fresh edition','document review')
phrase('VI_traditional',153,'The September visual release records','The recorded symbolic suite reports')
block('VI_traditional',153,'Read this as: A final edition','Read this as: Read every proof, verification record and finite computation at its stated scope.')
block('VI_visual',2,'Preservation and revision','Mathematical coverage')
phrase('VI_lean',2,'This edition preserves','This guide preserves')
phrase('VI_lean',3,'traditional edition goes beyond them','mathematical text goes beyond them')
block('VI_lean',3,'The latest core is release','The formal ledger records all 33 scoped results as complete. The source contract names 341 explicit theorem declarations across 47 proof modules. The saved compiler and namespace audit reports record that 782 declarations were inspected in the project namespace. These counts measure manuscript endpoints, named theorem declarations, files and the wider namespace. None counts independent new mathematical discoveries.')
phrase('VI_lean',3,'Part I is the latest reviewed core','Part I gives the formal core')
phrase('VI_lean',3,'The saved September 6 build and axiom audit for the pinned source and de-','The saved compiler build and axiom audit for the pinned source and de-')
phrase('VI_lean',3,'No new Lean compilation occurred in this edition.','This guide does not claim a new Lean compilation.')
phrase('VI_lean',30,'The traditional edition preserves','The mathematical text contains')
phrase('VI_lean',30,'The precise hypotheses and editorial corrections are recorded in the traditional\nedition.','The precise hypotheses appear with the written proofs.')
phrase('VI_lean',31,'The latest core retains','The formal core retains')
phrase('VI_lean',31,'proved elsewhere in the edition','proved elsewhere in this book')
block('VI_lean',32,'Printed pages are the labels in the frozen traditional volume.','The Printed and PDF columns locate results in the attached Chapter VI source document. Printed labels and physical PDF pages differ because of the opening material. These locations refer to that source document rather than the continuous folios of this book.')
exclude('VI_lean',[34,35],'Compiler environment, timestamped execution reports, source integrity and replay commands belong with the exact source records.','The formal contract, all 33 scoped results, mathematical explanations, target declarations and hypotheses remain elsewhere in this guide. Preserve full evidence details in the source package; do not infer new kernel execution.')
phrase('VI_lean',47,'preserved v0.5.0 source contract','saved source contract')
omitregion('VI_lean',64,170,700,'The nine pinned dependency packages and their hashes are production metadata. The module-graph continuation above this region is retained.')
# Chapter VII.
block('VII_traditional',39,'Table 1. Reported finite numerical checks','Table 1. Recorded finite numerical checks.')
phrase('VII_traditional',39,'22/22 historical numerical tests, not rerun here.','22/22 recorded numerical tests.')
phrase('VII_traditional',87,'Continuum milestones and exact boundary','Continuum requirements and scope')
phrase('VII_traditional',89,'Milestone','Continuum objective')
phrase('VII_traditional',94,'The original paper’s\nnumerical convergence experiment and spectral dimension measurements provide a different kind of\nevidence and were not rerun during this prose revision.','The numerical convergence experiment and spectral dimension measurements provide finite computational evidence.')
block('VII_traditional',105,'These results concern operators on a finite dimensional space.','These results concern operators on a finite dimensional space. Continuum transfer limits, gravitational path integrals and physical spacetime models require further structure. The numerical figures provide separate computational illustrations.')
phrase('VII_traditional',159,'The strengthened edition supplies analytic','Part II supplies analytic')
phrase('VII_lean',2,'This edition preserves','This guide preserves')
phrase('VII_lean',2,'Finite computations and their dates are documented','Finite computations are documented')
block('VII_lean',6,'The frozen traditional volume has 159 physical PDF pages.','The Printed and PDF columns locate results in the attached Chapter VII source document. Physical PDF pages include its cover and opening material. These locations refer to that source document rather than the continuous folios of this book. A shared subject does not imply identical formal coverage.')
phrase('VII_lean',45,'The present edition does not rerun\nthe earlier paper.','The source correspondence is recorded separately.')
phrase('VII_lean',47,'The preserved original paper and the strengthened traditional edition','Parts I and II')
exclude('VII_lean',[49,50,51,52,53],'Five-page source-reconciliation, timestamped numerical evidence, font/rendering notes, compiler/replay commands and dependency provenance section.','No mathematical theorem or proof is present. It includes exact finite test counts and conditions, construction audit records and no-fresh-kernel-execution limits. Preserve these exact records with source material; mathematical coverage, the 19 finite item map and all hypotheses remain in this guide. The six constructed objects are also identified on page2 and in the later source catalogue.')
phrase('VII_lean',54,'inherited from the source release','supported by the saved compiler record')
phrase('VII_lean',70,'in this Lean module edition','in this Lean source')
exclude('VII_lean',[72],'Tail of source SHA-256 list and pinned compiler/dependency appendix.','No theorem, proof, definition or mathematical premise is present. Exact identities are retained in the source package.')
# Chapter VIII.
phrase('VIII_traditional',12,'No GPU timing is rerun for this edition.','They are not new timing measurements.')
block('VIII_lean',6,'The frozen traditional volume contains 124 physical PDF pages.','The Printed and PDF columns locate results in the attached Chapter VIII source document. Physical PDF pages include its cover and opening material. These locations refer to that source document rather than the continuous folios of this book. Original result numbers remain the correspondence keys.')
exclude('VIII_lean',[41],'Compiler summary, toolchain versions, source/log/interface identities, replay commands and guide assembly instructions.','No theorem or proof is present. The current 56-item contract, 392 named theorem declarations, 66 construction audits and four classical-input boundaries remain elsewhere in the guide. Retain exact verification evidence in the source package.')
phrase('VIII_lean',42,'are outside this release.','are not formalized here.')
block('VIII_lean',42,'11.5 Historical counts, failures, and numerical mirrors','11.5 Finite numerical examples')
block('VIII_lean',42,'The historical verification appendix records','')
block('VIII_lean',42,'The sixth development record retains','')
block('VIII_lean',42,'The inherited sixth numerical mirror records','The recorded numerical mirror covers 182 factor pairs, 638 truncation cases, 3,190 arbitrary rank-bounded competitors, nine invalid-input controls and two assumption-removal controls. It uses NumPy complex128 and numerical rank thresholds. It is neither extracted nor compiled Lean and does not prove universal matrix optimality. The CPU/GPU measurements remain separate and do not automatically instantiate the complete formal fair-match signature.')
phrase('VIII_lean',49,'remain outside this\nrelease.','are not formalized here.')
phrase('VIII_lean',60,'preserved with the edition','preserved in the accompanying files')
phrase('VIII_lean',76,'in this module edition','in these source modules')
exclude('VIII_lean',[80],'Tail of source/log hashes and the pinned inherited compiler, dependency and summary metadata.','No mathematical statement or proof is present. Preserve all exact source and verification identities in the source package.')
exclude('VIII_lean',list(range(92,99)),'Historical proof-development appendix with six successive block histories, versioned compiler identifiers, old remaining-work lists, development failures and repeated replay commands.','Read all seven pages. Historical unfinished-item lists are superseded by the current 56-item map. The substantive final small-core obligations are already explicit on page49 item5.6: actual compact ranges, supplied ordered thin SVD equations, ambient spectral/Frobenius optimality, exact tails and all zero/empty/rank-deficient boundaries. The four classical inputs are stated on page42. No distinct theorem, proof or extra mathematical hypothesis needs to be preserved from this history appendix in the reading book. Exact history remains in the source package.')
# Preserve scholarly editions/years and legitimate mathematical usage.
kept=[]
for row in json.loads((R/'editorial/volume_finish/version_candidates.json').read_text()):
 if row['component_id'].split('_')[0] not in ['V','VI','VII','VIII']:continue
 t=row['text']
 if row['source_page'] in next((x['source_pages_1based'] for x in ex if x['component_id']==row['component_id'] and row['source_page'] in x['source_pages_1based']),[]):continue
 if re.search(r'predict|prediction|Bayesian|posterior|likelihood|cached|updated system|update function|update performed|actual update|updat(e|ed) scores|update is local',t,re.I):why='Mathematical update operation or a code identifier, not publication history.'
 elif re.search(r'edition,? (?:19|20)\d\d|third edition|second edition|Archive version|DLMF|dlmf|Trigonometric Series',t,re.I):why='Scholarly source edition/year or technical source identity. Retain in the consolidated bibliography.'
 elif 'version' in t.lower():why='Inspect context: mathematical variant, or exact verification requirement kept with source records. Never apply a blanket version deletion.'
 else:continue
 kept.append({**row,'decision':'preserve_or_move_exact_source_record','reason':why})
plan={'status':'READY_FOR_ROOT_REVIEW','scope':'Current selected V–VIII display components only. No source or PDF mutations performed.','schema':'volume-finish.display-plan/1','operations':ops,'whole_page_exclusions':ex,'preserved_candidate_decisions':kept,'mathematical_token_changes':[],'notes':['Exact commands and filenames must never be renamed merely to hide version numbers; keep or omit the complete command with its context.','Scholarly publication dates and edition identifiers are bibliographic facts and should remain in the consolidated sources at the end.','Block replacements are intentionally shorter than the original. Root should preserve heading/font distinction, verify fit and compare unchanged mathematical glyphs outside edited prose regions.','Source navigation tables must not be described as current book folios unless their actual link/page map is transformed. Proposed text explicitly identifies the attached source document.','Broader editions/earlier branches are translated into current Part I/II/III structure where mathematically meaningful; formal coverage distinctions remain.']}
(R/'editorial/volume_finish/v_viii_plan.json').write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'operations':len(ops),'whole_page_exclusion_groups':len(ex),'pages':sum(len(x['source_pages_1based']) for x in ex),'kept_decisions':len(kept)},indent=2))
