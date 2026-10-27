"""Save every development source and compiler diagnostic. Not the release verifier."""
from pathlib import Path
import json, subprocess, sys, time, hashlib
base=Path(__file__).resolve().parents[1]
name=sys.argv[1]; proof=base/'formalization'/(name+'.lean')
kit=Path('/mnt/data/portable_lean_inputs/Komorebi_Portable_Lean_4.34.0-rc2')
out=base/'verification/development'; build=out/'build'; build.mkdir(exist_ok=True)
idx=1+len(list(out.glob(name+'_*.json'))); key=f'{name}_{idx:02d}'
snapshot=out/(key+'.lean'); snapshot.write_bytes(proof.read_bytes())
cmd=[sys.executable,str(base/'scripts/check_low_memory.py'),'--kit',str(kit),'--import-dir',str(build),'--output',str(build/(name+'.olean')),'--timeout','240',str(proof)]
t=time.monotonic()
try:
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300)
 rc,log=p.returncode,p.stdout
except subprocess.TimeoutExpired as e:
 rc=124; log=e.stdout or b''; log=log.decode(errors='replace') if isinstance(log,bytes) else log; log+='\nDEVELOPMENT TIMEOUT\n'
(out/(key+'.log')).write_text(log)
r={'module':name,'command':cmd,'exit_code':rc,'seconds':round(time.monotonic()-t,3),'sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest()}
(out/(key+'.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r)); print(log)
