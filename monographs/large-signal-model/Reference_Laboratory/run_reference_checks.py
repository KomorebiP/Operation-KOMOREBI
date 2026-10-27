"""Replay the reference laboratory with source-bound resumable checkpoints.

Run: python run_reference_checks.py --verify-hashes
For bounded execution, add --batch-start 0 --batch-count 4 --session audit,
then continue at successive indices using the same session. Reports bind each
batch to one source/input snapshot and environment. They are reproducibility
records, not cryptographic attestations of untrusted machines or formal proofs.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
VERSION = '1.0.0'
SCRIPTS = [
 'checks/exact_foundation_checks.py','checks/learning_stability_checks.py',
 'checks/controlled_stochastic_checks.py','checks/certified_domain_checks.py',
 'checks/curved_continuous_checks.py','checks/discovery_evidence_checks.py',
 'examples/output_only_example.py','examples/observable_probability_example.py',
 'examples/certified_probability_example.py','examples/replay_probability_certificate.py',
 'examples/continuous_moment_example.py','examples/replay_continuous_certificate.py',
 'examples/discover_quadratic_example.py','examples/replay_quadratic_certificate.py',
 'examples/robust_noisy_example.py','examples/robust_comparison_example.py',
 'examples/replay_robust_certificate.py','checks/robust_curved_checks.py',
 'examples/dependent_signal_generator.py','examples/dependent_data_certificate.py',
 'examples/replay_dependent_data_certificate.py','examples/reduced_repair_example.py',
 'examples/replay_reduced_repair.py','checks/data_supported_checks.py',
 'checks/audit_regressions.py','checks/verify_source_lineage.py','checks/verify_proof_register.py',
 'checks/release_regressions.py','checks/verify_release_freeze.py']


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execution_snapshot() -> dict[str, str]:
    """Bind code, fixed example inputs and dependency declarations, not outputs."""
    paths = set(ROOT.rglob('*.py'))
    paths.update((ROOT/'examples').glob('*.json'))
    paths.update(ROOT.glob('requirements*.txt'))
    fixed = ['PROOF_REGISTER.json','SCENARIO_REGISTER.json','SOURCE_LINEAGE.json',
             'theory/FOUNDATIONS.md','provenance/0.8.0/FOUNDATIONS.md',
             'provenance/0.8.0/run_reference_checks.py','provenance/0.9.0/FOUNDATIONS.md',
             'RELEASE_CONTRACT.json']
    for name in fixed:
        if (ROOT/name).exists(): paths.add(ROOT/name)
    return {p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)
            if p.is_file() and '__pycache__' not in p.parts and
            ('provenance' not in p.parts or p.relative_to(ROOT).as_posix() in fixed)}


def environment() -> dict[str, Any]:
    packages = {}
    for name in ['numpy','sympy','scipy']:
        try: packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: packages[name] = None
    return {'python':sys.version, 'implementation':platform.python_implementation(),
            'platform':platform.platform(), 'packages':packages}


def validate_resume(report: dict[str, Any], start: int, session: str) -> None:
    if report.get('version') != VERSION or report.get('session') != session:
        raise ValueError('Checkpoint version/session mismatch. Start a new session.')
    if report.get('expected_scripts') != SCRIPTS:
        raise ValueError('Checkpoint script inventory changed. Start a new session.')
    if report.get('execution_snapshot') != execution_snapshot():
        raise ValueError('Source or fixed example input changed between batches. Start a new session.')
    if report.get('environment') != environment():
        raise ValueError('Execution environment changed between batches. Start a new session.')
    runs = report.get('runs')
    if not isinstance(runs,list) or len(runs) != start:
        raise ValueError('Continuation must follow the recorded prefix exactly.')
    for expected,row in zip(SCRIPTS[:start],runs):
        if (row.get('script') != expected or row.get('passed') is not True or
                row.get('returncode') != 0 or row.get('source_sha256') != digest(ROOT/expected)):
            raise ValueError('Prior success record does not match the current source and expected prefix.')


def run_script(script: str) -> dict[str, Any]:
    start = time.perf_counter()
    before = digest(ROOT/script)
    try:
        r = subprocess.run([sys.executable,str(ROOT/script)],cwd=ROOT,text=True,
                           capture_output=True,timeout=180)
        changed = digest(ROOT/script) != before
        return {'script':script,'source_sha256':before,
                'seconds':round(time.perf_counter()-start,6),'returncode':r.returncode,
                'stdout':r.stdout,'stderr':r.stderr,'source_changed_during_run':changed,
                'passed':r.returncode==0 and not changed}
    except subprocess.TimeoutExpired as exc:
        return {'script':script,'source_sha256':before,
                'seconds':round(time.perf_counter()-start,6),'returncode':None,
                'stdout':str(exc.stdout or ''),'stderr':str(exc.stderr or ''),
                'passed':False,'error':'180-second subprocess timeout'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-hashes',action='store_true')
    parser.add_argument('--batch-start',type=int,default=0)
    parser.add_argument('--batch-count',type=int,default=len(SCRIPTS))
    parser.add_argument('--session',default='default')
    args = parser.parse_args()
    if (not re.fullmatch(r'[A-Za-z0-9_-]{1,48}',args.session) or
            not 0 <= args.batch_start < len(SCRIPTS) or args.batch_count < 1):
        parser.error('Invalid session or batch range.')
    folder = ROOT/'verification/replay_checkpoints'
    folder.mkdir(parents=True,exist_ok=True)
    path = folder/(args.session+'.json')
    if args.batch_start == 0:
        report = {'version':VERSION,'session':args.session,'environment':environment(),
                  'expected_scripts':SCRIPTS,'execution_snapshot':execution_snapshot(),
                  'runs':[],'hash_check':None,'passed':False,'complete':False,
                  'proof_kernel_run':False,'production_runtime_modified':False}
    else:
        if not path.exists(): parser.error('No checkpoint exists for this session.')
        report = json.loads(path.read_text(encoding='utf-8'))
        try: validate_resume(report,args.batch_start,args.session)
        except ValueError as exc: parser.error(str(exc))
    if args.verify_hashes:
        if args.batch_start != 0: parser.error('Verify hashes before the first mutating batch only.')
        report['hash_check'] = run_script('checks/verify_bundle.py')
        print(report['hash_check']['stdout'],end='',flush=True)
        if not report['hash_check']['passed']: raise SystemExit('Hash check failed.')
    def save() -> None:
        report['complete'] = len(report['runs']) == len(SCRIPTS)
        report['passed'] = (report['complete'] and all(x['passed'] for x in report['runs'])
                            and report['execution_snapshot'] == execution_snapshot())
        text = json.dumps(report,indent=2)+'\n'
        path.write_text(text,encoding='utf-8')
        (ROOT/'verification/reference_replay.json').write_text(text,encoding='utf-8')
    save()
    for script in SCRIPTS[args.batch_start:min(len(SCRIPTS),args.batch_start+args.batch_count)]:
        if report['execution_snapshot'] != execution_snapshot():
            raise SystemExit('Source/input snapshot changed before next script. Start a new session.')
        row = run_script(script)
        if report['execution_snapshot'] != execution_snapshot():
            row['passed'] = False
            row['snapshot_changed_during_run'] = True
        report['runs'].append(row)
        save()
        print(('PASS' if row['passed'] else 'FAIL')+': '+script,flush=True)
        if not row['passed']:
            print(row['stdout']); print(row['stderr'],file=sys.stderr)
            raise SystemExit(1)
    print(f"Completed {len(report['runs'])}/{len(SCRIPTS)} scripts; complete replay PASS = {report['passed']}.",flush=True)

if __name__ == '__main__': main()
