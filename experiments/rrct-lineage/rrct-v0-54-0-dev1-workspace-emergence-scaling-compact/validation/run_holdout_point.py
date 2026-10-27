from __future__ import annotations
import argparse, json, pathlib, sys
from dataclasses import asdict
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from workspace_scaling import train_and_evaluate
p=argparse.ArgumentParser();p.add_argument('--dim',type=int,required=True);p.add_argument('--hidden',type=int,required=True);p.add_argument('--steps',type=int,required=True);p.add_argument('--seed',type=int,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
r=train_and_evaluate(dim=a.dim,hidden=a.hidden,steps=a.steps,seed=a.seed,eval_cases=4096,calibration_cases=2048,patch_cases=2048)
payload=asdict(r);payload['uses_intermediate_workspace_labels_for_training']=False;payload['valence_model_present']=False;payload['self_preservation_reward']=0.0
payload['schema']='rrct.v054.holdout_point.v1'
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');print(json.dumps(payload,sort_keys=True))
