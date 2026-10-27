"""Execute discovery audit and bind all retained certificates to unchanged inputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=['discover.py','chainring.py','checks/check_certificate.py','checks/audit_discovery.py','tools/run_python.py']
before={n:sha(ROOT/n) for n in inputs}
argv=[sys.executable,'checks/audit_discovery.py'];started=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=35)
(ROOT/'evidence/PYTHON_RUN.log').write_text(p.stdout+p.stderr)
if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
result=json.loads((ROOT/'results/DISCOVERY_AUDIT.json').read_text());after={n:sha(ROOT/n) for n in inputs}
if before!=after:raise RuntimeError('inputs changed during audit')
certs=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'certificates').glob('*.json'))]
outputs=['results/DISCOVERY_AUDIT.json','evidence/PYTHON_RUN.log']+certs
manifest={'schema_version':2,'claim_id':'KRC-0.2-OBSERVATION-DISCOVERY',
 'repository':{'commit':'unavailable: standalone branch','dirty':True},'command':argv,
 'environment':{'software':[{'name':'Python','version':sys.version}], 'platform':platform.platform()},
 'mathematics':{'assertion_tested':'Exact observation-module discovery, witnessed strict refinements and independently checked all-state/all-word matrix certificates over finite chain rings.',
 'coefficient_domain':'Z/p^r Z for p=2,3,5, with exact integers and modular arithmetic.',
 'conventions':'Column-state actions; row observations; words left-to-right; every source state admissible. No state enumeration by the discovery algorithm.',
 'inputs':inputs,
 'bounds':{'cases':202,'random':'180 p/r/d configurations, d<=6,r<=5','hidden':'18 d=4,6 configurations plus one d=8,r=16 dyadic system',
           'word_tests':'12 random source state/word samples per case, lengths 0..12','exhaustive':'62 cases with at most 256 source states each',
           'long_horizon':'8-coordinate shift, 7-digit witness','mutations':11},
 'non_claims':['No learned search policy or independent held-out benchmark.','No universal theorem discovery or new all-precision partition classification.',
 'The new matrix-certificate proof reduction is written; Python checker and Smith code are not Lean-verified executables.']},
 'randomness':{'used':True,'seed':2026092002,'generator':'random.Random'},
 'run':{'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':time.monotonic()-tick,'exit_status':0,'status':'completed',
 'wall_cap_seconds':35,'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'missing_results':[],'invalid_results':[]},
 'input_artifacts':[{'path':n,'sha256':before[n],'sha256_after':after[n]} for n in inputs],
 'execution_artifacts':inputs,'declared_results':['results/DISCOVERY_AUDIT.json']+certs,
 'outputs':[{'path':n,'sha256':sha(ROOT/n),'kind':'log' if n.endswith('.log') else 'result'} for n in outputs],
 'checks':[{'name':k,'count':v,'status':'PASS'} for k,v in result['check_counts'].items()],
 'result':'exact implementation and certificate assertions verified for the recorded specifications',
 'residual_risks':['Synthetic test design and self-authored proofs may share errors; no performance comparison.','Source matrices are the input semantics, not automatically an encoding of every intended mathematical problem.']}
(ROOT/'COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(p.stdout)
