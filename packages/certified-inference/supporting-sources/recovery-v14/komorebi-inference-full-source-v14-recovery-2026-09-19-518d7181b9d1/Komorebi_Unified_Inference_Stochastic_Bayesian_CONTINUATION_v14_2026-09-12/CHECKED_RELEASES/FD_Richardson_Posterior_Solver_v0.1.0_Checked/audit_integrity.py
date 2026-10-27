#!/usr/bin/env python3
"""Check final-source receipts, dependency hashes and complete kernel axiom coverage.

Read-only unless --seal is given. A seal audits recorded runs; it does not itself
rerun Lean. The per-module verifier provides the actual compilation evidence.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re, subprocess
from pathlib import Path
PIN='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
LC='6a10ac8c22beadecabdbb0919c2b50214762f91d'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--seal',action='store_true')
    a=ap.parse_args();root=Path(__file__).resolve().parent;rt=a.runtime.resolve();ws=rt/'workspace'
    modules=json.loads((root/'MODULE_ORDER.json').read_text());decls=json.loads((root/'DECLARATIONS.json').read_text())
    inherited=json.loads((root/'INHERITED_SOURCES.json').read_text());cache=ws/'.lake/build/lib/lean/Komorebi'
    ml=ws/'.lake/packages/mathlib'
    revision=subprocess.check_output(['git','-c',f'safe.directory={ml}','-C',str(ml),'rev-parse','HEAD'],text=True).strip()
    version=subprocess.check_output(['bash',str(rt/'run.sh'),'lean','--version'],text=True).strip()
    if revision!=PIN or LC not in version:raise RuntimeError('Pinned environment mismatch')
    records={};failed=[];incomplete=[]
    for p in sorted((root/'audit').glob('*/*.json')):
        d=json.loads(p.read_text())
        if 'module' not in d:continue
        d=dict(d,receipt_path=str(p.relative_to(root)))
        if d['exit_status']!=0:failed.append(d);continue
        n=d['module'];s=root/'Komorebi'/f'{n}.lean'
        if s.exists() and d['source_sha256_after']==sha(s):records[n]=d
    for p in (root/'audit').glob('*/*.lean'):
        if not p.with_suffix('.json').exists():incomplete.append(str(p.relative_to(root)))
    checks=[]
    for n in modules:
        s=root/'Komorebi'/f'{n}.lean'
        if re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',s.read_text()):raise RuntimeError('Forbidden active source token '+n)
        if n not in records:raise RuntimeError('No successful final-source receipt '+n)
        d=records[n];h=sha(s)
        for key in ['source_sha256_before','source_sha256_after','staged_source_sha256']:
            if d[key]!=h:raise RuntimeError('Source mismatch '+n+' '+key)
        o=cache/f'{n}.olean'
        if not o.exists() or d['output_sha256']!=sha(o):raise RuntimeError('Compiled output mismatch '+n)
        lp=root/Path(d['receipt_path']).with_suffix('.log')
        if sha(lp)!=d['log_sha256']:raise RuntimeError('Compile log mismatch '+n)
        for dep,entry in d['dependencies'].items():
            dn=dep.split('.')[-1]
            if sha(root/'Komorebi'/f'{dn}.lean')!=entry['source_sha256']:raise RuntimeError('Dependency source mismatch '+n+' '+dn)
            if sha(cache/f'{dn}.olean')!=entry['olean_sha256']:raise RuntimeError('Dependency output mismatch '+n+' '+dn)
        if n in inherited and inherited[n]!=h:raise RuntimeError('Inherited source changed '+n)
        checks.append(d)
    audit=records['RichardsonSolverAxiomAudit'];log=root/Path(audit['receipt_path']).with_suffix('.log')
    text=log.read_text();axioms={}
    for name,body in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]",text,re.S):
        axioms[name]=[x.strip() for x in body.replace('\n',' ').split(',') if x.strip()]
    expected={d['name'] for d in decls}
    if set(axioms)!=expected:raise RuntimeError('Incomplete axiom coverage '+str(expected-set(axioms)))
    allowed={'propext','Classical.choice','Quot.sound'}
    if any(set(xs)-allowed for xs in axioms.values()):raise RuntimeError('Unexpected axiom')
    tests=json.loads((root/'results/exact_tests.json').read_text())
    if tests['status']!='PASS':raise RuntimeError('Exact diagnostics did not pass')
    if tests['script_sha256']!=sha(root/'checks/test_richardson.py'):raise RuntimeError('Diagnostic script changed')
    if tests['solver_sha256']!=sha(root/'checks/solve_richardson.py'):raise RuntimeError('Python solver changed')
    instances=json.loads((root/'results/FORMAL_INSTANCES.json').read_text())
    if instances['status']!='PASS':raise RuntimeError('Concrete instances not checked')
    for x in instances['instances']:
        if sha(root/x['source'])!=x['source_sha256']:raise RuntimeError('Instance source changed')
        rd=json.loads((root/x['compilation_receipt']).read_text())
        if rd['exit_status']!=0 or rd['source_sha256_after']!=x['source_sha256']:
            raise RuntimeError('Instance receipt mismatch')
        if not set(x['declarations'])<=expected:raise RuntimeError('Instance theorem not axiom audited')
    negatives=json.loads((root/'results/negative_controls.json').read_text())
    if not all(d['exit_status'] not in (0,124) and d['expected_rejection'] for d in negatives):raise RuntimeError('Negative control failed')
    if (root/'.git').exists():
        source_commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    else:
        snapshot=json.loads((root/'SOURCE_SNAPSHOT.json').read_text())
        source_commit=snapshot['commit']
    result=dict(status='PASS',sealed_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
      source_commit=source_commit,
      scope='Exact rational Richardson gain solver: residual contraction, explicit finite iteration bound, executable early-stop total correctness and actual posterior Wasserstein tolerance',
      environment=dict(lean=version,mathlib=revision,threads_per_lean_process=1,warning_as_error=True),
      final_modules_passed=len(modules),inherited_modules_unchanged=len(inherited),
      theorem_lemma_declarations=len(decls),new_declarations=sum(x['group']=='new' for x in decls),
      axiom_audit=dict(declarations=len(axioms),allowed_axioms=sorted(allowed),all_allowed=True,log_sha256=sha(log)),
      successful_final_modules=checks,failed_completed_checks=failed,
      incomplete_attempt_source_snapshots=incomplete,negative_controls=negatives,exact_diagnostics=tests,formal_instances=instances,
      verification_boundary='This seal checks actual final-source compilation receipts and dependencies. The pinned Mathlib cache is reused. Historical unrelated chains are preserved, not rebuilt.',
      non_claims=['No formal parser/exporter proof','No floating-point or uncertain-real input enclosures',
                 'No automatic covariance witness discovery','No monotonicity of the unknown true posterior error or global optimality','No finite-precision complexity bound or numerical performance superiority','No model-changing or packet-changing policy','No full sequential filtering kernel recursion','No literature-priority claim'])
    if a.seal:
        (root/'AXIOM_AUDIT.json').write_text(json.dumps(dict(status='PASS',count=len(axioms),axioms=axioms),indent=2)+'\n')
        (root/'FINAL_VERIFICATION_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'successful_final_modules','failed_completed_checks','negative_controls','exact_diagnostics'}},indent=2))
if __name__=='__main__':main()
