#!/usr/bin/env python3
"""Rebuild and audit the matrix-to-logic bridge against a pinned offline runtime.

All commands are synchronous children of this audit. Generated independent modules
may be compiled concurrently; each uses one Lean worker. The temporary local
build directory starts empty. Upstream Mathlib is a reused, pinned compiled cache.
"""
from __future__ import annotations
import argparse,concurrent.futures,hashlib,json,os,platform,re,subprocess,sys,tempfile,time
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'propext','Classical.choice','Quot.sound'}
NEW=['MatrixObservationCode','MatrixLogicalBridge','MatrixLogicalFibers','MatrixLogicalWitnesses','MatrixImageBoundary']
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def inventory(modules):
    rows=[]
    pat=r'^(?:@\[[^\n]*?\]\s*)?(?:(?:noncomputable|protected|private)\s+)*(theorem|def|abbrev|inductive|structure|instance)\s+([\w.]+)'
    for m in modules:
        text=(ROOT/'formalization'/(m+'.lean')).read_text()
        ns=re.findall(r'^namespace\s+([\w.]+)\s*$',text,re.M)
        if len(ns)!=1:raise AssertionError('Inventory requires one explicit namespace: '+m)
        for kind,name in re.findall(pat,text,re.M):
            rows.append({'module':m,'kind':kind,'name':ns[0]+'.'+name,'new_core':m in NEW,'generated':m.startswith('Cases/')})
    if len(rows)!=len({x['name'] for x in rows}):raise AssertionError('Duplicate declaration')
    return rows

def environment(runtime):
    lean=runtime/'toolchain/bin/lean';ml=runtime/'workspace/.lake/packages/mathlib'
    pin=json.loads((ROOT/'source_records/PARENT_ENVIRONMENT.json').read_text())
    version=subprocess.check_output([str(lean),'--version'],text=True,timeout=15).strip()
    revision=subprocess.check_output(['git','-C',str(ml),'rev-parse','HEAD'],text=True,timeout=15).strip()
    if version!=pin['lean_version'] or sha(lean)!=pin['lean_binary_sha256'] or revision!=pin['mathlib_commit']:
        raise AssertionError('Runtime does not match immutable parent pins')
    for x in pin['mathlib_sources']:
        if sha(ml/x['path'])!=x['sha256']:raise AssertionError('Changed upstream source '+x['path'])
    return {'lean_version':version,'lean_binary_sha256':sha(lean),'mathlib_commit':revision,
        'mathlib_sources':pin['mathlib_sources'],'python':sys.version,'platform':platform.platform(),
        'cgroup_memory_max':Path('/sys/fs/cgroup/memory.max').read_text().strip() if Path('/sys/fs/cgroup/memory.max').exists() else 'unavailable',
        'cgroup_cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip() if Path('/sys/fs/cgroup/cpu.max').exists() else 'unavailable',
        'boundary':'Pinned upstream compiled cache reused; local sources cold rebuilt, not all Mathlib.'}

def lineage_check():
    pins=json.loads((ROOT/'source_records/INPUT_LINEAGE.json').read_text())
    for x in pins:
        if sha(ROOT/x['path'])!=x['sha256']:raise AssertionError('Parent input changed: '+x['path'])
    parents=json.loads((ROOT/'source_records/PREDECESSORS.json').read_text())
    for x in parents:
        if sha(ROOT/'history'/x['name'])!=x['sha256']:raise AssertionError('Frozen ZIP changed')
    return {'status':'PASS','copied_payloads':len(pins),'frozen_archives':parents}

