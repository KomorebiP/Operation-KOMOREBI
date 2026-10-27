"""Run the declared exact audit and retain version-2 evidence with input hashes."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, platform, subprocess, sys, time
ROOT = Path(__file__).resolve().parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=['checks/audit_core.py','tools/run_audit.py']
declared=['results/AUDIT.json']
before={n:digest(ROOT/n) for n in inputs}
argv=[sys.executable,'checks/audit_core.py']
start=datetime.now(timezone.utc).isoformat(); tick=time.monotonic()
proc=subprocess.run(argv,cwd=ROOT,text=True,capture_output=True,timeout=35)
runtime=time.monotonic()-tick
(ROOT/'results/RUN.log').write_text(proc.stdout+proc.stderr)
after={n:digest(ROOT/n) for n in inputs}
if proc.returncode != 0: print(proc.stdout+proc.stderr); raise SystemExit(proc.returncode)
audit=json.loads((ROOT/declared[0]).read_text())
manifest={
 'schema_version':2,'claim_id':'KRC-0.1-FINITE-CORE-AUDIT',
 'repository':{'commit':'unavailable: new standalone conceptual branch','dirty':True},
 'command':argv,
 'environment':{'software':[{'name':'Python','version':sys.version}], 'platform':platform.platform()},
 'mathematics':{'assertion_tested':'Finite task-relative quotients, residual composition, quadratic lifting fibers and representative invariance, recovery of the retained Block15 relation, and the binary-two-color module precision profile.',
 'coefficient_domain':'Exact integer arithmetic, finite residue rings, finite fields; no floating mathematical arithmetic.',
 'conventions':'Column-state actions; all admissible toy states; radix digits as operation symbols. The lifting experiment uses scalar integer quadratics and exact one-step prime-power lifts.',
 'inputs':inputs,
 'bounds':{'finite_states':64,'transport_matrices':'400 trials of 2x2 matrices over moduli 4,8,9,25',
  'lifting':'p=2,3,5; r=1,2,3; all 125 quadratics with coefficients -2..2 and every lower residue root',
  'relations':'All 64 F2-linear functionals on six mixed-precision envelope coordinates',
  'precision_information':'r=1..1024'},
 'non_claims':['No new Lean verification.', 'No all-precision binary-three-color lattice classification.',
  'No novelty claim for observational minimization, matrix residual laws, or first-order polynomial lifting.',
  'No trained AI, comparative benchmark or autonomous theorem discovery result.']},
 'randomness':{'used':True,'seed':20260920,'generator':'random.Random; only matrix composition tests'},
 'run':{'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':runtime,
  'exit_status':proc.returncode,'status':'completed','wall_cap_seconds':35,
  'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},
  'missing_results':[],'invalid_results':[]},
 'input_artifacts':[{'path':n,'sha256':before[n],'sha256_after':after[n]} for n in inputs],
 'execution_artifacts':inputs,'declared_results':declared,
 'outputs':[{'path':n,'sha256':digest(ROOT/n),'kind':kind} for n,kind in [('results/AUDIT.json','result'),('results/RUN.log','log')]],
 'checks':[{'name':k,'count':v,'status':'PASS'} for k,v in audit['check_counts'].items()],
 'result':'implementation and finite assertions verified in the stated ranges',
 'residual_risks':['Written universal proofs have not been Lean-checked in this branch.',
 'The finite audit is self-authored; finite checks do not prove broader claims.',
 'The known Block15 relation is rediscovered; this is not a novel-claim discovery benchmark.']}
assert before==after
(ROOT/'COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(proc.stdout)
print('runtime_seconds',runtime)
