#!/usr/bin/env python3
"""Independently reconcile the recovered chart release's fresh Lean evidence.

This script imports none of the gate's code. It compares the actual source,
inventory, compiler logs and emitted axiom lists with the reported hashes.
It is an evidence audit, not an alternative implementation of Lean's kernel.
Run it after the verification runner, while that runner's build still exists.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def code_only(s):
    """Mask nested Lean comments and quoted strings, retaining line positions."""
    result = []
    offset = nesting = 0
    quoted = False
    while offset < len(s):
        c, pair = s[offset], s[offset:offset+2]
        if nesting:
            if pair == '/-':
                nesting += 1; result.append('  '); offset += 2; continue
            if pair == '-/':
                nesting -= 1; result.append('  '); offset += 2; continue
        elif quoted:
            if c == '\\':
                result.append('  '); offset += 2; continue
            if c == '"':
                quoted = False
        elif pair == '/-':
            nesting = 1; result.append('  '); offset += 2; continue
        elif pair == '--':
            stop = s.find('\n', offset)
            if stop < 0:
                break
            result.append(' ' * (stop-offset)); offset = stop; continue
        elif c == '"':
            quoted = True
        else:
            result.append(c); offset += 1; continue
        result.append('\n' if c == '\n' else ' ')
        offset += 1
    assert nesting == 0 and not quoted, 'Unclosed comment or string'
    return ''.join(result)


def declarations(source):
    clean = code_only(source)
    namespaces = re.findall(r'^namespace\s+(\S+)', clean, re.M)
    assert len(namespaces) == 1 and namespaces[0].startswith('Komorebi.')
    found = []
    # Apostrophes are part of identifiers, not closing delimiters.
    for match in re.finditer(r'\b(theorem|lemma|def|abbrev)\s+([^\s:({]+)', clean):
        kind, name = match.groups()
        assert all(ch.isalnum() or ch in "_'" for ch in name), name
        found.append({'kind': kind, 'name': namespaces[0] + '.' + name})
    forbidden = r'\b(sorry|admit|axiom|unsafe|native_decide|implemented_by)\b|debug\.skipKernelTC|Lean\.addDecl|ofReduceBool|ofReduceNat'
    assert re.search(forbidden, clean) is None
    assert re.search(r'set_option\s+(maxHeartbeats|maxRecDepth)\s+0', clean) is None
    assert re.search(r'set_option\s+linter\.\S+\s+false', clean) is None
    return found, re.findall(r'^public import\s+(\S+)', clean, re.M)


def read_axioms(log):
    result = {}
    chunks = log.splitlines()
    line_no = 0
    while line_no < len(chunks):
        line = chunks[line_no]
        line_no += 1
        if not line.startswith("'"):
            continue
        for suffix in ("' depends on axioms:", "' does not depend on any axioms"):
            if suffix not in line:
                continue
            name, tail = line[1:].split(suffix, 1)
            assert name not in result, name
            if 'does not' in suffix:
                result[name] = []
            else:
                while ']' not in tail:
                    assert line_no < len(chunks)
                    tail += '\n' + chunks[line_no]
                    line_no += 1
                values = tail[tail.index('[')+1:tail.index(']')]
                result[name] = sorted(v.strip() for v in values.split(',') if v.strip())
            break
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gate', type=Path, required=True)
    parser.add_argument('--previous', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    gate = args.gate.resolve()
    previous = args.previous or root.parent/'recovered/PRSC_IX_Complete_Perturbation/polynomial_deformation/formalization'
    if not previous.is_dir():
        previous = root.parent/'polynomial_deformation/formalization'
    assert previous.is_dir(), 'Supply --previous with the preserved prior formalization directory'
    output = args.output or root/'audit/reconciliation.json'
    report_path = gate/'polynomial_charts_verification.json'
    report = json.loads(report_path.read_text())
    inventory_path = root/'inventory.json'
    inventory = json.loads(inventory_path.read_text())
    assert report['status'] == 'PASS'
    assert report['source_inventory'] == inventory
    assert report['inventory_sha256'] == sha(inventory_path)
    assert report['fresh_project_compilation'] and report['warnings_as_errors']
    assert not report['mathlib_rebuilt']
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    assert set(report['allowed_axioms']) == allowed
    entries = inventory['modules'] + inventory['control_support'] + inventory['contracts']
    all_names = {e['module'] for e in entries}
    expected = {}
    source_hashes = {}
    seen = set()
    for entry in entries:
        path = root/entry['source']
        source_hashes[entry['source']] = sha(path)
        assert source_hashes[entry['source']] == entry['sha256'], str(path)
        decls, imports = declarations(path.read_text())
        assert decls == entry['declarations'], str(path)
        assert imports == entry['imports'], str(path)
        assert all(i.startswith('Mathlib.') or i in seen for i in imports), imports
        assert all(i not in all_names or i in seen for i in imports)
        seen.add(entry['module'])
        for decl in decls:
            assert decl['name'] not in expected, decl['name']
            expected[decl['name']] = decl['kind']
    for entry in inventory['negative_controls']:
        path = root/entry['source']
        source_hashes[entry['source']] = sha(path)
        assert source_hashes[entry['source']] == entry['sha256']
    for directory, key in [('formalization', 'modules'), ('contracts', 'contracts')]:
        assert {p.stem for p in (root/directory).glob('*.lean')} == {e['module'] for e in inventory[key]}
    assert {p.name for p in (root/'controls').glob('Invalid*.lean')} == {Path(e['source']).name for e in inventory['negative_controls']}
    assert {p.stem for p in (root/'controls').glob('Polynomial*.lean')} == {e['module'] for e in inventory['control_support']}
    expected_runs = ['SourceAuditParserRegression', 'LeanVersion'] + [e['module'] for e in entries] + ['PolynomialChartsAxiomAudit'] + [Path(e['source']).stem for e in inventory['negative_controls']]
    assert [r['name'] for r in report['runs']] == expected_runs
    logs = {}
    for run in report['runs']:
        path = gate/run['log']
        content = path.read_text()
        assert sha(path) == run['log_sha256'] and run['passed'] is True
        assert not re.search(r'PANIC|timed out|unknown module|unknown constant|does not exist', content, re.I)
        if run['expected_error'] is None:
            assert run['exit_code'] == 0 and 'error:' not in content
        else:
            assert run['exit_code'] == 1 and 'error:' in content
            assert re.search(run['expected_error'], content, re.I)
        if run['name'] not in {'SourceAuditParserRegression', 'LeanVersion'}:
            command = run['command']
            assert '--threads' in command and command[command.index('--threads')+1] == '1'
            assert '--timeout' in command and command[command.index('--timeout')+1] == '240'
        logs[run['name']] = {'exit_code': run['exit_code'], 'sha256': sha(path)}
    axioms = read_axioms((gate/'PolynomialChartsAxiomAudit.log').read_text())
    assert set(axioms) == set(expected), {'missing': sorted(set(expected)-set(axioms)), 'extra': sorted(set(axioms)-set(expected))}
    assert all(set(a) <= allowed for a in axioms.values())
    assert axioms == report['axiom_dependencies']
    counts = dict(collections.Counter(expected.values()))
    assert len(expected) == report['explicit_declaration_audits']
    assert counts == report['declarations']
    for field, key in [('module_count','modules'), ('statement_contracts','contracts'), ('positive_control_modules','control_support'), ('negative_controls','negative_controls')]:
        assert report[field] == len(inventory[key])
    compiled = {p.name: sha(p) for p in (gate/'build').iterdir() if p.is_file()}
    assert compiled == report['build_files']
    assert all(entry['module']+'.olean' in compiled for entry in entries)
    script_hashes = {}
    for field, filename in [('verifier_sha256','verify_polynomial_charts.py'), ('source_audit_sha256','source_audit.py'), ('runner_sha256','check_low_memory.py'), ('source_audit_regression_sha256','check_source_audit.py'), ('inventory_generator_sha256','generate_inventory.py')]:
        script_hashes[filename] = sha(root/'scripts'/filename)
        assert report[field] == script_hashes[filename]
    preserved = {}
    for prior_path in sorted(previous.glob('*.lean')):
        new = root/'formalization'/prior_path.name
        assert new.is_file() and sha(new) == sha(prior_path), prior_path.name
        preserved[prior_path.name] = sha(new)
    assert len(preserved) == 17
    execution = None
    environment_path = gate/'execution_environment.json'
    if environment_path.exists():
        execution = json.loads(environment_path.read_text())
        assert execution['verification_report_sha256'] == sha(report_path)
        assert execution['final_status'] == report['status'] == 'PASS'
        overrides = execution['environment_overrides']
        assert set(overrides) == {'LD_PRELOAD', 'TMPDIR'}
        assert overrides['TMPDIR'] == '/dev/shm'
        adapter = Path(overrides['LD_PRELOAD'])
        assert adapter.name == 'app_path.so' and adapter.parent.name == 'compat'
        assert sha(adapter) == execution['compatibility_adapter_sha256']
        kit = adapter.parent.parent
        kit_manifest_path = kit/'verification/file-manifest.json'
        kit_manifest = json.loads(kit_manifest_path.read_text())
        shipped = {e['path']: e for e in kit_manifest['files']}
        checked_adapter_files = {}
        for relative in ['compat/app_path.so', 'compat/app_path.c', 'run.sh']:
            assert sha(kit/relative) == shipped[relative]['sha256']
            checked_adapter_files[relative] = sha(kit/relative)
        assert execution['runtime_modified'] is False
        assert execution['mathematical_sources_modified'] is False
        execution = {
            'execution_environment_sha256': sha(environment_path),
            'overrides': overrides,
            'adapter_files_match_shipped_kit_manifest': checked_adapter_files,
            'kit_manifest_sha256': sha(kit_manifest_path),
            'review': 'The existing adapter remaps only the current process numeric /proc/PID/exe readlink to /proc/self/exe. The runner preserves inherited LD_PRELOAD and uses TMPDIR for temporary directories; no Lean kernel or proof source was edited.'
        }
    result = {
        'status': 'PASS', 'claim_id': inventory['claim_id'],
        'method': 'Independent raw-source, inventory, compiler-log, declaration and axiom-output reconciliation; no imports of gate parser or runner',
        'report_sha256': sha(report_path), 'inventory_sha256': sha(inventory_path),
        'source_and_control_count': len(source_hashes), 'source_and_control_hashes': source_hashes,
        'mathematical_module_count': len(inventory['modules']), 'new_mathematical_module_count': len(inventory['modules'])-17,
        'preserved_previous_module_count': len(preserved), 'preserved_previous_modules': preserved,
        'gate_count': len(logs), 'gate_logs': logs,
        'compiled_file_count': len(compiled), 'compiled_file_hashes': compiled,
        'explicit_declaration_audits': len(axioms), 'declarations': counts,
        'allowed_axioms': sorted(allowed), 'axiom_closures': axioms,
        'verifier_script_hashes': script_hashes,
        'execution_environment_check': execution,
        'reconciliation_script_sha256': sha(Path(__file__)),
        'limitations': [
            'This uses the same pinned Lean kernel and precompiled Mathlib, not a second kernel or fresh Mathlib build.',
            'Negative controls check their stated false extensions, not all possible theorem edits.',
            'Reconstructed new chart sources have new current hashes; byte identity with lost unpublished sources is not asserted.'
        ]}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','report_sha256','inventory_sha256','mathematical_module_count','new_mathematical_module_count','source_and_control_count','gate_count','compiled_file_count','explicit_declaration_audits','declarations']}, indent=2))


if __name__ == '__main__':
    main()
