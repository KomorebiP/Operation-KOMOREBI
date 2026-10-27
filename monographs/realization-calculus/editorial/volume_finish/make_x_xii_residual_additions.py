from pathlib import Path
import json,re,hashlib,zipfile,sys
import fitz
R=Path('/dev/shm/komorebi_core_monograph_fbc994080222');O=R/'editorial/volume_finish';sys.path.insert(0,str(R))
from preserved_pdf_proofread import ismath
S=json.loads((O/'baseline_build_spec.json').read_text());C={c['id']:c for p in S['parts'] for c in p['components']};Z=zipfile.ZipFile('/workspace/scratch/fbc994080222/komorebi_core_monograph_delivery/Realization_Calculus_Publication_Package.zip');D={}
oldplan=json.loads((O/'ix_xii_plan.json').read_text());oldops=oldplan.get('changes',oldplan.get('operations',[]));ops=[];pages=[];scope=[]
def doc(cid):
 if cid not in D:
  data=Z.read('Realization_Calculus_Publication_Package/'+C[cid]['path']);assert hashlib.sha256(data).hexdigest()==C[cid]['sha256'];D[cid]=fitz.open(stream=data,filetype='pdf')
 return D[cid]
def add(cid,pn,old,new,kind='replace_phrase',reason='Remove production chronology while preserving the claim and its scope.',bbox=None,**kw):
 pg=doc(cid)[pn-1]
 if bbox is None:
  hits=pg.search_for(' '.join(old.split()))
  if not hits:
   # Full native block may contain line-wrap ligatures; resolve by exact PDF block text.
   hits=[fitz.Rect(b[:4]) for b in pg.get_text('blocks') if old in b[4]]
  assert hits,(cid,pn,old)
  b=fitz.Rect(hits[0])
  for h in hits[1:]:b|=h
  bbox=list(b)
 row={'component_id':cid,'source_page_1based':pn,'kind':kind,'action':kind,'old':old.rstrip('\n'),'new':new,'bbox':bbox,'reason':reason,'category':'publication_prose','baseline_source':C[cid]['path'],**kw};ops.append(row);return row
def block(cid,pn,bi,new,**kw):
 b=doc(cid)[pn-1].get_text('blocks')[bi];return add(cid,pn,b[4],new,'replace_block',bbox=list(b[:4]),**kw)
def omit(cid,pn,indices,reason,table=False):
 pg=doc(cid)[pn-1];bs=pg.get_text('blocks');b=fitz.Rect(bs[indices[0]][:4])
 for i in indices[1:]:b|=fitz.Rect(bs[i][:4])
 b=fitz.Rect(b.x0-.2,b.y0-.2,b.x1+.2,b.y1+.2)
 bad=[s['text'] for bl in pg.get_text('dict')['blocks'] for l in bl.get('lines',[]) for s in l['spans'] if fitz.Rect(s['bbox']).intersects(b) and ismath(s) and s['text'].strip()]
 assert not bad,(cid,pn,indices,bad)
 return add(cid,pn,pg.get_text(clip=b),'','omit_region',reason,list(b),source_block_indices=indices,math_spans_present=False,exact_bounded_region=True,nonmathematical_table_rules_in_region=[{'bbox':list(x['rect']),'type':x['type']} for x in pg.get_drawings() if fitz.Rect(x['rect']).intersects(b)] if table else [])
