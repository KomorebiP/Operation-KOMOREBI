#!/usr/bin/env python3
"""Bounded fresh source replay for v0.29. Reuses ONLY the pinned portable Mathlib cache."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time, zipfile
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

BASE_NAME='Strong_Artin_Lean_v0.28.0_Continuous_Local_Gluing_Checked.zip'
BASE_ROOT='Strong_Artin_Lean_v0.28.0_Continuous_Local_Gluing'
BASE_SHA='35043bbef695875f2f1316a2313dadab77d7b23ab5a28660c3bd735ae673d5f0'
MATHLIB='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
LEAN_COMMIT='6a10ac8c22beadecabdbb0919c2b50214762f91d'
ALLOWED={'propext','Classical.choice','Quot.sound'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def code_only(text):
    out=[];i=0;depth=0
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;out.extend('  ');i+=2
            elif text.startswith('-/',i):depth-=1;out.extend('  ');i+=2
            else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        elif text.startswith('/-',i):depth=1;out.extend('  ');i+=2
        elif text.startswith('--',i):
            while i<len(text) and text[i]!='\n':out.append(' ');i+=1
        elif text[i]=='"':
            out.append(' ');i+=1
            while i<len(text):
                if text[i]=='\\':out.extend('  ');i+=2
                elif text[i]=='"':out.append(' ');i+=1;break
                else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        else:out.append(text[i]);i+=1
    if depth:raise RuntimeError('Unclosed comment')
    return ''.join(out)
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kit',required=True,type=Path)
    ap.add_argument('--timeout',type=int,default=90)
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--max-modules',type=int)
    args=ap.parse_args()
    root=Path(__file__).resolve().parent;kit=args.kit.resolve();ws=kit/'workspace';lean=kit/'toolchain/bin/lean'
    version=subprocess.check_output([str(lean),'--version'],text=True).strip()
    if '4.34.0-rc2' not in version or LEAN_COMMIT not in version:raise RuntimeError('Incorrect Lean version')
    rev=subprocess.check_output(['git','-C',str(ws/'.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()
    if rev!=MATHLIB:raise RuntimeError('Incorrect Mathlib revision')
    base=root/'base'/BASE_NAME
    if sha(base)!=BASE_SHA:raise RuntimeError('Incorrect base archive')
    modules=json.loads((root/'MODULES.json').read_text())
    decls=json.loads((root/'DECLARATIONS.json').read_text())
    with zipfile.ZipFile(base) as z:
        if z.testzip() is not None:raise RuntimeError('Corrupt base ZIP')
        for m in modules['dependency_modules']:
            candidates=[f'{BASE_ROOT}/{kind}/{m}.lean' for kind in ['src','dependencies']]
            n=next((n for n in candidates if n in z.namelist()),None)
            if n is None or z.read(n)!=(root/'dependencies'/f'{m}.lean').read_bytes():raise RuntimeError('Changed dependency '+m)
    paths={m:root/'dependencies'/f'{m}.lean' for m in modules['dependency_modules']}
    paths.update({m:root/'src'/f'{m}.lean' for m in modules['new_modules']})
    audit=modules['audit_module'];paths[audit]=root/'audit'/f'{audit}.lean'
    counts=Counter();bad=[]
    for m,p in paths.items():
        text=code_only(p.read_text())
        if m!=audit:
            hits=re.findall(r'\b(?:sorry|admit|axiom|opaque|native_decide|unsafe)\b',text)
            if hits:bad.append({'module':m,'markers':hits})
        if m in modules['new_modules']:
            counts.update(re.findall(r'(?m)^\s*(?:@\[[^\n]*\]\s*)?(?:(?:noncomputable|private|protected|public)\s+)*(theorem|lemma|def|abbrev|structure)\s+',text))
    if bad:raise RuntimeError('Prohibited code markers '+str(bad))
    if counts!=Counter(d['kind'] for d in decls):raise RuntimeError('Declaration inventory mismatch')
    hashes={m:sha(p) for m,p in paths.items()};out=root/'verification/fresh';result=root/'RESULT.json'
    records=[]
    if args.resume:
        prev=json.loads(result.read_text())
        if prev['source_hashes']!=hashes:raise RuntimeError('Sources changed; cannot resume')
        records=prev['module_results']
        for rec in records:
            obj=root/rec['object_file']
            if rec['returncode']!=0 or not obj.exists() or sha(obj)!=rec['object_sha256']:raise RuntimeError('Stale/failed prior object')
    elif out.exists():shutil.rmtree(out)
    for d in ['src','olean','logs']:(out/d).mkdir(parents=True,exist_ok=True)
    for p in paths.values():shutil.copy2(p,out/'src'/p.name)
    lp=subprocess.check_output(['bash',str(kit/'run.sh'),'lake','env','printenv','LEAN_PATH'],cwd=ws,text=True).strip()
    env=os.environ.copy();env['LEAN_PATH']=str(out/'olean')+':'+str(out/'src')+':'+lp
    env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
    manifest={'checkpoint':'Strong Artin v0.29 — Continuous Local Gauge Obstruction',
        'status':'IN_PROGRESS','verification_scope':'fresh direct source closure; pinned Mathlib cache reused',
        'lean':version,'mathlib':rev,'base_archive':BASE_NAME,'base_sha256':BASE_SHA,
        'dependency_sources_unchanged':True,'dependency_modules':len(modules['dependency_modules']),
        'new_modules':len(modules['new_modules']),'source_modules':len(paths)-1,'audit_modules':1,
        'additive_declarations':dict(counts),'named_constants_audited':len(decls),
        'new_source_lines':sum(len(paths[m].read_text().splitlines()) for m in modules['new_modules']),
        'anonymous_local_instances':sum(len(re.findall(r'(?m)^local instance',paths[m].read_text())) for m in modules['new_modules']),
        'source_hashes':hashes,'module_results':records,'prohibited_active_source_occurrences':bad,
        'warning_as_error':True,'cohomology_convention':'explicit continuous inhomogeneous cochains, including independent local C0 gauge terms',
        'nonclaims':['no general vanishing of the constructed class','no identification with a homogeneous/derived API or arithmetic Selmer complex',
            'no full coefficient-tower theorem','no automorphic carrier or Strong Artin conclusion','not an independent kernel or all-historical replay']}
    def save():
        manifest['last_observed_utc']=datetime.now(timezone.utc).isoformat()
        result.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
    done={rec['module'] for rec in records};n=0;save()
    for m,p in paths.items():
        if m in done:continue
        if args.max_modules is not None and n>=args.max_modules:
            manifest['status']='PARTIAL';save();print('PARTIAL: requested batch completed');return 0
        obj=out/'olean'/f'{m}.olean';log=out/'logs'/f'{m}.log'
        cmd=[str(lean),'-j1','-DwarningAsError=true','-R',str(out/'src'),'-o',str(obj),str(out/'src'/p.name)]
        started=time.monotonic()
        try:
            proc=subprocess.run(cmd,cwd=ws,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=args.timeout)
            rc=proc.returncode;text=proc.stdout
        except subprocess.TimeoutExpired as e:
            rc=124;text=e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout or ''
        log.write_text(text)
        rec={'module':m,'source_sha256':hashes[m],'command':cmd,'returncode':rc,'seconds':time.monotonic()-started,
            'log':str(log.relative_to(root)),'log_sha256':sha(log),'object_file':str(obj.relative_to(root)),
            'object_sha256':sha(obj) if obj.exists() else None,'sorryAx':'sorryAx' in text}
        records.append(rec);save();print(m,'RC',rc,'s',round(rec['seconds'],2),flush=True)
        if rc!=0 or rec['sorryAx']:
            manifest['status']='FAIL';save();print(text);return 1
        n+=1
    text=(out/'logs'/f'{audit}.log').read_text()
    reports=re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]",text,re.S)
    noaxioms=re.findall(r"'([^']+)' does not depend on any axioms",text)
    reported={name for name,_ in reports}|set(noaxioms)
    missing={d['name'] for d in decls}-reported
    axioms={a.strip() for _,chunk in reports for a in chunk.split(',') if a.strip()}
    if missing or not axioms<=ALLOWED:
        manifest['status']='FAIL';manifest['missing_axiom_reports']=sorted(missing);manifest['axiom_dependencies']=sorted(axioms);save()
        raise RuntimeError('Missing/disallowed axiom reports')
    manifest['axiom_dependencies']=sorted(axioms);manifest['all_exit_codes_zero']=True;manifest['status']='PASS';save()
    print('PASS:',len(paths)-1,'source modules + axiom audit;',len(decls),'named constants')
    return 0
if __name__=='__main__':
    try:sys.exit(main())
    except Exception as e:print('FAILED:',e,file=sys.stderr);sys.exit(1)
