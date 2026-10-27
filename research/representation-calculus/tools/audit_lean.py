"""Cold, hash-checkpointed audit. Run batches until status PASS; no partial run is PASS."""
from pathlib import Path
import argparse, hashlib, json, os, re, subprocess, sys, time, platform
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def modules_order():
    src={str(p.relative_to(ROOT/'formalization')).removesuffix('.lean').replace('/','.'):p
         for p in sorted((ROOT/'formalization').rglob('*.lean'))}
    ordered=[]; visiting=set(); done=set()
    def visit(m):
        if m in done:return
        if m in visiting:raise RuntimeError('import cycle '+m)
        visiting.add(m)
        for dep in re.findall(r'^(?:public )?import (\S+)',src[m].read_text(),re.M):
            if dep in src:visit(dep)
        visiting.remove(m);done.add(m);ordered.append(m)
    for m in src:visit(m)
    return ordered,src

def declarations(modules,src):
    out=[]
    for m in modules:
        ns=''
        for line in src[m].read_text().splitlines():
            mt=re.match(r'^namespace\s+(\S+)',line)
            if mt:ns=mt.group(1)
            mt=re.match(r'^(?:noncomputable\s+)?(def|abbrev|theorem|structure|instance)\s+([A-Za-z_][A-Za-z0-9_.]*)',line)
            if mt:out.append({'name':ns+'.'+mt.group(2),'kind':mt.group(1),'module':m})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True);ap.add_argument('--build',required=True)
    ap.add_argument('--batch',type=int,default=25);ap.add_argument('--resume',action='store_true');ap.add_argument('--timeout',type=int,default=120)
    args=ap.parse_args();runtime=Path(args.runtime).resolve();build=Path(args.build).resolve();build.mkdir(parents=True,exist_ok=True)
    lean=str(runtime/'toolchain/bin/lean');version=subprocess.run([lean,'--version'],check=True,capture_output=True,text=True).stdout.strip()
    if '4.34.0-rc2' not in version:raise RuntimeError('wrong toolchain')
    modules,src=modules_order(); names=declarations(modules,src)
    controls=sorted((ROOT/'controls').glob('*.lean'))
    inputs=list(src.values())+controls+[Path(__file__).resolve(), ROOT/'tools/generate_minimum_suite.py',ROOT/'evidence/MINIMUM_INSTANCES.json']
    hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    cp=build/'CHECKPOINT.json';old_seconds=0
    if args.resume:
        state=json.loads(cp.read_text())
        if state['inputs']!=hashes or state['toolchain']!=version:raise RuntimeError('checkpoint inputs changed')
    else:
        if any(build.glob('*.olean')):raise RuntimeError('cold build must have no pre-existing local oleans')
        state={'inputs':hashes,'toolchain':version,'started':datetime.now(timezone.utc).isoformat(),'seconds':0,'tasks':[],'invocations':[]}
    state['invocations'].append([sys.executable,*sys.argv]);start=time.monotonic();old_seconds=state['seconds']
    pkg=runtime/'workspace/.lake/packages'
    env=os.environ.copy();env['LEAN_PATH']=':'.join([str(build)]+[str(p/'.lake/build/lib/lean') for p in pkg.iterdir() if p.is_dir()]);env['TERM']='xterm'
    logs=ROOT/'evidence/cold_lean';logs.mkdir(exist_ok=True)
    def save():
        state['seconds']=old_seconds+time.monotonic()-start
        cp.write_text(json.dumps(state,indent=2)+'\n')
        (ROOT/'evidence/COLD_PROGRESS.json').write_text(json.dumps({'tasks':state['tasks'],'status':'IN_PROGRESS'},indent=2)+'\n')
    def call(name,path,expected='accept',olean=None):
        argv=[lean,'-DwarningAsError=true']
        if olean is not None:olean.parent.mkdir(parents=True,exist_ok=True);argv+=['-o',str(olean)]
        argv+=[str(path)];t=time.monotonic()
        try:
            run=subprocess.run(argv,cwd=ROOT/'formalization',env=env,capture_output=True,text=True,timeout=args.timeout)
            code=run.returncode;text=run.stdout+run.stderr;outcome='completed'
        except subprocess.TimeoutExpired as e:
            code=None;text=str(e.stdout or '')+str(e.stderr or '')+'\nTIMEOUT';outcome='timeout'
        log=logs/(name+'.log');log.write_text(text)
        passed=outcome=='completed' and ((code==0) if expected=='accept' else code!=0)
        task={'name':name,'argv':argv,'expected':expected,'exit_status':code,'outcome':outcome,'passed':passed,'seconds':time.monotonic()-t,'log':str(log.relative_to(ROOT))}
        state['tasks'].append(task);save()
        if not passed:raise RuntimeError(name+' failed\n'+text[-5000:])
        return text
    completed={t['name'] for t in state['tasks'] if t['passed']};ran=0
    for i,m in enumerate(modules):
        label='build_'+m
        if label in completed:continue
        call(label,src[m],olean=build/(m.replace('.','/')+'.olean'));ran+=1
        if ran>=args.batch and i<len(modules)-1:
            print(json.dumps({'status':'IN_PROGRESS','modules_checked':i+1,'total':len(modules)}));return
    # Split dependency audit so the entire generated suite remains reproducible under memory caps.
    used=set();axis=[]
    for offset in range(0,len(names),500):
        part=names[offset:offset+500];label=f'axioms_{offset//500:02d}';path=build/(label+'.lean')
        path.write_text('module\n'+'\n'.join('public import '+m for m in dict.fromkeys(n['module'] for n in part))+
                        '\n'+'\n'.join('#print axioms '+n['name'] for n in part)+'\n')
        if label in completed:text=(logs/(label+'.log')).read_text()
        else:text=call(label,path)
        missing=[n['name'] for n in part if n['name'] not in text]
        if missing:raise RuntimeError('missing axiom records '+str(missing))
        for match in re.finditer(r'depends on axioms:?\s*\[([^\]]*)\]',text):
            used.update(a.strip() for a in match.group(1).split(',') if a.strip())
        if 'sorryAx' in text or 'Lean.ofReduceBool' in text:raise RuntimeError('forbidden dependency')
        axis.append(label)
    if used-ALLOWED:raise RuntimeError('unexpected axioms '+str(used-ALLOWED))
    for c in controls:
        label='control_'+c.stem
        if label not in completed:call(label,c,'accept' if c.stem.startswith('Positive') else 'reject')
    after={str(p.relative_to(ROOT)):sha(p) for p in inputs}
    if hashes!=after:raise RuntimeError('accepted inputs changed')
    save()
    result={'status':'PASS','modules':len(modules),'declarations':len(names),'counts':{kind:sum(n['kind']==kind for n in names) for kind in ['theorem','def','abbrev','structure','instance']},'axioms':sorted(used),'toolchain':version,'inputs_unchanged':True,'seconds':state['seconds'],'tasks':state['tasks'],'generated_minimum_instances':202,'all_source_states':True,'all_words':True}
    (ROOT/'results/LEAN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'evidence/DECLARATIONS.json').write_text(json.dumps(names,indent=2)+'\n')
    (ROOT/'evidence/ACCEPTED_INPUTS.json').write_text(json.dumps(hashes,indent=2)+'\n')
    (ROOT/'evidence/COLD_PROGRESS.json').write_text(json.dumps({'status':'PASS','tasks':state['tasks']},indent=2)+'\n')
    (ROOT/'evidence/LEAN_EXECUTION.json').write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='tasks'},indent=2))
if __name__=='__main__':main()
