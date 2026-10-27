#!/usr/bin/env python3
"""Verify publication sources, inventories, original-source preservation, and PDFs."""
from pathlib import Path
import collections
import csv
import hashlib
import io
import json
import re
import zipfile
import fitz

ROOT = Path(__file__).resolve().parent
ORIGINAL = ROOT / 'provenance' / 'Komorebi_Sufficient_Resolution_Lean_v0.16.0.zip'
EXPECTED_ORIGINAL = 'ebb2d71a211ea9938c1b223f9858d5636d0973b5aa519244667200646b832ff4'
DOCUMENTS = [
    ('traditional', 'Sufficient_Resolution_Traditional'),
    ('visual', 'Sufficient_Resolution_Visual_Guide'),
    ('lean', 'Sufficient_Resolution_Lean_Guide'),
]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def tex_graph(main):
    seen = set()
    texts = []
    def visit(path):
        path = path.resolve()
        if path in seen:
            return
        if not path.is_relative_to(ROOT):
            raise ValueError(f'TeX source outside the bundle: {path}')
        seen.add(path)
        source = path.read_text(encoding='utf-8')
        source = re.sub(r'(?<!\\)%[^\n]*', '', source)
        texts.append(source)
        for name in re.findall(r'\\(?:input|include)\s*\{([^}]+)\}', source):
            candidate = path.parent / name
            if candidate.suffix == '':
                candidate = candidate.with_suffix('.tex')
            visit(candidate)
    visit(main)
    return '\n'.join(texts), sorted(str(p.relative_to(ROOT)) for p in seen)

