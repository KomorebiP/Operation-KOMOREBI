from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time,platform
R=Path(__file__).resolve().parents[1]
P=R/'predecessor/komorebi_pnp_cut_comparison'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
seal=json.loads((P/'ARTIFACT_SEAL.json').read_text())
for name,h in seal['files'].items():assert sha(P/name)==h,('source drift',name)
# Full immediate-predecessor run in a separate working copy. Original remains sealed.
S=R/'results/predecessor_replay'
if S.exists():shutil.rmtree(S)
shutil.copytree(P,S)
before={k:sha(P/k) for k in seal['files']}
start=time.perf_counter()
run=subprocess.run([sys.executable,str(S/'checks/run_all.py')],cwd=S,capture_output=True,text=True,timeout=180)
(R/'logs/predecessor_replay.log').write_text(run.stdout+run.stderr)
res={'argv':[sys.executable,'results/predecessor_replay/checks/run_all.py'],'elapsed_seconds':time.perf_counter()-start,'exit_code':run.returncode,'sealed_files':len(before),'scientific_comparisons':[],'python':sys.version,'platform':platform.platform()}
if run.returncode:raise RuntimeError(run.stderr[-3000:])
for f in ['cut_comparison.json','clique_packets.json']:
 assert json.loads((S/'results'/f).read_text())==json.loads((P/'results'/f).read_text()),f
 res['scientific_comparisons'].append(f)
assert all(sha(P/k)==v for k,v in before.items())
res['source_unchanged']=True;res['status']='PASS'
(R/'results/predecessor_replay_record.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
