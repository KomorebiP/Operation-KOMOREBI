from pathlib import Path
import hashlib,json,subprocess,time
root=Path('/workspace/scratch/9f53d520971c/release_work')
names=['CategoryExport','CategoryPackets','GrammarAlgebra','GrammarTyped','GrammarModules','GrammarEquivalence','GrammarIdeal','GrammarPaths','GrammarFactorization','CategoryBoundaries']
records=[]
for name in names:
 src=root/'formal/PaperIRelease'/f'{name}.lean';obj=root/'formal/.objects/PaperIRelease'/f'{name}.olean'
 cmd=['bash',str(root/'runtime/run_lean.sh'),'-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-o',str(obj),str(src)]
 start=time.time(); result=subprocess.run(cmd,capture_output=True,text=True)
 (root/'category_notes'/f'{name}_final.log').write_text(result.stdout+result.stderr)
 row={'module':'PaperIRelease.'+name,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'exit_code':result.returncode,'seconds':round(time.time()-start,3),'object_sha256':hashlib.sha256(obj.read_bytes()).hexdigest() if result.returncode==0 else None}
 records.append(row); print(name,result.returncode,flush=True)
 if result.returncode: print(result.stdout,result.stderr,flush=True);break
(root/'category_notes/final_compile.json').write_text(json.dumps({'modules':records,'all_pass':len(records)==len(names) and all(r['exit_code']==0 for r in records)},indent=2)+'\n')
raise SystemExit(0 if len(records)==len(names) and all(r['exit_code']==0 for r in records) else 1)
