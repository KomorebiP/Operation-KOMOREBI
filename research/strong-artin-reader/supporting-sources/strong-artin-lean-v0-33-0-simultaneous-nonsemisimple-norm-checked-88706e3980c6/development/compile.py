from pathlib import Path
import subprocess,hashlib,json,time,os,sys
root=Path(__file__).resolve().parent.parent
kit=Path('/mnt/data/portable_parts/Komorebi_Portable_Lean_4.34.0-rc2');ws=kit/'workspace'
lpf=root/'development/LEAN_PATH.txt'
if not lpf.exists():lpf.write_text(subprocess.check_output(['bash',str(kit/'run.sh'),'lake','env','printenv','LEAN_PATH'],cwd=ws,text=True).strip())
env=os.environ.copy();env['LEAN_PATH']=':'.join([str(root/'development/olean'),str(root/'src'),str(root/'dependencies'),lpf.read_text()]);env['PATH']=str(kit/'toolchain/bin')+':'+env.get('PATH','')
for mod in sys.argv[1:]:
 p=root/'src'/f'{mod}.lean'
 if not p.exists():p=root/'dependencies'/f'{mod}.lean'
 stamp=str(time.time_ns());text=p.read_bytes();sha=hashlib.sha256(text).hexdigest()
 (root/'development/snapshots'/f'{mod}.{stamp}.lean').write_bytes(text)
 obj=root/'development/olean'/f'{mod}.olean';log=root/'development/logs'/f'{mod}.{stamp}.log'
 cmd=[str(kit/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-R',str(root),'-o',str(obj),str(p)]
 t=time.monotonic()
 try:
  r=subprocess.run(cmd,cwd=ws,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
  rc=r.returncode;output=r.stdout
 except subprocess.TimeoutExpired as e:
  rc=124;output=(e.stdout.decode(errors='replace') if isinstance(e.stdout,bytes) else e.stdout) or ''
 log.write_text(output)
 rec={'module':mod,'source_sha256':sha,'command':cmd,'returncode':rc,'seconds':time.monotonic()-t,'log':str(log.relative_to(root)),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest() if rc==0 and obj.exists() else None}
 with (root/'development/ATTEMPTS.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
 print(mod,'RC',rc,'seconds',round(rec['seconds'],2));print(output,flush=True)
 if rc:sys.exit(rc)
