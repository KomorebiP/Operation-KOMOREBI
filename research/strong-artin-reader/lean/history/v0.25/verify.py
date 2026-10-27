#!/usr/bin/env python3
"""Replay the exact direct source closure in bounded, resumable batches.
No network access or unobserved background process is used.
"""
from __future__ import annotations
import argparse,hashlib,json,os,re,shutil,subprocess,sys,time,zipfile
from pathlib import Path
H=lambda b:hashlib.sha256(b).hexdigest()
ALLOWED={'propext','Classical.choice','Quot.sound'}

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--kit',type=Path,required=True)
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--max-modules',type=int,default=5)
    ap.add_argument('--timeout',type=int,default=80)
    a=ap.parse_args()
    if min(a.max_modules,a.timeout)<1:ap.error('positive limits required')
    root=Path(__file__).resolve().parent; kit=a.kit.resolve()
    mf=json.loads((root/'MANIFEST.json').read_text())
    lean=kit/'toolchain/bin/lean'; ws=kit/'workspace'
    version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ws/'.lake/packages/mathlib',text=True).strip()
    if mf['lean'] not in version or rev!=mf['mathlib']:raise RuntimeError('version mismatch')
    for b,h in mf['bases'].items():
        if H((root/'base'/b).read_bytes())!=h:raise RuntimeError('base hash mismatch: '+b)
    src={}
    for m in mf['dependency_modules']:
        x=mf['dependency_sources'][m]; p=root/'dependencies'/f'{m}.lean'
        with zipfile.ZipFile(root/'base'/x['archive']) as z:b=z.read(x['member'])
        if H(b)!=x['sha256'] or b!=p.read_bytes():raise RuntimeError('dependency mismatch: '+m)
        src[m]=p
    for x in mf['new_sources']:
        p=root/'src'/f"{x['module']}.lean"
        if H(p.read_bytes())!=x['sha256']:raise RuntimeError('source changed: '+str(p))
        src[x['module']]=p
    src['AxiomAudit']=root/'AxiomAudit.lean'
    if H(src['AxiomAudit'].read_bytes())!=mf['audit_sha256']:raise RuntimeError('audit changed')
    for m,p in src.items():
        t=p.read_text()
        if re.search(r'\b(sorry|admit)\b',t) or re.search(r'^\s*(?:(?:public|unsafe)\s+)*(?:axiom|opaque)\b',t,re.M):
            raise RuntimeError('prohibited source token: '+m)
    fresh=root/'verification/fresh'; stage=fresh/'src'; out=fresh/'olean'; logs=fresh/'logs'
    progress=fresh/'progress.json'
    modules=mf['dependency_modules']+mf['new_modules']+['AxiomAudit']
    if not a.resume:
        if fresh.exists():shutil.rmtree(fresh)
        for p in [stage,out,logs]:p.mkdir(parents=True,exist_ok=True)
        for m,p in src.items():shutil.copyfile(p,stage/f'{m}.lean')
        evidence=[]
        (root/'RESULT.json').unlink(missing_ok=True)
    else:
        evidence=json.loads(progress.read_text())['module_results']
        for m,p in src.items():
            if p.read_bytes()!=(stage/f'{m}.lean').read_bytes():raise RuntimeError('resume source changed')
        for x in evidence:
            if H((out/f"{x['module']}.olean").read_bytes())!=x['object_sha256']:raise RuntimeError('object changed')
    lp=subprocess.check_output(['bash',str(kit/'run.sh'),'lake','env','printenv','LEAN_PATH'],cwd=ws,text=True).strip()
    env=os.environ.copy();env['PATH']=str(lean.parent)+':'+env.get('PATH','')
    env['LEAN_PATH']=str(out)+':'+str(stage)+':'+lp
    done={x['module'] for x in evidence};ran=0
    for m in modules:
        if m in done:continue
        if ran>=a.max_modules:break
        p=stage/f'{m}.lean';obj=out/f'{m}.olean'
        cmd=[str(lean),'-j1','-DwarningAsError=true','-R',str(stage),'-o',str(obj),str(p)]
        print('CHECK',m,flush=True);start=time.monotonic()
        try:
            r=subprocess.run(cmd,cwd=ws,env=env,capture_output=True,text=True,timeout=a.timeout)
            code=r.returncode;text=r.stdout+r.stderr
        except subprocess.TimeoutExpired as e:
            code=124;text=str(e.stdout or '')+'\nTIMEOUT'
        sec=time.monotonic()-start;(logs/f'{m}.log').write_text(text)
        axioms=set()
        for names in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',text,re.S):
            axioms.update(v.strip() for v in names.split(',') if v.strip())
        if code or 'sorryAx' in text or axioms-ALLOWED or not obj.exists():
            fail={'status':'FAILED','module':m,'returncode':code,'seconds':sec,'axioms':sorted(axioms),'output':text}
            (fresh/'FAILED.json').write_text(json.dumps(fail,indent=2)+'\n')
            print(text,flush=True);return code or 1
        rec={'module':m,'returncode':0,'source_sha256':H(p.read_bytes()),'object_sha256':H(obj.read_bytes()),'log_sha256':H(text.encode()),'seconds':round(sec,3),'axioms':sorted(axioms)}
        evidence.append(rec);done.add(m);ran+=1
        progress.write_text(json.dumps({'status':'INCOMPLETE','module_results':evidence},indent=2)+'\n')
        print('PASS',m,round(sec,2),'s',flush=True)
    if len(done)!=len(modules):
        print(f'INCOMPLETE: {len(done)}/{len(modules)} compiled. Resume with --resume.',flush=True);return 0
    audit=(logs/'AxiomAudit.log').read_text()
    count=len(re.findall('depends on axioms:',audit))+len(re.findall('does not depend on any axioms',audit))
    if count!=len(mf['declarations']):raise RuntimeError(f'audit count mismatch {count}')
    result={'checkpoint':mf['checkpoint'],'status':'PASS','verification_scope':'fresh source replay of seven unchanged direct dependencies, ten new modules and the all-new-constant axiom audit','lean':version,'mathlib':rev,'base_hashes':mf['bases'],'direct_dependencies':len(mf['dependency_modules']),'new_modules':len(mf['new_modules']),'source_modules_replayed':len(modules)-1,'audit_modules_replayed':1,'new_declarations':mf['new_declarations'],'new_source_lines':mf['new_source_lines'],'named_constants_axiom_audited':count,'all_exit_codes_zero':True,'axiom_dependencies':sorted(set().union(*(set(x['axioms']) for x in evidence))),'module_results':evidence,'open_boundaries':mf['open_boundaries']}
    (root/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    progress.write_text(json.dumps({'status':'PASS','module_results':evidence},indent=2)+'\n')
    print('PASS: complete fresh replay; all '+str(count)+' named new constants audited.',flush=True)
    return 0

if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:
        print('VERIFICATION ERROR:',type(e).__name__,str(e),file=sys.stderr);sys.exit(1)
