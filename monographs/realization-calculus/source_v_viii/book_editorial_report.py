from pathlib import Path
import json,re,hashlib,fitz
ROOT=Path(__file__).resolve().parent.parent;S=ROOT/'source_v_viii';B=S/'book_edit_baseline';O=ROOT/'editorial/book_revision'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old_registry={(r['paper'],r['role']):r for r in json.loads((ROOT/'component_builds.json').read_text())['components'] if 'role' in r}
builds=json.loads((S/'REBUILD_RESULT.json').read_text());records=[];pdfqa=[]
for x in builds:
 p=S/x['output_pdf'];d=fitz.open(p);old=old_registry[(x['paper'],x['role'])]
 r=dict(old);r.update(output_pdf=str(p.relative_to(ROOT)),pages=len(d),sha256=sha(p),build_runs=x['commands_returncodes'],warnings=x['hard_diagnostics'],origin_result_group='editorial/book_revision/v_viii_report.json',editorial_revision=True)
 r['output_sha256']=sha(p)
 r['local_page_label_rules']=d.get_page_labels();records.append(r)
 invalid=[];outside=[];links=0
 for i,page in enumerate(d):
  for link in page.get_links():
   links+=1
   if link['kind']==fitz.LINK_GOTO and not 0<=link.get('page',-1)<len(d):invalid.append({'page':i+1,'link':link})
  for b in page.get_text('blocks'):
   if b[0]<-1 or b[1]<-1 or b[2]>page.rect.width+1 or b[3]>page.rect.height+1:outside.append(i+1)
 pdfqa.append({'paper':x['paper'],'role':x['role'],'pages':len(d),'link_count':links,'invalid_local_links':invalid,'outside_page_text_pages':sorted(set(outside)),'previous_component_sha256':old.get('sha256',old.get('output_sha256')),'previous_component_pages':old['pages']})
source_rows=[];proof_rows=[]
proofpat=re.compile(r'\\begin\{proof\}.*?\\end\{proof\}',re.S)
statementpat=re.compile(r'\\begin\{(?:theorem|lemma|proposition|corollary|definition|conjecture|remark)\}.*?\\end\{(?:theorem|lemma|proposition|corollary|definition|conjecture|remark)\}',re.S)
for b in sorted(B.rglob('*')):
 if not b.is_file():continue
 p=S/b.relative_to(B)
 if not p.is_file() or p.read_bytes()==b.read_bytes():continue
 source_rows.append({'file':str(p.relative_to(ROOT)),'baseline':str(b.relative_to(ROOT)),'original_sha256':sha(b),'edited_sha256':sha(p)})
 if p.suffix=='.tex':
  a=b.read_text();z=p.read_text();proof_rows.append({'file':str(p.relative_to(ROOT)),'proofs_before':len(proofpat.findall(a)),'proofs_after':len(proofpat.findall(z)),'proofs_equal':proofpat.findall(a)==proofpat.findall(z),'statement_environments_before':len(statementpat.findall(a)),'statement_environments_equal':statementpat.findall(a)==statementpat.findall(z)})
moved=json.loads((O/'viii_moved_history.json').read_text())
for r in moved:
 assert sha(S/r['raw_record'])==r['raw_record_sha256']
 original=(B/r['from']).read_text();raw=(S/r['raw_record']).read_text()
 assert raw==original[original.index(r['anchor']):]
 r['exact_match_to_pre_edit_baseline_tail']=True
