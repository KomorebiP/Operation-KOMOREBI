import zipfile,subprocess,shutil,time,json
from pathlib import Path
start=time.monotonic()
log=Path('/mnt/data/restore_logs')
with (log/'tar.log').open('w') as out:
 p=subprocess.Popen(['tar','-xJf','-','-C','/mnt/data/runtime'],stdin=subprocess.PIPE,stdout=out,stderr=subprocess.STDOUT)
 try:
  for path in sorted(Path('/mnt/data/lean_parts').glob('Lean_Compact_*.zip')):
   print('streaming',path.name,flush=True)
   with zipfile.ZipFile(path) as z,z.open(z.namelist()[0]) as f:
    shutil.copyfileobj(f,p.stdin,8*1024*1024)
  p.stdin.close()
  status=p.wait()
 except BaseException:
  p.kill();raise
(log/'result.json').write_text(json.dumps({'exit_code':status,'seconds':time.monotonic()-start}))
print('RESTORE_EXIT',status,flush=True)
