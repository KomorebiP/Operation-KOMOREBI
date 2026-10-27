#!/usr/bin/env python3
"""Verify retained evidence bytes; this is not a mathematical proof checker."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(path, expected):
    actual = digest(ROOT / path)
    if actual != expected:
        raise AssertionError((str(path), expected, actual))


def main():
    manifests = sorted((ROOT / 'verification').glob('**/manifest.json'))
    for path in manifests:
        data = json.loads(path.read_text())
        assert data['run']['status'] == 'completed'
        assert data['run']['exit_status'] == 0
        for entry in data['input_artifacts']:
            check(entry['path'], entry['sha256'])
            assert entry['sha256_after'] == entry['sha256']
        for entry in data['outputs']:
            check(entry['path'], entry['sha256'])
    formal = json.loads((ROOT / 'verification/formal/BLOCK47_FORMAL_VERIFICATION.json').read_text())
    assert formal['status'] == 'PASS_FORMAL_CERTIFICATE_AND_MOD7_ALGEBRA'
    assert formal['theorem_count'] == 21
    assert formal['kernel_replay']['exit_code'] == 0
    assert formal['axiom_audit']['passed']
    assert all(x['passed'] and x['rejected_for_expected_reason'] for x in formal['negative_controls'])
    for name, expected in formal['source_sha256'].items():
        check('lean/' + name, expected)
    check('verification/formal/Beal47Replay.lean', formal['replay_source_sha256'])

    def walk_logs(value):
        if isinstance(value, dict):
            if 'log' in value and 'log_sha256' in value:
                check(value['log'], value['log_sha256'])
            for item in value.values():
                walk_logs(item)
        elif isinstance(value, list):
            for item in value:
                walk_logs(item)
    walk_logs(formal)
    review = json.loads((ROOT / 'verification/good7_global_independent_audit.json').read_text())
    for name, expected in review['reviewed_hashes'].items():
        check(name, expected)
    modular = json.loads((ROOT / 'verification/modular_correlations_receipt.json').read_text())
    for name, expected in modular['files'].items():
        check(name, expected)
    predecessor = json.loads((ROOT / 'predecessor/IDENTITY.json').read_text())
    for name, rec in predecessor.items():
        check('predecessor/' + name, rec['sha256'])
    result = {
        'status': 'PASS_RETAINED_EVIDENCE_HASHES',
        'experiment_manifests_checked': len(manifests),
        'formal_theorems': formal['theorem_count'],
        'canonical_written_theorem': 'Absolute mod-seven RM irreducibility for 14 not dividing C.',
        'canonical_theorem_sha256': digest(ROOT / 'notes/mod7_good_reduction_irreducibility.md'),
        'boundaries': [
            'This script verifies evidence identity and recorded checks, not external arithmetic theorems.',
            'No primitive integer solution or indexed modular form has been eliminated.',
            'The branch 14 dividing C remains outside the irreducibility proof.'
        ]
    }
    (ROOT / 'verification/VERIFICATION_SUMMARY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