def whole(cid,nums,reason):pages.append({'component_id':cid,'source_pages_1based':nums,'reason':reason})
# X: reader-facing scope, without chronological ledger chatter.
block('X_traditional',63,2,'Main text: §§1–3, 8–11. Conditional contract: Appendix D.')
block('X_traditional',63,27,'The foundational scalar/Mellin contract covers 17 of 20 records. Claims 9.1, 9.2 and 11.1 need their completed interfaces. The amended conditional assembly covers all twenty under the inputs stated in Appendix D. The finite character examples below do not prove prescribed Frobenius occurrence.')
block('X_traditional',63,28,'The figures illustrate exact models. Their finite Python checks and formal verification have separate records and scopes.')
block('X_traditional',92,3,'The three contracts have different hypotheses. Their coverage counts do not make them interchangeable.')
add('X_traditional',92,'Historical 17/20','Foundational 17/20','replace_table_cells')
add('X_traditional',92,'Block 27 and the scalar/Mellin continuation. Claims 9.1, 9.2, and 11.1\nwere partial in those revisions.','The foundational scalar/Mellin contract. Claims 9.1, 9.2 and 11.1 remain partial under those statements.','replace_table_cells')
add('X_traditional',92,'Later 19/20','Stronger 19/20','replace_table_cells')
add('X_traditional',92,'A stronger residual-system attempt with no promoted terminal\nendpoint and an unavailable pinned Lean executable. It is a different\ncontract, not a failed recompilation of the checked source.','A stronger residual-system contract with an unproved terminal endpoint. It does not recheck or replace the conditional assembly.','replace_table_cells')
add('X_lean',2,'Their saved verification and the separate\nOctober 20 production replay remain explicit.','Their verification scope is stated separately.')
block('X_lean',4,0,'1 Formal verification and scope')
omit('X_lean',4,[1,2],'Exact source-snapshot identity, archive-access history and dated run selection are production records retained with the source package.')
block('X_lean',4,3,'The recorded compiler checks cover 122 project and support modules, including the 97-module terminal closure. Two clean builds agreed on 392 artifacts. The matching Lean toolchain and all nine dependency identities were checked. External Mathlib caches were reused. This is not a cold dependency rebuild.')
# Keep positive audited scope, but remove repairs/memory-history in following split continuation.
add('X_lean',4,'The unchanged checker first hit its 4 GB memory cap. The\nsuccessful serial run raised the cap to 6 GB. Failed attempts remain recorded.','The source records give the checking procedure and its limits.')
add('X_lean',5,'Block\n27\nand\nscalar/Mellin','Foundational contract','replace_table_cells')
add('X_lean',5,'Historical 17/20, with Claims 9.1, 9.2, and 11.1 still partial in those source revisions.','The foundational contract covers 17/20. Claims 9.1, 9.2 and 11.1 remain partial under those statements.','replace_table_cells')
add('X_lean',5,'Later residual attempt','Stronger residual contract','replace_table_cells')
add('X_lean',5,'19/20 and an unpromoted terminal claim under a stronger contract. Its unavailable\npinned compiler is not a rejection of the earlier checked module.','19/20 under a stronger contract with an unproved terminal claim. This does not invalidate the conditional assembly.','replace_table_cells')
whole('X_lean',[16,17],'Source preservation/replay instructions, environment identities and listing typography only. Actual theorem statements, twenty-row contract, positive verified scope and conditional boundaries remain in the mathematical walkthrough and source listings.')
omit('X_lean',37,[7,8],'Archive directory and licence-production note; exact paths and all third-party notices remain in the package, while the volume has its own rights notice.')
# XI: source methods and arithmetic boundary stay; chronology and audit execution diary leave book.
block('XI_lean',2,1,'This companion explains the formal mechanisms and their arithmetic interfaces. The general realization endpoint is Conjecture 66. Detailed proofs, construction notes and evidence records accompany the sources.')
block('XI_lean',4,10,'The compiler record covers all 423 selected modules with unchanged source hashes. All 4,342 catalogued names resolved to their recorded owners, including four private or local source names matched through Lean’s private-name map. The terminal and the single-candidate comparison supplement are separate checked targets.')
omit('XI_lean',5,[5,6,7,8,9],'Execution diary, failed runs, repair history and archive reporting instructions only. The positive checked module/name counts and standard axiom set above remain intact.')
omit('XI_lean',9,[4,5],'Introduction to the historical proof-obligation/source navigation crosswalk. Its complete exact JSON and source records remain in the package.')
block('XI_lean',9,6,'The source catalog identifies all 423 module paths, 4,342 named lexical declarations and forty teaching excerpts. Compiler and axiom records state their own checked targets. A source census and a kernel check have different scopes.')
whole('XI_lean',[237,238,239,240],'Pure original-obligation and excerpt/source crosswalks. Actual existence contract, declared source range, Conjecture66 quantifiers, same-candidate H5, factor-profile separation and complete conditional formal signature remain explicitly on pp32–34 and in their retained exact excerpts.')
scope.append({'component_id':'XI_lean','retained_pages':[32,33,34],'verified_preservation':'p32 states actual existence as unresolved, same-candidate H5 and factor-profile separation; p33 prints full conditional signature and Conjecture66 realization contract plus same-candidate H5; p34 states conjectural arithmetic realization versus conditional comparison and restricted ordinary constructions. Source-only crosswalk removal does not promote Conjecture66.'})
# Research companion: exact native blocks selected geometrically, including out-of-order extraction.
omit('XI_research_progress',8,[4,11],'Compiler version/dependency hash and repeated replay-provenance qualification only. The explicit Realization.exists_atom input and existence/conditional-comparison distinction remain directly above.')
omit('XI_research_progress',32,[8,14],'Source-map heading, archive JSON paths and production source-map introduction. Arithmetic hypotheses and limitations above remain untouched.')
omit('XI_research_progress',33,[0,1,2,4,5,6],'Pure source/evidence map and its wrapped introduction. The finite-computation section below and p33 final sentence continuing onto p34 remain untouched.',True)
omit('XI_research_progress',34,[14,15,16],'Source provenance/census/publication-audit paragraphs only. The opening mathematical continuation, research reading route, and separate bibliography are preserved.')
block('XI_research_progress',32,12,'Written proofs, finite tests and formal declarations have distinct scopes. None supplies a missing arithmetic input.')
omit('XI_research_progress',32,[16,13],'Continuation of the replaced evidence-ledger paragraph, with historical compiler and completion-percentage commentary. No mathematical hypothesis, assertion or proof occurs.')
# XII: wording changes only around unchanged mathematical glyphs.
add('XII_traditional',37,'The revision therefore states','The statement imposes')
add('XII_traditional',37,'The revision requires the','The statement needs the')
add('XII_visual',19,'reported separately from the source release.','recorded separately.')
# Keep p26 mathematical scope and all p28 catalogue rows, remove literal replay/build sections.
omit('XII_lean',26,list(range(3,15)),'Replay prerequisites, exact toolchain table, commands and production instructions only. Complete coefficient-topology and conditional-realization scope in the top three blocks remains.',True)
whole('XII_lean',[27],'Literal replay verifier and package/reader-build instructions only. Exact sources retain those commands and provenance; mathematical scope and the formal claim correspondence remain in the companion.')
omit('XII_lean',28,[0],'Wrapped continuation of source-package PDF build reproducibility instructions. Full 96-module source catalogue below remains intact.')
# Small metadata variants that are unambiguous and do not change mathematical meaning.
add('XI_research_progress',2,'the entire historical archive.','the entire source archive.')
add('XI_research_atlas',35,'preserved checkpoint.','source collection.')
# Overlap manifest for safe merge: supersede only operations wholly contained in each new omission or whole-page omission.
sup=[]
for i,x in enumerate(oldops):
 pn=x.get('source_page_1based',x.get('page_1based'));cid=x['component_id'];b=x.get('bbox')
 wh=next((v for v in pages if v['component_id']==cid and pn in v['source_pages_1based']),None)
 if wh:sup.append({'plan_index':i,'reason':'New whole-page source-only omission supersedes this operation.','old':x.get('old','')[:120]});continue
 for y in ops:
  if y['kind']=='omit_region' and cid==y['component_id'] and pn==y['source_page_1based'] and b and fitz.Rect(y['bbox']).contains(fitz.Rect(b)):
   sup.append({'plan_index':i,'reason':'New source-only region fully contains this existing operation.','old':x.get('old','')[:120]});break
result={'status':'FROZEN_PROPOSAL_READ_ONLY','scope':'X–XII production chronology and source-replay residue only; baseline bytes read from exact preceding publication ZIP. No source/PDF mutation.','changes':ops,'whole_page_exclusion_candidates':pages,'supersede_existing_plan_indices':sup,'preserved_scope_checks':scope,'mathematical_token_changes':[],'cautions':['Do not remove the p33 final research-companion sentence or p34 opening continuation. These are outside the source-map omission region.','All replacements in tables use replace_table_cells. Original 17/20 versus amended conditional20/20 and stronger19/20 remain distinct.','Whole-page XI237–240 omissions concern source crosswalks, not formal declarations or proofs; pp32–34 retain the full contract and H5 boundary.','Exact bibliography identities and publication years remain in the back references. Mathematical uses of version (unframed, derived, indexed, etc.) are retained.']}
(O/'x_xii_residual_additions.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'changes':len(ops),'whole_page_groups':pages,'superseded_existing':len(sup)},indent=2))
