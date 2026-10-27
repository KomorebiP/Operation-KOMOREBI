#!/usr/bin/env python3
"""Recheck Paper VII third block, with atomic checkpoints and verified resume.

Author: Komorebi P. Checks twelve modules and two expected rejection controls.
Exit codes: 0 = complete PASS, 1 = failure, 2 = paused/incomplete.
Use --max-checks 3 --resume repeatedly in hosts with short command limits.
No Mathlib rebuild, independent dependency recheck, or earlier-paper rebuild.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time

MATHLIB_REV = "aeb72f1e9981b6d35b426b16dca7759be3e7ba06"
LEAN_VERSION = "4.34.0-rc2"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
MODULES = ("ComputationalSeed", "TensorRefinement", "MovingFrames", "CanonicalConnection", "KrausChannels",
           "QuantumPacketCore", "SchurFeshbach", "LowModeConvergence", "ConstraintAudit", "SeedOrbit", "CyclicProjectors", "EuclideanTransfer")


def without_comments(text: str) -> str:
    """Discard Lean comments (including nested block comments) and string contents."""
    result: list[str] = []
    i, depth = 0, 0
    while i < len(text):
        if text.startswith("/-", i):
            depth += 1
            i += 2
        elif depth and text.startswith("-/", i):
            depth -= 1
            i += 2
            result.append(" ")
        elif depth:
            i += 1
        elif text.startswith("--", i):
            j = text.find("\n", i)
            i = len(text) if j < 0 else j
        elif text[i] == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
            i += 1
            result.append(" ")
        else:
            result.append(text[i])
            i += 1
    if depth:
        raise ValueError("Unterminated block comment")
    return "".join(result)


def run(command: list[str], timeout: int, cwd: Path | None = None) -> tuple[int, str, float]:
    started = time.monotonic()
    try:
        proc = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, timeout=timeout)
        return proc.returncode, proc.stdout, round(time.monotonic() - started, 3)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or ""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return 124, output + "\nVERIFIER TIMEOUT\n", round(time.monotonic() - started, 3)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--max-checks', type=int, help='Pause after this many fresh checks')
    args = parser.parse_args()
    if args.timeout < 1 or (args.max_checks is not None and args.max_checks < 1):
        parser.error('Timeout and max-checks must be positive')
    base = Path(__file__).resolve().parents[1]
    kit = args.kit.expanduser().resolve()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = (args.out or base/'verification'/('rerun_'+stamp)).resolve()
    out.mkdir(parents=True, exist_ok=True)
    summary = out/'SUMMARY.json'
    inventory = json.loads((base/'verification/theorem_inventory.json').read_text())
    if set(inventory) != set(MODULES):
        raise ValueError('Inventory module set mismatch')
    runner = base/'scripts/check_low_memory.py'
    runner_hash = sha(runner)
    prior = json.loads(summary.read_text()) if args.resume and summary.exists() else {}
    report = {
        'release':'PRSC_VII_v0.3.0_Checked_Third_Block',
        'started_utc':prior.get('started_utc',stamp),
        'expected_lean_version':LEAN_VERSION, 'expected_mathlib_revision':MATHLIB_REV,
        'allowed_axioms': sorted(ALLOWED_AXIOMS), 'runner_sha256':runner_hash,
        'modules':[], 'negative_controls':[],
        'scope':{'manuscript_items_checked':16,'manuscript_finite_items':19,
                 'manuscript_finite_items_not_checked':3,'continuum_conjectures_not_proved':5,
                 'new_manuscript_items_this_block':5,'new_theorem_declarations':64,
                 'prior_block_theorem_declarations':82,'prior_papers_rerun':False,
                 'original_numerical_suite_rerun':False,
                 'mathlib_rebuilt_or_independently_rechecked':False}
    }
    def checkpoint() -> None:
        report['theorem_declarations'] = sum(r['theorem_declarations'] for r in report['modules'])
        report['complete'] = (len(report['modules']) == len(MODULES) and
                              len(report['negative_controls']) == 2)
        report['pass'] = (report['complete'] and report['runtime']['pass'] and
                         all(r['pass'] for r in report['modules']+report['negative_controls']))
        report['total_module_seconds'] = round(sum(r['seconds'] for r in report['modules']),3)
        report['updated_utc'] = datetime.now(timezone.utc).isoformat()
        tmp = summary.with_suffix('.json.tmp')
        tmp.write_text(json.dumps(report, indent=2)+'\n')
        tmp.replace(summary)
    version_cmd = ['bash',str(kit/'run.sh'),'lean','--version']
    rc, version, seconds = run(version_cmd, 45, kit/'workspace')
    (out/'lean_version.log').write_text(version)
    manifest = json.loads((kit/'workspace/lake-manifest.json').read_text())
    mathlib = next((x for x in manifest['packages'] if x['name']=='mathlib'),{})
    grc, rev, _ = run(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),'rev-parse','HEAD'],20)
    report['runtime'] = {'version':version.strip(),'version_exit_code':rc,
        'version_seconds':seconds,'manifest_mathlib_revision':mathlib.get('rev'),
        'actual_mathlib_revision':rev.strip(),'git_exit_code':grc,
        'pass':rc==0 and LEAN_VERSION in version and grc==0 and rev.strip()==MATHLIB_REV and
               mathlib.get('rev')==MATHLIB_REV}
    if not report['runtime']['pass']:
        checkpoint(); print('FAIL: runtime or dependency pins',flush=True); return 1
    previous_runtime = prior.get('runtime',{})
    same_runtime = (previous_runtime.get('version')==version.strip() and
                    previous_runtime.get('actual_mathlib_revision')==rev.strip() and
                    prior.get('runner_sha256')==runner_hash)
    def cache_ok(row: dict, source: Path, logpath: Path) -> bool:
        return bool(same_runtime and row.get('pass') and row.get('sha256')==sha(source)
                    and logpath.is_file() and row.get('log_sha256')==sha(logpath))
    old_modules = {r['module']:r for r in prior.get('modules',[])}
    old_controls = {r['name']:r for r in prior.get('negative_controls',[])}
    # Restore only successful, hash-matching entries. Failed or stale entries are rechecked.
    for name in MODULES:
        source = base/'formalization'/(name+'.lean')
        row = old_modules.get(name,{})
        if cache_ok(row,source,out/(name+'.log')) and set(row.get('axiom_audits',{}))==set(inventory[name]):
            report['modules'].append(row)
    for name in ('FalseEquality','SorryPlaceholder'):
        source=base/'verification/negative_controls'/(name+'.lean')
        row=old_controls.get(name,{})
        if cache_ok(row,source,out/(name+'.log')):
            report['negative_controls'].append(row)
    checkpoint()
    completed=0
    def exhausted() -> bool:
        return args.max_checks is not None and completed>=args.max_checks
    for name in MODULES:
        if any(r['module']==name for r in report['modules']):
            print(name+': cached PASS (source and log hashes verified)',flush=True); continue
        if exhausted(): break
        source=base/'formalization'/(name+'.lean')
        stripped=without_comments(source.read_text())
        forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',stripped)))
        declarations=re.findall(r'\btheorem\s+(\w+)',stripped)
        expected=set(inventory[name])
        source_audits=set(re.findall(r'^#print axioms ([\w.]+)',stripped,re.M))
        cmd=[sys.executable,str(runner),'--kit',str(kit),'--threads','1','--timeout',str(args.timeout),str(source)]
        rc, log, seconds=run(cmd,args.timeout+90)
        logfile=out/(name+'.log'); logfile.write_text(log)
        audits={n:[a.strip() for a in ax.split(',') if a.strip()] for n,ax in
                re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",log)}
        unexpected=sorted({a for ax in audits.values() for a in ax}-ALLOWED_AXIOMS)
        good=(rc==0 and not forbidden and not unexpected and set(audits)==expected==source_audits
              and len(declarations)==len(expected) and
              not re.search(r'\b(?:warning|error):',log,re.I))
        row={'module':name,'source':str(source.relative_to(base)),'sha256':sha(source),
             'command':cmd,'exit_code':rc,'seconds':seconds,'theorem_declarations':len(declarations),
             'forbidden_tokens':forbidden,'axiom_audits':audits,'unexpected_axioms':unexpected,
             'log':logfile.name,'log_sha256':sha(logfile),'checked_utc':datetime.now(timezone.utc).isoformat(),
             'pass':good}
        report['modules'].append(row); completed+=1; checkpoint()
        print(f"{name}: {'PASS' if good else 'FAIL'} ({len(declarations)} declarations, {seconds}s)",flush=True)
        if not good:
            print(log,flush=True); return 1
    if len(report['modules'])==len(MODULES):
        for name,marker in [('FalseEquality','decide'),('SorryPlaceholder','sorry')]:
            if any(r['name']==name for r in report['negative_controls']): continue
            if exhausted(): break
            source=base/'verification/negative_controls'/(name+'.lean')
            cmd=[sys.executable,str(runner),'--kit',str(kit),'--threads','1','--timeout',str(args.timeout),str(source)]
            rc,log,seconds=run(cmd,args.timeout+90)
            logfile=out/(name+'.log');logfile.write_text(log)
            good=rc==1 and 'error:' in log and marker in log
            report['negative_controls'].append({'name':name,'expected_exit_code':1,'exit_code':rc,
                 'seconds':seconds,'source':str(source.relative_to(base)),'sha256':sha(source),
                 'command':cmd,'log':logfile.name,'log_sha256':sha(logfile),'pass':good})
            completed+=1;checkpoint()
            print(f"{name}: {'PASS (expected rejection)' if good else 'FAIL'}",flush=True)
            if not good: print(log,flush=True);return 1
    checkpoint()
    if not report['complete']:
        print('PAUSED: checkpoint saved; rerun with --resume. Overall PASS not yet claimed.',flush=True)
        return 2
    print(f"COMPLETE {'PASS' if report['pass'] else 'FAIL'}: {report['theorem_declarations']} declarations; {summary}",flush=True)
    return 0 if report['pass'] else 1

if __name__=='__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        print(f'Verification failed: {exc}',file=sys.stderr)
        raise SystemExit(1)
