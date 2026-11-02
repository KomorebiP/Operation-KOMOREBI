"""Standalone native Lean runner shipped with the site's source bundle.

Uses retained Lake projects where available. Otherwise constructs an explicitly
labelled workspace from unchanged local import sources and a pinned environment.
Only the selected file is checked; this is not an axiom or whole-paper audit.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import subprocess
import sys
import time

EXTERNAL_ROOTS = {'Init', 'Std', 'Lean', 'Lake', 'Mathlib', 'Batteries', 'Aesop',
                  'Qq', 'Plausible', 'ProofWidgets', 'Cli', 'ImportGraph', 'LeanSearchClient'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def safe_path(value):
    if (not isinstance(value, str) or not value or '\\' in value or ':' in value
            or any(ord(c) < 32 for c in value) or value.startswith('/')
            or any(p in {'', '.', '..'} for p in value.split('/'))):
        raise ValueError('Expected a relative source path: '+repr(value))
    return value


def imports(text):
    """Mask nested comments and strings before recognizing import lines.

    This is source routing, not a Lean parser or a proof check. Unsupported
    import syntax stops workspace construction instead of inventing a module.
    """
    clean=list(text); i=depth=0; string=False
    while i < len(text):
        pair=text[i:i+2]
        if depth:
            width=2 if pair in {'/-', '-/'} else 1
            if pair == '/-':depth+=1
            elif pair == '-/':depth-=1
        elif string:
            width=2 if text[i] == '\\' else 1
            if text[i] == '"':string=False
        elif pair == '/-':depth=1;width=2
        elif pair == '--':
            end=text.find('\n',i)
            width=(len(text) if end < 0 else end)-i
        elif text[i] == '"':string=True;width=1
        else:i+=1;continue
        for j in range(i,min(i+width,len(text))):
            if clean[j] != '\n':clean[j]=' '
        i+=width
    result=[]
    for match in re.finditer(r'(?m)^\s*(?:(?:public|private|meta)\s+)*import\s+([^\n]+)', ''.join(clean)):
        names=match[1].split()
        if len(names)>1 and names[0]=='all':names=names[1:]
        for name in names:
            if not re.fullmatch(r"[^\W\d][\w']*(?:\.[^\W\d][\w']*)*",name):
                raise ValueError('Unsupported import syntax: '+name)
            if name not in result:result.append(name)
    return result


class Collection:
    def __init__(self, catalog, read):
        self.data=catalog;self.read_raw=read
        self.inputs=catalog['inputs'];self.sources={s['path']:s for s in catalog['sources']}
        self.by_name=defaultdict(list);self.import_cache={}
        for path, entry in self.inputs.items():
            if path.endswith('.lean') and PurePosixPath(path).name != 'lakefile.lean':
                self.by_name[(entry['work'],PurePosixPath(path).name)].append(path)

    def read(self,path):
        safe_path(path);entry=self.inputs[path];raw=self.read_raw(path)
        if digest(raw) != entry['sha256']:
            raise ValueError('Source bytes differ from the bundle record: '+path)
        return raw

    def module_imports(self,path):
        if path not in self.import_cache:
            self.import_cache[path]=imports(self.read(path).decode('utf-8-sig'))
        return self.import_cache[path]

    def resolve(self, name, importer):
        work=self.inputs[importer]['work'];suffix=name.replace('.','/')+'.lean'
        candidates=[p for p in self.by_name[(work,PurePosixPath(suffix).name)]
                    if p == suffix or p.endswith('/'+suffix)]
        if not candidates:raise ValueError('Missing local import '+name+' requested by '+importer)
        origin=PurePosixPath(importer).parent.parts
        def score(path):
            target=PurePosixPath(path).parent.parts;shared=0
            for a,b in zip(origin,target):
                if a != b:break
                shared+=1
            return (shared,-(len(origin)+len(target)-2*shared))
        best=max(map(score,candidates));chosen=[p for p in candidates if score(p)==best]
        if len(chosen) != 1:
            # Identical leaf modules have the same source and only pinned external
            # imports. Selecting their lexical first copy does not mix local editions.
            if (len({self.inputs[p]['sha256'] for p in chosen})==1 and
                    all(n.split('.')[0] in EXTERNAL_ROOTS for n in self.module_imports(chosen[0]))):
                return sorted(chosen)[0]
            raise ValueError('Ambiguous local import '+name+': '+'; '.join(sorted(chosen)))
        return chosen[0]

    def plan(self,path):
        safe_path(path)
        if path not in self.sources:raise ValueError('File is not in the selected reading collection: '+path)
        source=self.sources[path];native=source.get('project')
        if native:
            project=self.data['projects'][native]
            files={p[len(native)+1:]:p for p in project['files']}
            return dict(mode='retained-project',toolchain=project['toolchain'],project=native,
                        target=path[len(native)+1:],files=files,generated={},issues=[])
        selected='SelectedProof.lean';files={selected:path};modules={};active=[];issues=[]
        def visit(current):
            if current in active:raise ValueError('Local import cycle: '+' -> '.join(active+[current]))
            active.append(current)
            try:
                for name in self.module_imports(current):
                    if name.split('.')[0] in EXTERNAL_ROOTS:continue
                    dependency=self.resolve(name,current)
                    if name in modules:
                        if modules[name] != dependency:
                            raise ValueError('Two source editions requested for module '+name)
                        continue
                    modules[name]=dependency;files[name.replace('.','/')+'.lean']=dependency
                    visit(dependency)
            finally:active.pop()
        try:visit(path)
        except ValueError as error:issues.append(str(error))
        roots=sorted({'SelectedProof'}|{name.split('.')[0] for name in modules})
        fallback=self.data['fallback'];lock=dict(fallback['lock']);lock['name']='KomorebiCollectionRun'
        config=('name = "KomorebiCollectionRun"\nversion = "0.1.0"\n\n'
                '[[require]]\nname = "mathlib"\ngit = "https://github.com/leanprover-community/mathlib4.git"\n'
                'rev = "'+fallback['mathlib']+'"\n\n[[lean_lib]]\nname = "Collection"\nroots = '+json.dumps(roots)+'\n')
        generated={'lakefile.toml':config,'lean-toolchain':fallback['toolchain']+'\n',
                   'lake-manifest.json':json.dumps(lock,indent=2)+'\n'}
        return dict(mode='reconstructed-workspace',toolchain=fallback['toolchain'],project=None,
                    target=selected,files=files,generated=generated,issues=issues)


def open_collection(root):
    root=Path(root).resolve();data=json.loads((root/'CATALOG.json').read_bytes())
    def read(path):
        target=(root/'inputs'/safe_path(path)).resolve()
        if not target.is_relative_to(root/'inputs'):raise ValueError('Input escapes the bundle')
        return target.read_bytes()
    return Collection(data,read)


def prepare(collection, source, output, leanweb_project=None):
    plan=collection.plan(source)
    if plan['issues']:raise ValueError('\n'.join(plan['issues']))
    if leanweb_project and not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}',leanweb_project):
        raise ValueError('Lean web project name must be an ASCII identifier')
    if leanweb_project and any(p in plan['files'] for p in ('leanweb-config.json','leanweb-build.sh',leanweb_project+'.lean')):
        raise ValueError('Lean web entry would replace a retained source; choose another project name')
    output=Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    project=output/'project';project.mkdir()
    inputs={}
    for relative,original in plan['files'].items():
        safe_path(relative);raw=collection.read(original)
        dest=project/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        mode=collection.inputs[original].get('mode','100644');dest.chmod(int(mode,8)&0o777)
        inputs[relative]=dict(original_path=original,sha256=digest(raw),generated=False,mode=mode)
    for relative,text in plan['generated'].items():
        raw=text.encode('utf-8');(project/relative).write_bytes(raw)
        inputs[relative]=dict(sha256=digest(raw),generated=True)
    if leanweb_project:
        target=leanweb_project+'.lean';raw=collection.read(source);(project/target).write_bytes(raw)
        inputs[target]=dict(original_path=source,sha256=digest(raw),generated=False)
        config=dict(name=leanweb_project+' · '+plan['mode'],default=False,hidden=False,
                    examples=[dict(file=target,name=PurePosixPath(source).name)])
        generated={'leanweb-config.json':json.dumps(config,indent=2)+'\n',
                   'leanweb-build.sh':'#!/usr/bin/env bash\nset -euo pipefail\ncd -- "$(dirname -- "$0")"\nlake exe cache get\nlake setup-file '+target+'\n'}
        for relative,text in generated.items():
            raw=text.encode();(project/relative).write_bytes(raw);inputs[relative]=dict(sha256=digest(raw),generated=True)
        (project/'leanweb-build.sh').chmod(0o755)
    else:target=plan['target']
    record=dict(schema=1,source_revision=collection.data['source_revision'],source=source,
                source_sha256=collection.sources[source]['sha256'],mode=plan['mode'],
                retained_project=plan['project'],toolchain=plan['toolchain'],target=target,
                leanweb_project=leanweb_project,
                inputs=inputs,scope='One selected file; no whole-paper replay or axiom audit.')
    (output/'RUN_INPUTS.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    return output


def validate_workspace(output, record):
    project=(output/'project').resolve()
    for path,entry in record['inputs'].items():
        target=(project/safe_path(path)).resolve()
        if not target.is_relative_to(project) or digest(target.read_bytes()) != entry['sha256']:
            raise ValueError('Workspace input changed: '+path)
        if os.name!='nt' and 'mode' in entry and target.stat().st_mode&0o777 != int(entry['mode'],8)&0o777:
            raise ValueError('Workspace input permissions changed: '+path)
    if (project/'lean-toolchain').read_text(encoding='utf-8').strip() != record['toolchain']:
        raise ValueError('Workspace toolchain changed')


def diagnostics(stdout):
    messages=[]
    for line in stdout.splitlines():
        try:message=json.loads(line)
        except (ValueError,TypeError):continue
        if isinstance(message,dict) and 'severity' in message:messages.append(message)
    return messages


def execute(output, timeout=1200, skip_cache=False):
    output=Path(output).resolve();record=json.loads((output/'RUN_INPUTS.json').read_bytes())
    validate_workspace(output,record)
    result=dict(record,started_at=datetime.now(timezone.utc).isoformat(),steps=[],status='setup_failed',
                compiler_exit_code=None,diagnostics=[],changes_recorded_verification=False)
    deadline=time.monotonic()+timeout
    def step(name,args):
        started=time.monotonic();stdout=stderr='';exit_code=None;timed_out=False
        try:
            kwargs={'start_new_session':True} if os.name != 'nt' else {'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP}
            process=subprocess.Popen(args,cwd=output/'project',stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                    env={**os.environ,'GIT_TERMINAL_PROMPT':'0','LEAN_NUM_THREADS':os.environ.get('LEAN_NUM_THREADS','2')},**kwargs)
            try:
                raw_out,raw_err=process.communicate(timeout=max(.1,deadline-time.monotonic()))
            except subprocess.TimeoutExpired:
                timed_out=True
                if os.name == 'nt':subprocess.run(['taskkill','/PID',str(process.pid),'/T','/F'],capture_output=True)
                else:os.killpg(process.pid,signal.SIGKILL)
                raw_out,raw_err=process.communicate()
            exit_code=process.returncode;stdout=raw_out.decode('utf-8',errors='replace');stderr=raw_err.decode('utf-8',errors='replace')
        except OSError as error:stderr=str(error)
        (output/(name+'.stdout.log')).write_text(stdout,encoding='utf-8')
        (output/(name+'.stderr.log')).write_text(stderr,encoding='utf-8')
        entry=dict(name=name,command=args,exit_code=exit_code,timed_out=timed_out,
                   seconds=round(time.monotonic()-started,3),stdout_sha256=digest(stdout.encode()),stderr_sha256=digest(stderr.encode()))
        result['steps'].append(entry)
        return entry,stdout,stderr
    try:
        entry,version,_=step('version',['lake','env','lean','--version']);result['actual_version']=version.strip()
        if entry['timed_out']:result['status']='timed_out'
        elif entry['exit_code'] == 0:
            stages=[] if skip_cache else [('cache',['lake','exe','cache','get'])]
            stages += [('imports',['lake','setup-file',record['target']]),
                       ('check',['lake','lean',record['target'],'--','--json'])]
            for name,command in stages:
                entry,stdout,stderr=step(name,command)
                if entry['timed_out']:result['status']='timed_out';break
                if name == 'check':
                    result['compiler_exit_code']=entry['exit_code'];result['diagnostics']=diagnostics(stdout)
                    warnings=[m for m in result['diagnostics'] if m['severity']=='warning']
                    errors=[m for m in result['diagnostics'] if m['severity']=='error']
                    result['status']=('compiler_success_with_warnings' if warnings else 'compiler_success') if entry['exit_code']==0 and not errors else 'compiler_failure'
                    result['warning_count']=len(warnings)
                    result['sorry_diagnostic']=any('sorry' in str(m).lower() for m in warnings+errors)
                elif entry['exit_code'] != 0:result['status']=name+'_setup_failed';break
        validate_workspace(output,record)
    except (OSError,ValueError) as error:
        result['status']='input_or_environment_changed';result['error']=str(error)
    result['finished_at']=datetime.now(timezone.utc).isoformat()
    (output/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--source',help='Exact repository path from CATALOG.json')
    parser.add_argument('--list',action='store_true')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--execute',type=Path,help='Run an already prepared workspace')
    parser.add_argument('--skip-cache',action='store_true')
    parser.add_argument('--timeout',type=int,default=1200)
    parser.add_argument('--github-output',type=Path)
    parser.add_argument('--leanweb-project',help='Also export a named project for a dedicated lean4web server')
    args=parser.parse_args()
    if not 1 <= args.timeout <= 7200:parser.error('timeout must be between 1 and 7200 seconds')
    if args.execute:
        result=execute(args.execute,args.timeout,args.skip_cache)
    else:
        collection=open_collection(args.bundle)
        if args.list:
            for path in collection.sources:print(path)
            return 0
        if not args.source or not args.output:parser.error('--source and --output are required')
        output=prepare(collection,args.source,args.output,args.leanweb_project)
        if args.github_output:
            with args.github_output.open('a',encoding='utf-8') as stream:stream.write('project='+str(output/'project')+'\n')
        if args.prepare_only:
            print(json.dumps(dict(workspace=str(output),status='prepared',lean_executed=False)));return 0
        result=execute(output,args.timeout,args.skip_cache)
    print(json.dumps({k:result.get(k) for k in ('source','mode','toolchain','status','compiler_exit_code','warning_count')}))
    return 0 if result['status']=='compiler_success' else 1


if __name__ == '__main__':
    try:sys.exit(main())
    except (OSError,ValueError,KeyError) as error:print('Lean runner: '+str(error),file=sys.stderr);sys.exit(2)
