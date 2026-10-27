from pathlib import Path
import json,hashlib,re,difflib,collections
import fitz
R=Path(__file__).resolve().parents[1];G=R/'source_ix_xii';E=R/'editorial/book_revision'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=json.loads((E/'ix_xii_prose_inventory_before.json').read_text());changes=[];diff=[]
for q in inv:
 p=R/q['path'];a=G/'book_edit_before'/p.relative_to(G)
 if a.read_bytes()!=p.read_bytes():
  changes.append({'path':q['path'],'original_sha256':sha(a),'edited_sha256':sha(p),'original_lines':len(a.read_text().splitlines()),'edited_lines':len(p.read_text().splitlines())})
  diff.extend(difflib.unified_diff(a.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='before/'+q['path'],tofile=q['path']))
(E/'ix_xii_prose.patch').write_text(''.join(diff))
# The authoritative final source delta includes the corrected braces/keys/anchors.
(E/'ix_xii_final_source_changes.json').write_text(json.dumps(changes,indent=2)+'\n')
base=json.loads((R/'component_builds.json').read_text())['components'];updates=[]
fronts={
('IX','traditional'):{'cover':[1],'pure_contents':[[5,9]],'retain_front_prose':[[2,4]],'main_mathematical_body_starts':10},
('IX','visual'):{'cover':[1],'pure_contents':[],'mixed_scope_and_contents':[2],'main_mathematical_body_starts':3},
('IX','lean'):{'cover':[1],'pure_contents':[[3,4]],'mixed_scope_and_contents':[2],'main_mathematical_body_starts':5},
('X','traditional'):{'cover':[1],'pure_contents':[[4,5]],'retain_front_prose':[[2,3]],'main_mathematical_body_starts':6,'duplicate_atlas_intro_leaf':62,'duplicate_atlas_pages':[[63,92]]},
('X','visual'):{'cover':[1],'pure_contents':[],'retain_front_prose':[[2,3]],'main_mathematical_body_starts':4},
('X','lean'):{'cover':[1],'pure_contents':[[3,3]],'mixed_abstract_and_contents':[2],'main_mathematical_body_starts':4},
('XI','traditional'):{'cover':[1],'pure_contents':[[3,3]],'retain_front_prose':[[2,2],[4,5]],'main_mathematical_body_starts':6},
('XI','visual'):{'cover':[1],'pure_contents':[[5,6]],'retain_front_prose':[[2,4]],'main_mathematical_body_starts':7},
('XI','lean'):{'cover':[1],'pure_contents':[[3,3]],'retain_front_prose':[[2,2]],'main_mathematical_body_starts':4},
('XII','traditional'):{'cover':[1],'pure_contents':[[3,3]],'retain_front_prose':[[2,2]],'main_mathematical_body_starts':4},
('XII','visual'):{'cover':[1],'pure_contents':[],'main_mathematical_body_starts':2},
('XII','lean'):{'cover':[1],'pure_contents':[],'retain_front_prose':[[2,2]],'mixed_abstract_and_contents':[3],'main_mathematical_body_starts':4},
}
for paper,folder in [('IX',G/'IX/publication/pdfs'),('X',G/'X/publication/pdfs'),('XI',G/'book_rebuild_xi_scope'),('XII',G/'book_rebuild_xii_scope')]:
 for p in sorted(folder.glob('*.pdf')):
  role='lean' if 'Lean' in p.name else 'visual' if 'Visual' in p.name else 'traditional';b=next(x for x in base if x['paper']==paper and x['baseline_filename']==p.name);d=fitz.open(p)
  updates.append({'paper':paper,'role':role,'baseline_filename':b['baseline_filename'],'baseline_sha256':b['baseline_sha256'],'prior_output_sha256':b.get('sha256',b.get('output_sha256')),'output_pdf':str(p.relative_to(R)),'pages':len(d),'sha256':sha(p),'local_page_label_rules':d.get_page_labels(),'front_page_map':fronts[(paper,role)],'build_kind':'source_retypeset_editorial_book_revision','returncode':0})
