#!/usr/bin/env python3
"""Cold verification of the new discovery loop and only its local dependencies.
Upstream Mathlib cache is pinned/reused. The full old 202-case Lean suite is not
rebuilt here. Every new universal declaration and four symbolic queue traces are.
"""
from __future__ import annotations
import argparse,json,os,re,sys,time,tempfile,subprocess,hashlib,platform
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from audit_all import environment,manifest,sha
NEW=['DiscoveryRank','DiscoveryWorklist','DiscoveryTermination','DiscoveryFinite','DiscoveryLogic','DiscoveryTrace','DiscoveryExamples',
     'DiscoveryLargeTrace','DiscoveryDelayTrace','DiscoveryTorsionTrace','DiscoveryZeroTrace']
ALLOWED={'propext','Classical.choice','Quot.sound'}
def now():return datetime.now(timezone.utc).isoformat()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def modules():
    visited=set();order=[]
    def visit(m):
        if m in visited:return
        visited.add(m);p=ROOT/'formalization'/(m+'.lean')
        for dep in re.findall(r'^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)',p.read_text(),re.M):
            rel=dep.replace('.','/')
            if (ROOT/'formalization'/(rel+'.lean')).exists():visit(rel)
        order.append(m)
    for m in NEW:visit(m)
    return order

def inventory(mods):
    rows=[]
    pat=r'^(?:@\[[^\n]*?\]\s*)?(?:(?:noncomputable|protected|private)\s+)*(theorem|def|abbrev|inductive|structure|instance)\s+([\w.]+)'
    for m in mods:
        text=(ROOT/'formalization'/(m+'.lean')).read_text()
        ns=re.findall(r'^namespace\s+([\w.]+)\s*$',text,re.M)
        if len(ns)!=1:raise ValueError('namespace count '+m)
        for kind,name in re.findall(pat,text,re.M):
            rows.append({'module':m,'kind':kind,'name':ns[0]+'.'+name,'new':m in NEW,'generated_trace':m.endswith('Trace') and m!='DiscoveryTrace'})
    if len(rows)!=len({x['name'] for x in rows}):raise ValueError('duplicate declaration')
    return rows

