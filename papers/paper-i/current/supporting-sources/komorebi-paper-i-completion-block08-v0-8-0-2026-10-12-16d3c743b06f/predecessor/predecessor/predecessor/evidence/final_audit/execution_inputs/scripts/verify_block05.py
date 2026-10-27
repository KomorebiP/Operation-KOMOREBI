#!/usr/bin/env python3
"""Verify fresh Block 05 sources against an authenticated unchanged predecessor.
Four new production modules are freshly compiled. All 37 production objects
are serially replayed by the pinned official Lean kernel. The predecessor's
33 source/object pairs are authenticated, not described as freshly rebuilt.
"""
from __future__ import annotations
import argparse,collections,hashlib,json,os,re,shutil,signal,subprocess,time
from pathlib import Path

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def scrub(text:str)->str:
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

def main()->int:
    ap=argparse.ArgumentParser()
    for n in ('root','kit','out'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();root=a.root.resolve();kit=a.kit.resolve();out=a.out.resolve();pred=root/'predecessor'
    if out.exists():raise SystemExit('Refusing existing output directory')
    upstream=[]
    for part in os.environ.get('LEAN_PATH','').split(os.pathsep):
        p=Path(part).resolve()
        if str(p).startswith(str(kit/'workspace/.lake/packages')+os.sep) or p==kit/'toolchain/lib/lean':upstream.append(str(p))
    if not any('/mathlib/' in p for p in upstream):raise SystemExit('Use the pinned Lake environment')
    out.mkdir(parents=True);obj=out/'objects';inherited=out/'inherited_objects';tobj=out/'test_objects';ctrl=out/'control_objects'
    for p in (obj,inherited,tobj,ctrl):p.mkdir()
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join([str(obj),str(inherited)]+upstream)
    flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
    newmods=['PaperICompletion5.LinearPrimaryEigenspace','PaperICompletion5.GeometricSeedFormula','PaperICompletion5.CyclicGeometricCriterion','PaperICompletion5']
    report={'schema':'paper-i-block05-audit/0.5.0','status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'checks':[],'source_files':[],'flags':flags,'scope':'Fresh new modules; authenticated unchanged predecessor objects; complete same-kernel production replay.', 'limits':['The 33 predecessor modules are source/object authenticated, not freshly rebuilt in this accepted run.','Cached pinned Mathlib dependencies reused, not rebuilt or fully replayed.','Replays use the official Lean kernel, not an independent verifier.','Publication correspondence is a reviewed semantic map, not a kernel parsing of prose.','Constructions are noncomputable, not an executable eigensolver or canonical-form algorithm.']}
    started=time.monotonic()
    def save():(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    def run(label,args,*,cwd=None,reject=False,pattern=None,extra=None,timeout=300):
        en=env.copy();en.update(extra or {});log=out/(label+'.log');t=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(args,cwd=cwd or root,env=en,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
        text=log.read_text(errors='replace');ok=(0<code<124) if reject else code==0
        if pattern:ok=ok and re.search(pattern,text,re.I) is not None
        report['checks'].append({'label':label,'command':args,'cwd':str(cwd or root),'expected_exit':'nonzero' if reject else 'zero','actual_exit':code,'passed':ok,'required_pattern':pattern,'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':sha(log),'environment_additions':extra or {}})
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
        pats=[r'^\s*(?:axiom|opaque|unsafe)\b',r'\b(?:sorry|admit|native_decide|implemented_by)\b',r'^\s*set_option\s+warningAsError\s+false',r'^\s*set_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true']
        assert not any(re.search(p,clean,re.M) for p in pats),'Forbidden production source '+str(source)
        return clean
    save()
    try:
        inputs=sorted([*list((root/'source/extension').rglob('*.lean')),*list((root/'tests').rglob('*.lean')),root/'scripts/verify_block05.py',root/'scripts/run_block05.sh'])
        report['frozen_inputs']=[]
        for ip in inputs:
            rel=ip.relative_to(root);t=out/'execution_inputs'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ip,t)
            report['frozen_inputs'].append({'path':str(rel),'sha256':sha(ip)})
        report['predecessor_payloads_authenticated']=check_manifest()
        oldtop=json.loads((pred/'VERIFICATION.json').read_text());assert oldtop['status']=='PASS'
        for s in oldtop['stages']:
            assert sha(pred/s['path'])==s['sha256']
        report['predecessor_verification_sha256']=sha(pred/'VERIFICATION.json')
        source_rows=[]
        for sub,srcroot in [('baseline_fresh',pred/'predecessor'),('extension_fresh',pred)]:
            stage=pred/'evidence'/sub;b=json.loads((stage/'verification.json').read_text());assert b['status']=='PASS'
            for row in b['source_files']:
                source=srcroot/row['source'];oldobj=stage/row['object'];assert sha(source)==row['source_sha256'] and sha(oldobj)==row['object_sha256']
                source_policy(source)
                rel=Path(*row['module'].split('.'));target=(inherited/rel).with_suffix('.olean');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(oldobj,target)
                snap=(out/'source_snapshots'/rel).with_suffix('.lean');snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snap)
                source_rows.append({'module':row['module'],'source':str(source.relative_to(root)),'source_sha256':sha(source),'source_lines':len(source.read_text().splitlines()),'object':str(target.relative_to(out)),'object_sha256':sha(target),'origin':'authenticated_predecessor'})
        assert len(source_rows)==33 and len({r['module'] for r in source_rows})==33
        report['source_files']=source_rows;report['predecessor_module_pairs_authenticated']=33;save()
        binding=json.loads((pred/'predecessor/predecessor/baseline/evidence/environment/runtime_bindings.json').read_text())
        for row in binding['files']:assert sha(kit/row['path'])==row['sha256'],row['path']
        report['runtime_files_authenticated']=len(binding['files']);report['runtime_archive_sha256']=binding['kit_archive_sha256']
        version=run('lean_version',['lean','--version']).strip();assert version==binding['lean_version'];report['lean_version']=version
        report['dependencies']=[]
        for row in binding['dependencies']:
            rev=run('pin_'+row['name'],['git','-C',str(kit/'workspace/.lake/packages'/row['name']),'rev-parse','HEAD']).strip();assert rev==row['rev']
            report['dependencies'].append({'name':row['name'],'expected_revision':row['rev'],'actual_revision':rev})
        public=[]
        for module in newmods:
            rel=Path(*module.split('.')).with_suffix('.lean');source=root/'source/extension'/rel;clean=source_policy(source)
            ns=re.search(r'^namespace ([\w.]+)',clean,re.M)
            if ns:
                for m in re.finditer(r'^(?:(?:noncomputable|protected)\s+)*(def|abbrev|theorem|lemma|instance|structure)\s+([\w.\']+)',clean,re.M):
                    public.append({'name':ns.group(1)+'.'+m.group(2),'source_kind':m.group(1),'module':module,'line':clean.count('\n',0,m.start())+1})
            h=sha(source);target=(obj/rel).with_suffix('.olean');snap=out/'source_snapshots'/rel;snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snap)
            lean('compile_'+module.replace('.','_'),source,target=target,cwd=root/'source/extension');assert sha(source)==h
            report['source_files'].append({'module':module,'source':str(source.relative_to(root)),'source_sha256':h,'source_lines':len(source.read_text().splitlines()),'object':str(target.relative_to(out)),'object_sha256':sha(target),'origin':'fresh_compile'});save()
        report['fresh_new_production_modules']=len(newmods);public.sort(key=lambda x:x['name']);(out/'public_declarations.json').write_text(json.dumps(public,indent=2)+'\n')
        report['new_public_count']=len(public);report['new_public_kind_counts']=dict(collections.Counter(r['source_kind'] for r in public))
        previous=set(re.findall(r'^#check\s+([\w.\']+)',(pred/'evidence/baseline_fresh/DeclarationTypes.lean').read_text(),re.M))
        previous.update(r['name'] for r in json.loads((pred/'evidence/extension_fresh/public_declarations.json').read_text()))
        names=sorted(previous|{r['name'] for r in public});types=out/'DeclarationTypes.lean'
        types.write_text('import PaperICompletion5\n'+''.join(f'#check {n}\n#print axioms {n}\n' for n in names)+'#eval IO.println "BLOCK05_TYPES_PASS"\n')
        text=lean('declaration_types_and_axioms',types,pattern='BLOCK05_TYPES_PASS');report['declaration_names_resolved']=len(names)
        proof_types=out/'NewPublicTypes.lean';proof_types.write_text('import PaperICompletion5\n'+''.join(f'#print {r["name"]}\n' for r in public))
        lean('new_public_full_types',proof_types)
        text=lean('source_owned_audit',root/'tests/OwnedBlock05Audit.lean',pattern=r'OWNED_AUDIT_PASS \d+')
        owned=[json.loads(l[6:]) for l in text.splitlines() if l.startswith('OWNED ')];hit=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text)
        assert hit and int(hit.group(1))==len(owned) and len({r['name'] for r in owned})==len(owned)
        assert {r['name'] for r in public} <= {r['name'] for r in owned if r['module'] in newmods}
        (out/'owned_declarations.json').write_text(json.dumps(owned,indent=2)+'\n');report['owned_total']=len(owned);report['owned_new']=sum(r['module'] in newmods for r in owned);report['axioms']=sorted({ax for r in owned for ax in r['axioms']});report['outside_project_namespace']=int(hit.group(2));save()
        # New mathematical boundary consumers import only the explicitly authenticated old suites.
        for sub,name in [('baseline_fresh','PrimaryBoundaryConsumers'),('extension_fresh','IntrinsicBoundaryConsumers')]:
            shutil.copy2(pred/'evidence'/sub/'test_objects'/(name+'.olean'),tobj/(name+'.olean'))
        tenv={'LEAN_PATH':os.pathsep.join([str(tobj),env['LEAN_PATH']])}
        test=root/'tests/GeometricBoundaryConsumers.lean';lean('geometric_boundary_consumers',test,target=tobj/'GeometricBoundaryConsumers.olean',cwd=root/'tests',extra=tenv)
        bnames=['PaperIBlock05Tests.'+m.group(1) for m in re.finditer(r'^theorem ([\w\']+)',scrub(test.read_text()),re.M)]
        report['new_boundary_assertions']=len(bnames);bp=out/'BoundaryAxioms.lean';bp.write_text('import GeometricBoundaryConsumers\n'+''.join(f'#print axioms {n}\n' for n in bnames))
        bt=lean('boundary_axioms',bp,extra=tenv)
        found=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",bt);assert len(found)==len(bnames)
        for n,axs in found:assert not ({x.strip() for x in axs.split(',') if x.strip()}-{'propext','Classical.choice','Quot.sound'}),n
        report['boundary_object_sha256']=sha(tobj/'GeometricBoundaryConsumers.olean')
        # Guard fixtures are kept off the production and mathematical-test import paths.
        cenv={'LEAN_PATH':os.pathsep.join([str(ctrl),env['LEAN_PATH']])}
        for name in ['InjectedAxiom','InjectedPlaceholder','ForeignClean']:
            lean('compile_control_'+name,root/'tests/fixtures'/(name+'.lean'),target=ctrl/(name+'.olean'),cwd=root/'tests/fixtures',extra=cenv,warning=name!='InjectedPlaceholder')
            lean('guard_'+name,root/'tests/fixtures'/(name+'Audit.lean'),extra=cenv,reject=name!='ForeignClean',pattern='OWNED_AUDIT_PASS' if name=='ForeignClean' else 'OWNED AUDIT REJECTED')
        negatives=[('FalseEquality','unsolved goals|type mismatch|Tactic.*rfl.*failed'),('Placeholder','declaration uses.*sorry'),('MissingAlgClosed','failed to synthesize'),('MissingNonzero','failed to synthesize'),('WrongJordanMultiplicity','type mismatch'),('CokernelNotInjectivity','type mismatch')]
        for name,pattern in negatives:lean('negative_'+name,root/'tests/negative'/(name+'.lean'),extra=tenv,reject=True,pattern=pattern)
        report['negative_controls']=len(negatives)+2;report['positive_foreign_namespace_control']=1
        # Replay ALL current production modules, not only the four freshly compiled additions.
        replayed=[]
        for row in report['source_files']:
            module=row['module'];lean('replay_'+module.replace('.','_'),root/'tests/ReplayExact.lean',pattern='REPLAY_EXACT_PASS '+re.escape(module),extra={'KOMOREBI_REPLAY_MODULE':module})
            replayed.append(module);report['same_kernel_modules_replayed']=replayed;save()
        lean('replay_geometric_boundaries',root/'tests/ReplayExact.lean',pattern='REPLAY_EXACT_PASS GeometricBoundaryConsumers',extra={**tenv,'KOMOREBI_REPLAY_MODULE':'GeometricBoundaryConsumers'})
        report['new_boundary_module_replayed']=True
        for row in report['source_files']:assert sha(root/row['source'])==row['source_sha256'] and sha(out/row['object'])==row['object_sha256']
        for row in report['frozen_inputs']:assert sha(root/row['path'])==row['sha256'],'Changed execution input '+row['path']
        assert check_manifest()==report['predecessor_payloads_authenticated']
        report['postflight_source_object_pairs_verified']=len(report['source_files'])
        report.update(status='PASS',elapsed_seconds=round(time.monotonic()-started,3),finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));save();print('BLOCK05_AUDIT_PASS',flush=True);return 0
    except Exception as exc:
        report.update(status='FAIL',failure=str(exc),elapsed_seconds=round(time.monotonic()-started,3));save();raise
if __name__=='__main__':raise SystemExit(main())
