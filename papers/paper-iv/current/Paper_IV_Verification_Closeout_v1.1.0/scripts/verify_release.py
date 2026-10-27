#!/usr/bin/env python3
"""Verify the frozen delivered file set and the precise recorded Paper IV gates.

Hash/receipt verification is not a new Lean compiler run. Use replay_lean.py for
fresh source compilation. The manifest is an integrity record, not a signature.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
from typing import Any
sys.dont_write_bytecode = True


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative(root: Path, name: str) -> Path:
    rel = PurePosixPath(name)
    if not name or rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or str(rel) != name:
        raise ValueError(f'Unsafe or noncanonical path: {name!r}')
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Symlink not allowed: {name}')
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes root: {name}')
    return current


def verify_manifest(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    rows = manifest['files']
    if not isinstance(rows, list) or not rows:
        raise ValueError('Manifest must have a nonempty file list')
    seen = set()
    for row in rows:
        name = row['path']
        if name in seen:
            raise ValueError(f'Duplicate manifest member: {name}')
        seen.add(name)
        path = relative(root, name)
        if not path.is_file():
            raise ValueError(f'Missing file: {name}')
        if path.stat().st_size != row['bytes'] or sha(path) != row['sha256']:
            raise ValueError(f'Hash or size mismatch: {name}')
        if path.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.ttc'}:
            raise ValueError(f'Font binary forbidden in release: {name}')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    expected = seen | {'MANIFEST.json'}
    if actual != expected:
        raise ValueError(f'Unexpected/missing files: extra={sorted(actual-expected)[:8]}, missing={sorted(expected-actual)[:8]}')
    return {'status':'PASS','files':len(rows),'manifest_sha256':sha(root/'MANIFEST.json')}


def check_evidence(root: Path) -> dict[str, Any]:
    def load(name: str) -> Any:
        return json.loads(relative(root,name).read_text())
    source = load('verification/SOURCE_CONTRACT.json')
    replay = load('verification/lean_primary/REPLAY.json')
    if replay['status'] != 'PASS':
        raise ValueError('No complete primary Lean pass')
    if replay['source_contract_sha256'] != sha(root/'verification/SOURCE_CONTRACT.json'):
        raise ValueError('Changed source contract')
    expected = source['production_modules']
    if len(expected) != 118 or [x['module'] for x in replay['production_done']] != expected:
        raise ValueError('Incomplete or reordered production closure')
    if replay['production_count'] != len(expected):
        raise ValueError('Production count mismatch')
    for name,digest in source['source_sha256'].items():
        if sha(relative(root,'formalization/lean/'+name)) != digest:
            raise ValueError('Changed mathematical source '+name)
    for name,digest in source['configuration_sha256'].items():
        if sha(relative(root,'formalization/lean/'+name)) != digest:
            raise ValueError('Changed formal configuration '+name)
    spec = load(source['contract_relative'])
    if sha(relative(root,source['contract_relative'])) != source['contract_sha256']:
        raise ValueError('Changed reviewed mapping contract')
    if replay['reviewed_kinds_passed'] != len(spec['targets']) or len(spec['targets']) != 1164:
        raise ValueError('Kind coverage mismatch')
    for item in replay['production_done']:
        if sha(relative(root,item['source'])) != item['source_sha256']:
            raise ValueError('Production source receipt mismatch')
        for name,digest in item['objects'].items():
            if sha(relative(root,'verification/lean_primary/objects/'+name)) != digest:
                raise ValueError('Changed produced object '+name)
    path = root/'scripts/replay_lean.py'
    module_spec = importlib.util.spec_from_file_location('paper_iv_replay_check',path)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    checks = replay['checks']; labels = [x['label'] for x in checks]
    if len(labels) != len(set(labels)):
        raise ValueError('Ambiguous duplicate check labels')
    by_label = {x['label']:x for x in checks}
    required = {'lean_version','reviewed_kinds','original_kernel_audit'} | {'compile_'+n for n in expected}
    required |= {'control_'+name for name in ['positive','false','sorry','missing-premise','custom-axiom','wrong-kind']}
    if set(labels) != required:
        raise ValueError('Check sequence has missing or unexpected labels')
    for item in checks:
        log = relative(root,item['log'])
        if sha(log) != item['log_sha256']:
            raise ValueError('Changed compiler log '+item['label'])
        if item['timed_out']:
            raise ValueError('Timeout cannot be a successful compiler gate')
        if not item['label'].startswith('control_') and item['returncode'] != 0:
            raise ValueError('Unsuccessful compile/audit '+item['label'])
    audit=by_label['original_kernel_audit']
    text=relative(root,audit['log']).read_text()
    parsed=module.check_axiom_reports(text,{x['declaration'] for x in spec['targets']})
    if replay['kernel_audit']['namespace_declarations'] != spec['namespace_declarations']:
        raise ValueError('Namespace census mismatch')
    sent=f'FAIL-CLOSED PAPER IV v1.0.0 KERNEL AUDIT PASS: {spec["namespace_declarations"]} declarations ({spec["namespace_theorems"]} theoremInfo); 1164 explicit mapped targets; allowed axioms only: propext, Classical.choice, Quot.sound'
    if text.count(sent)!=1:
        raise ValueError('Missing or ambiguous namespace audit sentinel')
    names=['positive','false','sorry','missing-premise','custom-axiom','wrong-kind']
    if [x['name'] for x in replay['controls']] != names:
        raise ValueError('Compiler control coverage mismatch')
    for name,control in zip(names,replay['controls']):
        item=by_label['control_'+name]
        if not control['passed'] or not module.diagnostic_accept(item,relative(root,item['log']).read_text(),name):
            raise ValueError('Invalid compiler control '+name)
        fixture=relative(root,'verification/lean_primary/Control_'+name.replace('-','_')+'.lean')
        if sha(fixture)!=control['source_sha256']:
            raise ValueError('Changed compiler fixture '+name)
    finite=load('verification/finite_primary/FINITE_REPLAY.json')
    if finite['status']!='PASS' or finite['baseline_files_unchanged']!=836:
        raise ValueError('Finite replay failed or baseline preservation mismatch')
    if [x['name'] for x in finite['checks']]!=['algebra_exact','exact_visual','original_tables','strengthened','original_paper']:
        raise ValueError('Missing finite gate')
    for item in finite['checks']:
        if item['status']!='PASS' or item['returncode']!=0 or item['timed_out']:
            raise ValueError('Failed finite gate')
        for a,b in [('log','log_sha256'),('result','result_sha256')]:
            if a in item and sha(relative(root,'verification/finite_primary/'+item[a]))!=item[b]:
                raise ValueError('Changed finite output')
    if finite['rational_tables_and_brackets']!={'status':'PASS','rows':818,'brackets':4}:
        raise ValueError('Unexpected rational table/bracket scope')
    tests=load('verification/VERIFIER_TESTS.json')
    if tests['status']!='PASS' or tests['tests_run']!=42 or tests['failures'] or tests['errors'] or tests['skipped']:
        raise ValueError('Verification test suite incomplete')
    return {'status':'PASS','production_modules':len(expected),'scoped_results':68,
            'reviewed_targets':len(spec['targets']),'namespace_declarations':spec['namespace_declarations'],
            'namespace_theorems':spec['namespace_theorems'],'axiom_union':parsed['allowed_union'],
            'compiler_controls':6,'python_verifier_tests':tests['tests_run'],
            'fresh_compiler_execution_in_this_command':False}


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();root=args.root.resolve()
    try:
        report={'status':'PASS','integrity':verify_manifest(root,json.loads((root/'MANIFEST.json').read_text())),
                'evidence':check_evidence(root)}
    except Exception as exc:
        report={'status':'FAILED','error':str(exc)}
    text=json.dumps(report,indent=2)+'\n';print(text,end='')
    if args.output:
        if args.output.resolve().is_relative_to(root):
            print('Output must be outside the frozen release tree',file=sys.stderr);return 2
        args.output.write_text(text)
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':
    sys.exit(main())
