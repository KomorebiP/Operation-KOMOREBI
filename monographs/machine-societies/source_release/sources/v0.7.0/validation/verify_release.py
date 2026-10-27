#!/usr/bin/env python3
"""Verify this release's inventory and exact-computation record; no proof checking.

Uses the legacy v1 computation-manifest contract with additional input pinning.
Run: python validation/verify_release.py
Option --manifest-only skips the release inventory during development.
"""
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,math,re,sys
ROOT=Path(__file__).resolve().parents[1]

def digest(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def path(name:str)->Path:
    q=Path(name)
    if q.is_absolute() or '..' in q.parts:raise ValueError(f'Unsafe relative path: {name}')
    p=(ROOT/q).resolve()
    if not p.is_relative_to(ROOT.resolve()):raise ValueError(f'Escaping path: {name}')
    return p

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-only',action='store_true');args=parser.parse_args()
    errors=[];checked=0
    try:
        m=json.loads(path('validation/computation_manifest.json').read_text())
        required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
        if required-set(m):errors.append('Missing computation-manifest fields')
        if m.get('schema_version')!=1:errors.append('Expected legacy schema version 1')
        mathdata=m['mathematics'];run=m['run']
        for key in ('assertion_tested','coefficient_domain','conventions'):
            if not isinstance(mathdata.get(key),str) or not mathdata[key].strip():errors.append('Missing '+key)
        if not mathdata.get('bounds') or not mathdata.get('non_claims'):errors.append('Missing tested range/non-claims')
        if type(run.get('exit_status')) is not int or run['exit_status']!=0:errors.append('Computation did not exit successfully')
        if not isinstance(run.get('runtime_seconds'),(int,float)) or not math.isfinite(run['runtime_seconds']) or run['runtime_seconds']<0:errors.append('Invalid runtime')
        if not m['environment'].get('software') or not run.get('started_at'):errors.append('Incomplete environment/timing')
        for record in mathdata['inputs']+m['outputs']:
            checksum=record.get('sha256','');p=path(record['path'])
            if not re.fullmatch('[0-9a-f]{64}',checksum):errors.append('Invalid SHA256 '+record['path'])
            elif not p.is_file() or digest(p)!=checksum:errors.append('Changed or missing computation artifact: '+record['path'])
            checked+=1
        result=json.loads(path('validation/finite_checks.json').read_text())
        if result['status']!='PASS' or any(g['status']!='PASS' for g in result['groups']):errors.append('A finite check failed')
        if sum(g['assertions'] for g in result['groups'])!=result['assertions']:errors.append('Incorrect assertion total')
        if len(result['groups'])!=result['group_count']:errors.append('Incorrect group total')
        if not args.manifest_only:
            inventory=path('SHA256SUMS.txt')
            if not inventory.is_file():errors.append('Missing release inventory')
            else:
                for line in inventory.read_text().splitlines():
                    if not line.strip():continue
                    checksum,name=line.split('  ',1);p=path(name)
                    if not p.is_file() or digest(p)!=checksum:errors.append('Release mismatch: '+name)
                    checked+=1
        output={'status':'PASS' if not errors else 'FAIL','hash_records_checked':checked,'groups':result['group_count'],'assertions':result['assertions'],'errors':errors,'limits':['Integrity and finite-code validation only; not a proof-kernel build or independent review.','Legacy v1 manifest does not authenticate resource limits or a Git revision; this package separately pins code and manuscript inputs.']}
    except Exception as exc:
        output={'status':'FAIL','errors':[f'{type(exc).__name__}: {exc}']}
    print(json.dumps(output,indent=2));return 0 if output['status']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
