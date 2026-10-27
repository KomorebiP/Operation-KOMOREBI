#!/usr/bin/env python3
"""Fresh local AVOC v0.38 build/audit/negative runner against exact pinned caches."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
RD=ROOT/'results/v0.38.0'; RD.mkdir(parents=True,exist_ok=True)
P=argparse.ArgumentParser()
P.add_argument('--prepare',action='store_true')
P.add_argument('--index',action='store_true')
P.add_argument('--audit',action='store_true')
P.add_argument('--negative',action='store_true')
P.add_argument('--start',type=int,default=0)
P.add_argument('--count',type=int,default=100000)
P.add_argument('--seconds',type=int,default=180)
A=P.parse_args()
KIT=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
HELPER=ROOT/'tools/lean_one.py'

def build_order():
    files={str(q.relative_to(ROOT).with_suffix('')).replace('/','.'):q
           for q in (ROOT/'AVOC').glob('*.lean') if q.name not in ['Audit.lean','FullAudit.lean']}
    files['AVOC']=ROOT/'AVOC.lean'
    for q in sorted((ROOT/'tools').glob('*.lean')):
        files[str(q.relative_to(ROOT).with_suffix('')).replace('/','.')]=q
    order=[]; visited=set(); active=set()
    def visit(name):
        if name in visited:return
        if name in active:raise ValueError('Import cycle: '+name)
        active.add(name)
        text=files[name].read_text()
        for d in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',text,re.M):
            if d not in files:raise ValueError('Missing local import '+d+' from '+name)
            visit(d)
        active.remove(name); visited.add(name); order.append(str(files[name].relative_to(ROOT)))
    for name in sorted(files):visit(name)
    return order

if A.prepare or A.index:
    pins=json.loads((ROOT/'lake-manifest.json').read_text())['packages']; checks=[]
    for pin in pins:
        d=KIT/'workspace/.lake/packages'/pin['name']
        actual=subprocess.check_output(['git','-c',f'safe.directory={d}','-C',str(d),'rev-parse','HEAD'],text=True).strip()
        checks.append(dict(name=pin['name'],expected=pin['rev'],actual=actual,passed=actual==pin['rev']))
    (RD/'dependency_pins.json').write_text(json.dumps(checks,indent=2)+'\n')
    if not all(c['passed'] for c in checks):raise SystemExit('Dependency pin mismatch')
    order=build_order(); (RD/'build_order.json').write_text(json.dumps(order,indent=2)+'\n')
    if A.prepare: shutil.rmtree(ROOT/'.lake/build',ignore_errors=True)
    (ROOT/'.lake/build/lib/lean').mkdir(parents=True,exist_ok=True)
    print(('Prepared clean local rebuild:' if A.prepare else 'Indexed local targets:'),len(order))
    raise SystemExit(0)

if A.audit:
    log='results/v0.38.0/full_axiom_audit.log'
    rc=subprocess.call([sys.executable,str(HELPER),'AVOC/FullAudit.lean','--no-output','--seconds',str(max(A.seconds,600)),'--log',log])
    if rc: raise SystemExit(rc)
    text=(ROOT/log).read_text(); deps=set()
    for block in re.findall(r'depends on axioms:\s*\[(.*?)\]',text,re.S):
        deps.update(s.strip() for s in block.split(',') if s.strip())
    names=re.findall(r"^'([^']+)' (?:depends on axioms|does not depend on any axioms)",text,re.M)
    expected=json.loads((RD/'declaration_inventory.json').read_text())
    expected_names={x['qualified_name'] for x in expected}
    allowed={'propext','Classical.choice','Quot.sound'}
    result=dict(passed=not(deps-allowed) and set(names)==expected_names and len(names)==len(set(names)),
                reports=len(names),unique_reports=len(set(names)),expected=len(expected),
                missing=sorted(expected_names-set(names)),extra=sorted(set(names)-expected_names),
                duplicates=len(names)-len(set(names)),axiom_union=sorted(deps),unexpected=sorted(deps-allowed),
                allowed_only=not bool(deps-allowed))
    (RD/'axiom_audit_summary.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['passed'] else 1)

if A.negative:
    files=sorted((ROOT/'tests/negative').glob('*.lean'))
    selected=files[A.start:A.start+A.count]; outdir=RD/'negative_all'; outdir.mkdir(parents=True,exist_ok=True)
    results=[]
    for f in selected:
        log=outdir/f'{f.stem}.log'
        cmd=[sys.executable,str(HELPER),str(f.relative_to(ROOT)),'--no-output','--seconds',str(A.seconds),'--log',str(log.relative_to(ROOT))]
        subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=False)
        recp=log.with_suffix('.json')
        if not recp.exists():
            rec={'source':str(f.relative_to(ROOT)),'returncode':None,'timed_out':False,'expected_rejection':False,'reason':'missing record'}
        else:
            rec=json.loads(recp.read_text()); txt=log.read_text(errors='replace')
            setup=bool(re.search(r'object file .*does not exist|unknown module|failed to locate application|No such file or directory',txt,re.I))
            rec.update(source=str(f.relative_to(ROOT)),setup_failure=setup,
                       expected_rejection=rec.get('returncode',0)!=0 and not rec.get('timed_out',False) and not setup)
        results.append(rec); print(f.name,'EXPECTED REJECTION' if rec['expected_rejection'] else 'BAD/INCONCLUSIVE',flush=True)
    part=outdir/f'part_{A.start}_{A.start+len(selected)}.json'; part.write_text(json.dumps(results,indent=2)+'\n')
    # Complete summary only when all records exist and are current enough for this invocation set.
    if A.start==0 and len(selected)==len(files):
        summary={'total':len(results),'substantive_rejections':sum(bool(x['expected_rejection']) for x in results),'records':results}
        (outdir/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    raise SystemExit(0 if results and all(r['expected_rejection'] for r in results) else (0 if not results else 1))

order=json.loads((RD/'build_order.json').read_text())
for i in range(A.start,min(A.start+A.count,len(order))):
    f=order[i]; print(f'BUILD {i+1}/{len(order)} {f}',flush=True)
    log=f'results/v0.38.0/clean_{Path(f).stem}.log'
    rc=subprocess.call([sys.executable,str(HELPER),f,'--seconds',str(A.seconds),'--log',log],stdout=subprocess.DEVNULL)
    if rc:
        print((ROOT/log).read_text(errors='replace')[-5000:]); raise SystemExit(rc)
print('Chunk passed.',flush=True)
