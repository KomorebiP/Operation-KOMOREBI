from pathlib import Path
import subprocess,os,time,json,re,hashlib,shutil,zipfile,traceback,sys
W=Path('/mnt/data/block29_work/current'); O=W/'results'; O.mkdir(parents=True,exist_ok=True)
RT=Path('/mnt/data/runtime29/Komorebi_Portable_Lean_4.34.0-rc2')
NEW=['PrimePowerIdeals','PrimePowerIdealValuation','CoordinateIdealClosure','IdealMaskAutomaton','CyclicIdealCoordinates','CyclicMaskAutomaton','IdealClosureExamples']
env=os.environ|{'PATH':str(RT/'toolchain/bin')+':'+os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
 return {str(p.relative_to(W)):sha(p) for p in sorted(W.rglob('*.lean')) if '.lake' not in p.parts}
def command(label,cmd,timeout=600):
 before=snapshot();t=time.time()
 try:
  with (O/f'{label}.log').open('w') as f:
   result=subprocess.run(cmd,cwd=W,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
  rc=result.returncode;status='completed' if rc==0 else 'failed'
 except subprocess.TimeoutExpired:rc=124;status='timeout'
 except Exception as e:
  rc=127;status='launch-failed';(O/f'{label}.log').write_text(repr(e))
 after=snapshot();record={'argv':cmd,'status':status,'exit_code':rc,'seconds':time.time()-t,
  'inputs_unchanged':before==after,'inputs_before':before,'inputs_after':after,'log_sha256':sha(O/f'{label}.log')}
 (O/f'{label}.json').write_text(json.dumps(record,indent=2));print(label,rc,flush=True)
 return record

def main():
 end=time.time()+600
 while not (O/'baseline_build.json').exists() and time.time()<end:time.sleep(2)
 status={'base':'Block28','new_modules':NEW,'steps':{},'scope':'new-module replay plus inherited-source preservation; not independent kernel implementation'}
 if not (O/'baseline_build.json').exists():raise RuntimeError('Baseline did not return its receipt within 600 seconds.')
 base=json.loads((O/'baseline_build.json').read_text());status['baseline']=base
 if base['exit']!=0:raise RuntimeError('Predecessor root build failed. Inspect baseline_build.log.')
 p=next(Path('/mnt/data/block29_work/predecessor').iterdir())
 oldsource=list((p/'lean/KomorebiPadic').glob('*.lean'))
 status['predecessor_modules_unchanged']=all(sha(f)==sha(W/'lean/KomorebiPadic'/f.name) for f in oldsource)
 status['predecessor_module_count']=len(oldsource)
 # Generate audit before the frozen compilation sequence.
 oldaudits=[f for f in (p/'verification').rglob('*.lean') if '#print axioms' in f.read_text()]
 oldaudit=max(oldaudits,key=lambda f:f.read_text().count('#print axioms')) if oldaudits else None
 ns={'PrimePowerIdeals':'KomorebiPadic.PrimePowerIdeal','PrimePowerIdealValuation':'KomorebiPadic.PrimePowerIdeal',
     'CoordinateIdealClosure':'KomorebiPadic.CoordinateIdeal','IdealMaskAutomaton':'KomorebiPadic',
     'CyclicMaskAutomaton':'KomorebiPadic','IdealClosureExamples':'KomorebiPadic.CoordinateIdeal'}
 names=[]
 for name in NEW:
  text=(W/'lean/KomorebiPadic'/f'{name}.lean').read_text()
  for match in re.finditer(r'\btheorem\s+([A-Za-z_][\w.\']*)',text):
   if name=='CyclicIdealCoordinates':
    prefix='KomorebiPadic.PrimePowerIdeal' if match.start()<text.index('namespace CoordinateIdeal') else 'KomorebiPadic.CoordinateIdeal'
   else:prefix=ns[name]
   names.append(prefix+'.'+match.group(1))
 status['new_theorem_names']=names
 audit=oldaudit.read_text() if oldaudit else 'import KomorebiPadic\n'
 audit+='\n'+'\n'.join('#print axioms '+n for n in names)+'\n'
 (W/'verification/AllAxioms29_30.lean').write_text(audit)
 # Root extension is the only edit to an inherited Lean file.
 root=W/'lean/KomorebiPadic.lean'
 root.write_text('import KomorebiPadic.IdealClosureExamples\n'+root.read_text())
 for name in NEW:
  rec=command('build_'+name,['lake','build','KomorebiPadic.'+name])
  status['steps'][name]=rec
  if rec['exit_code']!=0:
   status['status']='INCOMPLETE_LEAN_BUILD';status['failed_module']=name
   (O/'VERIFICATION.json').write_text(json.dumps(status,indent=2));return status
 status['steps']['root']=command('integrated_root',['lake','build'])
 status['steps']['axioms']=command('axioms',['lake','env','lean','-DwarningAsError=true','verification/AllAxioms29_30.lean'])
 status['steps']['examples']=command('examples',['lake','env','lean','-DwarningAsError=true','verification/IdealCyclicExamples.lean'])
 status['steps']['integer_audit']=command('integer_audit',['python','verification/audit_ideal_cyclic.py'],timeout=300)
 controls=[]
 for file in ['FalseControl','PlaceholderControl','OverclaimControl']:
  rec=command('negative_'+file,['lake','env','lean','-DwarningAsError=true',f'verification/{file}.lean'])
  txt=(O/f'negative_{file}.log').read_text()
  okay=rec['exit_code']!=0 and rec['status']=='failed' and ('sorry' in txt if file=='PlaceholderControl' else any(t in txt for t in ['false','unsolved goals','failed to synthesize','decide tactic failed']))
  controls.append({'name':file,'correctly_rejected':okay,'receipt':rec})
 status['negative_controls']=controls
 txt=(O/'axioms.log').read_text()
 found=re.findall(r"[‘']([^’'\n]+)[’'] (?:depends on axioms:|does not depend on any axioms)",txt)
 status['axiom_reports_count']=len(found)
 status['new_axiom_reports_complete']=all(n in found for n in names)
 axioms=set()
 for group in re.findall(r'depends on axioms:\s*\[([^\]]*)\]',txt):
  axioms.update(x.strip() for x in group.split(',') if x.strip())
 status['observed_axioms']=sorted(axioms);status['unexpected_axioms']=sorted(axioms-{'propext','Quot.sound','Classical.choice'})
 status['status']='PASS' if (all(v['exit_code']==0 and v['inputs_unchanged'] for v in status['steps'].values()) and
  all(c['correctly_rejected'] for c in controls) and status['new_axiom_reports_complete'] and not status['unexpected_axioms'] and status['predecessor_modules_unchanged']) else 'INCOMPLETE_VERIFICATION'
 (O/'VERIFICATION.json').write_text(json.dumps(status,indent=2));return status

if __name__=='__main__':
 try:state=main()
 except Exception as e:
  state={'status':'RESTORATION_OR_RUN_FAILURE','error':repr(e),'traceback':traceback.format_exc()}
  (O/'VERIFICATION.json').write_text(json.dumps(state,indent=2))
 print('FINAL_STATUS',state['status'],flush=True)
