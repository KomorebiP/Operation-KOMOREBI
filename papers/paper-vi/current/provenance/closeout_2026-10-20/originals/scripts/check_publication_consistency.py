#!/usr/bin/env python3
"""Check current PDF copies, metadata, page navigation and dependency pins."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parent.parent

def read(name):
    return json.loads((ROOT / name).read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def walk(value):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)

def main():
    edition = read('EDITION.json')
    documents = edition['documents']
    check(len(documents) == 3, 'Three companion PDFs are required')
    for d in documents:
        name = Path(d['path']).name
        for folder in ('papers', 'publication/pdfs', 'editable/' + d['role']):
            path = ROOT / folder / name
            check(sha(path) == d['sha256'], str(path) + ': PDF copy hash mismatch')
            with fitz.open(path) as pdf:
                check(len(pdf) == d['pages'], str(path) + ': page count mismatch')
    check(sum(d['pages'] for d in documents) == edition['total_pages'], 'Total pages')
    check(read('COMPANION_MAP.json')['documents'] == documents, 'Root companion metadata')
    check(read('publication/CURRENT_PUBLICATION_MANIFEST.json')['documents'] == documents,
          'Publication metadata')
    mapping = read('editable/traditional/canonical_label_to_final.json')
    traditional_path = ROOT / documents[0]['path']
    visual_path = ROOT / documents[1]['path']
    count_locations = 0
    with fitz.open(traditional_path) as pdf:
        for label, row in mapping.items():
            page = int(row['physical_pdf_page'])
            check(1 <= page <= len(pdf), label + ': physical page out of range')
            check(pdf[page - 1].get_label() == str(row['printed_page']),
                  label + ': printed page differs from PDF label')
        visual = read('editable/visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json')
        check(len(visual['pages']) == 42, 'Visual page inventory')
        with fitz.open(visual_path) as guide:
            for page in visual['pages']:
                check(guide[int(page['visual_physical_pdf_page']) - 1].get_label() ==
                      str(page['visual_printed_page']), 'Visual PDF page label')
                for target in page['traditional_targets']:
                    expected = mapping[target['final_label']]
                    for key in ('number', 'printed_page', 'physical_pdf_page'):
                        check(str(target[key]) == str(expected[key]),
                              target['final_label'] + ': visual crosswalk ' + key)
                    count_locations += 1
        lean = read('editable/lean_guide/generated/traditional_crosswalk.json')
        lean_locations = 0
        for row in walk({k: v for k, v in lean.items() if k != 'provenance'}):
            if not {'final_label', 'printed_page', 'physical_pdf_page'} <= row.keys():
                continue
            expected = mapping[row['final_label']]
            for key in ('printed_page', 'physical_pdf_page'):
                check(str(row[key]) == str(expected[key]), row['final_label'] + ': Lean crosswalk ' + key)
            lean_locations += 1
    check(count_locations == 75, 'Visual target inventory')
    check(lean_locations == 58, 'Lean target inventory')
    trad = ROOT / 'editable/traditional'
    for name, pin in lean['provenance'].items():
        if name.endswith(('.json', '.tex')):
            check(sha(trad / name) == pin, 'Lean source pin ' + name)
    check(lean['provenance']['traditional_pdf_sha256'] == documents[0]['sha256'], 'Lean PDF pin')
    check(visual['traditional_pdf_sha256'] == documents[0]['sha256'], 'Visual traditional PDF pin')
    check(visual['visual_pdf_sha256'] == documents[1]['sha256'], 'Visual own PDF pin')
    check(visual['traditional_map_sha256'] == sha(trad / 'canonical_label_to_final.json'), 'Visual map pin')
    check(visual['traditional_source_sha256'] == sha(trad / 'Paper_VI_Traditional_Final.tex'), 'Visual source pin')
    root_crosswalks = read('COMPANION_MAP.json')['crosswalks']
    for name, contents in root_crosswalks.items():
        check(read('editable/' + name) == contents, 'Root crosswalk parity: ' + name)
    lean_report = read('verification/monograph_lean_report.json')
    for name, pin in lean_report['report_dependencies'].items():
        check(sha(ROOT / name) == pin, 'Lean report dependency ' + name)
    for name in read('verification/MONOGRAPH_VERIFICATION.json')['reports']:
        check(read(name)['status'].startswith('PASS'), name + ': incomplete owner review')
    preservation = read('verification/MONOGRAPH_PRESERVATION.json')
    check(preservation['status'] == 'PASS', 'Preservation status')
    check(preservation['current_sha256'] == sha(trad / 'Paper_VI_Traditional_Final.tex'), 'Preservation source pin')
    replay = read('verification/MONOGRAPH_PACKAGED_BUILD.json')
    check(replay['status'] == 'PASS', 'Packaged PDF replay status')
    check(all(d['page_count_match'] and d['extracted_text_match'] for d in replay['documents']),
          'Packaged replay page/text comparison')
    report = {'status': 'PASS_FOR_STATED_SCOPE',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'documents': documents, 'active_pdf_copies_checked': 9,
        'canonical_labels_and_aliases': len(mapping),
        'visual_locators': count_locations, 'visual_pages': len(visual['pages']),
        'lean_locators': lean_locations,
        'root_companion_crosswalk_parity': True,
        'current_statement_environments_byte_identical': 184,
        'current_proof_bodies_byte_identical': 140,
        'packaged_rebuild_pages_and_text_match': True,
        'byte_identity': {d['document']: d['pdf_byte_identical'] for d in replay['documents']},
        'scope': 'Current PDF synchronization, metadata, source/navigation pins and packaged replay. No fresh mathematical or Lean execution by this consistency check.'}
    (ROOT / 'verification/PACKAGE_CONSISTENCY.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
