#!/usr/bin/env python3
"""Strict execution/evidence primitives. Standard library only; no downloads.

These validate integrity against supplied pins, not the external truth of those
pins. A recorded success marker never overrides a failed or timed-out process.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import time
from typing import Any

ALLOWED = frozenset({'propext', 'Classical.choice', 'Quot.sound'})
LEAN_SHA256 = 'e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550'
LEAN_COMMIT = '6a10ac8c22beadecabdbb0919c2b50214762f91d'
PREFIX = 'P10AUDIT '
KINDS = {'theorem','definition','opaque','axiom','inductive','constructor','recursor','quotient'}

class AuditError(ValueError):
    pass

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    tmp.replace(path)

def parse_json(text: str) -> Any:
    def pairs(items):
        obj = {}
        for k,v in items:
            if k in obj:
                raise AuditError('Duplicate JSON key: ' + k)
            obj[k] = v
        return obj
    return json.loads(text, object_pairs_hook=pairs)

def safe_relative(value: str) -> PurePosixPath:
    if not isinstance(value,str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise AuditError('Unsafe relative path')
    bits = value.split('/')
    if any(b in ('', '.', '..') for b in bits):
        raise AuditError('Unsafe relative path')
    p = PurePosixPath(value)
    if p.is_absolute():
        raise AuditError('Absolute path is not allowed')
    return p

def verify_files(root: Path, records: dict[str,str], *, strict: bool = False,
                 ignored: frozenset[str] = frozenset()) -> dict:
    root = root.resolve()
    if not records:
        raise AuditError('Empty source or file manifest')
    for rel,digest in records.items():
        p = root / safe_relative(rel)
        if not isinstance(digest,str) or re.fullmatch(r'[0-9a-f]{64}',digest) is None:
            raise AuditError('Invalid digest: ' + rel)
        # Reject symlinks at every path component, including internal symlinks.
        chain = [root.joinpath(*p.relative_to(root).parts[:i])
                 for i in range(1, len(p.relative_to(root).parts)+1)]
        if any(q.is_symlink() for q in chain) or not p.is_file():
            raise AuditError('Missing or symlinked file: ' + rel)
        if sha256(p) != digest:
            raise AuditError('Hash mismatch: ' + rel)
    if strict:
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*')
                  if p.is_file() or p.is_symlink()}
        if actual - ignored != set(records):
            raise AuditError('Strict membership mismatch')
    return {'status':'PASS', 'files':len(records)}

def execute(argv: list[str], cwd: Path, env: dict[str,str], timeout: float, log: Path) -> dict:
    if not isinstance(timeout,(float,int)) or not math.isfinite(timeout) or timeout <= 0:
        raise AuditError('Timeout must be finite and positive')
    if log.exists():
        raise AuditError('Refusing to overwrite an existing log')
    log.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    result = {'argv':list(map(str,argv)), 'cwd':str(cwd), 'started_utc':utc(),
              'timeout_seconds':timeout, 'timed_out':False, 'spawn_error':None}
    with log.open('xb') as out:
        try:
            process = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out,
                stderr=subprocess.STDOUT, start_new_session=(os.name=='posix'))
            try:
                result['returncode'] = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                result['timed_out'] = True
                if os.name=='posix':
                    try: os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError: pass
                else:
                    process.kill()
                result['returncode'] = process.wait()
        except OSError as error:
            result['spawn_error'] = f'{type(error).__name__}: {error}'
            result['returncode'] = None
    result.update(finished_utc=utc(), seconds=round(time.monotonic()-start,4),
                  log=str(log), log_sha256=sha256(log))
    return result

def require_success(result: dict) -> None:
    if result.get('returncode') != 0 or result.get('timed_out') is not False or result.get('spawn_error'):
        raise AuditError('Process did not complete successfully')

def require_rejection(result: dict, text: str, diagnostic: str) -> None:
    code = result.get('returncode')
    if not isinstance(code,int) or code <= 0 or result.get('timed_out') is not False or result.get('spawn_error'):
        raise AuditError('Crash, timeout or spawn failure is not an intended rejection')
    if diagnostic not in text or 'error' not in text.lower():
        raise AuditError('Expected rejection diagnostic missing')

def parse_audit(result: dict, text: str, owners: list[str], targets: list[dict]) -> dict:
    require_success(result)
    if not owners or len(owners)!=len(set(owners)):
        raise AuditError('Empty/duplicate expected owners')
    expected = {t['name']:t for t in targets}
    if len(expected)!=len(targets):
        raise AuditError('Duplicate expected targets')
    declarations, found_targets, end = {}, {}, None
    for line in text.splitlines():
        if not line.startswith(PREFIX):
            continue
        if end is not None:
            raise AuditError('Audit record after completion marker')
        r = parse_json(line[len(PREFIX):])
        kind = r.get('event')
        if kind=='declaration':
            if set(r)!={'event','name','kind','owner','axioms','forbidden'}:
                raise AuditError('Malformed declaration record')
            name = r['name']
            if not isinstance(name,str) or not name or name in declarations:
                raise AuditError('Empty/duplicate declaration name')
            if r['owner'] not in owners or r['kind'] not in KINDS:
                raise AuditError('Unknown owner or declaration kind')
            if not isinstance(r['axioms'],list) or not all(isinstance(a,str) for a in r['axioms']):
                raise AuditError('Malformed axiom list')
            if len(r['axioms'])!=len(set(r['axioms'])):
                raise AuditError('Duplicate axiom')
            forbidden = sorted(set(r['axioms'])-ALLOWED)
            if r['forbidden']!=forbidden or forbidden:
                raise AuditError('Forbidden or misreported axiom dependencies')
            declarations[name]=r
        elif kind=='target':
            if set(r)!={'event','name','kind','owner'}:
                raise AuditError('Malformed target record')
            if r['name'] in found_targets:
                raise AuditError('Duplicate target record')
            found_targets[r['name']]={k:r[k] for k in ('name','kind','owner')}
        elif kind=='complete':
            if set(r)!={'event','owners','declarations','theorems','targets'}:
                raise AuditError('Malformed completion record')
            end=r
        else:
            raise AuditError('Unknown audit event')
    if end is None or not declarations:
        raise AuditError('Missing completion or empty declaration census')
    if end['owners']!=owners or found_targets!=expected:
        raise AuditError('Owner or target contract mismatch')
    expected_counts = {'declarations':len(declarations),
                       'theorems':sum(r['kind']=='theorem' for r in declarations.values()),
                       'targets':len(targets)}
    for k,v in expected_counts.items():
        if type(end[k]) is not int or end[k]!=v:
            raise AuditError('Completion count mismatch: '+k)
    for name,t in expected.items():
        d=declarations.get(name)
        if d is None or d['kind']!=t['kind'] or d['owner']!=t['owner']:
            raise AuditError('Target is absent from owned census or disagrees')
    return {'status':'PASS', **expected_counts, 'owners':owners,
            'axiom_union':sorted({a for r in declarations.values() for a in r['axioms']}),
            'records':list(declarations.values()), 'targets_resolved':list(found_targets.values())}

def runtime_env(runtime: Path, objects: list[Path], *, packages: list[str] = ()) -> tuple[Path,dict]:
    lean=runtime/'toolchain/bin/lean'
    if not lean.is_file() or sha256(lean)!=LEAN_SHA256:
        raise AuditError('Pinned Lean executable missing or digest mismatch')
    env=dict(os.environ, PATH=str(lean.parent)+os.pathsep+os.environ.get('PATH',''),
             LEAN_PATH=os.pathsep.join(map(str,objects+list(packages))),
             MALLOC_ARENA_MAX='2', PYTHONDONTWRITEBYTECODE='1', TZ='UTC')
    for key in ('LD_PRELOAD','LEAN_SRC_PATH','LEAN_SYSROOT'):
        env.pop(key,None)
    return lean,env

def audit_source(owners: list[str], targets: list[dict]) -> str:
    if any(re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.]*',m) is None for m in owners):
        raise AuditError('Unsupported module name')
    if len(owners)!=len(set(owners)) or not owners:
        raise AuditError('Empty/duplicate module names')
    names = lambda xs: '#[' + ', '.join(json.dumps(s)+'.toName' for s in xs) + ']'
    ts = '#[' + ', '.join('⟨'+json.dumps(t['name'],ensure_ascii=False)+'.toName, '+
         json.dumps(t['kind'])+', '+json.dumps(t['owner'])+'.toName⟩' for t in targets) + ']'
    return '\n'.join(['import AuditCore']+['import '+m for m in owners]+[
        'run_cmd PaperXAudit.auditModules '+names(owners)+' '+ts, ''])
