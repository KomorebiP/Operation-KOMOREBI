"""Execute the v0.4 finite audit with exact input/output provenance."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    extra=['tools/run_python.py','checks/audit_minimality.py','checks/check_certificate.py','discover.py','chainring.py','tools/export_symbolic_lean.py','tools/export_minimum_lean.py','source_records/SYMBOLIC_EXPORTS_v03.json','history/Komorebi_Representation_Calculus_v0.3.zip']
    records=json.loads((ROOT/'source_records/SYMBOLIC_EXPORTS_v03.json').read_text())
    inputs=sorted(set(extra+[r[k] for r in records for k in ['source','certificate','generated']]))
    before={p:sha(ROOT/p) for p in inputs};start=datetime.now(timezone.utc).isoformat();t=time.monotonic()
    cmd=[sys.executable,'checks/audit_minimality.py']
    run=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=120)
    elapsed=time.monotonic()-t;log='evidence/PYTHON_FINAL.log';(ROOT/log).write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError((run.stdout+run.stderr)[-4000:])
    result=json.loads((ROOT/'results/PYTHON_AUDIT.json').read_text());assert result['status']=='PASS'
    after={p:sha(ROOT/p) for p in inputs};assert before==after
    outputs=['results/PYTHON_AUDIT.json','results/ONE_ROW_COUNTEREXAMPLES.json',log]
    boundaries=result['boundaries']
    manifest={'schema_version':2,'claim_id':'KRC-0.4-MINIMUM-IMPLEMENTATION-AUDIT',
      'repository':{'commit':'standalone archive, no git commit','dirty':True},'command':cmd,
      'environment':{'software':[{'name':'Python','version':sys.version}],'platform':platform.platform()},
      'mathematics':{'assertion_tested':'Exact rediscovery, unchanged symbolic data, nonzero factors, minimality source emission, exhaustive linear/nonlinear torsion boundary and rejected invalid inputs.',
       'coefficient_domain':'Z/p^r Z, integer arithmetic only','conventions':'All initial states, all-word certificate contracts, linear initial encoding for generator minimum.',
       'inputs':inputs,'bounds':result['ranges'],'non_claims':boundaries},
      'randomness':{'used':False,'seed':None,'generator':'none'},
      'run':{'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':elapsed,'exit_status':run.returncode,'status':'completed','wall_cap_seconds':120,
       'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'missing_results':[],'invalid_results':[]},
      'input_artifacts':[{'path':p,'sha256':before[p],'sha256_after':after[p]} for p in inputs],
      'execution_artifacts':inputs,'declared_results':outputs[:2],
      'outputs':[{'path':p,'sha256':sha(ROOT/p),'kind':'log' if p==log else 'result'} for p in outputs],
      'checks':[{'name':k,'status':'PASS'} for k in result['counts']],
      'result':'PASS in the declared finite scopes','residual_risks':boundaries}
    (ROOT/'COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'PASS','seconds':elapsed,'instances':result['instances'],'inputs_unchanged':True}))
if __name__=='__main__':main()
