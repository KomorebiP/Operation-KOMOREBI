#!/usr/bin/env python3
"""Independent clean replay of the completed-tensor dependency closure from an extracted release.
The initial release report certifies the full 96-module rebuild. This extra replay
cleans all project objects and rebuilds the new block plus its actual source closure.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,shutil,sys
from datetime import datetime,timezone
import verify as V
ROOT=Path(__file__).resolve().parents[1]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('kit',type=Path);ap.add_argument('--start',action='store_true');ap.add_argument('--batch',type=int,default=10000);a=ap.parse_args()
 ref=json.load(open(ROOT/'verification.json'));conf=json.load(open(ROOT/'checks/modules.json'));assert ref['status']=='PASS'
 needed=set(conf['new_modules'])
 while True:
  more=needed|{d for m in needed for d in conf['dependencies'][m]}
  if more==needed:break
  needed=more
 mods=[m for m in conf['modules'] if m in needed]
 kit=a.kit.resolve();lean=kit/'toolchain/bin/lean';ws=kit/'workspace'
 assert V.sha(lean)==ref['compiler_sha256']
 assert subprocess.check_output(['git','-C',str(ws/'.lake/packages/mathlib'),'rev-parse','HEAD'],text=True).strip()==V.PIN
 env=os.environ.copy();env['MALLOC_ARENA_MAX']='2';env['LEAN_PATH']=os.pathsep.join(map(str,[ROOT/'build',ws/'.lake/build/lib/lean',*sorted((ws/'.lake/packages').glob('*/.lake/build/lib/lean'))]))
 for rel,h in ref['source_hashes_after'].items():assert V.sha(ROOT/'lean'/rel)==h,rel
 rp=ROOT/'EXTRACTED_COMPLETION_REPLAY.json'
 if a.start:
  shutil.rmtree(ROOT/'build',ignore_errors=True);(ROOT/'build').mkdir()
  (ROOT/'archive_replay_logs').mkdir(exist_ok=True)
  r={'status':'RUNNING','scope':'fresh extracted-archive completed-tensor dependency closure; separate release verification.json covers all 96 project modules',
     'started_utc':V.now(),'modules_expected':mods,'modules':[],'axioms':[],'controls':[],
     'all_96_source_hashes_matched':True,'compiler_sha256':V.sha(lean),'mathlib_commit':V.PIN,
     'script_sha256':V.sha(__file__)}
 else:
  r=json.load(open(rp));assert r['status']=='RUNNING'
  for x in r['modules']:assert V.sha(ROOT/x['object'])==x['object_sha256']
 save=lambda:rp.write_text(json.dumps(r,indent=2)+'\n')
 save()
 try:
  for mod in mods[len(r['modules']):len(r['modules'])+a.batch]:
   src=ROOT/'lean'/Path(mod.replace('.','/')+'.lean');obj=ROOT/'build'/Path(mod.replace('.','/')+'.olean');obj.parent.mkdir(exist_ok=True,parents=True)
   cr=V.run([str(lean),'-j1','-DwarningAsError=true','-o',str(obj),str(src)],env,ROOT/'archive_replay_logs'/(mod+'.build.log'),180)
   assert cr['exit_code']==0 and not cr['timed_out'],('compilation',mod,cr)
   ds,private=V.inventory(src,mod)
   probe=ROOT/'checks/ExtractedAxiomAudit.lean';probe.write_text('import '+mod+'\n'+'\n'.join('#print axioms '+d['name'] for d in ds)+'\n')
   ar=V.run([str(lean),'-j1','-DwarningAsError=true',str(probe)],env,ROOT/'archive_replay_logs'/(mod+'.axioms.log'),180)
   assert ar['exit_code']==0 and not ar['timed_out'],('audit',mod,ar)
   text=(ROOT/ar['log']).read_text()
   for d in ds:
    import re
    ma=re.search(re.escape("'"+d['name']+"'")+r' depends on axioms:\s*\[([^\]]*)\]',text)
    if ma:axs=[x.strip() for x in ma[1].split(',') if x.strip()]
    else:
     assert "'"+d['name']+"' does not depend on any axioms" in text,d['name'];axs=[]
    assert set(axs)<=V.ALLOWED,(d['name'],axs)
    old=next(x['axioms'] for x in ref['axioms'] if x['name']==d['name'])
    assert set(old)==set(axs),(d['name'],old,axs)
    r['axioms'].append({'name':d['name'],'axioms':axs})
   oldobj=next(x['olean_sha256'] for x in ref['modules'] if x['module']==mod)
   r['modules'].append({'module':mod,'build':cr,'axiom_audit':ar,'object':str(obj.relative_to(ROOT)),
     'object_sha256':V.sha(obj),'same_object_as_full_rebuild':V.sha(obj)==oldobj})
   save();print('PASS extracted '+str(len(r['modules']))+'/'+str(len(mods))+' '+mod,flush=True)
  if len(r['modules'])<len(mods):return 0
  for name,msg in [('RejectFalse','Type mismatch'),('RejectPlaceholder','sorry'),('RejectWrongEmptyNormalization','unsolved goals')]:
   cr=V.run([str(lean),'-j1','-DwarningAsError=true',str(ROOT/'checks'/(name+'.lean'))],env,ROOT/'archive_replay_logs'/(name+'.log'),180)
   cr['name']=name;cr['passed']=cr['exit_code']!=0 and not cr['timed_out'] and msg in (ROOT/cr['log']).read_text();assert cr['passed']
   r['controls'].append(cr)
  for rel,h in ref['source_hashes_after'].items():assert V.sha(ROOT/'lean'/rel)==h
  r.update(status='PASS',finished_utc=V.now(),module_count=len(mods),audited_declaration_count=len(r['axioms']),same_all_object_hashes=all(x['same_object_as_full_rebuild'] for x in r['modules']),same_all_axiom_reports=True)
  save();print('EXTRACTED REPLAY PASS '+str(r['module_count'])+' modules, '+str(r['audited_declaration_count'])+' audits',flush=True);return 0
 except Exception as e:
  r.update(status='FAIL',error=str(e));save();print('FAIL '+str(e),flush=True);return 1
if __name__=='__main__':sys.exit(main())
