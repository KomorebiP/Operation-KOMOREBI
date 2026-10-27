#!/usr/bin/env python3
"""Validate this project's v1 computation-evidence record and its output hashes.

Implements the v1 record requirements used by the installed computation-audit
workflow. This project-local validator supports version 1 only. Manifest
validation is not mathematical verification; Lean replay is a separate check.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys


def validate(obj: dict, root: Path) -> list[str]:
    errors: list[str] = []
    def check(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)
    def text(x: object) -> bool:
        return isinstance(x, str) and bool(x.strip())
    required = {'schema_version','claim_id','repository','command','environment',
                'mathematics','randomness','run','outputs','checks','result','residual_risks'}
    check(isinstance(obj, dict), 'Top level must be an object.')
    if not isinstance(obj, dict):
        return errors
    check(required.issubset(obj), 'Missing top-level fields.')
    check(obj.get('schema_version') == 1, 'This validator accepts version 1 only.')
    for field in ('claim_id','result'):
        check(text(obj.get(field)), field+' must be nonempty.')
    command = obj.get('command')
    check(text(command) or (isinstance(command,list) and bool(command) and all(map(text,command))),
          'A command string or argv list is required.')
    for field in ('repository','environment','mathematics','randomness','run'):
        check(isinstance(obj.get(field),dict), field+' must be an object.')
    for field in ('outputs','checks','residual_risks'):
        check(isinstance(obj.get(field),list), field+' must be an array.')
    if errors:
        return errors
    m=obj['mathematics']
    for field in ('assertion_tested','coefficient_domain','conventions'):
        check(text(m.get(field)), 'mathematics.'+field+' must be nonempty.')
    check(isinstance(m.get('inputs'),list), 'Input list required.')
    check(isinstance(m.get('bounds'),dict) and bool(m['bounds']), 'Scope/bounds required.')
    check(isinstance(m.get('non_claims'),list) and bool(m['non_claims']) and all(map(text,m['non_claims'])),
          'Non-claims required.')
    check(type(obj['repository'].get('dirty')) is bool, 'repository.dirty must be boolean.')
    check(obj['repository'].get('commit') is None or isinstance(obj['repository'].get('commit'),str),
          'Repository commit must be text or explicitly unavailable.')
    software=obj['environment'].get('software')
    check(isinstance(software,list) and bool(software), 'Software versions required.')
    for item in software if isinstance(software,list) else []:
        check(text(item) or (isinstance(item,dict) and text(item.get('name')) and text(item.get('version'))),
              'Software entries require names/versions.')
    rand=obj['randomness']
    check(type(rand.get('used')) is bool, 'randomness.used must be boolean.')
    if rand.get('used'):
        check(text(rand.get('generator')) and rand.get('seed') is not None, 'Seed/generator required.')
    run=obj['run']; seconds=run.get('runtime_seconds')
    check(text(run.get('started_at')), 'Run start required.')
    check(type(seconds) in (int,float) and math.isfinite(seconds) and seconds>=0, 'Invalid runtime.')
    check(type(run.get('exit_status')) is int, 'Exit status required.')
    check(bool(obj['outputs']), 'Hashed outputs required.')
    for item in obj['outputs']:
        if not isinstance(item,dict):
            errors.append('Invalid output item.'); continue
        name=item.get('path'); digest=item.get('sha256')
        if not text(name) or not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):
            errors.append('Invalid output path/hash.'); continue
        path=Path(name)
        if path.is_absolute() or '..' in path.parts or not (root/path).resolve().is_relative_to(root.resolve()):
            errors.append('Output path escapes the project: '+name); continue
        path=root/path
        if not path.is_file():
            errors.append('Missing output: '+name)
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            errors.append('Changed output: '+name)
    # This supplement is stronger than the base v1 schema: pin all library source.
    for name,digest in obj.get('input_source_sha256',{}).items():
        path=root/name
        if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
            errors.append('Missing/invalid pinned input: '+name)
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            errors.append('Changed input: '+name)
    return errors


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--root',type=Path,required=True)
    args=parser.parse_args()
    try:
        errors=validate(json.loads(args.manifest.read_text()),args.root)
    except (OSError,ValueError,TypeError,KeyError) as exc:
        errors=[str(exc)]
    if errors:
        print('INVALID: '+'; '.join(errors),file=sys.stderr)
        return 1
    print('PASS: complete v1 evidence record; all declared output and source hashes match.')
    print('LIMIT: v1 schema validation does not certify execution or mathematics. See Lean replay, axiom audit and explicit proof boundary.')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
