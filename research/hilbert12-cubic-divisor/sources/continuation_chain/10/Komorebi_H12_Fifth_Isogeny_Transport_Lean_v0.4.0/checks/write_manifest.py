#!/usr/bin/env python3
"""Completed Mathbox v1 evidence record with checked file identities."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,platform
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ex=json.loads((ROOT/'evidence/exact_results.json').read_text());nums=[json.loads((ROOT/f'evidence/numerical_{d}.json').read_text()) for d in (40,70)];le=json.loads((ROOT/'evidence/lean_results.json').read_text());pr=json.loads((ROOT/'evidence/predecessor.json').read_text())
 assert ex['check_count']==60 and len(ex['negative_controls'])==6
 assert le['theorem_count']==140
 assert all(n['equality_count']==132 and len(n['negative_controls'])==7 for n in nums)
 for n,h in pr['inherited_formal_sources'].items():assert sha(ROOT/'formalization'/n)==h,('changed inherited formal source',n)
 for n,h in le['source_hashes'].items():assert sha(ROOT/'formalization'/n)==h,('compiled source changed',n)
 rows=[ex,*nums,le]
 obj={'schema_version':1,'claim_id':'H12-FIFTH-ISOGENY-TRANSPORT-0.4.0','repository':{'commit':None,'dirty':False,'context':'Isolated source release, not a Git repository; provenance is file hashes and exact external pins.'},
 'command':['python checks/exact_checks.py','python checks/numerical_checks.py --digits 40','python checks/numerical_checks.py --digits 70',*[f'python checks/run_lean.py --runtime <pinned external kit> --part {i}' for i in (1,2,3,4)]],
 'environment':{'software':[f'Python {sys.version.split()[0]}','SymPy '+ex['sympy'],'mpmath '+nums[0]['mpmath'],le['lean_version'],'Mathlib '+le['mathlib_revision']],'hardware':platform.platform()+'; CPU only; one Lean worker','resource_caps':{'Lean_workers':1,'Lean_subprocess_timeout_seconds':120,'differentiated_series_max_terms':20000,'tool_invocations':'separate synchronous bounded executions'}},
 'mathematics':{'assertion_tested':'Normalized fifth-isogeny rational map, marking changes, source/target moduli and differential transport identities; full inherited and new Lean algebra audit.',
 'coefficient_domain':'Q[u,x,y], rational function fields; Lean fields and explicit hypotheses; mpmath complex floating arithmetic.',
 'conventions':'Full Weierstrass derivative; Tate model Y^2+(1-u)XY-uY=X^3-uX^2; quotient Z=2Y+(1-u)X-u; analytic kernel P=1/5.',
 'inputs':[pr,json.loads((ROOT/'evidence/runtime_restore.json').read_text()),{'path':'prior/v03_numerical_checks.py','sha256':sha(ROOT/'prior/v03_numerical_checks.py')},{'path':'prior/gamma_evaluator.py','sha256':sha(ROOT/'prior/gamma_evaluator.py')}],
 'bounds':{'exact_assertions':60,'exact_negative_controls':6,'symbolic_family':'Q(u), generic X,Y, reduced modulo the source curve when stated','bounded_rational_parameters':['-3','-1','1/2','1','2','3'],'bounded_x_values':['7/3','-5/2'],'numerical_periods':['.23+.71i','-.31+1.13i','actual cubic t,s and coarse 5t,5s'],'requested_digits':[40,70],'guard_digits':25,'equality_tolerance':'10^(-requested_digits+8)','negative_control_minimum':'1e-7','Lean_theorems':140,'inherited_unchanged_theorems':109},
 'non_claims':['No gamma-arithmetic equality or power identity.','No arithmetic evaluation of the return limits.','The analytic uniformization/degree, derivative dictionary, eta identity and uniqueness theorem are not Lean-formalized.','No directed-rounding enclosure.','No literature novelty claim.','The rational moduli parameter is not asserted to be an algebraic number.']},
 'randomness':{'used':False,'generator':'none','seed':None},'run':{'started_at':min(r['started_at'] for r in rows),'runtime_seconds':sum(r['runtime_seconds'] for r in rows),'exit_status':0,'record_created_utc':datetime.now(timezone.utc).isoformat()},
 'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='MANIFEST.json' and not any(v.startswith('.') or v=='__pycache__' for v in p.relative_to(ROOT).parts)],
 'checks':[{'name':'exact polynomial/rational identities','count':60,'negative_controls':6,'result':'PASS'},{'name':'full Lean kernel and axiom audit','count':140,'result':'PASS'},{'name':'inherited 109 theorem sources unchanged','result':'PASS'},{'name':'false integer theorem rejected','result':'PASS'},*[{'name':f'numerical {n["requested_digits"]} digits','count':132,'negative_controls':7,'result':'PASS'} for n in nums]],
 'result':'Implemented exact identities verified; all 140 Lean theorem constants compiled and audited. Analytic comparisons passed finite floating tolerances. Universal analytic claims have separate ordinary proofs; the main arithmetic identification is open.',
 'residual_risks':['Legacy v1 record has no Git revision or mandatory comprehensive resource schema.','Analytic dependencies are not formalized.','Floating rounding error is not bounded by the recorded truncation estimates.','The comparison function with independently established arithmetic value has not been constructed.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(obj,indent=2)+'\n')
 print('manifest',len(obj['outputs']),'file hashes')
if __name__=='__main__':main()
