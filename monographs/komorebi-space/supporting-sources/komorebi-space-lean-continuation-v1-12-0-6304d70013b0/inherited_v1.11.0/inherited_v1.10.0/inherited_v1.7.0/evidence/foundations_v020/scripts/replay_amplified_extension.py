#!/usr/bin/env python3
"""Replay the v0.20 additions against a separately rebuilt v0.19 baseline.
Every reused source and compiled module is checked against the supplied PASS
report. Recompiles all new modules and the cumulative root, runs the complete
axiom inventories, and exercises three negative controls. Not a full rebuild.
"""
from __future__ import annotations
import argparse,datetime as dt,hashlib,json,os,shutil,subprocess,time
from pathlib import Path
from verify import axiom_records, uncomment, ALLOWED_AXIOMS

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--baseline-report',type=Path,required=True)
    ap.add_argument('--audit-dir',type=Path,default=Path('audit/extension_replay_v020'));args=ap.parse_args()
    root=Path(__file__).resolve().parents[1];base=args.baseline.resolve();runtime=args.runtime.resolve()
    audit=args.audit_dir if args.audit_dir.is_absolute() else root/args.audit_dir;audit.mkdir(parents=True,exist_ok=True)
    report=json.loads(args.baseline_report.read_text());oldmods=json.loads((base/'audit/module_order.json').read_text())
    mods=json.loads((root/'audit/module_order.json').read_text());newmods=[m for m in mods if m not in oldmods]
    assert report['status']=='PASS' and len(oldmods)==117
    assert newmods==['AmplifiedTransport','AmplifiedHolonomy','AmplifiedRepair','AmplifiedViews','AmplifiedExamples']
    assert sha(runtime/'toolchain/bin/lean')==report['lean_binary_sha256']
    oldruns={r['source']:r for r in report['runs'] if 'source' in r}
    reused={}
    for m in oldmods:
        rel=f'KomorebiSpace/{m}.lean';obj=base/'.lake/replay/lib/lean'/Path(rel).with_suffix('.olean')
        rec=oldruns[rel];assert sha(base/rel)==sha(root/rel)==rec['source_sha256']
        assert sha(obj)==rec['olean_sha256'];reused[m]={'source_sha256':sha(root/rel),'olean_sha256':sha(obj)}
    build=root/'.lake/replay/lib/lean'
    if build.exists():shutil.rmtree(build)
    (build/'KomorebiSpace').mkdir(parents=True)
    for m in oldmods:shutil.copy2(base/f'.lake/replay/lib/lean/KomorebiSpace/{m}.olean',build/f'KomorebiSpace/{m}.olean')
    env=dict(os.environ)
    for k in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME'):env.pop(k,None)
    packages=runtime/'workspace/.lake/packages'
    env['LEAN_PATH']=os.pathsep.join(map(str,[build]+[p/'.lake/build/lib/lean' for p in sorted(packages.iterdir()) if (p/'.lake/build/lib/lean').is_dir()]))
    lean=runtime/'toolchain/bin/lean';runs=[];checks={}
    sources=[root/'KomorebiSpace'/f'{m}.lean' for m in mods]+[root/'KomorebiSpace.lean']
    before={str(p.relative_to(root)):sha(p) for p in sources}
    def run(label,argv):
        start=time.perf_counter()
        try:
            p=subprocess.run(argv,cwd=root,env=env,text=True,capture_output=True,timeout=150)
            text=p.stdout+p.stderr;code=p.returncode;timed=False
        except subprocess.TimeoutExpired as e:
            text=str(e.stdout or '')+str(e.stderr or '');code=None;timed=True
        logfile=audit/f'{label}.log';logfile.write_text(text)
        runs.append({'label':label,'argv':list(map(str,argv)),'exit_code':code,'timed_out':timed,
                     'elapsed_seconds':time.perf_counter()-start,'log':str(logfile.relative_to(root)),
                     'log_sha256':sha(logfile)})
        print(label,code,flush=True)
        if code:print(text[:3000],flush=True)
        return code,text
    checks['verified_inherited_modules']=len(reused)==117
    for m in newmods+['ROOT']:
        src='KomorebiSpace.lean' if m=='ROOT' else f'KomorebiSpace/{m}.lean'
        out=build/Path(src).with_suffix('.olean')
        code,_=run('compile_'+m,[str(lean),'-j1','-DwarningAsError=true','-DautoImplicit=false','-o',str(out),src])
        checks['compile_'+m]=code==0 and out.exists()
        if not checks['compile_'+m]:break
    if all(checks.values()):
        idx=json.loads((root/'audit/declaration_index.json').read_text())
        for kind,src in [('theorems','checks/AxiomAudit.lean'),('constructions','checks/ConstructionAudit.lean')]:
            expected={x['name'] for x in idx if (x['kind']=='theorem')==(kind=='theorems')}
            code,text=run(kind,[str(lean),'-j1','-DwarningAsError=true','-DautoImplicit=false',src])
            records=axiom_records(text)
            checks[kind+'_complete']=code==0 and set(records)==expected
            checks[kind+'_allowed']=not ({a for aa in records.values() for a in aa}-ALLOWED_AXIOMS)
        for name,marker in [('FalseStatement','error'),('Placeholder','sorry')]:
            code,text=run('negative_'+name,[str(lean),'-j1','-DwarningAsError=true',f'tests/negative/{name}.lean'])
            checks['reject_'+name]=code not in (0,None) and marker in text
        code,text=run('negative_AxiomInjection',[str(lean),'-j1','-DwarningAsError=true','tests/negative/AxiomInjection.lean'])
        bad={a for aa in axiom_records(text).values() for a in aa}-ALLOWED_AXIOMS
        checks['reject_injected_axiom']=code==0 and any(a=='injected' or a.endswith('.injected') for a in bad)
    checks['source_unchanged']=before=={str(p.relative_to(root)):sha(p) for p in sources}
    currentobj={str(p.relative_to(build)):sha(p) for p in build.rglob('*.olean')}
    result={'status':'PASS' if all(checks.values()) and len(currentobj)==123 else 'FAIL',
        'version':'0.20.0','strategy':'117 modules reused from separately rebuilt, hash-verified v0.19; five additions and root freshly compiled; complete theorem/construction inventories re-audited.',
        'baseline_report_sha256':sha(args.baseline_report),'reused':reused,'checks':checks,'runs':runs,
        'source_sha256':before,'compiled_sha256':currentobj,'finished_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'trust_boundary':['Lean compiler and cached external dependencies are trusted.','Lexical indexing is not an independent Lean parser.','This extension replay is not a second full cumulative build.']}
    (audit/'EXTENSION_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],checks,flush=True)
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
