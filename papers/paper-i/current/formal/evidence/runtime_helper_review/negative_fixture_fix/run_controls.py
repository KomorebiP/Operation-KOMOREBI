from pathlib import Path
import os,json,subprocess,hashlib,time,re
root=Path(__file__).resolve().parents[4];out=Path(__file__).resolve().parent
up=[p for p in os.environ['LEAN_PATH'].split(os.pathsep) if '/workspace/.lake/packages/' in p or p.endswith('/toolchain/lib/lean')]
env=os.environ.copy();env['LEAN_PATH']=str(root/'release_work/final_audit_v2/objects')+os.pathsep+os.pathsep.join(up)
results=[]
for name in ['WrongCeiling','WrongProductSum','WrongCoefficientOrder']:
 src=out/(name+'.lean');log=out/(name+'.log');cmd=['lean','-j1','-DwarningAsError=true','-DautoImplicit=false','-DrelaxedAutoImplicit=false','-DmaxSynthPendingDepth=3',str(src)];t=time.monotonic()
 with log.open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 txt=log.read_text();ok=p.returncode>0 and re.search('type mismatch',txt,re.I) is not None and not re.search('unknown module|unknown identifier|failed to synthesize',txt,re.I)
 results.append({'name':name,'command':cmd,'exit':p.returncode,'expected_failure_observed':ok,'seconds':time.monotonic()-t,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()});print(name,ok,txt[-600:])
(out/'verification.json').write_text(json.dumps({'status':'PASS' if all(x['expected_failure_observed'] for x in results) else 'FAIL','scope':'Three negative controls must reach and reject the intended false conclusion by type mismatch.','checks':results},indent=2)+'\n')
raise SystemExit(0 if all(x['expected_failure_observed'] for x in results) else 1)
