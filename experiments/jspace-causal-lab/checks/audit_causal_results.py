"""Separate scalar/NumPy rescore. Does not trust summary scores or neural targets."""
from pathlib import Path
import json,numpy as np,hashlib
ROOT=Path(__file__).resolve().parents[1]
specs=json.loads((ROOT/'checks/causal_specs.json').read_text());summary=json.loads((ROOT/'checks/causal_assay.json').read_text())
raw=np.load(ROOT/'checks/causal_raw.npz')
def execute(bits,ops):
 a,b=map(int,bits)
 for op in ops:
  if op==1:a=1-a
  elif op==2:b=1-b
  elif op==3:a,b=b,a
  elif op!=0:raise AssertionError(op)
 return a+2*b
vals=[]
for s in specs:
 world=[0]*8
 for k,d,ss,v,fresh,alias,owner in s['events']:
  if fresh:
   assert k==0
   world[d]=v
 assert world==s['world']
 vals.append(execute([world[j] for j in s['cue']],s['ops']))
vals=np.array(vals);donors=vals^((np.arange(len(vals))%3)+1)
assert np.array_equal(vals,raw['original']);assert np.array_equal(donors,raw['target'])
metrics=0;outputs=0
for row in summary['rows']:
 lin,method,suffix=row['lineage'],row['method'],row['suffix'];key=f'{lin}_{method}_suffix{len(suffix)}'
 fv=np.array([execute([v&1,v>>1],suffix) for v in vals]);dv=np.array([execute([v&1,v>>1],suffix) for v in donors])
 pred=raw[key+'_pred'];private=raw[key+'_private'];mem=raw[key+'_memory']
 y=np.stack([dv,(dv&1)^(dv>>1),dv^3,(dv==1).astype(int)])
 yf=np.stack([fv,(fv&1)^(fv>>1),fv^3,(fv==1).astype(int)])
 rebuilt={'exact_donor_pair':float((pred[:,0]==dv).mean()),'factual_match':float((pred[:,0]==fv).mean()),
          'private_preservation':float((private==raw['roles']).mean()),'all_eight_memory':float((mem==raw['world'][None]).all(-1).mean()),
          'memory_bit_accuracy':float((mem==raw['world'][None]).mean())}
 for k,v in rebuilt.items():assert abs(v-row[k])<1e-7,(key,k,v,row[k]);metrics+=1
 for q in range(4):
  assert abs((pred[:,q]==y[q]).mean()-row['consumer_donor_match'][q])<1e-7;metrics+=1
  c=y[q]!=yf[q];assert int(c.sum())==row['contrast_case_count_by_consumer'][q]
  assert abs((pred[:,q,c]==y[q,c]).mean()-row['contrast_donor_match'][q])<1e-7;metrics+=2
 outputs+=pred.size+private.size+mem.size
# Require direct causal baseline/noise controls, without setting a workspace pass flag.
for lin in ['A','B']:
 r=[r for r in summary['rows'] if r['lineage']==lin and r['method']=='J' and r['suffix']==[]][0]
 assert r['exact_donor_pair']==1.0
for source in [ROOT/'checks/causal_support.py',ROOT/'checks/fit_causal_frames.py',ROOT/'checks/evaluate_causal_frames.py']:
 assert source.is_file()
result={'status':'PASS','recomputed_metric_entries':metrics,'recorded_output_entries':outputs,
        'scope':'Reuses histories across methods, suffixes, agents and consumers; not independent experiments.',
        'candidate_hash_matches':summary['frames_sha256']==hashlib.sha256((ROOT/'app/frames.json').read_bytes()).hexdigest()}
assert result['candidate_hash_matches']
(ROOT/'checks/causal_independent_audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
