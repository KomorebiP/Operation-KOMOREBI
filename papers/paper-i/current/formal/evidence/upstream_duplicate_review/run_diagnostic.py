from pathlib import Path
import os,json,subprocess,time,hashlib
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
up=[p for p in os.environ['LEAN_PATH'].split(os.pathsep) if '/workspace/.lake/packages/' in p or p.endswith('/toolchain/lib/lean')]
env=os.environ.copy();env['LEAN_PATH']=str(root/'release_work/final_audit_v3/objects')+os.pathsep+os.pathsep.join(up);env.update(json.loads((out/'replay_environment.json').read_text()))
cmd=['lean','-j1','-DwarningAsError=true',str(out/'InspectOverlaps.lean')];t=time.monotonic()
with (out/'overlap_diagnostic.log').open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
log=(out/'overlap_diagnostic.log').read_text();rows=[json.loads(s[len('OVERLAP_DIAGNOSTIC '):]) for s in log.splitlines() if s.startswith('OVERLAP_DIAGNOSTIC ')]
(out/'overlap_diagnostic.json').write_text(json.dumps({'exit':p.returncode,'command':cmd,'seconds':time.monotonic()-t,'overlaps':rows},indent=2)+'\n')
print('exit',p.returncode,'overlaps',len(rows));print(log[-1500:]);raise SystemExit(p.returncode)
