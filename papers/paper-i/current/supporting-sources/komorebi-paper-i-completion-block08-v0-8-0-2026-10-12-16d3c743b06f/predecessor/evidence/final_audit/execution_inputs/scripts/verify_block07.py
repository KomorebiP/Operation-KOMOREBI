#!/usr/bin/env python3
"""Fresh additions, authenticated predecessor and upstream-only whole-project replay.
Uses the pinned official Lean kernel, not an independent verifier.
Every process has an observed exit and preserved log. No failed run yields PASS.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, os, re, shutil, signal, subprocess, time
from pathlib import Path

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def scrub(text: str) -> str:
    out=[];i=0;depth=0;quoted=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;i+=2
            elif text.startswith('-/',i):depth-=1;i+=2
            else:
                if text[i]=='\n':out.append('\n')
                i+=1
        elif quoted:
            if text[i]=='\\':i+=2
            elif text[i]=='"':quoted=False;i+=1
            else:
                if text[i]=='\n':out.append('\n')
                i+=1
        elif text.startswith('/-',i):depth=1;i+=2
        elif text.startswith('--',i):
            e=text.find('\n',i);i=len(text) if e<0 else e
        elif text[i]=='"':quoted=True;i+=1
        else:out.append(text[i]);i+=1
    return ''.join(out)

def main() -> int:
    ap=argparse.ArgumentParser()
    for n in ('root','kit','out'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();root=a.root.resolve();kit=a.kit.resolve();out=a.out.resolve();pred=root/'predecessor'
    if out.exists():raise SystemExit('Refusing existing output directory')
    upstream=[]
    for part in os.environ.get('LEAN_PATH','').split(os.pathsep):
        p=Path(part).resolve()
        if str(p).startswith(str(kit/'workspace/.lake/packages')+os.sep) or p==kit/'toolchain/lib/lean':
            upstream.append(str(p))
    if not any('/mathlib/' in p for p in upstream):raise SystemExit('Use the pinned Lake environment')
    out.mkdir(parents=True)
    obj=out/'objects';inherited=out/'inherited_objects';tobj=out/'test_objects';ctrl=out/'control_objects'
    for p in (obj,inherited,tobj,ctrl):p.mkdir()
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join([str(obj),str(inherited)]+upstream)
    flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
    newmods=['PaperICompletion7.Nakayama','PaperICompletion7.ModuleTop','PaperICompletion7.LocalResidue','PaperICompletion7']
    report={'schema':'paper-i-block07-audit/0.7.0','status':'RUNNING',
      'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':[],'source_files':[],'flags':flags,
      'scope':'Fresh new modules and new boundary module; authenticated unchanged predecessor; exact-name-matched whole-closure replay from an upstream-only starting environment.',
      'limits':['The 42 predecessor sources are authenticated against accepted objects, not freshly recompiled in this run.',
        'Pinned upstream Mathlib cache reused, not rebuilt or fully replayed.',
        'Replay uses Lean\'s own kernel, not an independent verifier.',
        'Compiler-generated unsafe/partial runtime implementation constants are recorded separately and excluded from proof replay, as in official replay.',
        'Publication mapping is semantic review, not kernel parsing of prose.',
        'Constructions are mathematical, noncomputable objects, not an executable decomposition algorithm.']}
    started=time.monotonic()
    def save():(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    def run(label,args,*,cwd=None,reject=False,pattern=None,extra=None,timeout=1200):
        en=env.copy();en.update(extra or {});log=out/(label+'.log');t=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(args,cwd=cwd or root,env=en,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
        text=log.read_text(errors='replace');ok=(0<code<124) if reject else code==0
        if pattern:ok=ok and re.search(pattern,text,re.I) is not None
        report['checks'].append({'label':label,'command':args,'cwd':str(cwd or root),
          'expected_exit':'nonzero' if reject else 'zero','actual_exit':code,'passed':ok,
          'required_pattern':pattern,'seconds':round(time.monotonic()-t,3),'log':log.name,
          'log_sha256':sha(log),'environment_additions':extra or {}})
        save();print(('PASS ' if ok else 'FAIL ')+label,flush=True)
        if not ok:raise RuntimeError(label+' failed')
        return text
    def lean(label,source,*,target=None,cwd=None,reject=False,pattern=None,extra=None,warning=True):
        fl=flags.copy()
        if not warning:fl[1]='-DwarningAsError=false'
        args=['lean',*fl]
        if target:target.parent.mkdir(parents=True,exist_ok=True);args+=['-o',str(target)]
        return run(label,args+[str(source)],cwd=cwd or source.parent,reject=reject,pattern=pattern,extra=extra)
    def check_manifest():
        m=json.loads((pred/'MANIFEST_SHA256.json').read_text());assert m['count']==len(m['files'])
        for row in m['files']:
            p=pred/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],row['path']
        return len(m['files'])
    def source_policy(source):
        clean=scrub(source.read_text())
        pats=[r'^\s*(?:axiom|opaque|unsafe|partial)\b',r'\b(?:sorry|admit|native_decide|implemented_by)\b',
          r'^\s*set_option\s+warningAsError\s+false',r'^\s*set_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true']
        assert not any(re.search(p,clean,re.M) for p in pats),'Forbidden production source '+str(source)
        return clean
    def parse_owned(text):
        owned=[json.loads(l[6:]) for l in text.splitlines() if l.startswith('OWNED ')]
        hit=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text)
        assert hit and int(hit.group(1))==len(owned) and len({r['name'] for r in owned})==len(owned)
        return owned,int(hit.group(2))
    save()
    try:
        inputs=sorted([*list((root/'source/extension').rglob('*.lean')),*list((root/'tests').rglob('*.lean')),
          root/'scripts/verify_block07.py',root/'scripts/run_block07.sh'])
        report['frozen_inputs']=[]
        for ip in inputs:
            rel=ip.relative_to(root);t=out/'execution_inputs'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ip,t)
            report['frozen_inputs'].append({'path':str(rel),'sha256':sha(ip)})
        report['predecessor_payloads_authenticated']=check_manifest()
        oldtop=json.loads((pred/'VERIFICATION.json').read_text());assert oldtop['status']=='PASS'
        accepted=oldtop['accepted_run'];assert sha(pred/accepted['path'])==accepted['sha256']
        report['predecessor_verification_sha256']=sha(pred/'VERIFICATION.json')
        stage=(pred/accepted['path']).parent;b=json.loads((pred/accepted['path']).read_text());assert b['status']=='PASS'
        for row in b['source_files']:
            source=pred/row['source'];oldobj=stage/row['object']
            assert sha(source)==row['source_sha256'] and sha(oldobj)==row['object_sha256']
            source_policy(source)
            rel=Path(*row['module'].split('.'));target=(inherited/rel).with_suffix('.olean')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(oldobj,target)
            snap=(out/'source_snapshots'/rel).with_suffix('.lean');snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snap)
            report['source_files'].append({'module':row['module'],'source':str(source.relative_to(root)),
              'source_sha256':sha(source),'source_lines':len(source.read_text().splitlines()),
              'object':str(target.relative_to(out)),'object_sha256':sha(target),'origin':'authenticated_predecessor'})
        assert len(report['source_files'])==42 and len({r['module'] for r in report['source_files']})==42
        report['predecessor_module_pairs_authenticated']=42;save()
        bindings=list(pred.rglob('runtime_bindings.json'));assert len(bindings)==1
        binding=json.loads(bindings[0].read_text())
        for row in binding['files']:assert sha(kit/row['path'])==row['sha256'],row['path']
        report['runtime_files_authenticated']=len(binding['files']);report['runtime_archive_sha256']=binding['kit_archive_sha256']
        version=run('lean_version',['lean','--version']).strip();assert version==binding['lean_version'];report['lean_version']=version
        report['dependencies']=[]
        for row in binding['dependencies']:
            rev=run('pin_'+row['name'],['git','-C',str(kit/'workspace/.lake/packages'/row['name']),'rev-parse','HEAD']).strip()
            assert rev==row['rev']
            report['dependencies'].append({'name':row['name'],'expected_revision':row['rev'],'actual_revision':rev})
        public=[]
        for module in newmods:
            rel=Path(*module.split('.')).with_suffix('.lean');source=root/'source/extension'/rel;clean=source_policy(source)
            ns=re.search(r'^namespace ([\w.]+)',clean,re.M)
            if ns:
                for m in re.finditer(r'^(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|protected)\s+)*(def|abbrev|theorem|lemma|instance|structure)\s+([\w.\']+)',clean,re.M):
                    public.append({'name':ns.group(1)+'.'+m.group(2),'source_kind':m.group(1),'module':module,'line':clean.count('\n',0,m.start())+1})
            h=sha(source);target=(obj/rel).with_suffix('.olean');snap=out/'source_snapshots'/rel
            snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snap)
            lean('compile_'+module.replace('.','_'),source,target=target,cwd=root/'source/extension');assert sha(source)==h
            report['source_files'].append({'module':module,'source':str(source.relative_to(root)),
              'source_sha256':h,'source_lines':len(source.read_text().splitlines()),'object':str(target.relative_to(out)),
              'object_sha256':sha(target),'origin':'fresh_compile'});save()
        report['fresh_new_production_modules']=len(newmods);public.sort(key=lambda x:x['name'])
        (out/'public_declarations.json').write_text(json.dumps(public,indent=2)+'\n')
        report['new_public_count']=len(public);report['new_public_kind_counts']=dict(collections.Counter(r['source_kind'] for r in public))
        previous=set(re.findall(r"^#check\s+([\w.']+)",(pred/'evidence/final_audit/DeclarationTypes.lean').read_text(),re.M))
        assert len(previous)==oldtop['resolved_public_or_coverage_names']
        upstream_coverage={'IsSemisimpleRing.isSemisimpleModule'}
        names=sorted(previous|{r['name'] for r in public}|upstream_coverage);types=out/'DeclarationTypes.lean'
        types.write_text('import PaperICompletion7\n'+''.join(f'#check {n}\n#print axioms {n}\n' for n in names)+'#eval IO.println "BLOCK07_TYPES_PASS"\n')
        lean('declaration_types_and_axioms',types,pattern='BLOCK07_TYPES_PASS');report['declaration_names_resolved']=len(names)
        report['new_upstream_coverage_names']=sorted(upstream_coverage-previous)
        proof_types=out/'NewPublicTypes.lean';proof_types.write_text('import PaperICompletion7\n'+''.join(f'#print {r["name"]}\n' for r in public))
        lean('new_public_full_types',proof_types)
        text=lean('source_owned_audit',root/'tests/OwnedBlock07Audit.lean',pattern=r'OWNED_AUDIT_PASS \d+')
        owned,outside=parse_owned(text)
        assert {r['name'] for r in public}<={r['name'] for r in owned if r['module'] in newmods}
        (out/'owned_declarations.json').write_text(json.dumps(owned,indent=2)+'\n')
        report['owned_total']=len(owned);report['owned_new']=sum(r['module'] in newmods for r in owned)
        report['owned_runtime_only']=sum(r['runtime_only'] for r in owned)
        report['owned_logical_total']=sum(not r['runtime_only'] for r in owned)
        report['axioms']=sorted({ax for r in owned for ax in r['axioms']});report['outside_project_namespace']=outside;save()
        tenv={'LEAN_PATH':os.pathsep.join([str(tobj),env['LEAN_PATH']])}
        test=root/'tests/BoundaryConsumers.lean'
        lean('boundary_consumers',test,target=tobj/'BoundaryConsumers.olean',cwd=root/'tests',extra=tenv)
        bnames=['PaperIBlock07Tests.'+m.group(1) for m in re.finditer(r'^theorem ([\w\']+)',scrub(test.read_text()),re.M)]
        report['new_boundary_assertions']=len(bnames)
        bt=lean('boundary_owned_audit',root/'tests/OwnedBoundaryAudit.lean',extra=tenv,pattern=r'OWNED_AUDIT_PASS \d+')
        bowned,_=parse_owned(bt);assert set(bnames)<={r['name'] for r in bowned}
        (out/'boundary_owned_declarations.json').write_text(json.dumps(bowned,indent=2)+'\n')
        report['boundary_owned_total']=len(bowned)
        report['boundary_object_sha256']=sha(tobj/'BoundaryConsumers.olean')
        cenv={'LEAN_PATH':os.pathsep.join([str(ctrl),env['LEAN_PATH']])}
        for name in ['InjectedAxiom','InjectedPlaceholder','ForeignClean']:
            lean('compile_control_'+name,root/'tests/fixtures'/(name+'.lean'),target=ctrl/(name+'.olean'),cwd=root/'tests/fixtures',extra=cenv,warning=name!='InjectedPlaceholder')
            lean('guard_'+name,root/'tests/fixtures'/(name+'Audit.lean'),extra=cenv,reject=name!='ForeignClean',pattern='OWNED_AUDIT_PASS' if name=='ForeignClean' else 'OWNED AUDIT REJECTED')
        negatives=[('FalseEquality','unsolved goals|type mismatch|Tactic.*rfl.*failed'),
            ('Placeholder','declaration uses.*sorry'),('MissingFinite','failed to synthesize'),
            ('MissingRadicalContainment','type mismatch'),('MissingLocal','failed to synthesize'),
            ('WrongResidueDimension','type mismatch'),('WrongLift','type mismatch')]
        for name,pattern in negatives:
            lean('negative_'+name,root/'tests/negative'/(name+'.lean'),extra=tenv,reject=True,pattern=pattern)
        # The malformed-proof control must fail at kernel checking, not at source elaboration.
        lean('kernel_corrupt_control',root/'tests/ReplayClosure.lean',extra={**cenv,
          'KOMOREBI_REPLAY_MODULES':'ForeignClean','KOMOREBI_REPLAY_CORRUPT':'1'},reject=True,
          pattern=r'kernel.*type mismatch|declaration type mismatch|type mismatch')
        corrupt=(out/'kernel_corrupt_control.log').read_text()
        assert 'REPLAY_CORRUPT_CONTROL_INJECTED' in corrupt and 'REPLAY_CLOSURE_PASS' not in corrupt
        report['negative_controls']=len(negatives)+3;report['positive_foreign_namespace_control']=1
        modules=[r['module'] for r in report['source_files']]+['BoundaryConsumers']
        text=lean('replay_whole_closure',root/'tests/ReplayClosure.lean',pattern=r'REPLAY_CLOSURE_PASS MODULES 47 CONSTANTS \d+',
          extra={**tenv,'KOMOREBI_REPLAY_MODULES':','.join(modules),'KOMOREBI_REPLAY_CORRUPT':'0'})
        checked=[json.loads(l[len('REPLAY_CHECKED '):]) for l in text.splitlines() if l.startswith('REPLAY_CHECKED ')]
        runtimes=[json.loads(l[len('REPLAY_RUNTIME_ONLY '):]) for l in text.splitlines() if l.startswith('REPLAY_RUNTIME_ONLY ')]
        duplicates=[json.loads(l[len('REPLAY_IDENTICAL_DUPLICATE '):]) for l in text.splitlines() if l.startswith('REPLAY_IDENTICAL_DUPLICATE ')]
        replaynames={r['name'] for r in checked};ownednames={r['name'] for r in owned+bowned if not r['runtime_only']}
        runtime_owned_names={r['name'] for r in owned+bowned if r['runtime_only']}
        assert len(replaynames)==len(checked) and replaynames==ownednames,{
          'extra':sorted(replaynames-ownednames),'missing':sorted(ownednames-replaynames)}
        assert not ({r['name'] for r in runtimes}&ownednames)
        assert {r['name'] for r in runtimes}==runtime_owned_names
        assert 'REPLAY_UPSTREAM_ONLY_PASS' in text
        for name,rows in [('replayed_constants',checked),('runtime_only_constants',runtimes),('identical_theorem_duplicates',duplicates)]:
            (out/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
        report['same_kernel_modules_replayed']=modules[:-1];report['new_boundary_module_replayed']=True
        report['replay_checked_constants']=len(checked);report['replay_runtime_only_entries']=len(runtimes)
        report['replay_identical_duplicate_entries']=len(duplicates)
        report['replay_owned_exact_name_set_match']=True;report['replay_starting_environment_excludes_all_project_modules']=True
        for row in report['source_files']:
            assert sha(root/row['source'])==row['source_sha256'] and sha(out/row['object'])==row['object_sha256']
        assert sha(tobj/'BoundaryConsumers.olean')==report['boundary_object_sha256']
        for row in report['frozen_inputs']:assert sha(root/row['path'])==row['sha256'],'Changed execution input '+row['path']
        assert check_manifest()==report['predecessor_payloads_authenticated']
        report['postflight_source_object_pairs_verified']=len(report['source_files'])
        report.update(status='PASS',elapsed_seconds=round(time.monotonic()-started,3),
          finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        save();print('BLOCK07_AUDIT_PASS',flush=True);return 0
    except Exception as exc:
        report.update(status='FAIL',failure=str(exc),elapsed_seconds=round(time.monotonic()-started,3));save();raise

if __name__=='__main__':raise SystemExit(main())
