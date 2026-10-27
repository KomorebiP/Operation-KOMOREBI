#!/usr/bin/env python3
"""Clean, fail-closed Paper I Block 03 verification in the pinned Lake environment.
Serial bounded processes only. Cached upstream dependencies are reused, not rebuilt.
An existing output directory is never resumed or overwritten.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, os, re, shutil, signal, subprocess, time
from pathlib import Path

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def scrub(text: str) -> str:
    """Remove nested Lean comments and string literals, preserving line numbers."""
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
            end=text.find('\n',i);i=len(text) if end<0 else end
        elif text[i]=='"':quoted=True;i+=1
        else:out.append(text[i]);i+=1
    return ''.join(out)

def main() -> int:
    ap=argparse.ArgumentParser()
    for n in ('root','kit','out'):ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();root=a.root.resolve();kit=a.kit.resolve();out=a.out.resolve()
    if out.exists():raise SystemExit('Refusing existing output directory')
    out.mkdir(parents=True);obj=out/'objects';obj.mkdir();tobj=out/'test_objects';tobj.mkdir()
    pred=root/'predecessor';base=pred/'baseline';tests=root/'tests'
    upstream=[]
    for s in os.environ.get('LEAN_PATH','').split(os.pathsep):
        q=Path(s).resolve()
        if str(q).startswith(str(kit/'workspace/.lake/packages')+os.sep) or q==kit/'toolchain/lib/lean':
            upstream.append(str(q))
    if not any('/mathlib/' in q for q in upstream):raise SystemExit('Run through the pinned kit Lake environment')
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join([str(obj)]+upstream)
    flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
    old=json.loads((pred/'evidence/baseline_replay/main/fresh_verification.json').read_text())
    oldmods=[r['module'] for r in old['modules']]
    b2mods=['PaperICompletion.CyclicClassification','PaperICompletion.SpectralCertificates','PaperICompletion.ConditionedCoordinates','PaperICompletion']
    newmods=['PaperICompletion3.PrimarySeedFormula','PaperICompletion3.OperatorPrimaryAPI','PaperICompletion3.InvariantFactorCount','PaperICompletion3']
    sources=[(m,base/'source/main') for m in oldmods]+[(m,pred/'source/extension') for m in b2mods]+[(m,root/'source/extension') for m in newmods]
    tstart=time.monotonic()
    report={'schema':'paper-i-block03-audit/0.3.0','status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'flags':flags,'upstream_search_paths':upstream,'source_files':[],'checks':[],
      'limits':['Cached pinned Mathlib dependencies reused, not freshly rebuilt or fully replayed.','Replay uses the official Lean kernel, not an independently implemented verifier.','The publication map is reviewed semantic correspondence, not a kernel interpretation of prose.','The constructions are noncomputable; no executable factorization, normal-form algorithm or eigensolver is claimed.','Intrinsic primary-submodule and X_p/p(T)X_p identification remains outside this block.']}
    def save():(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    def run(label,args,*,cwd=None,reject=False,pattern=None,extra=None,timeout=300):
        e=env.copy();e.update(extra or {});log=out/(label+'.log');start=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(args,cwd=cwd or root,env=e,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try:code=p.wait(timeout=timeout)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
        txt=log.read_text(errors='replace')
        ok=(code>0 and code!=124) if reject else code==0
        if pattern:ok=ok and bool(re.search(pattern,txt))
        report['checks'].append({'label':label,'command':args,'cwd':str(cwd or root),'expected_exit':'nonzero' if reject else 'zero','actual_exit':code,'required_pattern':pattern,'passed':ok,'seconds':round(time.monotonic()-start,3),'log':log.name,'log_sha256':sha(log),'environment_additions':extra or {}})
        save();print(('PASS ' if ok else 'FAIL ')+label,flush=True)
        if not ok:raise RuntimeError(label+' failed: '+str(log))
        return txt
    def lean(label,source,*,object_path=None,cwd=None,reject=False,pattern=None,extra=None,warning=True):
        fl=flags.copy()
        if not warning:fl[1]='-DwarningAsError=false'
        args=['lean',*fl]
        if object_path:object_path.parent.mkdir(parents=True,exist_ok=True);args+=['-o',str(object_path)]
        args+=[str(source)]
        return run(label,args,cwd=cwd or source.parent,reject=reject,pattern=pattern,extra=extra)
    def predecessor_check():
        m=json.loads((pred/'MANIFEST_SHA256.json').read_text())
        assert m['count']==len(m['files'])
        for r in m['files']:
            f=pred/r['path']
            if f.stat().st_size!=r['bytes'] or sha(f)!=r['sha256']:raise RuntimeError('Predecessor changed: '+r['path'])
        return len(m['files'])
    save()
    try:
        report['predecessor_payloads_verified']=predecessor_check()
        binding=json.loads((base/'evidence/environment/runtime_bindings.json').read_text())
        for r in binding['files']:
            if sha(kit/r['path'])!=r['sha256']:raise RuntimeError('Pinned runtime mismatch '+r['path'])
        report['runtime_files_authenticated']=len(binding['files'])
        report['runtime_archive_sha256']=binding['kit_archive_sha256']
        version=run('lean_version',['lean','--version']).strip()
        if version!=binding['lean_version']:raise RuntimeError('Wrong compiler version')
        report['lean_version']=version
        deps=[]
        for r in binding['dependencies']:
            d=kit/'workspace/.lake/packages'/r['name']
            actual=run('pin_'+r['name'],['git','-C',str(d),'rev-parse','HEAD']).strip()
            if actual!=r['rev']:raise RuntimeError('Wrong dependency commit '+r['name'])
            deps.append({'name':r['name'],'expected_revision':r['rev'],'actual_revision':actual})
        report['dependencies']=deps;save()
        public=[]
        for module,src in sources:
            rel=Path(*module.split('.')).with_suffix('.lean');p=src/rel;text=p.read_text();clean=scrub(text)
            patterns=[r'^\s*(?:axiom|opaque|unsafe)\b',r'\b(?:sorry|admit|native_decide|implemented_by)\b',r'^\s*set_option\s+warningAsError\s+false',r'^\s*set_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true']
            hits=[pat for pat in patterns if re.search(pat,clean,re.M)]
            if hits:raise RuntimeError('Forbidden production source '+module+': '+str(hits))
            if module in newmods:
                ns=re.search(r'^namespace ([\w.]+)',clean,re.M)
                if ns:
                    for m in re.finditer(r'^(?:(?:noncomputable|protected)\s+)*(def|abbrev|theorem|lemma|instance|structure)\s+([\w.\']+)',clean,re.M):
                        public.append({'name':ns.group(1)+'.'+m.group(2),'source_kind':m.group(1),'module':module,'line':clean.count('\n',0,m.start())+1})
            snap=out/'source_snapshots'/rel;snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,snap)
            o=obj/rel.with_suffix('.olean')
            before=sha(p)
            lean('compile_'+module.replace('.','_'),p,object_path=o,cwd=src)
            if sha(p)!=before:raise RuntimeError('Source changed during compile '+module)
            report['source_files'].append({'module':module,'source':str(p.relative_to(root)),'source_sha256':before,'object':str(o.relative_to(out)),'object_sha256':sha(o),'source_lines':len(text.splitlines()),'new_in_block03':module in newmods});save()
        public.sort(key=lambda d:d['name']);(out/'public_declarations.json').write_text(json.dumps(public,indent=2)+'\n')
        report['public_new_count']=len(public);report['public_new_kind_counts']=dict(collections.Counter(r['source_kind'] for r in public))
        # The original exact normative declaration set is still resolved independently.
        mapped_file=pred/'evidence/baseline_replay/main/MappedTypes.lean'
        lean('original_contract_declarations',mapped_file)
        report['original_mapped_declarations']=len(re.findall(r'^#check ',mapped_file.read_text(),re.M));report['original_contract_rows']=35
        lean('original_explicit_kernel_gate',base/'source/main/KomorebiVerification/KernelAudit.lean',cwd=base/'source/main',pattern=r'FAIL-CLOSED KERNEL AUDIT PASS')
        cov=json.loads((root/'coverage/COVERAGE_108.json').read_text());mapped={n for r in cov['records'] for n in r['mapped_declarations']}
        previous=json.loads((pred/'evidence/extension_attempt01/public_declarations.json').read_text())
        names=sorted(mapped|{r['name'] for r in public}|{r['name'] for r in previous})
        upstream_names=['Module.equiv_directSum_of_isTorsion','Module.AEval.isTorsion_of_finiteDimensional','Ideal.pi_quotient_surjective','Polynomial.exists_irreducible_of_natDegree_pos','Ideal.Quotient.factor_surjective']
        types=out/'DeclarationTypes.lean';types.write_text('import PaperICompletion3\nimport KomorebiVerification.KernelAudit\n'+''.join(f'#check {n}\n#print {n}\n#print axioms {n}\n' for n in names+upstream_names)+'#eval IO.println "BLOCK03_TYPES_PASS"\n')
        lean('complete_declaration_types',types,pattern='BLOCK03_TYPES_PASS')
        report['resolved_coverage_declarations']=len(mapped);report['resolved_public_or_coverage']=len(names);report['explicit_upstream_inputs']=upstream_names
        text=lean('owned_block03_audit',tests/'OwnedBlock03Audit.lean',pattern='OWNED_AUDIT_PASS ')
        rows=[json.loads(s[6:]) for s in text.splitlines() if s.startswith('OWNED ')]
        hit=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text)
        if not hit or len(rows)!=int(hit.group(1)) or len({r['name'] for r in rows})!=len(rows):raise RuntimeError('Invalid ownership count')
        newrows=[r for r in rows if r['module'] in newmods]
        for r in public:
            if r['name'] not in {d['name'] for d in newrows}:raise RuntimeError('Missing public declaration '+r['name'])
        (out/'owned_declarations.json').write_text(json.dumps(rows,indent=2)+'\n')
        report.update(owned_total=len(rows),owned_new=len(newrows),owned_new_kind_counts=dict(collections.Counter(r['kind'] for r in newrows)),axioms=sorted({ax for r in rows for ax in r['axioms']}),outside_project_namespace=int(hit.group(2)));save()
        for module,_ in sources:
            lean('replay_'+module.replace('.','_'),tests/'ReplayExact.lean',pattern='REPLAY_EXACT_PASS '+re.escape(module),extra={'KOMOREBI_REPLAY_MODULE':module})
        report['replayed_production_modules']=len(sources);save()
        # Standard strict-compiler controls.
        for name,pattern in [('FalseEquality','error:'),('Placeholder','declaration uses.*sorry')]:
            lean('negative_'+name,pred/'evidence/baseline_replay/main'/(name+'.lean'),reject=True,pattern=pattern)
        controlenv={'LEAN_PATH':os.pathsep.join([str(tobj),env['LEAN_PATH']])}
        for n in ['ForeignClean','InjectedAxiom','InjectedPlaceholder']:
            src=base/'tests/fixtures'/(n+'.lean');aud=base/'tests/fixtures'/(n+'Audit.lean')
            lean('compile_control_'+n,src,object_path=tobj/(n+'.olean'),extra=controlenv,warning=n!='InjectedPlaceholder',pattern='declaration uses.*sorry' if n=='InjectedPlaceholder' else None)
            lean('guard_'+n,aud,extra=controlenv,reject=n!='ForeignClean',pattern='OWNED_AUDIT_PASS 1 OUTSIDE_NAMESPACE 1' if n=='ForeignClean' else ('OWNED AUDIT REJECTED (axiom|dependency)' if n=='InjectedAxiom' else 'OWNED AUDIT REJECTED dependency sorryAx'))
        lean('original_boundary_regressions',base/'tests/BoundaryRegression.lean')
        lean('block02_boundary_consumers',pred/'tests/BoundaryConsumers.lean')
        for n,pattern in [('MissingNontrivial','failed to synthesize'),('ComplexSymmetryNotHermitian','type mismatch'),('ZeroConditionLowerBound','failed to synthesize')]:
            lean('negative_block02_'+n,pred/'tests'/(n+'.lean'),reject=True,pattern=pattern)
        lean('block03_boundary_consumers',tests/'PrimaryBoundaryConsumers.lean',object_path=tobj/'PrimaryBoundaryConsumers.olean',extra=controlenv)
        bnames=['PaperIBlock03Tests.'+m.group(1) for m in re.finditer(r'^theorem ([\w\']+)',(tests/'PrimaryBoundaryConsumers.lean').read_text(),re.M)]
        bp=out/'BoundaryAxioms.lean';bp.write_text('import PrimaryBoundaryConsumers\n'+''.join(f'#print axioms {n}\n' for n in bnames))
        txt=lean('block03_boundary_axioms',bp,extra=controlenv)
        found=re.findall(r"'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)",txt)
        if len(found)!=len(bnames):raise RuntimeError('Boundary axiom inventory count mismatch')
        for name,axs in found:
            if {s.strip() for s in axs.split(',') if s.strip()}-{'propext','Classical.choice','Quot.sound'}:raise RuntimeError('Unapproved test axiom '+name)
        lean('replay_block03_boundaries',tests/'ReplayExact.lean',extra={**controlenv,'KOMOREBI_REPLAY_MODULE':'PrimaryBoundaryConsumers'},pattern='REPLAY_EXACT_PASS PrimaryBoundaryConsumers')
        for n,pattern in [('ZeroExponentMisuse','error:'),('WrongResidueDimension','type mismatch'),('RepeatedPrimaryOneSeed','type mismatch'),('MissingDivisibilityChain','type mismatch')]:
            lean('negative_block03_'+n,tests/'negative'/(n+'.lean'),extra=controlenv,reject=True,pattern=pattern)
        report.update(boundary_theorems_original=4,boundary_theorems_block02=12,boundary_theorems_block03=len(bnames),rejection_controls=11,positive_foreign_namespace_control=1,replayed_boundary_modules=1)
        for r in report['source_files']:
            if sha(root/r['source'])!=r['source_sha256'] or sha(out/r['object'])!=r['object_sha256']:raise RuntimeError('Final source/object mismatch '+r['module'])
        report['post_replay_identity_modules']=len(sources);report['predecessor_final_identity']=predecessor_check()
        report['coverage_sha256']=sha(root/'coverage/COVERAGE_108.json')
        report['status']='PASS';report['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());report['elapsed_seconds']=round(time.monotonic()-tstart,3);save()
        print('PAPER_I_BLOCK03_PASS',flush=True);return 0
    except Exception as ex:
        report['status']='FAIL';report['failure']=str(ex);report['elapsed_seconds']=round(time.monotonic()-tstart,3);save();print(str(ex),flush=True);return 1
if __name__=='__main__':raise SystemExit(main())
