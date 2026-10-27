#!/usr/bin/env python3
"""Compile one pinned Lean source into an isolated object tree and save an exact receipt."""
from __future__ import annotations
import argparse,datetime,hashlib,json,os,pathlib,subprocess,time

def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('module');p.add_argument('--kit',type=pathlib.Path,required=True)
    p.add_argument('--timeout',type=int,default=180);p.add_argument('--tag',default='development')
    p.add_argument('--objects',type=pathlib.Path);p.add_argument('--source-root',type=pathlib.Path)
    a=p.parse_args(); root=pathlib.Path(__file__).resolve().parents[1]
    src=(a.source_root or root/'formal/current').resolve();objects=(a.objects or root/'build/objects').resolve()
    objects.mkdir(parents=True,exist_ok=True)
    source=src/(a.module.replace('.','/')+'.lean')
    if not source.is_file():raise FileNotFoundError(source)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run=root/'verification'/a.tag/(a.module.replace('.','_')+'_'+stamp);run.mkdir(parents=True)
    snapshot=run/'source.lean';snapshot.write_bytes(source.read_bytes())
    outfile=objects/(a.module.replace('.','/')+'.olean');outfile.parent.mkdir(parents=True,exist_ok=True)
    for candidate in [outfile, pathlib.Path(str(outfile)+'.server'), pathlib.Path(str(outfile)+'.private'), outfile.with_suffix('.ilean')]:
        candidate.unlink(missing_ok=True)
    env=os.environ.copy()
    for key in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME'):env.pop(key,None)
    libs=sorted((a.kit/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
    env['LEAN_PATH']=os.pathsep.join(map(str,[objects,*libs]))
    env['PATH']=str(a.kit/'toolchain/bin')+os.pathsep+env.get('PATH','')
    cmd=[str(a.kit/'toolchain/bin/lean'),'-j1','-M4096','-DwarningAsError=true','-DmaxHeartbeats=8000000','-o',str(outfile),str(source.relative_to(src))]
    receipt={'module':a.module,'source':str(source.relative_to(root)),'source_sha256':digest(snapshot),'command':cmd,'cwd':str(src),'LEAN_PATH':env['LEAN_PATH'],'timeout_seconds':a.timeout,'status':'RUNNING','started_utc':stamp}
    (run/'receipt.json').write_text(json.dumps(receipt,indent=2));start=time.monotonic()
    try:
      with (run/'compile.log').open('w') as log:
        result=subprocess.run(cmd,cwd=src,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=a.timeout)
      receipt['exit_code']=result.returncode
      receipt['status']='PASS' if result.returncode==0 and outfile.is_file() else 'FAIL'
    except subprocess.TimeoutExpired:
      receipt.update(status='TIMEOUT',exit_code=None)
    receipt['elapsed_seconds']=time.monotonic()-start
    receipt['source_after_sha256']=digest(source)
    receipt['source_unchanged']=receipt['source_after_sha256']==receipt['source_sha256']
    if not receipt['source_unchanged']:receipt['status']='SOURCE_CHANGED'
    if outfile.is_file():receipt['object_sha256']=digest(outfile)
    receipt['output_artifacts']=[{'path':str(p.relative_to(root)), 'sha256':digest(p), 'bytes':p.stat().st_size} for p in (outfile,pathlib.Path(str(outfile)+'.server'),pathlib.Path(str(outfile)+'.private')) if p.is_file()]
    receipt['log_sha256']=digest(run/'compile.log')
    (run/'receipt.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({'module':a.module,'status':receipt['status'],'seconds':receipt['elapsed_seconds'],'receipt':str(run/'receipt.json')}),flush=True)
    if receipt['status']!='PASS':
      lines=(run/'compile.log').read_text().splitlines()
      for i,line in enumerate(lines):
        if 'error:' in line or line.startswith(('REPLAY_', 'OWNED AUDIT REJECTED')):
          print('\n'.join(lines[i:i+5])[:3000])
    return 0 if receipt['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
