#!/usr/bin/env python3
"""Resumable synchronous cold audit. Every batch validates all input and completed
build hashes. No background tasks. Use --init once, --batch 6 until complete,
then --finish. Only --finish writes a PASS manifest after every task is complete.
"""
from __future__ import annotations
import argparse,json,os,re,sys,time,tempfile,subprocess
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_release import ROOT,NEW,ALLOWED,modules,inventory,environment,make_manifest,sha,now,dump
STATE=ROOT/'new_evidence/BATCH_STATE.json'

def verify(st):
    for i in st['inputs']:
        if sha(ROOT/i['path'])!=i['sha256']:raise ValueError('changed accepted input '+i['path'])
    for i in st['built_artifacts']:
        if not Path(i['path']).is_file() or sha(i['path'])!=i['sha256']:raise ValueError('changed build artifact '+i['path'])
    for t in st['tasks']:
        if sha(ROOT/t['log'])!=t['sha256']:raise ValueError('changed completed log')
    for p,h in st['runtime_hashes'].items():
        if sha(p)!=h:raise ValueError('changed toolchain/source '+p)

def init(runtime):
    if STATE.exists():
        old=json.loads(STATE.read_text())
        if old['status'] not in ('COMPLETE','FAILED'):raise ValueError('existing incomplete run: resume, do not silently overwrite')
        stamp=str(int(time.time()));dump(ROOT/'new_evidence'/('previous_batch_'+stamp+'.json'),old)
    ev=environment(runtime);dump(ROOT/'new_evidence/ENVIRONMENT.json',ev)
    mods=modules();decls=inventory(mods)
    dump(ROOT/'new_evidence/DECLARATIONS.json',decls);dump(ROOT/'new_evidence/MODULES.json',mods)
    ax=ROOT/'new_checks/AxiomAudit.lean';ax.write_text(''.join('import '+m.replace('/','.')+'\n' for m in mods)+'\n'+''.join('#print axioms '+d['name']+'\n' for d in decls))
    import zipfile
    parent=ROOT/'history/Komorebi_ModelTheory_Normalization_v0.3.zip'
    if sha(parent)!='e694d635ad8582b5f13b415825ee58821bec2c6e37854d7b8e6969903902c42d':raise ValueError('parent SHA')
    keep=[]
    with zipfile.ZipFile(parent) as z:
        for n in z.namelist():
            if '/formalization/' in n and n.endswith('.lean'):
                p=ROOT/'formalization'/n.split('/formalization/',1)[1]
                if p.read_bytes()!=z.read(n):raise ValueError('changed parent source '+str(p))
                keep.append(str(p.relative_to(ROOT)))
    dump(ROOT/'new_evidence/PARENT_PRESERVATION.json',{'status':'PASS','parent_sha256':sha(parent),'unchanged_lean_modules':len(keep),'files':keep})
    controls=[('Positive',True),('False',False),('Placeholder',False),('WrongLoopResult',False),('PrematureTrace',False),('BadSeparation',False)]
    accepted=sorted(set([ROOT/'formalization'/(m+'.lean') for m in mods]+[ax]+list((ROOT/'new_checks/controls').glob('*.lean'))+
      [Path(__file__).resolve(),ROOT/'new_checks/audit_release.py',ROOT/'tools/audit_all.py',ROOT/'tools/validate_manifest.py',ROOT/'source_records/PARENT_ENVIRONMENT.json',ROOT/'new_evidence/DECLARATIONS.json']))
    inputs=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in accepted]
    tmp=Path(tempfile.mkdtemp(prefix='komorebi-worklist-batched-cold-'));lean=runtime/'toolchain/bin/lean'
    plan=[]
    for m in mods:
        dest=tmp/(m+'.olean');dest.parent.mkdir(parents=True,exist_ok=True)
        plan.append({'name':'build_'+m,'argv':[str(lean),'-j1','-DwarningAsError=true','-o',str(dest),m+'.lean'],'expect':True,'module':m})
    plan.append({'name':'axioms','argv':[str(lean),'-j1','-DwarningAsError=true',str(ax)],'expect':True})
    for n,ex in controls:plan.append({'name':'control_'+n,'argv':[str(lean),'-j1','-DwarningAsError=true',str(ROOT/'new_checks/controls'/(n+'.lean'))],'expect':ex})
    runtime_hashes={str(lean):sha(lean)}
    ml=runtime/'workspace/.lake/packages/mathlib'
    for x in ev['mathlib_sources']:runtime_hashes[str(ml/x['path'])]=sha(ml/x['path'])
    # Load-bearing new dependencies, in addition to inherited pinned files.
    for path in ['Mathlib/GroupTheory/Coset/Card.lean','Mathlib/LinearAlgebra/Finsupp/LinearCombination.lean','Mathlib/Data/Nat/Log.lean','Mathlib/Data/ZMod/Basic.lean']:
        runtime_hashes[str(ml/path)]=sha(ml/path)
    st={'status':'IN_PROGRESS','started_at':now(),'runtime':str(runtime),'build':str(tmp),'environment':ev,'inputs':inputs,'runtime_hashes':runtime_hashes,
        'plan':plan,'tasks':[],'built_artifacts':[],'modules':mods,'declarations':decls,'invocations':[], 'compile_seconds':0.0}
    dump(STATE,st);print(json.dumps({'status':'INITIALIZED_COLD','modules':len(mods),'tasks':len(plan),'empty_build':str(tmp)},indent=2))

