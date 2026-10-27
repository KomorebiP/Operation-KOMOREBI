#!/usr/bin/env python3
"""Create a v1 computation record after accepted checks; no Git state is invented."""
from pathlib import Path
import hashlib,json,platform
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    exact=json.loads((ROOT/'evidence/exact_results.json').read_text())
    lean=json.loads((ROOT/'evidence/lean_results.json').read_text())
    ancestor=ROOT/'prior/v09_source_and_evidence.zip'
    (ROOT/'evidence/predecessor.json').write_text(json.dumps({'checkpoint':'v0.9.0','archive':str(ancestor.relative_to(ROOT)),'sha256':sha(ancestor),'inherited_fresh_replay':False},indent=2)+'\n')
    files=sorted(p for p in ROOT.rglob('*') if p.is_file() and '.lean-check' not in p.parts and '__pycache__' not in p.parts and p.name!='MANIFEST.json' and p.suffix not in ('.olean','.ilean'))
    m={'schema_version':1,'claim_id':'Komorebi-H12-v010-gauge-class-detector-and-based-holonomy',
       'repository':{'commit':None,'dirty':True,'base_checkpoint':'Komorebi_H12_Explicit_Descent_Packet_Lean_v0.9.0','base_archive_sha256':sha(ancestor),'fresh_inherited_replay':False},
       'command':['python checks/exact_checks.py','python checks/verify_lean.py --lean /absolute/path/to/toolchain/bin/lean'],
       'environment':{'software':['Python '+platform.python_version(),'SymPy '+exact['software']['sympy'],lean['lean_version'],'Bundled Std only'],'hardware':platform.platform()+'; one Lean worker'},
       'mathematics':{'assertion_tested':'Exact unit coinvariants, mixed-gauge and Hodge identities, full finite primitive seven-class selector, rational fixed-point carries, and coefficient counterexamples. Compact-line and character-valued based-holonomy interpretations have separate ordinary proofs.',
          'coefficient_domain':'Z, Q, finite residues modulo 6 and 7, exact Eisenstein coefficient pairs.',
          'conventions':'M on column lattice vectors; ell=(1,-1,3); holomorphic gauge exp(2*pi*i*u*m1*z0); cyclic Hodge pairs 12,20,01; omega residue maps 2 and 4; marked point e2/3; based multiplier hol_p/hol_0.',
          'inputs':[{'path':'prior/v09_source_and_evidence.zip','sha256':sha(ancestor)}]+[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted((ROOT/'formalization').glob('H12*.lean'))],
          'bounds':dict(exact['domains'],new_lean_theorems=lean['theorem_count'],exact_assertions=exact['assertion_count'],negative_controls=exact['negative_count'],lean_workers=1,lean_module_timeout_seconds=90),
          'non_claims':['No gamma equality or polarized reality is proved.','No actual extra-Eisenstein gamma cochain or compact comparison line is constructed.','No gamma phase is placed in mu3 by the conditional endpoint theorem.','No formal analytic bundle, gerbe or Appell-Humbert development.','No full fresh replay of the inherited 308 declarations.','No new gamma numerical or interval computation.']},
       'randomness':{'used':False,'generator':'none','seed':None},
       'run':{'started_at':exact['started_at'],'runtime_seconds':exact['runtime_seconds']+lean['runtime_seconds'],'exit_status':0},
       'outputs':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in files],
       'checks':[{'name':'exact implementation and finite assertions','result':'PASS','assertions':exact['assertion_count'],'negative_controls':exact['negative_count']},{'name':'new Lean compilation and all-theorem axiom audit','result':'PASS','theorems':lean['theorem_count']},{'name':'false integer equality','result':'REJECTED','exit_status':lean['negative_control_exit']}],
       'result':'52 new coefficient theorems and finite class tests verified. Original analytic target remains open. Compact based-holonomy theorem has an ordinary proof with explicit hypotheses.',
       'residual_risks':['Analytic geometry and the interpretation of coefficient identities are outside Lean.','No actual compact gamma descent or normalized comparison line is supplied.','Only self-review performed; no independent researcher review.','Adapted legacy v1 manifest checker validates recorded hashes and structure, not mathematics.','The inherited scientific claims were read and scoped but not freshly rebuilt in full.']}
    (ROOT/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':main()
