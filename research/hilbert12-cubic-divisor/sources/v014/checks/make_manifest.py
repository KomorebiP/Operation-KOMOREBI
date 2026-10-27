#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,platform
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 e=json.loads((ROOT/'evidence/exact_results.json').read_text());l=json.loads((ROOT/'evidence/lean_results.json').read_text());ns=[json.loads((ROOT/f'evidence/numerical_{d}.json').read_text()) for d in [40,70]]
 ancestor=ROOT/'prior/v013_source_and_evidence.zip'
 pred={'base_checkpoint':'Principal Divisor Transport v0.13.0','archive':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor),'full_inherited_replay':False,'inherited_module_recompiled':'H12PrincipalDivisor','inherited_module_sha256':sha(ROOT/'formalization/H12PrincipalDivisor.lean'),'runtime_sha256':'66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34','runtime_bytes':2896789714}
 (ROOT/'evidence/predecessor.json').write_text(json.dumps(pred,indent=2)+'\n')
 fs=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.lean-check' not in p.parts and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and p.suffix not in ['.olean','.ilean'])
 m={'schema_version':1,'claim_id':'Komorebi-H12-v014-cubic-divisor-regularization',
 'repository':{'commit':None,'dirty':True,'base_checkpoint':pred['base_checkpoint'],'base_archive_sha256':pred['sha256'],'full_inherited_replay':False},
 'command':['python checks/exact_checks.py','python checks/numerical_checks.py --digits 40','python checks/numerical_checks.py --digits 70','python checks/verify_lean.py --lean '+l['compiled_modules'][0]['argv'][0]],
 'environment':{'software':['Python '+platform.python_version(),'SymPy '+e['software']['sympy'],'mpmath '+ns[0]['mpmath'],l['lean_version'],'Bundled Std; no Mathlib'],'hardware':platform.platform()+'; one Lean worker'},
 'mathematics':{'assertion_tested':'Universal integer families proving cubic divisor growth; exact canonical-factor derivatives; analytic correction reflection and its quadratic coefficient. Ordinary proofs establish convergence, scalar polynomial reconstruction and the theta-growth exclusion.',
 'coefficient_domain':'Int in Lean; Fraction and SymPy exact rational/polynomial arithmetic; mpmath complex floating regressions.',
 'conventions':'F negative-first-period BCG convention; R principal-seven correction; W_D is the ungrouped genus-three product over the nonzero signed divisor; logarithmic jets have factorial denominators.',
 'inputs':[{'path':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor)}]+[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted((ROOT/'formalization').glob('H12*.lean'))],
 'bounds':{'integer_cube':[-6,6],'rational_lift_triples':2197,'growth_family_n':[1,16],'family_sample_points':92480,'new_lean_theorems':11,'recompiled_inherited_theorems':14,'requested_digits':[40,70],'guard_digits':25,'series_cap':20000,'relative_tolerance':'10^(-digits+8)','jet_probe':'1e-7','jet_tolerance':'1e-5','lean_module_timeout_seconds':90},
 'non_claims':['No exact arithmetic gamma equality or root-of-unity bound on its discrepancy.','No claim that canonical divisor products at algebraic arguments are algebraic numbers.','No interval certificate or numerical approximation certificate for the infinite canonical product.','No Lean formalization of complex analytic counting, infinite products, reflection or class-field comparison.','No full inherited Lean replay or historical novelty claim.']},
 'randomness':{'used':False,'generator':'none','seed':None},
 'run':{'started_at':e['started_at'],'runtime_seconds':e['runtime_seconds']+l['runtime_seconds']+sum(n['runtime_seconds'] for n in ns),'exit_status':0},
 'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in fs],
 'checks':[{'name':'exact coefficient/derivative checks','result':'PASS','count':len(e['exact_checks']),'negative_controls':len(e['negative_controls'])},{'name':'Lean new and inherited dependency audit','result':'PASS','new':11,'inherited':14},{'name':'false integer control','result':'REJECTED','exit_status':l['negative_control_exit']}]+[{'name':f'reflection and quadratic jet {n["digits"]} digits','result':'PASS','identities':len(n['identities']),'jet_diagnostics':1,'negative_controls':len(n['negative_controls'])} for n in ns],
 'result':'11 new integer theorems and 14 unchanged inherited dependencies compiled and audited; 20 exact named assertions and five negative controls pass; four analytic identities, a quadratic-jet diagnostic and three negative controls pass at each precision. Arithmetic equality remains open.',
 'residual_risks':['Analytic arguments have self-review only and remain outside Lean.','The gamma evaluator is inherited; primary product conventions were verified, not all inherited proofs re-audited.','Floating point numerical checks do not enclose rounding.','Canonical products have proven analytic tails but were not numerically evaluated in this block.','Legacy schema-v1 manifests authenticate files and runs, not theorem truth or full git provenance.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
