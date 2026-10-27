#!/usr/bin/env python3
"""Bind publication acceptance to exact PDF/source and accepted formal evidence."""
from pathlib import Path
from collections import Counter
import hashlib,json

root=Path(__file__).resolve().parents[1]
run=root.parent/'budget_v1.10.0/integration/runs/clean_budget_01'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
formal=read(run/'receipt.json')
post=read(run/'postflight.json')
assert formal['status']=='PASS' and post['status']=='PASS'
assert post['run_receipt_sha256']==sha(run/'receipt.json')
assert all(c['passed'] for c in formal['commands'])
build_path=root/'audit/final_candidate_003/receipt.json'
build=read(build_path)
source={str(p.relative_to(root/'source')):sha(p) for p in sorted((root/'source').rglob('*')) if p.is_file()}
assert build['status']=='PASS' and source==build['source_sha256']
pdf=root/'publication/Komorebi_Space_Monograph.pdf'
visual=read(root/'audit/FINAL_VISUAL_COVERAGE.json')
assert visual['status']=='PASS' and visual['full_page_coverage']
assert sha(pdf)==visual['pdf_sha256']==build['pdf_sha256']
structure=read(root/'reviews/STRUCTURAL_CHECK.json')
assert structure['status']=='PASS'
assert all(source[n]==v for n,v in structure['source_sha256'].items())
changes=read(root/'audit/SOURCE_CHANGES.json')
assert source==changes['source_sha256']
assert not any(c['path'].startswith('figures/') for c in changes['changed'])
assert source['chapters/05g_budget_certificates.tex']=='1869172bd3afba714e3ed12ef8ff3781bc1da2686e7071b8856033d27aeb5591'
assert source['chapters/11_written_extensions.tex']=='a811d4230d5d681220061ad8ab8bb10042a812e2b5bddac51a44725b2b2ea682'
counts=dict(Counter(c['kind'] for c in formal['controls']))
assert counts=={'positive':8,'negative':20,'policy':2}
assert formal['production_modules']==148 and formal['compile_targets']==151
assert formal['axiom_declarations']==4935 and formal['new_axiom_declarations']==63
assert formal['explicit_theorem_lemma_count']==1619
report=root/'reviews/PROOFREADING_REPORT.md'
text=report.read_text().replace('Its formal acceptance and final rendered coverage are recorded in `PUBLICATION_VERIFICATION.json` once the release gates pass.',
    'Its formal acceptance and final rendered coverage are recorded in `PUBLICATION_VERIFICATION.json`. The clean replay and independent postflight both passed.')
report.write_text(text)
out={'status':'PASS','version':'1.10.0','release_kind':'WR03–WR05 formal budget continuation and full-monograph synchronization',
    'pdf_sha256':sha(pdf),'pdf_pages':visual['page_count'],'source_sha256':source,
    'formal_receipt_path':str(run.relative_to(root.parent)/'receipt.json'),
    'formal_receipt_sha256':sha(run/'receipt.json'),'formal_postflight_sha256':sha(run/'postflight.json'),
    'production_modules':148,'roots':3,'compile_targets':151,'audited_declarations':4935,
    'new_audited_declarations':63,'explicit_theorem_lemma_count':1619,'new_explicit_theorem_lemma_count':39,
    'control_counts':counts,'controls_total':30,'formal_commands':len(formal['commands']),
    'axiom_union':formal['axiom_union'],'clean_project_replay':formal['clean_project_build'],
    'build_receipt_sha256':sha(build_path),'structure_receipt_sha256':sha(root/'reviews/STRUCTURAL_CHECK.json'),
    'visual_coverage_sha256':sha(root/'audit/FINAL_VISUAL_COVERAGE.json'),
    'proofreading_report_path':'reviews/PROOFREADING_REPORT.md','proofreading_report_sha256':sha(report),
    'independent_changed_passages_review_sha256':sha(root/'reviews/INDEPENDENT_CHANGED_PASSAGES_CHECK.md'),
    'source_change_manifest_sha256':sha(root/'audit/SOURCE_CHANGES.json'),
    'source_diff_sha256':sha(root/'audit/MANUSCRIPT_CHANGES.diff'),
    'underfull_diagnostics_count':len(build['underfull_diagnostics']),
    'all_fonts_embedded':visual['all_fonts_embedded'],'out_of_page_words':visual['out_of_page_words'],
    'proofreading_scope':'Changed edition/evidence passages, new declaration map, and one image/residual erratum, with surrounding context. The v1.9.0 full proofreading remains preserved.',
    'figures_unchanged':True,'included_plates':structure['counts']['monograph_plates'],
    'reproducible_png_intermediates_omitted_from_release':True,
    'lean_executed_for_formal_continuation':True,'lean_executed_by_pdf_build':False,
    'historical_finite_suites_rerun':False,
    'wr_complete':['WR01','WR02','WR03','WR04','WR05','WR06','WR07','WR13','WR14'],
    'wr_partial':['WR09','WR16'],'wr_written_only':['WR08','WR10','WR11','WR12','WR15'],
    'not_claimed':['Independent rebuild of mathlib','Another full-monograph theorem-by-theorem referee audit','Fresh historical finite-suite execution','New full proofreading of historical companion guides']}
(root/'PUBLICATION_VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='source_sha256'},indent=2))
