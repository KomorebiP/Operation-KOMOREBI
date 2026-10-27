from pathlib import Path
import zipfile,lzma,tarfile,io,time,json,hashlib,os
root=Path('/mnt/data'); out=root/'runtime_v017';out.mkdir(exist_ok=True)
class Parts(io.RawIOBase):
 def __init__(self):self.i=0;self.z=None;self.f=None
 def readable(self):return True
 def readinto(self,b):
  while True:
   if self.f is None:
    self.i+=1
    if self.i>5:return 0
    self.z=zipfile.ZipFile(root/f'lean_parts/Lean_Compact_0{self.i}.zip');self.f=self.z.open(self.z.namelist()[0]);print('PART',self.i,flush=True)
   n=self.f.readinto(b)
   if n:return n
   self.f.close();self.z.close();self.f=None
start=time.monotonic();count=0
with io.BufferedReader(Parts(),buffer_size=1024*1024) as c, lzma.LZMAFile(c) as d, tarfile.open(fileobj=d,mode='r|') as t:
 for m in t:
  dest=(out/m.name).resolve()
  if not dest.is_relative_to(out.resolve()):raise ValueError(m.name)
  t.extract(m,path=out,filter='data');count+=1
  if count%5000==0:print('FILES',count, m.name,flush=True)
print('DONE',count,round(time.monotonic()-start,2),flush=True)
