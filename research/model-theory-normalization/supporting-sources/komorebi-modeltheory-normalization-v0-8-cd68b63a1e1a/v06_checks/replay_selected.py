#!/usr/bin/env python3
"""Cold selected replay on an extracted release. Writes only an external report/build."""
from pathlib import Path
import argparse,json,hashlib,subprocess,os,tempfile,time,re
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 a=argparse.ArgumentParser();a.add_argument('--runtime',type=Path);a.add_argument('--state',type=Path,required=True);a.add_argument('--init',action='store_true');a.add_argument('--batch',type=int);a.add_argument('--finish',action='store_true');a.add_argument('--skip-controls',action='store_true');arg=a.parse_args()
 if arg.init:
  if arg.state.exists():raise ValueError('preserve previous replay state before restarting')
  rt=arg.runtime.resolve();env=json.loads((ROOT/'v06_evidence/ENVIRONMENT.json').read_text());binary=rt/'toolchain/bin/lean';ver=subprocess.check_output([str(binary),'--version'],text=True).strip();assert sha(binary)==env['lean_binary_sha256'] and ver==env['lean_version']
  mods=[];seen=set()
  def visit(m):
   if m in seen:return
   seen.add(m);p=ROOT/'formalization'/(m+'.lean')
   for d in re.findall(r'^(?:public\s+)?(?:meta\s+)?import\s+([\w.]+)',p.read_text(),re.M):
    d=d.replace('.','/')
    if (ROOT/'formalization'/(d+'.lean')).exists():visit(d)
   mods.append(m)
  for m in ['EchelonExamples','EchelonCases/Case201','EchelonCases/Case202']:visit(m)
  build=Path(tempfile.mkdtemp(prefix='komorebi-v06-extracted-cold-'));logs=arg.state.parent/(arg.state.stem+'_logs');logs.mkdir(exist_ok=True);plan=[]
  for m in mods:
   out=build/(m+'.olean');out.parent.mkdir(parents=True,exist_ok=True);plan.append({'name':'build_'+m,'argv':[str(binary),'-j1','-DwarningAsError=true','-o',str(out),m+'.lean'],'expect':True})
  for name in ([] if arg.skip_controls else ['Positive','False','Placeholder','FalseMembership','LostCoupling','ZeroFuel','WrongOutput','InvalidPivot']):
   plan.append({'name':'control_'+name,'argv':[str(binary),'-j1','-DwarningAsError=true',str(ROOT/'v06_checks/controls'/(name+'.lean'))],'expect':name=='Positive'})
  paths=[ROOT/'formalization'/(m+'.lean') for m in mods]+list((ROOT/'v06_checks/controls').glob('*.lean'))+[Path(__file__)]
  st={'status':'IN_PROGRESS','started_at':now(),'root':str(ROOT),'runtime':str(rt),'build':str(build),'logs':str(logs),'modules':mods,'plan':plan,'tasks':[],'source_hashes':{str(p.relative_to(ROOT)):sha(p) for p in paths},'lean_version':ver,'scope':'Cold selected dependency replay, EchelonExamples, standalone large and torsion-stress solver evaluations. Controls included: '+str(not arg.skip_controls)+'. Not a second full 203-case rebuild.'};dump(arg.state,st);print('initialized',len(mods),len(plan));return
 st=json.loads(arg.state.read_text());assert st['root']==str(ROOT)
 for p,h in st['source_hashes'].items():assert sha(ROOT/p)==h,(p,'changed')
 for t in st['tasks']:assert sha(t['log'])==t['sha256']
 if arg.batch:
  rt=Path(st['runtime']);env=os.environ.copy();env['LEAN_PATH']=':'.join([st['build']]+[str(p) for p in (rt/'workspace/.lake/packages').glob('*/.lake/build/lib/lean')]);env['OMP_NUM_THREADS']='1'
  for p in st['plan'][len(st['tasks']):len(st['tasks'])+arg.batch]:
   log=Path(st['logs'])/(p['name'].replace('/','_')+'.log');t=time.monotonic()
   with log.open('w') as f:
    try:c=subprocess.run(p['argv'],cwd=ROOT/'formalization',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=80);rc=c.returncode;timed=False
    except subprocess.TimeoutExpired:rc=None;timed=True
   text=log.read_text();ok=not timed and (rc==0 if p['expect'] else rc not in [None,0] and 'error:' in text)
   if not p['expect'] and any(x in text.lower() for x in ['unknown module prefix','does not exist','heartbeats','out of memory']):ok=False
   rec={'name':p['name'],'argv':p['argv'],'exit_code':rc,'timed_out':timed,'passed':ok,'seconds':time.monotonic()-t,'log':str(log),'sha256':sha(log)};st['tasks'].append(rec);st['last_observed_at']=now();dump(arg.state,st);print(len(st['tasks']),rec['name'],ok,flush=True)
   if not ok:raise RuntimeError(text[-2000:])
 if arg.finish:
  assert len(st['tasks'])==len(st['plan']) and all(x['passed'] for x in st['tasks']);st['status']='PASS';st['finished_at']=now();st['source_hashes_unchanged']=True;st['compile_seconds']=sum(x['seconds'] for x in st['tasks']);dump(arg.state,st);print('PASS',len(st['modules']),len(st['tasks']))
if __name__=='__main__':main()
