"""Record source snapshots and diagnostics for fifth-block development, not a release gate."""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, time
base=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(); p.add_argument('module'); p.add_argument('--kit',type=Path,default=Path('/mnt/data/portable_parts/Komorebi_Portable_Lean_4.34.0-rc2')); a=p.parse_args()
proof=base/'formalization'/(a.module+'.lean')
out=base/'verification/development_fifth'; out.mkdir(parents=True,exist_ok=True)
build=base/'verification/fifth_baseline/build'; build.mkdir(parents=True,exist_ok=True)
idx=1+len(list(out.glob(a.module+'_*.json'))); key=f'{a.module}_{idx:02d}'
snapshot=out/(key+'.lean'); snapshot.write_bytes(proof.read_bytes())
cmd=[sys.executable,str(base/'scripts/check_low_memory.py'),'--kit',str(a.kit),'--import-dir',str(build),'--output',str(build/(a.module+'.olean')),'--timeout','240',str(proof)]
t=time.monotonic()
try:
 r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=300); rc,log=r.returncode,r.stdout
except subprocess.TimeoutExpired as e:
 rc=124; log=e.stdout or b''; log=log.decode(errors='replace') if isinstance(log,bytes) else log; log+='\nDEVELOPMENT TIMEOUT\n'
(out/(key+'.log')).write_text(log)
row={'module':a.module,'command':cmd,'exit_code':rc,'seconds':round(time.monotonic()-t,3),'sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest()}
(out/(key+'.json')).write_text(json.dumps(row,indent=2)+'\n'); print(json.dumps(row)); print(log); sys.exit(rc)
