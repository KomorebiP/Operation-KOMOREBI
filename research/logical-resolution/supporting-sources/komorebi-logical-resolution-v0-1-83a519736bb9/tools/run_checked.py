"""Run the two audits and emit source-bound version-2 computation manifests."""
from __future__ import annotations
import argparse, hashlib, json, platform, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run_one(kind,argv,inputs,declared,software):
    before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    started=datetime.now(timezone.utc).isoformat(); tick=time.monotonic()
    p=subprocess.run(argv,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
    elapsed=time.monotonic()-tick
    log=ROOT/'evidence'/('final_'+kind+'.log');log.write_text(p.stdout)
    after={str(f.relative_to(ROOT)):sha(f) for f in inputs}
    if p.returncode: raise RuntimeError(f'{kind} audit failed: {p.stdout}')
    if before!=after: raise RuntimeError('Changed execution inputs')
    results=[ROOT/s for s in declared]
    if not all(s.is_file() for s in results):raise RuntimeError('Missing result')
    raw=json.loads(results[0].read_text())
    if raw['status']!='PASS':raise RuntimeError('Invalid result status')
    outputs=[{'path':str(s.relative_to(ROOT)),'sha256':sha(s),'kind':'result'} for s in results]
    logs=[log]
    if kind=='lean':logs+=sorted((ROOT/'evidence'/'lean_cold').glob('*.log'))
    outputs += [{'path':str(s.relative_to(ROOT)),'sha256':sha(s),'kind':'log'} for s in logs]
    nonclaims=raw.get('non_claims',[])
    if kind=='python':
        maths={'assertion_tested':'Finite reference semantics, quotient preservation, finite formula discovery, and named failure boundaries',
               'coefficient_domain':'Finite state/value sets; exact integer indexing and Boolean truth values',
               'conventions':'Finite typed observational formulas; value equality only; de Bruijn bound variable at index zero; words left to right',
               'inputs':list(before),'bounds':raw['bounds'],'non_claims':nonclaims}
        checkrecords=[{'name':k,'count':v,'passed':True} for k,v in raw['checks'].items()]
    else:
        maths={'assertion_tested':'Lean kernel accepts exact named first-order-fragment theorems and rejects expected false/placeholder controls',
               'coefficient_domain':'Arbitrary state/action/observation/value types; generic unary deterministic systems; finite and infinite counterexamples',
               'conventions':'Typed observation-value terms, no state equality, all value literals, state-only quantifiers, exact inherited operational semantics',
               'inputs':list(before),'bounds':{'modules':len(raw['modules']),'named_declarations':raw['named_declarations'],
                                            'new_theorems':raw['new_counts']['theorem']},'non_claims':nonclaims}
        checkrecords=[{'name':t['name'],'passed':t['passed'],'exit_status':t['exit_status']} for t in raw['tasks']]
    manifest={'schema_version':2,'claim_id':'KLR-v0.1-'+kind,
              'repository':{'commit':'unavailable (standalone; exact source hashes supplied)','dirty':False},
              'command':argv,'environment':{'software':software,'hardware':platform.platform()},
              'mathematics':maths,'randomness':{'used':kind=='python','generator':'Python random.Random' if kind=='python' else '',
                                               'seed':raw.get('seed')},
              'input_artifacts':[{'path':s,'sha256':h,'sha256_after':after[s]} for s,h in before.items()],
              'execution_artifacts':list(before),'declared_results':declared,
              'run':{'started_at':started,'runtime_seconds':elapsed,'exit_status':p.returncode,'status':'completed',
                     'missing_results':[],'invalid_results':[],
                     'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},
                     'wall_timeout_seconds':180,'inner_lean_task_wall_timeout_seconds':60 if kind=='lean' else None},
              'outputs':outputs,'checks':checkrecords,'result':'PASS',
              'residual_risks':['Authoring-assistant self-review, not an independent referee',
                                'Python implementation/export and prose are not kernel-verified',
                                'No full first-order-language embedding or historical novelty claim']}
    dest=ROOT/(kind.upper()+'_MANIFEST.json');dest.write_text(json.dumps(manifest,indent=2)+'\n')
    p=subprocess.run([sys.executable,str(ROOT/'tools'/'validate_manifest.py'),str(dest),'--root',str(ROOT)],
                     text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (ROOT/'evidence'/(kind+'_manifest_validation.log')).write_text(p.stdout)
    if p.returncode:raise RuntimeError(p.stdout)
    print(json.dumps({'audit':kind,'status':'PASS','runtime':elapsed,'manifest':dest.name}),flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);a=ap.parse_args()
    lean=Path(a.lean).resolve(); version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    run_one('lean',[sys.executable,str(ROOT/'tools'/'verify_lean.py'),'--lean',str(lean)],
            sorted((ROOT/'formalization').glob('*.lean'))+sorted((ROOT/'tests').glob('*.lean'))+
              [ROOT/'tools'/'verify_lean.py',Path(__file__).resolve()],
            ['results/LEAN_AUDIT.json','results/DECLARATIONS.json'],
            [{'name':'Lean','version':version},{'name':'Python','version':platform.python_version()}])
    run_one('python',[sys.executable,str(ROOT/'tools'/'audit_python.py')],
            [ROOT/'observation_logic.py',ROOT/'tools'/'audit_python.py',Path(__file__).resolve()],
            ['results/PYTHON_AUDIT.json'],[{'name':'Python','version':platform.python_version()}])
if __name__=='__main__':main()
