from pathlib import Path
import subprocess,os,sys,json,time,hashlib,signal
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25');RT=Path('/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2');OUT=R/'evidence/control_preflight18';OUT.mkdir(exist_ok=True)
env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,[Path('/mnt/data/core25/devobjects')]+sorted((RT/'workspace/.lake/packages').glob('*/.lake/build/lib/lean'))));env['LEAN_NUM_THREADS']='1'
sys.path.insert(0,str(R/'scripts'));import verify
records=[]
for c in json.loads((R/'checks/NEGATIVE_CONTROLS.json').read_text())[170:]:
 cmd=[str(RT/'toolchain/bin/lean'),'-j1','-M4096','-DwarningAsError=true',c['file']]
 t=time.monotonic();s=subprocess.Popen(cmd,cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,start_new_session=True)
 timeout=False
 try: text,_=s.communicate(timeout=45)
 except subprocess.TimeoutExpired:
  os.killpg(s.pid,signal.SIGKILL);text,_=s.communicate();timeout=True
 ok=s.returncode!=0 and not timeout and not verify.invalid_control_diagnostic(text) and all(d in text for d in c['expected_diagnostics'])
 (OUT/(c['name']+'.log')).write_text(text)
 records.append({'name':c['name'],'cmd':cmd,'source_sha256':hashlib.sha256((R/c['file']).read_bytes()).hexdigest(),'exit_code':s.returncode,'timeout':timeout,'seconds':time.monotonic()-t,'expected_rejection':ok})
 print(c['name'],'PASS' if ok else 'FAIL',s.returncode,round(records[-1]['seconds'],2))
 if not ok: print(text)
(OUT/'report.json').write_text(json.dumps({'status':'PASS' if all(r['expected_rejection'] for r in records) else 'FAIL','checks':records},indent=2)+'\n')
