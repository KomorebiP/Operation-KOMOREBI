import hashlib,json,subprocess,time
from pathlib import Path
root=Path('/workspace/scratch/9f53d520971c')
notes=root/'release_work/topology_notes'
names=['TopologyTransport','TopologyFiniteCompletion','TopologySeedRank','TopologyDenseCompletion','TopologyPresentations','TopologyCountablePackets','TopologyUnconditional','TopologyUnconditionalBridge']
rows=[]
for name in names:
 source=root/'release_work/formal/PaperIRelease'/f'{name}.lean'
 obj=root/'release_work/formal/.objects/PaperIRelease'/f'{name}.olean'
 cmd=[str(root/'release_work/runtime/run_lean.sh'),'-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-o',str(obj),str(source)]
 start=time.monotonic()
 result=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 (notes/f'compile_{name}.log').write_text(result.stdout)
 rows.append({'module':'PaperIRelease.'+name,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest() if obj.exists() else None,'exit_code':result.returncode,'seconds':round(time.monotonic()-start,2),'command':cmd})
 print(name, result.returncode,flush=True)
 if result.returncode: print(result.stdout,flush=True);break
(notes/'FINAL_COMPILE.json').write_text(json.dumps({'strict_flags':cmd[1:4],'modules':rows,'all_pass':len(rows)==len(names) and all(r['exit_code']==0 for r in rows)},indent=2)+'\n')
raise SystemExit(any(r['exit_code'] for r in rows))
