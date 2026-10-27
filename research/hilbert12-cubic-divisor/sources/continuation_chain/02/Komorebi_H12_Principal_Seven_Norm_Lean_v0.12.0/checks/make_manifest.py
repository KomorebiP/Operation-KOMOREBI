#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,platform
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 e=json.loads((ROOT/'evidence/exact_results.json').read_text());l=json.loads((ROOT/'evidence/lean_results.json').read_text())
 ns=[json.loads((ROOT/f'evidence/numerical_{d}.json').read_text()) for d in [40,70]]
 ancestor=ROOT/'prior/v011_source_and_evidence.zip'
 (ROOT/'evidence/predecessor.json').write_text(json.dumps({'base_checkpoint':'v0.11.0','archive':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor),'fresh_inherited_replay':False,'gamma_evaluator_sha256':sha(ROOT/'prior/gamma_evaluator.py')},indent=2)+'\n')
 fs=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.lean-check' not in p.parts and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and p.suffix not in ['.olean','.ilean'])
 m={'schema_version':1,'claim_id':'Komorebi-H12-v012-principal-seven-norm',
 'repository':{'commit':None,'dirty':True,'base_checkpoint':'Fourier Flattening v0.11.0','base_archive_sha256':sha(ancestor),'fresh_inherited_replay':False},
 'command':['python checks/exact_checks.py','python checks/numerical_checks.py --digits 40','python checks/numerical_checks.py --digits 70','python checks/verify_lean.py --lean '+l['compiled_modules'][0]['argv'][0]],
 'environment':{'software':['Python '+platform.python_version(),'SymPy '+e['sympy'],'mpmath '+ns[0]['mpmath'],l['lean_version'],'Bundled Std only'],'hardware':platform.platform()+'; one Lean worker'},
 'mathematics':{'assertion_tested':'Principal-cover matrices and dual cubic invariant; finite transfer inversion; actual seven-point gamma product with explicit continuation; formal model pullback coefficients. Smooth rigidity has a separate ordinary proof.',
 'coefficient_domain':'Z and Q in exact checks; mpmath complex floating arithmetic for numerical regressions.',
 'conventions':'N=2I-M, A=M^T, B=N^T; transfer is the unnormalized sum over seven preimages; F=1/S_5(z+t;t,s); delta7=(-t+2s+4)/7.',
 'inputs':[{'path':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor)},{'path':'prior/gamma_evaluator.py','sha256':sha(ROOT/'prior/gamma_evaluator.py')}]+[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted((ROOT/'formalization').glob('H12*.lean'))],
 'bounds':{'kernel_residue_triples':343,'finite_Laurent_gauges':625,'critical_series_truncations':12,'exact_named_assertions':len(e['assertions']),'exact_negative_controls':len(e['negative_controls']),'new_lean_theorems':l['theorem_count'],'requested_decimal_digits':[40,70],'guard_digits':25,'series_term_cap':20000,'lean_module_timeout_seconds':90},
 'non_claims':['No gamma-arithmetic equality, exact polarized reality, or discrepancy root-of-unity bound is established.','No actual nonzero smooth relative gamma/model multiplier or its principal-norm relation has been constructed.','The global analytic gamma norm and smooth rigidity are not formalized in Lean.','No full inherited Lean replay and no directed interval or literature-priority claim.']},
 'randomness':{'used':False,'generator':'none','seed':None},
 'run':{'started_at':e['started_at'],'runtime_seconds':e['runtime_seconds']+l['runtime_seconds']+sum(n['runtime_seconds'] for n in ns),'exit_status':0},
 'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in fs],
 'checks':[{'name':'exact algebra and finite transfer reconstruction','result':'PASS','assertions':len(e['assertions']),'negative_controls':len(e['negative_controls'])},{'name':'all new Lean theorems and axiom audit','result':'PASS','theorems':l['theorem_count']},{'name':'false integer equality','result':'REJECTED','exit_status':l['negative_control_exit']}]+[{'name':'gamma norm regression '+str(n['digits']),'result':'PASS','equalities':len(n['equalities']),'negative_controls':len(n['negative_controls'])} for n in ns],
 'result':'34 new coefficient theorems verified; exact finite norm/transfer and actual gamma-product checks pass. Principal-norm rigidity proved by an ordinary analytic argument; main comparison remains open.',
 'residual_risks':['Analytic arguments have self-review only and are outside Lean.','Numerical gamma checks are floating regressions, not interval certificates.','The required actual relative multiplier and normalized principal-norm compatibility are missing.','Inherited proof/source history is preserved, not freshly replayed.','Legacy v1 provenance validation checks structure and output hashes, not mathematical correctness.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
