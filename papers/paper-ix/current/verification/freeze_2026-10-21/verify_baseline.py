#!/usr/bin/env python3
"""Read-only Paper IX distribution/source/evidence identity audit.

No archived checker, compiler, finite suite, generator, parser control or TeX
build is run. ZIPs are streamed. Safe live-checker receipts are read separately.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import stat
import zipfile

TASK = Path('/dev/shm/komorebi_paper_ix_freeze_fbc994080222')
ARCHIVE_SHA = '785d0a66c0b1caef1c673fd19185aa3a92c8fbe494847476855d91f19376d9a4'
STRICT_SHA = 'dff3d8725afdd6b93c97802827ca9233ab8099ced2bdb88f933ab20ba3c41b58'


def stream_sha(stream):
    h = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        h.update(chunk)
    return h.hexdigest()


def sha(path):
    with path.open('rb') as f:
        return stream_sha(f)


def read(path):
    return json.loads(path.read_text())


def safe(name):
    p = PurePosixPath(name)
    return (bool(name) and ':' not in name and '\\' not in name
            and not p.is_absolute() and p.as_posix() == name
            and all(x not in ('', '.', '..') for x in name.split('/')))


def archive_rows(path):
    with zipfile.ZipFile(path) as z:
        infos = z.infolist()
        assert len({x.filename for x in infos}) == len(infos), 'duplicate ZIP paths'
        assert all(safe(x.filename.rstrip('/')) for x in infos), 'unsafe ZIP path'
        assert all(not stat.S_ISLNK(x.external_attr >> 16) for x in infos), 'ZIP symlink'
        rows = {}
        for x in infos:
            if x.is_dir():
                continue
            with z.open(x) as f:
                rows[x.filename] = {'bytes': x.file_size, 'sha256': stream_sha(f)}
        return rows  # full EOF reads additionally check every regular member CRC


def audit(root, archive, output):
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    counts = {}

    def check(name, condition, detail=None):
        checks.append({'check': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})

    def pins(rows):
        return all(safe(x['path']) and (root / x['path']).is_file() and sha(root / x['path']) == x['sha256']
                   and ('bytes' not in x or (root / x['path']).stat().st_size == x['bytes']) for x in rows)

    files = {p.relative_to(root).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)}
             for p in root.rglob('*') if p.is_file()}
    check('baseline_no_symlinks', not any(p.is_symlink() for p in root.rglob('*')))
    check('input_archive_bytes_hash', archive.stat().st_size == 335957366 and sha(archive) == ARCHIVE_SHA)
    archived = archive_rows(archive)
    prefix = root.name + '/'
    check('input_archive_expected_root', all(x.startswith(prefix) for x in archived))
    stripped = {p[len(prefix):]: x for p, x in archived.items()}
    check('all_3559_archive_payloads_exact', len(files) == 3559 and stripped == files)
    check('archive_uncompressed_bytes', sum(x['bytes'] for x in archived.values()) == 389717603)
    manifest = read(root / 'MANIFEST_SHA256.json')
    rows = manifest['files']
    check('strict_manifest_schema', manifest['schema'] == 'komorebi.strict_manifest.v1'
          and set(manifest) <= {'schema', 'checkpoint', 'scope', 'edition', 'generated_at_utc', 'files'})
    check('manifest_safe_unique_paths', len({x['path'] for x in rows}) == len(rows) and all(safe(x['path']) for x in rows))
    check('manifest_complete_file_set', len(rows) == 3558 and {x['path'] for x in rows} == set(files) - {'MANIFEST_SHA256.json'})
    check('manifest_all_bytes_sha256', pins(rows))
    counts.update(core_files=len(files), manifest_rows=len(rows))
    e = root / 'verification/2026-10-20'
    preservation = read(e / 'MATHEMATICAL_SOURCE_PRESERVATION.json')
    original = preservation['original_preserved_and_figure_files']
    check('preserved_original_and_figure_hashes', len(original) == len({x['path'] for x in original}) == 2405 and pins(original))
    counts['preserved_original_file_pins'] = sum(x['path'].startswith('preserved/') for x in original)
    counts['preserved_figure_file_pins'] = sum(x['path'].startswith('figures/') for x in original)
    check('preserved_scope_counts', counts['preserved_original_file_pins'] == 2334 and counts['preserved_figure_file_pins'] == 71)
    pinned_preserved = {x['path'] for x in original}
    actual_preserved = {p for p in files if p.startswith(('preserved/', 'figures/'))}
    residue = actual_preserved - pinned_preserved
    check('preserved_inventory_and_transfer_residue_accounted', not pinned_preserved - actual_preserved and len(residue) == 1
          and all(files[p]['bytes'] == 34340864 and files[p]['sha256'] == 'f1e1f7eb034a3832faf55246c01609416dcbb1dbad7695efe772694947d4d605'
                  and not zipfile.is_zipfile(root / p) for p in residue))
    counts['all_preserved_regular_files'] = sum(p.startswith('preserved/') for p in files)
    counts['additional_incomplete_transfer_residues'] = len(residue)
    tex = preservation['source_tex_files']
    check('108_tex_file_bindings', len(tex) == len({x['path'] for x in tex}) == 108 and pins(tex))
    environments = ('theorem', 'proposition', 'lemma', 'corollary', 'definition', 'remark', 'example',
                    'histtheorem', 'histproposition', 'histlemma', 'histcorollary', 'histdefinition',
                    'histremark', 'histexample', 'histstandardfact')
    body = re.compile(r'\\begin\{(' + '|'.join(environments) + r')\}(.*?)\\end\{\1\}', re.S)
    proof = re.compile(r'\\begin\{proof\}(.*?)\\end\{proof\}', re.S)
    counts['current_tex_files'] = len(tex)
    counts['numbered_environment_bodies'] = counts['proof_bodies'] = 0
    bodies_equal = recorded_counts_equal = True
    changed = []
    for row in tex:
        p = root / row['path']
        text = p.read_text()
        old = e / 'predecessor_files' / row['path']
        if row['sha256'] != row['baseline_sha256']:
            changed.append(row['path'])
            assert old.is_file() and sha(old) == row['baseline_sha256'], 'changed TeX predecessor binding'
            before = old.read_text()
        else:
            before = text
        n, pr = len(body.findall(text)), len(proof.findall(text))
        counts['numbered_environment_bodies'] += n
        counts['proof_bodies'] += pr
        recorded_counts_equal &= (n == row['numbered_environment_bodies'] and pr == row['proof_bodies'])
        bodies_equal &= (body.findall(text) == body.findall(before) and proof.findall(text) == proof.findall(before))
    check('201_environment_153_proof_counts', recorded_counts_equal and counts['numbered_environment_bodies'] == 201 and counts['proof_bodies'] == 153)
    check('all_mathematical_bodies_unchanged', bodies_equal and preservation['mathematical_statement_or_proof_token_changes'] == [])
    check('exact_three_presentational_tex_changes', sorted(changed) == sorted(preservation['changed_tex_files']) and len(changed) == 3)
    history = read(root / 'recovered_history/HISTORICAL_RECOVERY_REPORT.json')
    historical_zip = root / 'recovered_history' / history['source_archive']['name']
    check('recovered_historical_archive_identity', historical_zip.stat().st_size == history['source_archive']['bytes']
          and sha(historical_zip) == history['source_archive']['sha256'])
    history_rows = archive_rows(historical_zip)
    historical_prefix = history['source_archive']['name'][:-4] + '/'
    recovered_rows = {p[len(historical_prefix):]: x for p, x in history_rows.items()}
    check('historical_archive_62_files_exact_inventory', len(recovered_rows) == 62 and recovered_rows == {x['path']: {'bytes': x['bytes'], 'sha256': x['sha256']} for x in history['inventory']})
    with zipfile.ZipFile(historical_zip) as z:
        historical_manifest = z.read(historical_prefix + 'MANIFEST.sha256').decode()
        parsed = [line.split(None, 1) for line in historical_manifest.splitlines() if line.strip()]
        normalized = [(pin, path[2:] if path.startswith('./') else path) for pin, path in parsed]
        check('historical_61_row_manifest', len(normalized) == 61 and {p for _, p in normalized} == set(recovered_rows) - {'MANIFEST.sha256'}
              and all(recovered_rows[p]['sha256'] == pin for pin, p in normalized))
        bib_name = history['bibliography']['path']
        source_bib = z.read(historical_prefix + bib_name)
        check('recovered_bibliography_exact_22_keys', len(history['bibliography']['keys']) == 22
              and source_bib == (root / 'recovered_history/PSC_Paper_IX_Local_Polyphase_Annals_Edition.bib').read_bytes()
              == (root / 'recovered_history/PSC_Paper_IX_Strengthened_Annals_Edition.bib').read_bytes())
    figures = history['figures']['files']
    check('14_original_historical_figures', len(figures) == 14 and all(recovered_rows[x['path']] == {'bytes': x['bytes'], 'sha256': x['sha256']}
          and x['pages'] == 1 and x['raster_image_objects'] == 0 for x in figures))
    # Existing large preserved ZIPs are streamed independently; no archive tree is copied.
    nested_counts = {}
    for p in sorted((root / 'preserved').rglob('*.zip')):
        nested_counts[p.relative_to(root).as_posix()] = len(archive_rows(p))
    check('three_preserved_archives_safe_crc', len(nested_counts) == 3, nested_counts)
    counts.update(recovered_original_figures=14, recovered_bibliography_keys=22, historical_archive_files=62)
    bib = read(e / 'BIBLIOGRAPHY_REPAIR.json')
    check('current_bibliography_repair_pins', bib['status'] == 'PASS' and bib['resolved_historical_entries'] == 22
          and bib['remaining_unidentified_historical_keys'] == []
          and pins([bib['input_bib'], bib['corrected_bib'], bib['rendered_fragment']]) and pins(bib['recovered_artifacts'])
          and bib['theorem_application_audit'] is False and bib['reconstructed_current_artwork_replaced'] is False)
    release = read(root / 'RELEASE.json')
    check('current_six_reader_copies', len(release['documents']) == 3 and release['total_pdf_pages'] == 396
          and [x['pages'] for x in release['documents']] == [232, 25, 139]
          and all(sha(root / row[key]) == row['sha256'] and (root / row[key]).stat().st_size == row['bytes']
                  for row in release['documents'] for key in ['file', 'mirror']))
    check('release_source_revision_pins', all(sha(root / p) == pin for p, pin in release['source_revision'].items()))
    finite = read(e / 'finite/FINITE_REPLAY.json')
    check('nine_recorded_gate_set', len(finite['runs']) == 9 and finite['status'] == 'PASS_STATED_FINITE_SCOPE'
          and finite['script_sha256'] == sha(root / 'scripts/replay_finite.py'))
    inputs = outputs = 0
    for row in finite['runs']:
        manifest = read(root / row['manifest'])
        inputs += len(manifest['input_artifacts'])
        outputs += len(manifest['outputs'])
        check('gate_identity_' + row['suite'], manifest['schema_version'] == 2 and manifest['run']['status'] == 'completed'
              and manifest['run']['exit_status'] == 0 and pins(manifest['input_artifacts']) and pins(manifest['outputs'])
              and all(x['sha256_after'] == x['sha256'] for x in manifest['input_artifacts']))
    counts.update(recorded_bounded_gates=9, gate_input_artifact_rows=inputs, gate_output_artifact_rows=outputs)
    controls = read(e / 'integrity_controls/CONTROLS.json')
    check('exact_current_strict_verifier_code', sha(root / 'scripts/verify_integrity.py') == STRICT_SHA)
    check('recorded_21_integrity_controls_bind', controls['status'] == 'PASS' and controls['test_methods'] == 21
          and controls['failures'] == controls['errors'] == controls['skips'] == 0
          and set(controls['source_sha256']) == {'verify_integrity.py', 'test_integrity.py'}
          and all(sha(root / 'scripts' / name) == pin for name, pin in controls['source_sha256'].items()))
    replay = read(e / 'FINAL_PDF_REPLAY.json')
    check('recorded_pdf_replay_exact_scope', replay['status'] == 'PASS' and len(replay['documents']) == 3
          and all(not r['byte_identical'] and r['identical_except_trailer_id'] and r['page_count_match']
                  and r['extracted_text_match'] and r['frozen_sha256'] == d['sha256']
                  for r, d in zip(replay['documents'], release['documents'])))
    qa = read(e / 'PUBLICATION_QA.json')
    check('recorded_visual_review_pins', qa['status'] == 'PASS' and qa['total_pages'] == 396
          and qa['selected_detail_pages'] == 47 and pins(qa['portable_captures']) and pins(qa['review_reports']))
    docpins = read(e / 'FINAL_DOCUMENTATION_PINS.json')
    check('dated_documentation_pins', docpins['status'] == 'PASS' and pins(docpins['files']))
    existing = output / 'SAFE_EXISTING_RELEASE_CHECK.json'
    check('safe_existing_release_checker', existing.is_file() and read(existing)['status'] == 'PASS')
    formal_path = output / 'FORMAL_STATIC_AUDIT.json'
    if formal_path.is_file():
        formal = read(formal_path)
        check('independent_formal_static_audit', formal['status'] == 'PASS', formal)
    limitations = {
        'formal_scope': 'Inherited external Nishibuchi capstone and individually identified arithmetic/dyadic/lifting endpoints. The 15 frontiers,644 sources,713 logs,202 links and515 parser records are distinct units, not newly compiled full-paper coverage. Expanded mixed/factorial/all-rank/radius routes remain written proofs. Four legacy affine fingerprints have no original log digests.',
        'compiler_boundary': 'No Lean/Lake/compiler or control reruns. sources/lean/audit_sources.py would rerun historical parser negative controls and was deliberately not executed. Saved source/log/axiom identities are authenticated statically.',
        'pdf_replay': 'Inherited October20 per-page text/page matches and trailer-ID-normalized byte identity are authenticated. All3 raw PDF byte-identity flags are false. Earlier source-faithfulness failures and bibliography formatter failure remain retained.',
        'historical_recovery': 'Exact62-file historical archive,22 bibliography identities and14 original vector figures recovered. Current corrected reconstructions remain distinct. No external theorem-application or whole-manuscript correctness audit is claimed.',
        'preservation_counts': 'The2,405 scientific preservation pins consist of2,334 preserved/ files and71 figures/ files. There are2,335 actual preserved/ regular files: one extra34,340,864-byte incomplete ZIP transfer residue is covered by the complete root manifest/input archive, but is not a complete archive or scientific preservation pin. The complete Euler archive is separately retained and authenticated. All packaging bytes must remain preserved.',
        'documentation_adapter': 'Existing strict verifier uses schema komorebi.strict_manifest.v1 and the accepted6metadata fields, SHA ' + STRICT_SHA + '. No root-manifest digest or README requirement in the live checker. Keep scripts unchanged. FINAL_DOCUMENTATION_PINS.json retains the original README path/hash: after wrapper replacement it is historical and resolves through before/ plus baseline preservation mapping.',
        'research_open': release['open'],
        'safe_live_check': 'verify_release.py --report EXTERNAL invokes strict integrity,PDF/navigation preflight and saved finite-manifest validation only. It does not run scientific suites or the15-frontier reconciliation program.'
    }
    failures = [x for x in checks if x['status'] == 'FAIL']
    report = {'schema': 'komorebi.paper-ix.freeze-baseline-integrity/1', 'status': 'FAIL' if failures else 'PASS',
              'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'baseline_root': str(root), 'archive': str(archive),
              'checks_passed': len(checks)-len(failures), 'checks_total': len(checks), 'counts': counts,
              'checks': checks, 'failures': failures, 'scope_and_limits': limitations,
              'baseline_read_only': True, 'no_fresh_lean_tex_finite_control_or_generator_execution': True,
              'audit_harness_history': 'The first audit used the supplied2,335original/70figure split and assumed no extra transfer residue. Exact receipt inspection establishes2,334original+71figure pins and one additional manifest-covered partial transfer artifact. The initial audit result is retained as FIRST_AUDIT_HARNESS_RESULT.json. Only audit predicates and descriptions changed; no baseline/evidence bytes were modified.'}
    (output / 'BASELINE_INTEGRITY_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    lines = [f"Paper IX baseline integrity: {report['status']} ({report['checks_passed']}/{len(checks)} checks).",
             '3,559 exact archive/baseline files; 3,558 manifest rows plus the manifest itself.',
             '2,334 preserved original-file pins and 71 figure-file pins authenticate. One additional manifest-covered incomplete transfer residue is retained separately. 108 current TeX files preserve 201 numbered environment bodies and 153 proof bodies.',
             f"Nine recorded bounded gates: {inputs:,} input artifact rows and {outputs} output rows authenticate. The current 21-control strict checker/harness receipt authenticates; no suites rerun."]
    lines += [k + ': ' + v for k, v in limitations.items()]
    lines.append('Audit harness history: ' + report['audit_harness_history'])
    if failures:
        lines.append('FAILURES: ' + json.dumps(failures))
    (output / 'BASELINE_INTEGRITY_AUDIT.txt').write_text('\n\n'.join(lines) + '\n')
    print(json.dumps({'status': report['status'], 'checks_passed': report['checks_passed'], 'checks_total': len(checks), 'counts': counts, 'failures': failures}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=TASK / 'baseline/Paper_IX_Final_Release_v1.0.0')
    p.add_argument('--archive', type=Path, default=TASK / 'inputs/Paper_IX_Final_Release_v1.0.0_2026-10-20.zip')
    p.add_argument('--output', type=Path, default=TASK / 'audit_integrity')
    args = p.parse_args()
    raise SystemExit(audit(args.root, args.archive, args.output))