assert len(updates)==12
(E/'ix_xii_component_updates.json').write_text(json.dumps({'schema':'realization-calculus.book-component-updates/1','sealed':True,'components':updates},indent=2)+'\n')
# Refresh page inventory metadata after the paragraph-anchor rebuild.
pi=json.loads((E/'ix_xii_pdf_inventory.json').read_text())
for q in pi:
 u=next(u for u in updates if u['paper']==q['paper'] and u['role']==q['kind']);q['sha256']=u['sha256'];q['pages']=u['pages']
(E/'ix_xii_pdf_inventory.json').write_text(json.dumps(pi,indent=2)+'\n')
# Assertions against the original source texts, not only successful compilation.
pat=re.compile(r'\\(?:label|ref|eqref|pageref|autoref|hypertarget|hyperlink|href)\{([^{}]*)\}|\\hyperref\[([^\[\]]*)\]')
id_delta=[];original_identifiers=0
for q in inv:
 p=R/q['path'];a=(G/'book_edit_before'/p.relative_to(G)).read_text();b=p.read_text();ka=collections.Counter(m[0] for m in pat.finditer(a));kb=collections.Counter(m[0] for m in pat.finditer(b));original_identifiers+=sum(ka.values());removed=list((ka-kb).elements());assert not removed,(q['path'],removed)
 if kb!=ka:id_delta.append({'path':q['path'],'added':list((kb-ka).elements())})
preserve=json.loads((E/'ix_xii_preservation_check.json').read_text())
assert not preserve['display_math']['changes'];assert not preserve['literal_environments']['changes']
logs=list((G/'IX/compiled').glob('*/*Final.log'))+list((G/'X/compiled').glob('*/*Final.log'))+list((G/'book_rebuild_xi_scope/build').glob('*/*Final.log'))+list((G/'book_rebuild_xii_scope').glob('*/*Final.log'))
logchecks=[]
for p in logs:
 s=p.read_text(errors='replace');flags=[l for l in s.splitlines() if re.search(r'Overfull|Missing character|undefined|multiply defined|Label\(s\) may|LaTeX Error|^!',l)];assert not flags,(p,flags);logchecks.append({'log':str(p.relative_to(R)),'flags':flags})
