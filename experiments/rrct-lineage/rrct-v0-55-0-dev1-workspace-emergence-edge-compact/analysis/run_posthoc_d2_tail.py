from __future__ import annotations
import concurrent.futures, json, multiprocessing as mp, os, pathlib, sys
from dataclasses import asdict
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from workspace_edge import D1_CHECKPOINTS, train_trajectory
CHECKPOINTS=D1_CHECKPOINTS

def worker(seed:int):
 return asdict(train_trajectory(dim=2,hidden=32,base_seed=seed,checkpoints=CHECKPOINTS))

def main():
 seeds=json.loads((ROOT/'validation/SEEDS.json').read_text())['primary_base_seeds']
 out=ROOT/'results/posthoc_d2_tail';out.mkdir(parents=True,exist_ok=True)
 tasks=[s for s in seeds if not (out/f'seed{s}.json').exists()]
 with concurrent.futures.ProcessPoolExecutor(max_workers=min(4,os.cpu_count() or 1),mp_context=mp.get_context('spawn')) as ex:
  fmap={ex.submit(worker,s):s for s in tasks}
  for i,f in enumerate(concurrent.futures.as_completed(fmap),1):
   s=fmap[f];r=f.result();(out/f'seed{s}.json').write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
   print(json.dumps({'completed':i,'total':len(tasks),'seed':s,'stable_onset_step':r['stable_onset_step']}),flush=True)
 return 0
if __name__=='__main__':raise SystemExit(main())
