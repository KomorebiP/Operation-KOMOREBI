"""Bounded execution and hash provenance for the small exact worked examples."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import resource
import shutil
import subprocess
import sys
import time
import sympy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evidence/computation'
OUT.mkdir(parents=True,exist_ok=True)
inputs=['computations/exact_examples.py','computations/run_examples.py']
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p:digest(ROOT/p) for p in inputs}
available=os.sched_getaffinity(0) if hasattr(os,'sched_getaffinity') else None
def caps():
    resource.setrlimit(resource.RLIMIT_AS,(1073741824,1073741824))
    resource.setrlimit(resource.RLIMIT_CPU,(20,20))
    if available:os.sched_setaffinity(0,{min(available)})
env=dict(os.environ)
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
    env[key]='1'
command=[sys.executable,'computations/exact_examples.py','--output','evidence/computation/results.json']
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
t=time.perf_counter()
proc=subprocess.run(command,cwd=ROOT,env=env,preexec_fn=caps,capture_output=True,timeout=30)
elapsed=time.perf_counter()-t
(OUT/'stdout.txt').write_bytes(proc.stdout)
(OUT/'stderr.txt').write_bytes(proc.stderr)
after={p:digest(ROOT/p) for p in inputs}
result_path=OUT/'results.json'
assert proc.returncode==0,(proc.returncode,proc.stderr.decode())
assert before==after
result=json.loads(result_path.read_text())
shutil.copyfile(result_path,ROOT/'computations/exact_examples.json')
manifest={
 'schema_version':2,'claim_id':'IG09_EXACT_WORKED_EXAMPLES',
 'repository':{'commit':'unavailable (new publication workspace)','dirty':True},
 'command':command,
 'environment':{'software':[{'name':'Python','version':platform.python_version()},
                            {'name':'SymPy','version':sympy.__version__}],
                'hardware':platform.platform()},
 'mathematics':{'assertion_tested':'Exact scalar polynomial certificates, all36 ordered pairs of six S3 subgroup averages, one faithful S4 representation boundary and two finite embedding toys.',
                'coefficient_domain':'Q; exact finite fields F2 andF7; finite permutations.',
                'conventions':'Permutation p after q; left regular lambda(g)e_x=e_(gx); lexicographic permutation basis; arithmetic is exact SymPy Rational.',
                'inputs':inputs,'bounds':result['scope'],'non_claims':result['non_claims']},
 'randomness':{'used':False,'generator':'','seed':None},
 'run':{'started_at':started,'runtime_seconds':elapsed,'exit_status':proc.returncode,'status':'completed',
        'timeout_seconds':30.0,'max_output_bytes':None,
        'resource_limits':{'memory_bytes':1073741824,'cpu_seconds':20,'max_cores':1 if available else None,'max_threads':1},
        'missing_results':[],'invalid_results':[]},
 'execution_artifacts':inputs,
 'input_artifacts':[{'path':p,'sha256':before[p],'sha256_after':after[p]} for p in inputs],
 'output_directory':'evidence/computation',
 'declared_results':['evidence/computation/results.json'],
 'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p),'kind':kind} for p,kind in
            [(OUT/'stdout.txt','log'),(OUT/'stderr.txt','log'),(result_path,'result')]],
 'checks':[{'check':'input hashes unchanged','passed':before==after},
           {'check':'bounded process exited successfully','passed':proc.returncode==0},
           {'check':'figure data copy is byte-identical to declared result','passed':digest(result_path)==digest(ROOT/'computations/exact_examples.json')}],
 'result':'Implementation assertions passed in the declared finite scope. Mathematical interpretation is separately audited.',
 'residual_risks':['Exact factorization and rank routines use the recorded SymPy version.',
                   'The universal theorems require written proofs and verified source contracts.',
                   'Thread environment limits are cooperative; CPU affinity and POSIX memory/CPU limits are enforced for this child process.']}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':'passed','scope':result['scope'],'runtime_seconds':elapsed,'manifest':'evidence/computation/manifest.json'}))
