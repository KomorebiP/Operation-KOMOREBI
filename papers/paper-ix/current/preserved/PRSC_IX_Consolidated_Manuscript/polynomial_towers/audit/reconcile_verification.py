#!/usr/bin/env python3
"""Independently reconcile a finished tower gate with exact on-disk evidence.

This does not run a second Lean kernel. It checks the final reported proof run,
all source/control hashes, all output hashes, all log hashes and expectations,
and the complete explicit axiom closure inventory.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report_path = args.report.resolve()
    run_dir = report_path.parent
    r = json.loads(report_path.read_text())
    assert r['status'] == 'PASS'
    assert r['fresh_project_compilation'] is True
    assert r['mathlib_rebuilt'] is False
    assert r['warnings_as_errors'] is True
    assert set(r['allowed_axioms']) == ALLOWED
    assert '4.34.0-rc2' in r['runtime']['lean']
    assert r['runtime']['mathlib_revision'] == 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
    assert digest(ROOT/'inventory.json') == r['inventory_sha256']
    inv = json.loads((ROOT/'inventory.json').read_text())
    assert inv == r['source_inventory']
    entries = inv['modules'] + inv['contracts']
    assert len(inv['modules']) == r['module_count']
    assert len(inv['contracts']) == r['statement_contracts']
    assert len(inv['negative_controls']) == r['negative_controls']
    assert {p.stem for p in (ROOT/'formalization').glob('*.lean')} == {e['module'] for e in inv['modules']}
    assert {p.stem for p in (ROOT/'contracts').glob('*.lean')} == {e['module'] for e in inv['contracts']}
    assert {str(p.relative_to(ROOT)) for p in (ROOT/'controls').glob('Invalid*.lean')} == {e['source'] for e in inv['negative_controls']}
    source_hashes = {}
    for e in entries + inv['negative_controls']:
        p = ROOT/e['source']
        assert p.is_file() and not p.is_symlink()
        assert digest(p) == e['sha256'], str(p)
        source_hashes[e['source']] = e['sha256']
    declarations = [d for e in entries for d in e['declarations']]
    names = {d['name'] for d in declarations}
    assert len(names) == len(declarations) == r['explicit_declaration_audits']
    assert dict(Counter(d['kind'] for d in declarations)) == r['declarations']
    audit_log = (run_dir/'PolynomialTowersAxiomAudit.log').read_text()
    pattern = re.compile(r"'([^']+)'\s+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)", re.S)
    found = {}
    for m in pattern.finditer(audit_log):
        assert m[1] not in found
        ax = sorted(x.strip() for x in (m[2] or '').split(',') if x.strip())
        assert set(ax) <= ALLOWED
        found[m[1]] = ax
    assert set(found) == names
    assert found == r['axiom_dependencies']
    for item in r['runs']:
        log = run_dir/item['log']
        assert digest(log) == item['log_sha256']
        txt = log.read_text()
        assert item['passed'] is True
        if item['expected_error'] is None:
            assert item['exit_code'] == 0
            assert not re.search(r'error:|PANIC', txt)
        else:
            assert item['exit_code'] == 1
            assert 'error:' in txt
            assert re.search(item['expected_error'], txt, re.I)
            assert not re.search(r'unknown module|unknown constant|does not exist|PANIC|timed out', txt, re.I)
    expected_runs = ['LeanVersion']+[e['module'] for e in entries]+['PolynomialTowersAxiomAudit']+[Path(e['source']).stem for e in inv['negative_controls']]
    assert [e['name'] for e in r['runs']] == expected_runs
    for e in entries:
        item = next(x for x in r['runs'] if x['name']==e['module'])
        assert item['command'][-1] == str(ROOT/e['source'])
        assert item['command'][item['command'].index('--import-dir')+1] == str(run_dir/'build')
        assert item['command'][item['command'].index('--output')+1] == str(run_dir/'build'/(e['module']+'.olean'))
    actual_build = {p.name:digest(p) for p in (run_dir/'build').iterdir() if p.is_file()}
    assert actual_build == r['build_files']
    assert all(not p.is_symlink() for p in (run_dir/'build').iterdir())
    for key, path in [('verifier_sha256', 'scripts/verify_polynomial_towers.py'),
                      ('source_audit_sha256','scripts/source_audit.py'),
                      ('runner_sha256','scripts/check_low_memory.py')]:
        assert digest(ROOT/path) == r[key]
    result = {
        'status':'PASS', 'scope':'Independent evidence reconciliation, not an independent kernel implementation',
        'report':str(report_path.relative_to(ROOT)) if report_path.is_relative_to(ROOT) else str(report_path),
        'report_sha256':digest(report_path),
        'script_sha256':digest(Path(__file__)), 'module_count':len(inv['modules']),
        'statement_contracts':len(inv['contracts']), 'negative_controls':len(inv['negative_controls']),
        'source_and_control_hashes_checked':len(source_hashes),
        'explicit_declaration_audits_checked':len(names), 'build_hashes_checked':len(actual_build),
        'gate_logs_and_expectations_checked':len(r['runs']),
        'declarations':r['declarations'], 'source_hashes':source_hashes,
        'allowed_axioms':sorted(ALLOWED), 'original_gate_seconds':r['seconds']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},indent=2))

if __name__=='__main__':
    main()
