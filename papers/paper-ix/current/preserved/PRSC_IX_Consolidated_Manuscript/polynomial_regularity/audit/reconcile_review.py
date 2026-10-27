#!/usr/bin/env python3
"""Independently reconcile a frozen raw-proof review with a completed fresh gate.

This checks evidence provenance; it is not a substitute for the raw proof review.
Run immediately after a fresh gate, while its compiled output files still exist.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gate-dir', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    gate = args.gate_dir.resolve()
    report_path = gate / 'polynomial_regularity_verification.json'
    report = json.loads(report_path.read_text())
    review = json.loads((root / 'audit/REVIEWED_SOURCES.json').read_text())
    inventory = json.loads((root / 'inventory.json').read_text())
    assert report['status'] == 'PASS'
    assert report['fresh_project_compilation'] and report['warnings_as_errors']
    assert report['source_inventory'] == inventory
    assert report['inventory_sha256'] == sha(root / 'inventory.json')
    assert report['target_contract_sha256'] == sha(root / 'TARGET_CONTRACT.json')
    for field, relative in [
        ('verifier_sha256', 'scripts/verify_polynomial_regularity.py'),
        ('source_audit_sha256', 'scripts/source_audit.py'),
        ('source_audit_regression_sha256', 'scripts/check_source_audit.py'),
        ('inventory_generator_sha256', 'scripts/generate_regularity_inventory.py'),
        ('runner_sha256', 'scripts/check_low_memory.py'),
    ]:
        assert report[field] == sha(root / relative), field

    for entry in review['reviewed_project_sources']:
        assert sha(root.parent / entry['path']) == entry['sha256'], entry['path']
    exposition = review['exposition_review']
    assert sha(root.parent / exposition['path']) == exposition['sha256']
    reviewed_target = review['target_contract']
    assert sha(root.parent / reviewed_target['path']) == reviewed_target['sha256']
    assert reviewed_target['sha256'] == report['target_contract_sha256']
    assert sha(root / review['full_record']) == review['full_record_sha256']
    raw_record = json.loads((root / review['full_record']).read_text())
    route_audit = raw_record['route_audit']
    assert sha(root / route_audit['path']) == route_audit['sha256']
    local_source_record = raw_record['local_source_record']
    assert sha(root / local_source_record['path']) == local_source_record['sha256']
    for entry in review.get('release_document_review', []):
        path = root.parent / entry['path']
        if not path.exists():
            path = root.parent / entry['package_path']
        assert sha(path) == entry['sha256'], entry['path']

    entries = inventory['modules'] + inventory['control_support'] + inventory['contracts']
    all_sources = entries + inventory['negative_controls']
    for entry in all_sources:
        assert sha(root / entry['source']) == entry['sha256'], entry['source']
    expected_names = {d['name'] for e in entries for d in e['declarations']}
    counts = Counter(d['kind'] for e in entries for d in e['declarations'])
    assert counts == report['declarations']
    assert len(expected_names) == report['explicit_declaration_audits']
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    assert set(report['allowed_axioms']) == allowed
    assert set(report['axiom_dependencies']) == expected_names
    for name, dependencies in report['axiom_dependencies'].items():
        assert set(dependencies) <= allowed, name

    # Re-read the actual compiler output using exact declared-name prefixes,
    # independently of the gate's regular-expression parser.
    axiom_text = (gate / 'PolynomialRegularityAxiomAudit.log').read_text()
    assert sum(line.startswith("'") for line in axiom_text.splitlines()) == len(expected_names)
    for name in expected_names:
        prefix = f"'{name}' depends on axioms: ["
        empty = f"'{name}' does not depend on any axioms"
        assert axiom_text.count(prefix) + axiom_text.count(empty) == 1, name
        if prefix in axiom_text:
            body = axiom_text.split(prefix, 1)[1].split(']', 1)[0]
            actual_dependencies = {s.strip() for s in body.split(',') if s.strip()}
        else:
            actual_dependencies = set()
        assert actual_dependencies == set(report['axiom_dependencies'][name]), name

    for run in report['runs']:
        log = gate / run['log']
        assert sha(log) == run['log_sha256'], run['name']
        text = log.read_text()
        assert run['passed'] and not run['timed_out'], run['name']
        if run['expected_error'] is None:
            assert run['exit_code'] == 0, run['name']
            assert not re.search(r'error:|PANIC', text), run['name']
        else:
            assert run['exit_code'] == 1 and 'error:' in text, run['name']
            assert re.search(run['expected_error'], text, re.I), run['name']
            assert not re.search(r'unknown module|unknown constant|PANIC|timed out', text, re.I)

    build = gate / 'build'
    actual_build = {p.name: sha(p) for p in build.iterdir() if p.is_file()}
    assert actual_build == report['build_files']
    for entry in entries:
        assert entry['module'] + '.olean' in actual_build, entry['module']

    inherited_path = root / 'audit/inherited_sources.json'
    inherited = json.loads(inherited_path.read_text())
    assert sha(inherited_path) == report['inherited_source_record_sha256']
    for entry in inherited['modules']:
        assert sha(root / entry['source']) == entry['sha256']
    assert len(inherited['modules']) == report['inherited_modules_preserved']
    for entry in inherited.get('negative_controls', []):
        assert sha(root / entry['source']) == entry['sha256']

    manifest = json.loads((gate / 'computation_manifest.json').read_text())
    assert manifest['result'] == 'PASS' and manifest['run']['exit_status'] == 0
    assert manifest['outputs'][0]['sha256'] == sha(report_path)
    result = {
        'status': 'PASS',
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'raw_proof_verdict': review['verdict'],
        'report': 'verification/polynomial_regularity_verification.json',
        'report_sha256': sha(report_path),
        'inventory_sha256': sha(root / 'inventory.json'),
        'reviewed_sources_record_sha256_before_reconciliation': sha(root / 'audit/REVIEWED_SOURCES.json'),
        'reconciliation_script_sha256': sha(Path(__file__).resolve()),
        'source_files_reconciled': len(all_sources),
        'positive_compiled_modules': len(entries),
        'compiled_files_reconciled': len(actual_build),
        'run_logs_reconciled': len(report['runs']),
        'declaration_axiom_closures_reconciled': len(expected_names),
        'declaration_kinds': dict(counts),
        'inherited_mathematical_sources_unchanged': len(inherited['modules']),
        'inherited_negative_controls_unchanged': len(inherited.get('negative_controls', [])),
        'scope': 'Fresh report, hashes of raw-reviewed sources and exposition, full source inventory, logs, compiled output hashes, independently re-parsed standard axiom closures, inherited-source preservation, and report/manifest linkage. Earlier Paper IX proofs are not independently re-audited here.',
    }
    (root / 'audit/reconciliation.json').write_text(json.dumps(result, indent=2) + '\n')
    review['fresh_release_gate_reconciliation'] = {
        'status': 'PASS', 'report_sha256': result['report_sha256'],
        'record': 'audit/reconciliation.json',
        'record_sha256': sha(root / 'audit/reconciliation.json'),
    }
    (root / 'audit/REVIEWED_SOURCES.json').write_text(json.dumps(review, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
