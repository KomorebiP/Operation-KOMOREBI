#!/usr/bin/env python3
"""Fresh Block 04 extension verification against the freshly rebuilt Block 03 closure.
The baseline and extension have distinct empty output directories. Both are required.
No Mathlib rebuild or independent kernel implementation is claimed.
"""
from __future__ import annotations
import argparse, collections, hashlib, importlib.util, json, os, re, shutil, signal, subprocess, sys, time
from pathlib import Path

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main() -> int:
    ap=argparse.ArgumentParser()
    for n in ['root','kit','baseline','out']: ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();root=a.root.resolve();kit=a.kit.resolve();base=a.baseline.resolve();out=a.out.resolve()
    if out.exists():raise SystemExit('Refusing existing extension output directory')
    b=json.loads((base/'verification.json').read_text())
    if b['status']!='PASS':raise SystemExit('Fresh baseline has not passed')
    out.mkdir(parents=True);obj=out/'objects';obj.mkdir();tobj=out/'test_objects';tobj.mkdir()
    pred=root/'predecessor'
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('old_verifier',pred/'scripts/verify_block03.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    upstream=[]
    for s in os.environ.get('LEAN_PATH','').split(os.pathsep):
        q=Path(s).resolve()
        if str(q).startswith(str(kit/'workspace/.lake/packages')+os.sep) or q==kit/'toolchain/lib/lean':upstream.append(str(q))
    if not any('/mathlib/' in x for x in upstream):raise SystemExit('Use the pinned Lake environment')
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join([str(obj),str(base/'objects')]+upstream)
    flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
    modules=['PaperICompletion4.ResidueQuotient','PaperICompletion4.IntrinsicPrimary','PaperICompletion4.GroupedPrimary','PaperICompletion4.OperatorIntrinsicFormula','PaperICompletion4']
    report={'schema':'paper-i-block04-extension-audit/0.4.0','status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'baseline_report_sha256':sha(base/'verification.json'),'flags':flags,'checks':[],'source_files':[],'limits':['Fresh project builds in two stages, not a full Mathlib rebuild.','Official same-kernel replay; no independent verifier.','Prose-to-Lean coverage is a reviewed semantic map.','Noncomputable mathematical construction, not an executable normal-form or eigensolver algorithm.']}
    t0=time.monotonic()
    def save(): (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    def run(label,args,*,cwd=None,reject=False,pattern=None,extra=None,timeout=300):
        en=env.copy();en.update(extra or {});log=out/(label+'.log');t=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(args,env=en,cwd=cwd or root,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
        txt=log.read_text(errors='replace');ok=(0<code<124) if reject else code==0
        if pattern:ok=ok and re.search(pattern,txt,re.I) is not None
        report['checks'].append({'label':label,'command':args,'cwd':str(cwd or root),'actual_exit':code,'expected_exit':'nonzero' if reject else 'zero','required_pattern':pattern,'passed':ok,'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':sha(log),'environment_additions':extra or {}})
        save();print(('PASS ' if ok else 'FAIL ')+label,flush=True)
        if not ok:raise RuntimeError(label+' failed')
        return txt
    def lean(label,source,*,target=None,cwd=None,reject=False,pattern=None,extra=None):
        args=['lean',*flags]
        if target:target.parent.mkdir(parents=True,exist_ok=True);args+=['-o',str(target)]
        return run(label,args+[str(source)],cwd=cwd or source.parent,reject=reject,pattern=pattern,extra=extra)
    def manifest_check():
        m=json.loads((pred/'MANIFEST_SHA256.json').read_text());assert m['count']==len(m['files'])
        for f in m['files']:
            p=pred/f['path'];assert p.stat().st_size==f['bytes'] and sha(p)==f['sha256'],f['path']
        return len(m['files'])
    try:
        inputs=sorted(set([*list((root/'source/extension').rglob('*.lean')),*list((root/'tests').rglob('*.lean')),root/'scripts/verify_block04.py',root/'scripts/run_block04.sh',root/'coverage/COVERAGE_108.json']))
        report['frozen_inputs']=[]
        for ip in inputs:
            rel=ip.relative_to(root);target=out/'execution_inputs'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ip,target)
            report['frozen_inputs'].append({'path':str(rel),'sha256':sha(ip)})
        report['predecessor_payloads_verified']=manifest_check()
        for row in b['source_files']:
            assert sha(pred/row['source'])==row['source_sha256']
            assert sha(base/row['object'])==row['object_sha256']
        report['fresh_baseline_modules_verified']=len(b['source_files'])
        binding=json.loads((pred/'predecessor/baseline/evidence/environment/runtime_bindings.json').read_text())
        for row in binding['files']:assert sha(kit/row['path'])==row['sha256']
        report['runtime_files_authenticated']=len(binding['files']);report['runtime_archive_sha256']=binding['kit_archive_sha256'];report['lean_version']=binding['lean_version'];report['dependencies']=b['dependencies']
        assert run('lean_version',['lean','--version']).strip()==binding['lean_version']
        public=[]
        for module in modules:
            rel=Path(*module.split('.')).with_suffix('.lean');source=root/'source/extension'/rel;txt=source.read_text();clean=old.scrub(txt)
            pats=[r'^\s*(?:axiom|opaque|unsafe)\b',r'\b(?:sorry|admit|native_decide|implemented_by)\b',r'^\s*set_option\s+warningAsError\s+false',r'^\s*set_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true']
            if any(re.search(p,clean,re.M) for p in pats):raise RuntimeError('Forbidden production source: '+module)
            ns=re.search(r'^namespace ([\w.]+)',clean,re.M)
            if ns:
                for match in re.finditer(r'^(?:(?:noncomputable|protected)\s+)*(def|abbrev|theorem|lemma|instance|structure)\s+([\w.\']+)',clean,re.M):
                    public.append({'name':ns.group(1)+'.'+match.group(2),'source_kind':match.group(1),'module':module,'line':clean.count('\n',0,match.start())+1})
            snap=out/'source_snapshots'/rel;snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snap)
            h=sha(source);target=obj/rel.with_suffix('.olean')
            lean('compile_'+module.replace('.','_'),source,target=target,cwd=root/'source/extension')
            assert sha(source)==h
            report['source_files'].append({'module':module,'source':str(source.relative_to(root)),'source_sha256':h,'object':str(target.relative_to(out)),'object_sha256':sha(target),'source_lines':len(txt.splitlines())});save()
        public.sort(key=lambda r:r['name']);(out/'public_declarations.json').write_text(json.dumps(public,indent=2)+'\n')
        report['public_count']=len(public);report['public_kind_counts']=dict(collections.Counter(r['source_kind'] for r in public))
        types=out/'DeclarationTypes.lean';types.write_text('import PaperICompletion4\n'+''.join(f'#check {r["name"]}\n#print {r["name"]}\n#print axioms {r["name"]}\n' for r in public)+'#eval IO.println "BLOCK04_TYPES_PASS"\n')
        lean('public_declaration_types',types,pattern='BLOCK04_TYPES_PASS')
        text=lean('source_owned_audit',root/'tests/OwnedBlock04Audit.lean',pattern=r'OWNED_AUDIT_PASS \d+')
        rows=[json.loads(s[6:]) for s in text.splitlines() if s.startswith('OWNED ')]
        hit=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text);assert hit and len(rows)==int(hit.group(1)) and len(set(r['name'] for r in rows))==len(rows)
        new=[r for r in rows if r['module'] in modules];assert all(r['name'] in {s['name'] for s in new} for r in public)
        (out/'owned_declarations.json').write_text(json.dumps(rows,indent=2)+'\n');report.update(owned_total=len(rows),owned_new=len(new),axioms=sorted({ax for r in rows for ax in r['axioms']}),outside_project_namespace=int(hit.group(2)));save()
        for module in modules:
            lean('replay_'+module.replace('.','_'),root/'tests/ReplayExact.lean',pattern='REPLAY_EXACT_PASS '+re.escape(module),extra={'KOMOREBI_REPLAY_MODULE':module})
        report['replayed_extension_modules']=len(modules)
        tenv={'LEAN_PATH':os.pathsep.join([str(tobj),str(base/'test_objects'),env['LEAN_PATH']])}
        test=root/'tests/IntrinsicBoundaryConsumers.lean'
        lean('boundary_consumers',test,target=tobj/'IntrinsicBoundaryConsumers.olean',extra=tenv)
        bnames=['PaperIBlock04Tests.'+m.group(1) for m in re.finditer(r'^theorem ([\w\']+)',old.scrub(test.read_text()),re.M)]
        report['new_boundary_assertions']=len(bnames)
        report['boundary_source_sha256']=sha(test);report['boundary_object_sha256']=sha(tobj/'IntrinsicBoundaryConsumers.olean')
        bp=out/'BoundaryAxioms.lean';bp.write_text('import IntrinsicBoundaryConsumers\n'+''.join(f'#print axioms {n}\n' for n in bnames))
        bt=lean('boundary_axioms',bp,extra=tenv)
        found=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",bt)
        assert len(found)==len(bnames), 'Boundary axiom inventory count mismatch'
        for name,axs in found:
            assert not ({x.strip() for x in axs.split(',') if x.strip()}-{'propext','Classical.choice','Quot.sound'}),name
        lean('replay_boundary_consumers',root/'tests/ReplayExact.lean',extra={**tenv,'KOMOREBI_REPLAY_MODULE':'IntrinsicBoundaryConsumers'},pattern='REPLAY_EXACT_PASS IntrinsicBoundaryConsumers')
        controls=[('MissingArtinian','failed to synthesize'),('WrongIntrinsicDimension','type mismatch'),('WrongResidueKernel','type mismatch'),('MissingIrreducibility','failed to synthesize|type mismatch|unsolved goals')]
        for name,pattern in controls:
            lean('negative_'+name,root/'tests/negative'/(name+'.lean'),extra=tenv,reject=True,pattern=pattern)
        report['new_negative_controls']=len(controls)
        for row in report['source_files']:
            assert sha(root/row['source'])==row['source_sha256'] and sha(out/row['object'])==row['object_sha256']
        for row in b['source_files']:
            assert sha(pred/row['source'])==row['source_sha256'] and sha(base/row['object'])==row['object_sha256']
        assert sha(test)==report['boundary_source_sha256'] and sha(tobj/'IntrinsicBoundaryConsumers.olean')==report['boundary_object_sha256']
        report['postflight_source_object_pairs_verified']=len(b['source_files'])+len(report['source_files']);assert manifest_check()==report['predecessor_payloads_verified']
        for row in report['frozen_inputs']:assert sha(root/row['path'])==row['sha256'], 'Changed execution input '+row['path']
        report.update(status='PASS',elapsed_seconds=round(time.monotonic()-t0,3),finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()));save();print('BLOCK04_EXTENSION_PASS',flush=True);return 0
    except Exception as exc:
        report.update(status='FAIL',failure=str(exc),elapsed_seconds=round(time.monotonic()-t0,3));save();raise
if __name__=='__main__':raise SystemExit(main())
