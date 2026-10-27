from __future__ import annotations
import argparse,json,pathlib,sys
from dataclasses import asdict
import torch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import workspace_formation as wf

def main()->int:
 p=argparse.ArgumentParser(); p.add_argument('--kind',choices=('primary','edge','naive'),required=True); p.add_argument('--seed',type=int,required=True); p.add_argument('--lambda-cost',type=float,default=0.12); p.add_argument('--output',type=pathlib.Path,required=True); a=p.parse_args(); a.output.parent.mkdir(parents=True,exist_ok=True)
 if a.kind=='primary':
  result=wf.evaluate_seed(a.seed,lambda_cost=a.lambda_cost,evaluation_cases=20000); payload=asdict(result)
 elif a.kind=='edge':
  result=wf.evaluate_seed(a.seed,lambda_cost=a.lambda_cost,evaluation_cases=10000); payload=asdict(result)
 else:
  router=wf.train_naive(a.seed,lambda_cost=a.lambda_cost)
  batch=wf.sample_batch(15000,torch.Generator().manual_seed(wf.deterministic_seed(f'{a.seed}:naive-eval')),0.08)
  metric=wf.evaluate(router,batch)
  payload={'schema':'rrct.v056.naive_control.v2','seed':a.seed,'task_accuracy':metric.task_accuracy,'route_accuracy':metric.route_accuracy,'mean_cost':metric.mean_cost,'oracle_cost':metric.oracle_cost,'excess_cost':metric.excess_cost,'route_by_task':metric.route_by_task}
 a.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n'); print(a.output); return 0
if __name__=='__main__': raise SystemExit(main())
