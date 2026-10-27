#!/usr/bin/env python3
"""Compile one exact project module, recording failures as well as successes."""
import datetime, hashlib, json, os, pathlib, subprocess, sys, time, shutil
ROOT=pathlib.Path('/mnt/data/lean_runtime_parts/Komorebi_Portable_Lean_4.34.0-rc2')
WORK=pathlib.Path('/mnt/data/fd_bayes_work')
SRC=WORK/'src'; LOG=WORK/'audit'; LOG.mkdir(exist_ok=True)
name=sys.argv[1]
source=SRC/'Komorebi'/f'{name}.lean'
out=ROOT/'workspace/.lake/build/lib/lean/Komorebi'/f'{name}.olean'
out.parent.mkdir(parents=True,exist_ok=True)
count=len(list(LOG.glob(f'{name}.*.json')))+1
log=LOG/f'{name}.{count:02d}.log'
cmd=['bash',str(ROOT/'run.sh'),'lake','env','lean','-DwarningAsError=true','-o',str(out),f'Komorebi/{name}.lean']
shutil.copy2(source, ROOT/'workspace/Komorebi'/source.name)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'module':name,'source_sha256_before':sha(source),'command':cmd,'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timeout_seconds':75}
t=time.monotonic()
with log.open('w') as f:
 try:
  r=subprocess.run(cmd,cwd=ROOT/'workspace',stdout=f,stderr=subprocess.STDOUT,timeout=75)
  rc=r.returncode
 except subprocess.TimeoutExpired:
  rc=124
record.update(exit_status=rc,runtime_seconds=round(time.monotonic()-t,3),source_sha256_after=sha(source),log_sha256=sha(log))
if rc==0:
 record['olean_sha256']=sha(out)
else:
 # Never expose an older output after a failed new check.
 out.unlink(missing_ok=True)
(LOG/f'{name}.{count:02d}.json').write_text(json.dumps(record,indent=2)+'\n')
print(name,'RC',rc,'SECONDS',record['runtime_seconds'],flush=True)
print(log.read_text(),flush=True)
sys.exit(rc)
