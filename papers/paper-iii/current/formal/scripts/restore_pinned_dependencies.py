#!/usr/bin/env python3
"""Restore this release's exact Git pins, optionally obtaining their mathlib cache.

Existing dependency directories are reused only when their HEAD is the recorded
revision and their tracked files are unmodified. No mismatched tree is overwritten.
"""
from pathlib import Path
import argparse, concurrent.futures, datetime, hashlib, json, os, shutil, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--lean',type=Path,help='Path to the exact pinned Lean executable; otherwise use PATH')
    ap.add_argument('--cache',action='store_true',help='Download compiled files for the pinned mathlib revision')
    args=ap.parse_args()
    manifest=json.loads((ROOT/'lake-manifest.json').read_text())
    report={'schema':'paper-iii.dependency-restore/1','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':[],'packages':[]}
    def command(cmd,cwd=None,env=None):
        r=subprocess.run(list(map(str,cmd)),cwd=cwd,env=env,capture_output=True,text=True)
        return {'command':list(map(str,cmd)),'cwd':str(cwd) if cwd else None,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    executable=args.lean or (Path(shutil.which('lean')) if shutil.which('lean') else None)
    if executable is None:raise SystemExit('Install the compiler pinned in lean-toolchain, or pass --lean PATH')
    executable=executable.resolve()
    version=command([executable,'--version']);report['commands'].append(version)
    expected=(ROOT/'lean-toolchain').read_text().strip().split(':v')[-1]
    if version['exit_code']!=0 or f'version {expected},' not in version['stdout']:
        raise SystemExit('Compiler does not report the exact pinned version: '+version['stdout']+version['stderr'])
    packages=ROOT/manifest['packagesDir'];packages.mkdir(parents=True,exist_ok=True)
    def restore(spec):
        dest=packages/spec['name'];rows=[]
        if dest.exists():
            head=command(['git','-C',dest,'rev-parse','HEAD']);rows.append(head)
            clean=command(['git','-C',dest,'diff','--quiet','HEAD','--']);rows.append(clean)
            good=head['exit_code']==0 and head['stdout'].strip()==spec['rev'] and clean['exit_code']==0
            return {'name':spec['name'],'expected_revision':spec['rev'],'reused':True,'passed':good,'commands':rows}
        for cmd in [
            ['git','init',dest],
            ['git','-C',dest,'remote','add','origin',spec['url']],
            ['git','-C',dest,'fetch','--depth','1','origin',spec['rev']],
            ['git','-C',dest,'-c','advice.detachedHead=false','checkout','--detach',spec['rev']],
            ['git','-C',dest,'rev-parse','HEAD'],
        ]:
            r=command(cmd);rows.append(r)
            if r['exit_code']!=0:return {'name':spec['name'],'passed':False,'commands':rows}
        return {'name':spec['name'],'expected_revision':spec['rev'],'reused':False,'passed':rows[-1]['stdout'].strip()==spec['rev'],'commands':rows}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        report['packages']=list(pool.map(restore,manifest['packages']))
    good=all(r['passed'] for r in report['packages'])
    if good and args.cache:
        lake=executable.with_name('lake.exe' if executable.name.endswith('.exe') else 'lake')
        env=os.environ.copy();env['PATH']=str(executable.parent)+os.pathsep+env.get('PATH','')
        r=command([lake,'exe','cache','get'],cwd=ROOT,env=env);report['commands'].append(r)
        good=r['exit_code']==0
    report['status']='PASS' if good else 'FAIL'
    report['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    directory=ROOT/'verification';directory.mkdir(exist_ok=True)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output=directory/('DEPENDENCY_RESTORE_'+stamp+'.json')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'receipt':str(output),'packages':len(report['packages'])}))
    return 0 if good else 1

if __name__=='__main__':raise SystemExit(main())
