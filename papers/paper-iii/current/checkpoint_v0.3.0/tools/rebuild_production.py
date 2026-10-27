#!/usr/bin/env python3
"""Cold own-project rebuild, retaining only authenticated pinned upstream caches."""
from pathlib import Path
import argparse,datetime,hashlib,json,subprocess,sys,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--kit',type=Path,required=True);ap.add_argument('--run-name',default='final');a=ap.parse_args();r=Path(__file__).resolve().parents[1]
 obj=r/'build'/f'{a.run_name}_objects'
 if obj.exists():raise SystemExit(f'Refusing nonempty or existing own-object destination: {obj}')
 obj.mkdir();mods=json.loads((r/'coverage/PRODUCTION_MODULES.json').read_text());src=r/'formal/current';t=time.monotonic()
 hashes={m:sha(src/(m.replace('.','/')+'.lean')) for m in mods}
 report={'schema':'paper-iii.production-rebuild/1','status':'RUNNING','started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'own_objects_initially_empty':True,'upstream_cache_rebuilt':False,'source_hashes':hashes,'runner_sha256':sha(r/'tools/run_lean.py'),'commands':[]}
 out=r/'verification'/f'PRODUCTION_REBUILD_{a.run_name}.json'
 out.write_text(json.dumps(report,indent=2)+'\n')
 for m in mods:
  cmd=[sys.executable,str(r/'tools/run_lean.py'),m,'--kit',str(a.kit),'--objects',str(obj),'--tag',a.run_name,'--timeout','300']
  process=subprocess.run(cmd,capture_output=True,text=True);print(process.stdout[:3000],flush=True)
  receipt=json.loads(process.stdout.splitlines()[0]);path=Path(receipt['receipt']);data=json.loads(path.read_text());report['commands'].append({'module':m,'receipt':str(path.relative_to(r)),'status':data['status']})
  out.write_text(json.dumps(report,indent=2)+'\n')
  if process.returncode!=0:break
 report['unchanged']=all(sha(src/(m.replace('.','/')+'.lean'))==h for m,h in hashes.items())
 report['status']='PASS' if len(report['commands'])==len(mods) and all(x['status']=='PASS' for x in report['commands']) and report['unchanged'] else 'FAIL'
 report['elapsed_seconds']=time.monotonic()-t;out.write_text(json.dumps(report,indent=2)+'\n')
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