def manifest(claim,cmd,inputs,outputs,run,maths,env,random=False):
    return {'schema_version':2,'claim_id':claim,
      'repository':{'commit':'Standalone merge of two immutable archives pinned in source_records/PREDECESSORS.json; no git commit','dirty':True},
      'command':cmd,'environment':{'software':[{'name':'Python','version':sys.version},{'name':'Lean','version':env.get('lean_version','not invoked')}],
         'hardware':{'platform':platform.platform(),'memory_cgroup':env.get('cgroup_memory_max'),'cpu_cgroup':env.get('cgroup_cpu_max')}},
      'mathematics':{'assertion_tested':maths['assertion'],'coefficient_domain':'Arbitrary semiring matrix certificates in Lean, Fin(p^r) generated cases; exact integers/residues in Python.',
        'conventions':'All source states, left-to-right operation words, original observation language, separate state/value tags; quantified target is actual image.',
        'inputs':[x['path'] for x in inputs],'bounds':maths['bounds'],'non_claims':['Not full first-order elementarity, QE, or theory-wide elimination of imaginaries.','No minimum logical formula or test-count theorem.','Python discoverer/checker/exporter are not verified executables.','No new all-upstream or full predecessor-corpus rebuild.']},
      'randomness':{'used':random,'generator':'Python random.Random' if random else 'none','seed':2026092103 if random else None},
      'run':{'started_at':run['started_at'],'finished_at':run['finished_at'],'runtime_seconds':run['runtime_seconds'],'exit_status':0,'status':'completed',
        'resource_limits':{'memory_bytes':4294967296 if env.get('cgroup_memory_max')=='4294967296' else None,'cpu_seconds':None,'max_cores':4,'max_threads':run.get('workers',1)},
        'per_command_wall_timeout_seconds':run.get('timeout',90),'missing_results':[],'invalid_results':[]},
      'input_artifacts':inputs,'execution_artifacts':[x['path'] for x in inputs],
      'declared_results':[x['path'] for x in outputs if x['kind']=='result'],'outputs':outputs,
      'checks':[{'name':'all declared expected outcomes','status':'PASS'},{'name':'accepted input hashes unchanged','status':'PASS'}],
      'result':'PASS','residual_risks':['Authoring-assistant self-review, not an independent researcher.','Proof concerns literal formal source; semantic transcription independently tested, not formally verified.','Reused upstream binaries are trusted as part of the pinned environment.']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--selection',choices=['all','smoke'],default='all');ap.add_argument('--workers',type=int,default=3);ap.add_argument('--python-only',action='store_true');args=ap.parse_args()
    if not 1<=args.workers<=4:raise ValueError('workers must be 1..4')
    runtime=args.runtime.resolve();lean=runtime/'toolchain/bin/lean';ev=environment(runtime)
    dump(ROOT/'evidence/ENVIRONMENT_VERIFIED.json',ev);dump(ROOT/'evidence/PARENT_PRESERVATION.json',lineage_check())
    inherited=json.loads((ROOT/'tools/inherited_modules.json').read_text());cases=json.loads((ROOT/'source_records/EXPORTED_CASES.json').read_text())
    if args.selection=='smoke':
        zero=next(x['module'] for x in cases if x['coordinates']==0)
        selected={zero,'Cases/Case000','Cases/Case001','Cases/Case201'}
        cases=[c for c in cases if c['module'] in selected]
    modules=inherited+NEW+[c['module'] for c in cases]
    if not args.python_only:
        decls=inventory(modules)
        invpath=ROOT/'evidence'/('DECLARATIONS_'+args.selection.upper()+'.json');dump(invpath,decls)
        auditdir=ROOT/'checks'/('axioms_'+args.selection);auditdir.mkdir(parents=True,exist_ok=True)
        batches=[inherited+NEW]+[[c['module'] for c in cases[i:i+32]] for i in range(0,len(cases),32)]
        audit_files=[]
        for k,mods in enumerate(batches):
            path=auditdir/f'Batch{k:02}.lean'
            text=''.join('import '+m.replace('/','.')+'\n' for m in mods)+'\n'
            text+=''.join('#print axioms '+d['name']+'\n' for d in decls if d['module'] in mods)
            path.write_text(text);audit_files.append(path)
        header='import MatrixImageBoundary\nimport Cases.Case201\nopen Komorebi.Representation\nopen Komorebi.Representation.Matrix\nopen Komorebi.ModelTheory\nopen Komorebi.ModelTheory.Standard\nopen Komorebi.ModelTheory.MatrixBridge\n'
        controls={
          'Positive':(header+'example : ImageBoundary.data.encoding = ImageBoundary.data.encoding := rfl\n',True),
          'FalseStatement':(header+'example : False := by decide\n',False),
          'Placeholder':(header+'example : True := by sorry\n',False),
          'BadTestList':(header+'example : matrixTests Komorebi.Representation.Symbolic.Logic201.data = [] := by decide\n',False),
          'BadObservationCertificate':(header+'def corrupted : CertificateData (Fin 4) 1 1 1 1 1 :=\n { ImageBoundary.data with observations := fun _ _ => 1 }\nexample : Valid corrupted := by decide\n',False),
          'BadQuantifiedTarget':(header+'example : ImageBoundary.existsOddObservation.Sat (sourceSystem ImageBoundary.data) Fin.elim0 :=\n  ImageBoundary.free_target_has_odd_observation\n',False)}
        control_files=[]
        for name,(text,expect) in controls.items():
            p=ROOT/'controls'/(name+'.lean');p.write_text(text);control_files.append((name,p,expect))
        accepted=[ROOT/'formalization'/(m+'.lean') for m in modules]+audit_files+[p for _,p,_ in control_files]+[
            Path(__file__).resolve(),ROOT/'tools/inherited_modules.json',ROOT/'source_records/EXPORTED_CASES.json',ROOT/'source_records/INPUT_LINEAGE.json',ROOT/'source_records/PREDECESSORS.json',ROOT/'source_records/PARENT_ENVIRONMENT.json',invpath]
        accepted=sorted(set(accepted));before={p:sha(p) for p in accepted};tasks=[];started=now();t0=time.monotonic()
        logdir=ROOT/'evidence'/('lean_'+args.selection);logdir.mkdir(parents=True,exist_ok=True)
        def progress():
            dump(ROOT/'evidence'/('CHECKPOINT_'+args.selection.upper()+'.json'),{'status':'IN_PROGRESS','started_at':started,'completed_tasks':len(tasks),'tasks':tasks})
        with tempfile.TemporaryDirectory(prefix='komorebi-m3-'+args.selection+'-cold-') as tmp:
            env=os.environ.copy();env['LEAN_PATH']=':'.join([tmp]+[str(p) for p in (runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')]);env['OMP_NUM_THREADS']='1'
            def run(name,argv,expect=True):
                t=time.monotonic();log=logdir/(name.replace('/','_')+'.log')
                try:
                    res=subprocess.run(argv,cwd=ROOT/'formalization',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=90)
                    out=res.stdout;rc=res.returncode;timed=False
                except subprocess.TimeoutExpired as ex:
                    out=ex.stdout or '';out=out.decode() if isinstance(out,bytes) else out;rc=None;timed=True
                log.write_text(out)
                passed=not timed and ((rc==0) if expect else (rc is not None and rc>0 and 'error:' in out))
                if not expect and any(bad in out.lower() for bad in ['unknown module prefix','does not exist','out of memory','maximum number of heartbeats','deep recursion']):passed=False
                rec={'name':name,'argv':argv,'exit_code':rc,'expected_success':expect,'timed_out':timed,'seconds':time.monotonic()-t,'passed':passed,'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
                return rec,out
            def accept(result):
                rec,out=result;tasks.append(rec);progress()
                print(f"{len(tasks):03} {'PASS' if rec['passed'] else 'FAIL'} {rec['name']} {rec['seconds']:.3f}s",flush=True)
                if not rec['passed']:
                    dump(ROOT/'results'/('FAILED_LEAN_'+args.selection.upper()+'.json'),{'status':'FAIL','tasks':tasks})
                    raise RuntimeError(json.dumps(rec)+'\n'+out)
                return out
            def build(m):
                dest=Path(tmp)/(m+'.olean');dest.parent.mkdir(parents=True,exist_ok=True)
                return run('build_'+m,[str(lean),'-j1','-DwarningAsError=true','-o',str(dest),m+'.lean'])
            for m in inherited+NEW:accept(build(m))
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
                for result in pool.map(build,[c['module'] for c in cases]):accept(result)
            axiom_text=[]
            for k,p in enumerate(audit_files):axiom_text.append(accept(run(f'axioms_{k:02}',[str(lean),'-j1','-DwarningAsError=true',str(p)])))
            all_ax='\n'.join(axiom_text);found=set()
            for block in re.findall(r'depends on axioms:\s*\[([^]]*)\]',all_ax,re.S):found.update(x.strip() for x in block.replace('\n',' ').split(',') if x.strip())
            audited=set(re.findall(r"'([^']+)'\s+(?:depends on axioms|does not depend on any axioms)",all_ax))
            missing=[d['name'] for d in decls if d['name'] not in audited]
            if found-ALLOWED or missing:raise AssertionError({'unexpected_axioms':sorted(found-ALLOWED),'missing_audits':missing})
            for name,p,expect in control_files:accept(run('control_'+name,[str(lean),'-j1','-DwarningAsError=true',str(p)],expect))
        inputs=[{'path':str(p.relative_to(ROOT)),'sha256':before[p],'sha256_after':sha(p)} for p in accepted]
        if any(x['sha256']!=x['sha256_after'] for x in inputs):raise AssertionError('Changed input during accepted audit')
        rec={'status':'PASS','selection':args.selection,'started_at':started,'finished_at':now(),'runtime_seconds':time.monotonic()-t0,'workers':args.workers,'timeout':90,
          'lean_version':ev['lean_version'],'mathlib_commit':ev['mathlib_commit'],'modules':len(modules),'inherited_modules':len(inherited),'new_generic_modules':len(NEW),'generated_modules':len(cases),
          'named_declarations':len(decls),'declaration_counts':dict(Counter(d['kind'] for d in decls)),'new_generic_counts':dict(Counter(d['kind'] for d in decls if d['new_core'])),
          'generated_counts':dict(Counter(d['kind'] for d in decls if d['generated'])),'axioms':sorted(found),'axiom_audited_names':len(audited),'tasks':tasks,
          'scope':'All selected local sources rebuilt from an empty local directory; pinned upstream cache reused. Selection='+args.selection}
        rp=ROOT/'results'/('LEAN_AUDIT_'+args.selection.upper()+'.json');dump(rp,rec)
        dump(ROOT/'evidence'/('CHECKPOINT_'+args.selection.upper()+'.json'),rec)
        outputs=[{'path':str(rp.relative_to(ROOT)),'sha256':sha(rp),'kind':'result'}]+[{'path':t['log'],'sha256':t['sha256'],'kind':'log'} for t in tasks]
        cmd=[sys.executable,'tools/audit_all.py','--runtime',str(runtime),'--selection',args.selection,'--workers',str(args.workers)]
        dump(ROOT/('LEAN_MANIFEST.json' if args.selection=='all' else 'LEAN_SMOKE_MANIFEST.json'),manifest('KMT-M3-MATRIX-LOGIC-'+args.selection.upper(),cmd,inputs,outputs,rec,
          {'assertion':'Kernel-check matrix certificate to finite logical code, standard defining formula, term-definable encoding, actual-image quantified transport, class formulas, and distinguishing formulas.',
           'bounds':{'generic_modules':len(NEW),'generated_instances':len(cases),'all_state_word_scope':'arbitrary states and arbitrary finite operation words; arbitrary observational formulas'}},ev))
    # Full independent executable audit, whether selection is all or smoke.
    pinputs=sorted(set(list(ROOT.glob('*.py'))+list((ROOT/'checks').glob('*.py'))+list((ROOT/'tools').glob('*.py'))+list((ROOT/'tests').glob('*.py'))+list((ROOT/'certificates').glob('*.json'))+list((ROOT/'exports').glob('*.json'))+list((ROOT/'formalization/Cases').glob('*.lean'))+[ROOT/'source_records/EXPORTED_CASES.json']))
    before={p:sha(p) for p in pinputs};started=now();t0=time.monotonic();cmd=[sys.executable,'tests/audit.py']
    res=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90)
    plog=ROOT/'evidence/python_final.log';plog.write_text(res.stdout)
    if res.returncode:raise RuntimeError(res.stdout)
    prp=ROOT/'results/LOGICAL_DISCOVERY_AUDIT.json';pr=json.loads(prp.read_text())
    inputs=[{'path':str(p.relative_to(ROOT)),'sha256':before[p],'sha256_after':sha(p)} for p in pinputs]
    if any(x['sha256']!=x['sha256_after'] for x in inputs):raise AssertionError('Changed Python audit input')
    prec={'started_at':started,'finished_at':now(),'runtime_seconds':time.monotonic()-t0,'workers':1,'timeout':90}
    outputs=[{'path':str(prp.relative_to(ROOT)),'sha256':sha(prp),'kind':'result'},{'path':str(plog.relative_to(ROOT)),'sha256':sha(plog),'kind':'log'}]
    dump(ROOT/'COMPUTATION_MANIFEST.json',manifest('KMT-M3-EXACT-EXECUTABLE-AUDIT',cmd,inputs,outputs,prec,
      {'assertion':'Independently check frozen matrix certificates, logical AST and literal Lean export, exact reconstruction, equal/non-equal and wrong-sort state pairs, growth witnesses, actual-image quantified queries and mutation controls.',
       'bounds':pr['bounds']|{'certificate_pairs':pr['cases'],'exhaustive_small_systems':pr['small_count']}},ev,True))
    print(json.dumps({'status':'PASS','selection':args.selection,'python_checks':pr['total_checks'],'python_cases':pr['cases'],'python_seconds':prec['runtime_seconds']},indent=2),flush=True)
if __name__=='__main__':main()
