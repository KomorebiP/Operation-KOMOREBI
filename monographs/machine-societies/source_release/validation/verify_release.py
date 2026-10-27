#!/usr/bin/env python3
"""Verify this project's computation receipts and optional original snapshot.

This is a project-local integrity checker, not an authenticated external auditor
or a general mathematical manifest standard implementation.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def safe_path(name:str)->Path:
    p=Path(name)
    if p.is_absolute() or '..' in p.parts:raise ValueError(f'Unsafe relative path: {name}')
    out=(ROOT/p).resolve()
    if not out.is_relative_to(ROOT):raise ValueError(f'Path escapes package: {name}')
    return out

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--snapshot',action='store_true');args=ap.parse_args()
    errors=[];checked=0
    def check_file(name,expected):
        nonlocal checked
        try:
            p=safe_path(name)
            if not p.is_file():errors.append(f'Missing: {name}')
            elif digest(p)!=expected:errors.append(f'Hash mismatch: {name}')
            else:checked+=1
        except (ValueError,OSError) as exc:errors.append(str(exc))
    try:
        manifest=json.loads((ROOT/'validation/computation_manifest.json').read_text())
        result=json.loads((ROOT/'validation/finite_checks.json').read_text())
        audit=json.loads((ROOT/'validation/source_audit.json').read_text())
        if manifest['schema_version']!=1:errors.append('This release checker expects its documented legacy v1 record.')
        if manifest['run']['exit_status']!=0 or manifest['result']=='FAIL':errors.append('Recorded computation failed.')
        if result['status']!='PASS' or result.get('error'):errors.append('Finite suite is not a recorded pass.')
        if result['group_count']!=len(result['groups']):errors.append('Group count mismatch.')
        if result['assertions']!=sum(g['assertions'] for g in result['groups']):errors.append('Assertion count mismatch.')
        if any(g.get('status') not in (None,'PASS') for g in result['groups']):errors.append('A group is not a pass.')
        for item in manifest['mathematics']['inputs']+manifest['outputs']:check_file(item['path'],item['sha256'])
        if audit['status']!='PASS' or any(audit['issues'].values()):errors.append('Source audit has unresolved issues.')
        check_file('Machine_Societies_v1.0.0.tex',audit['source_sha256'])
        check_file('sources/v0.7.0/Machine_Societies_v0.7.0.tex',audit['predecessor_source_sha256'])
        if audit['counts']['proved_statements']!=audit['counts']['proof']:errors.append('Proof inventory mismatch.')
        if args.snapshot:
            for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines():
                if not line.strip():continue
                checksum,name=line.split('  ',1);check_file(name,checksum)
    except (OSError,ValueError,KeyError,TypeError) as exc:errors.append(f'Invalid or missing release evidence: {exc}')
    print(json.dumps({'status':'FAIL' if errors else 'PASS','hash_checks':checked,'snapshot_checked':args.snapshot,'errors':errors,
                      'scope':'Package integrity and recorded execution consistency, not mathematical proof validity.'},indent=2))
    return bool(errors)
if __name__=='__main__':sys.exit(main())
