#!/usr/bin/env python3
"""Offline, isolated replay of the K-COS end-to-end development companion.

Requires the exact pinned portable Lean runtime. Does not fetch dependencies,
modify the official monograph, or overwrite an existing evidence directory.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, pathlib, re, shutil, subprocess, sys, tempfile, time
ROOT=pathlib.Path(__file__).resolve().parent
ALLOWED={'propext','Classical.choice','Quot.sound'}

def digest(p: pathlib.Path) -> str:
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,default=ROOT/'verification/local_replay')
    ap.add_argument('--timeout',type=int,default=900)
    args=ap.parse_args(); rt=args.runtime.resolve(); out=args.output.resolve()
    if out.exists() and any(out.iterdir()): ap.error('Output must be new or empty; existing evidence is preserved.')
    if not (rt/'toolchain/bin/lean').is_file(): ap.error('Portable runtime not found.')
    out.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy()
    for k in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME','LD_PRELOAD'): env.pop(k,None)
    env['PATH']=str(rt/'toolchain/bin')+os.pathsep+env.get('PATH','')
    env['LEAN_NUM_THREADS']='1'
    checks=[]; report={'status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks}
    def save(): (out/'run.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    with tempfile.TemporaryDirectory(prefix='kcos-e2e-') as td:
        work=pathlib.Path(td)/'lean'
        shutil.copytree(ROOT/'lean',work,ignore=shutil.ignore_patterns('.lake','__pycache__'))
        def run(name,cmd,expected=0,cwd=work,required=None,forbidden=()):
            start=time.monotonic()
            try:
                p=subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=args.timeout)
                text=p.stdout;code=p.returncode
            except subprocess.TimeoutExpired as exc:
                text=exc.stdout or ''; text=text.decode(errors='replace') if isinstance(text,bytes) else text
                (out/(name+'.log')).write_text(text)
                checks.append({'name':name,'command':cmd,'passed':False,'timeout_seconds':args.timeout})
                save(); raise RuntimeError(f'{name} timed out') from exc
            (out/(name+'.log')).write_text(text)
            ok=code==expected and (required is None or required.lower() in text.lower()) and not any(s.lower() in text.lower() for s in forbidden)
            checks.append({'name':name,'command':cmd,'cwd':str(cwd),'exit_code':code,'expected_exit_code':expected,'passed':ok,'seconds':time.monotonic()-start,'log':name+'.log'})
            save();print(('PASS ' if ok else 'FAIL ')+name,flush=True)
            if not ok: raise RuntimeError(f'{name}: unexpected result; inspect its retained log')
            return text
        try:
            run('compiler',['lean','--version'],required='6a10ac8c22beadecabdbb0919c2b50214762f91d')
            run('lake',['lake','--version'],required='4.34.0-rc2')
            if (work/'lean-toolchain').read_bytes() != (rt/'workspace/lean-toolchain').read_bytes():
                raise RuntimeError('Toolchain pin mismatch')
            target=json.loads((work/'lake-manifest.json').read_text())['packages']
            available={x['name']:x for x in json.loads((rt/'workspace/lake-manifest.json').read_text())['packages']}
            deps=[]
            for d in target:
                c=available.get(d['name'])
                if c is None or (c['url'],c['rev'])!=(d['url'],d['rev']): raise RuntimeError('Dependency manifest mismatch: '+d['name'])
                folder=rt/'workspace/.lake/packages'/d['name']
                head=run('pin_'+d['name'],['git','rev-parse','HEAD'],cwd=folder).strip()
                status=run('clean_'+d['name'],['git','status','--porcelain','--untracked-files=no'],cwd=folder)
                if head!=d['rev'] or status.strip(): raise RuntimeError('Dirty or mismatched dependency: '+d['name'])
                deps.append({'name':d['name'],'revision':head,'tracked_clean':True})
            report['dependencies']=deps;save()
            production=[work/'KomorebiQCOS.lean',*sorted((work/'KomorebiQCOS').glob('*.lean'))]
            for p in production:
                text=p.read_text()
                if re.search(r'\b(sorry|admit|sorryAx|native_decide)\b|(?m:^\s*(axiom|unsafe)\s)',text):
                    raise RuntimeError('Disallowed production token: '+str(p.relative_to(work)))
            inv=json.loads((ROOT/'docs/DECLARATIONS.json').read_text())
            audit=['import KomorebiQCOS','']+['#print axioms '+x['name'] for x in inv['declarations']]
            (work/'AxiomAudit.lean').write_text('\n'.join(audit)+'\n')
            run('attach',['bash',str(rt/'run.sh'),'attach',str(work)])
            run('strict_build',['lake','build'])
            text=run('production_axioms',['lake','env','lean','-j1','-DwarningAsError=true','AxiomAudit.lean'])
            rows=[{'name':n,'axioms':[a.strip() for a in ax.split(',') if a.strip()]} for n,ax in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",text)]
            if {x['name'] for x in rows}!={x['name'] for x in inv['declarations']} or len(rows)!=len(inv['declarations']):
                raise RuntimeError('Exact declaration audit inventory mismatch')
            if any(set(x['axioms'])-ALLOWED for x in rows): raise RuntimeError('Unexpected axiom')
            (out/'axioms.json').write_text(json.dumps(rows,indent=2)+'\n')
            run('project_kernel_replay',['lake','env','leanchecker','--verbose','KomorebiQCOS'])
            for stem in ('Positive','RecordedTilted'):
                dest=work/'.lake/build/lib/lean/Controls';dest.mkdir(parents=True,exist_ok=True)
                run('control_'+stem,['lake','env','lean','-j1','-DwarningAsError=true','-o',str(dest/(stem+'.olean')),'Controls/'+stem+'.lean'])
            control_rows=inv['controls']
            (work/'ControlAxiomAudit.lean').write_text('import Controls.Positive\nimport Controls.RecordedTilted\n'+''.join('#print axioms '+x+'\n' for x in control_rows))
            text=run('control_axioms',['lake','env','lean','-j1','-DwarningAsError=true','ControlAxiomAudit.lean'])
            ca=[{'name':n,'axioms':[a.strip() for a in ax.split(',') if a.strip()]} for n,ax in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",text)]
            if {x['name'] for x in ca}!=set(control_rows) or any(set(x['axioms'])-ALLOWED for x in ca):
                raise RuntimeError('Control axiom inventory mismatch')
            (out/'control_axioms.json').write_text(json.dumps(ca,indent=2)+'\n')
            reject=[('RejectFalseArithmetic','unsolved goals'),('RejectMissingBudget','mismatch'),('RejectReversedProbability','unsolved goals'),('RejectMidpointAsWidth','unsolved goals'),('RejectPlaceholder','declaration uses `sorry`')]
            for stem,message in reject:
                run(stem,['lake','env','lean','-j1','-DwarningAsError=true','Controls/'+stem+'.lean'],expected=1,required=message,forbidden=['unknown identifier','object file','failed to synthesize','unexpected token'])
            correspondence={}
            for p in production:
                rel=p.relative_to(work)
                if p.read_bytes()!=(ROOT/'lean'/rel).read_bytes(): raise RuntimeError('Source mutated during replay')
                correspondence[str(rel)]=digest(p)
            (out/'source_hashes.json').write_text(json.dumps(correspondence,indent=2)+'\n')
            shutil.copytree(work/'.lake/build/lib/lean/KomorebiQCOS',out/'compiled_project/KomorebiQCOS')
            for ext in ('olean','ilean','olean.private','olean.server'):
                p=work/'.lake/build/lib/lean'/('KomorebiQCOS.'+ext)
                if p.exists(): shutil.copy2(p,out/'compiled_project'/p.name)
            report.update(status='PASS',theorems=inv['theorems'],definitions=inv['definitions'],named_instances=inv['instances'],audited_declarations=len(rows),positive_control_theorems=len(control_rows),rejected_controls=len(reject),axiom_union=sorted({a for r in rows for a in r['axioms']}),kernel_scope='Project modules only, against pinned imported environments; same Lean kernel; not an independent verifier or rebuild of all Mathlib.')
        except Exception as e:
            report.update(status='FAIL',error=str(e));print('FAILED: '+str(e),flush=True)
        finally:
            report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