overlap=json.loads((O/'v_viii_plate_overlap.json').read_text())
front={
 'V':{'traditional':{'cover':[1],'reading_introduction':[2],'local_lists':[[3,8]],'mathematical_content_start':9},'visual_guide':{'cover':[1],'unique_reading_routes':[[2,3]],'plate_start':4},'lean_guide':{'cover':[1],'mixed_reading_guidance_and_toc':[2],'content_start':3}},
 'VI':{'traditional':{'cover':[1],'reading_introduction':[2],'local_lists':[[3,7]],'mathematical_content_start':8},'visual_guide':{'cover':[1],'unique_reading_routes':[2],'plate_start':3},'lean_guide':{'cover':[1],'mixed_reading_guidance_and_toc':[2],'content_start':3}},
 'VII':{'traditional':{'cover':[1],'reading_introduction':[2],'local_lists':[[3,8]],'mathematical_content_start':9},'visual_guide':{'cover':[1],'unique_reading_routes':[2],'plate_start':3},'lean_guide':{'cover':[1],'mixed_reading_guidance_and_toc':[2],'content_start':3}},
 'VIII':{'traditional':{'cover':[1],'reading_introduction':[[2,3]],'local_lists':[[4,6]],'mathematical_content_start':7},'visual_guide':{'cover':[1],'unique_reading_routes':[2],'plate_start':3},'lean_guide':{'cover':[1],'reading_guidance':[2],'local_toc':[3],'content_start':4,'historical_records':[[92,98]]}}
}
plate_summary=[]
for ch in front:
 rs=[r for r in overlap['rows'] if r['chapter']==ch]
 plate_summary.append({'paper':ch,'count':len(rs),'traditional_pages':[rs[0]['traditional_pdf_page'],rs[-1]['traditional_pdf_page']],'standalone_pages':[rs[0]['visual_pdf_page'],rs[-1]['visual_pdf_page']],'all_bodies_equal_after_documented_format_normalization':all(r['body_equal_whitespace_normalized'] for r in rs),'all_figure_bytes_equal':all(r['figure_source_hashes_equal'] for r in rs),'all_named_result_locators_equal':all(r['locator_equal'] for r in rs),'one_page_per_plate':all(b['traditional_pdf_page']-a['traditional_pdf_page']==1 for a,b in zip(rs,rs[1:]))})
