#!/usr/bin/env python3
"""Freeze the completed two-part run into the retained legacy evidence format."""
from pathlib import Path
import hashlib,json,platform,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 core=json.loads((ROOT/'evidence/run_core.json').read_text()); high=json.loads((ROOT/'evidence/run_high.json').read_text())
 lean=json.loads((ROOT/'evidence/lean_results.json').read_text())
 for run in [core,high]:
  if run['exit_status']!=0 or run['input_hashes_before']!=run['input_hashes_after']:raise AssertionError('Incomplete/changed run')
  for rel,h in run['input_hashes_after'].items():
   if sha(ROOT/rel)!=h:raise AssertionError('Changed verified source '+rel)
 out={'schema_version':1,'claim_id':'H12-norm-projector-and-Lean-core-v0.1.0',
 'repository':{'commit':None,'dirty':True,'description':'Standalone conversation package; not a Git checkout.'},
 'command':'python checks/run_all.py --runtime PINNED_KIT --part core; python checks/run_all.py --runtime PINNED_KIT --part high',
 'environment':{'software':['Python '+sys.version.split()[0],'SymPy 1.14.0','mpmath 1.3.0',lean['lean_version'],'Mathlib '+lean['mathlib_revision']],'hardware':platform.platform()},
 'mathematics':{'assertion_tested':'Uniform ordinary-proof norm classification plus 50 kernel-checked algebraic/combinatorial/conditional lemmas. Separate exact divisor checks and theta regressions.',
 'coefficient_domain':'Exact integer/rational finite divisors; generic Lean fields and finitely supported integer functions; floating complex arithmetic kept separate.',
 'conventions':'N_n f(w)=product over nz=w of f(z); q is fifth-smoothed theta; S=s has infinite order for divisor interpretation. Classes modulo full s-translation coboundaries and constants.',
 'inputs':[{'path':rel,'sha256':h} for rel,h in core['input_hashes_before'].items()],
 'bounds':{'lean':'All 50 theorem constants, no admitted proofs; dependencies limited to standard logical axioms; actual negative compiler control.',
 'exact':'Norm divisor pushforwards n=1,...,24 and all 100 residue-ten semigroup products, plus exact symbolic identities.',
 'numerical':'33 equalities and 4 negative controls at each of 50 and 90 digits, with 20 guard digits. Generic and actual cubic theta parameters.',
 'resources':'Sequential single-worker Lean; per-subprocess limits recorded in core/high receipts; 4 GiB environment memory maximum. Two synchronous invocations avoid the outer tool envelope.'},
 'non_claims':['No formal elliptic gamma theory or formal meromorphic-divisor dictionary in this package.','No proof of U_Gamma^3=U_alg^3, of phase algebraicity, or of the general Hilbert-12 problem.','Numerical checks are not interval certificates.','No novelty or independent-researcher review claim.']},
 'randomness':{'used':False,'generator':'none','seed':None},
 'run':{'started_at':core['started_at'],'runtime_seconds':core['runtime_seconds']+high['runtime_seconds'],'exit_status':0,'measurement':'Sum of the two recorded synchronous runner durations.'},
 'outputs':[],
 'checks':[{'name':'lean_core','result':'50 passed, all axioms audited, false statement rejected'},{'name':'exact','result':'63 passed'},{'name':'numerical','result':'33 equalities and 4 controls at both precisions'}],
 'result':'Exact formal core compiled and audited; analytical norm classification proved in prose with stated inherited theta input. Original comparison open.',
 'residual_risks':['Lean compiler/kernel and pinned Mathlib are trusted dependencies.','Analytic applications of formal algebra are ordinary proofs, not compiled analytic statements.','Legacy manifest validates structure and hashes, not mathematical truth.']}
 for p in sorted(ROOT.rglob('*')):
  if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts:
   out['outputs'].append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
 (ROOT/'evidence/manifest.json').write_text(json.dumps(out,indent=2)+'\n')
 print('Manifest written with',len(out['outputs']),'hashed outputs.')
if __name__=='__main__':main()
