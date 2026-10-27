#!/usr/bin/env python3
"""Read-only independent reconciliation of the finite-count verification record."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
default_run = 'verification' if (root / 'verification').is_dir() else 'replay_01'
run = (root / (sys.argv[1] if len(sys.argv) > 1 else default_run)).resolve()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
report_path = run / 'polynomial_counts_verification.json'
report = json.loads(report_path.read_text())
assert report['status'] == 'PASS'
assert report['fresh_project_compilation'] is True
assert report['mathlib_rebuilt'] is False
assert report['warnings_as_errors'] is True
assert report['runtime']['mathlib_revision'] == 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
assert '4.34.0-rc2' in report['runtime']['lean']
inventory = json.loads((root / 'inventory.json').read_text())
assert sha(root / 'inventory.json') == report['inventory_sha256']
assert inventory == report['source_inventory']
entries = inventory['modules'] + inventory['contracts']
for entry in entries:
    path = root / entry['source']
    assert not path.is_symlink()
    assert sha(path) == entry['sha256']
for entry in inventory['negative_controls']:
    assert sha(root / entry['source']) == entry['sha256']
assert {p.stem for p in (root / 'formalization').glob('*.lean')} == {e['module'] for e in inventory['modules']}
assert {p.stem for p in (root / 'contracts').glob('*.lean')} == {e['module'] for e in inventory['contracts']}
assert {str(p.relative_to(root)) for p in (root / 'controls').glob('Invalid*.lean')} == {e['source'] for e in inventory['negative_controls']}

originals = {
    'FiniteFiberCounts': root / 'linear/FiniteFiberCounts.lean',
    'PolynomialDigitBridge': root / 'digits/PolynomialDigitBridge.lean',
    'ResidueLiftDigits': root / 'residues/ResidueLiftDigits.lean',
    'IntegerFiniteCokernel': root / 'cokernel/IntegerFiniteCokernel.lean',
    'PolynomialLiftCounts': root / 'counts/PolynomialLiftCounts.lean',
    'AffineObstructionCore': root.parent / 'polynomial_lifting/formalization/AffineObstructionCore.lean',
    'PolynomialTaylor': root.parent / 'polynomial_lifting/formalization/PolynomialTaylor.lean',
    'PolynomialObstruction': root.parent / 'polynomial_lifting/formalization/PolynomialObstruction.lean',
}
for name, path in originals.items():
    if not path.exists() and path.is_relative_to(root):
        path = root / 'development' / path.relative_to(root)
    assert path.read_bytes() == (root / 'formalization' / (name+'.lean')).read_bytes()
for entry in report['runs']:
    log = run / entry['log']
    assert sha(log) == entry['log_sha256']
    assert entry['passed'] is True
    output = log.read_text()
    if entry['expected_error'] is None:
        assert entry['exit_code'] == 0
        assert re.search(r'error:|PANIC', output) is None
    else:
        assert entry['exit_code'] == 1
        assert re.search(entry['expected_error'], output, re.I)
        assert re.search(r'unknown module|unknown constant|does not exist|PANIC|timed out', output, re.I) is None
actual_build = {p.name:sha(p) for p in (run/'build').iterdir() if p.is_file()}
assert actual_build == report['build_files']
assert not any(p.is_symlink() for p in (run/'build').iterdir())

expected = {d['name'] for e in entries for d in e['declarations']}
allowed = {'propext','Classical.choice','Quot.sound'}
output = (run/'PolynomialCountsAxiomAudit.log').read_text()
pattern = r"'([^']+)'\s+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
parsed = {}
for match in re.finditer(pattern, output, re.S):
    name = match[1]
    assert name not in parsed
    deps = sorted(x.strip() for x in (match[2] or '').split(',') if x.strip())
    assert set(deps) <= allowed
    parsed[name] = deps
assert set(parsed) == expected
assert parsed == report['axiom_dependencies']
assert len(parsed) == report['explicit_declaration_audits']
assert len(inventory['modules']) == report['module_count']
assert len(inventory['contracts']) == report['statement_contracts']
assert len(inventory['negative_controls']) == report['negative_controls']
for key, path in [('verifier_sha256','scripts/verify_polynomial_counts.py'),
                  ('source_audit_sha256','scripts/source_audit.py'),
                  ('runner_sha256','scripts/check_low_memory.py')]:
    assert report[key] == sha(root/path)
print(json.dumps({
    'status':'PASS',
    'report_sha256':sha(report_path),
    'source_inventory_sha256':sha(root/'inventory.json'),
    'module_sources':len(inventory['modules']),
    'statement_contracts':len(inventory['contracts']),
    'negative_controls':len(inventory['negative_controls']),
    'original_source_matches':len(originals),
    'run_logs':len(report['runs']),
    'compiled_output_hashes':len(actual_build),
    'explicit_axiom_closures':len(parsed),
    'allowed_axioms':sorted(allowed),
    'observed_runtime_seconds':report['seconds'],
    'scope':'Independent file/record reconciliation and source review; no independent Lean kernel implementation.'
}, indent=2))
