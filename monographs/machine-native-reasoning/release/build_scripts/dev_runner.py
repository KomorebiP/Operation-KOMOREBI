from pathlib import Path
import subprocess,os,sys,json,time,hashlib,signal,shutil
ROOT=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25')
RT=Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2')
OBJ=Path('/mnt/data/core25/devobjects'); OBJ.mkdir(exist_ok=True)
p=Path(sys.argv[1]); src=ROOT/p
outdir=ROOT/'evidence/development18';outdir.mkdir(parents=True,exist_ok=True)
num=len(list(outdir.glob('attempt_*.json')))+1
base=f'attempt_{num:03d}_{p.stem}'
(outdir/(base+'.lean')).write_bytes(src.read_bytes())
sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
inputs={str(f.relative_to(ROOT)):sha(f) for f in sorted(ROOT.rglob('*.lean')) if 'evidence' not in f.parts}
env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[OBJ]+sorted((RT/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))));env['LEAN_NUM_THREADS']='1'
target=OBJ/p.with_suffix('.olean');target.parent.mkdir(parents=True,exist_ok=True)
cmd=[str(RT/'toolchain/bin/lean'),'-j1','-M4096','-DwarningAsError=true','-o',str(target),str(p)]
start=time.monotonic();timeout=False
s=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
try:text,_=s.communicate(timeout=45)
except subprocess.TimeoutExpired:
 os.killpg(s.pid,signal.SIGKILL);text,_=s.communicate();timeout=True
seconds=time.monotonic()-start
(outdir/(base+'.log')).write_text(text)
receipt={'command':cmd,'source':str(p),'source_sha256':sha(src),'local_source_hashes':inputs,'seconds':seconds,'exit_code':s.returncode,'timeout':timeout,'output_sha256':sha(target) if target.is_file() and s.returncode==0 and not timeout else None,'development_only':True}
(outdir/(base+'.json')).write_text(json.dumps(receipt,indent=2))
print(base,'EXIT',s.returncode,'SECONDS',round(seconds,3),'TIMEOUT',timeout);print(text)
sys.exit(0 if s.returncode==0 and not timeout else 1)
