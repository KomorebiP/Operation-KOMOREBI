"""Reproduce the consolidated current source without changing retained evidence.
Author: Komorebi P. Python standard library only; no network or solver packages.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parent
PACKAGE = ROOT.parent


def main():
    if not __debug__:
        raise RuntimeError('Assertions must remain enabled')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--current-only',action='store_true')
    args = parser.parse_args()
    out = (args.output or Path.cwd()/'smith-replay-runs'/datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')).resolve()
    if (out/'summary.json').exists():
        raise ValueError('Choose a fresh result directory')
    out.mkdir(parents=True,exist_ok=True)
    plan = json.loads((ROOT/'replay-plan.json').read_bytes())
    tasks = plan['tasks'] if not args.current_only else []
    archives = {}
    for key,entry in plan['archives'].items():
        source = PACKAGE/entry['path']
        if hashlib.sha256(source.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Retained archive checksum mismatch: '+key)
        if not tasks:
            continue
        dest = out/'inputs'/key
        dest.mkdir(parents=True,exist_ok=False)
        with zipfile.ZipFile(source) as archive:
            infos = archive.infolist()
            prefix = infos[0].filename.split('/')[0]+'/'
            if sum(i.file_size for i in infos)>40_000_000:
                raise ValueError('Checkpoint resource cap exceeded')
            for info in infos:
                path = PurePosixPath(info.filename)
                if (info.is_dir() or path.is_absolute() or '..' in path.parts or ':' in info.filename
                        or '\\' in info.filename or not info.filename.startswith(prefix)
                        or (info.external_attr>>16)&0o170000==0o120000):
                    raise ValueError('Unsafe checkpoint member')
                target = dest/info.filename[len(prefix):]
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(archive.read(info))
        archives[key] = dest
    env = os.environ.copy()
    local_temp = out/'temp'
    local_temp.mkdir(exist_ok=True)
    env.update(TEMP=str(local_temp),TMP=str(local_temp),PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',
        OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',KOMOREBI_CHECK_ONLY='1')
    rows = []
    for task in tasks+[{'id':'current-exact-suites','arguments':['solver/check_current_routes.py'],'archive':None}]:
        if task['archive'] is None:
            work = ROOT
        else:
            work = out/'workspaces'/task['id']
            shutil.copytree(archives[task['archive']],work)
        cmd = [sys.executable,'-B','-S']+task['arguments']
        print('RUN '+task['id'],flush=True)
        start = time.monotonic()
        result = subprocess.run(cmd,cwd=work,env=env,capture_output=True,timeout=240)
        for stream,raw in (('stdout',result.stdout),('stderr',result.stderr)):
            (out/(task['id']+'.'+stream+'.txt')).write_bytes(raw)
        status = 'PASS' if result.returncode==0 else 'FAIL'
        rows.append({'id':task['id'],'command':cmd,'status':status,'returncode':result.returncode,
            'seconds':round(time.monotonic()-start,3),'stdout_sha256':hashlib.sha256(result.stdout).hexdigest(),
            'stderr_sha256':hashlib.sha256(result.stderr).hexdigest()})
        print(status+' '+task['id'],flush=True)
    unchanged = all(hashlib.sha256((PACKAGE/e['path']).read_bytes()).hexdigest()==e['sha256'] for e in plan['archives'].values())
    summary = {'status':'PASS' if all(r['status']=='PASS' for r in rows) and unchanged else 'FAIL',
        'author':'Komorebi P.','python':sys.version,'commands':len(rows),'retained_archives_unchanged':unchanged,
        'results':rows,'scope':'Reproduced finite checks in isolated copies; no independent implementation validation or formal universal proof'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2))
    return 0 if summary['status']=='PASS' else 1


if __name__=='__main__':
    raise SystemExit(main())
