#!/usr/bin/env python3
"""Local v1-only adaptation of the installed mathbox computation-audit validator.

The schema and v1 checks are transcribed from the installed skill's
scripts/validate_manifest.py, read through api_tool. This adapter intentionally
rejects v2 instead of claiming to implement its additional execution contracts.
It validates evidence metadata/bytes, not the mathematical interpretation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

REQUIRED_TOP = {'schema_version','claim_id','repository','command','environment',
                'mathematics','randomness','run','outputs','checks','result','residual_risks'}
REQUIRED_MATH = {'assertion_tested','coefficient_domain','conventions','inputs','bounds','non_claims'}

def file_hash(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def safe_project_path(root: Path,name: str):
    source=Path(name);rr=root.resolve()
    if source.is_absolute() or '..' in source.parts:return None
    candidate=(root/source).resolve()
    return candidate if candidate.is_relative_to(rr) else None

def resolve_output_path(root: Path,manifest_path: Path,name: str):
    candidate=safe_project_path(root,name)
    if candidate is None:return None,'escape'
    parent=manifest_path.resolve().parent
    if not parent.is_relative_to(root.resolve()):return candidate,'project'
    local=safe_project_path(parent,name)
    if local is None or not local.is_relative_to(root.resolve()):return candidate,'project'
    if candidate==local:return candidate,'project'
    if candidate.is_file() and local.is_file():return None,'ambiguous'
    if not candidate.is_file() and local.is_file():return local,'manifest'
    return candidate,'project'

def validate(obj,root:Path,manifest_path:Path):
    errors=[]
    def check(ok,msg):
        if not ok:errors.append(msg)
    def nonempty(x):return isinstance(x,str) and bool(x.strip())
    if not isinstance(obj,dict):return ['top level must be an object']
    check(not REQUIRED_TOP-obj.keys(),'missing required top-level fields')
    check(type(obj.get('schema_version')) is int and obj['schema_version']==1,
          'this local adaptation supports version 1 only')
    maths=obj.get('mathematics')
    if not isinstance(maths,dict):return errors+['mathematics must be an object']
    check(not REQUIRED_MATH-maths.keys(),'missing mathematics fields')
    for k in ['repository','environment','randomness','run']:
        check(isinstance(obj.get(k),dict),f'{k} must be an object')
    for k in ['outputs','checks','residual_risks']:
        check(isinstance(obj.get(k),list),f'{k} must be an array')
    if errors:return errors
    for k in ['claim_id','result']:check(nonempty(obj.get(k)),f'{k} must be nonempty')
    command=obj.get('command')
    check(nonempty(command) or (isinstance(command,list) and bool(command) and all(nonempty(x) for x in command)),
          'command must be nonempty text or argv')
    for k in ['assertion_tested','coefficient_domain','conventions']:
        check(nonempty(maths.get(k)),f'mathematics.{k} must be nonempty')
    check(isinstance(maths.get('inputs'),list),'mathematics.inputs must be an array')
    check(isinstance(maths.get('bounds'),dict) and bool(maths['bounds']), 'bounds must state tested range')
    check(isinstance(maths.get('non_claims'),list) and bool(maths['non_claims']) and all(nonempty(x) for x in maths['non_claims']),
          'non_claims must state limits')
    check(type(obj['repository'].get('dirty')) is bool,'repository.dirty must be Boolean')
    commit=obj['repository'].get('commit')
    check(commit is None or isinstance(commit,str),'legacy commit must be text or null')
    software=obj['environment'].get('software')
    check(isinstance(software,list) and bool(software),'software versions required')
    for i,e in enumerate(software if isinstance(software,list) else []):
        check(nonempty(e) or (isinstance(e,dict) and nonempty(e.get('name')) and nonempty(e.get('version'))),
              f'software[{i}] needs a version')
    rand=obj['randomness']
    check(type(rand.get('used')) is bool,'randomness.used must be Boolean')
    if rand.get('used'):
        check(nonempty(rand.get('generator')) and rand.get('seed') is not None,'random generator/seed required')
    run=obj['run'];runtime=run.get('runtime_seconds')
    check(nonempty(run.get('started_at')),'run.started_at required')
    check(type(runtime) in [float,int] and math.isfinite(runtime) and runtime>=0,'runtime invalid')
    check(type(run.get('exit_status')) is int,'exit status must be integer')
    check(bool(obj['outputs']),'hashed outputs required')
    for i,out in enumerate(obj['outputs']):
        if not isinstance(out,dict):errors.append(f'outputs[{i}] must be object');continue
        name=out.get('path');digest=out.get('sha256')
        check(nonempty(name),f'outputs[{i}] needs path')
        valid=isinstance(digest,str) and bool(re.fullmatch('[0-9a-f]{64}',digest))
        check(valid,f'outputs[{i}] needs SHA-256')
        if nonempty(name) and valid:
            path,mode=resolve_output_path(root,manifest_path,name)
            if mode in ['escape','ambiguous']:errors.append(f'{mode} output path: {name}')
            elif path is None or not path.is_file():errors.append('missing output: '+name)
            elif file_hash(path)!=digest:errors.append('changed output: '+name)
    return errors

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest',type=Path);p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    try:
        errors=validate(json.loads(a.manifest.read_text()),a.root,a.manifest)
    except (OSError,ValueError,TypeError) as e:errors=[str(e)]
    if errors:print('invalid manifest: '+'; '.join(errors),file=sys.stderr);return 1
    print('valid version 1 evidence record (local v1-only adaptation); mathematical interpretation requires review')
    print('v1 limits: execution-input hashes and machine-checkable resource limits are not required; output paths may be project- or manifest-relative')
    return 0
if __name__=='__main__':raise SystemExit(main())
