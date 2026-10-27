#!/usr/bin/env python3
"""Run the exact finite matrix audit and emit a version-1 computation manifest."""
from __future__ import annotations
import argparse,datetime,hashlib,json,platform,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output-dir',default='audit/computation')
 args=ap.parse_args();out=(ROOT/args.output_dir).resolve()
 if not out.is_relative_to(ROOT):ap.error('Output must stay inside project')
 out.mkdir(parents=True,exist_ok=True)
 code=ROOT/'checks/computation/moving_spaces_exact.py'
 before={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'KomorebiSpace').glob('*.lean'))}
 before[str(code.relative_to(ROOT))]=sha(code)
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
 argv=[sys.executable,str(code),'--output',str(out/'RESULT.json')]
 with (out/'run.log').open('w') as log:
  run=subprocess.run(argv,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=60)
 seconds=time.monotonic()-t
 if run.returncode:
  print((out/'run.log').read_text());return run.returncode
 report=json.loads((out/'RESULT.json').read_text())
 manifest={'schema_version':1,'claim_id':'moving-exact-spaces-v032-finite-audit',
  'repository':{'commit':None,'dirty':True},
  'command':'python3 checks/computation/moving_spaces_exact.py --output '+str((out/'RESULT.json').relative_to(ROOT)),
  'environment':{'software':['Python '+platform.python_version(),'fractions.Fraction (standard library)'],
    'hardware':platform.platform()},
  'mathematics':{'assertion_tested':'Exact finite matrix versions of two-sided projection motion, split perturbation, kernel transport, and noise estimates.',
   'coefficient_domain':'Rational numbers with Fraction; exact Gaussian elimination and PSD checks.',
   'conventions':'Euclidean source and matrix norms; certified rational Frobenius upper bounds. No random input.',
   'inputs':[{'path':str(code.relative_to(ROOT)),'sha256':sha(code),'content':'The full deterministic fixture family is defined in this script.'}],
   'bounds':{'source_dimensions':[2,3,4],'split_systems':36,'candidate_vectors':324,'moving_line_slopes':17,'rank_loss_witnesses':32,'time_cap_seconds':60},
   'non_claims':report['nonclaims']},
  'randomness':{'used':False,'generator':'none','seed':None},
  'run':{'started_at':start,'runtime_seconds':seconds,'exit_status':run.returncode},
  'outputs':[{'path':str((out/name).relative_to(ROOT)),'sha256':sha(out/name)} for name in ['RESULT.json','run.log']],
  'input_source_sha256':before,
  'checks':['Independent nullspace/Gram construction versus split-section formulas.',
   'Exact coefficient and PSD checks instead of sampled numerical eigenvalues.',
   'Four false stronger claims rejected by explicit finite witnesses.'],
  'result':'PASS: '+str(report['assertions'])+' assertions for the declared finite input family.',
  'residual_risks':['Python implementation not formally verified; all universal claims are separate Lean proofs.',
   'Version-1 manifests record execution metadata and hashes, not independent execution attestation.']}
 (out/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 cmd=[sys.executable,str(ROOT/'scripts/validate_manifest.py'),str(out/'MANIFEST.json'),'--root',str(ROOT)]
 r=subprocess.run(cmd,cwd=ROOT)
 print(report['status'],report['counts'],report['assertions']);return r.returncode
if __name__=='__main__':raise SystemExit(main())
