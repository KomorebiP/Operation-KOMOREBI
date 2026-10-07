#!/usr/bin/env python3
"""Replay the pinned proof source with separate command receipts and strict negative controls.

This tool never installs software, upgrades dependencies, or edits mathematical source.
It requires the public toolchain/dependencies to have been obtained separately.
Only --clean removes padic/.lake/build. Cached dependencies are not deleted.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
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

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'padic'
PIN = '4.34.0-rc2'
COMMIT = '6a10ac8'

def snapshot() -> dict[str, str]:
    paths = list((PROJECT / 'lean').rglob('*.lean'))
    paths += list((PROJECT / 'verification').rglob('*.lean'))
    paths += [PROJECT / n for n in ('lean-toolchain', 'lakefile.lean', 'lake-manifest.json')]
    paths += [Path(__file__).resolve(), PROJECT / 'verification/evidence_parser.py',
              PROJECT / 'verification/theorem_inventory.json']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}

def negative_is_expected(text: str, placeholder: bool = False) -> bool:
    # Exactly one diagnostic: a mixed import/proof failure must not count as a control pass.
    if len(re.findall(r'(?m)^.*?\berror:', text)) != 1:
        return False
    if placeholder:
        return bool(re.search(r'declaration uses\s+[`\'\"]sorry[`\'\"]', text))
    return bool(re.search(r'Tactic\s+[`\'\"]decide[`\'\"]\s+proved that the proposition[\s\S]+?is false', text))

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--clean', action='store_true', help='Delete only padic/.lake/build before proof replay.')
    parser.add_argument('--timeout', type=int, default=900, help='Per-command timeout in seconds; default 900.')
    parser.add_argument('--output', type=Path, help='New receipt directory; must not already exist.')
    parser.add_argument('--self-test', action='store_true', help='Test diagnostic classification only; does not run Lean.')
    args = parser.parse_args()
    if args.self_test:
        tests = [
            (negative_is_expected('error: Tactic `decide` proved that the proposition\n  1 = 2\nis false'), True),
            (negative_is_expected('unknown module prefix'), False),
            (negative_is_expected('maximum recursion depth exceeded'), False),
            (negative_is_expected('error: declaration uses `sorry`', True), True),
            (negative_is_expected('warning: unused variable', True), False),
            (negative_is_expected('error: unknown module\nerror: Tactic `decide` proved that the proposition\n1 = 2\nis false'), False),
            (negative_is_expected('error: declaration uses `sorry`\nerror: unknown identifier', True), False),
        ]
        assert all(got is expected for got, expected in tests)
        print(json.dumps({'status':'PASS','scope':'Diagnostic classifier only; no Lean execution.','tests':len(tests)}))
        return 0
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    out = args.output.resolve() if args.output else PROJECT / 'results' / ('proof_replay_' + stamp)
    if out.exists():
        parser.error('Refusing to overwrite a receipt directory')
    out.mkdir(parents=True)
    before = snapshot()
    receipts: list[dict] = []
    report = {'status':'INCOMPLETE', 'scope':'Pinned project proof replay with cached dependencies. Not an independent dependency/kernel build.',
              'started_at_utc':datetime.now(timezone.utc).isoformat(), 'commands':receipts,
              'initial_project_build_present':(PROJECT / '.lake/build').exists(),
              'clean_requested':args.clean, 'proof_source_hashes_before':before}
    def finish(status: str, reason: str, exit_code: int) -> int:
        report['status'], report['reason'] = status, reason
        report['proof_source_hashes_after'] = snapshot()
        report['inputs_unchanged'] = report['proof_source_hashes_after'] == before
        if not report['inputs_unchanged']:
            report['status'] = 'FAIL'
            report['reason'] += '; frozen execution inputs changed'
            exit_code = 1
        report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        (out / 'REPLAY.json').write_text(json.dumps(report, indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':report['status'],'reason':report['reason'],'receipt_directory':str(out)},indent=2))
        return exit_code
    missing = [name for name in ('lean','lake','git') if shutil.which(name) is None]
    if missing:
        return finish('BLOCKED', 'Required executables unavailable: ' + ', '.join(missing), 2)
    def run(name: str, argv: list[str], *, negative: bool = False, placeholder: bool = False) -> tuple[bool,str]:
        log = out / (name + '.log')
        start = time.monotonic()
        timed_out = False
        launch_error = None
        code = None
        with log.open('wb') as stream:
            try:
                proc = subprocess.Popen(argv,cwd=PROJECT,stdout=stream,stderr=subprocess.STDOUT,
                                        start_new_session=(os.name != 'nt'))
                try:
                    code = proc.wait(timeout=args.timeout)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    if os.name == 'nt':
                        subprocess.run(['taskkill','/F','/T','/PID',str(proc.pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                    else:
                        os.killpg(proc.pid, signal.SIGKILL)
                    code = proc.wait()
            except OSError as exc:
                launch_error = str(exc)
                stream.write(launch_error.encode())
        text = log.read_text(errors='replace')
        passed = not timed_out and launch_error is None and (
            code != 0 and negative_is_expected(text,placeholder) if negative else code == 0)
        receipts.append({'name':name,'argv':argv,'exit_code':code,'seconds':time.monotonic()-start,
                         'timeout':timed_out,'launch_error':launch_error,'expected_rejection':negative,
                         'status':'PASS' if passed else ('TIMEOUT' if timed_out else 'FAIL'),
                         'log':log.name,'sha256':hashlib.sha256(log.read_bytes()).hexdigest()})
        return passed,text
    ok,version = run('lean_version',['lean','--version'])
    if not ok or PIN not in version or COMMIT not in version:
        return finish('BLOCKED','Lean version/commit does not match the retained pin.',2)
    ok,_ = run('lake_version',['lake','--version'])
    if not ok:
        return finish('BLOCKED','Lake version command failed.',2)
    manifest = json.loads((PROJECT / 'lake-manifest.json').read_text())
    for package in manifest['packages']:
        path = PROJECT / manifest['packagesDir'] / package['name']
        if not (path / '.git').exists():
            return finish('BLOCKED',f"Pinned dependency checkout unavailable: {package['name']}",2)
        ok,revision = run('pin_'+package['name'],['git','-C',str(path),'rev-parse','HEAD'])
        if not ok or revision.strip() != package['rev']:
            return finish('BLOCKED',f"Dependency revision differs: {package['name']}",2)
    build = PROJECT / '.lake/build'
    if args.clean and build.exists():
        if build.is_symlink():
            return finish('BLOCKED','Refusing to delete a symlinked project build directory.',2)
        shutil.rmtree(build)
    report['fresh_project_build'] = not build.exists()
    commands = [('build',['lake','build']),
                ('positive',['lake','env','lean','-DwarningAsError=true','verification/PositiveControl.lean']),
                ('concrete',['lake','env','lean','-DwarningAsError=true','verification/ResidualChecks.lean']),
                ('universal',['lake','env','lean','-DwarningAsError=true','verification/ResidualUniversal.lean']),
                ('declared_axioms',['lake','env','lean','verification/AllAxioms34.lean']),
                ('environment_axioms',['lake','env','lean','verification/KernelAxiomInventory.lean'])]
    for name,argv in commands:
        ok,_ = run(name,argv)
        if not ok:
            return finish('INCONCLUSIVE' if receipts[-1]['timeout'] else 'FAIL','Command did not pass: '+name,1)
    sys.path.insert(0,str(PROJECT / 'verification'))
    from evidence_parser import parse_declared, parse_environment
    inventory = json.loads((PROJECT / 'verification/theorem_inventory.json').read_text())
    try:
        declared = parse_declared((out / 'declared_axioms.log').read_text())
        environment = parse_environment((out / 'environment_axioms.log').read_text())
        allowed = {'propext','Quot.sound','Classical.choice'}
        assert set(declared) == set(inventory['names']), 'Declared axiom coverage differs'
        assert set(declared) <= set(environment), 'Environment inventory omits declared theorem'
        assert all(declared[n] == environment[n][1] for n in declared), 'Axiom routes disagree'
        assert all(ax <= allowed for _,ax in environment.values()), 'Unexpected theorem axioms'
        report['axiom_audit']={'status':'PASS','declared':len(declared),'environment':len(environment)}
    except (AssertionError,ValueError) as exc:
        return finish('FAIL','Fresh axiom parsing/coverage failed: '+str(exc),1)
    for name in ('FalseControl','PlaceholderControl','FalseAllWord','FalseIgnoreOutput','FalseLinearMinimum'):
        ok,_ = run(name,['lake','env','lean','-DwarningAsError=true',f'verification/{name}.lean'],
                   negative=True,placeholder=(name == 'PlaceholderControl'))
        if not ok:
            return finish('INCONCLUSIVE' if receipts[-1]['timeout'] else 'FAIL','Negative control did not produce its expected diagnostic: '+name,1)
    return finish('PASS','All requested pinned proof commands, fresh axiom checks, and negative controls passed.',0)

if __name__ == '__main__':
    raise SystemExit(main())
