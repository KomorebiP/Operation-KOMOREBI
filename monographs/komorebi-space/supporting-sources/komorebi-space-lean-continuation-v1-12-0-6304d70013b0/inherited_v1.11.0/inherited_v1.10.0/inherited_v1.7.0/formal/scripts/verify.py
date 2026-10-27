#!/usr/bin/env python3
"""Clean, pinned, sequential source replay. Does not rebuild imported mathlib.

Usage: python3 formal/scripts/verify.py --runtime /path/to/portable-runtime --label replay1
Each label is immutable: choose a new label for a new run. Reports a failed or
incomplete attempt as such, never as success. No network access is performed.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, re, signal, subprocess, sys, time
from pathlib import Path

FORMAL = Path(__file__).resolve().parents[1]
ROOT = FORMAL.parent
sys.path.insert(0, str(ROOT / 'checks'))
from build_concordance import strip_comments

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--label', required=True)
    ap.add_argument('--timeout', type=int, default=300)
    args = ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.label):
        ap.error('label must contain only letters, digits, underscores and hyphens')
    rt = args.runtime.resolve()
    audit = ROOT / 'audit/formal' / args.label
    build = FORMAL / '.lake' / args.label / 'lib/lean'
    if audit.exists() or build.exists():
        ap.error('Refusing to reuse existing audit or build directory; use a new label')
    audit.mkdir(parents=True)
    build.mkdir(parents=True)
    env = dict(os.environ)
    env['LEAN_PATH'] = os.pathsep.join(map(str, [build] + sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))))
    env['PATH'] = str(rt/'toolchain/bin') + os.pathsep + env.get('PATH', '')
    env['KS_AUDIT_OUTPUT'] = str(audit/'axioms.json')
    lean = str(rt/'toolchain/bin/lean')
    rep = {'schema':'komorebi-space-formal-replay-v1', 'label':args.label,
           'status':'RUNNING', 'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'clean_local_build':True, 'runtime':str(rt), 'environment':{'LEAN_PATH':env['LEAN_PATH']},
           'commands':[], 'dependencies':[], 'source_scan':[],
           'trust_boundary':['Pinned external compiled dependency caches reused, not rebuilt.',
                             'Official Lean kernel/compiler, not an independent verifier.',
                             'Lean checks typed declarations, not prose or Python refinement.']}
    def save():
        (audit/'receipt.json').write_text(json.dumps(rep, indent=2)+'\n')
    def run(label, argv, *, expected=0, custom_env=None):
        path = audit/(label+'.log')
        start = time.monotonic()
        with path.open('w') as log:
            p = subprocess.Popen(argv, cwd=FORMAL, env=custom_env or env, stdout=log,
                                 stderr=subprocess.STDOUT, start_new_session=True)
            timed_out = False
            try:
                code = p.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(p.pid, signal.SIGKILL)
                p.wait(); code = 124
        text = path.read_text(errors='replace')
        passed = (code == expected) if expected == 0 else (code != 0 and not timed_out)
        if expected != 0:
            # A missing environment is not a mathematical negative control.
            passed = passed and 'error' in text and not any(t in text.lower() for t in
                ['unknown module', 'object file', 'unknown identifier', 'unknown constant',
                 'failed to load', 'no such file'])
        rec = {'label':label,'argv':argv,'exit_code':code,'timeout':timed_out,'expected':expected,
               'passed':passed,'seconds':round(time.monotonic()-start,3),
               'log':str(path.relative_to(ROOT)),'log_sha256':sha(path)}
        rep['commands'].append(rec);save()
        print(label, 'PASS' if passed else 'FAIL', code, rec['seconds'], flush=True)
        if not passed:
            raise RuntimeError(f'{label} failed. See {path}')
        return text
    auxiliary = [Path(__file__), FORMAL/'scripts/ExportAudit.lean', FORMAL/'scripts/type_names.txt',
                 FORMAL/'pinned-dependencies.json'] + sorted((FORMAL/'tests').rglob('*.lean'))
    auxiliary_before = {str(p.relative_to(FORMAL)):sha(p) for p in auxiliary}
    rep['auxiliary_sha256']=auxiliary_before
    try:
        if len(list((FORMAL/'tests/positive').glob('*.lean'))) != 1 or len(list((FORMAL/'tests/negative').glob('*.lean'))) != 6 or len(list((FORMAL/'tests/policy').glob('*.lean'))) != 1:
            raise RuntimeError('Incomplete regression/control inventory')
        rep['lean_binary_sha256']=sha(rt/'toolchain/bin/lean')
        version = run('lean_version',[lean,'--version']).strip()
        if '4.34.0-rc2' not in version or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:
            raise RuntimeError('Unexpected Lean version/commit')
        rep['lean_version'] = version
        pins = json.loads((FORMAL/'pinned-dependencies.json').read_text())
        for pkg in pins['packages']:
            actual = run('pin_'+pkg['name'],['git','-C',str(rt/'workspace/.lake/packages'/pkg['name']),'rev-parse','HEAD']).strip()
            if actual != pkg['rev']: raise RuntimeError('Dependency pin mismatch: '+pkg['name'])
            rep['dependencies'].append({'name':pkg['name'],'expected':pkg['rev'],'actual':actual})
        paths = sorted((FORMAL/'KomorebiSpace').rglob('*.lean')) + [FORMAL/'KomorebiSpace.lean']
        mods = {'.'.join(p.relative_to(FORMAL).with_suffix('').parts):p for p in paths}
        deps = {}
        for mod,p in mods.items():
            clean = strip_comments(p.read_text())
            bad = re.findall(r'\b(?:sorry|admit|axiom|native_decide|unsafe)\b',clean)
            rep['source_scan'].append({'module':mod,'bad_tokens':bad})
            if bad: raise RuntimeError(f'Forbidden positive-source tokens in {mod}: {bad}')
            dep = []
            for line in clean.splitlines():
                if line.strip().startswith('import '):
                    dep.extend(x for x in line.strip().split()[1:] if x.startswith('KomorebiSpace'))
            if any(x not in mods for x in dep): raise RuntimeError('Missing local dependency: '+mod)
            deps[mod] = sorted(set(dep))
        order=[]; visiting=set(); visited=set()
        def visit(m):
            if m in visited:return
            if m in visiting:raise RuntimeError('Local import cycle')
            visiting.add(m)
            for d in deps[m]:visit(d)
            visiting.remove(m);visited.add(m);order.append(m)
        visit('KomorebiSpace')
        if visited != set(mods):raise RuntimeError('Root does not cover all production files')
        before={str(p.relative_to(FORMAL)):sha(p) for p in paths}
        rep['source_sha256']=before
        rep['modules']=order
        rep['local_imports']=deps
        rep['production_modules']=len(paths)-1
        rep['compile_targets']=len(paths)
        save()
        flags=[lean,'-j1','-DwarningAsError=true','-DautoImplicit=false']
        for mod in order:
            out = build / (mod.replace('.','/')+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
            run('compile_'+mod,flags+['-o',str(out),str(mods[mod])])
        rep['olean_sha256']={str(p.relative_to(build)):sha(p) for p in sorted(build.rglob('*.olean'))}
        run('axiom_export',flags+[str(FORMAL/'scripts/ExportAudit.lean')])
        data=json.loads((audit/'axioms.json').read_text())
        if not data['declarations'] or data['unexpected']:raise RuntimeError('Incomplete or failed axiom report')
        seenmods={r['module'] for r in data['declarations']}
        if set(mods)-seenmods-{'KomorebiSpace'}:raise RuntimeError('Axiom report missing production module')
        rep['axiom_declarations']=len(data['declarations'])
        rep['axiom_union']=sorted({a for r in data['declarations'] for a in r['axioms']})
        rep['axiom_json_sha256']=sha(audit/'axioms.json')
        for p in sorted((FORMAL/'tests/positive').glob('*.lean')):
            run('positive_'+p.stem,flags+[str(p)])
        for p in sorted((FORMAL/'tests/negative').glob('*.lean')):
            run('negative_'+p.stem,flags+[str(p)],expected=1)
        # A deliberately introduced axiom is legal Lean, but must fail the audit policy.
        for p in sorted((FORMAL/'tests/policy').glob('*.lean')):
            run('policy_'+p.stem,flags+[str(p)],expected=1)
        after={str(p.relative_to(FORMAL)):sha(p) for p in paths}
        if before != after:raise RuntimeError('Source changed during replay')
        if auxiliary_before != {str(p.relative_to(FORMAL)):sha(p) for p in auxiliary}:
            raise RuntimeError('Verifier, pins, type-name input, or test sources changed during replay')
        rep['source_unchanged_during_run']=True
        rep['status']='PASS'
    except Exception as exc:
        rep['status']='FAIL';rep['failure']=str(exc)
        print(str(exc),file=sys.stderr,flush=True)
    finally:
        rep['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        rep['verifier_sha256']=sha(Path(__file__))
        rep['audit_program_sha256']=sha(FORMAL/'scripts/ExportAudit.lean')
        rep['test_source_sha256']={str(p.relative_to(FORMAL)):sha(p) for p in sorted((FORMAL/'tests').rglob('*.lean'))}
        save()
    print('FINAL',rep['status'],flush=True)
    return 0 if rep['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
