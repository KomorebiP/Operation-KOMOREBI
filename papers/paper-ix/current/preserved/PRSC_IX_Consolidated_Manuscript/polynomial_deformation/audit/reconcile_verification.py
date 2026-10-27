#!/usr/bin/env python3
"""Independent read-only reconciliation of the frozen deformation gate.

Does not import the builder's verification or source-audit scripts. It checks
the reported bytes, compiler results, explicit declarations, and axiom closure.
No claim of an independent Lean kernel implementation is made.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip_comments_and_strings(s):
    out = []; i = 0; depth = 0; in_string = False
    while i < len(s):
        pair = s[i:i+2]
        if depth:
            if pair == '/-': depth += 1; out.extend('  '); i += 2; continue
            if pair == '-/': depth -= 1; out.extend('  '); i += 2; continue
            out.append('\n' if s[i] == '\n' else ' '); i += 1; continue
        if in_string:
            if s[i] == '\\': out.extend('  '); i += 2; continue
            if s[i] == '"': in_string = False
            out.append('\n' if s[i] == '\n' else ' '); i += 1; continue
        if pair == '/-': depth = 1; out.extend('  '); i += 2; continue
        if pair == '--':
            end = s.find('\n', i)
            if end < 0: break
            out.extend(' ' * (end-i)); i = end; continue
        if s[i] == '"': in_string = True; out.append(' '); i += 1; continue
        out.append(s[i]); i += 1
    assert depth == 0 and not in_string
    return ''.join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--gate', type=Path, default=Path('polynomial_deformation/replay_01'))
    p.add_argument('--output', type=Path, default=Path('polynomial_deformation/audit/reconciliation.json'))
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    gate = args.gate.resolve()
    report_path = gate/'polynomial_deformation_verification.json'
    report = json.loads(report_path.read_text())
    inv_path = root/'inventory.json'
    inv = json.loads(inv_path.read_text())
    assert report['status'] == 'PASS'
    assert report['inventory_sha256'] == digest(inv_path)
    assert report['source_inventory'] == inv
    assert report['fresh_project_compilation'] is True
    assert report['warnings_as_errors'] is True
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    assert set(report['allowed_axioms']) == allowed
    entries = inv['modules'] + inv['control_support'] + inv['contracts']
    expected = {}; source_hashes = {}
    for e in entries:
        path = root/e['source']
        h = digest(path)
        assert h == e['sha256'], path
        source_hashes[e['source']] = h
        clean = strip_comments_and_strings(path.read_text())
        ns = re.findall(r'^namespace\s+([\w.]+)', clean, re.M)
        assert len(ns) == 1 and ns[0].startswith('Komorebi.')
        decls = [{'kind': kind, 'name': ns[0]+'.'+name}
                 for kind, name in re.findall(r'\b(theorem|lemma|def|abbrev)\s+([A-Za-z_]\w*)', clean)]
        assert decls == e['declarations'], path
        for d in decls:
            assert d['name'] not in expected
            expected[d['name']] = d['kind']
        assert re.search(r'\b(sorry|admit|axiom|unsafe|native_decide|implemented_by)\b', clean) is None
        assert re.search(r'debug\.skipKernelTC|Lean\.addDecl|ofReduceBool|ofReduceNat', clean) is None
        assert re.search(r'set_option\s+(maxHeartbeats|maxRecDepth)\s+0', clean) is None
    for e in inv['negative_controls']:
        h = digest(root/e['source']); assert h == e['sha256']
        source_hashes[e['source']] = h
    assert {p.stem for p in (root/'formalization').glob('*.lean')} == {e['module'] for e in inv['modules']}
    assert {p.stem for p in (root/'contracts').glob('*.lean')} == {e['module'] for e in inv['contracts']}
    assert {p.name for p in (root/'controls').glob('Invalid*.lean')} == {Path(e['source']).name for e in inv['negative_controls']}
    assert {e['module'] for e in inv['control_support']} == {'PolynomialDeformationControls'}
    expected_runs = ['LeanVersion'] + [e['module'] for e in entries] + ['PolynomialDeformationAxiomAudit'] + [Path(e['source']).stem for e in inv['negative_controls']]
    assert [r['name'] for r in report['runs']] == expected_runs
    logs = {}
    for r in report['runs']:
        log = gate/r['log']; assert digest(log) == r['log_sha256']
        text = log.read_text(); assert r['passed'] is True
        assert re.search('PANIC|timed out|unknown module|unknown constant', text, re.I) is None
        if r['expected_error'] is None:
            assert r['exit_code'] == 0 and 'error:' not in text
        else:
            assert r['exit_code'] == 1 and 'error:' in text
            assert re.search(r['expected_error'], text, re.I)
        logs[r['name']] = {'exit_code': r['exit_code'], 'sha256': digest(log)}
    axiom_text = (gate/'PolynomialDeformationAxiomAudit.log').read_text()
    axioms = {}
    for m in re.finditer(r"'([^']+)'\s+(?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)", axiom_text, re.S):
        assert m[1] not in axioms
        axioms[m[1]] = sorted(x.strip() for x in (m[2] or '').split(',') if x.strip())
        assert set(axioms[m[1]]) <= allowed
    assert set(axioms) == set(expected)
    assert axioms == report['axiom_dependencies']
    assert len(expected) == report['explicit_declaration_audits']
    assert dict(collections.Counter(expected.values())) == report['declarations']
    assert report['module_count'] == len(inv['modules'])
    assert report['statement_contracts'] == len(inv['contracts'])
    assert report['positive_control_modules'] == len(inv['control_support'])
    assert report['negative_controls'] == len(inv['negative_controls'])
    compiled = {p.name: digest(p) for p in (gate/'build').iterdir() if p.is_file()}
    assert compiled == report['build_files']
    for e in entries:
        assert e['module']+'.olean' in compiled
    for field, path in [('verifier_sha256',root/'scripts/verify_polynomial_deformation.py'), ('source_audit_sha256',root/'scripts/source_audit.py'), ('runner_sha256',root/'scripts/check_low_memory.py')]:
        assert report[field] == digest(path)
    preserved = {}
    for e in inv['modules']:
        old = root.parent/'polynomial_towers'/e['source']
        if old.exists():
            assert digest(old) == e['sha256']
            preserved[e['source']] = digest(old)
    result = {
        'status':'PASS', 'claim_id':inv['claim_id'],
        'method':'Independent script, no imports of builder audit code; bytes and logged kernel results reconciled',
        'verification_report_sha256':digest(report_path),
        'report_sha256':digest(report_path),
        'inventory_sha256':digest(inv_path),
        'source_and_control_count':len(source_hashes), 'source_and_control_hashes':source_hashes,
        'preserved_previous_module_count':len(preserved), 'preserved_previous_modules':preserved,
        'gate_count':len(logs), 'gate_logs':logs,
        'compiled_file_count':len(compiled), 'compiled_file_hashes':compiled,
        'explicit_declaration_audits':len(axioms), 'declarations':dict(collections.Counter(expected.values())),
        'allowed_axioms':sorted(allowed), 'axiom_closures':axioms,
        'reconciliation_script_sha256':digest(Path(__file__)),
        'limitations':['Same pinned Lean kernel and precompiled Mathlib; no second kernel or fresh Mathlib rebuild', 'Negative controls guard their explicit false statements, not all possible edits']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','verification_report_sha256','inventory_sha256','source_and_control_count','gate_count','compiled_file_count','explicit_declaration_audits','declarations']},indent=2))


if __name__ == '__main__':
    main()
