from pathlib import Path
import os,json,subprocess,time,hashlib,re
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
up=[p for p in os.environ['LEAN_PATH'].split(os.pathsep) if '/workspace/.lake/packages/' in p or p.endswith('/toolchain/lib/lean')]
env=os.environ.copy();env['LEAN_PATH']=str(root/'release_work/final_audit_v3/objects')+os.pathsep+os.pathsep.join(up);env.update(json.loads((out/'replay_environment.json').read_text()))
source=out/'ReplayClosureCandidate.lean'
cmd=['lean','-j1','-DwarningAsError=true',str(source)]
results=[]
for name,corrupt in [('candidate_positive','0'),('candidate_corrupt_duplicate','1')]:
 t=time.monotonic();env['KOMOREBI_REPLAY_DUPLICATE_CORRUPT']=corrupt
 with (out/(name+'.log')).open('w') as f:p=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
 text=(out/(name+'.log')).read_text();passed=(p.returncode==0 and 'REPLAY_CLOSURE_PASS MODULES 117 CONSTANTS 3500 NEW_NAME_REPLAYS 3499 DUPLICATE_BODY_RECHECKS 1' in text) if corrupt=='0' else (p.returncode!=0 and 'REPLAY_DUPLICATE_CORRUPT_CONTROL_INJECTED' in text and re.search('kernel.*type mismatch|declaration type mismatch|type mismatch',text,re.I) and 'REPLAY_CLOSURE_PASS' not in text)
 result={'name':name,'passed':bool(passed),'exit':p.returncode,'command':cmd,'environment':{k:v for k,v in env.items() if k.startswith('KOMOREBI_REPLAY') or k=='LEAN_PATH'},'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'seconds':round(time.monotonic()-t,3),'log':name+'.log','log_sha256':hashlib.sha256((out/(name+'.log')).read_bytes()).hexdigest()};results.append(result)
 print(name,p.returncode,passed,flush=True);print(text[-1500:],flush=True)
 if not passed:break
(out/'candidate_checks.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if len(results)==2 and all(x['passed'] for x in results) else 1)
