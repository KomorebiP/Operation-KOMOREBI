#!/usr/bin/env python3
"""Read-only Paper IX release/evidence checks. Does not run Lean or reprove mathematics."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / 'verification/2026-10-20'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):
    return json.loads(p.read_text())


def require(test, message):
    if not test:
        raise ValueError(message)


def command(argv, label):
    p = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True)
    require(p.returncode == 0, label + ': ' + p.stdout[-2000:] + p.stderr[-1000:])
    return p.stdout


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--report', type=Path)
    args = ap.parse_args()
    if args.report and args.report.resolve().is_relative_to(ROOT):
        ap.error('report must be outside the sealed package')
    result = {'schema': 'komorebi.paper-ix.release-evidence-check/1', 'status': 'FAIL',
              'checks': [], 'fresh_lean_execution': False}
    try:
        command([sys.executable, '-B', str(ROOT/'scripts/verify_integrity.py'), '--strict'], 'strict integrity')
        result['checks'].append('complete membership, paths, sizes and SHA256')
        import fitz
        release = read(ROOT/'RELEASE.json')
        docs = release['documents']
        require(len(docs) == 3 and {x['role'] for x in docs} ==
                {'traditional', 'visual', 'lean_evidence'}, 'reader role set differs')
        for row in docs:
            for key in ['file', 'mirror']:
                p = ROOT/row[key]
                require(p.resolve().is_relative_to(ROOT) and p.stat().st_size == row['bytes'] and
                        sha(p) == row['sha256'], 'PDF identity differs: ' + row[key])
            with fitz.open(ROOT/row['file']) as pdf:
                require(len(pdf) == row['pages'], 'PDF page count differs')
        require(sum(x['pages'] for x in docs) == release['total_pdf_pages'], 'reader total differs')
        for path, pin in release['source_revision'].items():
            require(sha(ROOT/path) == pin, 'source revision differs: ' + path)
        publication = read(ROOT/'publication/CURRENT_PUBLICATION_MANIFEST.json')
        require(publication['documents'] == docs, 'publication metadata differs')
        for row in publication['files']:
            p = ROOT/row['path']
            require(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'publication member differs')
        preflight = json.loads(command([sys.executable, '-B', str(ROOT/'preflight_pdfs.py')],
                                       'reader/navigation preflight'))
        require(preflight['status'] == 'PASS' and preflight['inherited_statement_rows'] == 62 and
                preflight['retained_source_links'] == 202 and preflight['main_labels_checked'] == 445,
                'navigation inventory differs')
        result['pages'] = {x['role']: x['pages'] for x in docs}
        result['checks'].append('coordinated readers, mirrors and 62/202 navigation')

        bib = read(E/'BIBLIOGRAPHY_REPAIR.json')
        require(bib['status'] == 'PASS' and bib['resolved_historical_entries'] == 22 and
                bib['remaining_unidentified_historical_keys'] == [], 'bibliography incomplete')
        for key in ['input_bib', 'corrected_bib', 'rendered_fragment']:
            row = bib[key]
            require(sha(ROOT/row['path']) == row['sha256'], 'bibliography pin differs: ' + key)
        for row in bib['recovered_artifacts']:
            require(sha(ROOT/row['path']) == row['sha256'], 'recovered artifact differs')
        fragment = (ROOT/bib['rendered_fragment']['path']).read_text()
        keys = re.findall(r'\\bibitem\{([^}]+)\}', fragment)
        require(len(keys) == 22 and set(keys) == set(bib['recovered_keys']) and
                r'\bysame' not in fragment and 'Exact source entry unavailable' not in fragment,
                'historical reference key/render inventory differs')
        first = read(ROOT/'recovered_history/AUTHENTICATION_A_M.json')
        last = read(ROOT/'recovered_history/AUTHENTICATION_L_Y.json')
        require(len(first['entries']) == 11 and all(x['status'] == 'bibliographic_identity_authenticated'
                for x in first['entries']) and last['conclusion']['keys_authenticated'] == 11 and
                len(last['records']) == 11 and all(x['metadata_verdict'].startswith('authenticated identity')
                for x in last['records']),
                'bibliographic identity checks incomplete')
        first_keys = {x['key'] for x in first['entries']}
        last_keys = {x['key'] for x in last['records']}
        require(len(first_keys) == len(last_keys) == 11 and not first_keys & last_keys and
                first_keys | last_keys == set(bib['recovered_keys']), 'bibliographic authentication key set differs')
        preserved = read(E/'MATHEMATICAL_SOURCE_PRESERVATION.json')
        require(preserved['status'] == 'PASS' and preserved['numbered_environment_bodies_preserved'] == 201 and
                preserved['proof_bodies_preserved'] == 153 and
                preserved['mathematical_statement_or_proof_token_changes'] == [], 'body preservation differs')
        require(len(preserved['source_tex_files']) == 108 and
                len({x['path'] for x in preserved['source_tex_files']}) == 108 and
                sum(x['numbered_environment_bodies'] for x in preserved['source_tex_files']) == 201 and
                sum(x['proof_bodies'] for x in preserved['source_tex_files']) == 153 and
                len(preserved['original_preserved_and_figure_files']) == 2405 and
                len({x['path'] for x in preserved['original_preserved_and_figure_files']}) == 2405,
                'preservation input inventory differs')
        for row in preserved['source_tex_files'] + preserved['original_preserved_and_figure_files']:
            require(sha(ROOT/row['path']) == row['sha256'], 'preserved source differs: ' + row['path'])
        result['checks'].append('22 recovered references and unchanged mathematical bodies')

        finite = read(E/'finite/FINITE_REPLAY.json')
        suites = {'delta_boundary', 'metric_tables', 'formal_source_reconciliation', 'dyadic_512',
                  'factorial_extension', 'factorial_frontier', 'visual_figures',
                  'worked_examples', 'reconstructed_figures'}
        require(finite['status'] == 'PASS_STATED_FINITE_SCOPE' and len(finite['runs']) == 9 and
                {x['suite'] for x in finite['runs']} == suites, 'finite suite set differs')
        require(finite['script_sha256'] == sha(ROOT/'scripts/replay_finite.py'), 'finite wrapper pin differs')
        require(len({x['manifest'] for x in finite['runs']}) == 9, 'finite manifest reused')
        for row in finite['runs']:
            require(row['execution_exit'] == row['manifest_validation_exit'] == 0 and
                    row['run_status'] == 'completed', 'finite execution incomplete')
            require(row['manifest'] == 'verification/2026-10-20/finite/runs/' + row['suite'] + '/manifest.json',
                    'finite suite manifest path differs')
            manifest = read(ROOT/row['manifest'])
            require(manifest['claim_id'] == 'PAPER_IX_RELEASE_20261020_' + row['suite'].upper() and
                    manifest['run']['status'] == 'completed' and manifest['run']['exit_status'] == 0 and
                    not manifest['run']['missing_results'] and not manifest['run']['invalid_results'],
                    'finite summary differs from actual run manifest')
            require(any(x['path'] == 'scripts/replay_finite.py' and
                        x['sha256'] == finite['script_sha256'] for x in manifest['input_artifacts']),
                    'finite manifest runner binding absent')
            command([sys.executable, '-B', str(ROOT/'preserved/threshold_free/computation/validate_manifest.py'),
                     str(ROOT/row['manifest']), '--root', str(ROOT)], 'finite binding: ' + row['suite'])
        controls = read(E/'integrity_controls/CONTROLS.json')
        require(controls['status'] == 'PASS' and controls['test_methods'] == 21 and
                controls['failures'] == controls['errors'] == controls['skips'] == 0, 'strict controls incomplete')
        require(set(controls['source_sha256']) == {'verify_integrity.py', 'test_integrity.py'},
                'strict control binding set differs')
        for name, pin in controls['source_sha256'].items():
            require(sha(ROOT/'scripts'/name) == pin, 'strict control source pin differs')
        result['checks'].append('nine fresh bounded manifest bindings and 21 integrity controls')

        replay = read(E/'FINAL_PDF_REPLAY.json')
        names = {Path(x['file']).name for x in docs}
        require(replay['status'] == 'PASS' and len(replay['documents']) == 3 and
                {x['file'] for x in replay['documents']} == names, 'PDF replay set differs')
        for row in replay['documents']:
            d = next(x for x in docs if Path(x['file']).name == row['file'])
            require(row['page_count_match'] and row['extracted_text_match'] and
                    row['frozen_sha256'] == d['sha256'], 'PDF replay comparison differs')
        qa = read(E/'PUBLICATION_QA.json')
        require(qa['status'] == 'PASS' and len(qa['documents']) == 3 and
                {x['file'] for x in qa['documents']} == names, 'QA set incomplete')
        for row in qa['documents']:
            require(sha(ROOT/'publication/pdfs'/row['file']) == row['sha256'] and
                    row['contact_reviewed_all_pages'] and not row['unresolved_findings'], 'QA binding differs')
        require(qa['portable_captures'] and len(qa['review_reports']) >= 3, 'visual QA artifacts absent')
        for row in qa['portable_captures'] + qa['review_reports']:
            require(sha(ROOT/row['path']) == row['sha256'], 'QA capture/report pin differs')
        license_status = read(ROOT/'LICENSE_STATUS.json')
        require(license_status['status'] == 'OPEN_LICENSES_APPLIED', 'explicit licenses absent')
        require(set(license_status['files']) == {'LICENSE.md', 'LICENSES/MIT.txt', 'LICENSES/CC-BY-4.0.txt',
                'LICENSES/THIRD_PARTY_NOTICES.txt', 'LICENSES/THIRD_PARTY_INVENTORY.json'},
                'license file inventory differs')
        for path, pin in license_status['files'].items():
            require(sha(ROOT/path) == pin, 'license pin differs')
        result['checks'].append('current PDF replay, bound visual review and explicit license grants')
        result['status'] = 'PASS'
    except Exception as exc:
        result['error'] = str(exc)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return result['status'] != 'PASS'


if __name__ == '__main__':
    raise SystemExit(main())
