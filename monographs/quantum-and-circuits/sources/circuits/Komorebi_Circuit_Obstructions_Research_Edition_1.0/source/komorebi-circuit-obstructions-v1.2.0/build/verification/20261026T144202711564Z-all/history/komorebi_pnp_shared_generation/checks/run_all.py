#!/usr/bin/env python3
"""Pinned finite replay. Successful execution is not a universal proof."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,platform,shlex,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
OUT=R/'results';LOG=R/'logs';OUT.mkdir(exist_ok=True);LOG.mkdir(exist_ok=True)
P=R/'predecessor/komorebi_pnp_cut_comparison'
pinned=[*sorted(R.glob('*.md')),*sorted((R/'checks').glob('*.py')),*sorted((R/'checks').glob('*.cpp')),R/'historical/failed_candidates.md',R/'predecessor/Komorebi_PNP_Cut_Comparison_Block_2026-09-21.zip']
seal=json.loads((P/'ARTIFACT_SEAL.json').read_text())
pinned += [P/'ARTIFACT_SEAL.json',*[P/name for name in seal['files']]]
pinned=sorted(set(pinned));before={str(p.relative_to(R)):sha(p) for p in pinned}
assert sha(R/'predecessor/Komorebi_PNP_Cut_Comparison_Block_2026-09-21.zip')=='2c72f7a75efc2277fed11aafbec5d77afbd376b81a98c0f3042e11d3c13ab0bd'
for name,h in seal['files'].items():assert sha(P/name)==h,(name,'predecessor seal mismatch')
cxx=shlex.split(os.environ.get('CXX','g++'));cxxver=subprocess.run(cxx+['--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
started=now();timer=time.perf_counter();records=[];status='completed';exit_code=0;failure=None
result_names=['results/predecessor_replay_record.json','results/completeness.json','results/projection.json','results/fingerprint.json',*[f'results/profiles{n}.bin' for n in range(1,5)]]
exe=R/'checks/degree_profiles'
commands=[('build_profiles',cxx+['-O2','-std=c++17',str(R/'checks/degree_profiles.cpp'),'-o',str(exe)],40),
          *[(f'profiles{n}',[str(exe),str(n),str(R/f'results/profiles{n}.bin')],40) for n in range(1,5)],
          ('predecessor_replay',[sys.executable,str(R/'checks/replay_predecessor.py')],210),
          ('completeness',[sys.executable,str(R/'checks/verify_completeness.py')],40),
          ('projection',[sys.executable,str(R/'checks/verify_projection.py')],40),
          ('fingerprint',[sys.executable,str(R/'checks/verify_fingerprint.py')],40)]
try:
 for name,argv,limit in commands:
  t=time.perf_counter();done=subprocess.run(argv,cwd=R,capture_output=True,text=True,timeout=limit)
  log=LOG/(name+'_final.log');log.write_text(done.stdout+done.stderr)
  record={'name':name,'argv':argv,'wall_time_limit_seconds':limit,'elapsed_seconds':time.perf_counter()-t,'exit_status':done.returncode,'log':str(log.relative_to(R)),'log_sha256':sha(log)}
  if name=='build_profiles':record['compiled_program_sha256']=sha(exe)
  records.append(record)
  if done.returncode:raise RuntimeError(name+' failed: '+done.stderr[-1500:])
 for name in result_names:
  if not (R/name).is_file():raise RuntimeError('missing scientific result '+name)
  if name.endswith('.json'):assert json.loads((R/name).read_text())['status']=='PASS',name
 for path,h in before.items():assert sha(R/path)==h,('changed execution input',path)
 for name,h in seal['files'].items():assert sha(P/name)==h,(name,'predecessor drift')
except subprocess.TimeoutExpired as e:
 status='timeout';exit_code=124;failure=repr(e)
except Exception as e:
 status='failed';exit_code=1;failure=repr(e)
outputs=[]
for name in result_names:
 if (R/name).is_file():outputs.append({'path':name,'sha256':sha(R/name),'kind':'result'})
for rec in records:outputs.append({'path':rec['log'],'sha256':rec['log_sha256'],'kind':'log'})
after={path:sha(R/path) for path in before}
manifest={
 'schema_version':2,'claim_id':'Komorebi-PNP-complete-packets-projection-2026-09-21',
 'repository':{'commit':'unavailable; archive-pinned continuation','dirty':True,'predecessor_sha256':'2c72f7a75efc2277fed11aafbec5d77afbd376b81a98c0f3042e11d3c13ab0bd'},
 'command':[sys.executable,'checks/run_all.py'],
 'environment':{'software':[{'name':'Python','version':sys.version},{'name':'C++ compiler','version':cxxver}],'hardware':platform.platform()+'; architecture='+platform.machine()+'; logical_cpus='+str(os.cpu_count())},
 'mathematics':{'assertion_tested':'Finite pointwise degree duality, complete restored-oracle bounds, grade-extraction construction/rank identities, weighted trace and algebra-map controls; immediate predecessor reproduction.',
  'coefficient_domain':'exact F2 Boolean truth tables, GF16 via t^4+t+1, integers',
  'conventions':'bit x is truth value at assignment x; only distinct-wire NCT gates; ANF degree; zero function has b=0; Toffoli count distinct from total gates',
  'inputs':['Pinned predecessor sources and result JSON','Generated full truth tables in stated small ranges','Explicit unbalanced-OR, affine-factor, and weighted-witness families'],
  'bounds':{'profile_functions':'every Boolean function on 1..4 inputs','independent_rank_controls_four_inputs':765,'complete_oracles':'all 276 functions on 1..3 inputs','unbalanced_OR_family':'full truth tables n=4..9; all affine masks only n<=8','projection':'m=2..10 rank/coefficients; full truth tables only m=2,3,4','weighted_trace':'all verifiers up to 3 witness bits; full GF16 root grids; extraction grid explicitly limited for 3 bits'},
  'non_claims':['Not a proof of P versus NP.','Not Lean verified or independently reviewed.','No exhaustive circuit search; optimal small counts rely on proved lower bounds and matching constructions.','No superpolynomial unrestricted gate lower bound.','No polynomial-time weighted trace evaluator.']},
 'randomness':{'used':True,'generator':'Python random.Random, fixed independent 4-input rank-control sample','seed':20260921},
 'run':{'started_at':started,'finished_at':now(),'runtime_seconds':time.perf_counter()-timer,'exit_status':exit_code,'status':status,'subprocesses':records,'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'limit_note':'Per-subprocess wall limits are recorded and enforced; no additional OS memory/CPU/thread caps imposed.'},
 'input_artifacts':[{'path':p,'sha256':h,'sha256_after':after[p]} for p,h in before.items()],
 'execution_artifacts':list(before), 'declared_results':result_names, 'outputs':outputs,
 'checks':['52-file predecessor seal and full isolated replay','All 276 small optimal constructed oracles','Exact full 4-bit subset-minimum profiles with independent stated controls','Projection coefficient, rank, and restored-circuit checks','Exact finite-field trace/root and primitive-idempotent map checks','Execution-input before/after hashes'],
 'result':'All finite assertions completed successfully; universal mathematical interpretation rests on the written proofs.' if status=='completed' else 'Execution incomplete: '+str(failure),
 'residual_risks':['Self-review only; no Lean or independent audit.','Primary-source check is bounded, not a novelty audit.','Compiler and Python runtime are trusted.','Written universal proofs are separate from bounded finite outputs.']}
if failure:manifest['run']['failure']=failure
(R/'COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
if exit_code:raise SystemExit(exit_code)
validated=subprocess.run([sys.executable,str(R/'checks/validate_manifest.py'),str(R/'COMPUTATION_MANIFEST.json'),'--root',str(R)],cwd=R,capture_output=True,text=True)
(LOG/'manifest_validation.log').write_text(validated.stdout+validated.stderr)
if validated.returncode:raise RuntimeError(validated.stderr)
print(json.dumps({'status':'PASS','runtime_seconds':manifest['run']['runtime_seconds'],'subprocesses':len(records),'pinned_inputs':len(before),'predecessor_sealed_files':len(seal['files']),'manifest_validation':validated.stdout.strip()},indent=2))
