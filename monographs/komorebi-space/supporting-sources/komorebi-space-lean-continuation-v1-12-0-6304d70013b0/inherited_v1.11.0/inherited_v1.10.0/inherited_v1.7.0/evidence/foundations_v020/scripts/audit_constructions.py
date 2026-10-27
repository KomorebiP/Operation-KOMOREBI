#!/usr/bin/env python3
"""Audit axiom dependencies of every explicit non-theorem in the complete v0.20.0 project.

Run scripts/verify.py first. This is supplementary to, not a replacement for,
the complete theorem audit. No compiler or dependency downloads are performed.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from verify import ALLOWED_AXIOMS, axiom_records

MODULES = {f.stem for f in (Path(__file__).resolve().parents[1]/'KomorebiSpace').glob('*.lean')}

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True, type=Path)
    parser.add_argument('--audit-dir', type=Path, default=Path('audit/constructions'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    runtime = args.runtime.resolve()
    lean = runtime/'toolchain/bin/lean'
    packages = runtime/'workspace/.lake/packages'
    build = root/'.lake/replay/lib/lean'
    if not (build/'KomorebiSpace.olean').is_file():
        parser.error('Compile the project with scripts/verify.py first.')
    if not lean.is_file() or not packages.is_dir():
        parser.error('Invalid portable Lean runtime directory.')
    audit = args.audit_dir if args.audit_dir.is_absolute() else root/args.audit_dir
    audit.mkdir(parents=True, exist_ok=True)
    indexed = json.loads((root/'audit/declaration_index.json').read_text())
    names = [e['name'] for e in indexed
             if Path(e['file']).stem in MODULES and e['kind'] != 'theorem']
    request = root/'checks/ConstructionAudit.lean'
    expected = 'import KomorebiSpace\n\nset_option autoImplicit false\n\n' + ''.join(
        '#print axioms '+name+'\n' for name in names)
    if request.read_text() != expected:
        parser.error('ConstructionAudit.lean does not match the declaration index.')
    sources = [root/'KomorebiSpace'/f'{name}.lean' for name in sorted(MODULES)] + [request]
    hashes = {str(p.relative_to(root)): digest(p) for p in sources}
    env = dict(os.environ)
    for key in ('LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME'):
        env.pop(key, None)
    env['LEAN_PATH'] = os.pathsep.join(str(p) for p in [build] + [
        p/'.lake/build/lib/lean' for p in sorted(packages.iterdir())
        if (p/'.lake/build/lib/lean').is_dir()])
    argv = [str(lean), '-j1', '-DwarningAsError=true', '-DautoImplicit=false',
            'checks/ConstructionAudit.lean']
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    start = time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=root, env=env, capture_output=True,
                              text=True, timeout=120)
        output, code, timed_out = proc.stdout + proc.stderr, proc.returncode, False
    except subprocess.TimeoutExpired as exc:
        output = str(exc.stdout or '') + '\n' + str(exc.stderr or '')
        code, timed_out = None, True
    log = audit/'construction_axioms.log'
    log.write_text(output)
    records = axiom_records(output)
    unexpected = sorted({a for xs in records.values() for a in xs} - ALLOWED_AXIOMS)
    checks = {'compiler_success': code == 0,
              'all_requested_declarations_reported': set(records) == set(names),
              'only_allowed_axioms': not unexpected,
              'sources_unchanged': hashes == {str(p.relative_to(root)):digest(p) for p in sources}}
    result = {'status':'PASS' if all(checks.values()) else 'FAIL',
              'started_at_utc':started, 'elapsed_seconds':time.monotonic()-start,
              'argv':argv, 'cwd':str(root), 'exit_code':code, 'timeout':timed_out,
              'declaration_count':len(names), 'checks':checks,
              'axioms_by_declaration':records, 'unexpected_axioms':unexpected,
              'source_sha256':hashes, 'log':str(log.relative_to(root)),
              'log_sha256':digest(log),
              'boundary':'Explicit indexed non-theorem declarations in the project. Compiler and dependency declarations remain trusted.'}
    (audit/'CONSTRUCTION_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'], 'constructions=',len(names), checks)
    if result['status'] != 'PASS':
        print(output[:5000])
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
