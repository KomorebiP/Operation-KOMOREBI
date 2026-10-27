#!/usr/bin/env python3
"""Strict cold Lean audit plus an independent finite reference replay.

Supply the pinned portable runtime directory. No network access is used. All
new mathematical sources compile with warningAsError. A cached Mathlib is used;
this script does not claim to recheck every upstream .olean from source.
"""
from __future__ import annotations
import argparse,hashlib,json,os,platform,re,subprocess,sys,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODULES=json.loads((ROOT/'tools/module_order.json').read_text())
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def inventory():
    rows=[]
    for i,m in enumerate(MODULES):
        ns='Komorebi.Representation' if i<2 else 'Komorebi.ModelTheory' if i<6 else 'Komorebi.ModelTheory.Standard'
        text=(ROOT/'formalization'/f'{m}.lean').read_text()
        for k,n in re.findall(r'^(?:noncomputable\s+)?(theorem|def|abbrev|inductive|structure|instance)\s+([\w.]+)',text,re.M):
            rows.append({'module':m,'kind':k,'name':ns+'.'+n,'new':i>=6})
    if len({d['name'] for d in rows})!=len(rows):raise AssertionError('Duplicate declaration inventory')
    return rows

def make_manifest(claim,cmd,inputs,outputs,record,assertion,bounds,random=False):
    return {'schema_version':2,'claim_id':claim,
      'repository':{'commit':'standalone successor of v0.1; source_records/PREDECESSOR.json pins immutable predecessor','dirty':True},
      'command':cmd,'environment':{'software':[{'name':'Python','version':sys.version},{'name':'Lean','version':record.get('lean_version','not used')}],'platform':platform.platform()},
      'mathematics':{'assertion_tested':assertion,'coefficient_domain':'Arbitrary typed deterministic systems and tagged states/values in Lean; exact finite integer tables in Python.',
        'conventions':'Complete observation-value naming; source state variables newest-first, target bound variables append; state-guarded quantifiers; every source state admissible.',
        'inputs':[x['path'] for x in inputs],'bounds':bounds,'non_claims':['Not unrestricted first-order elementarity, QE, or elimination of imaginaries.','Python is not formally verified or extracted.','No all-upstream cold Mathlib proof replay.']},
      'randomness':{'used':random,'seed':2026092102 if random else None,'generator':'Python random.Random' if random else 'none'},
      'run':{'started_at':record['started_at'],'finished_at':record['finished_at'],'runtime_seconds':record['runtime_seconds'],
        'exit_status':0,'status':'completed','wall_cap_seconds':60,'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':1},'missing_results':[],'invalid_results':[]},
      'input_artifacts':inputs,'execution_artifacts':[x['path'] for x in inputs],
      'declared_results':[x['path'] for x in outputs if x['kind']=='result'],'outputs':outputs,
      'checks':[{'name':'accepted input hashes unchanged','status':'PASS'},{'name':'all declared execution outcomes','status':'PASS'}],
      'result':'PASS','residual_risks':['Semantic and proof review is self-review.','Pinned upstream cache reused; external source hashes and revision recorded.','60-second timeout is per command, not total audit.']}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=Path);args=ap.parse_args()
    runtime=args.runtime.resolve();lean=runtime/'toolchain/bin/lean';ml=runtime/'workspace/.lake/packages/mathlib'
    version=subprocess.check_output([str(lean),'--version'],text=True,timeout=15).strip()
    if '6a10ac8c22beadecabdbb0919c2b50214762f91d' not in version:raise AssertionError('Unpinned Lean version')
    revision=subprocess.check_output(['git','-C',str(ml),'rev-parse','HEAD'],text=True,timeout=15).strip()
    if revision!='aeb72f1e9981b6d35b426b16dca7759be3e7ba06':raise AssertionError('Unpinned Mathlib revision')
    for item in json.loads((ROOT/'evidence/ENVIRONMENT_VERIFIED.json').read_text())['mathlib_sources']:
        if sha(ml/item['path'])!=item['sha256']:raise AssertionError('Changed upstream source')
    decls=inventory();dump(ROOT/'evidence/DECLARATION_INVENTORY.json',decls)
    (ROOT/'formalization/AxiomAudit.lean').write_text('import StandardLogicalBoundaries\nimport PathCompilerBridge\n'+''.join('#print axioms '+d['name']+'\n' for d in decls))
    header='import StandardLogicalBoundaries\nopen Komorebi.ModelTheory\nopen Komorebi.ModelTheory.Standard\n'
    controls={
      'Positive':(header+'example : standardRealize twoObservedStates (toMathlib nestedRememberOuter) Fin.elim0 := nested_binder_translation\n',True),
      'FalseStatement':(header+'example : False := by decide\n',False),
      'Placeholder':(header+'example : True := by sorry\n',False),
      'BadGuard':(header+'example : standardRealize oneObservedState (toMathlib existsTrueObservation) Fin.elim0 := unguarded_value_is_spurious_witness\n',False),
      'BadStateEquality':(header+'example : standardRealize constantCollapse fixedPointFormula (fun _ => true) := standard_fixedpoint_true\n',False),
      'BadSurjectiveReflection':(header+'example : existsTrueObservation.Sat oneObservedState Fin.elim0 := target_has_true_witness\n',False)}
    for n,(s,_) in controls.items():(ROOT/'controls'/f'{n}.lean').write_text(s)
    accepted=sorted(list((ROOT/'formalization').glob('*.lean'))+list((ROOT/'controls').glob('*.lean'))+
        [Path(__file__).resolve(),ROOT/'tools/module_order.json',ROOT/'evidence/ENVIRONMENT_VERIFIED.json',ROOT/'source_records/PREDECESSOR.json'])
    before={p:sha(p) for p in accepted};tasks=[];started=now();t0=time.monotonic()
    logdir=ROOT/'evidence/lean';logdir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='komorebi-model-v02-cold-') as tmp:
        env=os.environ.copy();env['LEAN_PATH']=':'.join([tmp]+[str(p) for p in (runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')]);env['OMP_NUM_THREADS']='1'
        def run(name,argv,expected=True):
            t=time.monotonic()
            try:
                p=subprocess.run(argv,cwd=ROOT/'formalization',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
                text=p.stdout;rc=p.returncode;timed_out=False
            except subprocess.TimeoutExpired as exc:
                text=exc.stdout or '';text=text.decode() if isinstance(text,bytes) else text;rc=None;timed_out=True
            log=logdir/(name+'.log');log.write_text(text)
            passed=not timed_out and ((rc==0)==expected)
            if not expected and ('unknown module prefix' in text or 'object file' in text and 'does not exist' in text):passed=False
            record={'name':name,'argv':argv,'exit_code':rc,'expected_success':expected,'timed_out':timed_out,'seconds':time.monotonic()-t,'passed':passed,'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
            tasks.append(record)
            if not passed:
                dump(ROOT/'results/FAILED_LEAN_RUN.json',{'tasks':tasks,'status':'FAIL'});raise RuntimeError(json.dumps(record)+'\n'+text)
            return text
        for m in MODULES:
            run(m,[str(lean),'-j1','-DwarningAsError=true','-o',str(Path(tmp)/(m+'.olean')),m+'.lean'])
        ax=run('AxiomAudit',[str(lean),'-j1','-DwarningAsError=true','AxiomAudit.lean'])
        found=set()
        for block in re.findall(r'depends on axioms:\s*\[([^]]*)\]',ax,re.S):found.update(x.strip() for x in block.replace('\n',' ').split(',') if x.strip())
        if found-ALLOWED:raise AssertionError('Unexpected axioms: '+str(found-ALLOWED))
        if any(d['name'] not in ax for d in decls):raise AssertionError('Missing axiom-audited declaration')
        for name,(_,expected) in controls.items():run(name,[str(lean),'-j1','-DwarningAsError=true',str(ROOT/'controls'/f'{name}.lean')],expected)
    inputs=[{'path':str(p.relative_to(ROOT)),'sha256':before[p],'sha256_after':sha(p)} for p in accepted]
    if any(x['sha256']!=x['sha256_after'] for x in inputs):raise AssertionError('Inputs changed during audit')
    rec={'status':'PASS','started_at':started,'finished_at':now(),'runtime_seconds':time.monotonic()-t0,'lean_version':version,'mathlib_revision':revision,'modules':len(MODULES),'new_modules':5,'named_declarations':len(decls),'new_theorems':sum(d['new'] and d['kind']=='theorem' for d in decls),'all_theorems':sum(d['kind']=='theorem' for d in decls),'axioms':sorted(found),'tasks':tasks,'scope':'All eleven local library modules cold rebuilt; pinned upstream compiled dependency cache reused.'}
    lr=ROOT/'results/LEAN_AUDIT.json';dump(lr,rec)
    outs=[{'path':str(lr.relative_to(ROOT)),'sha256':sha(lr),'kind':'result'}]+[{'path':t['log'],'sha256':t['sha256'],'kind':'log'} for t in tasks]
    cmd=[sys.executable,'tools/audit_all.py','--runtime',str(runtime)]
    dump(ROOT/'LEAN_MANIFEST.json',make_manifest('KMT-M2-STANDARD-SYNTAX',cmd,inputs,outs,rec,
      'Kernel-check the structural compiler into Mathlib FirstOrder syntax, guarded satisfaction, exact fragment transport, standard quantifier-free definability and explicit stronger-language counterexamples.',{'local_library_modules':len(MODULES),'expected_outcome_tasks':len(tasks),'formula_scope':'arbitrary finite source formulas; arbitrary state/observation types'}))
    pyinputs=[ROOT/'observational_logic.py',ROOT/'standard_logic.py',ROOT/'tests/audit.py',Path(__file__).resolve()]
    bef={p:sha(p) for p in pyinputs};started=now();t=time.monotonic()
    p=subprocess.run([sys.executable,'tests/audit.py'],cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=60)
    plog=ROOT/'evidence/python_final.log';plog.write_text(p.stdout)
    if p.returncode:raise RuntimeError(p.stdout)
    pr=json.loads((ROOT/'results/TRANSLATION_AUDIT.json').read_text())
    pyrec={'status':'PASS','started_at':started,'finished_at':now(),'runtime_seconds':time.monotonic()-t}
    pin=[{'path':str(p.relative_to(ROOT)),'sha256':bef[p],'sha256_after':sha(p)} for p in pyinputs]
    if any(x['sha256']!=x['sha256_after'] for x in pin):raise AssertionError('Python inputs changed')
    pout=[{'path':'results/TRANSLATION_AUDIT.json','sha256':sha(ROOT/'results/TRANSLATION_AUDIT.json'),'kind':'result'},{'path':'evidence/python_final.log','sha256':sha(plog),'kind':'log'}]
    dump(ROOT/'COMPUTATION_MANIFEST.json',make_manifest('KMT-M2-FINITE-REFERENCE',[sys.executable,'tests/audit.py'],pin,pout,pyrec,
        'Compare custom observational semantics with an independent primitive FO interpreter using tagged universes and appended bound-variable levels; verify finite codes and mutation controls.',pr['bounds']|{'systems':100,'exhaustive_two_state_systems':64},True))
    print(json.dumps({'status':'PASS','lean_modules':len(MODULES),'tasks':len(tasks),'named_declarations':len(decls),'new_theorems':rec['new_theorems'],'axioms':sorted(found),'python_checks':pr['total_checks'],'lean_seconds':rec['runtime_seconds'],'python_seconds':pyrec['runtime_seconds']},indent=2))
if __name__=='__main__':main()
