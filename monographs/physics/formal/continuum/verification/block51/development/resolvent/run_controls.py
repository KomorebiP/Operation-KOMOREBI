from pathlib import Path
import datetime,hashlib,json,os,re,subprocess,time
base=Path('/workspace/scratch/6a8ff46cf015/physics_next')
project=base/'work/Komorebi_Physics_Lean_v0.49.0_Checked_Block_49'
attempts=base/'attempts/resolvent'
num=1
while (attempts/f'controls_{num:03}').exists():num+=1
out=attempts/f'controls_{num:03}';out.mkdir()
spec=json.loads((attempts/'CONTROL_MANIFEST.json').read_text())
kit=base/'runtime/Komorebi_Portable_Lean_4.34.0-rc2'
env=os.environ.copy();env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH','');env['LD_PRELOAD']=str(kit/'compat/app_path.so')
for k in ('LEAN_PATH','LEAN_SRC_PATH','LEAN_SYSROOT','LAKE_HOME'):env.pop(k,None)
results=[]
for item in spec['controls']:
 source=project/item['path'];snapshot=out/source.name;snapshot.write_bytes(source.read_bytes())
 log=out/(source.stem+'.log');argv=['lake','env','lean','-j1','-DwarningAsError=true',item['path']]
 start=time.monotonic()
 with log.open('w') as stream:p=subprocess.run(argv,cwd=project,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=180)
 text=log.read_text();passed=p.returncode==0 if item['expected']=='accept' else p.returncode!=0 and re.search(item['diagnostic_pattern'],text) is not None and not re.search('unknown|object file|ambiguous',text,re.I)
 row={**item,'argv':argv,'returncode':p.returncode,'seconds':time.monotonic()-start,'passed':passed,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'log':log.name};results.append(row)
 (out/'RESULT.json').write_text(json.dumps({'status':'PASS' if all(r['passed'] for r in results) else 'FAIL','completed':len(results),'controls':results},indent=2)+'\n')
 print(source.name,passed,p.returncode,flush=True)
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
