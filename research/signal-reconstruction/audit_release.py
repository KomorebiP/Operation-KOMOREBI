#!/usr/bin/env python3
"""Audit publication integration and preserved evidence; this is not a proof checker."""
from pathlib import Path
import collections
import hashlib
import json
import re
import fitz

ROOT = Path(__file__).resolve().parent
DOCUMENTS = {
    'traditional': 'Signal_Reconstruction_Traditional',
    'visual': 'Signal_Reconstruction_Visual_Guide',
    'lean': 'Signal_Reconstruction_Lean_Guide',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def tex_graph(main):
    seen, contents = set(), []
    def visit(path):
        path = path.resolve()
        if path in seen:
            return
        if not path.is_relative_to(ROOT):
            raise ValueError(f'TeX input outside this bundle: {path}')
        seen.add(path)
        source = path.read_text(encoding='utf-8')
        contents.append(re.sub(r'(?<!\\)%[^\n]*', '', source))
        for name in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}', source):
            if '#' in name:
                continue
            candidate = path.parent / name
            visit(candidate if candidate.suffix else candidate.with_suffix('.tex'))
    visit(main)
    return '\n'.join(contents), [p.relative_to(ROOT).as_posix() for p in sorted(seen)]

def main():
    checks, documents = [], {}
    def check(name, passed, detail=None):
        checks.append({'check': name, 'passed': bool(passed), 'detail': detail})

    preservation = json.loads((ROOT / 'verification/SOURCE_PRESERVATION.json').read_text())
    originals = [f for group in preservation['sources'] for f in group['files']]
    changed = [f['release_path'] for f in originals
               if not (ROOT / f['release_path']).is_file()
               or digest(ROOT / f['release_path']) != f['sha256']]
    check('preserved_signal_payload_hashes', not changed, {'payloads': len(originals), 'changed': changed})
    related = json.loads((ROOT / 'provenance/PAPER_V_CHECKED_CHECKPOINT.json').read_text())
    changed_related = [f['release_path'] for f in related['copied_payloads']
                       if not (ROOT / f['release_path']).is_file()
                       or digest(ROOT / f['release_path']) != f['sha256']]
    check('preserved_related_formal_payload_hashes', not changed_related,
          {'payloads': len(related['copied_payloads']), 'changed': changed_related})
    check('malformed_latest_archive_failure_disclosed',
          (ROOT / 'provenance/PAPER_V_FINAL_ARCHIVE_FAILURE.json').is_file())

    label_sets, tex_sources = {}, {}
    for folder, stem in DOCUMENTS.items():
        tex = ROOT / folder / (stem + '.tex')
        md, pdf = tex.with_suffix('.md'), tex.with_suffix('.pdf')
        combined, inputs = tex_graph(tex)
        tex_sources[folder] = combined
        labels = re.findall(r'\\label\s*\{([^}]+)\}', combined)
        label_sets[folder] = set(labels)
        duplicate = sorted(k for k, v in collections.Counter(labels).items() if v > 1)
        references = [part.strip() for group in re.findall(
            r'\\(?:ref|eqref|autoref|cref|Cref)\*?\s*\{([^}]+)\}', combined)
            for part in group.split(',')]
        unresolved = sorted(set(references) - set(labels))
        check(folder + '_unique_labels', not duplicate, duplicate)
        check(folder + '_resolved_cross_references', not unresolved, unresolved)
        data = md.read_bytes()
        controls = [(i, b) for i, b in enumerate(data) if b < 32 and b not in {9, 10}]
        check(folder + '_markdown_present_and_clean', len(data) > 1000 and not controls,
              {'bytes': len(data), 'control_characters': controls[:10]})
        log = tex.with_suffix('.log')
        warnings = [line for line in log.read_text(errors='replace').splitlines()
                    if any(term in line for term in ['Overfull', 'undefined references',
                       'undefined citations', 'multiply defined'])] if log.is_file() else ['Missing build log']
        check(folder + '_no_material_tex_warnings', not warnings, warnings)
        with fitz.open(pdf) as doc:
            outside, empty = [], []
            for number, page in enumerate(doc, 1):
                if not page.get_text().strip():
                    empty.append(number)
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines', []):
                        for span in line['spans']:
                            if not span.get('text', '').strip():
                                continue
                            box = fitz.Rect(span['bbox']) * page.rotation_matrix
                            rect = page.rect
                            if (box.x0 < rect.x0 - 1 or box.y0 < rect.y0 - 1
                                or box.x1 > rect.x1 + 1 or box.y1 > rect.y1 + 1):
                                outside.append({'page': number, 'text': span['text'][:100]})
            check(folder + '_text_within_pages', not outside, outside[:20])
            check(folder + '_no_empty_text_pages', not empty, empty)
            pages = len(doc)
        documents[folder] = {'path': pdf.relative_to(ROOT).as_posix(), 'pages': pages,
                             'bytes': pdf.stat().st_size, 'sha256': digest(pdf),
                             'tex_inputs': inputs, 'labels': len(labels),
                             'references': len(references), 'markdown_bytes': len(data)}

    concordance_file = ROOT / 'traditional/Claim_Concordance.json'
    concordance = json.loads(concordance_file.read_text())
    claims = concordance['claims'] if isinstance(concordance, dict) else concordance
    ids = [c['claim_id'] for c in claims]
    check('principal_claim_ids_unique', len(ids) > 0 and len(set(ids)) == len(ids), {'count': len(ids)})
    scope_missing, labels_missing, anchors_bad, printed_missing, dependencies_bad = [], [], [], [], []
    for claim in claims:
        cid = claim['claim_id']
        if not claim.get('domain') or not claim.get('hypotheses'):
            scope_missing.append(cid)
        if claim.get('document_label') not in label_sets['traditional']:
            labels_missing.append(cid)
        if claim.get('hypotheses_tex', claim.get('hypotheses')) not in tex_sources['traditional']:
            printed_missing.append(cid)
        for dependency in claim.get('dependencies', []):
            if dependency not in ids:
                dependencies_bad.append({'claim': cid, 'dependency': dependency})
        for anchor in claim.get('source_anchors', claim.get('anchors', [])):
            path_value = anchor.get('path', anchor.get('file', anchor.get('source_path')))
            hash_value = anchor.get('sha256', anchor.get('source_sha256'))
            if not path_value or not hash_value or not (ROOT / path_value).is_file():
                anchors_bad.append({'claim': cid, 'anchor': anchor})
            elif digest(ROOT / path_value) != hash_value:
                anchors_bad.append({'claim': cid, 'path': path_value, 'reason': 'hash mismatch'})
    check('principal_claim_domains_and_hypotheses', not scope_missing, scope_missing)
    check('principal_claim_document_labels', not labels_missing, labels_missing)
    check('principal_claim_anchor_hashes', not anchors_bad, anchors_bad)
    check('principal_claim_hypotheses_printed', not printed_missing, printed_missing)
    check('principal_claim_dependencies_exist', not dependencies_bad, dependencies_bad)
    check('principal_claim_markdown_ids',
          all(cid in (ROOT / 'traditional/Signal_Reconstruction_Traditional.md').read_text() for cid in ids))
    lean_map = json.loads((ROOT / 'lean/Claim_Lean_Concordance.json').read_text())
    lean_by_id = {c['claim_id']: c for c in lean_map['claims']}
    stale_claims = []
    for claim in claims:
        counterpart = lean_by_id.get(claim['claim_id'])
        if counterpart is None or any(counterpart.get(field) != claim.get(field)
                                      for field in ['title', 'statement_tex', 'hypotheses', 'hypotheses_tex', 'domain']):
            stale_claims.append(claim['claim_id'])
    check('lean_concordance_exact_live_claim_fields', not stale_claims and set(lean_by_id) == set(ids), stale_claims)
    check('lean_concordance_live_input_hash', lean_map['traditional_claim_input_sha256'] == digest(concordance_file))
    inventory = json.loads((ROOT / 'lean/Related_Declaration_Inventory.json').read_text())
    declarations = {d['name']: d for d in inventory}
    bad_declarations = []
    for counterpart in lean_map['claims']:
        for anchor in counterpart['related_declarations']:
            item = declarations.get(anchor['declaration'])
            source = ROOT / anchor['file']
            if (item is None or item['file'] != anchor['file']
                or item['source_sha256'] != anchor['source_sha256']
                or digest(source) != anchor['source_sha256']
                or anchor['source_quoted'] not in source.read_text()):
                bad_declarations.append({'claim': counterpart['claim_id'], 'declaration': anchor['declaration']})
    check('lean_concordance_related_source_anchors', not bad_declarations, bad_declarations)
    literal_anchors = json.loads((ROOT / 'lean/SOURCE_ANCHORS.json').read_text())['anchors']
    literal_bad = []
    for anchor in literal_anchors:
        source = ROOT / anchor['file']
        quoted = '\n'.join(source.read_text().splitlines()[anchor['start_line'] - 1:anchor['end_line']])
        if digest(source) != anchor['source_sha256'] or quoted != anchor['source_quoted']:
            literal_bad.append(anchor['anchor_id'])
    check('lean_guide_literal_source_excerpts', not literal_bad, {'anchors': len(literal_anchors), 'mismatches': literal_bad})
    mapping_audit = json.loads((ROOT / 'lean/CLAIM_MAPPING_AUDIT.json').read_text())
    check('lean_coverage_is_scoped', mapping_audit['full_signal_claims_formally_covered'] == 0
          and mapping_audit['fresh_lean_execution'] is False)
    crosswalk = json.loads((ROOT / 'visual/validation/claim_crosswalk.json').read_text())
    check('visual_crosswalk_current_catalogue_hash',
          crosswalk['source_concordance_sha256'] == digest(concordance_file))
    check('visual_crosswalk_covers_all_claims', set(crosswalk['traditional_groups_covered']) == set(ids)
          and {r['claim_id'] for r in crosswalk['rows']} == set(ids))
    bad_visual_labels = [r['claim_id'] for r in crosswalk['rows']
                         if r['document_label'] not in label_sets['visual']]
    check('visual_crosswalk_labels_exist', not bad_visual_labels, bad_visual_labels)
    execution_file = ROOT / 'verification/CURRENT_RELEASE_VERIFICATION.json'
    execution = json.loads(execution_file.read_text())
    check('current_bounded_verification_record_present', bool(execution))
    active = execution['active_suites']
    bad_execution_hashes = []
    for suite in active:
        for field in ['manifest', 'scientific_result']:
            if digest(ROOT / suite[field]) != suite[field + '_sha256']:
                bad_execution_hashes.append({'suite': suite['suite'], 'field': field})
    check('active_evidence_live_hashes', not bad_execution_hashes, bad_execution_hashes)
    check('active_suite_names_unique', len({s['suite'] for s in active}) == len(active))
    check('active_check_counts_consistent',
          sum(s['recorded_checks'] for s in active) == execution['recorded_check_count']
          and sum(s['counted_unique_checks'] for s in active) == execution['deduplicated_recorded_check_count'])
    validation = json.loads((ROOT / 'verification/FINAL_EVIDENCE_VALIDATION.json').read_text())
    stale_validation = [r['manifest'] for r in validation['records']
                        if digest(ROOT / r['manifest']) != r['manifest_sha256']]
    check('all_v2_evidence_records_validated', validation['status'] == 'PASS' and not stale_validation,
          {'records': validation['record_count'], 'stale': stale_validation})
    historical_status = ROOT / 'visual/validation/HISTORICAL_RUN_STATUS.json'
    check('evidence_historical_root_declaration_current',
          validation.get('historical_root_declaration_sha256') == digest(historical_status))
    traditional_review = json.loads((ROOT / 'reviews/FINAL_TRADITIONAL_AUDIT.json').read_text())
    visual_review = json.loads((ROOT / 'reviews/FINAL_VISUAL_AUDIT.json').read_text())
    lean_review = json.loads((ROOT / 'reviews/FINAL_LEAN_AUDIT.json').read_text())
    review_stale = []
    for review, entries in [('traditional', traditional_review['artifacts']),
                            ('visual', visual_review['final_artifacts'])]:
        review_stale.extend({'review': review, 'path': entry['path']} for entry in entries
                            if digest(ROOT / entry['path']) != entry['sha256'])
    review_stale.extend({'review': 'lean', 'path': path}
                        for path, sha in lean_review['frozen_artifacts'].items()
                        if digest(ROOT / path) != sha)
    check('independent_review_bindings_current', not review_stale, review_stale)
    lean = json.loads((ROOT / 'verification/FRESH_LEAN_STATUS.json').read_text())
    check('fresh_lean_scope_explicit', lean['fresh_signal_lean_check'] is False)
    result = {'status': 'PASS_DOCUMENT_AND_SOURCE_INTEGRATION' if all(c['passed'] for c in checks) else 'FAIL',
              'scope': 'Publication, hash, label, PDF-bound and evidence-presence checks; no new formal proof.',
              'documents': documents, 'total_pdf_pages': sum(d['pages'] for d in documents.values()),
              'principal_claim_groups': len(claims), 'preserved_signal_payloads': len(originals),
              'preserved_related_formal_payloads': len(related['copied_payloads']),
              'checks': checks, 'fresh_lean': lean,
              'claim_concordance_sha256': digest(concordance_file),
              'bounded_verification_sha256': digest(execution_file)}
    (ROOT / 'PUBLICATION_AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks),
                      'total_pdf_pages': result['total_pdf_pages'],
                      'failed': [c for c in checks if not c['passed']]}))
    if result['status'] == 'FAIL':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
