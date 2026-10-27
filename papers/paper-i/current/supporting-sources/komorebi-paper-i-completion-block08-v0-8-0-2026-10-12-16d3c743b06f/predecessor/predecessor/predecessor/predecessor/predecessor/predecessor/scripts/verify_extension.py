#!/usr/bin/env python3
"""Strict Paper I completion audit. Run inside the pinned Lake environment.
No network or dependency updates. Every attempt owns a new output directory.
The baseline must already have a successful clean build, ownership audit,
serial replay, and control run. All outcomes derive from executed commands.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, os, re, shutil, signal, subprocess, time
from pathlib import Path

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def main()->int:
    ap=argparse.ArgumentParser()
    for arg in ('source','tests','baseline_root','baseline_run','coverage','out'):
        ap.add_argument('--'+arg.replace('_','-'),dest=arg,type=Path,required=True)
    a=ap.parse_args()
    src,tests,br,run,coverage,out=[getattr(a,x).resolve() for x in ('source','tests','baseline_root','baseline_run','coverage','out')]
    if out.exists(): raise SystemExit('Refusing existing output directory')
    out.mkdir(parents=True);(out/'objects').mkdir();(out/'source_snapshots').mkdir()
    base=json.loads((run/'main/fresh_verification.json').read_text())
    additional=json.loads((run/'additional/verification.json').read_text())
    controls=json.loads((run/'controls/verification.json').read_text())
    if not all(x.get('status')=='PASS' for x in (base,additional,controls)):
        raise SystemExit('Baseline does not have all three successful receipts')
    modules=['PaperICompletion.CyclicClassification','PaperICompletion.SpectralCertificates','PaperICompletion.ConditionedCoordinates','PaperICompletion']
    flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3']
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join((str(out/'objects'),str(run/'main/objects'),env.get('LEAN_PATH','')))
    tstart=time.monotonic()
    report={'schema':'paper-i-completion-audit/0.2.0','status':'RUNNING','started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'flags':flags,'source_files':[],'checks':[], 'baseline_receipts':{str(p.relative_to(run)):sha(p) for p in [run/'main/fresh_verification.json',run/'additional/verification.json',run/'controls/verification.json']},'limits':['Pinned cached Mathlib imports reused, not rebuilt in this block.','Replay uses the official Lean kernel, not an independent verifier.','Coverage classification is a reviewed prose-to-type correspondence, not a kernel interpretation of TeX.','Spectral and PID constructions are noncomputable. No executable eigensolver is claimed.']}
    def save(): (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    def command(label,args,expected=0,marker=None,extra=None):
        e=env.copy();e.update(extra or {});log=out/(label+'.log');t=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(args,cwd=src,env=e,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try: code=p.wait(timeout=600)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
        text=log.read_text(errors='replace')
        ok=(code==0 if expected==0 else code!=0 and code!=124) and (marker is None or marker in text)
        rec={'label':label,'command':args,'expected_exit':'zero' if expected==0 else 'nonzero','actual_exit':code,'required_marker':marker,'passed':ok,'seconds':round(time.monotonic()-t,3),'log':log.name,'log_sha256':sha(log),'environment_additions':extra or {}}
        report['checks'].append(rec);save();print(('PASS ' if ok else 'FAIL ')+label,flush=True)
        if not ok: raise RuntimeError(label+' failed, inspect '+str(log))
        return text
    save()
    try:
        for item in base['modules']:
            p=br/'source/main'/Path(*item['module'].split('.')).with_suffix('.lean')
            obj=run/'main/objects'/Path(*item['module'].split('.')).with_suffix('.olean')
            if sha(p)!=item['source_sha256'] or sha(obj)!=item['object_sha256']:
                raise RuntimeError('Baseline source/object identity mismatch: '+item['module'])
        report['baseline_identity_modules']=len(base['modules'])
        public=[]
        for module in modules:
            rel=Path(*module.split('.')).with_suffix('.lean');p=src/rel
            text=p.read_text()
            # A local explicit scan is deliberately conservative; the ownership
            # audit is the authoritative transitive check, including private code.
            forbidden=[r'^\s*(?:axiom|opaque|unsafe)\b',r'\b(?:sorry|admit|native_decide|implemented_by)\b',r'^\s*set_option\s+(?:warningAsError|autoImplicit)\s+(?:false|true)']
            # Remove block and line comments and string contents before policy scan.
            cleaned=[];i=0;depth=0;in_string=False
            while i<len(text):
                if depth:
                    if text.startswith('/-',i): depth+=1;i+=2
                    elif text.startswith('-/',i):depth-=1;i+=2
                    else:
                        if text[i]=='\n':cleaned.append('\n')
                        i+=1
                elif in_string:
                    if text[i]=='\\':i+=2
                    elif text[i]=='"':in_string=False;i+=1
                    else:i+=1
                elif text.startswith('/-',i):depth=1;i+=2
                elif text.startswith('--',i):
                    end=text.find('\n',i);i=len(text) if end<0 else end
                elif text[i]=='"':in_string=True;i+=1
                else:cleaned.append(text[i]);i+=1
            clean=''.join(cleaned)
            # autoImplicit false is required, not forbidden.
            forbidden=forbidden[:2]+[r'^\s*set_option\s+warningAsError\s+false',r'^\s*set_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true']
            hits=[pat for pat in forbidden if re.search(pat,clean,re.M)]
            if hits:raise RuntimeError(f'Forbidden production source in {p}: {hits}')
            ns=re.search(r'^namespace ([\w.]+)',clean,re.M)
            if ns:
                for m in re.finditer(r'^(?:(?:noncomputable|protected)\s+)*(def|abbrev|theorem|lemma|instance)\s+(\w+)',clean,re.M):
                    public.append({'name':ns.group(1)+'.'+m.group(2),'source_kind':m.group(1),'module':module,'line':clean.count('\n',0,m.start())+1})
            snap=out/'source_snapshots'/rel;snap.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,snap)
            obj=out/'objects'/rel.with_suffix('.olean');obj.parent.mkdir(parents=True,exist_ok=True)
            command('compile_'+module.replace('.','_'),['lean',*flags,'-o',str(obj),str(p)])
            report['source_files'].append({'module':module,'relative_path':str(rel),'source_sha256':sha(p),'object_sha256':sha(obj),'source_lines':len(text.splitlines())});save()
        public.sort(key=lambda x:x['name'])
        (out/'public_declarations.json').write_text(json.dumps(public,indent=2)+'\n')
        report['public_declaration_count']=len(public)
        report['public_kind_counts']=dict(collections.Counter(x['source_kind'] for x in public))
        cov=json.loads(coverage.read_text());mapped=sorted({d for r in cov['records'] for d in r['mapped_declarations']})
        names=sorted(set(mapped)|{r['name'] for r in public})
        upstream=['Module.exists_ker_toSpanSingleton_eq_annihilator','Module.equiv_directSum_of_isTorsion','LinearMap.IsSymmetric.eigenvectorBasis','LinearMap.IsSymmetric.card_filter_eigenvalues_eq']
        typetest=out/'DeclarationTypes.lean'
        typetest.write_text('import PaperICompletion\nimport KomorebiVerification.KernelAudit\n'+''.join(f'#check {n}\n#print {n}\n#print axioms {n}\n' for n in names+upstream)+'#eval IO.println "COMPLETION_TYPES_PASS"\n')
        command('declaration_types',['lean',*flags,str(typetest)],marker='COMPLETION_TYPES_PASS')
        report['resolved_coverage_declarations']=len(mapped);report['resolved_source_or_coverage_declarations']=len(names);report['explicit_upstream_inputs']=upstream;save()
        text=command('owned_completion_audit',['lean',*flags,str(tests/'OwnedCompletionAudit.lean')],marker='OWNED_AUDIT_PASS ')
        rows=[json.loads(x[6:]) for x in text.splitlines() if x.startswith('OWNED ')]
        m=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text)
        if not m or len(rows)!=int(m.group(1)) or len({r['name'] for r in rows})!=len(rows):raise RuntimeError('Owned inventory count mismatch')
        newrows=[r for r in rows if r['module'] in modules]
        for p in public:
            if p['name'] not in {r['name'] for r in newrows}:raise RuntimeError('Public declaration absent from ownership inventory: '+p['name'])
        (out/'owned_declarations.json').write_text(json.dumps(rows,indent=2)+'\n')
        report.update({'owned_total':len(rows),'owned_new':len(newrows),'owned_new_kind_counts':dict(collections.Counter(x['kind'] for x in newrows)),'outside_project_namespaces':int(m.group(2)),'axioms':sorted({ax for r in rows for ax in r['axioms']})});save()
        for module in modules:
            command('replay_'+module.replace('.','_'),['lean',*flags,str(tests/'ReplayExact.lean')],marker='REPLAY_EXACT_PASS '+module,extra={'KOMOREBI_REPLAY_MODULE':module})
        command('boundary_consumers',['lean',*flags,str(tests/'BoundaryConsumers.lean')])
        report['boundary_theorems']=len(re.findall(r'^theorem ',(tests/'BoundaryConsumers.lean').read_text(),re.M))
        for fixture,marker in [('MissingNontrivial.lean','failed to synthesize'),('ComplexSymmetryNotHermitian.lean','type mismatch'),('ZeroConditionLowerBound.lean','failed to synthesize')]:
            command('negative_'+fixture[:-5],['lean',*flags,str(tests/fixture)],expected=1,marker=marker)
        for item in report['source_files']:
            p=src/item['relative_path'];obj=out/'objects'/Path(item['relative_path']).with_suffix('.olean')
            if sha(p)!=item['source_sha256'] or sha(obj)!=item['object_sha256']:raise RuntimeError('Post-replay identity failure '+str(p))
        report['final_identity_modules']=len(modules);report['replayed_new_modules']=len(modules);report['coverage_json_sha256']=sha(coverage)
        report['status']='PASS';report['elapsed_seconds']=round(time.monotonic()-tstart,3);report['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());save()
        print('PAPER_I_COMPLETION_BLOCK02_PASS',flush=True);return 0
    except Exception as ex:
        report['status']='FAIL';report['failure']=str(ex);report['elapsed_seconds']=round(time.monotonic()-tstart,3);save();print(str(ex),flush=True);return 1
if __name__=='__main__':raise SystemExit(main())
