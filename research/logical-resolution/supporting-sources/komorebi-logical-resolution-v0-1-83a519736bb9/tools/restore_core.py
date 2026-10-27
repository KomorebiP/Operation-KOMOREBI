"""Restore only Lean core/Std from frozen user-provided split-xz archive."""
import io, json, shutil, tarfile, time, zipfile
from pathlib import Path
class Parts(io.RawIOBase):
    def __init__(self, paths):
        self.paths=iter(paths); self.z=None; self.f=None
    def readable(self): return True
    def read(self,n=-1):
        if n<0: n=1024*1024
        buf=bytearray()
        while len(buf)<n:
            if self.f is None:
                try: p=next(self.paths)
                except StopIteration: break
                self.z=zipfile.ZipFile(p); self.f=self.z.open(self.z.namelist()[0])
            b=self.f.read(n-len(buf))
            if b: buf.extend(b)
            else: self.f.close(); self.z.close(); self.f=None
        return bytes(buf)
base=Path('/mnt/data/logical_runtime'); start=time.monotonic(); count=0; size=0
seen=False; last=''
with tarfile.open(fileobj=Parts(sorted(Path('/mnt/data/model_theory_runtime_parts').glob('*.zip'))),mode='r|xz') as t:
    for m in t:
        parts=Path(m.name).parts
        if len(parts)<2: continue
        if parts[1]=='toolchain': seen=True
        elif seen: break
        keep=parts[1]=='compat' or (parts[1]=='toolchain' and len(parts)>2 and parts[2] in ('bin','lib'))
        if not keep: continue
        if '..' in parts or Path(m.name).is_absolute(): raise RuntimeError('unsafe member')
        dst=base/m.name
        if m.isdir(): dst.mkdir(parents=True,exist_ok=True)
        elif m.isfile():
            dst.parent.mkdir(parents=True,exist_ok=True)
            with t.extractfile(m) as src, dst.open('wb') as out: shutil.copyfileobj(src,out,1024*1024)
            dst.chmod(m.mode); count+=1; size+=m.size
        elif m.issym():
            dst.parent.mkdir(parents=True,exist_ok=True)
            if not dst.exists(): dst.symlink_to(m.linkname)
        if count%1500==0 and m.name!=last:
            print(json.dumps({'files':count,'bytes':size,'elapsed':round(time.monotonic()-start,2),'last':m.name}),flush=True); last=m.name
print(json.dumps({'status':'CORE_RESTORED','files':count,'bytes':size,'elapsed':time.monotonic()-start}),flush=True)
