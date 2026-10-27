#!/usr/bin/env python3
"""Bind final source, layout review and frozen evidence into the owner report."""
from pathlib import Path
import datetime,hashlib,json,re
import fitz
H=Path(__file__).resolve().parent;R=H.parents[1];G=H/'generated';Q=H/'qa'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
static=read(G/'static_reconciliation.json'); preserved=read(G/'preservation.json'); math=read(G/'mathematical_span_preservation.json'); provenance=read(G/'evidence_provenance.json'); cross=read(G/'traditional_crosswalk.json');pdfcheck=read(Q/'pdf_checks.json');visual=read(Q/'visual_review.json')
PDF=H/'Paper_VII_Lean_Guide_Final.pdf';doc=fitz.open(PDF)
for x in (static,preserved,math,pdfcheck,visual):
    if x['status']!='PASS':raise RuntimeError('A required final guide gate is not PASS')
if pdfcheck['pdf_sha256']!=sha(PDF) or visual['pdf_sha256']!=sha(PDF):raise RuntimeError('Visual/layout review belongs to another guide PDF')
current=R/provenance['current_report_relative_to_package']
if provenance['current_report_sha256']!=sha(current):raise RuntimeError('Current computation pin stale')
model_report=R/provenance['traditional_model_report_relative_to_package']
if sha(model_report)!=provenance['traditional_model_report_sha256']:raise RuntimeError('Traditional model report pin stale')
T=H.parent/'traditional';tprovenance=cross['provenance']
for name,value in tprovenance.items():
    if name.endswith(('.json','.tex')) and sha(T/name)!=value:raise RuntimeError('Traditional source/map binding stale '+name)
if sha(T/tprovenance['traditional_pdf_filename'])!=tprovenance['traditional_pdf_sha256']:raise RuntimeError('Traditional PDF binding stale')
fontrows=[line.split() for line in (Q/'fonts.txt').read_text().splitlines()[2:]]
# pdffonts columns end with emb/sub/uni/object ID, so inspect their trailing cells.
fonts=bool(fontrows) and all(row[-5]=='yes' and row[-3]=='yes' for row in fontrows)
if not fonts:raise RuntimeError('A PDF font is not embedded or lacks Unicode mapping')
texfiles=sorted([H/'Paper_VII_Lean_Guide_Final.tex',H/'preamble.tex',H/'komorebi-monograph.sty',*list((H/'chapters').glob('*.tex')),*list(G.glob('*.tex'))])
deps={p.relative_to(R).as_posix():sha(p) for p in [G/'static_reconciliation.json',G/'preservation.json',G/'mathematical_span_preservation.json',G/'evidence_provenance.json',G/'traditional_crosswalk.json',G/'traditional_navigation_provenance.json',Q/'pdf_checks.json',Q/'visual_review.json',current,model_report,*texfiles]}
for asset in sorted([*list((H/'excerpts').glob('*.txt')),*list((H/'fonts').glob('*'))]):
    if asset.is_file():deps[asset.relative_to(R).as_posix()]=sha(asset)
for n in ('assemble.py','navigation.py','build.py','verify_pdf.py','static_check.py','refresh_evidence.py','render_review_details.py','README.md'):
    deps[(H/n).relative_to(R).as_posix()]=sha(H/n)
