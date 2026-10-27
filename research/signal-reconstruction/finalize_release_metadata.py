#!/usr/bin/env python3
"""Record the final publication counts after all integration checks pass."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

def read(path):
    return json.loads((ROOT / path).read_text())

def main():
    audit = read('PUBLICATION_AUDIT.json')
    if audit['status'] != 'PASS_DOCUMENT_AND_SOURCE_INTEGRATION':
        raise RuntimeError('Publication integration audit must pass before final metadata is recorded')
    execution = read('verification/CURRENT_RELEASE_VERIFICATION.json')
    visual = read('visual/validation/PUBLICATION_QA.json')
    formal = read('lean/INVENTORY_AUDIT.json')
    record = {
        'status': 'FINAL_PUBLICATION_EDITION_WITH_SCOPED_EVIDENCE',
        'title': 'Signal Reconstruction: Polyphase Sampling, Unknown Edges, and Self-Calibration',
        'author': 'Komorebi P.', 'edition': '2026-10-06',
        'documents': audit['documents'], 'total_pdf_pages': audit['total_pdf_pages'],
        'principal_result_groups': audit['principal_claim_groups'],
        'visual_figures': visual['figure_count'],
        'markdown_companions_included': all((ROOT / folder / stem).is_file() for folder, stem in [
            ('traditional', 'Signal_Reconstruction_Traditional.md'),
            ('visual', 'Signal_Reconstruction_Visual_Guide.md'),
            ('lean', 'Signal_Reconstruction_Lean_Guide.md')]),
        'source_verification': {
            'active_scoped_suites': execution['active_suite_count'],
            'recorded_checks': execution['recorded_check_count'],
            'deduplicated_checks': execution['deduplicated_recorded_check_count'],
            'observed_identification_failures': execution['observed_recovery_failures'],
            'interpretation': execution['counting_convention'],
        },
        'visual_finite_controls': {
            'recorded_checks': visual['exact_finite_assertions'],
            'counts_merged_with_source_verification': False,
        },
        'evidence_record_validation': read('verification/FINAL_EVIDENCE_VALIDATION.json'),
        'source_payloads_preserved': audit['preserved_signal_payloads'],
        'related_formal_payloads_preserved': audit['preserved_related_formal_payloads'],
        'related_formal_inventory': formal,
        'fresh_signal_lean': read('verification/FRESH_LEAN_STATUS.json'),
        'full_signal_claims_formally_covered': 0,
        'mathematical_review': read('reviews/FINAL_TRADITIONAL_AUDIT.json')['primary_verdict'],
        'mathematical_review_limit': 'The 46 printed implications under their explicit hypotheses; no global novelty or unconditional algorithm reliability claim.',
        'visual_review': read('reviews/FINAL_VISUAL_AUDIT.json')['verdict'],
        'lean_correspondence_review': read('reviews/FINAL_LEAN_AUDIT.json')['verdict'],
        'later_paper_v_archive': 'Two downloaded copies failed ZIP validation; checked v1.1.0 checkpoint supplies related sources.',
        'external_repository_publication': False,
        'machine_native_edition': 'deferred',
    }
    (ROOT / 'RELEASE_STATUS.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'status': record['status'], 'pages': record['total_pdf_pages'],
                      'result_groups': record['principal_result_groups']}))

if __name__ == '__main__':
    main()
