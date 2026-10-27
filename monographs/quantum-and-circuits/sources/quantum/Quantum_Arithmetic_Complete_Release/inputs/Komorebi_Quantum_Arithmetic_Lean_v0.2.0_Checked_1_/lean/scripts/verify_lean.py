#!/usr/bin/env python3
"""Build fresh sources, audit theorem dependencies, and replay their proof terms.

Requires the pinned Lean toolchain and the pinned, cached Lake packages.
No network access or installation is performed by this script.
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
import signal
import subprocess
import sys
import time

MODULES = ['QuantumArithmeticBridge', 'FiniteFourier', 'SemanticBridge', 'Conventions', 'Publication']
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def strip_comments(s: str) -> str:
    """Remove nested Lean block comments and line comments for source audit."""
    depth = 0
    i = 0
    out = []
    while i < len(s):
        if s.startswith('/-', i):
            depth += 1
            i += 2
        elif depth and s.startswith('-/', i):
            depth -= 1
            i += 2
        elif not depth and s.startswith('--', i):
            j = s.find('\n', i)
            i = len(s) if j < 0 else j
        else:
            out.append(s[i] if not depth or s[i] == '\n' else ' ')
            i += 1
    if depth:
        raise ValueError('Unclosed Lean block comment')
    return ''.join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--toolchain', required=True, type=Path, help='Directory containing bin/lean and bin/lake')
    ap.add_argument('--packages', required=True, type=Path, help='Pinned workspace .lake/packages directory')
    ap.add_argument('--out', type=Path, default=Path('verification/final'))
    ap.add_argument('--timeout', type=int, default=300)
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    fresh = out / 'fresh'
    if fresh.exists():
        raise FileExistsError(f'Refusing to overwrite fresh build directory: {fresh}')
    fresh.mkdir()
    (fresh / '.lake').mkdir()
    os.symlink(a.packages.resolve(), fresh / '.lake' / 'packages', target_is_directory=True)
    for name in ['lakefile.toml', 'lake-manifest.json', 'lean-toolchain'] + [m+'.lean' for m in MODULES]:
        shutil.copy2(root/name, fresh/name)
    shutil.copytree(root/'negative_controls', fresh/'negative_controls')
    env = os.environ.copy()
    env['PATH'] = str(a.toolchain.resolve()/'bin') + os.pathsep + env.get('PATH','')
    env['TERM'] = 'dumb'
    env['LEAN_NUM_THREADS'] = '1'
    report = {
        'status': 'RUNNING', 'started_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'modules': MODULES, 'checks': [], 'source_sha256': {},
        'trust_boundary': 'New module proofs rebuilt and replayed against supplied pinned Lean and Mathlib cache. The compiler and dependency cache were not rebuilt from source. leanchecker uses the Lean kernel, not an independently implemented verifier.',
    }
    report_path = out/'REPORT.json'
    def save():
        report_path.write_text(json.dumps(report,indent=2)+'\n')
    def run(label, argv, expected_failure=False, diagnostic=None):
        log = out/(label+'.log')
        start = time.monotonic()
        timed_out = False
        with log.open('w') as f:
            f.write('COMMAND '+json.dumps([str(x) for x in argv])+'\n')
            f.flush()
            p = subprocess.Popen([str(x) for x in argv], cwd=fresh, env=env,
                stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                rc = p.wait(timeout=a.timeout)
            except subprocess.TimeoutExpired:
                timed_out=True
                os.killpg(p.pid, signal.SIGKILL)
                rc = p.wait()
        text = log.read_text(errors='replace')
        passed = not timed_out and ((rc != 0) if expected_failure else (rc == 0))
        if diagnostic and not re.search(diagnostic,text,re.I):
            passed=False
        entry={'label':label,'command':[str(x) for x in argv], 'returncode':rc,
               'timed_out':timed_out,'expected_failure':expected_failure,
               'seconds':round(time.monotonic()-start,3),'status':'PASS' if passed else 'FAIL',
               'log':log.name,'log_sha256':sha256(log)}
        report['checks'].append(entry)
        save()
        print(label, entry['status'], entry['seconds'], flush=True)
        if not passed:
            raise RuntimeError(label+' failed, inspect '+str(log))
        return text
    try:
        version = run('lean_version',['lean','--version'])
        if '4.34.0-rc2' not in version:
            raise RuntimeError('Wrong compiler version')
        report['lean_version']=version.strip().splitlines()[-1]
        report['compiler_sha256']=sha256(a.toolchain/'bin'/'lean')
        pin=json.loads((root/'lake-manifest.json').read_text())
        report['dependency_revisions']={p['name']:p['rev'] for p in pin['packages']}
        for p in pin['packages']:
            rev=subprocess.run(['git','-C',str(a.packages/p['name']),'rev-parse','HEAD'],
                text=True,capture_output=True,check=True).stdout.strip()
            if rev != p['rev']:
                raise RuntimeError('Dependency revision mismatch: '+p['name'])
        theorem_names=[]
        inventory=[]
        for module in MODULES:
            path=fresh/(module+'.lean')
            text=strip_comments(path.read_text())
            bad=re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', text)
            if bad: raise RuntimeError(f'Forbidden active source token in {module}: {bad.group()}')
            report['source_sha256'][module+'.lean']=sha256(path)
            for match in re.finditer(r'\btheorem\s+([A-Za-z_][A-Za-z_0-9]*)',text):
                name='Komorebi.QuantumArithmetic.'+match.group(1)
                theorem_names.append(name)
                inventory.append({'theorem':name,'module':module,
                                  'line':text[:match.start()].count('\n')+1})
        report['theorem_count']=len(theorem_names)
        (out/'THEOREM_INDEX.json').write_text(json.dumps(inventory,indent=2)+'\n')
        audit='import Publication\n'+'\n'.join('#print axioms '+n+'\n#check '+n for n in theorem_names)+'\n'
        (fresh/'AxiomAudit.lean').write_text(audit)
        run('fresh_build',['lake','--wfail','build','Publication'])
        audittext=run('axiom_audit',['lake','env','lean','-DwarningAsError=true','AxiomAudit.lean'])
        dependencies=set()
        count=0
        for name in theorem_names:
            if name not in audittext:
                raise RuntimeError('Missing theorem from audit '+name)
        for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]",audittext):
            count+=1
            dependencies.update(s.strip() for s in match.group(2).split(',') if s.strip())
        count += len(re.findall(r"'[^']+' does not depend on any axioms",audittext))
        if count != len(theorem_names):
            raise RuntimeError(f'Audit theorem count mismatch: {count} != {len(theorem_names)}')
        if dependencies-ALLOWED_AXIOMS:
            raise RuntimeError('Unapproved axioms '+repr(dependencies-ALLOWED_AXIOMS))
        report['axiom_union']=sorted(dependencies)
        report['axiom_audit_count']=count
        for module in MODULES:
            run('kernel_replay_'+module,['lake','env','leanchecker','--verbose',module])
        run('reject_false_mode',['lake','env','lean','-DwarningAsError=true','negative_controls/FalseFourierMode.lean'],True,'evaluated to false|false')
        run('reject_false_sign',['lake','env','lean','-DwarningAsError=true','negative_controls/FalseSignalSign.lean'],True,'evaluated to false|false')
        run('reject_admitted_proof',['lake','env','lean','-DwarningAsError=true','negative_controls/AdmittedProof.lean'],True,'sorry')
        report['status']='PASS'
    except Exception as exc:
        report['status']='FAIL'
        report['error']=repr(exc)
        print(report['error'],file=sys.stderr,flush=True)
    finally:
        report['finished_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
        save()
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':
    raise SystemExit(main())
