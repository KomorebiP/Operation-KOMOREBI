#!/usr/bin/env python3
"""Recompile v0.18 additions and root against a verified, unchanged v0.17 build.

This is explicitly NOT a second full cumulative compile. It checks baseline
source and compiled hashes, recompiles the five new modules and cumulative
root, and reruns the complete theorem/construction audits and negative controls.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, shutil, subprocess, time
from pathlib import Path
from verify import axiom_records, ALLOWED_AXIOMS

NEW = ['HolonomyTransport','HolonomyCoordinates','HolonomyRepair','HolonomyViews','HolonomyExamples']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--baseline-report',type=Path,required=True)
    ap.add_argument('--audit-dir',type=Path,default=Path('audit/fresh_extension_v018'))
    args=ap.parse_args();root=Path(__file__).resolve().parents[1]
    baseline=args.baseline.resolve(); runtime=args.runtime.resolve()
    audit=args.audit_dir if args.audit_dir.is_absolute() else root/args.audit_dir
    audit.mkdir(parents=True,exist_ok=True)
    base=json.loads(args.baseline_report.read_text())
    if base['status']!='PASS': raise RuntimeError('Baseline was not fully verified')
    checks={};old=base['source_sha256']
    checks['baseline_sources_unchanged']=all(sha(baseline/name)==digest for name,digest in old.items())
    checks['all_prior_modules_identical']=all(sha(root/name)==digest for name,digest in old.items() if name!='KomorebiSpace.lean')
    expected_compiled={a['source']:a['olean_sha256'] for a in base['runs'] if a.get('olean_sha256')}
    basebuild=baseline/'.lake/replay/lib/lean'
    checks['baseline_compiled_outputs_unchanged']=all(
        sha(basebuild/Path(name).with_suffix('.olean'))==digest for name,digest in expected_compiled.items())
    if not all(checks.values()): raise RuntimeError('Baseline provenance mismatch')
    build=root/'.lake/extension-replay/lib/lean'
    if build.exists():shutil.rmtree(build)
    build.mkdir(parents=True)
    # Lean resolves a package prefix at its first search root. Place the
    # verified unchanged baseline modules in that root rather than relying
    # on fallthrough to a second KomorebiSpace/ directory.
    for name, digest in expected_compiled.items():
        if name == 'KomorebiSpace.lean':
            continue
        relative = Path(name).with_suffix('.olean')
        dest = build / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(basebuild / relative, dest)
        if sha(dest) != digest:
            raise RuntimeError('Copied baseline module failed hash validation')
    packages=runtime/'workspace/.lake/packages';env=dict(os.environ)
    for k in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME'):env.pop(k,None)
    env['LEAN_PATH']=os.pathsep.join(map(str,[build,basebuild]+[p/'.lake/build/lib/lean' for p in sorted(packages.iterdir()) if (p/'.lake/build/lib/lean').is_dir()]))
    env['PATH']=str(runtime/'toolchain/bin')+os.pathsep+env['PATH']
    sources=list((root/'KomorebiSpace').glob('*.lean'))+[root/'KomorebiSpace.lean']
    hashes={str(p.relative_to(root)):sha(p) for p in sources};runs=[]
    lean=runtime/'toolchain/bin/lean'
    def run(label,tail):
        argv=[str(lean),'-j1','-DwarningAsError=true','-DautoImplicit=false']+tail
        start=time.monotonic();p=subprocess.run(argv,cwd=root,env=env,capture_output=True,text=True,timeout=120)
        log=audit/(label+'.log');log.write_text(p.stdout+p.stderr)
        runs.append({'label':label,'argv':argv,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start,'log':str(log.relative_to(root)),'log_sha256':sha(log)})
        print(label,p.returncode,flush=True)
        if p.returncode:print((p.stdout+p.stderr)[:3000],flush=True)
        return p
    compiled={}
    for name in NEW+['ROOT']:
        src='KomorebiSpace.lean' if name=='ROOT' else f'KomorebiSpace/{name}.lean'
        out=build/Path(src).with_suffix('.olean');out.parent.mkdir(parents=True,exist_ok=True)
        p=run('compile_'+name,['-o',str(out),src])
        checks['compile_'+name]=p.returncode==0 and out.is_file()
        if not checks['compile_'+name]:break
        compiled[src]=sha(out)
    index=json.loads((root/'audit/declaration_index.json').read_text())
    for label,filename,kind in [('theorems','AxiomAudit.lean','theorem'),('constructions','ConstructionAudit.lean','other')]:
        p=run(label,['checks/'+filename]);records=axiom_records(p.stdout+p.stderr)
        names={e['name'] for e in index if (e['kind']=='theorem')==(kind=='theorem')}
        checks[label+'_complete']=p.returncode==0 and set(records)==names
        checks[label+'_axioms']=all(a in ALLOWED_AXIOMS for xs in records.values() for a in xs)
    for name,marker in [('FalseStatement','error'),('Placeholder','sorry')]:
        p=run('negative_'+name,['tests/negative/'+name+'.lean']);checks['reject_'+name]=p.returncode!=0 and marker in p.stdout+p.stderr
    p=run('negative_AxiomInjection',['tests/negative/AxiomInjection.lean']);record=axiom_records(p.stdout+p.stderr)
    checks['detect_injected_axiom']=p.returncode==0 and any(a not in ALLOWED_AXIOMS for xs in record.values() for a in xs)
    checks['sources_unchanged']=hashes=={str(p.relative_to(root)):sha(p) for p in sources}
    report={'schema':'komorebi-fresh-extension-replay-v1','version':'0.18.0',
      'finished_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
      'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'runs':runs,
      'source_sha256':hashes,'new_compiled_sha256':compiled,
      'baseline_compiled_sha256':expected_compiled,'baseline_report_sha256':sha(args.baseline_report),
      'baseline_source_root':str(baseline),'lean_binary_sha256':sha(lean),
      'scope':'Five new modules and cumulative root recompiled; unchanged 107 modules reused from a cleanly rebuilt v0.17 baseline. Complete cumulative axiom audits and negative controls rerun. Not a second full cumulative compilation.'}
    (audit/'EXTENSION_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],json.dumps(checks,indent=2),flush=True)
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