def batch(st,limit):
    if st['status'] not in ('IN_PROGRESS','TASKS_COMPLETE'):raise ValueError('run not resumable '+st['status'])
    verify(st);start=now();t0=time.monotonic();completed=0
    runtime=Path(st['runtime']);env=os.environ.copy();env['OMP_NUM_THREADS']='1';env['OPENBLAS_NUM_THREADS']='1'
    env['LEAN_PATH']=':'.join([st['build']]+[str(p) for p in (runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')])
    logdir=ROOT/'new_evidence/lean_batched';logdir.mkdir(parents=True,exist_ok=True)
    while len(st['tasks'])<len(st['plan']) and completed<limit:
        spec=st['plan'][len(st['tasks'])];t=time.monotonic();log=logdir/(spec['name']+'.log')
        try:
            c=subprocess.run(spec['argv'],cwd=ROOT/'formalization',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
            text=c.stdout;rc=c.returncode;timed=False
        except subprocess.TimeoutExpired as e:
            text=e.stdout or '';text=text.decode() if isinstance(text,bytes) else text;rc=None;timed=True
        log.write_text(text)
        passed=not timed and ((rc==0) if spec['expect'] else (rc is not None and rc>0 and 'error:' in text))
        if not spec['expect'] and any(x in text.lower() for x in ['does not exist','unknown module prefix','maximum number of heartbeats','deep recursion','out of memory']):passed=False
        rec={'name':spec['name'],'argv':spec['argv'],'exit_code':rc,'expected_success':spec['expect'],'timed_out':timed,'seconds':time.monotonic()-t,
             'passed':passed,'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
        st['tasks'].append(rec);completed+=1;st['compile_seconds']+=rec['seconds']
        if passed and 'module' in spec:
            for p in Path(st['build']).glob(spec['module']+'.*'):
                if p.is_file():st['built_artifacts'].append({'path':str(p),'sha256':sha(p)})
        if not passed:st['status']='FAILED'
        st['last_observed_at']=now();dump(STATE,st)
        print(f'{len(st["tasks"]):02} {"PASS" if passed else "FAIL"} {spec["name"]} {rec["seconds"]:.2f}s',flush=True)
        if not passed:raise RuntimeError(text)
    st['invocations'].append({'argv':sys.argv,'started_at':start,'finished_at':now(),'runtime_seconds':time.monotonic()-t0,'tasks_completed':completed})
    if len(st['tasks'])==len(st['plan']):st['status']='TASKS_COMPLETE'
    verify(st);dump(STATE,st);print(st['status'],len(st['tasks']), '/', len(st['plan']))

def finish(st):
    if len(st['tasks'])!=len(st['plan']) or not all(t['passed'] for t in st['tasks']):raise ValueError('not all tasks completed')
    verify(st)
    ax=ROOT/next(x['log'] for x in st['tasks'] if x['name']=='axioms');text=ax.read_text();found=set()
    for b in re.findall(r'depends on axioms:\s*\[([^]]*)\]',text,re.S):found.update(x.strip() for x in b.replace('\n',' ').split(',') if x.strip())
    audited=set(re.findall(r"'([^']+)'\s+(?:depends on axioms|does not depend on any axioms)",text))
    decls=st['declarations'];missing=[x['name'] for x in decls if x['name'] not in audited]
    if missing or found-ALLOWED:raise ValueError({'missing':missing,'axioms':list(found-ALLOWED)})
    st['status']='COMPLETE';st['finished_at']=now();dump(STATE,st)
    result={'status':'PASS','started_at':st['started_at'],'finished_at':st['finished_at'],'runtime_seconds':sum(x['runtime_seconds'] for x in st['invocations']),
       'compile_seconds':st['compile_seconds'],'timing_scope':'sum of active recorded batch invocation times, excludes user/tool intervals','workers':1,'timeout':90,
       'modules':len(st['modules']),'new_modules':len(NEW),'inherited_modules_rebuilt':len(st['modules'])-len(NEW),
       'named_declarations':len(decls),'declaration_counts':dict(Counter(x['kind'] for x in decls)),
       'new_counts':dict(Counter(x['kind'] for x in decls if x['new'])),
       'new_generic_counts':dict(Counter(x['kind'] for x in decls if x['new'] and not x['generated_trace'] and x['module']!='DiscoveryExamples')),
       'generated_trace_counts':dict(Counter(x['kind'] for x in decls if x['generated_trace'])),
       'axioms':sorted(found),'all_declarations_audited':len(audited),'tasks':st['tasks'],
       'cold':True,'batches':st['invocations'],'boundary':'Entire 23-module selected local dependency closure cold rebuilt; upstream cache reused, not a new full historical corpus rebuild.'}
    rp=ROOT/'results/DISCOVERY_LEAN_AUDIT.json';dump(rp,result)
    inputs=[x|{'sha256_after':sha(ROOT/x['path'])} for x in st['inputs']]
    outputs=[{'path':str(rp.relative_to(ROOT)),'sha256':sha(rp),'kind':'result'}]+[{'path':t['log'],'sha256':t['sha256'],'kind':'log'} for t in st['tasks']]
    cmd=[sys.executable,'new_checks/audit_batched.py','--runtime',st['runtime'],'--init; --batch 6 repeated synchronously; --finish']
    m=make_manifest('KMT-M4-VERIFIED-DISCOVERY-COLD-BATCHES',cmd,inputs,outputs,result,
       {'assertion':'Executable exact row discovery terminates with its full observable span and original-language defining formula; four certified queue traces equal the reference result without executing its enumerative oracle.',
        'bounds':{'new_modules':len(NEW),'all_prime_precision_dimensions':True,'generated_trace_instances':4,'tasks':len(st['tasks'])}},st['environment'])
    m['run']['batch_invocations']=st['invocations'];m['run']['command_note']='Actual concrete Lean argv and batch argv are retained in result.tasks and batch_invocations; command is the documented compound protocol.'
    dump(ROOT/'LEAN_MANIFEST.json',m)
    print(json.dumps({k:v for k,v in result.items() if k not in ['tasks','batches']},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path);ap.add_argument('--init',action='store_true');ap.add_argument('--batch',type=int);ap.add_argument('--finish',action='store_true');a=ap.parse_args()
    if a.init:
        if a.runtime is None:raise ValueError('--runtime required with --init')
        init(a.runtime.resolve())
    elif a.batch is not None:
        if not 1<=a.batch<=30:raise ValueError('batch 1..30')
        batch(json.loads(STATE.read_text()),a.batch)
    elif a.finish:finish(json.loads(STATE.read_text()))
    else:ap.error('choose --init, --batch, or --finish')
