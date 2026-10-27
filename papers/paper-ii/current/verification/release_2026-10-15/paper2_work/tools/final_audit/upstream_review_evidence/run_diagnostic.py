from pathlib import Path
import fcntl,hashlib,json,os,resource,signal,subprocess,time
root=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
prior=root/'paper2_work/final_audit_02';v=json.loads((prior/'verification.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in v['source_files']:assert sha(prior/row['object'])==row['object_sha256']
check=v['checks'][-1];cmd=check['command'][:-1]+[str(out/'OverlapInventory.lean')]
env=os.environ.copy();env['LEAN_PATH']=v['lean_path'];env['LD_PRELOAD']=str(root/'release_work/runtime/Komorebi_Portable_Lean_4.34.0-rc2/compat/app_path.so');env['MALLOC_ARENA_MAX']='2';env['LEAN_NUM_THREADS']='1';env.update(check['environment_additions'])
report={'status':'RUNNING','source_sha256':sha(out/'OverlapInventory.lean'),'prior_failed_receipt_sha256':sha(prior/'verification.json'),'compiled_objects_authenticated':len(v['source_files']),'command':cmd,'environment_additions':check['environment_additions'],'lean_path':v['lean_path'],'timeout_seconds':180};(out/'diagnostic_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
start=time.monotonic()
with (root/'paper2_work/lean_serial.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 with (out/'overlap_inventory.log').open('w') as log:
  p=subprocess.Popen(cmd,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  try:code=p.wait(timeout=180)
  except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
report.update(status='PASS' if code==0 else 'FAIL',exit=code,elapsed_seconds=time.monotonic()-start,max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,log_sha256=sha(out/'overlap_inventory.log'))
(out/'diagnostic_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
rows=[json.loads(l[len('OVERLAP_REVIEW '):]) for l in (out/'overlap_inventory.log').read_text().splitlines() if l.startswith('OVERLAP_REVIEW ')]
for r in rows:
 for k in ['project_type_expr','project_value_expr','upstream_type_expr','upstream_value_expr']:r[k+'_sha256']=hashlib.sha256(r[k].encode()).hexdigest()
(out/'overlap_rows.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['command','environment_additions','lean_path']},indent=2));print(json.dumps([{k:v for k,v in r.items() if not k.endswith('_expr') and k!='used_constants'} for r in rows],indent=2))
raise SystemExit(code)
