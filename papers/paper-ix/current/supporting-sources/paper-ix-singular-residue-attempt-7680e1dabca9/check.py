from pathlib import Path
import subprocess,sys,json,time,hashlib
root=Path(__file__).resolve().parent
name=sys.argv[1]
src=root/'formalization'/f'{name}.lean'
runs=root/'development';runs.mkdir(exist_ok=True)
num=len(list(runs.glob('*.json')))+1
snapshot=runs/f'{num:03d}_{name}.lean';snapshot.write_bytes(src.read_bytes())
cmd=['python','/mnt/data/ix_attempt/PRSC_IX_v0.8.0_Checked_Eighth_Block/scripts/check_low_memory.py','--kit','/mnt/data/portable_parts/Komorebi_Portable_Lean_4.34.0-rc2','--import-dir',str(root/'build'),'--output',str(root/'build'/f'{name}.olean'),'--timeout','180',str(src)]
t=time.time();p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
log=runs/f'{num:03d}_{name}.log';log.write_text(p.stdout)
(runs/f'{num:03d}_{name}.json').write_text(json.dumps({'command':cmd,'exit_code':p.returncode,'seconds':time.time()-t,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'snapshot':snapshot.name,'log':log.name},indent=2))
print(p.stdout);print('EXIT',p.returncode,'SECONDS',round(time.time()-t,2));sys.exit(p.returncode)
