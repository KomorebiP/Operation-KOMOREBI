#!/usr/bin/env python3
"""Verify every byte in an extracted Paper III final release (standard library).

This checks release integrity and consistency of recorded evidence. It does not
rerun Lean or turn a transcript into an independent proof. Use the documented
formal runner to produce a new verification event. Optional --pdf uses PyMuPDF.
"""
from pathlib import Path, PurePosixPath
import argparse
import datetime
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST = 'MANIFEST_SHA256.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='store_true', help='Also parse PDFs and check link destinations with PyMuPDF')
    parser.add_argument('--output', type=Path, help='Write a JSON receipt outside the frozen release tree')
    args = parser.parse_args()
    if args.output and args.output.resolve().is_relative_to(ROOT):
        parser.error('--output must be outside the frozen release tree')
    manifest = json.loads((ROOT / MANIFEST).read_text())
    expected = {row['path']: {'size_bytes': row['bytes'], 'sha256': row['sha256']} for row in manifest['files']}
    errors = []
    actual = {p.relative_to(ROOT).as_posix(): p for p in ROOT.rglob('*') if p.is_file() or p.is_symlink()}
    actual.pop(MANIFEST, None)
    for name in sorted(set(actual) - set(expected)):
        errors.append({'type': 'unexpected_file', 'path': name})
    for name, record in expected.items():
        path = PurePosixPath(name)
        if path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name:
            errors.append({'type': 'unsafe_manifest_path', 'path': name})
            continue
        target = ROOT.joinpath(*path.parts)
        if target.is_symlink() or not target.resolve().is_relative_to(ROOT):
            errors.append({'type': 'symlink_or_external_target', 'path': name})
        elif not target.is_file():
            errors.append({'type': 'missing_file', 'path': name})
        elif target.stat().st_size != record['size_bytes'] or sha(target) != record['sha256']:
            errors.append({'type': 'content_mismatch', 'path': name})
    phases = {}
    for label in ['full', 'audit', 'replay', 'controls']:
        path = ROOT / ('formal/verification/final_release_' + label + '/report.json')
        report = json.loads(path.read_text())
        passed = report.get('status') == 'PASS' and all(c.get('accepted') for c in report['commands'])
        phases[label] = {'status': report.get('status'), 'commands': len(report['commands']), 'accepted': passed}
        if not passed:
            errors.append({'type': 'recorded_formal_phase_not_passing', 'phase': label})
        if label == 'full':
            for command in report['commands']:
                current_source = ROOT / 'formal' / command['source']
                if sha(current_source) != command['source_sha256'] or not command['source_unchanged']:
                    errors.append({'type': 'formal_source_receipt_mismatch', 'source': command['source']})
    summary = json.loads((ROOT / 'formal/verification/FINAL_VERIFICATION_SUMMARY.json').read_text())
    if summary['status'] != 'PASS':
        errors.append({'type': 'final_formal_summary_not_passing'})
    for name, digest in summary['all_verified_source_sha256'].items():
        if sha(ROOT / 'formal' / name) != digest:
            errors.append({'type': 'verified_formal_source_changed', 'path': name})
    for label, phase in summary['accepted_phases'].items():
        if sha(ROOT / 'formal' / phase['report']) != phase['report_sha256']:
            errors.append({'type': 'formal_summary_report_mismatch', 'phase': label})
    register = json.loads((ROOT / 'metadata/MANUSCRIPT_STATEMENT_REGISTER_v1.0.0.json').read_text())
    for source in register['active_chapters']:
        if sha(ROOT / source['path']) != source['sha256']:
            errors.append({'type': 'statement_register_source_changed', 'path': source['path']})
    if sha(ROOT / 'publication/Paper_III_Final_v1.0.0.pdf') != register['selected_manuscript_sha256']:
        errors.append({'type': 'statement_register_pdf_changed'})
    state = json.loads((ROOT / 'RELEASE_STATUS.json').read_text())
    if state.get('release_version') != '1.0.0' or not state.get('technical_release_complete'):
        errors.append({'type': 'release_not_final'})
    pdf_records = []
    for path in sorted((ROOT / 'publication').glob('*.pdf')):
        data = path.read_bytes()
        item = {'path': path.relative_to(ROOT).as_posix(), 'bytes': len(data), 'pdf_header': data.startswith(b'%PDF-'),
                'eof_marker': b'%%EOF' in data[-2048:]}
        if not item['pdf_header'] or not item['eof_marker']:
            errors.append({'type': 'invalid_pdf_envelope', 'path': item['path']})
        if args.pdf:
            import fitz
            with fitz.open(path) as doc:
                item['pages'] = len(doc)
                item['bookmarks'] = len(doc.get_toc())
                item['internal_links'] = 0
                for i, page in enumerate(doc):
                    for link in page.get_links():
                        if link['kind'] in (fitz.LINK_GOTO, fitz.LINK_NAMED):
                            item['internal_links'] += 1
                            if not 0 <= link.get('page', -1) < len(doc):
                                errors.append({'type': 'invalid_internal_pdf_link', 'path': item['path'], 'page': i + 1})
        pdf_records.append(item)
    record = {'schema': 'komorebi.paper-iii.final-extraction-verification/1',
              'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'release_version': '1.0.0', 'status': 'PASS' if not errors else 'FAIL',
              'manifest_sha256': sha(ROOT / MANIFEST), 'expected_files': len(expected),
              'actual_files': len(actual), 'manifest_bytes': sum(r['size_bytes'] for r in expected.values()),
              'active_chapters_bound_to_register': len(register['active_chapters']),
              'current_formal_sources_bound_to_summary': len(summary['all_verified_source_sha256']),
              'recorded_formal_phases': phases, 'pdfs': pdf_records, 'errors': errors,
              'scope': 'Fresh extraction byte integrity and recorded evidence consistency; this command does not execute Lean.'}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
