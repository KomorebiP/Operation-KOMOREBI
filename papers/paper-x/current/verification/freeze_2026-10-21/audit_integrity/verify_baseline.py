#!/usr/bin/env python3
"""Read-only Paper X baseline identity and recorded-evidence authentication.

For the original 8,257-file tree only, not an expanded frozen wrapper. Restore
all three original administrative files and the original file set in a separate
working copy first. The accepted ZIP and external clean receipt are required.
No Lean, auditor, scientific suite, control, generator or TeX process is run.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from collections import Counter
import argparse
import hashlib
import json
import re
import stat
import zipfile

TASK = Path('/dev/shm/komorebi_paper_x_freeze_fbc994080222')
ARCHIVE_SHA = '1960094b48e73e34e8c1dc02411ecb1bda2ed6088d1a42a8bc948848b44c4c3b'
STRICT_SHA = 'dff3d8725afdd6b93c97802827ca9233ab8099ced2bdb88f933ab20ba3c41b58'


def digest(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(block)
    return h.hexdigest()


def sha(path):
    with path.open('rb') as f:
        return digest(f)


def read(path):
    return json.loads(path.read_text())


def safe(name):
    p = PurePosixPath(name)
    return (bool(name) and not p.is_absolute() and p.as_posix() == name
            and ':' not in name and '\\' not in name
            and all(x not in ('', '.', '..') for x in name.split('/')))


def audit(root, archive, receipt, output):
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    counts = {}

    def check(name, condition, detail=None):
        checks.append({'check': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})

    files = {p.relative_to(root).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in root.rglob('*') if p.is_file()}

    def pins(rows, prefix=''):
        return all(safe(x['path']) and prefix + x['path'] in files
                   and files[prefix + x['path']]['sha256'] == x['sha256']
                   and ('bytes' not in x or files[prefix + x['path']]['bytes'] == x['bytes']) for x in rows)

    check('no_baseline_symlinks', not any(p.is_symlink() for p in root.rglob('*')))
    check('accepted_archive_bytes_hash', archive.stat().st_size == 222548626 and sha(archive) == ARCHIVE_SHA)
    with zipfile.ZipFile(archive) as z:
        info = z.infolist()
        check('archive_unique_safe_regular_names', len({x.filename for x in info}) == len(info)
              and all(safe(x.filename.rstrip('/')) and not stat.S_ISLNK(x.external_attr >> 16) for x in info))
        prefix = 'Paper_X_Final_Release_v1.0.0/'
        archived = {}
        for x in info:
            if x.is_dir():
                continue
            with z.open(x) as f:
                archived[x.filename] = {'bytes': x.file_size, 'sha256': digest(f)}
        check('archive_expected_common_root', all(x.startswith(prefix) for x in archived))
        stripped = {p[len(prefix):]: x for p, x in archived.items()}
        check('all_8257_archive_baseline_files_exact', len(files) == 8257 and stripped == files)
        check('archive_uncompressed_bytes', sum(x['bytes'] for x in archived.values()) == 729817647)
    manifest = read(root / 'MANIFEST_SHA256.json')
    rows = manifest['files']
    check('strict_manifest_exact_schema', manifest['schema'] == 'komorebi.strict_manifest.v1'
          and set(manifest) <= {'schema', 'checkpoint', 'scope', 'edition', 'generated_at_utc', 'files'})
    check('manifest_safe_unique_rows', len({x['path'] for x in rows}) == len(rows) and all(safe(x['path']) for x in rows))
    check('manifest_exact_membership', len(rows) == 8256 and {x['path'] for x in rows} == set(files) - {'MANIFEST_SHA256.json'})
    check('manifest_all_bytes_sha256', pins(rows))
    pointer = read(root / 'MANIFEST.json')
    check('secondary_manifest_is_pointer_only', pointer['role'] == 'manifest_filename_pointer'
          and pointer['authoritative_manifest'] == 'MANIFEST_SHA256.json' and 'files' not in pointer)
    counts.update(baseline_files=len(files), manifest_rows=len(rows))
    accepted = read(receipt)
    check('external_accepted_clean_receipt_double_bind', accepted['status'] == 'PASS'
          and accepted['archive_identity'] == {'bytes': 222548626, 'sha256': ARCHIVE_SHA}
          and accepted['archive_regular_files'] == 8257 and accepted['strict_files_checked'] == 8256
          and accepted['extracted_payload_unchanged'] and accepted['archive_unchanged_during_verification'])
    check('external_receipt_no_science_rerun', accepted['new_lean_processes'] == 0 and accepted['scientific_suites_rerun'] is False)
    check('current_integrity_checker_identity', files['scripts/verify_integrity.py']['sha256'] == STRICT_SHA)
    controls = read(root / 'verification/2026-10-20/STRICT_VERIFIER_CONTROLS.json')
    check('current_21_control_receipt_and_code_bindings', controls['status'] == 'PASS' and controls['test_methods'] == 21
          and controls['failures'] == controls['errors'] == controls['skips'] == 0
          and set(controls['source_sha256']) == {'verify_integrity.py', 'test_integrity.py'}
          and all(files['scripts/' + name]['sha256'] == pin for name, pin in controls['source_sha256'].items()))
    mapping = read(root / 'formal_preservation/ARCHIVE_MAP.json')
    payloads = mapping['payloads']
    check('compact_unique_payload_rows', len(payloads) == len({x['sha256'] for x in payloads})
          == len({x['payload_path'] for x in payloads}) == 3079)
    check('all_compact_payload_bytes_sha256', all(safe(x['payload_path'])
          and files['formal_preservation/' + x['payload_path']] == {'bytes': x['bytes'], 'sha256': x['sha256']} for x in payloads))
    by_hash = {x['sha256']: x for x in payloads}
    leaves = mapping['leaf_occurrences']
    check('all_13730_leaf_mapping_references', len(leaves) == 13730 and all(
        x['sha256'] in by_hash and x['payload_path'] == by_hash[x['sha256']]['payload_path']
        and x['bytes'] == by_hash[x['sha256']]['bytes'] for x in leaves))
    frequencies = Counter(x['sha256'] for x in leaves)
    check('payload_occurrence_counts', all(x['occurrence_count'] == frequencies[x['sha256']] for x in payloads))
    check('compact_container_identity_scope', len(mapping['containers']) == 16 and len(mapping['container_occurrences']) == 33
          and len(mapping['root_archives']) == 3 and all(x['container_sha256'] in {c['sha256'] for c in mapping['containers']}
          for x in mapping['container_occurrences']))
    summary = read(root / 'formal_preservation/PRESERVATION_SUMMARY.json')
    check('compact_summary_counts_bytes', summary['unique_leaf_payloads'] == 3079 and summary['leaf_occurrences'] == 13730
          and summary['unique_payload_bytes'] == sum(x['bytes'] for x in payloads) == 301538108
          and summary['leaf_occurrence_bytes'] == sum(x['bytes'] for x in leaves) == 1070733009)
    counts.update(compact_unique_leaf_payloads=3079, compact_leaf_occurrences=13730,
                  compact_unique_container_identities=16, compact_container_occurrences=33)
    recovered = read(root / 'verification/2026-10-10/INPUT_RECOVERY.json')['files']
    evidence = [x for x in recovered if x['path'].startswith(('formal_preservation/', 'inherited_baseline/', 'current_continuation/', 'status_records/'))]
    check('6170_inherited_evidence_file_pins', len(evidence) == 6170 and pins(evidence))
    counts['inherited_evidence_file_pins'] = len(evidence)
    counts['formal_preservation_file_pins'] = sum(x['path'].startswith('formal_preservation/') for x in evidence)
    source = read(output / 'source_preservation_STDOUT.txt')
    check('safe_live_source_preservation', source['status'] == 'passed' and source['inherited_evidence_files_unchanged'] == 6170
          and source['unchanged_main_proof_bodies'] == 16 and source['numbered_source_records_unchanged_except_locators'] == 20
          and source['printed_complete_modules'] == 4 and source['printed_source_lines'] == 1117 and source['compiler_invoked'] is False)
    counts.update(unchanged_main_proof_bodies=16, numbered_main_source_records=20, complete_printed_modules=4, printed_source_lines=1117)
    prints = read(root / 'lean_guide/PRINTED_SOURCE_MANIFEST.json')
    check('four_printed_source_pins', len(prints) == 4 and all(files[x['source']]['sha256'] == x['sha256'] for x in prints))
    current = read(root / 'verification/2026-10-20/CURRENT_FINITE_REPLAY.json')
    check('accepted_current_seven_gate_record', current['status'] == 'PASS_STATED_FINITE_SCOPE'
          and current['execution_exit'] == current['manifest_validation_exit'] == 0
          and current['gates']['expected_gates'] == 7 and current['gates']['all_passed']
          and current['scientific_input_files'] == 6188 and current['input_hashes_before'] == current['input_hashes_after']
          and all(files[p]['sha256'] == pin for p, pin in current['input_hashes_after'].items()))
    finite = read(root / 'verification/2026-10-20/FINITE_REPLAY.json')
    active = [('current_seven_gates', current['manifest'])] + [(x['suite'], x['manifest']) for x in finite['runs'] if x['suite'] != 'documented_seven_gates']
    check('one_current_seven_gate_plus_six_finite_manifests', len(active) == 7
          and {name for name, path in active} == {'current_seven_gates', 'precision', 'summands', 'families', 'logarithms', 'quadratic_packets', 'local_quadratic'})
    input_rows = output_rows = 0
    for name, path in active:
        data = read(root / path)
        input_rows += len(data['input_artifacts'])
        output_rows += len(data['outputs'])
        check('recorded_artifact_bindings_' + name, data['schema_version'] == 2 and data['run']['status'] == 'completed'
              and data['run']['exit_status'] == 0 and pins(data['input_artifacts']) and pins(data['outputs'])
              and all(x['sha256'] == x['sha256_after'] for x in data['input_artifacts']))
    counts.update(current_documented_gates=7, additional_finite_suites=6, active_v2_manifests=7,
                  active_manifest_input_rows=input_rows, active_manifest_output_rows=output_rows)
    original = read(root / 'verification/2026-10-20/ORIGINAL_SOURCE_RECOVERY.json')
    check('51_recovered_original_source_files', original['recovered_files'] == 51 and pins(original['files'])
          and original['original_historical_pdf_pages'] == 41 and original['vector_figures'] == 14)
    bib = read(root / 'verification/2026-10-20/BIBLIOGRAPHY_INTEGRATION.json')
    check('23_bibliography_keys_and_original_identity', len(bib['keys']) == 23
          and files['manuscript/references.bib']['sha256'] == bib['current_bib_sha256']
          and len(re.findall(r'@\w+\s*\{\s*([^,]+),', (root / 'manuscript/references.bib').read_text())) == 23)
    release = read(root / 'RELEASE.json')
    check('accepted_162_page_reader_identity', release['total_pdf_pages'] == 162 and len(release['pdfs']) == 3
          and {x['pages'] for x in release['pdfs']} == {92, 33, 37}
          and all(files[x['file']] == {'bytes': x['bytes'], 'sha256': x['sha256']} for x in release['pdfs']))
    rebuilt = accepted['isolated_reader_rebuild']
    check('accepted_qualified_pdf_rebuild_record', rebuilt['status'] == 'PASS' and len(rebuilt['pdf_comparison']) == 3
          and all(not x['raw_byte_identical'] and x['identical_except_trailer_ids']
                  and x['differing_text_pages'] == x['differing_rendered_pages'] == []
                  and files['publication/pdfs/' + x['file']]['sha256'] == x['archive_pdf_sha256'] for x in rebuilt['pdf_comparison']))
    safe_checks = read(output / 'SAFE_EXISTING_CHECKS.json')
    check('ten_safe_existing_read_only_commands', safe_checks['status'] == 'PASS' and len(safe_checks['checks']) == 10)
    formal_path = output / 'FORMAL_STATIC_AUDIT.json'
    if formal_path.is_file():
        formal = read(formal_path)
        check('independent_production_static_audit', formal['status'] == 'PASS', formal)
    limits = {
        'accepted_production': 'Two accepted October 20 builds each compiled 122 selected modules; 392 generated artifact pairs match. The owning census has 2,846 declarations, 2,127 theorems, 444 private declarations and 45 exact target contracts. These are authenticated saved records/retained objects; this freeze runs no compiler or auditor.',
        'conditional_contract': 'The amended conditional 20/20 source contract is separate from the unpromoted stronger 19/20 attempt. Terminal conclusions are two independent existential outputs. Actual source members, carrier presentations, local comparison data and the named hypotheses remain inputs. The arithmetic separator is literally over GQ; zero multiplicities are allowed and nonzero occupancy is not supplied.',
        'preservation_units': '6,170 inherited evidence-file pins across four directories are distinct from 3,079 unique compact-store leaf payloads and 13,730 leaf occurrences. Container hashes identify 16 original ZIP containers/33 occurrences; original ZIP byte streams are not restored or authenticated as retained ZIP files.',
        'current_science': 'The current seven-gate record and six exact finite suites are authenticated by seven active v2 manifests. The separate selected-Oct10 documented_seven_gates manifest remains historical and is not a current root README/MANIFEST binding. No scientific, parser or control suite is rerun.',
        'historical_source': '51 recovered original source files include the 41-page historical PDF, 14 original vector figures and 23 bibliography keys. These file identities and recorded source-specific metadata checks are distinct from blanket theorem/application acceptance. The historical archive SHA is recorded; this audit does not claim a retained byte-exact ZIP container.',
        'reader_rebuild': 'Accepted external clean-extraction receipt binds the exact current ZIP and all three PDF hashes. It records identical ordered text and 86.4-dpi rendered pages, and complete PDF streams equal only after trailer-ID removal. Raw PDF byte equality is false; Lean artifact binary equality is a separate result. No fresh PDF build occurs in this audit.',
        'administrative_adapter': 'Only MANIFEST_SHA256.json pins the current root README.md and PROGRESS_LEDGER.md hashes. The production subdirectory README rows are local indexes and remain unchanged. MANIFEST.json is a listed authoritative-manifest pointer, not a second inventory, and can remain byte-identical. Keep original strict checker and own 21-control receipt unchanged; regenerate the strict v1 root manifest with only its accepted metadata fields.',
        'audit_usage': 'Baseline-only audit with --root original-tree --archive accepted-ZIP --receipt accepted-external-receipt --output external-dir. For an expanded freeze, first reconstruct a separate original tree using the baseline-preservation map, restoring all three administrative files and omitting freeze additions. Direct frozen validation uses unchanged strict/source/compact-store and current saved-manifest checkers.',
        'missing_history': 'October 16-17 packages and their reported 122-module/39-test run remain unrecovered and unauthenticated. Current October 20 production explicitly selects recovered October10 sources; it is not relabelled missing history.'
    }
    failures = [x for x in checks if x['status'] == 'FAIL']
    report = {'schema': 'komorebi.paper-x.freeze-baseline-integrity/1', 'status': 'FAIL' if failures else 'PASS',
              'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'baseline_root': str(root), 'archive': str(archive),
              'accepted_external_receipt': {'path': str(receipt), 'sha256': sha(receipt)},
              'checks_passed': len(checks) - len(failures), 'checks_total': len(checks), 'counts': counts,
              'checks': checks, 'failures': failures, 'scope_and_limits': limits,
              'baseline_read_only': True, 'no_compiler_auditor_tex_science_generator_or_control_execution': True}
    (output / 'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    prose = [f"Paper X baseline integrity: {report['status']} ({report['checks_passed']}/{len(checks)} checks).",
             'All 8,257 archive/baseline files and 8,256 manifest rows authenticate. The external accepted receipt double-binds the current ZIP.',
             '6,170 inherited evidence pins, 16 proof bodies, 20 numbered source records, four complete printed modules and 1,117 lines authenticate.',
             f"Seven active v2 manifest records authenticate {input_rows:,} input artifact rows and {output_rows} output artifact rows; no suites rerun."]
    prose += [k + ': ' + v for k, v in limits.items()]
    if failures:
        prose.append('FAILURES: ' + json.dumps(failures))
    (output / 'BASELINE_INTEGRITY_AUDIT.txt').write_text('\n\n'.join(prose) + '\n')
    print(json.dumps({'status': report['status'], 'checks_passed': report['checks_passed'], 'checks_total': len(checks), 'counts': counts, 'failures': failures}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=TASK / 'baseline/Paper_X_Final_Release_v1.0.0')
    p.add_argument('--archive', type=Path, default=TASK / 'inputs/Paper_X_Final_Release_v1.0.0_2026-10-20.zip')
    p.add_argument('--receipt', type=Path, default=TASK / 'ACCEPTED_CLEAN_EXTRACTION_RECEIPT.json')
    p.add_argument('--output', type=Path, default=TASK / 'audit_integrity')
    args = p.parse_args()
    raise SystemExit(audit(args.root, args.archive, args.receipt, args.output))
