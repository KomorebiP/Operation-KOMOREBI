#!/usr/bin/env python3
"""Compile the Lean project and reject unapproved transitive proof axioms.

Python 3.10+, no third-party Python dependencies.
Use --runtime for the recovered Komorebi portable kit; otherwise configure Lake
for this project first. The full process environment is NEVER written to disk.
Every replay writes to a fresh evidence directory and refuses to overwrite it.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from source_index import MODULES, generate, without_comments

VERSION = '4.34.0-rc2'
MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=Path, help='Komorebi portable Lean kit root')
    ap.add_argument('--evidence', type=Path, required=True, help='NEW directory for replay logs')
    ap.add_argument('--build-dir', type=Path, help='NEW directory for generated .olean files')
    ap.add_argument('--timeout', type=int, default=120, help='Per-module subprocess timeout')
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    evidence = args.evidence.resolve()
    if evidence.exists(): raise FileExistsError(f'Refusing existing evidence directory: {evidence}')
    evidence.mkdir(parents=True)
    build = (args.build_dir or evidence / 'build').resolve()
    if build.exists(): raise FileExistsError(f'Refusing existing build directory: {build}')
    (build / 'Euler').mkdir(parents=True)
    index = generate(root)
    lean_sources = [root/'Euler'/f'{m}.lean' for m in MODULES] + [root/'Euler.lean', root/'Audit.lean']
    for path in lean_sources:
        clean = without_comments(path.read_text())
        if re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b|\+native', clean):
            raise ValueError(f'Forbidden proof construct in {path.name}')
    if args.runtime:
        kit = args.runtime.resolve()
        cwd = kit / 'workspace'
        env_cmd = [str(kit/'run.sh'), 'lake', 'env', '/usr/bin/env', '-0']
        lean = kit/'toolchain/bin/lean'
        manifest = cwd/'lake-manifest.json'
    else:
        cwd = root
        env_cmd = ['lake', 'env', '/usr/bin/env', '-0']
        lean = None
        manifest = root/'lake-manifest.json'
    if not manifest.exists():
        raise FileNotFoundError('Lake dependencies not configured; see README.md')
    packages = json.loads(manifest.read_text())['packages']
    math_pkg = next(p for p in packages if p['name'] == 'mathlib')
    if math_pkg['rev'] != MATHLIB:
        raise ValueError('Mathlib manifest revision differs from pinned revision')
    ep = subprocess.run(env_cmd, cwd=cwd, capture_output=True, check=True, timeout=30)
    env = dict(os.environ)
    for field in ep.stdout.decode().split('\0'):
        if '=' in field:
            key, value = field.split('=', 1)
            env[key] = value
    for key in ('LEAN_PATH', 'LEAN_SRC_PATH'):
        if key in env:
            env[key] = os.pathsep.join(str((cwd/p).resolve()) if not Path(p).is_absolute() else p
                                      for p in env[key].split(os.pathsep) if p)
    if lean is None:
        resolved = shutil.which('lean', path=env.get('PATH'))
        if not resolved: raise FileNotFoundError('lean not found in Lake environment')
        lean = Path(resolved)
    ver = subprocess.run([str(lean), '--version'], capture_output=True, text=True,
                         check=True, env=env, timeout=15).stdout.strip()
    if f'version {VERSION},' not in ver:
        raise ValueError(f'Wrong Lean version: {ver}')
    old = env.get('LEAN_PATH','').split(os.pathsep)
    # Exclude this project's preexisting compiled output from a clean replay.
    old = [x for x in old if x and not Path(x).is_relative_to(root)]
    env['LEAN_PATH'] = os.pathsep.join([str(build), str(root)] + old)
    report = {'started_utc':datetime.now(timezone.utc).isoformat(), 'lean_version':ver,
              'mathlib_manifest_revision':MATHLIB, 'flags':['-j1','-DwarningAsError=true'],
              'declarations':len(index), 'sources_before':{str(p.relative_to(root)):sha256(p) for p in lean_sources},
              'commands':[], 'status':'running'}
    (evidence/'run.json').write_text(json.dumps(report,indent=2)+'\n')
    start = time.monotonic()
    for mod in MODULES + ['__root__', '__audit__']:
        if mod == '__root__': source, out = root/'Euler.lean', build/'Euler.olean'
        elif mod == '__audit__': source, out = root/'Audit.lean', build/'Audit.olean'
        else: source, out = root/'Euler'/f'{mod}.lean', build/'Euler'/f'{mod}.olean'
        command = [str(lean), '-j1', '-DwarningAsError=true','-o',str(out),str(source.relative_to(root))]
        t0 = time.monotonic()
        proc = subprocess.run(command,cwd=root,env=env,capture_output=True,text=True,timeout=args.timeout)
        label = 'Audit' if mod == '__audit__' else ('Euler' if mod == '__root__' else mod)
        (evidence/f'{label}.log').write_text(proc.stdout+proc.stderr)
        item = {'source':str(source.relative_to(root)), 'exit_code':proc.returncode,
                'seconds':round(time.monotonic()-t0,6),'command':command}
        report['commands'].append(item)
        (evidence/'run.json').write_text(json.dumps(report,indent=2)+'\n')
        print(f'{label}: exit={proc.returncode}, {item["seconds"]:.3f}s',flush=True)
        if proc.returncode: raise RuntimeError(f'Lean failed on {source}; see {label}.log')
    audit = (evidence/'Audit.log').read_text()
    rows = {}
    for name, axioms in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",audit):
        rows[name] = sorted(x.strip() for x in axioms.split(',') if x.strip())
    for name in re.findall(r"'([^']+)' does not depend on any axioms",audit): rows[name]=[]
    expected = {str(row['name']) for row in index}
    if set(rows) != expected:
        raise ValueError(f'Axiom audit coverage mismatch: missing={expected-set(rows)}, extra={set(rows)-expected}')
    all_axioms = set().union(*(set(a) for a in rows.values()))
    if not all_axioms <= ALLOWED:
        raise ValueError(f'Unapproved transitive axioms: {all_axioms-ALLOWED}')
    after = {str(p.relative_to(root)):sha256(p) for p in lean_sources}
    if after != report['sources_before']: raise ValueError('Lean source changed during replay')
    report.update({'status':'passed','seconds_total':round(time.monotonic()-start,6),
                   'axiom_union':sorted(all_axioms),'axiom_audit_count':len(rows),
                   'sources_unchanged':True,
                   'finished_utc':datetime.now(timezone.utc).isoformat()})
    (evidence/'axioms.json').write_text(json.dumps(rows,indent=2)+'\n')
    (evidence/'run.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(rows)} declarations; axioms={sorted(all_axioms)}')
    return 0

if __name__ == '__main__':
    try:
        sys.exit(run())
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
        print(f'REPLAY FAILED: {exc}',file=sys.stderr)
        sys.exit(1)
