from pathlib import Path
import subprocess, os, json, hashlib, datetime
base=Path(__file__).resolve().parents[3]
rt=base/'runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2'
formal=base/'continuation/formal'
evidence=base/'continuation/development/wr01'
build=evidence/'build'
(build/'KomorebiSpace').mkdir(parents=True,exist_ok=True)
env=os.environ.copy()
paths=[build]+sorted((rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))
env['LEAN_PATH']=os.pathsep.join(map(str,paths))
env['LD_PRELOAD']=str(rt/'compat/app_path.so')
flags=[str(rt/'toolchain/bin/lean'),'-j1','-DwarningAsError=true','-DautoImplicit=false']
cases=[('production',formal/'KomorebiSpace/BoundedApproximateRealization.lean',True),
 ('positive',base/'continuation/formal/tests/positive/WR01BudgetExamples.lean',True),
 ('negative_drop_bound',base/'continuation/formal/tests/negative/WR01DropBudgetBound.lean',False),
 ('negative_shrink_budget',base/'continuation/formal/tests/negative/WR01ShrinkPreservedBudget.lean',False)]
results=[]
for name,p,expected in cases:
 args=flags+(['-o',str(build/'KomorebiSpace/BoundedApproximateRealization.olean')] if name=='production' else [])+[str(p)]
 result=subprocess.run(args,cwd=formal,env=env,capture_output=True,text=True)
 log=result.stdout+result.stderr
 (evidence/(name+'_control.log')).write_text(log)
 rejected_for_expected_obligation = not expected and result.returncode!=0 and 'unsolved goals' in log and '⊢ False' in log and 'unknown' not in log.lower()
 passed=(expected and result.returncode==0) or rejected_for_expected_obligation
 results.append({'name':name,'path':str(p.relative_to(base)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'expected':'accept' if expected else 'reject_false_budget_obligation','exit_code':result.returncode,'pass':passed,'log':name+'_control.log'})
 print(name,result.returncode,'PASS' if passed else 'FAIL')
 print(log)
record={'timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS' if all(x['pass'] for x in results) else 'FAIL','results':results,'scope':'Boundary examples test the exact finite norm budget. They do not independently instantiate an infinite-dimensional nonclosed-range operator.'}
(evidence/'controls_verification.json').write_text(json.dumps(record,indent=2)+'\n')
