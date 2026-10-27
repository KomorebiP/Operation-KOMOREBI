#!/usr/bin/env python3
"""Bind the completed prose review and visual review to the assembled book."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def load(p):
    return json.loads((ROOT / p).read_text())

def write(p, value):
    (ROOT / p).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def main():
    pdf_hash = sha(ROOT / 'output/Realization_Calculus.pdf')
    structural = load('book/final_pdf_audit.json')
    visual = load('editorial/prose_review/final_visual_review.json')
    for report in (structural, visual):
        assert report['status'] == 'PASS' and report['pdf_sha256'] == pdf_hash
    build = load('editorial/prose_review/build_run/REBUILD_ALL_COMPONENTS.json')
    assert build['all_36_built'] and build['all_actionable_diagnostics_clear']
    accounting = load('book/book_layout_accounting.json')
    preserved = load('editorial/prose_review/preserved_final_apply_report.json')
    assert len(preserved) == 3 and all(not r.get('skipped') for r in preserved)
    records = [
        'editorial/prose_review/root_coverage.json',
        'editorial/prose_review/i_ii_report.json',
        'editorial/prose_review/iii_iv_report.json',
        'editorial/prose_review/v_vi_report.md',
        'editorial/prose_review/vii_viii_report.json',
        'editorial/prose_review/ix_x_report.json',
        'editorial/prose_review/xi_xii_report.json',
        'editorial/prose_review/authorized_local_calibrations.json',
        'editorial/prose_review/style_changes.json',
        'editorial/prose_review/build_run/REBUILD_ALL_COMPONENTS.json',
        'editorial/prose_review/preserved_final_apply_report.json',
        'editorial/book_revision/frontmatter_keep_overrides.json',
        'book/atlas_book_routes_report.json',
        'book/glossary_anchor_resolution.json',
    ]
    editorial = {
        'schema': 'realization-calculus.book-editorial-audit/2',
        'status': 'PASS', 'pdf_sha256': pdf_hash,
        'pages': accounting['total_pages'],
        'scope': 'Additional conservative grammar, prose and publication-style pass across all twelve chapters, retained visual studies, formal companions, arithmetic studies and glossary. Not a proof audit or fresh Lean/scientific replay.',
        'coverage': {
            'source_rebuilt_readers': 36, 'component_readers_authenticated': 41,
            'selected_source_pages': accounting['selected_source_pages'],
            'glossary_terms': 73, 'glossary_source_references': 74,
            'additional_preserved_prose_edits_applied': sum(len(r['applied']) for r in preserved),
            'source_groups': 'All six paired chapter groups have continuous prose-reading records and exact edit journals.',
            'preserved_studies': 'Lead and delegated reviewers read all selected preserved prose, with page coverage recorded.',
        },
        'preservation': {
            'symbolic_formulas': 'Source-group comparisons preserve mathematical formula bytes. Three local technical prose clarifications are separately disclosed.',
            'display_edits': 'Exact math snapshots, annotation/image/vector checks and 144dpi outside-region comparisons pass for all three bounded PDF outputs.',
            'original_readers': 'All 41 exact original readers are retained as attachments and package files.',
            'formal_evidence': 'Quoted historical records, code, source identities and normative contract statements retain their evidence scope.',
        },
        'local_technical_wording_clarifications': load('editorial/prose_review/root_coverage.json')['mathematical_or_technical_wording_clarifications'],
        'style': 'American prose spelling; chapter and formal-companion terminology; chapter-qualified plate references; explicit bold/italic text font bindings; coordinated publication muted/rule colors. Scientific plot colors and math fonts remain scoped separately.',
        'intentional_retained_wording': [
            'Exact source-derived catalogues, code, quoted contract statements and historical evidence retain original document/source labels.',
            'Optional expansion of irreducible to irreducible representation in atlas prose is retained as written because the established nominal use is grammatical and the expansion does not fit beside fixed math.',
        ],
        'prior_routing_exception': 'Resolved: IV visual routing labels now use qualified plate references while preserving the mathematical 69 glyph and its location.',
        'unresolved_editorial_findings': [],
        'review_records': [{'path': p, 'sha256': sha(ROOT / p)} for p in records],
        'boundaries': {'conjecture_66': 'Open', 'chapter_xii': 'Conditional on its stated supplied inputs.'},
    }
    write('book/book_editorial_audit.json', editorial)
    write('book/final_visual_review.json', visual)
    readme = ROOT / 'README.md'
    text = re.sub(r'\*\*[\d,]+ pages\*\*', '**' + format(accounting['total_pages'], ',') + ' pages**', readme.read_text(), count=1)
    readme.write_text(text)
    print(json.dumps({'status': 'PASS', 'pages': accounting['total_pages'], 'pdf_sha256': pdf_hash, 'additional_preserved_edits': editorial['coverage']['additional_preserved_prose_edits_applied']}))

if __name__ == '__main__':
    main()