def make_manifest(claim,cmd,inputs,outputs,run,maths,env):
    m=manifest(claim,cmd,inputs,outputs,run,maths,env)
    m['repository']['commit']='No git commit; exact parent ModelTheory v0.3 archive e694d635ad8582b5f13b415825ee58821bec2c6e37854d7b8e6969903902c42d'
    m['mathematics']['coefficient_domain']='Generic semiring/module queue, concrete prime-power rings ZMod(p^r), exact finite integer/residue witnesses'
    m['mathematics']['conventions']='All source states; column matrix dynamics; row extension PREPENDS a word symbol; FIFO roots; append accepted rows and successor candidates; one terminal fuel step.'
    m['mathematics']['non_claims']=['No verified efficient Smith oracle or verified Python parser/exporter.','The verified enumeration oracle may be exponentially expensive in accepted row count.','No new minimum test-count/formula-length/horizon theorem.','No full historical corpus or all-upstream Mathlib rebuild.','Not a held-out discovery or comparative performance study.']
    return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--python-only',action='store_true');a=ap.parse_args()
    runtime=a.runtime.resolve();lean=runtime/'toolchain/bin/lean';envinfo=environment(runtime)
    dump(ROOT/'new_evidence/ENVIRONMENT.json',envinfo)
    # Byte preservation against the immutable immediate predecessor, all 222 files.
    import zipfile
    parent=ROOT/'history/Komorebi_ModelTheory_Normalization_v0.3.zip'
    if sha(parent)!='e694d635ad8582b5f13b415825ee58821bec2c6e37854d7b8e6969903902c42d':raise ValueError('parent ZIP hash')
    preserved=[]
    with zipfile.ZipFile(parent) as z:
        for n in z.namelist():
            if '/formalization/' in n and n.endswith('.lean'):
                rel='formalization/'+n.split('/formalization/',1)[1];p=ROOT/rel
                if p.read_bytes()!=z.read(n):raise ValueError('inherited Lean source modified '+rel)
                preserved.append({'path':rel,'sha256':sha(p)})
    dump(ROOT/'new_evidence/PARENT_PRESERVATION.json',{'status':'PASS','parent_sha256':sha(parent),'unchanged_lean_modules':len(preserved),'files':preserved})
    mods=modules();decls=inventory(mods)
    dump(ROOT/'new_evidence/DECLARATIONS.json',decls)
    dump(ROOT/'new_evidence/MODULES.json',mods)
    if not a.python_only:
        ax=ROOT/'new_checks/AxiomAudit.lean'
        ax.write_text(''.join('import '+m.replace('/','.')+'\n' for m in mods)+'\n'+''.join('#print axioms '+d['name']+'\n' for d in decls))
        cd=ROOT/'new_checks/controls';cd.mkdir(exist_ok=True)
        control={
          'Positive':('import DiscoveryExamples\nexample : True := by trivial\n',True),
          'False':('import DiscoveryLogic\nexample : False := by decide\n',False),
          'Placeholder':('import DiscoveryLogic\nexample : True := by sorry\n',False),
          'WrongLoopResult':('import DiscoveryExamples\nopen Komorebi.Discovery Komorebi.Discovery.Examples\nexample : finitePrimeDiscover 2 2 3 (fun a => rowRight (shearA a)) shearO = some [] := by decide +kernel\n',False),
          'PrematureTrace':('import DiscoveryLargeTrace\nopen Komorebi.Discovery Komorebi.Discovery.LargeQueue\nexample : QueueTrace AA O [] (roots 2 1) [] := QueueTrace.done []\n',False)}
        for n,(txt,_) in control.items():(cd/(n+'.lean')).write_text(txt)
        bad=ROOT/'formalization/DiscoveryLargeTrace.lean'
        badtxt=bad.read_text().replace('namespace Komorebi.Discovery.LargeQueue','namespace Komorebi.Discovery.BadQueue').replace('end Komorebi.Discovery.LargeQueue','end Komorebi.Discovery.BadQueue')
        badtxt=re.sub(r'def delta0 : Fin 8 → R :=[^\n]*','def delta0 : Fin 8 → R := ![0,0,0,0,0,0,0,0]',badtxt)
        (cd/'BadSeparation.lean').write_text(badtxt);control['BadSeparation']=(badtxt,False)
        accepted=sorted(set([ROOT/'formalization'/(m+'.lean') for m in mods]+[ax]+list(cd.glob('*.lean'))+
                           [Path(__file__).resolve(),ROOT/'tools/audit_all.py',ROOT/'tools/validate_manifest.py',ROOT/'source_records/PARENT_ENVIRONMENT.json',ROOT/'new_evidence/DECLARATIONS.json']))
        before={p:sha(p) for p in accepted};start=now();t0=time.monotonic();tasks=[]
        ld=ROOT/'new_evidence/lean_cold';ld.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='komorebi-discovery-cold-') as tmp:
            env=os.environ.copy();env['OMP_NUM_THREADS']='1';env['OPENBLAS_NUM_THREADS']='1'
            env['LEAN_PATH']=':'.join([tmp]+[str(p) for p in (runtime/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')])
            def task(name,argv,expect=True):
                t=time.monotonic();log=ld/(name.replace('/','_')+'.log')
                try:
                    c=subprocess.run(argv,cwd=ROOT/'formalization',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
                    text=c.stdout;rc=c.returncode;timed=False
                except subprocess.TimeoutExpired as e:
                    text=e.stdout or '';text=text.decode() if isinstance(text,bytes) else text;rc=None;timed=True
                log.write_text(text);passed=not timed and ((rc==0) if expect else (rc is not None and rc>0 and 'error:' in text))
                if not expect and any(x in text.lower() for x in ['does not exist','unknown module prefix','maximum number of heartbeats','deep recursion','out of memory']):passed=False
                rec={'name':name,'argv':argv,'exit_code':rc,'expected_success':expect,'timed_out':timed,'seconds':time.monotonic()-t,'passed':passed,'log':str(log.relative_to(ROOT)),'sha256':sha(log)}
                tasks.append(rec);dump(ROOT/'new_evidence/PROGRESS.json',{'status':'IN_PROGRESS','tasks':tasks,'started_at':start})
                print(f'{len(tasks):02} {"PASS" if passed else "FAIL"} {name} {rec["seconds"]:.2f}s',flush=True)
                if not passed:raise RuntimeError(text)
                return text
            for m in mods:
                dest=Path(tmp)/(m+'.olean');dest.parent.mkdir(parents=True,exist_ok=True)
                task('build_'+m,[str(lean),'-j1','-DwarningAsError=true','-o',str(dest),m+'.lean'])
            text=task('axioms',[str(lean),'-j1','-DwarningAsError=true',str(ax)])
            found=set()
            for block in re.findall(r'depends on axioms:\s*\[([^]]*)\]',text,re.S):found.update(s.strip() for s in block.replace('\n',' ').split(',') if s.strip())
            audited=set(re.findall(r"'([^']+)'\s+(?:depends on axioms|does not depend on any axioms)",text))
            missing=[d['name'] for d in decls if d['name'] not in audited]
            if missing or found-ALLOWED:raise ValueError({'missing':missing,'unexpected_axioms':list(found-ALLOWED)})
            for n,(_,expect) in control.items():task('control_'+n,[str(lean),'-j1','-DwarningAsError=true',str(cd/(n+'.lean'))],expect)
        inputs=[{'path':str(p.relative_to(ROOT)),'sha256':before[p],'sha256_after':sha(p)} for p in accepted]
        if any(x['sha256']!=x['sha256_after'] for x in inputs):raise ValueError('input changed')
        result={'status':'PASS','started_at':start,'finished_at':now(),'runtime_seconds':time.monotonic()-t0,'workers':1,'timeout':120,
                'modules':len(mods),'new_modules':len(NEW),'inherited_modules_rebuilt':len(mods)-len(NEW),
                'named_declarations':len(decls),'declaration_counts':dict(Counter(x['kind'] for x in decls)),
                'new_counts':dict(Counter(x['kind'] for x in decls if x['new'])),
                'new_generic_counts':dict(Counter(x['kind'] for x in decls if x['new'] and not x['generated_trace'] and x['module']!='DiscoveryExamples')),
                'generated_trace_counts':dict(Counter(x['kind'] for x in decls if x['generated_trace'])),
                'axioms':sorted(found),'all_declarations_audited':len(audited),'tasks':tasks,
                'boundary':'Cold local dependency closure only; all 202 old generated certificate modules are preserved but not rebuilt.'}
        rp=ROOT/'results/DISCOVERY_LEAN_AUDIT.json';dump(rp,result);dump(ROOT/'new_evidence/PROGRESS.json',result)
        outputs=[{'path':str(rp.relative_to(ROOT)),'sha256':sha(rp),'kind':'result'}]+[{'path':t['log'],'sha256':t['sha256'],'kind':'log'} for t in tasks]
        cmd=[sys.executable,'new_checks/audit_release.py','--runtime',str(runtime)]
        dump(ROOT/'LEAN_MANIFEST.json',make_manifest('KMT-M4-VERIFIED-WORKLIST',cmd,inputs,outputs,result,
             {'assertion':'Universal oracle-parameterized queue invariant/termination, concrete executable enumerative membership, exact complete observable span and standard first-order definition; four symbolic queue traces replay the reference algorithm.',
              'bounds':{'modules':len(mods),'universal_prime_precision_dimension':True,'concrete_algorithm_examples':9,'symbolic_queue_traces':4}},envinfo))
    accepted=sorted(set([ROOT/'discovery_trace.py',ROOT/'discover.py',ROOT/'chainring.py']+list((ROOT/'new_checks').glob('*.py'))+
                         list((ROOT/'certificates').glob('*.json'))+list((ROOT/'queue_traces').glob('*.json'))+
                         [ROOT/'formalization'/(m+'.lean') for m in NEW]+[ROOT/'tools/audit_all.py']))
    before={p:sha(p) for p in accepted};start=now();t0=time.monotonic();cmd=[sys.executable,'new_checks/audit_discovery.py']
    p=subprocess.run(cmd,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
    log=ROOT/'new_evidence/python_audit.log';log.write_text(p.stdout)
    if p.returncode:raise RuntimeError(p.stdout)
    rp=ROOT/'results/DISCOVERY_AUDIT.json';data=json.loads(rp.read_text())
    inputs=[{'path':str(p.relative_to(ROOT)),'sha256':before[p],'sha256_after':sha(p)} for p in accepted]
    if any(x['sha256']!=x['sha256_after'] for x in inputs):raise ValueError('Python input changed')
    outputs=[{'path':str(rp.relative_to(ROOT)),'sha256':sha(rp),'kind':'result'},{'path':str(log.relative_to(ROOT)),'sha256':sha(log),'kind':'log'}]
    run={'started_at':start,'finished_at':now(),'runtime_seconds':time.monotonic()-t0,'workers':1,'timeout':120}
    dump(ROOT/'COMPUTATION_MANIFEST.json',make_manifest('KMT-M4-EXACT-TRACE-AUDIT',cmd,inputs,outputs,run,
      {'assertion':'All 202 frozen sources reproduce exact FIFO traces independently checked branch by branch; four literal Lean exports match inputs; independent coefficient-enumeration on exhaustive small source family; corrupted traces rejected.',
       'bounds':data['bounds']},envinfo))
    print(json.dumps({'status':'PASS','modules':len(mods),'new_modules':len(NEW),'declarations':len(decls),'python_counts':data['counts']},indent=2))
if __name__=='__main__':main()
