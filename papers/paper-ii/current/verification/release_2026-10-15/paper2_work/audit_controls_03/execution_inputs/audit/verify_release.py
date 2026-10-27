#!/usr/bin/env python3
"""Fresh source closure, source-owned axiom audit, and exact Lean kernel replay.

The pinned upstream cache and Lean kernel are trusted. Semantic correspondence
with the manuscript is a separate audit. This is not an independent kernel.
"""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import time


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scrub(text):
    out=[]; i=0; depth=0; quoted=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i): depth+=1; i+=2
            elif text.startswith('-/',i): depth-=1; i+=2
            else:
                if text[i]=='\n': out.append('\n')
                i+=1
        elif quoted:
            if text[i]=='\\': i+=2
            elif text[i]=='"': quoted=False; i+=1
            else:
                if text[i]=='\n': out.append('\n')
                i+=1
        elif text.startswith('/-',i): depth=1; i+=2
        elif text.startswith('--',i):
            end=text.find('\n',i); i=len(text) if end<0 else end
        elif text[i]=='"': quoted=True; i+=1
        else: out.append(text[i]); i+=1
    if depth or quoted:
        raise ValueError('Unterminated comment or string')
    return ''.join(out)


def inspect_sources(root):
    files={'.'.join(p.relative_to(root).with_suffix('').parts):p for p in root.rglob('*.lean')}
    if not files or any(p.is_symlink() for p in files.values()):
        raise ValueError('Missing sources or symlink in production tree')
    cleaned={m:scrub(p.read_text()) for m,p in files.items()}
    for module,text in cleaned.items():
        for pattern in [r'^\s*(?:(?:private|protected|noncomputable)\s+)*(?:axiom|opaque|unsafe|partial)\b',
                        r'\b(?:sorry|admit|native_decide|implemented_by)\b',
                        r'\bset_option\s+warningAsError\s+false',
                        r'\bset_option\s+(?:autoImplicit|relaxedAutoImplicit)\s+true']:
            if re.search(pattern,text,re.M):
                raise ValueError('Production source policy failed: '+module)
    imports={m:[x for line in re.findall(r'^\s*(?:public\s+)?import\s+([^\n]+)',text,re.M)
                for x in line.split() if x in files] for m,text in cleaned.items()}
    order=[];seen=set();visiting=set()
    def visit(module):
        if module in seen:return
        if module in visiting:raise ValueError('Local import cycle: '+module)
        visiting.add(module)
        for dep in imports[module]:visit(dep)
        visiting.remove(module);seen.add(module);order.append(module)
    for module in sorted(files):visit(module)
    rows=[{'module':m,'source':str(files[m].relative_to(root)),
           'source_sha256':sha(files[m]),'local_imports':imports[m]} for m in order]
    empty=[m for m in order if not re.search(
        r'^\s*(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|protected|private|scoped)\s+)*'
        r'(?:def|abbrev|theorem|lemma|instance|structure|inductive)\s+',cleaned[m],re.M)]
    return rows,empty


