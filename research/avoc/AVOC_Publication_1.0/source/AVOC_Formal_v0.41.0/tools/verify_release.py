#!/usr/bin/env python3
"""Rebuild local AVOC sources against exact pinned dependencies, in bounded chunks.
Does not delete or rebuild the shared mathlib cache. Requires Python 3.10+ on Linux.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--index',action='store_true');p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=10000);p.add_argument('--audit',action='store_true');p.add_argument('--negative',action='store_true');args=p.parse_args()
rdir=root/'results/v0.35.0';rdir.mkdir(parents=True,exist_ok=True)
kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
helper=root/'tools/lean_one.py'
if args.prepare or args.index:
    pins=json.loads((root/'lake-manifest.json').read_text())['packages'];checks=[]
    for pin in pins:
        d=kit/'workspace/.lake/packages'/pin['name']
        actual=subprocess.check_output(['git','-c',f'safe.directory={d}','-C',str(d),'rev-parse','HEAD'],text=True).strip()
        checks.append(dict(name=pin['name'],expected=pin['rev'],actual=actual,passed=actual==pin['rev']))
    (rdir/'dependency_pins.json').write_text(json.dumps(checks,indent=2)+'\n')
    if not all(c['passed'] for c in checks):raise SystemExit('Dependency pin mismatch')
    files={str(q.relative_to(root).with_suffix('')).replace('/','.'):q for q in (root/'AVOC').glob('*.lean') if q.name not in ['Audit.lean','FullAudit.lean']}
    files['AVOC']=root/'AVOC.lean'
    files['CertificateMain']=root/'tools/CertificateMain.lean'
    files['CertificateBatch']=root/'tools/CertificateBatch.lean'
    files['PlannerMain']=root/'tools/PlannerMain.lean'
    files['LivePlannerMain']=root/'tools/LivePlannerMain.lean'
    if (root/'tools/RecoveryMain.lean').exists(): files['RecoveryMain']=root/'tools/RecoveryMain.lean'
    files['AttemptMain']=root/'tools/AttemptMain.lean'
    files['AttemptBatch']=root/'tools/AttemptBatch.lean'
    files['RetryDecisionMain']=root/'tools/RetryDecisionMain.lean'
    files['UpgradeMain']=root/'tools/UpgradeMain.lean'
    files['SynthesisMain']=root/'tools/SynthesisMain.lean'
    files['SemanticSynthesisMain']=root/'tools/SemanticSynthesisMain.lean'
    files['SemanticLibraryMain']=root/'tools/SemanticLibraryMain.lean'
    files['AffineMain']=root/'tools/AffineMain.lean'
    files['AffineFactorMain']=root/'tools/AffineFactorMain.lean'
    files['AffineReuseMain']=root/'tools/AffineReuseMain.lean'
    files['AffineProbeMain']=root/'tools/AffineProbeMain.lean'
    files['AdaptiveProbeMain']=root/'tools/AdaptiveProbeMain.lean'
    files['MultiLevelMain']=root/'tools/MultiLevelMain.lean'
    files['AffineTerminalMain']=root/'tools/AffineTerminalMain.lean'
    files['StagedAffineMain']=root/'tools/StagedAffineMain.lean'
    if (root/'tools/DurableUpgradeMain.lean').exists(): files['DurableUpgradeMain']=root/'tools/DurableUpgradeMain.lean'
    if (root/'tools/DurableUpgradeBatch.lean').exists(): files['DurableUpgradeBatch']=root/'tools/DurableUpgradeBatch.lean'
    order=[];visited=set();active=set()
    def visit(name):
        if name in visited:return
        if name in active:raise ValueError('Import cycle: '+name)
        active.add(name)
        for d in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',files[name].read_text(),re.M):
            if d not in files:raise ValueError('Missing local import '+d)
            visit(d)
        active.remove(name);visited.add(name);order.append(str(files[name].relative_to(root)))
    for name in sorted(files):visit(name)
    (rdir/'build_order.json').write_text(json.dumps(order,indent=2)+'\n')
    if args.prepare: shutil.rmtree(root/'.lake/build',ignore_errors=True)
    (root/'.lake/build/lib/lean').mkdir(parents=True,exist_ok=True)
    print('Prepared clean local rebuild:' if args.prepare else 'Indexed local targets (existing outputs retained):',len(order),'modules; dependencies retained.')
    raise SystemExit(0)
if args.audit:
    rc=subprocess.call([sys.executable,str(helper),'AVOC/FullAudit.lean','--no-output','--log','results/v0.35.0/full_axiom_audit.log'])
    if rc:raise SystemExit(rc)
    text=(rdir/'full_axiom_audit.log').read_text();deps=set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):
        deps.update(s.strip() for s in block.split(',') if s.strip())
    allowed={'propext','Classical.choice','Quot.sound'}
    names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
    expected=json.loads((rdir/'declaration_inventory.json').read_text())
    ok=not(deps-allowed) and set(names)=={x['qualified_name'] for x in expected}
    result=dict(passed=ok,audited=len(names),expected=len(expected),axioms=sorted(deps),unexpected=sorted(deps-allowed))
    (rdir/'axiom_audit_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    raise SystemExit(0 if ok else 1)
if args.negative:
    results=[]
    for f in sorted((root/'tests/negative').glob('*.lean'))[args.start:args.start+args.count]:
        subprocess.run([sys.executable,str(helper),str(f.relative_to(root)),'--no-output','--log',f'results/v0.35.0/negative_{f.stem}.log'],stdout=subprocess.DEVNULL,check=False)
        rec=json.loads((rdir/f'negative_{f.stem}.json').read_text());text=(rdir/f'negative_{f.stem}.log').read_text()
        setup_failure=bool(re.search(r'object file .*does not exist|unknown module|failed to locate application',text))
        rec['expected_rejection']=rec['returncode']!=0 and not rec['timed_out'] and not setup_failure
        results.append(rec);print(f.name,'EXPECTED REJECTION' if rec['expected_rejection'] else 'BAD TEST FAILURE',flush=True)
    (rdir/'negative_summary.json').write_text(json.dumps(results,indent=2)+'\n')
    raise SystemExit(0 if all(r['expected_rejection'] for r in results) else 1)
order=json.loads((rdir/'build_order.json').read_text())
for i in range(args.start,min(args.start+args.count,len(order))):
    f=order[i]
    print(f'BUILD {i+1}/{len(order)} {f}',flush=True)
    rc=subprocess.call([sys.executable,str(helper),f,'--log',f'results/v0.35.0/clean_{Path(f).stem}.log'],stdout=subprocess.DEVNULL)
    if rc:
        print((rdir/f'clean_{Path(f).stem}.log').read_text());raise SystemExit(rc)
print('Chunk passed.',flush=True)
