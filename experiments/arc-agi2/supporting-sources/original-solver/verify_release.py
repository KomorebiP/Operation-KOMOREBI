"""Independent archive checks and direct grid scoring. Author: Komorebi P.

This verifier does not import the solver or evaluation implementation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def direct_score(submission, targets):
    assert set(submission) == set(targets), 'Task sets differ'
    first = second = whole = total = 0
    for key, outputs in targets.items():
        assert len(submission[key]) == len(outputs), 'Output arity differs'
        task_correct = True
        for attempts, expected in zip(submission[key], outputs):
            assert set(attempts) == {'attempt_1', 'attempt_2'}, 'Attempt schema differs'
            one = attempts['attempt_1'] == expected
            either = one or attempts['attempt_2'] == expected
            first += one
            second += either
            total += 1
            task_correct = task_correct and either
        whole += task_correct
    return dict(pass1_exact_outputs=first, pass2_exact_outputs=second,
                whole_tasks=whole, total_outputs=total, total_tasks=len(targets))


def verify(archive, rebuild):
    archive, rebuild = Path(archive), Path(rebuild)
    digest = sha256(archive)
    assert digest == sha256(rebuild), 'Deterministic rebuild differs'
    with zipfile.ZipFile(archive) as z, tempfile.TemporaryDirectory(prefix='block17-package-') as tmp:
        names = z.namelist()
        assert len(names) == len(set(names)), 'Duplicate archive entry'
        manifest = json.loads(z.read('block17/release_manifest.json'))
        expected = {'block17/' + n for n in manifest['files']} | {'block17/release_manifest.json'}
        assert set(names) == expected, 'Archive inventory differs'
        for info in z.infolist():
            path = PurePosixPath(info.filename)
            assert not path.is_absolute() and '..' not in path.parts, 'Unsafe archive path'
            assert info.date_time == (2026, 1, 1, 0, 0, 0), 'Timestamp differs'
            assert info.external_attr >> 16 == 0o644, 'File mode differs'
        for name, expected_file in manifest['files'].items():
            data = z.read('block17/' + name)
            assert len(data) == expected_file['bytes'], 'File size differs: ' + name
            assert hashlib.sha256(data).hexdigest() == expected_file['sha256'], 'File digest differs: ' + name
        targets = json.loads(z.read('block17/evidence/solutions.json'))
        evaluation = json.loads(z.read('block17/results/evaluation.json'))
        scores = {}
        for policy, row in evaluation['policies'].items():
            frozen = json.loads(z.read('block17/results/' + policy + '.json'))
            measured = direct_score(frozen['submission'], targets)
            assert all(row['score'][key] == value for key, value in measured.items()), 'Score differs: ' + policy
            assert measured['total_outputs'] == 1076 and measured['total_tasks'] == 1000
            scores[policy] = measured
        primary = evaluation['primary_policy']
        submission = json.loads(z.read('block17/results/submission.json'))
        primary_frozen = json.loads(z.read('block17/results/' + primary + '.json'))
        assert submission == primary_frozen['submission'], 'Export differs from preregistered primary'
        g47 = direct_score(json.loads(z.read('block17/evidence/g47.json')), targets)
        assert g47['pass2_exact_outputs'] == 864 and g47['whole_tasks'] == 804
        assert all(evaluation['reference_g47'][key] == value for key, value in g47.items())
        repair_scores = {}
        for prefix in ('', 'supported_'):
            frozen = json.loads(z.read('block17/repair_results/' + prefix + 'dispatch.json'))
            measured = direct_score(frozen['submission'], targets)
            recorded = json.loads(z.read('block17/repair_results/' + prefix + 'evaluation.json'))
            assert all(recorded['score'][key] == value for key, value in measured.items()), 'Repair score differs'
            repair_scores[frozen['policy']] = measured
        print('Archive inventory, metadata, deterministic rebuild and direct scores passed.', flush=True)
        z.extractall(tmp)
        root = Path(tmp) / 'block17'
        output = Path(tmp) / 'independent_validation.json'
        log = Path(tmp) / 'independent_validation.log'
        with log.open('w') as stream:
            result = subprocess.run([sys.executable, str(root / 'validate.py'), '--output', str(output)],
                                    cwd=root, stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError('Extracted validation failed:\n' + log.read_text()[-12000:])
        validation = json.loads(output.read_text())
        original_validation = json.loads(z.read('block17/results/validation.json'))
        assert validation == original_validation, 'Extracted validation differs from archived receipt'
        return dict(schema='komorebi.block17.independent_package_verification.v1',
                    author='Komorebi P.', archive=archive.name, archive_sha256=digest,
                    archive_bytes=archive.stat().st_size, files=len(names),
                    deterministic_rebuild_byte_identical=True, manifest_inventory_verified=True,
                    manifest_file_hashes_verified=True, deterministic_metadata_verified=True,
                    direct_grid_scores=scores, primary_policy=primary, g47_reference=g47,
                    direct_geometry_repair_scores=repair_scores,
                    exported_submission_matches_primary=True,
                    extracted_fresh_process_validation_matches_archived_receipt=True,
                    extracted_validation_sha256=sha256(output),
                    extracted_validation=validation,
                    claim_boundary='Exposed public training data; no unseen-set estimate.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--rebuild', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.archive, args.rebuild)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('archive', 'archive_sha256', 'primary_policy', 'files')}, indent=2))
