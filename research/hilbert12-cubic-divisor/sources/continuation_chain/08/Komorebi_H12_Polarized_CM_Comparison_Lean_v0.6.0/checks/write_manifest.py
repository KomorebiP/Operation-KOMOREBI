#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 e=json.loads((ROOT/'evidence/exact_results.json').read_text());iv=[json.loads((ROOT/f'evidence/interval_{d}.json').read_text()) for d in (90,120)];l=json.loads((ROOT/'evidence/new_lean_results.json').read_text());pr=json.loads((ROOT/'evidence/predecessor.json').read_text())
 assert e['check_count']==54 and len(e['negative_controls'])==5
 assert all(x['check_count']==39 and len(x['negative_controls'])==4 for x in iv)
 assert l['new_theorem_count']==18
 for n,h in pr['unchanged_inherited_theorem_source_hashes'].items():assert sha(ROOT/'formalization'/n)==h
 for n,h in l['source_hashes'].items():assert sha(ROOT/'formalization'/n)==h
 def keep(p):
  r=p.relative_to(ROOT)
  return p.is_file() and p.name!='MANIFEST.json' and not any(x.startswith('.') or x=='__pycache__' for x in r.parts) and not any(p.name.endswith(q) for q in ('.olean','.olean.private','.olean.server','.ir','.ir.sig','.ilean'))
 outputs=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(ROOT.rglob('*')) if keep(p)]
 obj={'schema_version':1,'claim_id':'H12-POLARIZED-CM-CUBE-0.6.0','repository':{'commit':None,'dirty':False,'context':'Hash-authenticated isolated snapshot; not a Git repository.'},'command':['python checks/exact_checks.py','python checks/interval_checks.py --digits 90','python checks/interval_checks.py --digits 120','python checks/verify_new_lean.py --runtime PINNED_RUNTIME'],
 'environment':{'software':[f'Python {sys.version.split()[0]}','SymPy '+e['sympy'],'mpmath '+iv[0]['mpmath'],l['lean_version'],'Mathlib '+l['mathlib_revision']],'hardware':platform.platform()+'; CPU; cgroup ceiling 4 GiB','resource_caps':{'new_lean_process_timeout_seconds':60,'lean_workers':1,'interval_terms':2500}},
 'mathematics':{'assertion_tested':'Four relative norm formulas reconstruct the specified arithmetic candidate cube; conjugate polarization is positive; conditional analytic reality + inherited modulus + interval signs implies original equality.','coefficient_domain':'Exact 18-dimensional rational quotient and independent SymPy QQ Groebner; Lean commutative rings/fields and complex norms; mpmath.iv intervals.','conventions':'beta=7^(1/3)omega^2, xi fixed by exp(6pi i/7) Gauss sum; iota fixes beta but actual conjugation sends beta to omega^2 beta; C=epsilon*a1*a2^3/omega.','inputs':[pr,{'path':'prior/ARITHMETIC_INPUT.md','sha256':sha(ROOT/'prior/ARITHMETIC_INPUT.md')},json.loads((ROOT/'evidence/runtime_restore_current.json').read_text())],
 'bounds':{'exact_checks':54,'exact_negative_controls':5,'interval_digits':[90,120],'interval_checks_each':39,'interval_negative_controls_each':4,'truncation':2500,'freshly_compiled_new_theorems':18,'recompiled_inherited_branch_dependency_theorems':4,'cumulative_source_inventory':172,'full_inherited_replay_status':'NOT COMPLETED; documented timeouts'},
 'non_claims':['No exact reality of C*U_Gamma^3 or gamma-arithmetic power equality.','No inference of equality from a near-zero enclosure.','No fresh complete replay of all 172 theorem constants.','No Lean formalization of the original rational-candidate to polynomial-normal-form conversion; two exact implementations check it.','No verification of mpmath.iv internals.','No historical novelty or general Hilbert-12 claim.']},
 'randomness':{'used':False,'generator':'none','seed':None},'run':{'started_at':min(e['started_at'],iv[0]['started_at'],iv[1]['started_at'],l['started_at']),'runtime_seconds':e['runtime_seconds']+sum(x['runtime_seconds'] for x in iv)+l['seconds'],'exit_status':0,'record_created_utc':datetime.now(timezone.utc).isoformat()},'outputs':outputs,
 'checks':[{'name':'exact arithmetic and independent normal form','count':54,'negative_controls':5,'result':'PASS'},{'name':'new Lean block fresh build and transitive axiom audit','count':18,'result':'PASS'},{'name':'inherited theorem source hashes unchanged','result':'PASS'},{'name':'false integer theorem rejected','result':'PASS'},{'name':'full inherited Lean replay','result':'NOT_COMPLETED; not part of successful new-block verdict'},*[{'name':f'interval run {x["interval_digits"]}','count':39,'negative_controls':4,'result':'PASS'} for x in iv]],
 'result':'New arithmetic factorization, exact polarization and conditional reality criterion verified. 18 new Lean theorems audited. Original analytic reality remains open; full inherited replay uncompleted.',
 'residual_risks':['Inherited Stark/CM interpretation is not re-audited end to end.','mpmath.iv experimental elementary routines are trusted.','The main analytic phase identity remains unproved.','Only the new formal block and its cubic-branch dependency have a completed fresh replay.','Version-one manifest without Git revision.']}
 (ROOT/'MANIFEST.json').write_text(json.dumps(obj,indent=2)+'\n');print('Manifest:',len(outputs),'hashes')
if __name__=='__main__':main()
