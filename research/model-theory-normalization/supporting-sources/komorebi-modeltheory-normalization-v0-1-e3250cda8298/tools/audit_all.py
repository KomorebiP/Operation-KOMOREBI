#!/usr/bin/env python3
"""Cold-check this scoped Lean library and independently replay its finite audit."""
from __future__ import annotations
import argparse,hashlib,json,os,platform,re,shutil,subprocess,sys,tempfile,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MODULES=['RepresentationCore','FiniteCertificates','ObservationalNormalization',
         'ObservationalFirstOrder','LogicalBoundaries','FiniteObservationCode']
ALLOWED={'Classical.choice','Quot.sound','propext'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def now()->str:return datetime.now(timezone.utc).isoformat()
def inventory():
    out=[]
    for m in MODULES:
        text=(ROOT/'formalization'/f'{m}.lean').read_text()
        namespace='Komorebi.Representation' if m in MODULES[:2] else 'Komorebi.ModelTheory'
        for kind,name in re.findall(r'^(?:noncomputable\s+)?(theorem|def|abbrev|inductive|structure)\s+([\w.]+)',text,re.M):
            out.append({'module':m,'kind':kind,'name':namespace+'.'+name,'inherited':m in MODULES[:2]})
    return out

def manifest(claim,command,inputs,outputs,record,assertion,bounds,random=False):
    return {'schema_version':2,'claim_id':claim,
      'repository':{'commit':'standalone archive; predecessor pinned in source_records/PREDECESSOR.json','dirty':True},
      'command':command,'environment':{'software':[{'name':'Python','version':sys.version},
         {'name':'Lean','version':record.get('lean_version','not used')}],'platform':platform.platform()},
      'mathematics':{'assertion_tested':assertion,'coefficient_domain':'Arbitrary typed deterministic systems in Lean; integer-labelled finite systems in Python.',
         'conventions':'All source states; words left-to-right; named output values; no state equality in the observational FO fragment; binder variable zero is newest.',
         'inputs':[x['path'] for x in inputs],'bounds':bounds,
         'non_claims':['Not full first-order elementarity or quantifier elimination.','Not proof of Python executable correctness or general discovery optimality.']},
      'randomness':{'used':random,'seed':2026092101 if random else None,'generator':'Python random.Random' if random else 'none'},
      'run':{'started_at':record['started_at'],'finished_at':record['finished_at'],
         'runtime_seconds':record['runtime_seconds'],'exit_status':0 if record['status']=='PASS' else 1,
         'status':'completed' if record['status']=='PASS' else 'failed','wall_cap_seconds':45,
         'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':1},
         'missing_results':[],'invalid_results':[]},
      'input_artifacts':inputs,'execution_artifacts':[x['path'] for x in inputs],
      'declared_results':[x['path'] for x in outputs if x['kind']=='result'],
      'outputs':outputs,'checks':[{'name':'accepted inputs unchanged','status':'PASS' if all(x['sha256']==x['sha256_after'] for x in inputs) else 'FAIL'},
        {'name':'declared execution checks','status':record['status']}],
      'result':record['status'],'residual_risks':['Statement interpretation self-review, not independent refereeing.',
        'The predecessor archive is preserved but only two inherited modules are rebuilt here.',
        'Per-subprocess 45-second wall limit, not a 45-second cap on the full multi-command audit.']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--lean',default=os.environ.get('LEAN',shutil.which('lean')))
    args=parser.parse_args()
    if not args.lean:raise SystemExit('Supply --lean /path/to/lean or set LEAN. No verification was run.')
    lean=str(Path(args.lean).resolve()); decls=inventory()
    if len({x['name'] for x in decls})!=len(decls):raise AssertionError('Duplicate inventory names')
    (ROOT/'formalization/AxiomAudit.lean').write_text('import LogicalBoundaries\nimport FiniteObservationCode\n'+
       '\n'.join('#print axioms '+x['name'] for x in decls)+'\n')
    (ROOT/'controls').mkdir(exist_ok=True)
    controls={'Positive':('import LogicalBoundaries\nexample : 2+2=4 := by decide\n',True),
      'FalseStatement':('import LogicalBoundaries\nexample : False := by decide\n',False),
      'Placeholder':('import LogicalBoundaries\nexample : True := by sorry\n',False),
      'BadQuantifierTransport':('import LogicalBoundaries\nopen Komorebi.ModelTheory\nexample : existsTrueObservation.Sat oneObservedState (fun i => nomatch i) := by decide\n',False)}
    for k,(s,_) in controls.items():(ROOT/'controls'/f'{k}.lean').write_text(s)
    (ROOT/'evidence/DECLARATION_INVENTORY.json').write_text(json.dumps(decls,indent=2)+'\n')
    accepted=sorted(list((ROOT/'formalization').glob('*.lean'))+list((ROOT/'controls').glob('*.lean'))+
                     [Path(__file__).resolve()])
    before={p:sha(p) for p in accepted}; tasks=[];start=now();t0=time.monotonic()
    version=subprocess.check_output([lean,'--version'],text=True,timeout=15).strip()
    (ROOT/'evidence/lean').mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='komorebi-m1-cold-') as tmp:
        env=os.environ.copy();env['LEAN_PATH']=tmp;env['OMP_NUM_THREADS']='1';env['TERM']='dumb'
        def run(name,argv,expected=True):
            t=time.monotonic()
            try:
                p=subprocess.run(argv,cwd=ROOT/'formalization',env=env,text=True,stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,timeout=45)
                text=p.stdout;rc=p.returncode;timed_out=False
            except subprocess.TimeoutExpired as e:
                text=e.stdout or '';text=text.decode() if isinstance(text,bytes) else text
                rc=None;timed_out=True
            log=ROOT/'evidence/lean'/f'{name}.log';log.write_text(text)
            passed=not timed_out and ((rc==0)==expected)
            item={'name':name,'argv':argv,'exit_code':rc,'expected_success':expected,
                'timed_out':timed_out,'seconds':time.monotonic()-t,'passed':passed,
                'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
            tasks.append(item)
            if not passed:raise RuntimeError(json.dumps(item)+'\n'+text)
            return text
        for m in MODULES:
            run(m,[lean,'-j1','-DwarningAsError=true','-o',str(Path(tmp)/(m+'.olean')),m+'.lean'])
        axioms=run('AxiomAudit',[lean,'-j1','-DwarningAsError=true','AxiomAudit.lean'])
        found=set()
        for block in re.findall(r'depends on axioms:\s*\[([^]]*)\]',axioms,re.S):
            found.update(x.strip() for x in block.replace('\n',' ').split(',') if x.strip())
        if found-ALLOWED:raise AssertionError(f'Unexpected axioms: {found-ALLOWED}')
        for d in decls:
            if d['name'] not in axioms:raise AssertionError('Declaration missing from axiom audit: '+d['name'])
        for name,(_,expected) in controls.items():
            run(name,[lean,'-j1','-DwarningAsError=true',str(ROOT/'controls'/f'{name}.lean')],expected)
    inp=[{'path':str(p.relative_to(ROOT)),'sha256':before[p],'sha256_after':sha(p)} for p in accepted]
    if any(x['sha256']!=x['sha256_after'] for x in inp):raise AssertionError('Accepted inputs changed')
    lean_result={'status':'PASS','started_at':start,'finished_at':now(),'runtime_seconds':time.monotonic()-t0,
       'lean_version':version,'modules':len(MODULES),'new_modules':len(MODULES)-2,'tasks':tasks,
       'named_declarations':len(decls),'new_theorems':sum(x['kind']=='theorem' and not x['inherited'] for x in decls),
       'all_theorems':sum(x['kind']=='theorem' for x in decls),'axioms':sorted(found),
       'scope':'All six library modules rebuilt from source in an empty local build directory. Std runtime reused. No full v0.4 suite replay.'}
    lr=ROOT/'results/LEAN_AUDIT.json';lr.write_text(json.dumps(lean_result,indent=2)+'\n')
    outs=[{'path':str(lr.relative_to(ROOT)),'sha256':sha(lr),'kind':'result'}]+[
        {'path':t['log'],'sha256':t['sha256'],'kind':'log'} for t in tasks]
    lm=manifest('KMT-M1-LEAN-SCOPE',[sys.executable,'tools/audit_all.py','--lean',lean],inp,outs,lean_result,
      'Kernel-check syntax normalization, exact observational types, finite horizons, surjective equality-restricted FO transport, quotient semantics, finite-code definability, and boundary counterexamples.',
      {'library_modules':len(MODULES),'expected_outcome_tasks':len(tasks)})
    (ROOT/'LEAN_MANIFEST.json').write_text(json.dumps(lm,indent=2)+'\n')
    ps=[ROOT/'observational_logic.py',ROOT/'tests/audit.py',Path(__file__).resolve()];pb={p:sha(p) for p in ps}
    start=now();t0=time.monotonic();cmd=[sys.executable,'tests/audit.py']
    p=subprocess.run(cmd,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=45)
    log=ROOT/'evidence/python_final.log';log.write_text(p.stdout)
    if p.returncode:raise RuntimeError(p.stdout)
    pr=json.loads((ROOT/'results/AUDIT.json').read_text())
    if pr['status']!='PASS':raise AssertionError('Python audit did not pass')
    rec={'status':'PASS','started_at':start,'finished_at':now(),'runtime_seconds':time.monotonic()-t0}
    inputs=[{'path':str(p.relative_to(ROOT)),'sha256':pb[p],'sha256_after':sha(p)} for p in ps]
    out=[{'path':'results/AUDIT.json','sha256':sha(ROOT/'results/AUDIT.json'),'kind':'result'},
         {'path':'evidence/python_final.log','sha256':sha(log),'kind':'log'}]
    pm=manifest('KMT-M1-EXECUTABLE-AUDIT',cmd,inputs,out,rec,
      'Exact tests of path normalization and retraction, independent pair-search quotient comparison, quantified transport to actual quotients, finite-code local certificates and negative boundaries.',
      {'systems':100,'exhaustive_two_state_systems':64,'seeded_additional_systems':36,
       'source_states':list(range(1,7)),'source_formula_depth':5,'fo_formula_depth':4,'free_variables':[0,1,2]},True)
    (ROOT/'COMPUTATION_MANIFEST.json').write_text(json.dumps(pm,indent=2)+'\n')
    print(json.dumps({'lean_modules':len(MODULES),'lean_tasks':len(tasks),
      'new_theorems':lean_result['new_theorems'],'named_declarations':len(decls),
      'axioms':sorted(found),'python_check_calls':pr['total_checks'],'status':'PASS'},indent=2))

if __name__=='__main__':main()
