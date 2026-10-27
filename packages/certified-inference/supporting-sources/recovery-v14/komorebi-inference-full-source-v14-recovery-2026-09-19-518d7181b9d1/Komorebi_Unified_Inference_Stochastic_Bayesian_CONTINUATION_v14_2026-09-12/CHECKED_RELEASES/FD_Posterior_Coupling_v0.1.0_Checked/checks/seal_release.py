#!/usr/bin/env python3
"""Seal ONLY final-source successful receipts; this is not a substitute for compiling Lean."""
from __future__ import annotations
import argparse,collections,datetime as dt,hashlib,json,platform,re,subprocess
from pathlib import Path

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p:Path,x:object)->None:p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def main()->None:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--runtime',type=Path,required=True);a=ap.parse_args()
    root=Path(__file__).resolve().parents[1];src=root/'Komorebi';rt=a.runtime.resolve()
    cache=rt/'workspace/.lake/build/lib/lean/Komorebi';mods=json.loads((root/'MODULE_ORDER.json').read_text())
    decl=json.loads((root/'DECLARATIONS.json').read_text());inherited=json.loads((root/'INHERITED_SOURCES.json').read_text())
    attempts=[]
    for p in sorted((root/'audit').glob('*/*.json')):
        d=json.loads(p.read_text());d['receipt_path']=str(p.relative_to(root));attempts.append(d)
    final=[]
    for mod in mods:
        sf=src/(mod+'.lean');sh=sha(sf);of=cache/(mod+'.olean');assert of.is_file(),mod
        assert not re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',sf.read_text()),mod
        candidates=[d for d in attempts if d.get('module')==mod and d.get('exit_status')==0
          and d.get('source_sha256_before')==sh and d.get('source_sha256_after')==sh
          and d.get('staged_source_sha256')==sh and d.get('output_sha256')==sha(of)]
        assert candidates,('No current successful receipt',mod)
        d=candidates[-1];ad=root/Path(d['receipt_path']).parent
        assert sha(ad/(mod+'.log'))==d['log_sha256']
        assert sha(ad/(mod+'.lean'))==sh
        for dep,h in d['dependencies'].items():
            dn=dep.rsplit('.',1)[1]
            assert sha(src/(dn+'.lean'))==h['source_sha256'],(mod,dep,'source')
            assert sha(cache/(dn+'.olean'))==h['olean_sha256'],(mod,dep,'compiled')
        if mod in inherited:assert sh==inherited[mod],('inherited source changed',mod)
        final.append(d)
    audit=next(d for d in final if d['module']=='FDPosteriorCouplingAxiomAudit')
    log=root/Path(audit['receipt_path']).with_suffix('.log');txt=log.read_text()
    results={}
    for m in re.finditer(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",txt,re.S):
        results[m[1]]=[x.strip() for x in (m[2] or '').split(',') if x.strip()]
    assert set(results)=={x['name'] for x in decl},(set(results)^{x['name'] for x in decl})
    allowed={'propext','Classical.choice','Quot.sound'}
    assert all(set(x)<=allowed for x in results.values())
    dump(root/'AXIOM_AUDIT.json',{'status':'PASS','audited_declarations':len(results),
      'allowed_axioms':sorted(allowed),'observed_axioms':sorted(set(sum(results.values(),[]))),
      'log_path':str(log.relative_to(root)),'log_sha256':sha(log),'results':results})
    neg=json.loads((root/'checks/NEGATIVE_CONTROLS.json').read_text())
    assert len(neg)==2 and all(x['expected_rejection'] and x['exit_status']!=0 for x in neg)
    diagnostic=json.loads((root/'checks/EXACT_CHECKS.json').read_text());assert diagnostic['status']=='PASS'
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    failed=[d for d in attempts if d.get('exit_status')!=0]
    record={'status':'PASS','sealed_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
     'source_commit':commit,'scope':'Actual finite-dimensional posterior coupling, all-plan W2 upper certificates, inexact-gain residual stopping implication, and two-model factor coupling',
     'environment':{'lean_version':final[0]['lean_version'],'mathlib_commit':final[0]['mathlib_commit'],
                    'platform':platform.platform(),'warning_as_error':True,'threads_per_lean_process':1},
     'active_modules':len(mods),'retained_modules_recompiled':len(inherited),'new_modules':len(mods)-len(inherited),
     'theorem_lemma_declarations':len(decl),'declaration_groups':dict(collections.Counter(x['group'] for x in decl)),
     'axiom_audit_coverage':len(results),'forbidden_tokens_in_active_sources':[],
     'successful_final_modules':final,'failed_completed_draft_checks':len(failed),
     'failed_attempts':[{'module':d['module'],'exit_status':d['exit_status'],'elapsed_seconds':d['elapsed_seconds'],'receipt_path':d['receipt_path']} for d in failed],
     'final_compile_process_seconds':round(sum(d['elapsed_seconds'] for d in final),3),
     'all_completed_attempt_process_seconds':round(sum(d['elapsed_seconds'] for d in attempts),3),
     'negative_controls':neg,'independent_diagnostic':{k:v for k,v in diagnostic.items() if k!='cases'},
     'verification_boundary':'Every active module compiled successfully in its final form this turn. This seal validates those existing receipts and hashes; sealing does not rerun Lean. The pinned mathlib cache was reused. The full historical v4/continuous-time program was not rebuilt.',
     'transport_definition_boundary':'Standard extended all-coupling infimum, not a selected-plan surrogate. Full metric axioms, optimal plans and equivalence with an independently defined API are not formalized.',
     'nonclaims':['No optimality of the displayed coupling','No certified floating-point, numerical eigenvalue bound, or iterative convergence implementation',
       'No factor-error conversion from covariance-only discrepancies','No Hilbert-Schmidt packet-refinement theorem in this block',
       'No common canonical null set across different models','No singular innovation, sequential filtering closure, nonlinear/non-Gaussian or full Ito development',
       'No literature-priority claim; declaration counts include support identities']}
    dump(root/'FINAL_VERIFICATION_RECEIPT.json',record)
    outputs=[root/'FINAL_VERIFICATION_RECEIPT.json',root/'AXIOM_AUDIT.json',root/'DECLARATIONS.json',
      root/'checks/EXACT_CHECKS.json',root/'checks/NEGATIVE_CONTROLS.json',log]
    outputs += [src/(m+'.lean') for m in mods]
    manifest={'schema_version':1,'claim_id':'KUI-POSTERIOR-COUPLING-v0.1.0',
      'repository':{'commit':commit,'dirty':bool(subprocess.check_output(['git','-C',str(root),'status','--porcelain'],text=True).strip())},
      'command':'python verify_blocks.py --runtime RUNTIME --modules MODULE --timeout 40 (one call per MODULE_ORDER entry; exact argv in the final receipt)',
      'environment':{'software':[final[0]['lean_version'],'mathlib '+final[0]['mathlib_commit'],'Python '+platform.python_version(),'SymPy '+diagnostic['sympy_version']],
                     'hardware':platform.machine()+' CPU; single Lean thread per process; hardware speed is not a scientific claim'},
      'mathematics':{'assertion_tested':'Lean kernel acceptance of the stated universal real finite-dimensional posterior coupling bounds; separate bounded rational diagnostics',
        'coefficient_domain':'Arbitrary real matrices in Lean; exact rationals in independent diagnostics',
        'conventions':'Euclidean Hilbert norms, Frobenius squared matrix energy, centered Gaussian covariance, ENNReal extended all-plan quadratic transport infimum',
        'inputs':['Komorebi/*.lean','MODULE_ORDER.json','pinned portable Lean and mathlib cache','checks/exact_checks.py'],
        'bounds':{'Lean':'Arbitrary finite index types and parameters satisfying each theorem hypotheses','diagnostics':'24 constructed cases, state/observation dimensions 1..3; 16-point finite quadratic check','process_cap_seconds':40},
        'non_claims':record['nonclaims']},
      'randomness':{'used':False,'generator':'deterministic rational construction; no random sampling','seed':None},
      'run':{'started_at':dt.datetime.strptime(min(d['started_at_utc'] for d in attempts),'%Y%m%dT%H%M%S%fZ').replace(tzinfo=dt.timezone.utc).isoformat(),
             'runtime_seconds':record['all_completed_attempt_process_seconds'],'exit_status':0},
      'outputs':[{'path':str(p.relative_to(root)),'sha256':sha(p)} for p in outputs],
      'checks':['31 final-source compilations with warning-as-error','119 complete axiom audits','source and dependency output hash consistency',
                'two negative-control rejections','24 exact-rational diagnostics','active-source forbidden token scan'],
      'result':'PASS within the formal statement and bounded diagnostic scopes',
      'residual_risks':['Pinned precompiled mathlib cache reused','Numerical implementations are not verified',
                        'Official Mathbox manifest validator executable unavailable; project verifier used','Version-1 manifest supplemented by per-process argv, input/output hashes and failed snapshots']}
    dump(root/'COMPUTATION_MANIFEST.json',manifest)
    print(json.dumps({k:record[k] for k in ['status','active_modules','theorem_lemma_declarations','declaration_groups','axiom_audit_coverage','failed_completed_draft_checks','final_compile_process_seconds']},indent=2))
if __name__=='__main__':main()
