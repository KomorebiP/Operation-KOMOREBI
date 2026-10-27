#!/usr/bin/env python3
"""Project-local validator for the supplied version-1 computation manifest format.

Checks the v1 structure, result hashes, and additional before/after source hashes
in this project's report.  This is not the upstream mathbox validator and does
not turn a v1 record into v2 evidence.
"""
from __future__ import annotations
import argparse, hashlib, json, math, pathlib, re


def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()


def local(root,name):
    p=pathlib.Path(name)
    if p.is_absolute() or '..' in p.parts: raise ValueError('Unsafe artifact path: '+name)
    resolved=(root/p).resolve()
    if not resolved.is_relative_to(root): raise ValueError('Artifact escapes root: '+name)
    return resolved


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('manifest', type=pathlib.Path)
    ap.add_argument('--root', type=pathlib.Path, required=True)
    a=ap.parse_args(); root=a.root.resolve(); m=json.loads(a.manifest.read_text())
    required={'schema_version','claim_id','repository','command','environment','mathematics',
              'randomness','run','outputs','checks','result','residual_risks'}
    assert required <= m.keys() and m['schema_version']==1
    assert isinstance(m['repository']['dirty'],bool)
    assert m['claim_id'] and m['command'] and m['result']
    assert m['environment']['software'] and m['mathematics']['bounds']
    for k in ('assertion_tested','coefficient_domain','conventions','inputs','non_claims'):
        assert m['mathematics'][k]
    run=m['run']; assert run['started_at'] and type(run['exit_status']) is int
    assert math.isfinite(run['runtime_seconds']) and run['runtime_seconds']>=0
    assert m['outputs'] and m['checks']
    for row in m['outputs']:
        assert re.fullmatch('[0-9a-f]{64}',row['sha256'])
        p=local(root,row['path']); assert digest(p)==row['sha256'],row['path']
        if p.name=='report.json':
            report=json.loads(p.read_text())
            assert report['passed'] and report['exit_status']==0
            for entry in report['input_artifacts']:
                assert entry['sha256']==entry['sha256_after']==digest(local(root,entry['path'])),entry['path']
    print('PASS version-1 manifest structure, result hashes, and supplementary source hashes')
    print('LIMIT: v1 provenance schema; same-kernel proof replay, not an independent verifier.')

if __name__=='__main__': main()
