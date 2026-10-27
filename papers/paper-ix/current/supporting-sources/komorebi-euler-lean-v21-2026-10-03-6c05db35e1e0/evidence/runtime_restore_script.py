import hashlib,json,tarfile,zipfile,time
from pathlib import Path
s=time.monotonic();parts=Path('/mnt/data/runtime_parts'); out=Path('/mnt/data/run_v21/Lean_Portable_Compact.tar.xz'); h=hashlib.sha256()
with out.open('wb') as dst:
 for p in sorted(parts.glob('Lean_Compact_*.zip')):
  with zipfile.ZipFile(p) as z,z.open(z.namelist()[0]) as src:
   while b:=src.read(8<<20):h.update(b);dst.write(b)
print('HASH',h.hexdigest(),flush=True)
assert h.hexdigest()=='f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7'
target=Path('/mnt/data/lean_runtime');target.mkdir(exist_ok=True)
with tarfile.open(out,'r:xz') as tar:
 for i,m in enumerate(tar):
  tar.extract(m,target,filter='data')
  if i%5000==0:print(i,m.name,flush=True)
print('DONE',time.monotonic()-s,flush=True)
