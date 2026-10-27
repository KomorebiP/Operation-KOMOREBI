#!/usr/bin/env python3
"""Compile frozen sources, audit source-owned declarations, and replay the exact logical closure.

The default is a fresh compile of every production module. --base-fresh may reuse
only a successful, hash-bound fresh compilation from the current release work.
This uses Lean's official kernel and pinned upstream cache, not an independent kernel.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, signal, subprocess, time
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def scrub(s):
    out=[];i=0;depth=0;quoted=False
    while i<len(s):
        if depth:
            if s.startswith('/-',i):depth+=1;i+=2
            elif s.startswith('-/',i):depth-=1;i+=2
            else:
                if s[i]=='\n':out.append('\n')
                i+=1
        elif quoted:
            if s[i]=='\\':i+=2
            elif s[i]=='"':quoted=False;i+=1
            else:
                if s[i]=='\n':out.append('\n')
                i+=1
        elif s.startswith('/-',i):depth=1;i+=2
        elif s.startswith('--',i):
            e=s.find('\n',i);i=len(s) if e<0 else e
        elif s[i]=='"':quoted=True;i+=1
        else:out.append(s[i]);i+=1
    return ''.join(out)
def policy(p):
    s=scrub(p.read_text())
    for pat in [r'^\s*(?:axiom|opaque|unsafe|partial)\b',r'\b(?:sorry|admit|native_decide|implemented_by)\b',r'^\s*set_option\s+warningAsError\s+false',r'^\s*set_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true']:
        assert not re.search(pat,s,re.M),'Production policy failed: '+str(p)
    return s
def main():
    ap=argparse.ArgumentParser()
    for key in ('root','kit','out'):ap.add_argument('--'+key,type=Path,required=True)
    ap.add_argument('--manifest',type=Path);ap.add_argument('--base-fresh',type=Path);ap.add_argument('--boundary',type=Path)
    a=ap.parse_args();root=a.root.resolve();kit=a.kit.resolve();out=a.out.resolve();audit=Path(__file__).resolve().parent
    manifest=(a.manifest or root/'release_modules.json').resolve();rows=json.loads(manifest.read_text())
    assert rows and len({r['module'] for r in rows})==len(rows)
    if out.exists():raise SystemExit('Refusing existing output')
    upstream=[p for p in os.environ.get('LEAN_PATH','').split(os.pathsep) if '/workspace/.lake/packages/' in p or p.endswith('/toolchain/lib/lean')]
    assert any('/mathlib/' in p for p in upstream),'Use run.sh with the pinned Lake environment'
    out.mkdir(parents=True);obj=out/'objects';obj.mkdir();env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join([str(obj)]+upstream)
    flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
    report={'status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'manifest_sha256':sha(manifest),'checks':[],'source_files':[],'flags':flags,'lean_path':env['LEAN_PATH'],'limits':['Pinned upstream cache reused, not rebuilt.','Replay uses Lean own kernel, not an independent verifier.','Prose-to-theorem coverage remains a separate semantic audit.','The exact reviewed generated partial runtime helpers are inventoried separately and excluded from logical proof replay; the actual count is recorded below.']}
    started=time.monotonic()
    def save():(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    def run(label,args,*,reject=False,pattern=None,extra=None,cwd=None,timeout=1800):
        e=env.copy();e.update(extra or {});log=out/(label+'.log');t=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(args,cwd=cwd or root,env=e,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
        text=log.read_text(errors='replace');ok=(0<code<124) if reject else code==0
        if pattern:ok=ok and re.search(pattern,text,re.I) is not None
        report['checks'].append({'label':label,'command':args,'cwd':str(cwd or root),'exit':code,'expected':'nonzero' if reject else 'zero','passed':ok,'required_pattern':pattern,'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':sha(log),'environment_additions':extra or {}});save();print(('PASS ' if ok else 'FAIL ')+label,flush=True)
        if not ok:raise RuntimeError(label)
        return text
    def lean(label,source,target=None,warning=True,**kw):
        fl=flags.copy()
        if not warning:fl[1]='-DwarningAsError=false'
        args=['lean',*fl]
        if target:target.parent.mkdir(parents=True,exist_ok=True);args+=['-o',str(target)]
        return run(label,args+[str(source)],**kw)
    def owned_parse(text):
        rr=[json.loads(x[6:]) for x in text.splitlines() if x.startswith('OWNED ')]
        hit=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text)
        assert hit and len(rr)==int(hit.group(1)) and len(rr)==len({r['name'] for r in rr})
        return rr
    save()
    try:
        frozen=out/'execution_inputs';shutil.copytree(audit,frozen/'audit',ignore=shutil.ignore_patterns('__pycache__'));shutil.copy2(manifest,frozen/'release_modules.json')
        report['audit_inputs']=[{'path':str(p.relative_to(audit)),'sha256':sha(p)} for p in sorted(audit.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
        helper_review=json.loads((audit/'reviewed_runtime_helpers.json').read_text())
        assert helper_review['status']=='REVIEWED'
        reviewed_helpers=helper_review['helpers'];reviewed_names={h['name'] for h in reviewed_helpers}
        assert len(reviewed_names)==len(reviewed_helpers)==helper_review['helper_count']
        template_text=(audit/'OwnedAudit.template.lean').read_text()
        whitelist_text=re.search(r'let generatedRuntime : Array Name := (#\[[^\n]*\])',template_text).group(1)
        assert set(re.findall(r'`([\w.]+)',whitelist_text))==reviewed_names
        manifest_modules={r['module'] for r in rows}
        for item in helper_review['source_modules']:
            if item['module'] in manifest_modules:assert sha(root/item['source'])==item['sha256'],item['module']
        for item in helper_review['evidence']:assert sha(audit/item['path'])==item['sha256'],item['path']
        report['reviewed_runtime_helpers_receipt_sha256']=sha(audit/'reviewed_runtime_helpers.json')
        report['reviewed_runtime_helper_count']=len(reviewed_names)
        binding=json.loads((audit/'runtime_bindings.json').read_text())
        for row in binding['files']:assert sha(kit/row['path'])==row['sha256'],row['path']
        report['runtime_files_authenticated']=len(binding['files'])
        version=run('lean_version',['lean','--version']).strip();assert version==binding['lean_version'];report['lean_version']=version
        report['dependencies']=[]
        for row in binding['dependencies']:
            rev=run('pin_'+row['name'],['git','-C',str(kit/'workspace/.lake/packages'/row['name']),'rev-parse','HEAD']).strip();assert rev==row['rev'];report['dependencies'].append({'name':row['name'],'rev':rev})
        reuse={}
        if a.base_fresh:
            bpath=a.base_fresh.resolve();b=json.loads((bpath/'verification.json').read_text());assert b['status']=='PASS';assert b['flags']==flags
            embedded=frozen/'prior_compilation';embedded.mkdir()
            shutil.copy2(bpath/'verification.json',embedded/'verification.json')
            if b.get('schema')=='paper-i-successful-compilation-component/1':
                parent=json.loads((bpath/'parent_verification.json').read_text())
                assert sha(bpath/'parent_verification.json')==b['parent_audit']['sha256']
                assert parent['status']==b['parent_audit']['status']=='FAIL'
                assert parent['failure']==b['parent_audit']['failure']=='owned_audit'
                original_sources={r['module']:r for r in parent['source_files']}
                original_checks={r['label']:r for r in parent['checks']}
                for r in b['modules']:
                    old=original_sources[r['module']];check=original_checks['compile_'+r['module'].replace('.','_')]
                    assert check['passed'] and check['exit']==0
                    assert old['source_sha256']==r['source_sha256'] and old['object_sha256']==r['object_sha256']
                    assert check['command']==r['command'] and check['log_sha256']==r['log_sha256']
                shutil.copy2(bpath/'parent_verification.json',embedded/'parent_verification.json')
                shutil.copy2(bpath/'parent_owned_audit.log',embedded/'parent_owned_audit.log')
            for row in b['modules']:
                assert row['passed'] and row['exit']==0
                assert sha(bpath/row['log'])==row['log_sha256']
                shutil.copy2(bpath/row['log'],embedded/row['log'])
                assert sha(bpath/row['object'])==row['object_sha256'];assert sha(bpath/'source_snapshots'/row['source'])==row['source_sha256']
                reuse[row['module']]=row
            report['prior_fresh_compile_report']={'path':str(bpath/'verification.json'),'sha256':sha(bpath/'verification.json'),'module_count':len(reuse),'scope':b.get('scope'),'component_schema':b.get('schema'),'parent_audit':b.get('parent_audit'),'embedded_record':str((embedded/'verification.json').relative_to(out))}
            assert len(reuse)==b.get('fresh_production_module_count',len(reuse))
        empties=[]
        for row in rows:
            module=row['module'];rel=Path(*module.split('.'));src=(root/rel).with_suffix('.lean');assert sha(src)==row['source_sha256'],module
            clean=policy(src)
            if not re.search(r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|protected|scoped)\s+)*(?:def|abbrev|theorem|lemma|instance|structure|inductive)\s+',clean,re.M):empties.append(module)
            snap=(out/'source_snapshots'/rel).with_suffix('.lean');snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,snap)
            target=(obj/rel).with_suffix('.olean');target.parent.mkdir(parents=True,exist_ok=True)
            if module in reuse:
                rr=reuse[module];assert rr['source_sha256']==row['source_sha256'];shutil.copy2(bpath/rr['object'],target);origin='authenticated_current_release_fresh_compile'
            else:
                lean('compile_'+module.replace('.','_'),src,target=target);origin='fresh_compile'
            assert sha(src)==row['source_sha256']
            report['source_files'].append({'module':module,'source':str(src.relative_to(root)),'source_sha256':sha(src),'object':str(target.relative_to(out)),'object_sha256':sha(target),'origin':origin});save()
        mods=[r['module'] for r in rows];report['production_module_count']=len(mods)
        if a.boundary:
            src=a.boundary.resolve();policy(src);module=src.stem;assert module not in mods
            snap=out/'source_snapshots'/src.name;shutil.copy2(src,snap);target=obj/(module+'.olean')
            lean('boundary_consumers',src,target=target,cwd=src.parent);mods.append(module)
            report['boundary']={'module':module,'source_sha256':sha(src),'object_sha256':sha(target)}
        templ=(audit/'OwnedAudit.template.lean').read_text()
        arr=lambda xs:'#['+', '.join('`'+x for x in xs)+']'
        source=templ.replace('__IMPORTS__','\n'.join('import '+m for m in mods)).replace('__MODULES__',arr(mods)).replace('__EMPTY_MODULES__',arr(empties))
        ownedfile=out/'OwnedAudit.lean';ownedfile.write_text(source)
        owned=owned_parse(lean('owned_audit',ownedfile,pattern=r'OWNED_AUDIT_PASS \d+'))
        expected_runtime_names={h['name'] for h in reviewed_helpers if h['module'] in mods}
        actual_runtime_names={r['name'] for r in owned if r['runtime_only']}
        assert actual_runtime_names==expected_runtime_names,{'unexpected_runtime':sorted(actual_runtime_names-expected_runtime_names),'missing_reviewed_runtime':sorted(expected_runtime_names-actual_runtime_names)}
        report['runtime_exact_reviewed_name_match']=True
        (out/'owned_declarations.json').write_text(json.dumps(owned,indent=2)+'\n');report.update(owned_total=len(owned),owned_logical_total=sum(not r['runtime_only'] for r in owned),owned_runtime_only=sum(r['runtime_only'] for r in owned),axioms=sorted({ax for r in owned for ax in r['axioms']}));save()
        for name in ['InjectedAxiom','InjectedPlaceholder','ForeignClean']:
            lean('compile_control_'+name,audit/'fixtures'/(name+'.lean'),target=obj/(name+'.olean'),cwd=audit/'fixtures',warning=name!='InjectedPlaceholder')
            lean('guard_'+name,audit/'fixtures'/(name+'Audit.lean'),cwd=audit/'fixtures',reject=name!='ForeignClean',pattern='OWNED_AUDIT_PASS' if name=='ForeignClean' else 'OWNED AUDIT REJECTED')
        for name,pat in [('FalseEquality','unsolved goals|type mismatch|Tactic.*rfl.*failed'),('Placeholder','declaration uses.*sorry'),('MissingFinite','failed to synthesize'),('MissingSemisimple','failed to synthesize'),('MissingPositive','type mismatch|unsolved goals'),('WrongCeiling','type mismatch'),('WrongProductSum','type mismatch'),('WrongCoefficientOrder','type mismatch')]:
            lean('negative_'+name,audit/'negative'/(name+'.lean'),reject=True,pattern=pat)
        text=lean('kernel_corrupt_control',audit/'ReplayClosure.lean',reject=True,pattern=r'kernel.*type mismatch|declaration type mismatch|type mismatch',extra={'KOMOREBI_REPLAY_MODULES':'ForeignClean','KOMOREBI_REPLAY_CORRUPT':'1'})
        assert 'REPLAY_CORRUPT_CONTROL_INJECTED' in text and 'REPLAY_CLOSURE_PASS' not in text
        text=lean('replay_whole_closure',audit/'ReplayClosure.lean',pattern=r'REPLAY_CLOSURE_PASS MODULES '+str(len(mods))+r' CONSTANTS \d+',extra={'KOMOREBI_REPLAY_MODULES':','.join(mods),'KOMOREBI_REPLAY_CORRUPT':'0'})
        replayed=[json.loads(x[len('REPLAY_CHECKED '):]) for x in text.splitlines() if x.startswith('REPLAY_CHECKED ')]
        runtime=[json.loads(x[len('REPLAY_RUNTIME_ONLY '):]) for x in text.splitlines() if x.startswith('REPLAY_RUNTIME_ONLY ')]
        expected={x['name'] for x in owned if not x['runtime_only']};actual={x['name'] for x in replayed}
        assert actual==expected and len(replayed)==len(actual),{'missing':sorted(expected-actual),'extra':sorted(actual-expected)}
        assert {x['name'] for x in runtime}=={x['name'] for x in owned if x['runtime_only']}
        assert 'REPLAY_UPSTREAM_ONLY_PASS' in text
        for name,items in [('replayed_constants',replayed),('runtime_only_constants',runtime)]:
            (out/(name+'.json')).write_text(json.dumps(items,indent=2)+'\n')
        report.update(replay_exact_name_match=True,replay_starting_environment_excludes_project_modules=True,replay_logical_constant_count=len(replayed),replay_runtime_only_count=len(runtime),replay_modules=mods,negative_controls=11)
        for row in report['source_files']:
            assert sha(root/row['source'])==row['source_sha256'];assert sha(out/row['object'])==row['object_sha256']
        if a.boundary:assert sha(a.boundary.resolve())==report['boundary']['source_sha256']
        assert sha(manifest)==report['manifest_sha256']
        for row in report['audit_inputs']:assert sha(audit/row['path'])==row['sha256']
        report.update(status='PASS',elapsed_seconds=round(time.monotonic()-started,3),finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));save();print('PAPER_I_RELEASE_AUDIT_PASS');return 0
    except Exception as exc:
        report.update(status='FAIL',failure=str(exc),elapsed_seconds=round(time.monotonic()-started,3));save();raise
if __name__=='__main__':raise SystemExit(main())
