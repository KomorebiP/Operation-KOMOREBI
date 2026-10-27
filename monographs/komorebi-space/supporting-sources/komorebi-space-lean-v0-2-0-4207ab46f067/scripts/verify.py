#!/usr/bin/env python3
"""Clean, offline Lean replay with source, axiom and negative-control audits.

Usage: python3 scripts/verify.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
This script writes only to the project audit directory and build directory.
It does not modify the runtime, fetch dependencies or mutate a user's Library.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

EXPECTED_LEAN = '4.34.0-rc2'
EXPECTED_MATHLIB = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uncomment(text: str) -> str:
    """Remove nested Lean block comments and line comments before lexical auditing."""
    out: list[str] = []
    i = depth = 0
    while i < len(text):
        if text[i:i+2] == '/-':
            depth += 1; out.extend('  '); i += 2
        elif depth and text[i:i+2] == '-/':
            depth -= 1; out.extend('  '); i += 2
        elif depth:
            out.append('\n' if text[i] == '\n' else ' '); i += 1
        elif text[i:i+2] == '--':
            j = text.find('\n', i)
            if j < 0: break
            out.append('\n'); i = j+1
        else:
            out.append(text[i]); i += 1
    if depth:
        raise ValueError('Unclosed block comment')
    return ''.join(out)


def axiom_records(text: str) -> dict[str, list[str]]:
    records: dict[str, list[str]] = {}
    for name, body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", text, re.S):
        records[name] = [x.strip() for x in body.split(',') if x.strip()]
    for name in re.findall(r"'([^']+)' does not depend on any axioms", text):
        records[name] = []
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=os.environ.get('KOMOREBI_LEAN_RUNTIME'))
    parser.add_argument('--audit-dir', type=Path)
    parser.add_argument('--timeout', type=int, default=60)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.runtime is None:
        parser.error('Provide --runtime or set KOMOREBI_LEAN_RUNTIME.')
    runtime = args.runtime.expanduser().resolve()
    lean = runtime / 'toolchain/bin/lean'
    packages = runtime / 'workspace/.lake/packages'
    if not lean.is_file() or not packages.is_dir():
        parser.error('The supplied runtime does not contain toolchain/bin/lean and workspace/.lake/packages.')
    audit = args.audit_dir or root / 'audit/latest'
    if not audit.is_absolute(): audit = root / audit
    audit.mkdir(parents=True, exist_ok=True)
    build = root / '.lake/replay/lib/lean'
    if build.exists(): shutil.rmtree(build)
    build.mkdir(parents=True)
    depdirs = [p / '.lake/build/lib/lean' for p in sorted(packages.iterdir())
               if (p / '.lake/build/lib/lean').is_dir()]
    env = dict(os.environ)
    for name in ('LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME'):
        env.pop(name, None)
    env['PATH'] = str(runtime / 'toolchain/bin') + os.pathsep + env.get('PATH', '')
    env['LEAN_PATH'] = os.pathsep.join(map(str, [build] + depdirs))
    result: dict = {
        'schema': 'komorebi-lean-verification-v1',
        'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'project': 'Komorebi Space Lean', 'version': '0.2.0',
        'allowed_axioms': sorted(ALLOWED_AXIOMS),
        'runs': [], 'checks': {}, 'proof_boundary':
        'Named Lean declarations under their explicit hypotheses. Not an unrestricted pro-category, stack, Langlands or higher-obstruction theorem.'
    }

    def run(label: str, argv: list[str], timeout: int | None = None) -> dict:
        before = time.monotonic()
        try:
            proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True,
                                  timeout=timeout or args.timeout)
            output, status, timed_out = proc.stdout + proc.stderr, proc.returncode, False
        except subprocess.TimeoutExpired as exc:
            output = str(exc.stdout or '') + '\n' + str(exc.stderr or '')
            status, timed_out = None, True
        logfile = audit / (label + '.log'); logfile.write_text(output)
        rec = {'label': label, 'argv': argv, 'cwd': str(root), 'exit_code': status,
               'timeout': timed_out, 'elapsed_seconds': round(time.monotonic()-before, 6),
               'log': str(logfile.relative_to(root)), 'log_sha256': sha256(logfile)}
        result['runs'].append(rec)
        print(label, 'exit=' + str(status), 'time=' + str(rec['elapsed_seconds']), flush=True)
        if status not in (0, None): print(output[:3500], flush=True)
        return rec

    ver = run('lean_version', [str(lean), '--version'])
    result['lean_version'] = (audit / 'lean_version.log').read_text().strip()
    result['lean_binary_sha256'] = sha256(lean)
    result['checks']['lean_pin'] = ver['exit_code'] == 0 and EXPECTED_LEAN in result['lean_version']
    git = run('mathlib_pin', ['git', '-C', str(packages/'mathlib'), 'rev-parse', 'HEAD'])
    result['mathlib_commit'] = (audit/'mathlib_pin.log').read_text().strip()
    result['checks']['mathlib_pin'] = git['exit_code'] == 0 and result['mathlib_commit'] == EXPECTED_MATHLIB
    sources = sorted((root/'KomorebiSpace').glob('*.lean')) + [root/'KomorebiSpace.lean']
    initial_hashes = {str(p.relative_to(root)): sha256(p) for p in sources}
    forbidden = {}
    for p in sources:
        tokens = re.findall(r'\b(?:sorry|admit|axiom|unsafe|native_decide|implemented_by)\b', uncomment(p.read_text()))
        if tokens: forbidden[str(p.relative_to(root))] = tokens
    result['forbidden_tokens'] = forbidden
    result['checks']['no_project_admissions_or_axioms'] = not forbidden
    modules = json.loads((root/'audit/module_order.json').read_text())
    compiled = []
    for mod in modules + ['ROOT']:
        source = 'KomorebiSpace.lean' if mod == 'ROOT' else f'KomorebiSpace/{mod}.lean'
        olean = build / Path(source).with_suffix('.olean')
        olean.parent.mkdir(parents=True, exist_ok=True)
        rec = run('compile_'+mod, [str(lean), '-j1', '-DwarningAsError=true',
                   '-DautoImplicit=false', '-o', str(olean), source])
        rec['source'] = source; rec['source_sha256'] = sha256(root/source)
        if olean.exists(): rec['olean_sha256'] = sha256(olean)
        compiled.append(rec['exit_code'] == 0 and olean.exists())
        if not compiled[-1]: break
    result['checks']['clean_compile_all'] = len(compiled) == len(modules)+1 and all(compiled)
    indexed = json.loads((root/'audit/declaration_index.json').read_text())
    theorem_names = {e['name'] for e in indexed if e['kind'] == 'theorem'}
    result['theorem_count'] = len(theorem_names)
    result['proof_module_count'] = len(modules)
    if result['checks']['clean_compile_all']:
        ax = run('axiom_audit', [str(lean), '-j1', '-DwarningAsError=true', 'checks/AxiomAudit.lean'])
        records = axiom_records((audit/'axiom_audit.log').read_text())
        result['axioms_by_theorem'] = records
        result['unexpected_axioms'] = sorted(set(a for xs in records.values() for a in xs) - ALLOWED_AXIOMS)
        result['checks']['axiom_audit_complete'] = ax['exit_code'] == 0 and set(records) == theorem_names
        result['checks']['only_allowed_axioms'] = not result['unexpected_axioms']
        for name, marker in [('FalseStatement', 'error'), ('Placeholder', 'sorry')]:
            neg = run('negative_'+name, [str(lean), '-j1', '-DwarningAsError=true', f'tests/negative/{name}.lean'])
            log = (audit/('negative_'+name+'.log')).read_text()
            result['checks']['reject_'+name] = neg['exit_code'] not in (0, None) and marker in log
        neg = run('negative_AxiomInjection', [str(lean), '-j1', '-DwarningAsError=true', 'tests/negative/AxiomInjection.lean'])
        injected = axiom_records((audit/'negative_AxiomInjection.log').read_text())
        unexpected = set(a for xs in injected.values() for a in xs) - ALLOWED_AXIOMS
        result['injected_axiom_audit'] = {'records': injected, 'unexpected': sorted(unexpected)}
        result['checks']['reject_axiom_injection'] = (neg['exit_code'] == 0 and bool(unexpected)
            and any(a == 'injected' or a.endswith('.injected') for a in unexpected))
    else:
        result['checks']['axiom_audit_complete'] = False
    final_hashes = {str(p.relative_to(root)): sha256(p) for p in sources}
    result['source_sha256'] = initial_hashes
    result['checks']['sources_unchanged_during_verification'] = initial_hashes == final_hashes
    result['status'] = 'PASS' if all(result['checks'].values()) else 'FAIL'
    result['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    (audit/'VERIFICATION.json').write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n')
    print(result['status'], json.dumps(result['checks'],indent=2), flush=True)
    return 0 if result['status']=='PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
