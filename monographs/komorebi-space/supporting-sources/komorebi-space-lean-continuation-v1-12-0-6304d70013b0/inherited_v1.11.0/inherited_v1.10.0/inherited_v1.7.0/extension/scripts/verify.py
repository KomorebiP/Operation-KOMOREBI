#!/usr/bin/env python3
"""Clean verification of the focused regularization extension and its actual imports.

This recompiles the three new modules and three inherited dependency modules,
plus the focused root, from source. It is not a cumulative 138-module replay.
The inherited canonical project is preserved separately and is never edited.
"""
from pathlib import Path
import argparse, datetime, hashlib, json, os, re, signal, subprocess, sys, time, shutil
EXT=Path(__file__).resolve().parents[1];ROOT=EXT.parent
sys.path.insert(0,str(ROOT/'checks'))
from build_concordance import strip_comments

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',required=True,type=Path);ap.add_argument('--label',required=True)
    args=ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.label):ap.error('Use a simple alphanumeric replay label')
    audit=ROOT/'audit/extension'/args.label;work=EXT/'.work'/args.label
    if audit.exists() or work.exists():ap.error('Refusing to overwrite an existing run')
    audit.mkdir(parents=True);work.mkdir(parents=True);build=work/'lib';build.mkdir()
    rt=args.runtime.resolve();lean=rt/'toolchain/bin/lean'
    env=os.environ.copy();env['LEAN_PATH']=':'.join(map(str,[build]+sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))))
    env['PATH']=str(rt/'toolchain/bin')+':'+env.get('PATH','');env['KS_EXTENSION_AUDIT']=str(audit/'axioms.json')
    rep={'status':'RUNNING','label':args.label,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'scope':'Focused regularization closure, not the cumulative canonical project.', 'clean_project_build':True,
         'runtime':str(rt),'commands':[],'dependencies':[],'source_files':{},'source_scan':[],
         'trust_boundary':['Official pinned Lean kernel/compiler.','Imported pinned mathlib caches reused, not rebuilt.','Not universal Python refinement or machine-certified prose.']}
    def save():(audit/'receipt.json').write_text(json.dumps(rep,indent=2)+'\n')
    def run(label,argv,negative=False):
        log=audit/(label+'.log');start=time.monotonic();timed=False
        with log.open('w') as f:
            q=subprocess.Popen(argv,cwd=work,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=q.wait(timeout=1200 if label=='axiom_export' else 300)
            except subprocess.TimeoutExpired:
                timed=True;os.killpg(q.pid,signal.SIGKILL);q.wait();code=124
        text=log.read_text(errors='replace');ok=code==0
        if negative:
            ok=code!=0 and not timed and ('error' in text.lower()) and not any(s in text.lower() for s in ['unknown module','unknown identifier','object file','no such file','unknown constant'])
        rep['commands'].append({'label':label,'argv':list(map(str,argv)),'exit_code':code,'passed':ok,'expected_rejection':negative,
                                'timeout':timed,'seconds':time.monotonic()-start,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log)})
        save();print(label,'PASS' if ok else 'FAIL',code,flush=True)
        if not ok:raise RuntimeError(label+' failed; see '+str(log))
        return text
    try:
        inputs=list((EXT/'KomorebiSpace').glob('*.lean'))+[EXT/'KomorebiSpaceRegularization.lean',Path(__file__),EXT/'scripts/ExportAudit.lean']+list((EXT/'tests').rglob('*.lean'))
        rep['input_hashes']={str(p.relative_to(ROOT)):sha(p) for p in inputs}
        rep['lean_binary_sha256']=sha(lean)
        version=run('lean_version',[lean,'--version']).strip()
        if '4.34.0-rc2' not in version or '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:raise RuntimeError('Wrong compiler')
        rep['lean_version']=version
        for pkg in json.loads((ROOT/'formal/pinned-dependencies.json').read_text())['packages']:
            actual=run('pin_'+pkg['name'],['git','-C',rt/'workspace/.lake/packages'/pkg['name'],'rev-parse','HEAD']).strip()
            if actual!=pkg['rev']:raise RuntimeError('Wrong pin: '+pkg['name'])
            rep['dependencies'].append({'name':pkg['name'],'revision':actual})
        sources={};order=[];active=set()
        def visit(mod):
            if mod in sources:return
            if mod in active:raise RuntimeError('Import cycle')
            active.add(mod)
            rel=Path(mod.replace('.','/')+'.lean');p=EXT/rel
            if not p.exists():p=ROOT/'formal'/rel
            if not p.exists():raise RuntimeError('Missing source '+mod)
            txt=strip_comments(p.read_text());bad=re.findall(r'\b(?:sorry|admit|axiom|native_decide|unsafe)\b',txt)
            if bad:raise RuntimeError('Forbidden production source '+mod)
            deps=[d for line in txt.splitlines() if line.strip().startswith('import ') for d in line.split()[1:] if d.startswith('KomorebiSpace')]
            for d in deps:visit(d)
            sources[mod]=p;order.append(mod);active.remove(mod)
            rep['source_scan'].append({'module':mod,'forbidden':bad,'local_imports':deps})
        visit('KomorebiSpaceRegularization')
        supplied={'KomorebiSpace.'+p.stem for p in (EXT/'KomorebiSpace').glob('*.lean')}
        if not supplied.issubset(sources):raise RuntimeError('Focused root omits a new module')
        rep['source_files']={mod:{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'new':p.is_relative_to(EXT)} for mod,p in sources.items()}
        rep['compile_order']=order;rep['compile_targets']=len(order);rep['new_modules']=len(supplied)
        rep['inherited_modules']=len(order)-len(supplied)-1
        for mod,p in sources.items():
            dest=work/(mod.replace('.','/')+'.lean');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        flags=[lean,'-j1','-DwarningAsError=true','-DautoImplicit=false']
        for mod in order:
            out=build/(mod.replace('.','/')+'.olean');out.parent.mkdir(parents=True,exist_ok=True)
            run('compile_'+mod,flags+['-o',out,work/(mod.replace('.','/')+'.lean')])
        rep['object_hashes']={str(p.relative_to(build)):sha(p) for p in build.rglob('*.olean')}
        (work/'wanted_modules.txt').write_text('\n'.join(order)+'\n')
        shutil.copy2(EXT/'scripts/ExportAudit.lean',work/'ExportAudit.lean')
        run('axiom_export',flags+[work/'ExportAudit.lean'])
        axs=json.loads((audit/'axioms.json').read_text())
        if not axs['declarations'] or axs['unexpected']:raise RuntimeError('Incomplete or failed axiom audit')
        actualmods={r['module'] for r in axs['declarations']}
        if set(order)-{'KomorebiSpaceRegularization'}-actualmods:raise RuntimeError('Audit missing a module')
        rep['axiom_declarations']=len(axs['declarations']);rep['axiom_report_sha256']=sha(audit/'axioms.json')
        rep['axiom_union']=sorted({a for row in axs['declarations'] for a in row['axioms']})
        for family in ['positive','negative','policy']:
            paths=sorted((EXT/'tests'/family).glob('*.lean'))
            if len(paths)!={'positive':1,'negative':4,'policy':1}[family]:raise RuntimeError('Control inventory mismatch')
            for p in paths:
                q=work/'tests'/family/p.name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
                run(family+'_'+p.stem,flags+[q],family!='positive')
        if any(sha(ROOT/r['path'])!=r['sha256'] for r in rep['source_files'].values()):raise RuntimeError('Source changed during run')
        if any(sha(ROOT/p)!=h for p,h in rep['input_hashes'].items()):raise RuntimeError('Verifier or tests changed during run')
        rep['source_unchanged_during_run']=True;rep['status']='PASS'
    except Exception as e:
        rep['status']='FAIL';rep['failure']=str(e);print(str(e),flush=True)
    finally:
        rep['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
    print('FINAL',rep['status'],flush=True);return 0 if rep['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