def main():
    checks = []
    details = {}
    def check(name, ok, detail=None):
        checks.append({'check': name, 'passed': bool(ok), 'detail': detail})
    check('original_archive_sha256', digest(ORIGINAL) == EXPECTED_ORIGINAL)
    with zipfile.ZipFile(ORIGINAL) as z:
        check('original_archive_crc', z.testzip() is None)
        prefix = 'Komorebi_Sufficient_Resolution_Lean_v0.16.0/'
        source_names = sorted(n for n in z.namelist()
                              if n.startswith(prefix + 'Komorebi/') and n.endswith('.lean'))
        changed = []
        for name in source_names:
            local = ROOT / 'formal' / name[len(prefix):]
            if not local.is_file() or local.read_bytes() != z.read(name):
                changed.append(name[len(prefix):])
        check('93_production_sources_preserved', len(source_names) == 93 and not changed, changed)
        original_index = list(csv.DictReader(io.StringIO(
            z.read(prefix + 'DECLARATION_INDEX_v0.16.0.csv').decode('utf-8'))))
    with (ROOT / 'lean' / 'Declaration_Inventory.csv').open(newline='', encoding='utf-8') as f:
        declarations = list(csv.DictReader(f))
    with (ROOT / 'lean' / 'Module_Inventory.csv').open(newline='', encoding='utf-8') as f:
        modules = list(csv.DictReader(f))
    original_names = {(x['name'], x['kind'], x['file']) for x in original_index}
    release_names = {(x['name'], x['kind'], x['file']) for x in declarations}
    check('declaration_inventory_matches_original', original_names == release_names
          and len(declarations) == 1159)
    check('module_inventory_count', len(modules) == 93)
    module_mismatches = [x['file'] for x in modules
                         if digest(ROOT / 'formal' / x['file']) != x['sha256']]
    check('module_inventory_live_hashes', not module_mismatches, module_mismatches)
    declaration_mismatches = [x['name'] for x in declarations
                              if digest(ROOT / 'formal' / x['file']) != x['source_sha256']]
    check('declaration_inventory_live_hashes', not declaration_mismatches,
          declaration_mismatches)
    kinds = dict(collections.Counter(x['kind'] for x in declarations))
    check('formal_declaration_kind_counts',
          kinds == {'theorem': 998, 'def': 144, 'abbrev': 9, 'structure': 8}, kinds)

    document_labels = {}
    for folder, stem in DOCUMENTS:
        tex = ROOT / folder / (stem + '.tex')
        md = tex.with_suffix('.md')
        pdf = tex.with_suffix('.pdf')
        combined, sources = tex_graph(tex)
        labels = re.findall(r'\\label\s*\{([^}]+)\}', combined)
        references = [part.strip() for group in re.findall(
            r'\\(?:ref|eqref|autoref|cref|Cref)\*?\s*\{([^}]+)\}', combined)
            for part in group.split(',')]
        duplicates = sorted(k for k, v in collections.Counter(labels).items() if v > 1)
        unresolved = sorted(set(references) - set(labels))
        document_labels[folder] = set(labels)
        check(folder + '_unique_labels', not duplicates, duplicates)
        check(folder + '_resolved_references', not unresolved, unresolved)
        source_includes = [name for name in re.findall(
            r'\\includegraphics(?:\[[^\]]*\])?\s*\{([^}]+)\}', combined)
                           if '#' not in name]
        # The visual source uses this known two-argument macro together with
        # graphicspath{figures/}. Check its actual calls, not the #1 template.
        source_includes.extend('figures/' + name + '.pdf' for name in re.findall(
            r'\\guidefig\s*\{([^}]+)\}', combined))
        missing_images = []
        for name in source_includes:
            candidate = tex.parent / name
            options = [candidate] if candidate.suffix else [candidate.with_suffix(s) for s in
                                                          ['.pdf', '.png', '.jpg', '.svg']]
            if not any(p.is_file() for p in options):
                missing_images.append(name)
        check(folder + '_figure_sources_exist', not missing_images, missing_images)
        md_bytes = md.read_bytes()
        controls = [(i, b) for i, b in enumerate(md_bytes) if b < 32 and b not in {9, 10}]
        check(folder + '_markdown_controls', not controls, controls[:10])
        check(folder + '_markdown_present', len(md_bytes) > 1000)
        log = tex.with_suffix('.log')
        warnings = []
        if log.is_file():
            warnings = [line for line in log.read_text(errors='replace').splitlines()
                        if any(s in line for s in ['Overfull', 'undefined references',
                                                  'undefined citations', 'multiply defined'])]
        check(folder + '_no_material_tex_warnings', not warnings, warnings)
        with fitz.open(pdf) as doc:
            outside = []
            for page_number, page in enumerate(doc, 1):
                for block in page.get_text('dict')['blocks']:
                    for line in block.get('lines', []):
                        for span in line['spans']:
                            if not span.get('text', '').strip():
                                continue
                            box = fitz.Rect(span['bbox']) * page.rotation_matrix
                            rect = page.rect
                            if (box.x0 < rect.x0 - 1 or box.y0 < rect.y0 - 1 or
                                box.x1 > rect.x1 + 1 or box.y1 > rect.y1 + 1):
                                outside.append({'page': page_number,
                                                'text': span['text'][:100]})
            check(folder + '_text_inside_pages', not outside, outside[:20])
            pages = len(doc)
        details[folder] = {'pdf': str(pdf.relative_to(ROOT)), 'pages': pages,
                           'bytes': pdf.stat().st_size, 'sha256': digest(pdf),
                           'tex_source_files': sources, 'labels': len(labels),
                           'references': len(references), 'figures': len(source_includes),
                           'unique_figure_sources': len(set(source_includes)),
                           'markdown_bytes': len(md_bytes)}
    concordance_path = ROOT / 'traditional' / 'Claim_Lean_Concordance.json'
    concordance = json.loads(concordance_path.read_text(encoding='utf-8'))
    claims = concordance['claims']
    claim_ids = [x['claim_id'] for x in claims]
    check('64_unique_principal_claim_groups', len(claim_ids) == 64
          and len(set(claim_ids)) == 64)
    known_declarations = {x['name'] for x in declarations}
    bad_anchors = []
    bad_labels = []
    empty_scope = []
    missing_printed_scope = []
    traditional_tex = (ROOT / 'traditional' / 'Sufficient_Resolution_Traditional.tex').read_text(encoding='utf-8')
    for claim in claims:
        if not claim.get('hypotheses') or not claim.get('domain'):
            empty_scope.append(claim['claim_id'])
        if not claim.get('anchors'):
            bad_anchors.append((claim['claim_id'], 'NO_ANCHORS'))
        for anchor in claim.get('anchors', []):
            if anchor['name'] not in known_declarations:
                bad_anchors.append((claim['claim_id'], anchor['name']))
            p = ROOT / 'formal' / anchor['file']
            if not p.is_file() or digest(p) != anchor['source_sha256']:
                bad_anchors.append((claim['claim_id'], 'SOURCE_HASH'))
        if claim.get('document_label') not in document_labels['traditional']:
            bad_labels.append(claim['claim_id'])
        printed = claim.get('hypotheses_tex')
        if not printed or printed not in traditional_tex:
            missing_printed_scope.append(claim['claim_id'])
    check('principal_claim_declarations_and_hashes', not bad_anchors, bad_anchors)
    check('principal_claim_document_labels', not bad_labels, bad_labels)
    check('principal_claim_explicit_domains_and_hypotheses', not empty_scope, empty_scope)
    check('principal_claim_hypotheses_printed_in_manuscript', not missing_printed_scope
          and traditional_tex.count(r'\textbf{Hypotheses.}') == 64, missing_printed_scope)
    traditional_md = (ROOT / 'traditional' / 'Sufficient_Resolution_Traditional.md').read_text(encoding='utf-8')
    check('principal_claim_hypotheses_preserved_in_markdown',
          traditional_md.count('**Hypotheses.**') == 64)
    check('16_blocks_present', {int(x['block']) for x in claims} == set(range(1, 17)))
    lean_claims = json.loads((ROOT / 'lean' / 'Claim_Lean_Concordance.json').read_text(encoding='utf-8'))
    lean_by_id = {x['claim_id']: x for x in lean_claims}
    stale_mapping = []
    for claim in claims:
        other = lean_by_id.get(claim['claim_id'])
        if other is None or (other['formula_tex'] != claim['statement_tex'] or
                             other['hypotheses'] != claim['hypotheses'] or
                             other['hypotheses_tex'] != claim['hypotheses_tex'] or
                             other['declarations'] != [a['name'] for a in claim['anchors']]):
            stale_mapping.append(claim['claim_id'])
    check('lean_claim_map_matches_current_manuscript', not stale_mapping
          and len(lean_claims) == 64, stale_mapping)
    mapping_audit = json.loads((ROOT / 'lean' / 'CLAIM_MAPPING_AUDIT.json').read_text())
    check('lean_claim_map_live_concordance_hash',
          mapping_audit['input_sha256'] == digest(concordance_path))
    visual_crosswalk = json.loads((ROOT / 'visual' / 'validation' / 'claim_crosswalk.json').read_text())
    check('visual_covers_all_principal_claim_groups',
          visual_crosswalk['traditional_groups_covered'] == [f'SR-{i:02d}' for i in range(1, 65)])
    evidence = json.loads((ROOT / 'verification' / 'FINAL_EVIDENCE_VALIDATION.json').read_text())
    stale_evidence = [x['manifest'] for x in evidence['records']
                      if digest(ROOT / x['manifest']) != x['manifest_sha256']]
    check('18_current_evidence_manifests_validated', evidence['status'] == 'PASS'
          and len(evidence['records']) == 18 and not stale_evidence, stale_evidence)
    execution = json.loads((ROOT / 'verification' / 'CURRENT_RELEASE_VERIFICATION.json').read_text())
    passed = all(x['passed'] for x in checks)
    record = {'status': 'PASS_DOCUMENT_AND_SOURCE_INTEGRATION' if passed else 'FAIL',
              'scope': 'Publication source, inventory, hash and PDF-bound checks; no new formal proof.',
              'documents': details, 'total_pdf_pages': sum(x['pages'] for x in details.values()),
              'principal_claim_groups': len(claims), 'formal_declarations': len(declarations),
              'production_modules': len(modules), 'checks': checks,
              'fresh_python': {k: execution['fresh_python'][k] for k in
                               ['status', 'suite_count', 'native_counted_assertions',
                                'additional_fixed_sanity_groups',
                                'additional_main_mathematical_assert_statements']},
              'evidence_manifests': {'base_records': 17, 'visual_example_records': 1,
                                     'total': len(evidence['records']),
                                     'verification': 'verification/FINAL_EVIDENCE_VALIDATION.json',
                                     'assertion_counts_merged': False},
              'fresh_lean': execution['fresh_lean']}
    (ROOT / 'PUBLICATION_AUDIT.json').write_text(json.dumps(record, indent=2) + '\n',
                                               encoding='utf-8')
    print(json.dumps({'status': record['status'], 'checks': len(checks),
                      'failed': [x for x in checks if not x['passed']],
                      'total_pdf_pages': record['total_pdf_pages']}))
    if not passed:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
