from __future__ import annotations
import concurrent.futures,json,multiprocessing as mp,os,pathlib,sys
from dataclasses import asdict
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from workspace_edge import DEFAULT_CHECKPOINTS,train_trajectory
SETTINGS=((10,8),(12,6),(14,5),(16,4),(20,3))
def worker(task):
 d,h,s=task
 return asdict(train_trajectory(dim=d,hidden=h,base_seed=s,checkpoints=DEFAULT_CHECKPOINTS))
def main():
 seeds=json.loads((ROOT/'validation/OVERCOMPLETE_SEEDS.json').read_text())['seeds']
 out=ROOT/'results/overcomplete';out.mkdir(parents=True,exist_ok=True)
 tasks=[(d,h,s) for d,h in SETTINGS for s in seeds if not (out/f'd{d}_h{h}_seed{s}.json').exists()]
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(4,os.cpu_count() or 1),mp_context=mp.get_context('spawn')) as ex:
  fm={ex.submit(worker,t):t for t in tasks}
  for i,f in enumerate(concurrent.futures.as_completed(fm),1):
   d,h,s=fm[f];r=f.result();(out/f'd{d}_h{h}_seed{s}.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
   print(json.dumps({'completed':i,'total':len(tasks),'dim':d,'hidden':h,'seed':s,'onset':r['stable_onset_step']}),flush=True)
if __name__=='__main__':raise SystemExit(main())
