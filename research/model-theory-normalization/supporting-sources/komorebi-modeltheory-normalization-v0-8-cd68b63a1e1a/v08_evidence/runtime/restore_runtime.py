from pathlib import Path
import io,zipfile,lzma,tarfile,shutil,time,json
root=Path('/mnt/data/model08_work/runtime');root.mkdir(exist_ok=True)
parts=sorted(Path('/mnt/data/model08_work/runtime_parts').glob('Lean_Compact_*.zip'))
class Chunks(io.RawIOBase):
 def __init__(self,parts):
  self.parts=iter(parts);self.z=None;self.f=None
 def readable(self):return True
 def readinto(self,b):
  while True:
   if self.f is None:
    try:p=next(self.parts)
    except StopIteration:return 0
    self.z=zipfile.ZipFile(p);self.f=self.z.open(self.z.namelist()[0])
   data=self.f.read(len(b))
   if data:b[:len(data)]=data;return len(data)
   self.f.close();self.z.close();self.f=None
start=time.time();count=0;size=0;skipped=0
f=lzma.LZMAFile(io.BufferedReader(Chunks(parts),1024*1024))
t=tarfile.open(fileobj=f,mode='r|')
for info in t:
 path=Path(info.name)
 if path.is_absolute() or '..' in path.parts:raise ValueError(info.name)
 if info.isdir():continue
 if not info.isfile():skipped+=1;continue
 s=info.name
 if '/.git/' in s and not any(x in s for x in ['/.git/HEAD','/.git/refs/','/.git/packed-refs']):skipped+=1;continue
 if s.endswith(('.a','.o','.c','.bc','.ilean','.ttf','.otf','.woff','.woff2','.png','.jpg','.pdf')):skipped+=1;continue
 out=root/path;out.parent.mkdir(parents=True,exist_ok=True)
 with t.extractfile(info) as src,out.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
 if '/bin/' in s:out.chmod(info.mode)
 size+=info.size;count+=1
 if count%5000==0:print(json.dumps({'files':count,'GB':round(size/1e9,3),'seconds':round(time.time()-start,2),'last':s}),flush=True)
report={'status':'PASS','files':count,'bytes':size,'skipped':skipped,'seconds':time.time()-start}
(root/'RESTORE.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
