from pathlib import Path
import io,zipfile,tarfile,lzma,json,time,hashlib
base=Path('/mnt/data/model010_work'); dest=base/'runtime'; dest.mkdir(exist_ok=True)
class Parts(io.RawIOBase):
 def __init__(self):
  self.paths=iter(sorted((base/'runtime_parts').glob('*.zip'))); self.z=None; self.f=None; self.total=0;self.sha=hashlib.sha256()
 def readable(self):return True
 def readinto(self,b):
  while True:
   if self.f is None:
    try:p=next(self.paths)
    except StopIteration:return 0
    self.z=zipfile.ZipFile(p);self.f=self.z.open(self.z.namelist()[0])
   s=self.f.read(len(b))
   if s:
    b[:len(s)]=s;self.total+=len(s);self.sha.update(s);return len(s)
   self.f.close();self.z.close();self.f=None
s=Parts(); start=time.time(); n=0;size=0
with lzma.LZMAFile(io.BufferedReader(s,buffer_size=1<<20)) as f:
 with tarfile.open(fileobj=f,mode='r|') as t:
  for a in t:
   p=(dest/a.name).resolve()
   if not p.is_relative_to(dest.resolve()):raise RuntimeError(a.name)
   if a.isfile() and a.name.lower().endswith(('.ttf','.otf','.woff','.woff2')): continue
   t.extract(a,dest,filter='data');n+=1;size+=a.size
   if n%1000==0:
    (base/'runtime_progress.json').write_text(json.dumps({'files':n,'bytes':size,'last':a.name,'elapsed':time.time()-start}));print(n,size,a.name,flush=True)
rec={'files':n,'bytes':size,'elapsed':time.time()-start,'compressed_bytes':s.total,'stream_sha256':s.sha.hexdigest(),'status':'PASS'}
(base/'RUNTIME_RESTORE.json').write_text(json.dumps(rec,indent=2));print(rec,flush=True)
