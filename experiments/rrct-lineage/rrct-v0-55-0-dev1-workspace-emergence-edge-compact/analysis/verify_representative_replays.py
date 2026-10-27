from __future__ import annotations
import json,pathlib,sys
from dataclasses import asdict
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from workspace_edge import D1_CHECKPOINTS,DEFAULT_CHECKPOINTS,train_trajectory
CASES=[
 ('primary_d1',1,44,198873906,D1_CHECKPOINTS,ROOT/'results/primary/d1_h44_seed198873906.json'),
 ('primary_d2_tail',2,32,665517235,D1_CHECKPOINTS,ROOT/'results/posthoc_d2_tail/seed665517235.json'),
 ('primary_d8',8,10,198873906,DEFAULT_CHECKPOINTS,ROOT/'results/primary/d8_h10_seed198873906.json'),
 ('overcomplete_d20',20,3,122254834,DEFAULT_CHECKPOINTS,ROOT/'results/overcomplete/d20_h3_seed122254834.json'),
]

def normalized(payload):
 payload=dict(payload);payload.pop('train_seconds',None);return json.loads(json.dumps(payload,sort_keys=True))
rows=[]
for name,d,h,s,c,path in CASES:
 expected=json.loads(path.read_text())
 observed=asdict(train_trajectory(dim=d,hidden=h,base_seed=s,checkpoints=c))
 passed=normalized(expected)==normalized(observed)
 rows.append({'name':name,'passed':passed,'expected_onset':expected['stable_onset_step'],'observed_onset':observed['stable_onset_step']})
 if not passed:
  raise SystemExit(f'replay mismatch: {name}')
out={'schema':'rrct.v055.representative_replay.v1','all_passed':all(r['passed'] for r in rows),'cases':rows}
(ROOT/'results/REPRESENTATIVE_REPLAY.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2))
