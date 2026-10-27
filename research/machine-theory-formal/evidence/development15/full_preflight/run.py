import concurrent.futures, datetime, hashlib, json, os, pathlib, re, shutil, signal, subprocess, time, zipfile
ROOT=pathlib.Path.cwd(); OUT=ROOT/'evidence/development15/full_preflight'; OBJ=OUT/'objects'; LOG=OUT/'logs';LOG.mkdir(exist_ok=True)
rt=pathlib.Path('/workspace/scratch/8e3bc2f54f55/runtime15');env=os.environ.copy();env['LD_PRELOAD']=str(rt/'compat/app_path.so');env['LEAN_PATH']=':'.join([str(OBJ)]+[str(p) for p in (rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')]);env['LEAN_NUM_THREADS']='1';lean=str(rt/'toolchain/bin/lean')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(4<<20),b''):h.update(chunk)
 return h.hexdigest()
archive=ROOT/'evidence/history/block14/Komorebi_Machine_Theory_Lean_Block14_v0.14.0_complete.zip';prefix='Komorebi_Machine_Theory_Lean_Block14_v0.14.0/'
extracted=[]
with zipfile.ZipFile(archive) as z:
 manifest_bytes=z.read(prefix+'checks/NEGATIVE_CONTROLS.json');controls=json.loads(manifest_bytes);assert len(controls)==143,len(controls)
 (OUT/'controls_snapshot.json').write_bytes(manifest_bytes)
 for info in z.infolist():
  op=prefix+'evidence/final14/objects/'
  if not info.filename.startswith(op) or info.is_dir():continue
  rel=pathlib.Path(info.filename[len(op):]);assert '..' not in rel.parts
  dest=OBJ/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(info));extracted.append({'path':str(rel),'bytes':info.file_size,'sha256':digest(dest)})
 inherited_sources={c['file']:hashlib.sha256(z.read(prefix+c['file'])).hexdigest() for c in controls}
assert all(digest(ROOT/p)==h for p,h in inherited_sources.items()),'Inherited control source changed'
new=['LegalQuotient','LegalTrace','LegalQuotientExamples']
for name in new:shutil.copy2(ROOT/f'evidence/development15/objects/MachineTheory/{name}.olean',OBJ/f'MachineTheory/{name}.olean')
report={'scope':'Inherited 143 controls against complete Block14 namespace plus final new15 modules and freshly compiled aggregate. Development preflight; not cold build or replay.', 'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'per_command_timeout_seconds':45,'memory_MiB':4096,'workers':2,'object_root':str(OBJ),'retained_archive_sha256':digest(archive),'manifest_snapshot_sha256':digest(OUT/'controls_snapshot.json'),'extracted_objects':extracted,'inherited_fixture_hashes':inherited_sources,'source_pins':{str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'MachineTheory.lean']+[ROOT/f'MachineTheory/{name}.lean' for name in new]},'new_objects':{name:digest(OBJ/f'MachineTheory/{name}.olean') for name in new},'steps':[],'status':'RUNNING'}
def write_report():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
def run(name,src,expected_success,diags=(),output=None):
 argv=[lean,'-j1','-M4096','-DwarningAsError=true']
 if output:argv+=['-o',str(output)]
 argv.append(str(src));t=time.monotonic();timedout=False
 p=subprocess.Popen(argv,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
 try:text,_=p.communicate(timeout=45);code=p.returncode
 except subprocess.TimeoutExpired:
  os.killpg(p.pid,signal.SIGKILL);text,_=p.communicate();code=None;timedout=True
 log=LOG/(name+'.log');log.write_text(text);low=text.lower()
 bad=any(x in low for x in ['unknown module','unknown constant','unknown identifier','invalid import','failed to load','expected token','does not exist']);diagok=all(x.lower() in low for x in diags)
 row={'name':name,'argv':argv,'source_sha256':digest(ROOT/src) if not pathlib.Path(src).is_absolute() else digest(pathlib.Path(src)),'exit_code':code,'timed_out':timedout,'expected_success':expected_success,'expected_diagnostics':list(diags),'diagnostic_ok':diagok,'bad_import_or_resolution':bad,'seconds':time.monotonic()-t,'log':str(log.relative_to(ROOT)),'log_sha256':digest(log),'passed':((code==0) if expected_success else (code is not None and code!=0)) and not timedout and diagok and not bad}
 return row,text
row,_=run('aggregate','MachineTheory.lean',True,output=OBJ/'MachineTheory.olean');report['steps'].append(row);write_report();print('aggregate',row['passed'],flush=True)
if not row['passed']:
 report['status']='FAILED_AGGREGATE';write_report();raise SystemExit(1)
def run_control(c):
 accepted=c['expected_compile']=='accepted_then_axiom_audit_rejects';row,text=run(c['name'],c['file'],accepted,c.get('expected_diagnostics',()))
 if accepted:
  ax=[]
  for m in re.finditer(r"['‘]([^'’]+)['’] depends on axioms:\s*\[([^]]*)\]",text):ax += [a.strip() for a in m.group(2).split(',') if a.strip()]
  leaked=sorted(set(ax)-{'propext','Classical.choice','Quot.sound'});row['unapproved_axioms']=leaked;row['axiom_policy_rejected']=c['unexpected_axiom'] in leaked;row['passed']=row['passed'] and row['axiom_policy_rejected']
 return row
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for row in pool.map(run_control,controls):
  report['steps'].append(row);write_report();print(row['name'],'PASS' if row['passed'] else 'FAIL',f"{row['seconds']:.2f}s",flush=True)
report['source_pins_unchanged']=all(digest(ROOT/p)==v for p,v in report['source_pins'].items());report['inherited_fixtures_unchanged']=all(digest(ROOT/p)==v for p,v in inherited_sources.items());report['negative_controls']=len(controls);report['passed_controls']=sum(r['passed'] for r in report['steps'][1:]);report['timeouts']=sum(r['timed_out'] for r in report['steps']);report['bad_imports']=sum(r['bad_import_or_resolution'] for r in report['steps']);report['status']='PASS' if all(r['passed'] for r in report['steps']) and report['source_pins_unchanged'] and report['inherited_fixtures_unchanged'] else 'FAIL';report['ended_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();write_report();print(report['status'],report['passed_controls'],flush=True)
