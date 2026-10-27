#!/usr/bin/env python3
"""Version-one validation path extracted/adapted from the installed Mathbox
computation-audit validator. Unused version-two handling is intentionally omitted.
It validates provenance structure and hashes, not mathematical truth.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

REQUIRED_TOP={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
REQUIRED_MATH={'assertion_tested','coefficient_domain','conventions','inputs','bounds','non_claims'}

def file_hash(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    return h.hexdigest()

def safe_project_path(root,name):
    p=Path(name)
    root=root.resolve()
    if p.is_absolute() or '..' in p.parts:
        return None
    p=(root/p).resolve()
    return p if p.is_relative_to(root) else None

def resolve_output(root,manifest_path,name):
    p=safe_project_path(root,name)
    if p is None:
        return None,'escape'
    local_root=manifest_path.resolve().parent
    if not local_root.is_relative_to(root.resolve()):
        return p,'project'
    q=safe_project_path(local_root,name)
    if q is None or q==p or not q.is_relative_to(root.resolve()):
        return p,'project'
    if p.is_file() and q.is_file():
        return None,'ambiguous'
    return (q,'manifest') if not p.is_file() and q.is_file() else (p,'project')

def validate(obj,root=None,manifest_path=None):
    errors=[]
    def ck(ok,msg):
        if not ok: errors.append(msg)
    nonempty=lambda s:isinstance(s,str) and bool(s.strip())
    if not isinstance(obj,dict): return ['top level must be an object']
    ck(not REQUIRED_TOP-obj.keys(),'missing top-level fields')
    ck(type(obj.get('schema_version')) is int and obj['schema_version']==1,'this extraction supports schema version one only')
    maths=obj.get('mathematics')
    if not isinstance(maths,dict): return errors+['mathematics must be an object']
    ck(not REQUIRED_MATH-maths.keys(),'missing mathematics fields')
    for k in ('repository','environment','randomness','run'): ck(isinstance(obj.get(k),dict),k+' must be an object')
    for k in ('outputs','checks','residual_risks'): ck(isinstance(obj.get(k),list),k+' must be an array')
    if errors:return errors
    for k in ('claim_id','result'): ck(nonempty(obj.get(k)),k+' must be nonempty')
    command=obj['command']
    ck(nonempty(command) or (isinstance(command,list) and bool(command) and all(nonempty(x) for x in command)),'command is missing')
    for k in ('assertion_tested','coefficient_domain','conventions'):ck(nonempty(maths.get(k)),'missing mathematics.'+k)
    ck(isinstance(maths.get('inputs'),list),'mathematics.inputs must be an array')
    ck(isinstance(maths.get('bounds'),dict) and bool(maths['bounds']),'mathematics.bounds missing')
    ck(isinstance(maths.get('non_claims'),list) and bool(maths['non_claims']) and all(nonempty(x) for x in maths['non_claims']),'non-claims missing')
    ck(type(obj['repository'].get('dirty')) is bool,'repository.dirty must be boolean')
    ck(obj['repository'].get('commit') is None or isinstance(obj['repository']['commit'],str),'invalid repository.commit')
    software=obj['environment'].get('software')
    ck(isinstance(software,list) and bool(software),'software versions missing')
    for i,s in enumerate(software if isinstance(software,list) else []):
        ck(nonempty(s) or (isinstance(s,dict) and nonempty(s.get('name')) and nonempty(s.get('version'))),f'invalid software entry {i}')
    rng=obj['randomness']
    ck(type(rng.get('used')) is bool,'randomness.used must be boolean')
    if rng.get('used'):ck(nonempty(rng.get('generator')) and rng.get('seed') is not None,'randomness provenance missing')
    run=obj['run'];runtime=run.get('runtime_seconds')
    ck(nonempty(run.get('started_at')),'start time missing')
    ck(type(runtime) in (int,float) and math.isfinite(runtime) and runtime>=0,'runtime invalid')
    ck(type(run.get('exit_status')) is int,'exit status invalid')
    ck(bool(obj['outputs']),'outputs missing')
    for i,out in enumerate(obj['outputs']):
        if not isinstance(out,dict):errors.append(f'output {i} must be an object');continue
        p,h=out.get('path'),out.get('sha256')
        ck(nonempty(p),f'output {i} path missing')
        valid_hash=isinstance(h,str) and bool(re.fullmatch(r'[0-9a-f]{64}',h))
        ck(valid_hash,f'output {i} hash invalid')
        if root is not None and nonempty(p) and valid_hash:
            source,mode=resolve_output(root,manifest_path,p)
            if mode in ('escape','ambiguous'):errors.append(f'{mode}: {p}')
            elif source is None or not source.is_file():errors.append(f'output missing: {p}')
            elif file_hash(source)!=h:errors.append(f'output changed: {p}')
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--root',type=Path)
    args=parser.parse_args()
    try:
        obj=json.loads(args.manifest.read_text(encoding='utf-8'))
        errors=validate(obj,args.root,args.manifest)
    except (OSError,ValueError,TypeError) as e:
        errors=[str(e)]
    if errors:
        print('invalid manifest: '+'; '.join(errors),file=sys.stderr);return 1
    print('valid legacy version 1 evidence record; hashes verified when --root was supplied; '
          'no repository revision and no mandatory machine-checkable input/resource schema; '
          'mathematical interpretation requires review')
    return 0
if __name__=='__main__':raise SystemExit(main())
