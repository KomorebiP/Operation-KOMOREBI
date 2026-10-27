#!/usr/bin/env python3
"""One-worker, bounded fresh verification of the immutable canonical H12 sources.
Builds into a new temporary directory, never into the historical source trees.
Std-only current block needs no mathlib. For the full selected-source replay,
use the pinned mathlib checkout with its compiled cache available.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,subprocess,hashlib,json,re,os,time,tempfile,platform,resource
ROOT=Path(__file__).resolve().parent
VERSION='4.34.0-rc2'
COMMIT='6a10ac8c22beadecabdbb0919c2b50214762f91d'
MATHLIB='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
ALLOWED={'propext','Classical.choice','Quot.sound'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def clean_code(s):
    # Nested block-comment removal; strings are left intact for admission scan.
    out=[];i=0;depth=0
    while i<len(s):
        if s[i:i+2]=='/-':depth+=1;i+=2
        elif depth and s[i:i+2]=='-/':depth-=1;i+=2
        elif depth:i+=1
        elif s[i:i+2]=='--':
            j=s.find('\n',i);i=len(s) if j<0 else j
        else:out.append(s[i]);i+=1
    return ''.join(out)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lean',type=Path,required=True)
    ap.add_argument('--mathlib',type=Path);ap.add_argument('--scope',choices=['current','all'],default='current')
    ap.add_argument('--timeout',type=int,default=120);ap.add_argument('--memory-mib',type=int,default=1536)
    ap.add_argument('--log-dir',type=Path);ap.add_argument('--audit-strategy',choices=['module','aggregate','source','auto'],default='auto');ap.add_argument('--only',nargs='+');a=ap.parse_args()
    assert 20<=a.timeout<=600 and 512<=a.memory_mib<=4096
    lean=a.lean.resolve();env=os.environ.copy()
    version=subprocess.check_output([str(lean),'--version'],env=env,text=True).strip()
    assert VERSION in version and COMMIT in version,version
    mathpaths=[]
    if a.scope=='all':
        assert a.mathlib is not None,'--mathlib with pinned cache is required for full replay'
        ml=a.mathlib.resolve()
        rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ml,text=True).strip()
        assert rev==MATHLIB,rev
        mathpaths=[ml/'.lake/build/lib/lean']+[p/'.lake/build/lib/lean' for p in (ml/'.lake/packages').iterdir() if p.is_dir()]
    source_map=json.loads((ROOT/'SOURCE_MODULE_MAP.json').read_text())
    bymod={r['module']:r for r in source_map}
    modules=json.loads((ROOT/'MODULE_ORDER.json').read_text()) if a.scope=='all' else ['H12PrincipalDivisor','H12CubicDivisorGrowth']
    if a.only:
        assert set(a.only)<=set(modules),a.only
        chosen=set(a.only)
        while True:
            before=set(chosen)
            chosen.update(x for m in before for x in bymod[m]['imports'] if x in bymod)
            if before==chosen:break
        modules=[m for m in modules if m in chosen]
    inventory=json.loads((ROOT/'DECLARATION_INVENTORY.json').read_text())
    theorems=[r for r in inventory if r['kind'] in ['theorem','lemma'] and r['module'] in modules]
    names=[r['name'] for r in theorems];assert len(names)==len(set(names))
    inputs={m+'.lean':sha(ROOT/(m+'.lean')) for m in modules}
    for m in modules:
        code=clean_code((ROOT/(m+'.lean')).read_text())
        assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b',code),m
        assert inputs[m+'.lean']==bymod[m]['sha256'],m
    logdir=(a.log_dir or ROOT/'verification'/a.scope).resolve();logdir.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat();tic=time.monotonic();checks=[]
    # Lean heap bound plus wall/CPU bounds. OS memory limits are not imposed:
    # shared-library virtual mappings are larger than the Lean heap budget.
    def cpu_cap():resource.setrlimit(resource.RLIMIT_CPU,(a.timeout,a.timeout+2))
    with tempfile.TemporaryDirectory(prefix='h12-fresh-') as tmp:
        build=Path(tmp)
        for m in modules:(build/(m+'.lean')).write_bytes((ROOT/(m+'.lean')).read_bytes())
        env['LEAN_PATH']=':'.join(map(str,[build]+mathpaths))
        env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
        success=set()
        def run(mod,expected=0,timeout=None,emit=True):
            cmd=[str(lean),'-j1',f'-M{a.memory_mib}','-DwarningAsError=true']
            if emit:cmd+=['-o',mod+'.olean']
            cmd+=[mod+'.lean'];tm=time.monotonic()
            logfile=logdir/(mod+'.log')
            # wait4 supplies this child's actual kernel peak RSS and CPU usage,
            # unlike cumulative RUSAGE_CHILDREN accounting.
            with logfile.open('w') as capture:
                proc=subprocess.Popen(cmd,cwd=build,env=env,stdout=capture,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,preexec_fn=cpu_cap)
                deadline=tm+(timeout or a.timeout);timed_out=False
                while True:
                    pid,raw,usage=os.wait4(proc.pid,os.WNOHANG)
                    if pid:break
                    if time.monotonic()>deadline:
                        timed_out=True;proc.kill();pid,raw,usage=os.wait4(proc.pid,0);break
                    time.sleep(0.05)
                code=os.waitstatus_to_exitcode(raw);proc.returncode=code
                status='TIMEOUT' if timed_out else code
            out=logfile.read_text()
            rec={'module':mod,'argv':cmd,'cwd':str(build),'exit_status':status,'expected_exit':expected,'seconds':time.monotonic()-tm,'user_cpu_seconds':usage.ru_utime,'system_cpu_seconds':usage.ru_stime,'peak_rss_kib':usage.ru_maxrss,'peak_rss_method':'POSIX wait4 child rusage; Linux KiB','log':str(logfile.relative_to(ROOT)) if logfile.is_relative_to(ROOT) else str(logfile),'log_sha256':sha(logfile)}
            checks.append(rec);print(mod,status,round(rec['seconds'],3),flush=True)
            return status,out
        for m in modules:
            deps={x for x in bymod[m]['imports'] if x in bymod}
            if not deps<=success:
                checks.append({'module':m,'exit_status':'BLOCKED','missing_dependencies':sorted(deps-success)})
                continue
            status,out=run(m)
            if status==0:success.add(m)
        selected=[r for r in theorems if r['module'] in success]
        audited={};audit_ok=True;combined_status='NOT_RUN_MODULE_STRATEGY'
        strategies=[('AuditFresh',list(success),selected)] if a.scope=='current' or a.audit_strategy=='aggregate' else [
            ('Audit_'+m,[m],[r for r in selected if r['module']==m]) for m in modules if m in success]
        all_audit=[]
        for auditor,imports,entries in strategies:
            commands='\n'+''.join('#check '+r['name']+'\n#print axioms '+r['name']+'\n' for r in entries)
            if a.scope=='all' and (a.audit_strategy=='source' or (a.audit_strategy=='auto' and imports==['H12PhaseRegulator'])):
                assert len(imports)==1
                original=(ROOT/(imports[0]+'.lean')).read_bytes()
                audit_bytes=original+commands.encode()
                assert sha(ROOT/(imports[0]+'.lean'))==hashlib.sha256(audit_bytes[:len(original)]).hexdigest()
                (build/(auditor+'.lean')).write_bytes(audit_bytes);(logdir/(auditor+'.lean')).write_bytes(audit_bytes)
                relation={'module':imports[0],'original_prefix_bytes':len(original),'original_sha256':hashlib.sha256(original).hexdigest(),'prefix_sha256':hashlib.sha256(audit_bytes[:len(original)]).hexdigest(),'auditor_sha256':hashlib.sha256(audit_bytes).hexdigest(),'appended_commands':commands,'relation':'auditor bytes = exact original source bytes + declared UTF-8 #check/#print commands; no import of its own compiled module'}
                (logdir/(auditor+'_PREFIX_RELATION.json')).write_text(json.dumps(relation,indent=2)+'\n')
            else:
                audit=''.join('import '+m+'\n' for m in imports)+commands
                (build/(auditor+'.lean')).write_text(audit);(logdir/(auditor+'.lean')).write_text(audit)
            audit_status,audit_out=run(auditor)
            all_audit.append('-- '+auditor+'\n'+audit_out)
            found=re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]",audit_out)+[(n,'') for n in re.findall(r"'([^']+)' does not depend on any axioms",audit_out)]
            part={n:{d.strip() for d in deps.split(',') if d.strip()} for n,deps in found}
            audit_ok &= audit_status==0 and set(part)=={r['name'] for r in entries} and all(v<=ALLOWED for v in part.values())
            assert not set(audited)&set(part)
            audited.update(part)
        (logdir/'AxiomAudit_AllModules.log').write_text('\n'.join(all_audit))
        if a.scope=='current' or a.audit_strategy=='aggregate':
            (build/'Combined.lean').write_text(''.join('import '+m+'\n' for m in modules if m in success))
            combined_status,_=run('Combined')
        audit_ok &= set(audited)=={r['name'] for r in selected}
        (build/'PositiveControl.lean').write_text('import Std\nexample : (2 : Int)+3=5 := by decide\n')
        pos_status,_=run('PositiveControl',emit=False,timeout=20)
        (build/'FalseControl.lean').write_text('import Std\nexample : (0 : Int)=1 := by decide\n')
        neg_status,neg_out=run('FalseControl',expected='nonzero',emit=False,timeout=20)
    post={name:sha(ROOT/name) for name in inputs};assert post==inputs
    controls_ok=pos_status==0 and isinstance(neg_status,int) and neg_status!=0 and 'error' in neg_out
    passed=len(success)==len(modules) and audit_ok and combined_status in [0,'NOT_RUN_MODULE_STRATEGY'] and controls_ok
    result={'status':'PASS' if passed else 'INCOMPLETE','scope':a.scope,'audit_strategy':a.audit_strategy if a.scope=='all' else 'aggregate-current-only','module_selection':a.only or 'all modules in scope','combined_import_status':combined_status,'verifier_sha256':sha(Path(__file__)),'started_at_utc':started,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'runtime_seconds':time.monotonic()-tic,'lean_version':version,'lean_binary_sha256':sha(lean),'mathlib_revision':MATHLIB if a.scope=='all' else None,'dependencies':'bundled Std only' if a.scope=='current' else 'pinned Mathlib and bundled Std','source_hashes_before':inputs,'source_hashes_after':post,'inputs_unchanged':post==inputs,'module_count':len(modules),'modules_compiled':sorted(success),'compiled_module_count':len(success),'selected_unique_theorem_count':len(names),'freshly_audited_theorem_count':len(audited),'axiom_audit_passed':audit_ok,'axiom_dependencies':{n:sorted(v) for n,v in audited.items()},'axiom_union':sorted(set().union(*audited.values())) if audited else [],'sorryAx':any('sorryAx' in v for v in audited.values()),'custom_axioms':any(not v<=ALLOWED for v in audited.values()),'controls_passed':controls_ok,'negative_control_exit_status':neg_status,'resource_caps':{'lean_workers':1,'lean_heap_mib':a.memory_mib,'per_process_wall_seconds':a.timeout,'per_process_cpu_seconds':a.timeout,'numerical_library_thread_caps':1,'os_address_space_cap':'not imposed'},'checks':checks,'environment':platform.platform(),'compiler_adapter':'LD_PRELOAD present' if env.get('LD_PRELOAD') else 'none','nonclaims':'No gamma equality, complex divisor order, canonical-product convergence, analytic counting, CM realization or class-field comparison is inferred from this compiler run.'}
    (logdir/'BUILD_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],len(audited),'fresh unique theorem audits',flush=True)
    raise SystemExit(0 if passed else 1)
if __name__=='__main__':main()
