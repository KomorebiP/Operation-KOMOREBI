import os,subprocess,json,time,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2];task=root.parent
out=Path(__file__).resolve().parent
upstream=[p for p in os.environ['LEAN_PATH'].split(os.pathsep) if '/workspace/.lake/packages/' in p or p.endswith('/toolchain/lib/lean')]
env=os.environ.copy();env['LEAN_PATH']=str(task/'release_work/final_audit/objects')+os.pathsep+os.pathsep.join(upstream)
cmd=['lean','-j1','-DwarningAsError=true',str(out/'Inventory.lean')];t=time.monotonic()
with (out/'inventory.log').open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
rows=[json.loads(s[len('DIAGNOSTIC_HELPER '):]) for s in (out/'inventory.log').read_text().splitlines() if s.startswith('DIAGNOSTIC_HELPER ')]
(out/'inventory.json').write_text(json.dumps({'purpose':'diagnostic inventory; no certification of unreviewed helpers','command':cmd,'exit':r.returncode,'seconds':time.monotonic()-t,'helpers':rows},indent=2)+'\n')
print(r.returncode,len(rows));print((out/'inventory.log').read_text()[-500:])
raise SystemExit(r.returncode)