def execute(args):
    root=args.root.resolve();kit=args.kit.resolve();out=args.out.resolve()
    audit=Path(__file__).resolve().parent
    if out==root or root in out.parents:
        raise ValueError('Output must be outside the production source tree')
    if out.exists():raise ValueError('Fresh output directory required')
    rows,empty=inspect_sources(root)
    if args.freeze_manifest:
        if args.freeze_manifest.exists():raise ValueError('Refusing existing frozen manifest')
        args.freeze_manifest.write_text(json.dumps(rows,indent=2)+'\n')
        print(str(len(rows))+' production source modules frozen')
        return 0
    if not args.controls_only:
        if args.manifest is None:raise ValueError('Explicit frozen manifest required')
        frozen=json.loads(args.manifest.read_text())
        if rows!=frozen:raise ValueError('Production sources or dependency order differ from frozen manifest')
    out.mkdir(parents=True);objects=out/'objects';objects.mkdir()
    flags=['-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false',
           '-DmaxSynthPendingDepth=3','-Dpp.unicode.fun=true']
    report={'schema':'komorebi.paper-ii.strict-replay/1','status':'RUNNING',
            'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'mode':'controls-only' if args.controls_only else 'fresh-complete-closure',
            'checks':[],'source_files':[],'flags':flags,
            'limits':['Pinned upstream cache reused, not independently rebuilt.',
                      'Replay uses Lean own kernel, not an independent implementation.',
                      'Source ownership and kernel validity do not establish manuscript correspondence.',
                      'Only independently reviewed exact-source/exact-body generated runtime helpers may be excluded from logical replay. Upstream duplicate exceptions are not preapproved.'],
            'container_memory_max_bytes':Path('/sys/fs/cgroup/memory.max').read_text().strip(),
            'per_process_timeout_seconds':args.timeout}
    started=time.monotonic()
    def save():(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    env=os.environ.copy()
    for key in ['LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME']:env.pop(key,None)
    env.update(PATH=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH',''),
               MALLOC_ARENA_MAX='2',LEAN_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
    adapter=kit/'compat/app_path.so'
    env['LD_PRELOAD']=str(adapter)+((':'+env['LD_PRELOAD']) if env.get('LD_PRELOAD') else '')
    def run(label,command,*,reject=False,pattern=None,cwd=None,extra=None):
        e=env.copy();e.update(extra or {});log=out/(label+'.log');begin=time.monotonic()
        with log.open('w') as handle:
            proc=subprocess.Popen(command,cwd=cwd or root,env=e,stdout=handle,
                                  stderr=subprocess.STDOUT,start_new_session=True)
            try:code=proc.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid,signal.SIGKILL);proc.wait();code=124
        text=log.read_text(errors='replace')
        passed=(0<code<124) if reject else code==0
        if pattern:passed=passed and re.search(pattern,text,re.I) is not None
        report['checks'].append({'label':label,'command':command,'cwd':str(cwd or root),
            'exit':code,'expected':'nonzero' if reject else 'zero','passed':passed,
            'required_pattern':pattern,'seconds':round(time.monotonic()-begin,3),
            'log':log.name,'log_sha256':sha(log),'environment_additions':extra or {}})
        save();print(('PASS ' if passed else 'FAIL ')+label,flush=True)
        if not passed:raise RuntimeError(label)
        return text
    def lean(label,source,target=None,warning=True,**kw):
        opts=flags.copy()
        if not warning:opts[1]='-DwarningAsError=false'
        command=[str(kit/'toolchain/bin/lean'),*opts]
        if target:
            target.parent.mkdir(parents=True,exist_ok=True);command+=['-o',str(target)]
        return run(label,command+[str(source)],**kw)
    template=(audit/'OwnedAudit.template.lean').read_text()
    reviewed_helpers=[]
    if not args.controls_only:
        review=json.loads((audit/'reviewed_runtime_helpers.json').read_text())
        if review['status']!='REVIEWED':raise ValueError('Runtime helpers require independent root review')
        reviewed_helpers=review['helpers']
        if len(reviewed_helpers)!=len({h['name'] for h in reviewed_helpers}):
            raise ValueError('Duplicate reviewed runtime helper name')
        for row in review['source_modules']:
            if sha(root/row['source'])!=row['sha256']:raise ValueError('Runtime helper source changed')
        for row in review['evidence']:
            if sha(audit/row['path'])!=row['sha256']:raise ValueError('Runtime helper review evidence changed')
        report['reviewed_runtime_helpers_sha256']=sha(audit/'reviewed_runtime_helpers.json')
    arr=lambda names:'#['+', '.join('`'+name for name in names)+']'
    def owned_source(modules,empty_modules,path,helpers=()):
        path.write_text(template.replace('__IMPORTS__','\n'.join('import '+m for m in modules))
            .replace('__MODULES__',arr(modules)).replace('__EMPTY_MODULES__',arr(empty_modules))
            .replace('__GENERATED_RUNTIME__',arr(helpers)))
        return path
    try:
        inputs=out/'execution_inputs'
        shutil.copytree(audit,inputs/'audit',ignore=shutil.ignore_patterns('__pycache__'))
        report['audit_inputs']=[{'path':str(p.relative_to(audit)),'sha256':sha(p)}
            for p in sorted(audit.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
        binding=json.loads((audit/'runtime_bindings.json').read_text())
        for item in binding['files']:
            if sha(kit/item['path'])!=item['sha256']:raise ValueError('Runtime mismatch: '+item['path'])
        report['runtime_bindings_sha256']=sha(audit/'runtime_bindings.json')
        report['adapter_sha256']=sha(adapter)
        version=run('lean_version',[str(kit/'toolchain/bin/lean'),'--version']).strip()
        if version!=binding['lean_version']:raise ValueError('Lean version mismatch')
        report['lean_version']=version;report['dependencies']=[];upstream=[]
        for item in binding['dependencies']:
            dep=kit/'workspace/.lake/packages'/item['name']
            head=run('pin_'+item['name'],['git','-C',str(dep),'rev-parse','HEAD']).strip()
            dirty=run('clean_'+item['name'],['git','-C',str(dep),'status','--porcelain','--untracked-files=no']).strip()
            if head!=item['rev'] or dirty:raise ValueError('Dependency pin/worktree mismatch: '+item['name'])
            lib=dep/'.lake/build/lib/lean'
            if lib.is_dir():upstream.append(str(lib))
            report['dependencies'].append({'name':item['name'],'rev':head,'tracked_changes':dirty})
        upstream.append(str(kit/'toolchain/lib/lean'))
        env['LEAN_PATH']=os.pathsep.join([str(objects),*upstream]);report['lean_path']=env['LEAN_PATH']
        # Fail-closed ownership checks use precisely the same template as production.
        controls=['ForeignClean','InjectedAxiom','InjectedPlaceholder','InjectedOpaque','InjectedUnsafe']
        for name in controls:
            source=audit/'fixtures'/(name+'.lean')
            lean('compile_control_'+name,source,target=objects/(name+'.olean'),
                 cwd=source.parent,warning=name!='InjectedPlaceholder')
            check=owned_source([name],[],out/(name+'Audit.lean'))
            lean('guard_'+name,check,reject=name!='ForeignClean',
                 pattern='OWNED_AUDIT_PASS' if name=='ForeignClean' else 'OWNED AUDIT REJECTED')
        lean('negative_false_equality',audit/'fixtures/FalseEquality.lean',reject=True,
             pattern=r'unsolved goals|type mismatch|Tactic.*rfl.*failed')
        lean('negative_placeholder',audit/'fixtures/InjectedPlaceholder.lean',reject=True,
             pattern=r'declaration uses.*sorry')
        lean('negative_missing_positive',audit/'fixtures/MissingPositive.lean',reject=True,
             pattern=r'evaluated to.*false|is false|unsolved goals|type mismatch')
        lean('kernel_clean_control',audit/'ReplayClosure.lean',
             pattern=r'REPLAY_CLOSURE_PASS MODULES 1 CONSTANTS 1 NEW_NAME_REPLAYS 1',
             extra={'KOMOREBI_REPLAY_MODULES':'ForeignClean','KOMOREBI_REPLAY_CORRUPT':'0'})
        corrupt=lean('kernel_corrupt_control',audit/'ReplayClosure.lean',reject=True,
             pattern=r'kernel.*type mismatch|declaration type mismatch|type mismatch',
             extra={'KOMOREBI_REPLAY_MODULES':'ForeignClean','KOMOREBI_REPLAY_CORRUPT':'1'})
        if 'REPLAY_CORRUPT_CONTROL_INJECTED' not in corrupt or 'REPLAY_CLOSURE_PASS' in corrupt:
            raise ValueError('Corrupt theorem did not reach the kernel rejection control')
        report['negative_controls']=8
        if not args.controls_only:
            shutil.copy2(args.manifest,inputs/'release_modules.json')
            report['manifest_sha256']=sha(args.manifest)
            for row in rows:
                source=root/row['source'];snapshot=out/'source_snapshots'/row['source']
                snapshot.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,snapshot)
                target=(objects/Path(*row['module'].split('.'))).with_suffix('.olean')
                lean('compile_'+row['module'].replace('.','_'),source,target=target)
                if sha(source)!=row['source_sha256']:raise ValueError('Source changed: '+row['module'])
                report['source_files'].append({**row,'object':str(target.relative_to(out)),
                    'object_sha256':sha(target),'origin':'fresh_compile'});save()
            modules=[r['module'] for r in rows]
            check=owned_source(modules,empty,out/'OwnedAudit.lean',[h['name'] for h in reviewed_helpers])
            text=lean('owned_audit',check,pattern=r'OWNED_AUDIT_PASS \d+')
            owned=[json.loads(line[6:]) for line in text.splitlines() if line.startswith('OWNED ')]
            hit=re.search(r'OWNED_AUDIT_PASS (\d+) OUTSIDE_NAMESPACE (\d+)',text)
            if not hit or len(owned)!=int(hit[1]) or len({r['name'] for r in owned})!=len(owned):
                raise ValueError('Owned declaration inventory/count mismatch')
            runtime_owned={r['name']:r for r in owned if r['runtime_only']}
            if set(runtime_owned)!={h['name'] for h in reviewed_helpers}:
                raise ValueError('Runtime helper set differs from exact reviewed set')
            for helper in reviewed_helpers:
                for key in ['module','type_expr','value_expr','level_params','axioms']:
                    if runtime_owned[helper['name']][key]!=helper[key]:
                        raise ValueError('Runtime helper exact body/type changed: '+helper['name']+' '+key)
            (out/'owned_declarations.json').write_text(json.dumps(owned,indent=2)+'\n')
            text=lean('replay_whole_closure',audit/'ReplayClosure.lean',
                pattern=r'REPLAY_CLOSURE_PASS MODULES '+str(len(modules))+r' CONSTANTS \d+',
                extra={'KOMOREBI_REPLAY_MODULES':','.join(modules),'KOMOREBI_REPLAY_CORRUPT':'0'})
            replayed=[json.loads(line[len('REPLAY_CHECKED '):]) for line in text.splitlines() if line.startswith('REPLAY_CHECKED ')]
            if len(replayed)!=len({r['name'] for r in replayed}) or {r['name'] for r in replayed}!={r['name'] for r in owned if not r['runtime_only']}:
                raise ValueError('Replay is not the exact owned logical declaration set')
            runtime=[json.loads(line[len('REPLAY_RUNTIME_ONLY '):]) for line in text.splitlines() if line.startswith('REPLAY_RUNTIME_ONLY ')]
            if {r['name'] for r in runtime}!=set(runtime_owned) or len(runtime)!=len(runtime_owned):
                raise ValueError('Replay runtime-only set differs from audited set')
            if any(r['unsafe'] or not r['partial'] for r in runtime) or 'REPLAY_UPSTREAM_ONLY_PASS' not in text:
                raise ValueError('Unexpected runtime declaration or starting-environment boundary')
            (out/'replayed_constants.json').write_text(json.dumps(replayed,indent=2)+'\n')
            if inspect_sources(root)[0]!=rows or sha(args.manifest)!=report['manifest_sha256']:
                raise ValueError('Frozen production inputs changed during verification')
            for row in report['source_files']:
                if sha(out/row['object'])!=row['object_sha256']:raise ValueError('Compiled object changed')
            report.update(production_module_count=len(modules),owned_total=len(owned),
                owned_logical_total=len(owned)-len(runtime_owned),owned_runtime_only=len(runtime_owned),logical_checked_count=len(replayed),
                replay_exact_name_match=True,replay_starting_environment_excludes_project_modules=True,
                axioms=sorted({a for r in owned for a in r['axioms']}))
        for row in report['audit_inputs']:
            if sha(audit/row['path'])!=row['sha256']:raise ValueError('Audit input changed during run')
        report.update(status='PASS',elapsed_seconds=round(time.monotonic()-started,3),
            max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        save();print('PAPER_II_'+('AUDIT_CONTROLS' if args.controls_only else 'RELEASE_AUDIT')+'_PASS');return 0
    except Exception as error:
        report.update(status='FAIL',failure=type(error).__name__+': '+str(error),
                      elapsed_seconds=round(time.monotonic()-started,3))
        save();raise


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['root','kit','out']:parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--freeze-manifest',type=Path)
    parser.add_argument('--controls-only',action='store_true')
    parser.add_argument('--timeout',type=int,default=600)
    parser.add_argument('--lock-file',type=Path,default=Path(__file__).resolve().parents[2]/'lean_serial.lock')
    args=parser.parse_args()
    if not 0<args.timeout<86400:parser.error('Invalid timeout')
    if args.freeze_manifest:return execute(args)
    with args.lock_file.open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        return execute(args)


if __name__=='__main__':
    if not __debug__:raise SystemExit('Python optimization is not permitted')
    raise SystemExit(main())
