#!/usr/bin/env python3
"""Check named modules in separate pinned Lean processes, preserving per-run evidence.

Use --modules in dependency order. To reproduce from scratch, use --clean first,
then run bounded groups from MODULE_ORDER.json. No network access is used.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, shutil, signal, subprocess, time
from pathlib import Path
PIN='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
LC='6a10ac8c22beadecabdbb0919c2b50214762f91d'
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--modules',nargs='*')
    ap.add_argument('--timeout',type=int,default=25)
    ap.add_argument('--clean',action='store_true')
    a=ap.parse_args(); root=Path(__file__).resolve().parent
    rt=a.runtime.resolve(); ws=rt/'workspace'; launch=rt/'run.sh'
    version=subprocess.check_output(['bash',str(launch),'lean','--version'],text=True).strip()
    if '4.34.0-rc2' not in version or LC not in version: raise RuntimeError(version)
    ml=ws/'.lake/packages/mathlib'
    commit=subprocess.check_output(['git','-c',f'safe.directory={ml}','-C',str(ml),'rev-parse','HEAD'],text=True).strip()
    if commit!=PIN: raise RuntimeError('Wrong mathlib '+commit)
    sources=root/'Komorebi'; staged=ws/'Komorebi'; staged.mkdir(exist_ok=True)
    cache=ws/'.lake/build/lib/lean/Komorebi'; cache.mkdir(parents=True,exist_ok=True)
    allmods=json.loads((root/'MODULE_ORDER.json').read_text())
    names=a.modules if a.modules is not None else allmods
    if a.clean:
        for n in allmods:
            for p in cache.glob(n+'.olean*'): p.unlink()
        (root/'audit/CLEAN_START.json').write_text(json.dumps({'time':dt.datetime.now(dt.timezone.utc).isoformat(),'project_cache_removed':allmods,'mathlib_cache_reused':True},indent=2)+'\n')
    for name in names:
        src=sources/(name+'.lean')
        if not src.is_file(): raise RuntimeError('Missing '+str(src))
        text=src.read_text()
        if re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',text):
            raise RuntimeError('Forbidden token in '+name)
        shutil.copy2(src,staged/src.name)
        stamp=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        ad=root/'audit'/stamp; ad.mkdir(parents=True)
        # Retain the exact attempted source, including failed drafts.
        shutil.copy2(src,ad/(name+'.lean'))
        out=cache/(name+'.olean'); log=ad/(name+'.log')
        deps={}
        for dep in re.findall(r'^(?:public )?import (Komorebi\.\w+)',text,re.M):
            dn=dep.rsplit('.',1)[1]; dp=cache/(dn+'.olean'); ds=sources/(dn+'.lean')
            if not dp.is_file(): raise RuntimeError('Dependency not compiled '+dep)
            deps[dep]={'olean_sha256':sha(dp),'source_sha256':sha(ds) if ds.exists() else None}
        argv=['bash',str(launch),'lake','env','lean','-j1','-DwarningAsError=true','-o',str(out),'Komorebi/'+name+'.lean']
        before=sha(src); t=time.monotonic()
        with log.open('w') as f:
            p=subprocess.Popen(argv,cwd=ws,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
            try: rc=p.wait(timeout=a.timeout)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGKILL); p.wait(); rc=124
        record={'module':name,'argv':argv,'cwd':str(ws),'started_at_utc':stamp,
                'elapsed_seconds':round(time.monotonic()-t,3),'exit_status':rc,'timeout_seconds':a.timeout,
                'threads':1,'lean_version':version,'mathlib_commit':commit,'source_sha256_before':before,
                'source_sha256_after':sha(src),'staged_source_sha256':sha(staged/src.name),
                'dependencies':deps,'log_sha256':sha(log),'output_sha256':sha(out) if rc==0 and out.exists() else None}
        if before!=record['source_sha256_after'] or before!=record['staged_source_sha256']:
            rc=125;record['exit_status']=rc
        (ad/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
        print(name,'RC',rc,'seconds',record['elapsed_seconds'],flush=True)
        if rc:
            for p in cache.glob(name+'.olean*'):p.unlink()
            print(log.read_text(),flush=True)
            return rc
    return 0
if __name__=='__main__':
    raise SystemExit(main())
