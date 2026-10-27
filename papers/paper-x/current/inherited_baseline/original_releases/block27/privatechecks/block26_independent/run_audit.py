from pathlib import Path
import os, sys, shutil, subprocess, json, hashlib, time
ROOT=Path(__file__).resolve().parents[2]
BASE=Path('/root/.codex/tmp/paperx_block25')
KIT=Path('/workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2')
OUT=ROOT/'privatechecks/block26_independent'
sys.path.insert(0,str(ROOT/'checks'))
from lean_env import lean_env
lean,env=lean_env(KIT)
BUILD=OUT/'build'
(BUILD/'PaperX').mkdir(parents=True, exist_ok=True)
for p in sorted((BASE/'build/PaperX').glob('*.olean')):
 if not (BUILD/'PaperX'/p.name).exists(): shutil.copy2(p,BUILD/'PaperX'/p.name)
if not (OUT/'initial_build_inventory.json').exists():
 (OUT/'initial_build_inventory.json').write_text(json.dumps({'count':len(list((BUILD/'PaperX').glob('*.olean'))),'sources':[{'path':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((BASE/'lean/PaperX').glob('*.lean'))],'oleans':[{'path':str(p.relative_to(BASE)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((BASE/'build/PaperX').glob('*.olean'))]},indent=2)+'\n')
env['LEAN_PATH']=str(BUILD)+os.pathsep+env['LEAN_PATH'].split(os.pathsep,1)[1]
results=[]
for arg in sys.argv[1:]:
 src=ROOT/arg
 cmd=[lean,'-DwarningAsError=true']
 if src.parent==ROOT/'lean/PaperX':cmd+=['-o',str(BUILD/'PaperX'/src.with_suffix('.olean').name)]
 cmd += [str(src)]
 start=time.time(); p=subprocess.run(cmd,cwd=ROOT/'lean',env=env,capture_output=True,text=True)
 dest=OUT/(src.stem+'.json')
 data={'source':str(src.relative_to(ROOT)), 'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'command':cmd,'cwd':str(ROOT/'lean'),'LEAN_PATH':env['LEAN_PATH'],'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'seconds':time.time()-start}
 dest.write_text(json.dumps(data,indent=2)+'\n')
 print(src.name,p.returncode,p.stdout,p.stderr,flush=True)
 results.append(data)
 if p.returncode:sys.exit(p.returncode)
