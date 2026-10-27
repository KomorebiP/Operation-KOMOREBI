#!/usr/bin/env python3
"""Cleanly verify the shipped focused dependency closure, with no network access.

The pinned portable Lean/mathlib runtime is external. Each invocation creates a
new build directory and compiles every supplied source module, not only changes.
"""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,pathlib,re,subprocess,sys,time

ROOT=pathlib.Path(__file__).resolve().parents[1]
ALLOWED={'propext','Classical.choice','Quot.sound'}
PIN='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'

def sha(p:pathlib.Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=pathlib.Path,required=True)
    ap.add_argument('--audit-dir',default='audit/clean_current')
    ap.add_argument('--build-name',default='clean_current')
    ap.add_argument('--timeout',type=int,default=150)
    args=ap.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.build_name):ap.error('Unsafe build-name')
    runtime=args.runtime.resolve();binary=runtime/'toolchain/bin/lean'
    packages=runtime/'workspace/.lake/packages'
    audit=(ROOT/args.audit_dir).resolve()
    if not audit.is_relative_to(ROOT):ap.error('Audit directory must be inside project')
    build=ROOT/'.lake'/args.build_name/'lib/lean'
    if build.exists():ap.error('Use a new build-name; reusing compiled project output is forbidden')
    audit.mkdir(parents=True,exist_ok=True);build.mkdir(parents=True)
    env=dict(os.environ)
    deps=sorted(q/'.lake/build/lib/lean' for q in packages.iterdir()
                if (q/'.lake/build/lib/lean').is_dir())
    env['LEAN_PATH']=':'.join(map(str,[build]+deps))
    env['PATH']=str(runtime/'toolchain/bin')+os.pathsep+env.get('PATH','')
    sources=list(sorted((ROOT/'KomorebiSpace').glob('*.lean')))+[ROOT/'KomorebiSpace.lean']
    before={str(p.relative_to(ROOT)):sha(p) for p in sources}
    report={'schema':'komorebi-focused-lean-verification-v1','status':'RUNNING',
      'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'scope':'All 11 supplied production modules and root, not the entire historical cumulative repository',
      'commands':[], 'source_sha256_before':before,
      'trust_boundary':['Pinned compiler/kernel and imported mathlib cache are trusted, not rebuilt.',
                       'Lexical declaration inventory is not an independent Lean parser.']}
    t0=time.monotonic()
    def run(label:str,argv:list[str])->subprocess.CompletedProcess:
        t=time.monotonic();dest=audit/(label+'.log')
        try:
            with dest.open('w') as log:
                r=subprocess.run(argv,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,
                                 timeout=args.timeout)
        except subprocess.TimeoutExpired:
            report['commands'].append({'label':label,'argv':argv,'exit_status':None,
                'timeout_seconds':args.timeout,'log':str(dest.relative_to(ROOT))})
            raise RuntimeError('Timeout: '+label)
        report['commands'].append({'label':label,'argv':argv,'exit_status':r.returncode,
           'elapsed_seconds':time.monotonic()-t,'log':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
        print(label,r.returncode,round(time.monotonic()-t,2),flush=True)
        return r
    def good(label:str,argv:list[str])->None:
        r=run(label,argv)
        if r.returncode:raise RuntimeError(label+' failed; see retained log')
    try:
        version=subprocess.check_output([str(binary),'--version'],text=True).strip()
        if '4.34.0-rc2' not in version:raise RuntimeError('Wrong Lean version')
        pin=subprocess.check_output(['git','-C',str(packages/'mathlib'),'rev-parse','HEAD'],text=True).strip()
        if pin!=PIN:raise RuntimeError('Wrong mathlib commit')
        report['runtime']={'lean_version':version,'lean_sha256':sha(binary),'mathlib_commit':pin,
                           'python':sys.version,'platform':sys.platform}
        inherited=json.loads((ROOT/'audit/INHERITED_SOURCES.json').read_text())
        if any(before[name]!=v['sha256'] for name,v in inherited.items()):
            raise RuntimeError('Inherited source hash mismatch')
        def strip_comments(text:str)->str:
            out=[];i=0;depth=0
            while i<len(text):
                if text[i:i+2]=='/-':depth+=1;i+=2
                elif depth and text[i:i+2]=='-/':depth-=1;i+=2
                elif depth:i+=1
                elif text[i:i+2]=='--':
                    e=text.find('\n',i);i=len(text) if e<0 else e
                else:out.append(text[i]);i+=1
            return ''.join(out)
        for f in sources:
            if re.search(r'\b(sorry|admit|axiom|native_decide)\b',strip_comments(f.read_text())):
                raise RuntimeError('Forbidden production source token: '+str(f))
        seen=set();order=[]
        def visit(mod:str)->None:
            if mod in seen:return
            seen.add(mod);path=ROOT/(mod.replace('.','/')+'.lean')
            if not path.exists():raise RuntimeError('Missing supplied source: '+str(path))
            for dep in re.findall(r'^import\s+(KomorebiSpace\.\w+)',path.read_text(),re.M):visit(dep)
            order.append(mod)
        visit('KomorebiSpace')
        if len(order)!=len(sources):raise RuntimeError('A shipped module is outside import closure')
        flags=[str(binary),'-j1','-DwarningAsError=true','-DautoImplicit=false']
        for mod in order:
            path=ROOT/(mod.replace('.','/')+'.lean');out=build/(mod.replace('.','/')+'.olean')
            out.parent.mkdir(parents=True,exist_ok=True)
            good('compile_'+mod.split('.')[-1],flags+['-o',str(out),str(path)])
        ds=json.loads((ROOT/'audit/declaration_index.json').read_text())
        # Axiom requests are part of the shipped source; demand exact inventory.
        for stem,subset in [('AxiomAudit',[d for d in ds if d['kind']=='theorem']),
                            ('ConstructionAudit',[d for d in ds if d['kind']!='theorem'])]:
            request=ROOT/'checks'/(stem+'.lean')
            expected={d['name'] for d in subset}
            if set(re.findall(r'^#print axioms (\S+)',request.read_text(),re.M))!=expected:
                raise RuntimeError('Axiom-request inventory mismatch')
            good(stem,flags+[str(request)])
            text=(audit/(stem+'.log')).read_text();records={}
            for n,b in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",text,re.S):
                records[n]=[a.strip() for a in b.split(',') if a.strip()]
            for n in re.findall(r"'([^']+)' does not depend on any axioms",text):records[n]=[]
            if set(records)!=expected:raise RuntimeError('Axiom output missing/extra declarations')
            observed=set(a for vals in records.values() for a in vals)
            if not observed<=ALLOWED:raise RuntimeError('Unexpected axioms: '+str(observed-ALLOWED))
            report[stem]={'declarations':len(records),'observed_axioms':sorted(observed)}
        for name in ['FalseStatement','Placeholder','ForgedKernelEquality','ForgedProjectionTransport','ForgedClosedRadius']:
            result=run('negative_'+name,flags+[str(ROOT/'tests/negative'/(name+'.lean'))])
            if result.returncode==0:raise RuntimeError('Negative control accepted: '+name)
            if name.startswith('Forged'):
                neg=(audit/('negative_'+name+'.log')).read_text()
                if 'unsolved goals' not in neg and 'Tactic' not in neg:
                    raise RuntimeError('New negative control did not reach a proof goal: '+name)
                if 'does not exist' in neg or 'Unknown identifier' in neg:
                    raise RuntimeError('New negative control failed on infrastructure: '+name)
        good('negative_AxiomInjection',flags+[str(ROOT/'tests/negative/AxiomInjection.lean')])
        injected=(audit/'negative_AxiomInjection.log').read_text()
        if 'projectAssumption' not in injected and 'injected' not in injected.lower():
            # Require at least one custom axiom in a printed dependency list.
            found=re.findall(r'depends on axioms: \[([^\]]*)\]',injected,re.S)
            custom={a.strip() for b in found for a in b.split(',')}-ALLOWED-{''}
            if not custom:raise RuntimeError('Custom-axiom negative control not detected')
        after={str(p.relative_to(ROOT)):sha(p) for p in sources}
        if before!=after:raise RuntimeError('Sources changed during verification')
        report['source_sha256_after']=after
        report['compiled_sha256']={str(p.relative_to(build)):sha(p) for p in sorted(build.rglob('*.olean'))}
        report['modules']=order
        report['inherited_source_count']=len(inherited)
        report['status']='PASS'
    except Exception as exc:
        report['status']='FAIL';report['failure']=str(exc)
    report['elapsed_seconds']=time.monotonic()-t0
    report['finished_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (audit/'VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],report.get('failure',''),flush=True)
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
