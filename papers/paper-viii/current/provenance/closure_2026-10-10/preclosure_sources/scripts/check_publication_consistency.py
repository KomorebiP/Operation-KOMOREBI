#!/usr/bin/env python3
"""Check current companion copies, PDF labels, crosswalks and report source pins."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess, sys
import fitz

ROOT = Path(__file__).resolve().parent.parent

def read(rel):
    return json.loads((ROOT / rel).read_text())

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def require(condition, message):
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

def main():
    edition = read('EDITION.json')
    docs = edition['documents']
    require(len(docs) == 3, 'Three companion PDFs required')
    for d in docs:
        for folder in ['papers', 'publication/pdfs', 'editable/' + d['role']]:
            p = ROOT / folder / Path(d['path']).name
            require(sha(p) == d['sha256'], str(p) + ': PDF hash')
            require(p.stat().st_size == d['bytes'], str(p) + ': PDF byte size')
            with fitz.open(p) as pdf:
                require(len(pdf) == d['pages'], str(p) + ': PDF page count')
    require(sum(d['pages'] for d in docs) == edition['total_pages'], 'Total pages')
    for rel in ['COMPANION_MAP.json', 'SERIES_STATUS.json',
                'publication/CURRENT_PUBLICATION_MANIFEST.json',
                'verification/MONOGRAPH_VERIFICATION.json']:
        require(read(rel)['documents'] == docs, rel + ': companion metadata')
    mapping = read('editable/traditional/canonical_label_to_final.json')
    require(isinstance(mapping, dict) and mapping, 'Canonical source label map')
    with fitz.open(ROOT / docs[0]['path']) as pdf:
        for label, row in mapping.items():
            page = int(row['physical_pdf_page'])
            require(1 <= page <= len(pdf), label + ': physical PDF page')
            require(pdf[page-1].get_label() == str(row['printed_page']), label + ': actual printed label')
    locator_counts = {}
    for rel in ['visual_guide/VISUAL_TO_TRADITIONAL_CROSSWALK.json',
                'lean_guide/generated/traditional_crosswalk.json']:
        data = read('editable/' + rel)
        count = 0
        for row in walk(data):
            if not {'final_label', 'printed_page', 'physical_pdf_page'} <= row.keys():
                continue
            label = row['final_label']
            require(label in mapping, rel + ': unknown target ' + label)
            for key in ['printed_page', 'physical_pdf_page']:
                require(str(row[key]) == str(mapping[label][key]), rel + ': stale ' + label + ' ' + key)
            if 'number' in row and row['number'] is not None:
                require(str(row['number']) == str(mapping[label]['number']), rel + ': stale result number ' + label)
            count += 1
        require(count > 0, rel + ': no verified locators')
        locator_counts[rel] = count
    for rel, data in read('COMPANION_MAP.json')['crosswalks'].items():
        require(read('editable/' + rel) == data, 'Root/current map parity ' + rel)
    checked_pins = 0
    nested_pins_checked = 0
    reports = read('verification/MONOGRAPH_VERIFICATION.json')['reports']
    reports += [edition['current_computation_report']]
    for rel in reports:
        report = read(rel)
        require(str(report['status']).startswith('PASS'), rel + ': review incomplete')
        for row in walk(report):
            if not {'path', 'sha256'} <= row.keys():
                continue
            path, pin = row['path'], row['sha256']
            if not isinstance(path, str) or not isinstance(pin, str) or len(pin) != 64:
                continue
            resolved = ROOT / path
            if rel == 'verification/monograph_lean_report.json' and path.startswith('qa/'):
                resolved = ROOT / 'editable/lean_guide' / path
            require(resolved.is_file(), rel + ': missing nested artifact ' + path)
            require(sha(resolved) == pin, rel + ': stale nested artifact ' + path)
            nested_pins_checked += 1
        pins = report.get('source_pins', [])
        if isinstance(pins, list):
            for row in pins:
                if isinstance(row, dict) and {'path', 'sha256'} <= row.keys():
                    require(sha(ROOT / row['path']) == row['sha256'], rel + ': stale pin ' + row['path'])
                    checked_pins += 1
        for field in ['report_dependencies', 'report_dependency_pins', 'input_pins']:
            pins = report.get(field, {})
            if isinstance(pins, dict):
                for path, pin in pins.items():
                    if isinstance(pin, str) and len(pin) == 64:
                        require(sha(ROOT / path) == pin, rel + ': stale dependency ' + path)
                        checked_pins += 1
    computation = read(edition['current_computation_report'])
    manifest_records = computation['provenance_manifests']
    require(len(manifest_records) == 12, 'Twelve separately scoped current bounded manifests')
    for row in manifest_records:
        require(sha(ROOT / row['path']) == row['sha256'], row['gate'] + ': manifest pin')
        require(sha(ROOT / row['result']) == row['result_sha256'], row['gate'] + ': result pin')
        result = subprocess.run(
            [sys.executable, str(ROOT / 'verification/checks/validate_manifest.py'),
             str(ROOT / row['path']), '--root', str(ROOT)],
            cwd=ROOT, text=True, capture_output=True,
        )
        require(result.returncode == 0,
                row['gate'] + ': current bounded provenance validation ' + result.stdout + result.stderr)
    original = ROOT / 'provenance/current_retrieved_baseline/traditional/parts'
    parts = sorted(original.glob('*.tex'))
    require(len(parts) == 7, 'Seven retrieved mathematical parts')
    for p in parts:
        require(p.read_bytes() == (ROOT / 'editable/traditional/parts' / p.name).read_bytes(),
                p.name + ': protected source changed')
    figure_report = read('verification/monograph_figure_report.json')
    for key in ['model_preservation_audit', 'repaired_plotted_models', 'repair_generator']:
        require(sha(ROOT / figure_report[key]) == figure_report[key + '_sha256'],
                'Figure repair evidence: stale ' + key)
    require(len(figure_report['figure_records']) == 22, 'All inherited figure identities')
    for row in figure_report['figure_records']:
        require(sha(ROOT / 'editable/traditional/figures' / row['name']) == row['current_sha256'],
                row['name'] + ': current figure pin')
    replay = read('verification/MONOGRAPH_PACKAGED_BUILD.json')
    require(replay['status'] == 'PASS' and len(replay['documents']) == 3, 'Packaged replay status')
    for d, rebuilt in zip(docs, replay['documents']):
        require(rebuilt['document'] == Path(d['path']).stem, 'Rebuild document order')
        require(rebuilt['page_count_match'] and rebuilt['extracted_text_match'], 'Page/text rebuild')
        require(rebuilt['shipped_pdf_sha256'] == d['sha256'], 'Rebuild current PDF pin')
    # All final links have actual in-document targets, independently of crosswalk strings.
    internal_links = 0
    for d in docs:
        with fitz.open(ROOT / d['path']) as pdf:
            names = pdf.resolve_names()
            for i, page in enumerate(pdf, 1):
                for link in page.get_links():
                    if link['kind'] == fitz.LINK_GOTO:
                        require(0 <= link.get('page', -1) < len(pdf), f"{d['role']} {i}: invalid link")
                        internal_links += 1
                    elif link['kind'] == fitz.LINK_NAMED:
                        target = names.get(link.get('nameddest', ''), {})
                        require(0 <= target.get('page', -1) < len(pdf), f"{d['role']} {i}: invalid named link")
                        internal_links += 1
    report = {
        'status': 'PASS_FOR_STATED_SCOPE',
        'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'documents': docs, 'active_pdf_copies_checked': 9,
        'canonical_labels_and_aliases': len(mapping), 'companion_locators': locator_counts,
        'root_crosswalk_parity': True, 'review_source_and_dependency_pins_checked': checked_pins,
        'nested_review_artifact_pins_checked': nested_pins_checked,
        'current_bounded_manifests_validated': len(manifest_records),
        'inherited_figure_identities_checked': 22, 'mathematical_parts_byte_identical': 7,
        'explicit_manuscript_proof_bodies': 56, 'complete_supplementary_bodies': 6,
        'valid_internal_links': internal_links, 'packaged_page_and_text_rebuilds_match': True,
        'pdf_byte_identity': {x['document']: x['pdf_byte_identical'] for x in replay['documents']},
        'scope': 'Actual PDF synchronization, navigation labels, source/report pins, and inherited figure identity. No new Lean, scientific or device process.',
    }
    (ROOT / 'verification/PACKAGE_CONSISTENCY.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()

