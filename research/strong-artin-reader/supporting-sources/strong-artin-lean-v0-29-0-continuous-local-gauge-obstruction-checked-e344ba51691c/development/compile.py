from pathlib import Path
import os,sys,subprocess,json,time,hashlib
root=Path(__file__).resolve().parents[1]
kit=Path('/mnt/data/portable_parts/Komorebi_Portable_Lean_4.34.0-rc2')
obj=root/'development/olean';obj.mkdir(exist_ok=True)
stage=root/'development/stage';stage.mkdir(exist_ok=True)
env=os.environ.copy();env['LEAN_PATH']=str(obj)+':'+str(stage)+':'+(root/'development/LEAN_PATH.txt').read_text()
for m in sys.argv[1:]:
 p=root/'src'/f'{m}.lean'
 if not p.exists():p=root/'dependencies'/f'{m}.lean'
 dst=stage/p.name;dst.write_bytes(p.read_bytes())
 stamp=time.time_ns(); log=root/'development/logs'/f'{m}.{stamp}.log'
 cmd=[str(kit/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-R',str(stage),'-o',str(obj/f'{m}.olean'),str(dst)]
 t=time.monotonic()
 try:
  proc=subprocess.run(cmd,cwd=kit/'workspace',env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=65)
  rc=proc.returncode;out=proc.stdout
 except subprocess.TimeoutExpired as e:rc=124;out=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else e.stdout or ''
 log.write_text(out)
 record={'module':m,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'command':cmd,'returncode':rc,'seconds':time.monotonic()-t,'log':str(log.relative_to(root))}
 with (root/'development/ATTEMPTS.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
 print(m,'RC',rc,'seconds',round(record['seconds'],2));print(out,flush=True)
 if rc:sys.exit(rc)
