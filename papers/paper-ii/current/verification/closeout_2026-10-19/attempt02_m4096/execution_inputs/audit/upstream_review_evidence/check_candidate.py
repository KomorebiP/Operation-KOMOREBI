from pathlib import Path
import fcntl,hashlib,json,os,resource,signal,subprocess,time
root=Path(__file__).resolve().parents[3];base=Path(__file__).resolve().parent;prior=root/'paper2_work/final_audit_02';v=json.loads((prior/'verification.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for row in v['source_files']:assert sha(prior/row['object'])==row['object_sha256']
source=base/'ReplayClosureCandidate.lean';priorcheck=v['checks'][-1];cmd=priorcheck['command'][:-1]+[str(source)]
env=os.environ.copy();env['LEAN_PATH']=v['lean_path'];env['LD_PRELOAD']=str(root/'release_work/runtime/Komorebi_Portable_Lean_4.34.0-rc2/compat/app_path.so');env.update(priorcheck['environment_additions']);env.update(MALLOC_ARENA_MAX='2',LEAN_NUM_THREADS='1')
receipts=[]
with (root/'paper2_work/lean_serial.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX)
 for label,corrupt in [('positive','0'),('corrupt_duplicate','1')]:
  log=base/(label+'.log');env['KOMOREBI_REPLAY_DUPLICATE_CORRUPT']=corrupt;start=time.monotonic()
  with log.open('w') as f:
   p=subprocess.Popen(cmd,cwd=root,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   try:code=p.wait(timeout=240)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();code=124
  text=log.read_text();passed=code==0 if corrupt=='0' else code not in [0,124] and 'REPLAY_DUPLICATE_CORRUPT_CONTROL_INJECTED' in text and 'type mismatch' in text and 'REPLAY_UPSTREAM_DUPLICATE_RECHECKED' not in text and 'REPLAY_CLOSURE_PASS' not in text
  receipt={'label':label,'status':'PASS' if passed else 'FAIL','exit':code,'command':cmd,'source_sha256':sha(source),'prior_receipt_sha256':sha(prior/'verification.json'),'compiled_objects_authenticated':62,'extra_environment':{'KOMOREBI_REPLAY_DUPLICATE_CORRUPT':corrupt},'seconds':time.monotonic()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'log':log.name,'log_sha256':sha(log)};receipts.append(receipt)
  (base/'candidate_checks.json').write_text(json.dumps(receipts,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='command'},indent=2),flush=True)
  if not passed:raise SystemExit(1)
  if corrupt=='0':
   replayed=[json.loads(l[len('REPLAY_CHECKED '):]) for l in text.splitlines() if l.startswith('REPLAY_CHECKED ')];owned=json.loads((prior/'owned_declarations.json').read_text());assert {r['name'] for r in replayed}=={r['name'] for r in owned if not r['runtime_only']};assert len(replayed)==1944
   dup=[json.loads(l[len('REPLAY_UPSTREAM_DUPLICATE_RECHECKED '):]) for l in text.splitlines() if l.startswith('REPLAY_UPSTREAM_DUPLICATE_RECHECKED ')];assert len(dup)==1 and dup[0]['name']=='Submodule.factor.eq_1';(base/'candidate_duplicate_recheck.json').write_text(json.dumps(dup,indent=2)+'\n');print('EXACT_OWNED_LOGICAL_REPLAY_PASS 1944',flush=True)
