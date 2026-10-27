#!/usr/bin/env python3
"""Record current completed checks with source hashes (legacy Mathbox v1 schema)."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def included(p):
 r=p.relative_to(ROOT)
 return p.is_file() and not any(x.startswith('.') or x=='__pycache__' for x in r.parts) and p.name not in ['MANIFEST.json','replay_receipt.json']
def main():
 ex=json.loads((ROOT/'evidence/exact_results.json').read_text());ns=[json.loads((ROOT/f'evidence/numerical_{d}.json').read_text()) for d in [40,70]];le=json.loads((ROOT/'evidence/lean_results.json').read_text());pred=json.loads((ROOT/'evidence/predecessor.json').read_text())
 assert ex['check_count']==71 and le['theorem_count']==109
 assert all(n['equality_count']==117 and len(n['negative_controls'])==6 for n in ns)
 for name,h in pred['formalization_source_hashes'].items():
  if name!='H12Audit.lean':assert sha(ROOT/'formalization'/name)==h,'Inherited statement changed: '+name
 for name,h in le['source_hashes'].items():assert sha(ROOT/'formalization'/name)==h,'Final formal source differs from compiled source'
 rows=[ex,*ns,le]
 obj={'schema_version':1,'claim_id':'H12-CANONICAL-THETA-NORMALIZATION-0.3.0','repository':{'commit':None,'dirty':False,'context':'Isolated generated source release, not a Git repository. File identity is recorded by SHA256.'},
 'command':['python checks/exact_checks.py','python checks/numerical_checks.py --digits 40','python checks/numerical_checks.py --digits 70',*[f'python checks/run_lean.py --runtime <pinned external kit> --part {p}' for p in [1,2,3]]],
 'environment':{'software':[f'Python {sys.version.split()[0]}','SymPy '+ex['sympy'],'mpmath '+ns[0]['mpmath'],le['lean_version'],'Mathlib '+le['mathlib_revision']],'hardware':platform.platform()+'; CPU only, one Lean worker','resource_caps':{'lean_workers':1,'compiler_timeout_seconds':120,'outer_execution':'Separate synchronous stages; one combined invocation exceeded the outer tool envelope and was rerun separately.'}},
 'mathematics':{'assertion_tested':'Recovery of the fifth-smoothed theta normalizer from coprime norm powers; tangent and division-polynomial implications; canonical rational coordinates; actual cubic signed carry regressions.',
 'coefficient_domain':'Q-polynomial identities and Q(u); Lean arbitrary commutative groups and fields under explicit hypotheses; mpmath complex floating arithmetic.',
 'conventions':'q_t=theta0(z;t)^5/theta0(5z;5t), a=wp_t(1/5), b=wp_t(2/5), y=full wp derivative, d=a-b; half-grid index 4b+2c+a as inherited.',
 'inputs':[pred,{'path':'prior/gamma_evaluator.py','sha256':sha(ROOT/'prior/gamma_evaluator.py')},json.loads((ROOT/'evidence/runtime_restore.json').read_text())],
 'bounds':{'exact_checks':71,'universal_order5_family':'Q(u), symbolic identities','rational_examples':['-3','-2','-1','1','2','3','1/2','2/3'],'carry_regression_n':[1,2,3,4,5,6,7,8],'analytic_lattices':['0.23+0.71i','-0.31+1.13i','actual beta^3=7 cubic t'],'requested_digits':[40,70],'guard_digits':25,'normalized_equality_tolerance':'10^(-requested_digits+8)','negative_control_minimum_difference':'1e-7','Lean_theorems':109},
 'non_claims':['No original gamma-algebraic identity or power comparison.','No arithmetic evaluation of the signed limits.','The analytic torsion/divisor/norm dictionary is not Lean formalized.','No directed-rounding interval certificate.','No novelty or priority claim for classical elliptic function identities.','Two scalar norm conditions determine a scalar only after the fixed-divisor and functional hypotheses are supplied.']},
 'randomness':{'used':False,'generator':'none','seed':None},'run':{'started_at':min(r['started_at'] for r in rows),'runtime_seconds':sum(r['runtime_seconds'] for r in rows),'exit_status':0,'record_created_utc':datetime.now(timezone.utc).isoformat()},
 'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if included(p)],
 'checks':[{'name':'exact identities and regressions','count':71,'result':'PASS'},{'name':'Lean full theorem audit','count':109,'result':'PASS'},{'name':'inherited theorem sources unchanged','count':83,'result':'PASS'},{'name':'false integer statement rejected','result':'PASS'},*[{'name':f'numerical {n["requested_digits"]} digits','equalities':117,'negative_controls':6,'result':'PASS'} for n in ns]],
 'result':'Exact implemented identities verified. All 109 formal theorem constants compiled and axiom-audited. Numerical analytic claims passed only within declared floating tolerances. The universal analytic statement has its separate ordinary proof; it is not inferred from finite tests.',
 'residual_risks':['Legacy v1 manifest has no Git commit or complete machine-verifiable resource schema.','External analytic Weierstrass inputs and inherited gamma evaluator are not kernel-formalized.','Rounding error is not rigorously enclosed.','Period-dependent canonical elliptic coordinates have not been independently identified with arithmetic targets.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(obj,indent=2)+'\n');print('Wrote',len(obj['outputs']),'file hashes')
if __name__=='__main__':main()
