"""Run exact symbolic-export audits, retaining immutable input hashes and scope."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, platform, subprocess, sys, time
ROOT = Path(__file__).resolve().parents[1]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    exports=json.loads((ROOT/'evidence/SYMBOLIC_EXPORTS.json').read_text())
    inputs=['discover.py','chainring.py','checks/check_certificate.py','checks/audit_symbolic.py',
      'tools/run_python.py','tools/export_symbolic_lean.py','evidence/SYMBOLIC_EXPORTS.json']
    inputs+=sorted({entry[key] for entry in exports for key in ('source','certificate','generated')})
    before={n:sha(ROOT/n) for n in inputs}
    argv=[sys.executable,'checks/audit_symbolic.py']
    started=datetime.now(timezone.utc).isoformat();tick=time.monotonic()
    p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=35)
    (ROOT/'evidence/PYTHON_RUN.log').write_text(p.stdout+p.stderr)
    if p.returncode:
        print(p.stdout+p.stderr);raise SystemExit(p.returncode)
    result=json.loads((ROOT/'results/SYMBOLIC_AUDIT.json').read_text())
    after={n:sha(ROOT/n) for n in inputs}
    if before != after: raise RuntimeError('Accepted input changed during audit')
    output_names=['results/SYMBOLIC_AUDIT.json','evidence/PYTHON_RUN.log']
    boundary=['Finite samples audit executable behavior, not universal theorem quantifiers.',
      'Universal certificate soundness and generated instances are checked in the separate Lean audit.',
      'Python discovery, Smith construction, exporter and source JSON parsing are not verified programs.',
      'Independent literal-data extraction checks the emitted source against separately supplied expected JSON.',
      'The fixtures are inherited synthetic mechanisms, not trained AI or held-out scientific discoveries.']
    manifest={'schema_version':2,'claim_id':'KRC-0.3-SYMBOLIC-EXPORT-AUDIT',
      'repository':{'commit':'standalone research release, no git commit','dirty':True},'command':argv,
      'environment':{'software':[{'name':'Python','version':sys.version}],'platform':platform.platform()},
      'mathematics':{'assertion_tested':'202 frozen finite-ring certificates rediscovered identically, checked independently, deterministically exported and independently matched to the emitted literal matrices; witness and large-image-code audits.',
        'coefficient_domain':'Z/p^r Z, exact integer/modular arithmetic; concrete Lean uses Fin(p^r).',
        'conventions':'Column states; observations as rows; words left to right; all states admissible. No state enumeration in matrix discovery or export.',
        'inputs':inputs,'bounds':result['ranges'],'non_claims':boundary},
      'randomness':{'used':True,'seed':2026092003,'generator':'random.Random'},
      'run':{'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
        'runtime_seconds':time.monotonic()-tick,'exit_status':0,'status':'completed','wall_cap_seconds':35,
        'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'missing_results':[],'invalid_results':[]},
      'input_artifacts':[{'path':n,'sha256':before[n],'sha256_after':after[n]} for n in inputs],
      'execution_artifacts':inputs,'declared_results':['results/SYMBOLIC_AUDIT.json'],
      'outputs':[{'path':n,'sha256':sha(ROOT/n),'kind':'log' if n.endswith('.log') else 'result'} for n in output_names],
      'checks':[{'name':k,'count':v,'status':'PASS'} for k,v in result['counts'].items()],
      'result':'The exact declared finite executable assertions passed with unchanged inputs.',
      'residual_risks':boundary}
    (ROOT/'COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
