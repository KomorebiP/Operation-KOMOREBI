#!/usr/bin/env python3
"""Clean, single-threaded, pinned Lean replay of the Fitting continuation.
Only the thirteen listed modules are rebuilt. This does not rebuild all of Paper XII.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PIN = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
ALLOWED = {'propext','Classical.choice','Quot.sound'}
def sha(p: Path) -> str: return hashlib.sha256(p.read_bytes()).hexdigest()
def clean_comments(s: str) -> str:
    out=[]; depth=0; i=0
    while i<len(s):
        if s[i:i+2]=='/-': depth+=1; i+=2
        elif depth and s[i:i+2]=='-/': depth-=1; i+=2
        elif depth: i+=1
        elif s[i:i+2]=='--':
            j=s.find('\n',i); i=len(s) if j<0 else j
        else: out.append(s[i]); i+=1
    if depth: raise ValueError('Unterminated block comment')
    return ''.join(out)
def execute(cmd: list[str], env: dict[str,str], log: Path, timeout: int) -> dict:
    start=time.monotonic(); p=subprocess.Popen(cmd,cwd=ROOT/'lean',env=env,
        stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
    timed_out=False
    try: text,_=p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out=True; os.killpg(p.pid,signal.SIGKILL);text,_=p.communicate()
    log.write_text(text)
    return {'command':cmd,'exit_code':p.returncode,'timed_out':timed_out,
        'seconds':round(time.monotonic()-start,3),'log':str(log.relative_to(ROOT)),
        'log_sha256':sha(log)}
def main() -> int:
    parser=argparse.ArgumentParser();parser.add_argument('portable_kit',type=Path)
    parser.add_argument('--timeout',type=int,default=180);args=parser.parse_args()
    kit=args.portable_kit.resolve();lean=kit/'toolchain/bin/lean';ws=kit/'workspace'
    conf=json.loads((ROOT/'checks/modules.json').read_text());modules=conf['modules']
    env=os.environ.copy();env['MALLOC_ARENA_MAX']='2'
    env['LEAN_PATH']=os.pathsep.join(map(str,[ROOT/'build',ws/'.lake/build/lib/lean']+
        sorted((ws/'.lake/packages').glob('*/.lake/build/lib/lean'))))
    report={'status':'RUNNING','started_utc':datetime.now(timezone.utc).isoformat(),
      'verification_scope':'clean rebuild of ten new modules and three unchanged predecessor support modules; not a full cumulative paper rebuild',
      'modules':[],'axioms':[],'controls':[]}
    logs=ROOT/'logs';logs.mkdir(exist_ok=True)
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    try:
        if not lean.is_file():raise RuntimeError('Portable Lean executable not found')
        version=subprocess.check_output([str(lean),'--version'],env=env,text=True).strip()
        if '4.34.0-rc2' not in version:raise RuntimeError('Wrong Lean toolchain: '+version)
        ml=ws/'.lake/packages/mathlib'
        commit=subprocess.check_output(['git','-C',str(ml),'rev-parse','HEAD'],text=True).strip()
        if commit!=PIN:raise RuntimeError('Wrong Mathlib commit: '+commit)
        manifest=json.loads((ws/'lake-manifest.json').read_text())
        if next(p for p in manifest['packages'] if p['name']=='mathlib')['rev']!=PIN:
            raise RuntimeError('Wrong manifest pin')
        report.update(lean_version=version,compiler_sha256=sha(lean),mathlib_commit=commit,
            threads=1,warnings_as_errors=True,timeout_per_process=args.timeout)
        expected={m.replace('.','/')+'.lean' for m in modules}
        actual={str(p.relative_to(ROOT/'lean')) for p in (ROOT/'lean').rglob('*.lean')}
        if expected!=actual:raise RuntimeError('Production module manifest mismatch')
        inputs={s:sha(ROOT/'lean'/s) for s in sorted(expected)}
        report['source_hashes_before']=inputs
        shutil.rmtree(ROOT/'build',ignore_errors=True);(ROOT/'build/PaperXII').mkdir(parents=True)
        declarations=[];private_helpers=[]
        for mod in modules:
            rel=mod.replace('.','/');src=ROOT/'lean'/f'{rel}.lean';olean=ROOT/'build'/f'{rel}.olean'
            body=clean_comments(src.read_text())
            banned=re.findall(r'\b(?:sorry|admit|axiom|native_decide|unsafe)\b',body)
            if banned:raise RuntimeError(f'Forbidden production token in {mod}: {banned}')
            ns=re.search(r'^namespace\s+(\S+)',body,re.M).group(1)
            pat=r'^(?:@\[[^\]]*\]\s*)*(?:(private)\s+)?(?:noncomputable\s+)?(theorem|lemma|def|abbrev|structure|instance)\s+([\w.]+)'
            for private,kind,name in re.findall(pat,body,re.M):
                d={'name':ns+'.'+name,'kind':kind,'module':mod,'new':mod in conf['new_modules']}
                (private_helpers if private else declarations).append(d)
            result=execute([str(lean),'-j1','-DwarningAsError=true','-o',str(olean),str(src)],
                env,logs/(mod+'.log'),args.timeout)
            result.update(module=mod,source_sha256=sha(src))
            report['modules'].append(result)
            if result['exit_code'] or result['timed_out']:raise RuntimeError('Compile failed: '+mod)
            result['olean_sha256']=sha(olean)
            print('PASS '+mod,flush=True)
        audit=ROOT/'checks/AxiomAudit.lean'
        audit.write_text('\n'.join('import '+m for m in modules)+'\n\n'+
            '\n'.join('#print axioms '+d['name'] for d in declarations)+'\n')
        result=execute([str(lean),'-j1','-DwarningAsError=true',str(audit)],env,logs/'AxiomAudit.log',args.timeout)
        report['axiom_run']=result
        if result['exit_code'] or result['timed_out']:raise RuntimeError('Axiom audit failed')
        text=(logs/'AxiomAudit.log').read_text()
        for d in declarations:
            name=d['name'];match=re.search(re.escape("'"+name+"'")+r' depends on axioms:\s*\[([^\]]*)\]',text)
            if match: axioms=[a.strip() for a in match.group(1).split(',') if a.strip()]
            elif "'"+name+"' does not depend on any axioms" in text:axioms=[]
            else:raise RuntimeError('Missing axiom report: '+name)
            if set(axioms)-ALLOWED:raise RuntimeError('Unapproved axioms: '+name+str(axioms))
            report['axioms'].append(dict(d,axioms=axioms))
        print('PASS axioms '+str(len(declarations)),flush=True)
        for name,required in [('RejectFalse','Type mismatch'),('RejectPlaceholder','sorry'),
                              ('RejectWrongNormalization','unsolved goals')]:
            result=execute([str(lean),'-j1','-DwarningAsError=true',str(ROOT/'checks'/(name+'.lean'))],
                env,logs/(name+'.log'),args.timeout)
            text=(logs/(name+'.log')).read_text()
            result['name']=name;result['passed']=(result['exit_code']!=0 and not result['timed_out'] and required in text)
            report['controls'].append(result)
            if not result['passed']:raise RuntimeError('Invalid-proof control did not fail correctly: '+name)
            print('PASS rejected '+name,flush=True)
        after={s:sha(ROOT/'lean'/s) for s in sorted(expected)}
        if inputs!=after:raise RuntimeError('Source mutated during verification')
        report['source_hashes_after']=after
        new=[d for d in declarations if d['new']]
        report.update(status='PASS',declarations=declarations,private_helpers=private_helpers,
          new_theorem_declarations=sum(d['kind'] in ('theorem','lemma') for d in new),
          new_named_declarations=len(new),new_module_count=len(conf['new_modules']),
          replayed_predecessor_modules=len(conf['unchanged_predecessor']),
          audited_named_declarations=len(declarations),
          inherited_global_theorem_census_updated=False)
    except Exception as e:
        report['status']='FAIL';report['error']=str(e);print('FAIL '+str(e),flush=True)
    report['finished_utc']=datetime.now(timezone.utc).isoformat()
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
