from pathlib import Path
import subprocess,os,sys,time,json,hashlib
root=Path(__file__).resolve().parents[1]
kit=Path('/mnt/data/portable_parts/Komorebi_Portable_Lean_4.34.0-rc2')
out=root/'development/olean';out.mkdir(exist_ok=True)
env=os.environ.copy();env['LEAN_PATH']=str(out)+':'+str(root/'src')+':'+str(root/'dependencies')+':'+(root/'development/LEAN_PATH.txt').read_text().strip()
for m in sys.argv[1:]:
 p=root/'src'/f'{m}.lean'
 if not p.exists():p=root/'dependencies'/f'{m}.lean'
 start=time.monotonic();cmd=[str(kit/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-R',str(p.parent),'-o',str(out/f'{m}.olean'),str(p)]
 try:
  cp=subprocess.run(cmd,cwd=kit/'workspace',env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=90);rc=cp.returncode;txt=cp.stdout
 except subprocess.TimeoutExpired as e:
  rc=124;txt=(e.stdout.decode() if isinstance(e.stdout,bytes) else e.stdout or '')+'\nTIMEOUT\n'
 logfile=root/'development/logs'/f'{m}.{time.time_ns()}.log';logfile.write_text(txt)
 rec={'module':m,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'returncode':rc,'seconds':round(time.monotonic()-start,3),'log':str(logfile.relative_to(root)),'command':cmd}
 with (root/'development/ATTEMPTS.jsonl').open('a') as f:f.write(json.dumps(rec)+'\n')
 print(m,'RC',rc,'SECONDS',rec['seconds'],flush=True);print(txt,flush=True)
 if rc:sys.exit(rc)
