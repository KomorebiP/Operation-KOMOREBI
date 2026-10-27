#!/usr/bin/env python3
"""Record the actual accepted runs and all delivered file hashes."""
from pathlib import Path
import hashlib,json,platform
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 exact=json.loads((ROOT/'evidence/exact_results.json').read_text())
 lean=json.loads((ROOT/'evidence/lean_results.json').read_text())
 ancestor=ROOT/'prior/v010_source_and_evidence.zip'
 (ROOT/'evidence/predecessor.json').write_text(json.dumps({'checkpoint':'v0.10.0','archive':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor),'inherited_fresh_replay':False},indent=2)+'\n')
 files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.lean-check' not in p.parts and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and p.suffix not in ('.olean','.ilean'))
 manifest={
 'schema_version':1,'claim_id':'Komorebi-H12-v011-Fourier-flattening-conjugation',
 'repository':{'commit':None,'dirty':True,'base_checkpoint':'Based Holonomy v0.10.0','base_archive_sha256':sha(ancestor),'fresh_inherited_replay':False},
 'command':['python checks/exact_checks.py','python checks/verify_lean.py --lean '+lean['compiled_modules'][0]['argv'][0]],
 'environment':{'software':['Python '+platform.python_version(),'SymPy '+exact['software']['sympy'],lean['lean_version'],'Bundled Std only'],'hardware':platform.platform()+'; one Lean worker'},
 'mathematics':{
  'assertion_tested':'Finite Fourier-orbit antidifference certificates, exact dual matrix/conductor transport, rational flat extension numerator and finite negative controls. Global smooth/holomorphic and conjugation results have separate ordinary proofs.',
  'coefficient_domain':'Z, Q, exact symbolic polynomials and sparse Laurent coefficient dictionaries.',
  'conventions':'A=M^T on frequency columns. h=g-g composed with M. Gauge a becomes a*b/(b composed with M). Marked point e2/3. Complex conjugation maps k to -k on Fourier coefficients.',
  'inputs':[{'path':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor)}]+[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted((ROOT/'formalization').glob('H12*.lean'))],
  'bounds':dict(exact['bounds'],finite_chain_cases=exact['finite_chain_cases'],new_lean_theorems=lean['theorem_count'],exact_assertions=exact['assertion_count'],negative_controls=exact['negative_control_count'],lean_module_timeout_seconds=90),
  'non_claims':['No original gamma equality or polarized reality is proved.','No relative gamma/model multiplier or actual Fourier residue has been constructed or evaluated.','No actual discrepancy is placed in mu3 by the conditional theorem.','No infinite analytic series or bundle theory is formalized in the new Std modules.','No inherited full Lean replay is claimed.','No gamma numerical/interval computation or novelty assertion.']},
 'randomness':{'used':False,'generator':'none','seed':None},
 'run':{'started_at':exact['started_at'],'runtime_seconds':exact['runtime_seconds']+lean['runtime_seconds'],'exit_status':0},
 'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in files],
 'checks':[{'name':'exact finite coefficient and matrix checks','result':'PASS','assertions':exact['assertion_count'],'negative_controls':exact['negative_control_count']},{'name':'fresh Lean compilation and all-theorem axiom audit','result':'PASS','theorems':lean['theorem_count']},{'name':'false integer equality','result':'REJECTED','exit_status':lean['negative_control_exit']}],
 'result':'28 new coefficient theorem constants verified; exact finite certificates pass. Analytic right inverse and conjugation-only phase criterion proved in ordinary mathematics; original gamma comparison remains open.',
 'residual_risks':['Global Fourier regularity arguments are outside Lean and have only self-review.','The actual gamma/model scalar identification and antisymmetric-residue cancellations are missing.','The adapted legacy v1 validator checks record structure and hashes, not mathematical correctness.','The 360 inherited declarations are retained as historical evidence without a fresh replay.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
