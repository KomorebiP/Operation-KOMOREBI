#!/usr/bin/env python3
"""Recheck Paper VIII first block, with atomic checkpoints and verified resume.

Author: Komorebi P. Checks six modules and two expected rejection controls.
Exit codes: 0 = complete PASS, 1 = failure, 2 = paused/incomplete.
Use --max-checks 3 --resume repeatedly in hosts with short command limits.
No Mathlib rebuild or independent dependency recheck. One unchanged Paper VII module is rebuilt.
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
MODULES = ("QuantumPacketCore", "PacketIR", "TransferSupport", "LowRankAlgebra", "PacketPerturbation", "BoundaryChecks")
CONSTRUCTIONS = {"PacketIR": {"KomorebiPaperVIII.coordinatePackets"}}



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


def parse_axiom_audits(log: str) -> dict[str, list[str]]:
    """Parse both Lean audit forms; an explicitly axiom-free theorem is valid.

    Missing reports remain missing, so the exact inventory comparison fails closed.
    Duplicate report names are rejected rather than overwritten silently.
    """
    audits: dict[str, list[str]] = {}
    pattern = re.compile(
        r"^'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)\s*$",
        re.MULTILINE,
    )
    for match in pattern.finditer(log):
        name, body = match.groups()
        if name in audits:
            raise ValueError(f"Duplicate axiom audit: {name}")
        audits[name] = [] if body is None else [a.strip() for a in body.split(',') if a.strip()]
    return audits



def local_dependencies(base: Path, name: str) -> list[str]:
    """Read local module imports; duplicate public/private imports count once."""
    text = without_comments((base/'formalization'/(name+'.lean')).read_text())
    imports = re.findall(r'^\s*(?:public\s+)?import\s+(?:all\s+)?([\w.]+)\s*$', text, re.M)
    return sorted({x for x in imports if x in MODULES})


def dependency_sources(base: Path, name: str, active: frozenset[str] = frozenset()) -> dict[str, str]:
    """Hash transitive local source dependencies; reject cycles."""
    if name in active:
        raise ValueError('Local import cycle at '+name)
    result: dict[str, str] = {}
    for dep in local_dependencies(base, name):
        result[dep] = sha(base/'formalization'/(dep+'.lean'))
        result.update(dependency_sources(base, dep, active | {name}))
    return dict(sorted(result.items()))


def build_hashes(build: Path, name: str) -> dict[str, str]:
    """Public/private interfaces and IR are all part of a cached module identity."""
    return {p.name: sha(p) for p in sorted(build.glob(name+'.*')) if p.is_file()}


def artifacts_match(build: Path, name: str, saved: dict[str, str]) -> bool:
    return bool(name+'.olean' in saved and name+'.olean.private' in saved
                and saved == build_hashes(build, name))


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
    build = out/'build'
    build.mkdir(exist_ok=True)
    inventory = json.loads((base/'verification/theorem_inventory.json').read_text())
    if set(inventory) != set(MODULES):
        raise ValueError('Inventory module set mismatch')
    runner = base/'scripts/check_low_memory.py'
    runner_hash = sha(runner)
    inventory_hash = sha(base/'verification/theorem_inventory.json')
    verifier_hash = sha(Path(__file__).resolve())
    prior = json.loads(summary.read_text()) if args.resume and summary.exists() else {}
    report = {
        'release':'PRSC_VIII_v0.1.0_Checked_First_Block',
        'started_utc':prior.get('started_utc',stamp),
        'expected_lean_version':LEAN_VERSION, 'expected_mathlib_revision':MATHLIB_REV,
        'allowed_axioms': sorted(ALLOWED_AXIOMS), 'runner_sha256':runner_hash,
        'verifier_sha256':verifier_hash, 'inventory_sha256':inventory_hash,
        'modules':[], 'negative_controls':[],
        'scope':{'manuscript_items_checked':10,'manuscript_proved_items':56,
                 'manuscript_proved_items_not_fully_checked':46,
                 'classical_inputs_not_formalized':4,
                 'new_theorem_declarations':41,
                 'reused_theorem_declarations':19,
                 'reused_foundation_module':'QuantumPacketCore from PRSC VII v0.6.0, unchanged',
                 'prior_papers_rebuilt_in_full':False,
                 'gpu_benchmarks_rerun':False,
                 'mathlib_rebuilt_or_independently_rechecked':False}

    }
    def checkpoint() -> None:
        report['theorem_declarations'] = sum(r['theorem_declarations'] for r in report['modules'])
        report['construction_audit_count'] = sum(len(r.get('construction_audits',[])) for r in report['modules'])
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
                    prior.get('runner_sha256')==runner_hash and
                    prior.get('verifier_sha256')==verifier_hash and
                    prior.get('inventory_sha256')==inventory_hash)
    def cache_ok(row: dict, source: Path, logpath: Path) -> bool:
        return bool(same_runtime and row.get('pass') and row.get('sha256')==sha(source)
                    and logpath.is_file() and row.get('log_sha256')==sha(logpath))
    old_modules = {r['module']:r for r in prior.get('modules',[])}
    old_controls = {r['name']:r for r in prior.get('negative_controls',[])}
    # Restore only successful, hash-matching entries. Failed or stale entries are rechecked.
    for name in MODULES:
        source = base/'formalization'/(name+'.lean')
        row = old_modules.get(name,{})
        deps = dependency_sources(base, name)
        accepted = {r['module']:r for r in report['modules']}
        dep_build = {d:accepted[d]['build_sha256'] for d in deps if d in accepted}
        if (cache_ok(row,source,out/(name+'.log'))
                and set(row.get('axiom_audits',{}))==set(inventory[name])
                and set(dep_build)==set(deps)
                and row.get('dependency_source_sha256')==deps
                and row.get('dependency_build_sha256')==dep_build
                and artifacts_match(build, name, row.get('build_sha256',{}))):
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
            print(name+': cached PASS (sources, dependencies, compiled artifacts and logs verified)',flush=True); continue
        if exhausted(): break
        source=base/'formalization'/(name+'.lean')
        stripped=without_comments(source.read_text())
        forbidden=sorted(set(re.findall(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',stripped)))
        declarations=re.findall(r'\btheorem\s+(\w+)',stripped)
        expected=set(inventory[name])
        source_audits=set(re.findall(r'^#print axioms ([\w.]+)',stripped,re.M))
        deps = dependency_sources(base, name)
        accepted = {r['module']:r for r in report['modules']}
        if not set(deps) <= set(accepted):
            raise ValueError('Module order does not build all dependencies of '+name)
        dep_build = {d:accepted[d]['build_sha256'] for d in deps}
        # Remove stale outputs before any new compile, so failures cannot reuse old binaries.
        for old_output in build.glob(name+'.*'):
            old_output.unlink()
        cmd=[sys.executable,str(runner),'--kit',str(kit),'--threads','1','--timeout',str(args.timeout),
             '--import-dir',str(build),'--output',str(build/(name+'.olean')),str(source)]
        rc, log, seconds=run(cmd,args.timeout+90)
        logfile=out/(name+'.log'); logfile.write_text(log)
        audits=parse_axiom_audits(log)
        unexpected=sorted({a for ax in audits.values() for a in ax}-ALLOWED_AXIOMS)
        compiled = build_hashes(build, name)
        good=(rc==0 and artifacts_match(build,name,compiled) and not forbidden and not unexpected and set(audits)==expected==source_audits
              and len(declarations)+len(CONSTRUCTIONS.get(name,set()))==len(expected)
              and set(declarations)=={a.rsplit('.',1)[-1] for a in expected-CONSTRUCTIONS.get(name,set())} and
              not re.search(r'\b(?:warning|error):',log,re.I))
        row={'module':name,'source':str(source.relative_to(base)),'sha256':sha(source),
             'command':cmd,'exit_code':rc,'seconds':seconds,'theorem_declarations':len(declarations),
             'construction_audits': sorted(CONSTRUCTIONS.get(name,set())),
             'dependency_source_sha256':deps, 'dependency_build_sha256':dep_build,
             'build_sha256':compiled, 'forbidden_tokens':forbidden,'axiom_audits':audits,'unexpected_axioms':unexpected,
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
