#!/usr/bin/env python3
"""Read-only verification of the current proofreading release.

Checks synchronized PDFs, actual page navigation, approved source/evidence
pins, proof-preservation records and the packaged PDF replay. Historical
October 9 reports retain their dates and are not treated as current runs.
Use --report PATH to write a fresh report outside the frozen package.
No mathematical experiment or Lean compiler is invoked by this command.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import sys
import fitz

ROOT = Path(__file__).resolve().parent.parent
CURRENT = 'verification/proofread_2026-10-18/'


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
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def verify():
    edition = read('EDITION.json')
    docs = edition['documents']
    check([d['role'] for d in docs] == ['traditional', 'visual_guide', 'lean_guide'],
          'Three ordered companion documents required')
    for d in docs:
        for folder in ['papers', 'publication/pdfs', 'editable/' + d['role']]:
            path = ROOT / folder / Path(d['path']).name
            check(sha(path) == d['sha256'], str(path) + ': PDF copy hash')
            check(path.stat().st_size == d['bytes'], str(path) + ': PDF byte size')
            with fitz.open(path) as pdf:
                check(len(pdf) == d['pages'], str(path) + ': page count')
    check(sum(d['pages'] for d in docs) == edition['total_pages'], 'Total pages')
    for name in ['COMPANION_MAP.json', 'publication/CURRENT_PUBLICATION_MANIFEST.json',
                 'SERIES_STATUS.json']:
        check(read(name)['documents'] == docs, name + ': document metadata parity')
    trad = ROOT / 'editable/traditional'
    mapping = read('editable/traditional/canonical_label_to_final.json')
    visual = read('editable/visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json')
    lean = read('editable/lean_guide/generated/traditional_crosswalk.json')
    check(read('CURRENT_PUBLICATION_LOCATORS.json')['canonical_labels'] == mapping,
          'Root canonical locator parity')
    visual_targets = lean_targets = 0
    with fitz.open(ROOT / docs[0]['path']) as pdf:
        for label, row in mapping.items():
            page = int(row['physical_pdf_page'])
            check(1 <= page <= len(pdf), label + ': physical page')
            check(pdf[page - 1].get_label() == str(row['printed_page']),
                  label + ': printed label')
        check(len(visual['pages']) == 40, 'Forty retained visual body pages')
        with fitz.open(ROOT / docs[1]['path']) as guide:
            for page in visual['pages']:
                position = int(page['visual_physical_pdf_page'])
                check(1 <= position <= len(guide), 'Visual physical page')
                check(guide[position - 1].get_label() == str(page['visual_printed_page']),
                      'Visual printed label')
                for row in page['traditional_targets']:
                    expected = mapping[row['final_label']]
                    for key in ['number', 'printed_page', 'physical_pdf_page']:
                        check(str(row[key]) == str(expected[key]),
                              row['final_label'] + ': visual ' + key)
                    visual_targets += 1
        for row in walk({k: v for k, v in lean.items() if k != 'provenance'}):
            if not {'final_label', 'printed_page', 'physical_pdf_page'} <= row.keys():
                continue
            expected = mapping[row['final_label']]
            for key in ['printed_page', 'physical_pdf_page']:
                check(str(row[key]) == str(expected[key]),
                      row['final_label'] + ': Lean ' + key)
            lean_targets += 1
    check(visual_targets == 80, 'Eighty visual reading targets')
    check(len(lean['core']) == 19 and len(lean['strengthened']) == 79
          and len(lean['supplements']) == 6, 'Lean reading inventory')
    check(lean_targets == 110, 'Lean locators including twelve supplement endpoints')
    check(visual['traditional_pdf_sha256'] == docs[0]['sha256'], 'Visual traditional PDF pin')
    check(visual['visual_pdf_sha256'] == docs[1]['sha256'], 'Visual own PDF pin')
    check(visual['traditional_map_sha256'] == sha(trad / 'canonical_label_to_final.json'),
          'Visual map pin')
    check(visual['traditional_source_sha256'] == sha(trad / 'Paper_VII_Traditional_Final.tex'),
          'Visual wrapper pin')
    check(lean['provenance']['traditional_pdf_sha256'] == docs[0]['sha256'],
          'Lean traditional PDF pin')
    for name, pin in lean['provenance'].items():
        if name.endswith(('.tex', '.json')):
            check(sha(trad / name) == pin, 'Lean source/map pin ' + name)
    for name, data in read('COMPANION_MAP.json')['crosswalks'].items():
        check(read('editable/' + name) == data, 'Root crosswalk parity ' + name)
    expected_crosswalk = [
        {'visual_page': row['visual_page'], 'title': row['title'],
         'source_line': row['source_line_current'],
         'targets': [dict(target, label=target['final_label'],
                          traditional_page=target['printed_page'],
                          physical_page=target['physical_pdf_page'])
                     for target in row['traditional_targets']]}
        for row in visual['pages']]
    check(read('editable/visual_guide/SOURCE_CROSSWALK.json') == expected_crosswalk,
          'Visual legacy-format crosswalk parity')

    validation = read(CURRENT + 'RELEASE_VALIDATION.json')
    check(validation['status'] == 'PASS_FOR_STATED_SCOPE', 'Current validation status')
    check(validation['documents'] == docs, 'Current validation PDF identity')
    for row in validation['source_pins']:
        check(sha(ROOT / row['path']) == row['sha256'], 'Approved current source pin ' + row['path'])
    for row in validation['report_pins']:
        check(sha(ROOT / row['path']) == row['sha256'], 'Current evidence pin ' + row['path'])
    for name in validation['required_pass_reports']:
        check(read(name)['status'].startswith('PASS'), name + ': incomplete current review')

    preservation = read(CURRENT + 'SOURCE_PRESERVATION.json')
    module_path = ROOT / 'verification/compare_monograph_preservation.py'
    spec = importlib.util.spec_from_file_location('paper_vii_preservation', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    current_preservation = module.verify()
    check(current_preservation == preservation, 'Preservation evidence differs from current source')
    check(preservation['status'].startswith('PASS'), 'Proof/math preservation')
    inherited = read(CURRENT + 'INHERITED_ASSET_PRESERVATION.json')
    for row in inherited['files']:
        check(sha(ROOT / row['path']) == row['baseline_sha256'],
              'Retrieved inherited asset changed ' + row['path'])
    replay = read(CURRENT + 'PACKAGED_BUILD_REPLAY.json')
    check(replay['status'] == 'PASS' and replay['check_only'], 'Packaged PDF replay status')
    check(len(replay['documents']) == 3, 'All replay documents')
    for shipped, fresh in zip(docs, replay['documents']):
        check(fresh['shipped_pdf_sha256'] == shipped['sha256'], 'Replay shipped PDF pin')
        check(fresh['page_count_match'] and fresh['extracted_text_match'],
              'Packaged PDF replay page/text equality')
    return {
        'status': 'PASS_FOR_STATED_SCOPE', 'documents': docs,
        'active_pdf_copies_checked': 9,
        'canonical_labels_and_aliases': len(mapping),
        'visual_body_pages': 40, 'visual_locators': visual_targets,
        'lean_locators': lean_targets,
        'root_companion_crosswalk_parity': True,
        'record_environments': preservation['record_environments'],
        'numbered_records': preservation['numbered_records'],
        'complete_proof_bodies_preserved': preservation['proof_bodies'],
        'mathematical_spans_preserved': preservation['extracted_mathematical_spans'],
        'complete_part_files_byte_identical': preservation['complete_files_byte_identical'],
        'inherited_files_byte_identical_to_retrieved_delivery': len(inherited['files']),
        'packaged_rebuild_pages_and_text_match': True,
        'byte_identity': {d['document']: d['pdf_byte_identical'] for d in replay['documents']},
        'fresh_lean_compilation': False,
        'scope': 'PDF synchronization, actual navigation, reviewed source/evidence pins, source preservation and packaged PDF replay. No new mathematical experiment or Lean process is invoked.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    try:
        result = verify()
    except (AssertionError, KeyError, OSError, ValueError) as error:
        result = {'status': 'FAIL', 'error': str(error)}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result['status'] == 'FAIL'


if __name__ == '__main__':
    sys.exit(main())