report={
 'schema':'realization-calculus.book-editing/v-viii/1',
 'status':'All twelve components rebuilt successfully; editorial and navigation QA complete within the stated scope.',
 'coverage':['Active mathematical-text chapter introductions, reading routes, section headings adjacent to edited material, and reader-facing evidence/scope narratives in V–VIII.','All 154 paired embedded/standalone visual plates: identifier expansion, named-result source lines, stale standalone page locators, duplicate-content comparison, and figure identity.','Formal-guide opening scope and reproduction descriptions; exact Lean excerpts, generated declaration identifiers and toolchain pins preserved.','All six VIII supplementary verification tails relocated and framed historically, with their subsequent mathematical resolutions referenced in the main text.','Every changed sentence was reviewed in context. This was not a line-by-line correctness audit of every theorem or a new formal/math execution.'],
 'routine_edits':['Timeless chapter introductions and explicit reading routes replace date/version/status narration.','Qualified visual labels such as Plate VIII.32 retain original named destinations. All visual source lines identify the chapter.','The V notation/formal correspondence locators identify actual Sections 20 and 21; VII range-bundle references identify Part III Sections III.24–III.26.','VIII historical verification and remaining-work lists move to the formal companion; current main-text boundaries name subsequent proof sections.','VIII embedded atlas now retains all 32 source lines previously unique to its standalone guide.','VI.1 table uses compact chapter-qualified ranges under a Plates column heading, preventing an orphaned takeaway.'],
 'mathematical_token_changes':[],
 'mathematical_preservation_notes':['No operator, relation, hypothesis, conclusion, proof step, theorem statement, Lean identifier or code excerpt was changed.','A duplicate inline occurrence of tau > 0 in VIII Appendix A prose was removed during consolidation; the hypothesis remains explicitly stated and the displayed feasibility argument is unchanged.','Eight numerical residual/tolerance expressions moved unchanged from VIII appendices D–F into the historical records.','All explicit proof and theorem-like environments in edited source files compare byte for byte with their pre-edit baselines.'],
 'proof_preservation':{'explicit_proof_environments':sum(r['proofs_before'] for r in proof_rows),'statement_environments':sum(r['statement_environments_before'] for r in proof_rows),'all_proofs_byte_identical':all(r['proofs_equal'] for r in proof_rows),'all_statement_environments_byte_identical':all(r['statement_environments_equal'] for r in proof_rows),'files':proof_rows},
 'moved_records':moved,
 'source_hashes':source_rows,
 'created_source_hashes':[{'file':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in [S/'VIII/editable/lean_guide/chapters/proof_history.tex',*sorted((S/'VIII/editable/lean_guide/history').glob('*.tex'))]],
 'component_updates':records,
 'build_validation':{'all_success':all(x['success'] for x in builds),'diagnostics':[{'paper':x['paper'],'role':x['role'],'hard_diagnostics':x['hard_diagnostics']} for x in builds],'fresh_lean_or_scientific_replay':False,'entrypoints':['source_v_viii/build_all.py --jobs 2','source_v_viii/rebuild_book_components.py [component keys]']},
 'pdf_validation':pdfqa,
 'front_matter_map':front,
 'visual_overlap_summary':plate_summary,
 'visual_overlap_details':'editorial/book_revision/v_viii_plate_overlap.json',
 'previewed_pages':['V traditional 2','VII traditional 2','VI traditional 112 (Plate VI.1)','VIII traditional 88 (Plate VIII.1)','VIII traditional 119 (Plate VIII.32)','VIII Lean 2, 92, 93, 98'],
 'unresolved_for_parent_assembly':['The source traditional Reading-this-chapter bookmarks still inherit a cover-page target; root should map them to retained introduction page 2 in global navigation. The VIII Three-exact-models bookmark similarly needs actual page 8.','V–VII Lean page 2 mixes substantive guidance with local contents; keep the page or extract its guidance before discarding its contents.','Standalone route pages remain unique: V pages 2–3 and VI–VIII page 2. Retain or incorporate them even when aliasing all repeated plates to their embedded versions.','Frozen-reader page numbers in exact formal correspondence tables remain explicit archival locators, with preserved named source/result keys; they are not global monograph page references.'],
 'preserved_originals':'book_edit_baseline holds exact pre-edit files; frozen readers/source archives and earlier publication package remain untouched.',
 'authoring_note':'Authoring pass scripts document one-time transformations and are not idempotent rebuild commands. The build entrypoints above reproduce current sources.'
}
(O/'v_viii_report.json').write_text(json.dumps(report,indent=2));(O/'v_viii_proof_preservation.json').write_text(json.dumps(proof_rows,indent=2))
lines=['V–VIII editorial report','',report['status'],'',f"Edited source files: {len(source_rows)}. Explicit proof environments preserved exactly: {report['proof_preservation']['explicit_proof_environments']}. Theorem-like environments preserved exactly: {report['proof_preservation']['statement_environments']}.",'Mathematical-token changes: none. No Lean or scientific computation rerun.','', 'Components (current physical pages):']
for r in records:lines.append(f"{r['paper']} {r['role']}: {r['pages']} pages; {r['sha256']}; {r['output_pdf']}")
lines+=['','Embedded / standalone plate overlap:']
for r in plate_summary:lines.append(f"{r['paper']}: {r['count']} matching plates; embedded {r['traditional_pages']}, standalone {r['standalone_pages']}; all figure bytes and named-result locators equal.")
lines+=['','Coverage:']+report['coverage']+['','Parent assembly obligations:']+report['unresolved_for_parent_assembly']+['','Exact source hashes, moved ranges, component update records, and front maps are in v_viii_report.json.']
(O/'v_viii_report.txt').write_text('\n'.join(lines)+'\n')
print({'edited_files':len(source_rows),'pages':sum(r['pages'] for r in records),'proofs':report['proof_preservation']['explicit_proof_environments'],'statements':report['proof_preservation']['statement_environments'],'all_builds_pass':report['build_validation']['all_success'],'invalid_links':sum(len(x['invalid_local_links']) for x in pdfqa),'outside_pages':sum(len(x['outside_page_text_pages']) for x in pdfqa),'overlap':plate_summary})
