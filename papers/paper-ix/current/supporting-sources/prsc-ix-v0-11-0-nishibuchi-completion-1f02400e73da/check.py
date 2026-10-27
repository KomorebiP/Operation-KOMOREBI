#!/usr/bin/env python3
"""Build real pinned Lean sources with dependency-aware caching and retained attempts."""
import sys,subprocess,json,time,hashlib,shutil,re,os
from pathlib import Path
root=Path(__file__).parent
kit=Path(os.environ.get('LEAN_PORTABLE_KIT','/mnt/data/portable_parts/Komorebi_Portable_Lean_4.34.0-rc2'))
build=root/'build'; build.mkdir(exist_ok=True)
dev=root/'development'; dev.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(name,force=False,stack=()):
 if name in stack: raise RuntimeError('Import cycle: '+str(stack))
 source=root/'formalization'/f'{name}.lean'
 deps=re.findall(r'^public import ([\w.]+)',source.read_text(),re.M)
 deps=[d for d in deps if (root/'formalization'/f'{d}.lean').exists()]
 for d in deps:
  if check(d,stack=stack+(name,)): return 1
 state=build/(name+'.json')
 hashes={d:sha(build/(d+'.olean')) for d in deps}
 if not force and state.exists() and (build/(name+'.olean')).exists():
  s=json.loads(state.read_text())
  if s.get('source_sha256')==sha(source) and s.get('dependencies')==hashes: return 0
 seq=1+len(list(dev.glob('*.json'))); prefix=dev/f'{seq:03d}_{name}'
 shutil.copy2(source,str(prefix)+'.lean')
 for p in build.glob(name+'.*'):
  if p.is_file() or p.is_symlink():p.unlink()
 cmd=[sys.executable,str(root/'scripts/check_low_memory.py'),'--kit',str(kit),'--threads','1','--timeout','240','--import-dir',str(build),'--output',str(build/f'{name}.olean'),str(source)]
 t=time.monotonic(); r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 record={'module':name,'command':cmd,'exit_code':r.returncode,'seconds':round(time.monotonic()-t,3),'source_sha256':sha(source),'dependencies':hashes}
 Path(str(prefix)+'.log').write_text(r.stdout);Path(str(prefix)+'.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record,indent=2),flush=True);print(r.stdout,flush=True)
 if r.returncode==0: state.write_text(json.dumps(record,indent=2)+'\n')
 return r.returncode
if __name__=='__main__':sys.exit(check(sys.argv[1],True))
