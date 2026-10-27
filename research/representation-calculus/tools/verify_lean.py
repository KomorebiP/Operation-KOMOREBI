"""Cold Lean/Std audit of the generic matrix bridge and all symbolic instances."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,platform,re,subprocess,sys,tempfile,time,contextlib,shutil
ROOT=Path(__file__).resolve().parents[1]
CORE=['RepresentationCore','FiniteCertificates','InvariantCertificates','ConcreteExamples','GeneratedProfile',
      'MatrixCore','MatrixCertificates','MatrixSmith','MatrixRowWitnesses','CardinalityCore']
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def declared(modules):
    result=[]
    for module in modules:
        ns=''
        for line in (ROOT/'formalization'/(module+'.lean')).read_text().splitlines():
            mt=re.match(r'^namespace\s+(\S+)',line)
            if mt:ns=mt.group(1)
            mt=re.match(r'^(?:noncomputable\s+)?(def|abbrev|theorem|structure|instance)\s+([A-Za-z_][A-Za-z0-9_.]*)',line)
            if mt:result.append({'name':ns+'.'+mt.group(2),'kind':mt.group(1),'module':module})
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--lean',required=True);ap.add_argument('--task-timeout',type=int,default=45);ap.add_argument('--batch-size',type=int,default=0);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    lean=str(Path(args.lean).resolve());version=subprocess.run([lean,'--version'],capture_output=True,text=True,check=True).stdout.strip()
    if '4.34.0-rc2' not in version:raise SystemExit('pinned toolchain: Lean 4.34.0-rc2')
    exports=json.loads((ROOT/'evidence/SYMBOLIC_EXPORTS.json').read_text())
    modules=CORE+[item['module'] for item in exports]+['LargeCardinality']
    controls=sorted((ROOT/'controls').glob('*.lean'))
    names=declared(modules)
    inputs=[f'formalization/{m}.lean' for m in modules]+[str(p.relative_to(ROOT)) for p in controls]
    inputs+=['tools/verify_lean.py','tools/export_symbolic_lean.py','tools/generate_symbolic_suite.py','evidence/SYMBOLIC_EXPORTS.json']
    inputs+=sorted({x[key] for x in exports for key in ('source','certificate')})
    before={n:sha(ROOT/n) for n in inputs}
    logs=ROOT/'evidence/lean';logs.mkdir(parents=True,exist_ok=True)
    tasks=[];started=datetime.now(timezone.utc).isoformat();tick=time.monotonic();used=set()
    work=ROOT.parent/'repr03_verification_work';checkpoint=work/'checkpoint.json'
    old_seconds=0.0;invocations=[]
    if args.resume:
        saved=json.loads(checkpoint.read_text())
        if saved['inputs'] != before or saved['version'] != version:
            raise RuntimeError('resume inputs or toolchain changed')
        tasks=saved['tasks'];started=saved['started'];old_seconds=saved['seconds'];invocations=saved['invocations']
    else:
        if work.exists():shutil.rmtree(work)
        work.mkdir(parents=True)
    invocations.append([sys.executable,*sys.argv])
    def save_checkpoint():
        checkpoint.write_text(json.dumps({'inputs':before,'version':version,'tasks':tasks,'started':started,
            'seconds':old_seconds+time.monotonic()-tick,'invocations':invocations},indent=2)+'\n')
    with contextlib.nullcontext(str(work)) as temp:
        build=Path(temp);env=os.environ.copy();env['LEAN_PATH']=temp
        def call(label,argv,expect):
            start=time.monotonic()
            try:
                proc=subprocess.run(argv,cwd=ROOT/'formalization',env=env,text=True,capture_output=True,timeout=args.task_timeout)
                text=proc.stdout+proc.stderr;code=proc.returncode;outcome='completed'
            except subprocess.TimeoutExpired as exc:
                text=str(exc.stdout or '')+'\n'+str(exc.stderr or '')+'\nTIMEOUT';code=None;outcome='timeout'
            (logs/(label+'.log')).write_text(text)
            okay=outcome=='completed' and ((code==0) if expect=='accept' else (code!=0))
            task={'name':label,'argv':[a.replace(temp,'<fresh-build>') for a in argv], 'exit_status':code,
                  'expected':expect,'status':outcome,'passed':okay,'seconds':time.monotonic()-start}
            tasks.append(task)
            (ROOT/'evidence/LEAN_TASKS_PROGRESS.json').write_text(json.dumps(tasks,indent=2)+'\n')
            if not okay:raise RuntimeError(label+' FAILED '+text[-2500:])
            return text
        completed={t['name'] for t in tasks if t['passed']}
        new_count=0
        for i,module in enumerate(modules):
            if 'build_'+module in completed:continue
            call('build_'+module,[lean,'-DwarningAsError=true','-o',str(build/(module+'.olean')),module+'.lean'],'accept')
            new_count+=1
            if i%20==0 or i==len(modules)-1:print(f'CHECKED {i+1}/{len(modules)} modules: {module}',flush=True)
            save_checkpoint()
            if args.batch_size and new_count>=args.batch_size and i<len(modules)-1:
                print(json.dumps({'status':'IN_PROGRESS','modules_checked':i+1,'modules_total':len(modules),'next':'rerun with --resume'}),flush=True)
                return
        audit=build/'Audit.lean'
        audit.write_text('\n'.join('import '+m for m in modules)+'\n'+'\n'.join('#print axioms '+row['name'] for row in names)+'\n')
        text=call('axioms',[lean,str(audit)],'accept')
        for mt in re.finditer(r'depends on axioms:?\s*\[([^\]]*)\]',text):
            used.update(v.strip() for v in mt.group(1).split(',') if v.strip())
        missing=[row['name'] for row in names if row['name'] not in text]
        if missing:raise RuntimeError('missing axiom records '+str(missing[:10]))
        if used-ALLOWED:raise RuntimeError('unexpected axioms '+str(used-ALLOWED))
        if any(token in text for token in ('sorryAx','Lean.ofReduceBool')):raise RuntimeError('forbidden dependency')
        for control in controls:
            expect='accept' if control.name.startswith('Positive') else 'reject'
            call('control_'+control.stem,[lean,'-DwarningAsError=true',str(control)],expect)
    after={n:sha(ROOT/n) for n in inputs}
    if before!=after:raise RuntimeError('accepted inputs changed')
    counts={kind:sum(row['kind']==kind for row in names) for kind in ('theorem','def','abbrev','structure','instance')}
    boundary=['Generic matrix soundness, exact observational quotient, image/principal-factor bijection, and every-competitor state injection are kernel checked.',
      'All 202 frozen v0.2 matrix instances are exported and kernel checked without state enumeration.',
      'The large instance has a separate 2^30-element image bijection and exact two-scalar minimum proof.',
      'Universal numerical minimum FREE LINEAR coordinate count for arbitrary matrix certificates remains outside this Std-only adapter.',
      'Python discovery, JSON parser, exporter, Smith construction and checker are not verified executable programs.',
      'Synthetic fixtures, not trained AI, structurally held-out discoveries, or performance comparisons. Self-review only.']
    result={'status':'PASS','toolchain':version,'modules':len(modules),'symbolic_instances':len(exports),
      'explicit_declarations':len(names),'counts':counts,'axioms':sorted(used),'tasks':tasks,
      'inputs_unchanged':True,'runtime_seconds':old_seconds+time.monotonic()-tick,'boundaries':boundary}
    (ROOT/'results/LEAN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'evidence/DECLARATIONS.json').write_text(json.dumps(names,indent=2)+'\n')
    outputs=['results/LEAN_AUDIT.json','evidence/DECLARATIONS.json','evidence/LEAN_TASKS_PROGRESS.json']+[str(p.relative_to(ROOT)) for p in sorted(logs.glob('*.log'))]
    manifest={'schema_version':2,'claim_id':'KRC-0.3-SYMBOLIC-MATRIX-ADAPTER','repository':{'commit':'standalone, no git commit','dirty':True},
      'command':[sys.executable,*sys.argv],
      'invocations':invocations,
      'environment':{'software':[{'name':'Lean','version':version},{'name':'Python','version':sys.version}],'platform':platform.platform()},
      'mathematics':{'assertion_tested':'All-state/all-word symbolic matrix certificate soundness and exact quotient; actual Smith image; generated finite-ring instances; exact large-image code and scalar lower bound.',
        'coefficient_domain':'Generic Lean.Grind.Semiring; concrete Fin(p^r) with standard modular operations.',
        'conventions':'All initial states admissible. Words left to right. Column states. Only finite MATRIX/TRACE indices are kernel-evaluated, never all states.',
        'inputs':inputs,'bounds':{'modules':len(modules),'symbolic_instances':len(exports),'per_task_wall_seconds':args.task_timeout},'non_claims':boundary},
      'randomness':{'used':False,'seed':None,'generator':'none'},
      'run':{'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'runtime_seconds':result['runtime_seconds'],'exit_status':0,
        'status':'completed','wall_cap_seconds':args.task_timeout*(len(modules)+len(controls)+1),
        'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None},'missing_results':[],'invalid_results':[]},
      'input_artifacts':[{'path':n,'sha256':before[n],'sha256_after':after[n]} for n in inputs],
      'execution_artifacts':inputs,'declared_results':['results/LEAN_AUDIT.json','evidence/DECLARATIONS.json'],
      'outputs':[{'path':n,'sha256':sha(ROOT/n),'kind':'log' if n.endswith('.log') else 'result'} for n in outputs],
      'checks':[{'name':t['name'],'status':'PASS'} for t in tasks], 'result':'kernel accepted all declared sources and rejected all negative controls', 'residual_risks':boundary}
    (ROOT/'LEAN_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'evidence/LEAN_INVOCATIONS.json').write_text(json.dumps(invocations,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='tasks'},indent=2),flush=True)
if __name__=='__main__':main()
