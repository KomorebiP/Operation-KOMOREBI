#!/usr/bin/env python3
"""Extract successful compilation evidence from a failed later-stage audit.
Never changes or upgrades the parent audit status.
"""
from pathlib import Path
import json,hashlib,shutil,time,os
root=Path(__file__).resolve().parents[3]
parent=root/'release_work/final_audit'
out=root/'release_work/runtime/fresh115_compilation_component'
source=root/'release_package/Komorebi_Paper_I_Release_2026-10-15/formal/current'
if out.exists():raise SystemExit('Refusing existing component output')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original_sha=sha(parent/'verification.json');j=json.loads((parent/'verification.json').read_text())
assert j['status']=='FAIL' and j['failure']=='owned_audit'
assert j['production_module_count']==116 and len(j['source_files'])==116
checks={x['label']:x for x in j['checks']}
assert checks['owned_audit']['passed'] is False
assert checks['boundary_consumers']['passed'] is True and checks['boundary_consumers']['exit']==0
out.mkdir(parents=True)
report={'schema':'paper-i-successful-compilation-component/1','status':'PASS','scope':'Compilation only:115 unchanged production sources compiled successfully in the parent run. The parent also compiled the old aggregate, which is excluded from reuse after an entrypoint import-list packaging fix. This receipt does not assert successful owned-declaration audit or kernel replay.','parent_audit':{'path':str(parent/'verification.json'),'sha256':original_sha,'status':j['status'],'failure':j['failure'],'failed_stage_log':'parent_owned_audit.log','failed_stage_log_sha256':sha(parent/'owned_audit.log')},'recorded_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'parent_compiled_module_count':116,'compilation_run_started_utc':j['started_utc'],'flags':j['flags'],'lean_version':j['lean_version'],'dependencies':j['dependencies'],'lean_path':j['lean_path'],'manifest_sha256':j['manifest_sha256'],'fresh_production_module_count':115,'modules':[],'limits':['Parent audit remains FAIL because its old whitelist rejected a new generated partial runtime helper.','This successful component certifies source compilation only; every later audit/replay stage must run and pass separately.','Objects are reused only after exact frozen-source/object/log hash validation.']}
shutil.copy2(parent/'verification.json',out/'parent_verification.json');shutil.copy2(parent/'owned_audit.log',out/'parent_owned_audit.log')
for row in j['source_files']:
 if row['module']=='PaperIRelease':
  report['excluded_from_reuse']=[{'module':row['module'],'original_source_sha256':row['source_sha256'],'reason':'Root repaired aggregate entrypoint to import all predecessor aggregate modules; final audit must freshly compile this updated aggregate.'}]
  continue
 assert row['origin']=='fresh_compile'
 chk=checks['compile_'+row['module'].replace('.','_')]
 assert chk['passed'] and chk['exit']==0 and chk['expected']=='zero'
 assert chk['command'][1:1+len(j['flags'])]==j['flags']
 src=source/row['source'];snap=parent/'source_snapshots'/row['source'];obj=parent/row['object'];log=parent/chk['log']
 assert sha(src)==sha(snap)==row['source_sha256'];assert sha(obj)==row['object_sha256'];assert sha(log)==chk['log_sha256']
 for original,relative in [(snap,Path('source_snapshots')/row['source']),(obj,Path(row['object'])),(log,Path(chk['log']))]:
  target=out/relative;target.parent.mkdir(parents=True,exist_ok=True);os.link(original,target)
 report['modules'].append({'module':row['module'],'source':row['source'],'source_sha256':row['source_sha256'],'command':chk['command'],'cwd':chk['cwd'],'exit':chk['exit'],'passed':True,'seconds':chk['seconds'],'log':chk['log'],'log_sha256':chk['log_sha256'],'object':row['object'],'object_sha256':row['object_sha256'],'provenance':'successful compile stage in preserved failed parent audit'})
b=j['boundary'];boundary_source=parent/'source_snapshots'/(b['module']+'.lean');boundary_obj=parent/'objects'/(b['module']+'.olean');bc=checks['boundary_consumers']
assert sha(boundary_source)==b['source_sha256'] and sha(boundary_obj)==b['object_sha256'];assert sha(parent/bc['log'])==bc['log_sha256']
shutil.copy2(boundary_source,out/'source_snapshots'/boundary_source.name);shutil.copy2(boundary_obj,out/'objects'/boundary_obj.name);shutil.copy2(parent/bc['log'],out/bc['log'])
report['boundary_compilation_component']={**b,'command':bc['command'],'cwd':bc['cwd'],'exit':0,'passed':True,'seconds':bc['seconds'],'log':bc['log'],'log_sha256':bc['log_sha256'],'scope':'Boundary compilation succeeded; new unified audit will recompile it.'}
report['elapsed_seconds']=round(sum(r['seconds'] for r in report['modules']),3)
report['elapsed_interpretation']='Sum of recorded compilation command wall times; not a newly executed build.'
assert sha(parent/'verification.json')==original_sha
for row in report['modules']:
 assert sha(source/row['source'])==row['source_sha256'];assert sha(out/row['object'])==row['object_sha256'];assert sha(out/row['log'])==row['log_sha256']
(out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('Successful compilation-only component:',out)
print('Parent remains',j['status'],j['failure'],original_sha)
print('Component receipt SHA256',sha(out/'verification.json'))
