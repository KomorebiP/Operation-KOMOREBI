#!/usr/bin/env python3
"""Replayable Paper III compile/audit runner with exact receipts and source snapshots."""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[1]
CORE = [
    'KomorebiPaperIII.EdgeOperators','KomorebiPaperIII.EdgeExtensions',
    'KomorebiPaperIII.Transport','KomorebiPaperIII.ReversibleConnections',
    'KomorebiPaperIII.CoordinateNaturality','KomorebiPaperIII.NonlinearObstructions',
    'KomorebiPaperIII.HolonomyBlocks','KomorebiPaperIII.PacketCoordinates',
    'KomorebiPaperIII.NonlinearPacketCoordinates','KomorebiPaperIII.PacketDirectSum',
    'KomorebiPaperIII','PaperIIIContinuation',
]
CANDIDATES = ['KomorebiPaperIII.MultilinearPacketJets','KomorebiPaperIII.BoundedPacketJetNorm','KomorebiPaperIII.ContinuousPacketJets','KomorebiPaperIII.PacketJetComposition']

def sha(path):
    return hashlib.file_digest(path.open('rb'),'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--lean',type=Path,required=True)
    ap.add_argument('--phase',choices=['core','candidates','full','audit','replay','controls','module'],required=True)
    ap.add_argument('--module')
    ap.add_argument('--label',required=True)
    ap.add_argument('--timeout',type=int,default=420)
    ap.add_argument('--objects',type=Path,default=ROOT/'build/release_objects')
    args=ap.parse_args()
    objects=args.objects.resolve()
    if args.phase in ['core','full'] and objects.exists():
        raise SystemExit('Refusing preexisting own-project object tree for a cold build: '+str(objects))
    objects.mkdir(parents=True,exist_ok=True)
    logs=ROOT/'verification'/args.label
    logs.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy()
    for key in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:
        env.pop(key,None)
    upstream=sorted((ROOT/'.lake/packages').glob('*/.lake/build/lib/lean'))
    if not upstream:
        raise SystemExit('No upstream compiled dependency directories')
    env['LEAN_PATH']=os.pathsep.join(map(str,[objects,*upstream]))
    env['PATH']=str(args.lean.parent)+os.pathsep+env.get('PATH','')
    report={'schema':'paper-iii.fresh-lean-verification/1','phase':args.phase,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'RUNNING','compiler':str(args.lean),'compiler_sha256':sha(args.lean),'runner_sha256':sha(Path(__file__)),'own_objects_initially_empty':args.phase in ['core','full'],'upstream_revisions':{p['name']:p['rev'] for p in json.loads((ROOT/'lake-manifest.json').read_text())['packages']},'LEAN_PATH':env['LEAN_PATH'],'commands':[]}
    def save():
        (logs/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    def run(module,source_dir=ROOT,expected='PASS',diagnostic=None,extra_env=None):
        source=source_dir/(module.replace('.','/')+'.lean')
        idx=len(report['commands'])
        record_dir=logs/f'{idx:03d}_{module.replace(".","_")}'
        record_dir.mkdir()
        (record_dir/'source.lean').write_bytes(source.read_bytes())
        output=objects/(module.replace('.','/')+'.olean')
        output.parent.mkdir(parents=True,exist_ok=True)
        for p in [output,Path(str(output)+'.server'),Path(str(output)+'.private'),output.with_suffix('.ilean')]:
            p.unlink(missing_ok=True)
        cmd=[str(args.lean),'-j1','-M4096','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3','-DmaxHeartbeats=8000000','-o',str(output),str(source.relative_to(source_dir))]
        local_env=env.copy()
        if extra_env: local_env.update(extra_env)
        rec={'module':module,'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'command':cmd,'cwd':str(source_dir),'expected':expected,'expected_diagnostic':diagnostic,'extra_env':extra_env or {},'status':'RUNNING'}
        report['commands'].append(rec);save()
        started=time.monotonic()
        try:
            with (record_dir/'compile.log').open('w') as stream:
                result=subprocess.run(cmd,cwd=source_dir,env=local_env,stdout=stream,stderr=subprocess.STDOUT,timeout=args.timeout)
            rec['exit_code']=result.returncode
            rec['status']='PASS' if result.returncode==0 and output.is_file() else 'FAIL'
        except subprocess.TimeoutExpired:
            rec.update(status='TIMEOUT',exit_code=None)
        text=(record_dir/'compile.log').read_text()
        rec['seconds']=time.monotonic()-started
        rec['source_unchanged']=sha(source)==rec['source_sha256']
        rec['log']=str((record_dir/'compile.log').relative_to(ROOT))
        rec['log_sha256']=sha(record_dir/'compile.log')
        rec['object_sha256']=sha(output) if output.is_file() else None
        rec['accepted']=rec['source_unchanged'] and ((rec['status']=='PASS') if expected=='PASS' else (rec['status']=='FAIL' and bool(diagnostic) and diagnostic in text))
        if expected=='PASS' and diagnostic: rec['accepted']=rec['accepted'] and diagnostic in text
        save()
        print(module,rec['status'],'accepted='+str(rec['accepted']),f"{rec['seconds']:.2f}s",flush=True)
        if not rec['accepted']: print(text[-5000:],flush=True)
        return rec['accepted']
    ok=True
    if args.phase=='module':
        if not args.module:
            raise SystemExit('--module is required for a module run')
        ok=run(args.module)
    elif args.phase=='core':
        for module in CORE:
            if not run(module):ok=False;break
    elif args.phase=='candidates':
        for module in CANDIDATES:
            if not run(module):ok=False
    elif args.phase=='full':
        for module in CORE[:-1]+CANDIDATES+CORE[-1:]:
            if not run(module):ok=False;break
    elif args.phase=='audit':
        ok=run('OwnedAudit',ROOT/'audit',diagnostic='OWNED_AUDIT_PASS')
    elif args.phase=='replay':
        ok=run('ReplayClosure',ROOT/'audit',diagnostic='REPLAY_CLOSURE_PASS')
    else:
        template=(ROOT/'audit/OwnedAudit.lean').read_text()
        # A traversal may encounter the consumer before the axiom itself. Either
        # exact audit rejection is valid; a compile/import failure has no marker.
        for name,diagnostic in [('GoodForeign',None),('BadAxiom','OWNED AUDIT REJECTED'),('BadOpaque','OWNED AUDIT REJECTED opaque'),('BadUnsafe','OWNED AUDIT REJECTED unsafe'),('BadPartial','OWNED AUDIT REJECTED unreviewed partial')]:
            ok=run(name,ROOT/'controls') and ok
            aud=template.replace('import PaperIIIContinuation','import '+name)
            aud=re.sub(r'let ownedModules : Array Name := #\[.*?\]',f'let ownedModules : Array Name := #[`{name}]',aud,count=1,flags=re.S)
            audit_name='Audit'+name
            (ROOT/'controls'/(audit_name+'.lean')).write_text(aud)
            ok=run(audit_name,ROOT/'controls',expected='PASS' if name=='GoodForeign' else 'REJECTION',diagnostic=diagnostic) and ok
        for name,diagnostic in [('FalseArithmetic','Tactic `decide` proved that the proposition'),('AdmittedProof','declaration uses `sorry`')]:
            ok=run(name,ROOT/'controls',expected='REJECTION',diagnostic=diagnostic) and ok
        ok=run('BoundaryConsumers',ROOT/'controls') and ok
        ok=run('ReplayClosure',ROOT/'audit',expected='REJECTION',diagnostic="while replaying declaration 'PaperIIIReplayControl.falseEquality'",extra_env={'KOMOREBI_REPLAY_CORRUPT':'1'}) and ok
        text=(ROOT/report['commands'][-1]['log']).read_text()
        ok=ok and 'REPLAY_CORRUPT_CONTROL_INJECTED' in text and '(kernel) declaration type mismatch' in text and 'REPLAY_CLOSURE_PASS' not in text
    report['status']='PASS' if ok else 'FAIL'
    report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    save()
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
