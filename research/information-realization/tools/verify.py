#!/usr/bin/env python3
"""Offline serial Lean build, axiom allowlist and deliberate negative controls.
No compiler installation, network request, or source mutation is performed.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, os, re, shutil, subprocess, sys, time
from pathlib import Path
from datetime import datetime, timezone
from prepare_audit import prepare, MODULES
ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
PIN = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
VERSION = '4.34.0-rc2'

def audit_axioms(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for name, axioms in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", text):
        result[name] = [s.strip() for s in axioms.split(',') if s.strip()]
    for name in re.findall(r"'([^']+)' does not depend on any axioms", text):
        result[name] = []
    return result

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kit', type=Path, default=os.environ.get('KOMOREBI_LEAN_KIT'))
    ap.add_argument('--label', default='clean_replay')
    ap.add_argument('--timeout', type=int, default=180, help='Per Lean process timeout in seconds.')
    args = ap.parse_args()
    if not args.kit:
        ap.error('Supply --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2, or KOMOREBI_LEAN_KIT.')
    kit = args.kit.resolve()
    if not (kit/'run.sh').is_file() or not (kit/'workspace').is_dir():
        ap.error('The selected directory is not the portable Lean kit.')
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.label):
        ap.error('Use letters, digits, underscores or hyphens for --label.')
    report = ROOT/'reports'/args.label
    report.mkdir(parents=True, exist_ok=True)
    def capture(cmd: list[str], name: str) -> dict:
        start = time.monotonic()
        timed_out = False
        try:
            p = subprocess.run(cmd,cwd=kit/'workspace',capture_output=True,text=True,
                               timeout=args.timeout,check=False)
            output, code = p.stdout+p.stderr,p.returncode
        except subprocess.TimeoutExpired as exc:
            def txt(value):
                return value.decode(errors='replace') if isinstance(value,bytes) else value or ''
            output, code = txt(exc.stdout)+txt(exc.stderr),124
            timed_out = True
        (report/f'{name}.log').write_text(output)
        entry = dict(name=name,command=cmd,returncode=code,timeout=timed_out,
                     seconds=round(time.monotonic()-start,3),log=str((report/f'{name}.log').relative_to(ROOT)))
        print(f'{name}: exit {code}',flush=True)
        return entry
    run = ['bash',str(kit/'run.sh')]
    versions = capture(run+['lean','--version'],'lean_version')
    text = (report/'lean_version.log').read_text()
    if versions['returncode'] or f'version {VERSION}' not in text:
        raise RuntimeError('Compiler version check failed.')
    lake = capture(run+['lake','--version'],'lake_version')
    revision = subprocess.check_output(['git','-C',str(kit/'workspace/.lake/packages/mathlib'),
                                       'rev-parse','HEAD'],text=True).strip()
    if revision != PIN:
        raise RuntimeError('Mathlib revision does not match the pinned release.')
    inventory = prepare()
    production = sorted((ROOT/'lean/KomorebiInformation').glob('*.lean'))
    forbidden = []
    # Ignore comments so wording in documentation is not mistaken for a declaration.
    for source in production:
        text = re.sub(r'/\-.*?\-/','',source.read_text(),flags=re.S)
        text = re.sub(r'--[^\n]*','',text)
        if re.search(r'\b(sorry|admit|axiom|native_decide|implemented_by|unsafe)\b',text):
            forbidden.append(str(source.relative_to(ROOT)))
    if forbidden:
        raise RuntimeError(f'Forbidden trust escape in production source: {forbidden}')
    build = ROOT/'lean/.lake/build/lib/lean'
    if build.exists():
        shutil.rmtree(build)
    (build/'KomorebiInformation').mkdir(parents=True)
    prefix = run+['lake','env','bash','-c',
        'export LEAN_PATH="$1:$LEAN_PATH"; shift; exec lean "$@"',
        'komorebi-information',str(build),'-j1','-DwarningAsError=true','-R',str(ROOT/'lean')]
    steps = []
    for module in MODULES+['__root__']:
        relative = 'KomorebiInformation' if module=='__root__' else f'KomorebiInformation/{module}'
        entry = capture(prefix+['-o',str(build/f'{relative}.olean'),str(ROOT/'lean'/f'{relative}.lean')],
                        'build_'+module)
        steps.append(entry)
        if entry['returncode']:
            raise RuntimeError(f'Lean compilation failed in {module}; see {entry["log"]}')
    audit = capture(prefix+[str(ROOT/'lean/Audit.lean')],'axiom_audit')
    if audit['returncode']:
        raise RuntimeError('The live axiom audit did not compile.')
    dependencies = audit_axioms((report/'axiom_audit.log').read_text())
    expected_names = {row['name'] for row in inventory}
    if set(dependencies) != expected_names:
        raise RuntimeError(f'Axiom audit coverage mismatch: missing {expected_names-set(dependencies)}')
    unapproved = {k:v for k,v in dependencies.items() if not set(v)<=ALLOWED}
    if unapproved:
        raise RuntimeError(f'Unapproved axioms: {unapproved}')
    negatives = []
    for name in ['FalseArithmetic','Placeholder','MutatedHaarDecoder','FalseSourceRecovery']:
        entry = capture(prefix+[str(ROOT/'lean/NegativeControls'/f'{name}.lean')],'negative_'+name)
        output = (ROOT/entry['log']).read_text()
        if entry['returncode'] == 0 or entry['timeout']:
            raise RuntimeError(f'Negative control {name} did not reject normally.')
        if 'object file' in output or 'unknownIdentifier' in output:
            raise RuntimeError(f'Negative control {name} failed for an unrelated import/name error.')
        if name=='Placeholder':
            if 'sorry' not in output:
                raise RuntimeError('Placeholder was not rejected for the intended reason.')
        elif 'proved that the proposition' not in output or 'is false' not in output:
            raise RuntimeError(f'{name}: expected a false-decidable-proposition rejection.')
        entry['expected_rejection_verified']=True
        negatives.append(entry)
    entry = capture(prefix+[str(ROOT/'lean/NegativeControls/InjectedAxiom.lean')],
                    'negative_InjectedAxiom')
    dep = audit_axioms((ROOT/entry['log']).read_text())
    if entry['returncode'] or not any(set(v)-ALLOWED for v in dep.values()):
        raise RuntimeError('The axiom contamination control did not trigger the allowlist.')
    entry['compiler_accepts_explicit_axiom']=True
    entry['dependency_policy_rejects']=True
    negatives.append(entry)
    summary = dict(status='PASS',timestamp_utc=datetime.now(timezone.utc).isoformat(),
                   lean=(report/'lean_version.log').read_text().strip(),
                   mathlib_revision=revision,clean_build=True,build_mode='serial, -j1, warningAsError=true',
                   fresh_theorem_declarations=len(inventory),
                   module_counts=dict(collections.Counter(row['module'] for row in inventory)),
                   production_source_trust_escape_scan='PASS',
                   axiom_allowlist=sorted(ALLOWED),theorem_axioms=dependencies,
                   build_steps=steps,axiom_audit=audit,negative_controls=negatives,
                   environment_checks=[versions,lake],
                   new_python_theory_replay=False,
                   source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in production})
    (report/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'PASS: {len(inventory)} theorem declarations, clean build, full axiom audit, 5 negative controls.',flush=True)
    return 0
if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'VERIFICATION FAILED: {type(exc).__name__}: {exc}',file=sys.stderr)
        raise SystemExit(1)
