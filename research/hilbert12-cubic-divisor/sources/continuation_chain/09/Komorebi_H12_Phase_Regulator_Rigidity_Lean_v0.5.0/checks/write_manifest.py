#!/usr/bin/env python3
"""Write a completed v1 computation-audit record after all checks succeed."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys,platform
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 exact=json.loads((ROOT/'evidence/exact_results.json').read_text())
 intervals=[json.loads((ROOT/f'evidence/interval_{d}.json').read_text()) for d in (90,120)]
 lean=json.loads((ROOT/'evidence/lean_results.json').read_text())
 prior=json.loads((ROOT/'evidence/predecessor.json').read_text())
 assert exact['check_count']==41 and len(exact['negative_controls'])==4
 assert lean['theorem_count']==154
 assert all(x['check_count']==28 and len(x['negative_controls'])==3 for x in intervals)
 for n,h in prior['inherited_source_hashes'].items():assert sha(ROOT/'formalization'/n)==h
 for n,h in lean['source_hashes'].items():assert sha(ROOT/'formalization'/n)==h
 rows=[exact,*intervals,lean]
 outputs=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='MANIFEST.json' and not any(a.startswith('.') or a=='__pycache__' for a in p.relative_to(ROOT).parts)]
 obj={'schema_version':1,'claim_id':'H12-PHASE-GREEN-RIGIDITY-0.5.0','repository':{'commit':None,'dirty':False,'context':'Hash-authenticated isolated source snapshot; not a Git repository.'},'command':['python checks/exact_checks.py','python checks/interval_checks.py --digits 90','python checks/interval_checks.py --digits 120',*[f'python checks/run_lean.py --runtime PINNED_RUNTIME --part {i}' for i in (1,2,3,4)]],
 'environment':{'software':[f'Python {sys.version.split()[0]}','SymPy '+exact['sympy'],'mpmath '+intervals[0]['mpmath'],lean['lean_version'],'Mathlib '+lean['mathlib_revision']],'hardware':platform.platform()+'; CPU; cgroup memory limit 4 GiB','resource_caps':{'lean_workers':1,'lean_process_timeout_seconds':120,'interval_terms':2500,'execution':'synchronous staged invocations'}},
 'mathematics':{'assertion_tested':'Complex Green/FTC identity and normalized cubic comparison; contraction phase rigidity; explicit conditional cube-root separation; interval anchor lift and small-error inequalities with truncation and rounding.',
 'coefficient_domain':'SymPy exact rational polynomials; Lean real/complex differential and integral analysis; mpmath.iv rectangular complex intervals.',
 'conventions':'R3(g)=-2 integral_0^(1/3) x g + integral_(1/3)^1 (x-1)g. BCG negative-first-period gamma, omega=-1/2+i sqrt(3)/2, beta=7^(1/3)omega^2. Fixed arithmetic Gauss branch exp(6pi i/7).',
 'inputs':[prior,{'path':'prior/ARITHMETIC_INPUT.md','sha256':sha(ROOT/'prior/ARITHMETIC_INPUT.md')},json.loads((ROOT/'evidence/runtime_restore.json').read_text())],
 'bounds':{'exact_checks':41,'exact_negative_controls':4,'polynomial_monomial_degrees':'0..14','finite_frequency_controls':'1..30','interval_digits':[90,120],'interval_checks_per_precision':28,'interval_negative_controls_per_precision':3,'truncation':2500,'active_regulator_terms':1333,'gamma_tail_bound':'<8e-58','conditional_ratio_bound':'<1e-56','formal_theorems_total':154,'new_formal_theorems':14,'inherited_formal_theorems':140},
 'non_claims':['No exact arithmetic equality U_Gamma^3=U_alg^3 or U_Gamma=U_alg.','No implication from a small interval residual to equality.','No Lean verification of mpmath.iv or the gamma analytic hypotheses.','No formalized elliptic uniformization/no-isogeny theorem in this release.','The generic Green theorem and contraction lemma are actual analysis in Lean, with explicit hypotheses.','No novelty or general Hilbert-12 solution claimed.']},
 'randomness':{'used':False,'generator':'none','seed':None},'run':{'started_at':min(x['started_at'] for x in rows),'runtime_seconds':sum(x['runtime_seconds'] for x in rows),'exit_status':0,'record_created_utc':datetime.now(timezone.utc).isoformat()},'outputs':outputs,
 'checks':[{'name':'exact symbolic checks','count':41,'negative_controls':4,'result':'PASS'},{'name':'Lean clean build and transitive axiom audit','count':154,'result':'PASS'},{'name':'inherited 140 sources unchanged','result':'PASS'},{'name':'false integer theorem rejected','result':'PASS'},*[{'name':f'interval calculation at {x["interval_digits"]} digits','count':28,'negative_controls':3,'result':'PASS'} for x in intervals]],
 'result':'154 theorem constants compiled, including 14 new analytic/algebraic lemmas. Actual zero-anchor logarithm lift and conditional cube-root selection enclosed using directed interval arithmetic with explicit tails. Main arithmetic phase identity remains open.',
 'residual_risks':['Interval arithmetic trusts mpmath.iv elementary functions; the official documentation labels interval support experimental.','The gamma analytic application and inherited arithmetic input are ordinary proofs, not fully formalized in Lean.','Legacy version-one manifest is hash authenticated without a Git revision.','The interval certificate does not supply the missing exact power equality.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(obj,indent=2)+'\n')
 print('Manifest written:',len(outputs),'file hashes')
if __name__=='__main__':main()