assert len(logchecks)==12
(E/'ix_xii_log_checks.json').write_text(json.dumps(logchecks,indent=2)+'\n')
report={
 'scope':'Conservative editorial proofreading and reader-reference review of the active IX–XII book sources; not a fresh proof audit, Lean replay, or complete word-by-word review of all 258k words.',
 'coverage':{'active_prose_include_files':len(inv),'original_words':sum(q.get('words',q.get('word_count',0)) for q in inv),'changed_files':len(changes),'method':'All active prose/include sources indexed; targeted version/date/block/plate/page-reference candidates reviewed in context; all changed passages reviewed against their originals. Figures, generated catalogs, preserved source archives and code bodies excluded from prose rewriting.'},
 'routine_changes':['Timeless reading scope and mathematical route introductions; release/date details removed from editable main fronts.','Chapter-qualified Plate X.N, Plate XI.N (research atlas only), and Plate XII.N references with original destinations retained.','X development-block shorthand replaced by named constructions with 17 distinct clickable paragraph destinations.','XI restriction/Conjecture 66 boundary and XII supplied arithmetic hypotheses explicitly retained.','Local word/number spacing and professional heading/caption cleanup; technical compiler versions and archival source identities preserved.'],
 'preservation':{'display_math_blocks_byte_identical':2731,'literal_environments_byte_identical':292,'original_cross_reference_occurrences_preserved':original_identifiers,'original_cross_reference_removals':0,'added_cross_references':id_delta,'inline_math_delta':'One B^{[j]} occurrence removed with an archival explanation of a previous typographic repair in XI reader_route.tex. The actual definition and proof are unchanged.','literal_command_delta':'Removed two .md format mentions and one duplicate RANK4_ENLARGED_CARRIER167.md path mention from reader/provenance prose. The source filename remains in the appendix provenance. No Lean identifier changes.','mathematical_claims':'No theorem, proof, displayed equation, binder, hypothesis or conclusion deliberately changed or strengthened. All display mathematics and literal environments are byte-identical.','no_lean_invocation':True,'source_files':changes},
 'layout_validation':{'compiled_components':12,'fatal_reference_glyph_overfull_flags':0,'rendered_sample_pages':['IX mathematical scope p4','X appendix p44 and visual Plate X.2','XI reading route p4 and rank-four proof p102','XII visual Plate XII.1'],'result':'Selected renders show readable typography, intact formulas, and unclipped plate/cross-reference labels. Existing underfull and microtype warnings are not new content failures.'},
 'caught_and_fixed':['X and XII plate-reference macro closing braces restored after X first build failed.','XI local prose-spacing substitution had reached rank2/rank4 identifiers. Every original reference key was restored exactly; full original-key multiset comparison passes.','X new named paragraph labels received phantom anchors after auxiliary-file inspection showed inherited theorem/figure destinations. All 17 now have distinct destinations.'],
 'x_duplicate_atlas':{'traditional_pages':[63,92],'visual_pages':[4,33],'traditional_intro_leaf':62,'comparison':'30/30 text and half-scale pixel renders identical; no source pages removed by this agent.'},
 'ix_unique_appendix_spans':{'detailed_continuation_derivations':[87,109],'restricted_native_proofs':[110,113],'recovered_polyphase_treatment':[114,160],'mathematical_checkpoint_supplements':[161,229],'worked_arithmetic_lifting_atlas':[230,239]},
 'unresolved_or_parent_actions':['Parent owns global page selection: remove repeated covers/contents and one exact X atlas copy using the supplied source-page maps.','XI preserved research atlas V01–V32 labels are parent-owned; use Plate XI.1–XI.32 and retain original destination IDs. Core XI visual lessons keep their section numbers.','Formal companion source snapshots, exact toolchain versions and verification dates remain as reproducibility information; no new Lean verification is asserted.','Opaque archival Block/source identifiers remain where they name retained historical provenance rather than an established unique theorem. They were not blindly stripped.','Some Lean source-map tables retain companion-local page addresses; global assembly should label them as local if retained.','X historical_checkpoint_frontmatter.tex is retained on disk but its redundant archival progress front matter is no longer input to the main reader; the mathematical constructions and conditional boundaries remain.'],
 'output_updates_file':'editorial/book_revision/ix_xii_component_updates.json','backup_root':'source_ix_xii/book_edit_before','source_diff':'editorial/book_revision/ix_xii_prose.patch'
}
(E/'ix_xii_report.json').write_text(json.dumps(report,indent=2)+'\n')
lines=['IX–XII editorial book revision','',report['scope'],'',f"Coverage: {len(inv)} active source/include files; {len(changes)} changed files. Exact originals and SHA256 records retained.",'Validation: 12/12 components compiled; no fatal, undefined-reference, duplicate-label, missing-glyph or overfull-box flags in final logs.','Preservation: 2731 display math blocks and 292 literal/code environments unchanged; every original cross-reference key occurrence preserved.','One inline B^{[j]} occurrence removed from obsolete repair-history prose only. No Lean replay or proof audit performed.','','Sealed component updates: editorial/book_revision/ix_xii_component_updates.json','Source diff: editorial/book_revision/ix_xii_prose.patch','','X overlap: main 63–92 = visual 4–33, exactly for all 30 rendered/text pages. Main p62 is the atlas introduction.','IX unique mathematical appendix spans: 87–109, 110–113, 114–160, 161–229, 230–239.','','Parent actions / limits:']+['- '+s for s in report['unresolved_or_parent_actions']]
(E/'ix_xii_report.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'changed_files':len(changes),'component_updates':12,'preserved_cross_reference_occurrences':original_identifiers,'component_pages':[(x['paper'],x['role'],x['pages']) for x in updates]},indent=2))
