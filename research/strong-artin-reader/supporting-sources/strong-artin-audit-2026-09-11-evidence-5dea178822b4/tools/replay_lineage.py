from pathlib import Path
import json,os,subprocess,time,hashlib,re,shutil,argparse
ap=argparse.ArgumentParser();ap.add_argument('--max-modules',type=int,default=10);ap.add_argument('--skip',nargs='*',default=[]);ap.add_argument('--scope',choices=['current','union'],default='current');a=ap.parse_args()
root=Path('/mnt/data/Strong_Artin_Audit_2026-09-11');inv=json.loads((root/'inventory.json').read_text());kit=root/'runtime/Komorebi_Portable_Lean_4.34.0-rc2';ws=kit/'workspace';lean=kit/'toolchain/bin/lean';H=lambda b:hashlib.sha256(b).hexdigest()
if a.scope=='current':
 ah=next(r['sha256'] for r in inv['by_root'] if r['archive']==inv['current_root']);seen=set();ss=set()
 def walk(h):
  if h in seen:return
  seen.add(h);ss.update(inv['archives'][h]['sources'])
  for x in inv['archives'][h]['nested']:walk(x)
 walk(ah)
else:ss=set(inv['sources'])
selected={Path(inv['sources'][s]['basename']).stem:inv['sources'][s] for s in ss}
out=root/('lineage_replay_'+a.scope);stage=out/'src';obj=out/'olean';logs=out/'logs'
for p in [stage,obj,logs]:p.mkdir(parents=True,exist_ok=True)
for m,s in selected.items():
 b=(root/s['audit_path']).read_bytes();dest=stage/(m+'.lean')
 if dest.exists() and dest.read_bytes()!=b:raise RuntimeError('source changed')
 if not dest.exists():dest.write_bytes(b)
order=[];done=set();pending=set()
def visit(m):
 if m in done:return
 if m in pending:raise RuntimeError('dependency cycle '+m)
 pending.add(m)
 for line in selected[m]['imports']:
  for imp in line.split():
   if imp in selected:visit(imp)
 pending.remove(m);done.add(m);order.append(m)
for m in sorted(selected):visit(m)
progress=out/'progress.json';data=json.loads(progress.read_text()) if progress.exists() else {'scope':a.scope,'status':'INCOMPLETE','order':order,'module_results':[],'failures':[]}
if data['order']!=order:raise RuntimeError('order changed')
seen={r['module'] for r in data['module_results'] if r['returncode']==0}
for r in data['module_results']:
 if r['module'] in seen and H((obj/(r['module']+'.olean')).read_bytes())!=r['object_sha256']:raise RuntimeError('object changed')
lp=subprocess.check_output(['bash',str(kit/'run.sh'),'lake','env','printenv','LEAN_PATH'],cwd=ws,text=True).strip();env=os.environ.copy();env['PATH']=str(lean.parent)+':'+env.get('PATH','');env['LEAN_PATH']=str(obj)+':'+str(stage)+':'+lp
startbatch=time.monotonic();n=0
for m in order:
 if m in seen or m in a.skip:continue
 if any(imp not in seen for line in selected[m]['imports'] for imp in line.split() if imp in selected):continue
 if n>=a.max_modules or time.monotonic()-startbatch>65:break
 p=stage/(m+'.lean');o=obj/(m+'.olean');cmd=[str(lean),'-j1','-DwarningAsError=true','-R',str(stage),'-o',str(o),str(p)]
 print('CHECK',m,flush=True);t=time.monotonic()
 try:
  r=subprocess.run(cmd,cwd=ws,env=env,capture_output=True,text=True,timeout=45);rc=r.returncode;txt=r.stdout+r.stderr
 except subprocess.TimeoutExpired as e:rc=124;txt=(e.stdout or b'').decode(errors='replace') if isinstance(e.stdout,bytes) else (e.stdout or '');txt+='\nTIMEOUT 45s'
 (logs/(m+'.log')).write_text(txt)
 rec={'module':m,'source_sha256':H(p.read_bytes()),'returncode':rc,'seconds':round(time.monotonic()-t,3),'log_sha256':H(txt.encode()),'sorryAx':'sorryAx' in txt}
 if rc==0 and o.exists():rec['object_sha256']=H(o.read_bytes())
 if rc or 'sorryAx' in txt:
  data['failures'].append(rec);data['status']='INTERRUPTED';progress.write_text(json.dumps(data,indent=2));print(txt[-10000:],flush=True);print('STOPPED',m,rc);raise SystemExit(1)
 data['module_results'].append(rec);seen.add(m);n+=1
 progress.write_text(json.dumps(data,indent=2));print('PASS',m,rec['seconds'],flush=True)
data['status']='PASS' if len(seen)==len(order) else 'INCOMPLETE';data['passed_modules']=len(seen);data['total_modules']=len(order);progress.write_text(json.dumps(data,indent=2));print(data['status'],len(seen),'/',len(order),flush=True)
