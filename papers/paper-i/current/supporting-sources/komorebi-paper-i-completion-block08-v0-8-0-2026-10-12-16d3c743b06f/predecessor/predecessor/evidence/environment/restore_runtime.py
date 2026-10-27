import zipfile,hashlib,pathlib,subprocess,time,json
root=pathlib.Path('/mnt/data'); start=time.time(); h=hashlib.sha256(); size=0
with open(root/'runtime_restore_tar.log','w') as log:
 p=subprocess.Popen(['tar','--zstd','-xf','-','-C',str(root)],stdin=subprocess.PIPE,stdout=log,stderr=log)
 try:
  for i in range(1,8):
   with zipfile.ZipFile(root/f'runtime_parts/Lean_Offline_{i:02}.zip') as z, z.open(z.namelist()[0]) as f:
    while b:=f.read(4*1024*1024):
     h.update(b); size+=len(b); p.stdin.write(b)
   print('restored chunk',i,flush=True)
  p.stdin.close(); code=p.wait()
 except BaseException:
  p.kill(); p.wait(); raise
out={'archive_sha256':h.hexdigest(),'archive_bytes':size,'returncode':code,'elapsed':time.time()-start}
(root/'runtime_restore.json').write_text(json.dumps(out,indent=2)); print(out,flush=True)
assert code==0 and h.hexdigest()=='66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34'