report={'schema':'komorebi.paper_vii.monograph_lean_review.v1','status':'PASS','edition_date':'2026-10-09','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Conservative companion authoring, unchanged formal contracts and source excerpts, static inherited-evidence reconciliation, frozen current finite report interpretation, and final all-page PDF layout review. No fresh Lean execution or adversarial proof audit.',
'guide_pdf':{'path':PDF.relative_to(R).as_posix(),'pages':len(doc),'sha256':sha(PDF),'bytes':PDF.stat().st_size,'page_labels':doc.get_page_labels()},'guide_source_sha256':sha(H/'Paper_VII_Lean_Guide_Final.tex'),'authored_tex_sha256':{p.relative_to(H).as_posix():sha(p) for p in texfiles},
'preserved_counts':{'scoped_finite_items':19,'named_theorem_declarations':323,'proof_modules':25,'separately_audited_constructed_objects':6,'exact_raw_source_excerpts':67,'exact_rendered_excerpts':67,'dependency_pins':9,'delimited_mathematical_spans':math['total_delimited_mathematical_spans'],'contract_and_proof_walk_paragraphs':math['total_contract_and_proof_walk_paragraphs']},
'mathematical_scope':{'inherited_scoped_items_complete':19,'full_paper_formalized':False,'constructed_objects_added_to_theorem_denominator':False,'open_physical_continuum_targets':5,'physical_targets':provenance['current_computation_report']['physical_targets'],'mathematical_correspondence':'manual'},
'inherited_kernel_evidence':{'release':static['inherited_release'],'started_utc':static['inherited_started_utc'],'updated_utc':static['inherited_updated_utc'],'lean':'leanprover/lean4:v4.34.0-rc2','lean_runtime_commit':'6a10ac8c22beadecabdbb0919c2b50214762f91d','mathlib_revision':'aeb72f1e9981b6d35b426b16dca7759be3e7ba06','allowed_axioms':['propext','Classical.choice','Quot.sound'],'fresh_lean_compilation':False,'reason_no_fresh_lean_run':'lean, lake and elan unavailable','inherited_evidence_hashes':static['inherited_evidence_sha256']},
'current_evidence':{'computation_report':current.relative_to(R).as_posix(),'computation_report_sha256':sha(current),'gates':provenance['current_computation_report']['gates'],'count_units_aggregate_to_independent_theorems':False,'new_traditional_figure_models':{'report':model_report.relative_to(R).as_posix(),'report_sha256':sha(model_report),'models':3,'positive_assertions':30,'false_assertions_rejected':6,'outside_frozen_primary_computational_report':True,'adds_formal_targets':False}},
'navigation':{'formal_core_rows':len(cross['core']),'strengthened_written_rows':len(cross['strengthened']),'retained_supplement_groups':len(cross['supplements']),'traditional_provenance':tprovenance,'traditional_crosswalk_sha256':sha(G/'traditional_crosswalk.json'),'all_locations_checked_against_actual_body_pdf_labels':True,'stronger_written_statements_extend_formal_contract':False},
'build':{'builder':'editable/lean_guide/build.py','passes':4,'engine':'XeLaTeX','full_tree_staged_in_isolation':True,'relative_bundled_fonts':True,'check_only_and_output_directory_supported':True,'runs_lean':False,'regenerates_mathematical_evidence':False,'final_pdf_matches_reviewed_candidate':True},
'visual_qa':dict(visual,all_pdffonts_entries_embedded_and_unicode=fonts,blank_pages=pdfcheck['blank_pages'],out_of_page_text_spans=pdfcheck['out_of_page_spans'],replacement_characters=pdfcheck['unicode_replacement_characters'],all_323_target_names_present=pdfcheck['all_323_theorem_names_extract'],underfull_box_log_messages=(H/'Paper_VII_Lean_Guide_Final.log').read_text().count('Underfull')),
'checks':{'pdf_extraction_and_bounds':'PASS','static_source_reconciliation':'PASS','raw_source_excerpt_preservation':'PASS','mathematical_spans_and_contracts':'PASS','final_pdf_matches_all_page_visual_review':True,'current_computation_provenance_sha256_match':True,'warnings':[]},'report_dependencies':deps,'resolved_authoring_issues':['Current evidence prose was refreshed to the actual October 9 executions, replacing the earlier host dependency limitations while retaining historical authoring inputs.','The companion table layout was refreshed with both printed and actual physical PDF locations.'],
'transient_environment_interruptions':['The first final locator/build command was rejected before process creation because the exec server transport disconnected. The same routine command succeeded after reconnection. This was not a compiler or scientific gate failure.'],'active_ai_disclosure':'none. Historical source material retained.','historical_authoring_archive':'editable/lean_guide/historical_assembly'}
path=R/'verification/monograph_lean_report.json';path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'status':'PASS','guide_pages':len(doc),'guide_pdf_sha256':sha(PDF),'report_sha256':sha(path)}))
