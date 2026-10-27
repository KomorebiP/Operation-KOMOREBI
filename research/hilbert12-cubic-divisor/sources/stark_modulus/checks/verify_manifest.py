#!/usr/bin/env python3
"""Validate the package's v1 evidence records and release SHA-256 hashes.

This checks provenance only, not mathematical truth. It implements the v1
requirements read from the installed mathbox computation-audit manifest schema.
It is not the full plugin v2 validator and does not claim v2 resource guarantees.
"""
import hashlib,json,math,re
from pathlib import Path
root=Path(__file__).resolve().parent.parent
errors=[]
def ck(test,message):
    if not test:errors.append(message)
def h(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(path):
    p=Path(path)
    if p.is_absolute() or '..' in p.parts:return None
    q=(root/p).resolve()
    return q if q.is_relative_to(root.resolve()) else None
required={'schema_version','claim_id','repository','command','environment','mathematics',
          'randomness','run','outputs','checks','result','residual_risks'}
for p in sorted((root/'evidence').glob('*_manifest.json')):
    d=json.loads(p.read_text());ck(required<=d.keys(),f'{p.name}: missing fields')
    ck(d['schema_version']==1,f'{p.name}: unsupported schema')
    ck(bool(d['claim_id']) and bool(d['command']) and bool(d['result']),f'{p.name}: incomplete evidence')
    ck(type(d['repository']['dirty']) is bool,f'{p.name}: dirty flag')
    for k in ('assertion_tested','coefficient_domain','conventions','bounds','non_claims'):
        ck(bool(d['mathematics'].get(k)),f'{p.name}: empty mathematics.{k}')
    ck(isinstance(d['mathematics']['inputs'],list),f'{p.name}: inputs not a list')
    ck(bool(d['environment']['software']),f'{p.name}: software missing')
    ck(bool(d['run']['started_at']),f'{p.name}: start time missing')
    ck(isinstance(d['run']['runtime_seconds'],(int,float)) and math.isfinite(d['run']['runtime_seconds'])
       and d['run']['runtime_seconds']>=0,f'{p.name}: runtime invalid')
    ck(type(d['run']['exit_status']) is int and d['run']['exit_status']==0,f'{p.name}: run not successful')
    ck(bool(d['outputs']),f'{p.name}: missing outputs')
    for rec in d['outputs']:
        q=safe(rec['path']);ck(q is not None and q.is_file(),f'{p.name}: missing or unsafe output')
        ck(bool(re.fullmatch('[0-9a-f]{64}',rec['sha256'])),f'{p.name}: invalid checksum')
        if q is not None and q.is_file():ck(h(q)==rec['sha256'],f'{p.name}: output changed {rec["path"]}')
    for rec in d.get('input_artifacts',[]):
        q=safe(rec['path']);ck(q is not None and q.is_file(),f'{p.name}: input missing')
        if q is not None and q.is_file():ck(h(q)==rec['sha256']==rec['sha256_after'],f'{p.name}: input changed')
release=json.loads((root/'MANIFEST.json').read_text())
for rec in release['files']:
    q=safe(rec['path']);ck(q is not None and q.is_file(),f'missing release file {rec["path"]}')
    if q is not None and q.is_file():ck(h(q)==rec['sha256'],f'changed release file {rec["path"]}')
if errors:raise SystemExit('\n'.join(errors))
print(f'PASS: {len(release["files"])} release file hashes and v1 evidence records verified.')
print('Provenance only. No mathematical, Lean, interval-rounding, or v2 resource certificate is implied.')
