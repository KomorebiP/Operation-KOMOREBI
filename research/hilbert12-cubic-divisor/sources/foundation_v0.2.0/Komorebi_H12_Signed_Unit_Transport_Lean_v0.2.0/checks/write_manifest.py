#!/usr/bin/env python3
"""Freeze a legacy v1 computation record for the current accepted local outputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included(p):
 r=p.relative_to(ROOT)
 if any(x.startswith('.') or x=='__pycache__' for x in r.parts):return False
 if r.parts[0]=='formalization' and p.suffix!='.lean':return False
 if p.name in ['MANIFEST.json','replay_receipt.json']:return False
 return p.is_file()
def main():
 exact=json.loads((ROOT/'evidence/exact_results.json').read_text())
 nums=[json.loads((ROOT/f'evidence/numerical_{d}.json').read_text()) for d in [40,70]]
 lean=json.loads((ROOT/'evidence/lean_results.json').read_text())
 if exact['check_count']!=124 or lean['theorem_count']!=83:raise AssertionError('Incomplete accepted outputs')
 if any(n['equality_count']!=44 or len(n['negative_controls'])!=3 for n in nums):raise AssertionError('Incomplete numerical outputs')
 pred=ROOT/'evidence/predecessor.json'
 if not pred.exists():raise AssertionError('Missing predecessor provenance')
 rows=[exact]+nums+[lean]
 obj={
  'schema_version':1,'claim_id':'H12-SIGNED-UNIT-TRANSPORT-0.2.0',
  'repository':{'commit':None,'dirty':False,'context':'Isolated generated source release, no Git repository. Source identity is authenticated by per-file SHA256.'},
  'command':[
   'python checks/exact_checks.py',
   'python checks/numerical_checks.py --digits 40',
   'python checks/numerical_checks.py --digits 70',
   'python checks/run_lean.py --runtime <pinned external kit> --part 1',
   'python checks/run_lean.py --runtime <pinned external kit> --part 2'],
  'environment':{'software':[f'Python {sys.version.split()[0]}','SymPy 1.14.0','mpmath 1.3.0',lean['lean_version'],'Mathlib '+lean['mathlib_revision']],
   'hardware':platform.platform()+'; CPU execution, one Lean worker; no GPU',
   'resource_caps':{'lean_worker_count':1,'compiler_timeout_seconds_per_module':120,'numerical_threads':'OMP/BLAS settings are cooperative; mpmath scalar CPU arithmetic','outer_execution':'Synchronous tool calls; split stages avoid the whole-project execution envelope'}},
  'mathematics':{
   'assertion_tested':'Exact eight-character transport, moment/gain identities, integral three-step affine carries, group reconstruction and gauge identities; actual analytic packet regressions at the fixed beta^3=7 embedding.',
   'coefficient_domain':'Z, Q, formal polynomial identities; Lean arbitrary commutative/additive groups and commutative rings as specified; complex floating-point theta/gamma regressions.',
   'conventions':'Bit vertex (b,c,a), index 4b+2c+a; T(b,c,a)=(a,b,c); negative first gamma period tau=-t; s upper half-plane; characters (-1)^(dot product).',
   'inputs':[json.loads(pred.read_text()),{'path':'prior/gamma_evaluator.py','sha256':sha(ROOT/'prior/gamma_evaluator.py')},json.loads((ROOT/'evidence/runtime_restore.json').read_text())],
   'bounds':{'exact_vertices':8,'character_pairings':64,'carry_regression_n':list(range(1,7)),'numerical_requested_digits':[40,70],'guard_digits':25,'small_argument_probe_exponents':[4,6,8,10,16],'asymptotic_tolerance':'1e-6','equality_tolerance':'10^(-requested_digits+8) normalized','Lean_scope':'83 statements, including arbitrary natural iterate in all_iterates_affine; no analytic theorem axiom.'},
   'non_claims':['No U_Gamma=U_alg or power comparison.','No arithmetic evaluation of the new rational elliptic product limits.','No formalized complex analytic theta/gamma theory.','No directed-rounding interval certificate.','The explicit phase gauge preserves only the stated finite snapshot constraints, not all gamma functional equations and normalized limits.','No general Hilbert-12 result and no literature-priority claim.']},
  'randomness':{'used':False,'generator':'none','seed':None},
  'run':{'started_at':min(x['started_at'] for x in rows),'runtime_seconds':sum(x['runtime_seconds'] for x in rows),'exit_status':0,'record_created_utc':datetime.now(timezone.utc).isoformat()},
  'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if included(p)],
  'checks':[{'name':'exact assertions','count':124,'result':'PASS'},{'name':'Lean theorem build and transitive axiom coverage','count':83,'result':'PASS'},{'name':'Lean false statement rejected','result':'PASS'},*({'name':f'numerical {n["requested_digits"]} digits','equality_count':44,'asymptotic_checks':1,'negative_controls':3,'result':'PASS'} for n in nums)],
  'result':'Exact implemented assertions verified; all 83 formal theorem constants compiled and axiom-audited. Numerical analytic identities verified only within the stated floating tolerances. Universal mathematical interpretations use the separate proofs and inherited inputs.',
  'residual_risks':['Legacy v1 manifest has no Git revision or mandatory machine-checkable resource/input schema.','Inherited gamma evaluator and analytic hypotheses are not Lean formalized.','Numerical rounding is not rigorously enclosed.','Rational elliptic expressions still involve analytic period data.','The main arithmetic phase comparison is open.']
 }
 (ROOT/'MANIFEST.json').write_text(json.dumps(obj,indent=2)+'\n')
 print('Wrote manifest with',len(obj['outputs']),'authenticated files.')
if __name__=='__main__':main()
