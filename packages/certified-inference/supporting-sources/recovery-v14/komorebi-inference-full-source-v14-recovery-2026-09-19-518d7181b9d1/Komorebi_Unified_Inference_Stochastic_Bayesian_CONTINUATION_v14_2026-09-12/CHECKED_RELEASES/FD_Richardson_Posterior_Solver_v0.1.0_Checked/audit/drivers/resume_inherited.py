from pathlib import Path
import subprocess,json,time
r=Path(__file__).resolve().parents[1]
mods=json.loads((r/'MODULE_ORDER.json').read_text());mods=mods[mods.index('FDGainSampler'):]
t=time.monotonic()
with (r/'audit/inherited_resume.log').open('w') as f:
 p=subprocess.run(['python',str(r/'verify_blocks.py'),'--runtime','/mnt/data/lean_runtime_parts/Komorebi_Portable_Lean_4.34.0-rc2','--timeout','40','--modules']+mods,stdout=f,stderr=subprocess.STDOUT)
(r/'audit/inherited_resume.json').write_text(json.dumps({'exit_status':p.returncode,'seconds':time.monotonic()-t}))
