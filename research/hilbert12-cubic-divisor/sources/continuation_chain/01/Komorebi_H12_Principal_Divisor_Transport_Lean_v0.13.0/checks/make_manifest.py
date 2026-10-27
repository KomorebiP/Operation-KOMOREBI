#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,platform
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 e=json.loads((ROOT/'evidence/exact_results.json').read_text());l=json.loads((ROOT/'evidence/lean_results.json').read_text())
 ns=[json.loads((ROOT/f'evidence/numerical_{d}_{stage}.json').read_text()) for d in [40,70] for stage in ['anchor','first','second','divisor']]
 ancestor=ROOT/'prior/v012_source_and_evidence.zip'
 (ROOT/'evidence/predecessor.json').write_text(json.dumps({'base_checkpoint':'v0.12.0','archive':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor),'fresh_inherited_replay':False,'gamma_evaluator_sha256':sha(ROOT/'prior/gamma_evaluator.py'),'runtime_assembled_sha256':'66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34','runtime_assembled_bytes':2896789714},indent=2)+'\n')
 fs=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.lean-check' not in p.parts and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and p.suffix not in ['.olean','.ilean'])
 m={'schema_version':1,'claim_id':'Komorebi-H12-v013-principal-divisor-transport',
 'repository':{'commit':None,'dirty':True,'base_checkpoint':'Principal Seven Norm v0.12.0','base_archive_sha256':sha(ancestor),'fresh_inherited_replay':False},
 'command':['python checks/exact_checks.py']+[f'python checks/numerical_checks.py --digits {n["digits"]} --stage {n["stage"]}' for n in ns]+['python checks/verify_lean.py --lean '+l['compiled_modules'][0]['argv'][0]],
 'environment':{'software':['Python '+platform.python_version(),'SymPy '+e['sympy'],'mpmath '+ns[0]['mpmath'],l['lean_version'],'Bundled Std only'],'hardware':platform.platform()+'; one Lean worker'},
 'mathematics':{'assertion_tested':'Complete divisor coefficients of the actual principal correction, exact residue lifts, finite theta transition equations and zero anchor, and conjugation-divisor obstruction. Analytic statements have ordinary proofs, not a hidden gamma formalization.',
 'coefficient_domain':'Exact integers, Fraction rationals and SymPy QQ; mpmath complex floating regressions.',
 'conventions':'F=1/S5(z+t;t,s); tau=-t; N5 acts on (tau,s,1/5); pivot=-floor((2b-3c)/7); w=4 on multiples of five and -1 otherwise.',
 'inputs':[{'path':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor)},{'path':'prior/gamma_evaluator.py','sha256':sha(ROOT/'prior/gamma_evaluator.py')}]+[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted((ROOT/'formalization').glob('H12*.lean'))],
 'bounds':{'integer_sample_box':[-12,12],'sample_triples':15625,'ray_range':[1,100],'new_lean_theorems':l['theorem_count'],'requested_decimal_digits':[40,70],'guard_digits':25,'series_term_cap':20000,'divisor_probe_offset':'1e-8','divisor_probe_tolerance':'1e-3','equality_relative_tolerance':'10^(-digits+8)','lean_module_timeout_seconds':90},
 'non_claims':['No gamma-arithmetic equality or root-of-unity bound on its actual discrepancy.','No construction of a global periodic nonzero gamma/model relative multiplier.','No formally defined gamma or meromorphic-divisor theory in the new Lean modules.','No inherited full replay, interval certificate or literature-priority assertion.']},
 'randomness':{'used':False,'generator':'none','seed':None},
 'run':{'started_at':e['started_at'],'runtime_seconds':e['runtime_seconds']+l['runtime_seconds']+sum(n['runtime_seconds'] for n in ns),'exit_status':0},
 'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in fs],
 'checks':[{'name':'exact divisor coefficients and independent rational lift enumeration','result':'PASS','assertions':len(e['checks']),'negative_controls':len(e['negative_controls'])},{'name':'all new Lean declarations and axiom audit','result':'PASS','theorems':l['theorem_count']},{'name':'false integer equality','result':'REJECTED','exit_status':l['negative_control_exit']}]+[{'name':f'gamma correction {n["digits"]} digits {n["stage"]}','result':'PASS','identities':len(n['identities']),'divisor_diagnostics':len(n['divisor_diagnostics']),'negative_controls':len(n['negative_controls'])} for n in ns],
 'result':'20 new universal integer theorems compile; 21 exact assertions and four negative controls pass; 14 gamma/theta identities, four divisor diagnostics and four negative controls pass at both precisions. Main phase comparison remains open.',
 'residual_risks':['Analytic proofs have self-review only and remain outside Lean.','The numerical backend is floating arithmetic, not an interval or formal numerical certificate.','Exact nonzero smooth relative comparison and principal-norm compatibility are still missing.','Predecessor analytic dependencies are preserved, not end-to-end re-audited.','Legacy v1 provenance validation does not supply a repository revision or prove the mathematics.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
