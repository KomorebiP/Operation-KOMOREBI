#!/usr/bin/env python3
"""Record and validate a fresh collection of current-source AVOC evidence.

This process validates existing per-target proof and test records. Its runtime is
not claimed to be the runtime of all underlying compilations or crash tests.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,platform,sqlite3,subprocess,sys,time
R=Path(__file__).resolve().parents[1]
RD=R/'results/v0.21.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--baseline',type=Path,required=True);args=a.parse_args()
    sources=[p for p in (R/'AVOC').glob('*.lean')]+[R/'tools/summarize_v021.py',R/'tools/run_retry_workflow.py',R/'tools/retry_store.py',R/'checks/test_costed_retry.py']
    before={str(p.relative_to(R)):sha(p) for p in sources}
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
    cmd=[sys.executable,'tools/summarize_v021.py','--baseline',str(args.baseline.resolve())]
    run=subprocess.run(cmd,cwd=R,capture_output=True,text=True,timeout=40)
    elapsed=time.monotonic()-t
    (RD/'collector_current.log').write_text(run.stdout+run.stderr)
    if run.returncode:raise SystemExit(run.returncode)
    after={str(p.relative_to(R)):sha(p) for p in sources}
    if before!=after:raise RuntimeError('input changed during collection')
    (RD/'collector_input_hashes.json').write_text(json.dumps({'before':before,'after':after},indent=2)+'\n')
    result=json.loads((R/'AUDIT.json').read_text())
    outputs=['AUDIT.json','results/v0.21.0/final_local_build_summary.json','results/v0.21.0/final_negative_summary.json',
      'results/v0.21.0/retry_test_summary.json','results/v0.21.0/source_scan.json','results/v0.21.0/inherited_source_match.json',
      'results/v0.21.0/collector_current.log','results/v0.21.0/collector_input_hashes.json',
      'results/v0.21.0/attempt_regression.json','results/v0.21.0/retry_demo_summary.json']
    m={'schema_version':1,'claim_id':'AVOC-v0.21-current-evidence-collection',
      'repository':{'commit':None,'dirty':True,'baseline_archive_sha256':sha(args.baseline),
                    'revision_note':'source release archive, not a Git checkout'},
      'command':cmd,'environment':{'software':[{'name':'Python','version':platform.python_version()},
           {'name':'SQLite','version':sqlite3.sqlite_version},{'name':'Lean','version':'4.34.0-rc2 / 6a10ac8c22beadecabdbb0919c2b50214762f91d'}],
           'hardware':platform.platform()+'; '+str(os.cpu_count())+' visible logical CPUs'},
      'mathematics':{'assertion_tested':'Current-source compilation, axiom, negative-test and protected-store crash evidence satisfy the declared release gates.',
           'coefficient_domain':'Lean propositions and exact rational finite control; exact ticket records; transactional SQLite test states.',
           'conventions':'Collector checks historical per-target records against current source/log/output hashes. This collector invocation is not a rerun of all Lean or crash cases.',
           'inputs':[str(p.relative_to(R)) for p in sources]+[str(args.baseline.resolve())],
           'bounds':{'local_targets':112,'theorem_reports':1070,'negative_files':47,'live_costed_retry_cases':12,'inherited_modules':100,'accounting_comparisons':7204,'collector_timeout_seconds':40},
           'non_claims':['No power-failure experiment or formal proof of SQLite/OS correctness.',
                         'Explicit paid retry is implemented; no automatic retry or outcome inference from a fault.',
                         'No real LLM calibration, runtime cost optimum or arbitrary external Lean-artifact backend.']},
      'randomness':{'used':False,'generator':'not used','seed':None},
      'run':{'started_at':start,'runtime_seconds':elapsed,'exit_status':run.returncode},
      'outputs':[{'path':p,'sha256':sha(R/p)} for p in outputs],
      'checks':[result,'Separate before/after source hashes match; individual original build/test logs remain available.'],
      'result':'PASS: current evidence and sources satisfy release gates.',
      'residual_risks':['Version 1 manifest does not itself require exhaustive execution-input closure or machine-checkable resource limits.',
                        'The checker runtime, pinned binary caches, Python, SQLite, filesystem and protected host remain trusted.',
                        'The local validator is a v1-only adaptation of the installed computation-audit validator; it does not implement v2.']}
    path=RD/'computation_manifest.json';path.write_text(json.dumps(m,indent=2)+'\n')
    check=[sys.executable,'tools/audit/validate_computation_manifest.py',str(path),'--root',str(R)]
    v=subprocess.run(check,cwd=R,capture_output=True,text=True,timeout=10)
    (RD/'computation_manifest_validation.log').write_text(v.stdout+v.stderr)
    print(run.stdout+v.stdout,end='')
    if v.returncode:print(v.stderr,file=sys.stderr);raise SystemExit(v.returncode)
if __name__=='__main__':main()
