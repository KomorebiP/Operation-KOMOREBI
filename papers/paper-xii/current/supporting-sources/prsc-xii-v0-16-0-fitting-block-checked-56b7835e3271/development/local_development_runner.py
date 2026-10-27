#!/usr/bin/env python3
from pathlib import Path
import os,subprocess,sys,time,json,hashlib,signal
ROOT=Path(__file__).resolve().parents[1]
KIT=Path('/mnt/data/files/Komorebi_Portable_Lean_4.34.0-rc2')
WORKSPACE=KIT/'workspace'
SRC=ROOT/'lean'/sys.argv[1]
args=sys.argv[2:]
LEAN=KIT/'toolchain/bin/lean'
env=os.environ.copy()
paths=[ROOT/'build',Path('/mnt/data/xii_work/PRSC_XII_v0.15.0/build'),WORKSPACE/'.lake/build/lib/lean']+sorted((WORKSPACE/'.lake/packages').glob('*/.lake/build/lib/lean'))
env['LEAN_PATH']=os.pathsep.join(map(str,paths))
name=SRC.stem
out=ROOT/'build'/SRC.relative_to(ROOT/'lean').with_suffix('.olean')
out.parent.mkdir(parents=True,exist_ok=True)
cmd=[str(LEAN),'-j1','-DwarningAsError=true','-o',str(out),str(SRC)]
start=time.monotonic()
p=subprocess.Popen(cmd,env=env,cwd=ROOT/'lean',stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
try:
 text,_=p.communicate(timeout=180)
except subprocess.TimeoutExpired:
 os.killpg(p.pid,signal.SIGKILL);text,_=p.communicate();text+='\nTIMEOUT after 180 seconds\n'
idx=len(list((ROOT/'development').glob(name+'_attempt*.log')))+1
log=ROOT/'development'/f'{name}_attempt{idx:03}.log';log.write_text(text)
meta={'source':str(SRC.relative_to(ROOT)),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'command':cmd,'seconds':time.monotonic()-start,'exit_code':p.returncode,'log':str(log.relative_to(ROOT))}
(ROOT/'development'/f'{name}_attempt{idx:03}.json').write_text(json.dumps(meta,indent=2))
print(text,end='');print(json.dumps(meta,indent=2))
sys.exit(p.returncode)
