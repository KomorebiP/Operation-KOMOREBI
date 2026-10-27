#!/usr/bin/env python3
"""Read-only Paper VIII baseline byte/provenance audit; no scientific execution.

The two optional safe checker receipts are produced separately after source inspection.
This audit streams ZIP members without extracting archived trees. All output is external.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import hashlib
import json
import stat
import zipfile
import xml.etree.ElementTree as ET

TASK = Path('/dev/shm/komorebi_paper_viii_freeze_fbc994080222')
OUTER_HASH = '2061f53add59a257a46ac837d69237ed29de152dbd9d30441f6dd46df0858793'
INNER_HASH = '84d59b17f5713fca69240a1697153971bd74dae663ee6de592e618980ba7831a'


def digest(stream):
    h = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(block)
    return h.hexdigest()


def sha(path):
    with path.open('rb') as f:
        return digest(f)


def safe(name):
    p = PurePosixPath(name)
    return (isinstance(name, str) and name and '\\' not in name and ':' not in name
            and not p.is_absolute() and '..' not in p.parts
            and p.as_posix() == name and all(x not in ('', '.') for x in name.split('/')))


def load(path):
    return json.loads(path.read_text())


def zip_inventory(path):
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        assert len({i.filename for i in infos}) == len(infos), 'duplicate ZIP names'
        assert all(safe(i.filename.rstrip('/')) for i in infos), 'unsafe ZIP name'
        assert all(not stat.S_ISLNK(i.external_attr >> 16) for i in infos), 'ZIP symlink'
        files = [i for i in infos if not i.is_dir()]
        result = {}
        for i in files:
            with z.open(i) as f:
                result[i.filename] = {'bytes': i.file_size, 'sha256': digest(f)}
        # Reading every member to EOF above checks CRC as well as the SHA256.
        return result


def audit(root, outer, delivery, output):
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    counts = {}

    def check(name, condition, detail=None):
        checks.append({'check': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})

    def pins(rows, base=root):
        return all(safe(row['path']) and (base / row['path']).is_file()
                   and sha(base / row['path']) == row['sha256']
                   and ('bytes' not in row or (base / row['path']).stat().st_size == row['bytes'])
                   for row in rows)

    original = {p.relative_to(root).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                for p in root.rglob('*') if p.is_file()}
    check('baseline_no_symlinks', not any(p.is_symlink() for p in root.rglob('*')))
    check('core_archive_bytes_hash', (delivery / 'Komorebi_Paper_VIII_Final_2026-10-10.zip').stat().st_size == 122660203
          and sha(delivery / 'Komorebi_Paper_VIII_Final_2026-10-10.zip') == INNER_HASH)
    check('outer_archive_bytes_hash', outer.stat().st_size == 122663345 and sha(outer) == OUTER_HASH)
    outer_rows = zip_inventory(outer)
    delivery_rows = {p.relative_to(delivery).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
                     for p in delivery.rglob('*') if p.is_file()}
    check('outer_three_files_exact_to_delivery', len(outer_rows) == 3 and outer_rows == delivery_rows)
    dm = load(delivery / 'DELIVERY_MANIFEST.json')
    check('delivery_manifest_unchanged_inner', len(dm) == 1 and dm[0]['source_bytes'] == 122660203
          and dm[0]['delivery_bytes'] == 122660203 and dm[0]['source_sha256'] == INNER_HASH
          and dm[0]['delivery_sha256'] == INNER_HASH and dm[0]['changed'] is False
          and dm[0]['font_files_removed'] == [])
    inner_rows = zip_inventory(delivery / 'Komorebi_Paper_VIII_Final_2026-10-10.zip')
    prefix = root.name + '/'
    check('inner_archive_single_expected_root', all(p.startswith(prefix) for p in inner_rows))
    stripped = {p[len(prefix):]: v for p, v in inner_rows.items()}
    check('all_core_archive_members_exact', len(original) == 2711 and stripped == original)
    check('inner_uncompressed_bytes', sum(x['bytes'] for x in inner_rows.values()) == 169775428)
    counts.update(core_files=len(original), core_manifest_rows=2710, outer_delivery_files=len(delivery_rows))
    manifest = load(root / 'MANIFEST_SHA256.json')
    rows = manifest['files']
    check('manifest_safe_unique_paths', all(safe(x['path']) for x in rows)
          and len({x['path'] for x in rows}) == len(rows))
    check('manifest_exact_set', len(rows) == 2710 and {x['path'] for x in rows} == set(original) - {'MANIFEST_SHA256.json'})
    check('manifest_all_bytes_hashes', pins(rows))
    preservation = load(root / 'verification/closure_2026-10-10/CONTENT_AND_SOURCE_PRESERVATION.json')
    raw, markup = preservation['raw_scientific_sources'], preservation['editable_markup']
    check('raw_scientific_source_pins', len(raw) == 1062 and len({x['path'] for x in raw}) == 1062 and pins(raw))
    check('raw_source_inventory_complete', {x['path'] for x in raw} == {p for p in original if p.startswith('source/')})
    check('editable_markup_pins', len(markup) == 258 and len({x['path'] for x in markup}) == 258 and pins(markup))
    counts.update(raw_scientific_sources=len(raw), editable_markup=len(markup))
    recoveries = load(root / 'provenance/RECOVERY.json')
    recovered = 0
    for recovery in recoveries:
        archive = root / 'downloads' / recovery['archive']
        check('recovery_archive_' + recovery['branch'], archive.stat().st_size == recovery['bytes'] and sha(archive) == recovery['sha256'])
        archived = zip_inventory(archive)
        live = {p[len('source/' + recovery['branch'] + '/'):]: x for p, x in original.items()
                if p.startswith('source/' + recovery['branch'] + '/')}
        check('recovery_payload_exact_' + recovery['branch'], archived == live and len(live) == recovery['files'])
        recovered += len(live)
    check('all_recovery_sources', recovered == 1062)
    # The extra nested historical ZIP is verified in place, never extracted.
    historical = list((root / 'source').rglob('Original_Paper_VIII_Package.zip'))
    check('historical_nested_zip_count', len(historical) == 1)
    for archive in historical:
        historic_rows = zip_inventory(archive)
        check('historical_nested_zip_crc_safe', len(historic_rows) == 132)
    preserved = load(root / 'verification/MONOGRAPH_PRESERVATION.json')
    check('seven_protected_parts_exact', len(preserved['mathematical_source_parts']) == 7 and all(
        sha(root / 'editable/traditional' / x['path']) == x['final_sha256'] == x['baseline_sha256']
        and (root / 'editable/traditional' / x['path']).read_bytes()
        == (root / 'provenance/current_retrieved_baseline/traditional' / x['path']).read_bytes()
        for x in preserved['mathematical_source_parts']))
    check('written_preservation_inventory', preserved['protected_statement_body_count'] == len(preserved['statement_bodies']) == 85
          and preserved['protected_proof_body_count'] == len(preserved['proof_bodies']) == 56
          and preserved['complete_supplement_body_count'] == 6 and preserved['protected_part_math_token_changes'] == [])
    counts.update(numbered_manuscript_records=85, explicit_main_proof_bodies=56, supplements=6)
    edition = load(root / 'EDITION.json')
    check('accepted_formal_scope_metadata', edition['formal_scope']['ledger_items'] == 56
          and edition['formal_scope']['active_modules'] == 40
          and edition['formal_scope']['named_theorem_declarations'] == 392
          and edition['formal_scope']['separate_construction_audits'] == 66
          and edition['formal_scope']['separately_tracked_classical_inputs'] == 4
          and edition['formal_scope']['fresh_lean_compilation'] is False)
    check('active_readers_exact', len(edition['documents']) == 3 and edition['total_pages'] == 252
          and [x['pages'] for x in edition['documents']] == [124, 34, 94]
          and all(sha(root / folder / Path(d['path']).name) == d['sha256']
                  for d in edition['documents'] for folder in ['papers', 'publication/pdfs', 'editable/' + d['role']]))
    computation = load(root / edition['current_computation_report'])
    gates = computation['provenance_manifests']
    check('twelve_recorded_gate_manifest_result_pins', len(gates) == 12 and all(
        sha(root / x['path']) == x['sha256'] and sha(root / x['result']) == x['result_sha256'] and x['status'] == 'PASS'
        for x in gates))
    input_count = output_count = 0
    for gate in gates:
        evidence = load(root / gate['path'])
        inputs, outputs = evidence['input_artifacts'], evidence['outputs']
        input_count += len(inputs)
        output_count += len(outputs)
        check('recorded_inputs_outputs_' + gate['gate'], evidence['schema_version'] == 2
              and evidence['run']['status'] == 'completed' and evidence['run']['exit_status'] == 0
              and pins(inputs) and pins(outputs) and all(x['sha256_after'] == x['sha256'] for x in inputs))
    counts.update(recorded_bounded_gates=len(gates), gate_input_artifact_rows=input_count, gate_output_artifact_rows=output_count)
    check('additional_recorded_check_bindings', all(sha(root / x['script']) == x['script_sha256']
          and sha(root / x['input']) == x['input_sha256'] and sha(root / x['result']) == x['result_sha256']
          for x in computation['additional_checks']))
    junit_dir = root / 'verification/monograph_checks/run_pytest_20261010_release'
    junit = ET.parse(junit_dir / 'pytest.xml').getroot()
    suites = list(junit.iter('testsuite'))
    measured = {key: sum(int(s.get(key, '0')) for s in suites) for key in ['tests', 'failures', 'errors', 'skipped']}
    check('recorded_pytest_junit_counts', measured == {'tests': 34, 'failures': 0, 'errors': 0, 'skipped': 0}
          == load(junit_dir / 'result.json')['junit_counts'])
    replay = load(root / 'verification/closure_2026-10-10/REBUILD_REPLAY.json')
    first = load(root / 'verification/closure_2026-10-10/predecessor_rebuild_retry.json')
    check('failed_first_replay_retained', first['status'] == 'FAIL' and first['documents'][2]['extracted_text_match'] is False
          and all(x['page_count_match'] for x in first['documents']))
    check('accepted_second_replay_current_bindings', replay['status'] == 'PASS' and len(replay['documents']) == 3
          and all(x['pdf_byte_identical'] and x['page_count_match'] and x['extracted_text_match']
                  and x['pdf_sha256'] == x['shipped_pdf_sha256'] == d['sha256']
                  for x, d in zip(replay['documents'], edition['documents'])))
    check('retained_lean_reflow_boundary', len(preservation['pdf_body_conservation'][2]['pages_with_text_reflow']) == 16
          and all(x['body_token_sequence_identical'] for x in preservation['pdf_body_conservation']))
    closure = load(root / 'verification/RELEASE_CLOSURE.json')
    check('closure_twelve_report_pins', len(closure['reports']) == 12 and pins(closure['reports']))
    check('inherited_proofreading_report_pin', pins([closure['inherited_proofreading_report']]))
    buildlog = load(root / 'verification/closure_2026-10-10/BUILD_LOG_REVIEW.json')
    check('final_build_log_pins', all(sha(root / x['log']) == x['sha256'] for x in buildlog['documents']))
    corpus = load(root / 'verification/closure_2026-10-10/CORPUS_ARITHMETIC.json')
    corpus_source = root / 'source/strengthened/PSC_Paper_VIII_Strengthened_Annals_Edition_Package/verification/benchmark_results_sanitized.json'
    check('historical_corpus_identity', sha(corpus_source) == corpus['corpus_sha256'] and corpus['rows'] == 154
          and corpus['ratio_fields_checked'] == 264 and corpus['gflops_fields_checked'] == 146 and corpus['failures'] == [])
    counts.update(historical_corpus_rows=154, recorded_ratio_fields=264, recorded_gflops_fields=146)
    # Consume only separately produced read-only receipts; never call a scientific runner.
    for name, status in [('INHERITED_INTEGRITY_RUN', 'PASS'), ('PUBLICATION_SOURCE_BINDING_CHECK', 'PASS_FOR_STATED_SCOPE')]:
        path = output / (name + '.json')
        check('safe_existing_' + name, path.is_file() and load(path)['status'] == status)
    formal_path = output / 'FORMAL_STATIC_AUDIT.json'
    if formal_path.is_file():
        formal = load(formal_path)
        check('independent_formal_static_audit', formal.get('status') == 'PASS', formal)
    facts = {
        'formal': 'Inherited September 6 v0.6.0 evidence:56 finite manuscript items,392 declarations in40 modules,66 separate constructions,4 classical inputs. No new compilation.',
        'original_manifest': '2710 list-format rows+self. Existing VII-style checker ignores top-level schema and accepts strict list schema unchanged on Linux. It lacks strict duplicate/symlink/canonical-path defenses and uses platform-native path strings.',
        'safe_existing_checks': 'Integrity and publication consistency authenticate bytes,9 reader copies/navigation/source pins/12 saved gate manifests and outputs/7 mathematical parts/22 figure identities/current replay. They do not rerun computations.',
        'replay_history': 'First strict replay failed per-page text matching on16 Lean-guide pages. Body token sequence was conserved. Current refrozen3PDFs have a retained successful byte-identical second replay; no TeX run in this audit.',
        'performance_boundary': '154 historical sanitized rows and saved264ratio/146GFLOPS arithmetic checks are authenticated, not device execution. Incomplete source-value/correctness-reference provenance and resident-vs-device-resident scopes remain explicit limits. No GPU or CUDA validation.',
        'historical_metadata': 'Earlier October6 metadata/October8 retrieved-reader discrepancies and pre-monograph reports remain archived and superseded by current October10 closure. Historical whole-predecessor archive identities are recorded, not independently recovered in this delivery.',
        'builds': 'build_pdfs.py --check-only compiles in temporary work; it was deliberately not run. Documentation generators and guide static scripts may write in place; none run.',
        'rights': 'This is a byte/source/evidence audit, not a new rights or whole-paper mathematical audit.'
    }
    failures = [x for x in checks if x['status'] == 'FAIL']
    report = {'schema': 'komorebi.paper-viii.freeze-baseline-integrity/1', 'status': 'FAIL' if failures else 'PASS',
              'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'root': str(root), 'outer_archive': str(outer),
              'checks_passed': len(checks) - len(failures), 'checks_total': len(checks), 'counts': counts,
              'failures': failures, 'checks': checks, 'scope_and_limits': facts,
              'no_fresh_scientific_compiler_tex_or_control_runs': True,
              'audit_harness_history': 'The first audit-only harness compared protected_part_math_token_changes with integer0, but this field is the accepted empty list. Its sole failed predicate was corrected to []; the first result is retained as FIRST_AUDIT_HARNESS_RESULT.json. No baseline/scientific source/evidence was modified.'}
    (output / 'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    prose = [f"Paper VIII baseline integrity: {report['status']}", f"{report['checks_passed']}/{len(checks)} checks passed.",
             f"Core: 2,711 regular files; 2,710 manifest entries plus manifest. Outer delivery: 3 files, including original core ZIP.",
             f"1,062 retrieved scientific files and 258 editable markup pins authenticated; both recovery ZIP payloads match exactly.",
             f"12 inherited bounded gates: {input_count:,} input rows and {output_count} output rows authenticated; no suites rerun."]
    prose += [key + ': ' + value for key, value in facts.items()]
    prose.append('Audit harness history: ' + report['audit_harness_history'])
    if failures:
        prose.append('FAILURES: ' + json.dumps(failures))
    (output / 'BASELINE_INTEGRITY_AUDIT.txt').write_text('\n\n'.join(prose) + '\n')
    print(json.dumps({'status': report['status'], 'checks_passed': report['checks_passed'], 'checks_total': len(checks), 'counts': counts, 'failures': failures}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=TASK / 'baseline/core/Komorebi_Paper_VIII_Final_2026-10-10')
    parser.add_argument('--outer', type=Path, default=TASK / 'inputs/Paper_VIII_Latest_2026-10-11.zip')
    parser.add_argument('--delivery', type=Path, default=TASK / 'baseline/delivery')
    parser.add_argument('--output', type=Path, default=TASK / 'audit_integrity')
    args = parser.parse_args()
    raise SystemExit(audit(args.root, args.outer, args.delivery, args.output))
