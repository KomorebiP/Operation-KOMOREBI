from pathlib import Path
import json,hashlib,zipfile,importlib.util,subprocess,time
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25')
s=importlib.util.spec_from_file_location('v',R/'scripts/verify.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
pins=v.source_pins(); out=R/'evidence/CORE25_FROZEN_SOURCE.zip'
assert not out.exists()
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for rel in sorted(pins):z.write(R/rel,rel)
fresh=Path('/mnt/data/core25/fresh18_source');fresh.mkdir()
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert not any(n.endswith(('.olean','.ilean','.c','.o')) for n in z.namelist())
 for info in z.infolist():
  p=Path(info.filename)
  assert not p.is_absolute() and '..' not in p.parts
 z.extractall(fresh)
assert all(hashlib.sha256((fresh/r).read_bytes()).hexdigest()==h for r,h in pins.items())
record={'archive':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'bytes':out.stat().st_size,'source_inputs':pins,'source_count':len(pins),'fresh_tree':str(fresh),'contains_project_objects':False,'status':'PASS'}
(R/'evidence/SOURCE_SNAPSHOT_BLOCK18.json').write_text(json.dumps(record,indent=2)+'\n')
log=R/'evidence/launch_final18.log'
f=log.open('wb')
cmd=['python',str(R/'scripts/supervise.py'),'--runtime','/mnt/data/lean_runtime/Komorebi_Portable_Lean_4.34.0-rc2','--out','evidence/final18','--whole-timeout','1800']
p=subprocess.Popen(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);f.close()
(R/'evidence/launch_final18.json').write_text(json.dumps({'pid':p.pid,'argv':cmd,'started_at':time.time()},indent=2)+'\n')
print('Frozen inputs',len(pins),'snapshot',record['sha256'],'primary supervisor PID',p.pid)
