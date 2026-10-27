from __future__ import annotations
import hashlib,json,pathlib
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1]
results=[]
for path in sorted((ROOT/'holdout_results/points').glob('*.json')):
    results.append(json.loads(path.read_text()))
if len(results)!=28: raise RuntimeError(f'expected 28 point results, found {len(results)}')
df=pd.DataFrame(results)
key=lambda d,h,s:f'd{d}_h{h}_s{s}'
summary={}
for (d,h,s),g in df.groupby(['bottleneck_dim','hidden_width','steps']):
    summary[key(int(d),int(h),int(s))]={
      'dim':int(d),'hidden':int(h),'steps':int(s),'n':len(g),
      'emergence_rate':float(g.emergence.mean()),
      'mean_action_accuracy':float(g.action_accuracy.mean()),
      'mean_probe_accuracy':float(g.probe_accuracy.mean()),
      'mean_patch_accuracy':float(g.patch_accuracy.mean()),
      'mean_cut_accuracy':float(g.cut_accuracy.mean()),
      'mean_compute':float(g.sample_parameter_product.mean()),
    }
endpoints={}
endpoints['E01_terminal_only']=bool((df.uses_intermediate_workspace_labels_for_training==False).all())
endpoints['E02_no_valence_or_self_preservation']=bool((df.valence_model_present==False).all() and (df.self_preservation_reward==0).all())
endpoints['E03_d1_negative']=summary[key(1,64,2400)]['emergence_rate']==0 and summary[key(1,64,2400)]['mean_action_accuracy']<=.15
endpoints['E04_d2_200_below']=summary[key(2,32,200)]['emergence_rate']<=.50
endpoints['E05_d2_400_near_above']=summary[key(2,32,400)]['emergence_rate']>=.75
endpoints['E06_d2_800_above']=summary[key(2,32,800)]['emergence_rate']==1.0
endpoints['E07_d4_200_below']=summary[key(4,16,200)]['emergence_rate']<=.50
endpoints['E08_d4_400_near_above']=summary[key(4,16,400)]['emergence_rate']>=.75
endpoints['E09_d4_800_above']=summary[key(4,16,800)]['emergence_rate']==1.0
emergent=df[df.emergence]
endpoints['E10_emergent_cut_necessary']=bool((emergent.cut_accuracy<=.15).all())
endpoints['E11_d2_monotone']=summary[key(2,32,200)]['emergence_rate']<=summary[key(2,32,400)]['emergence_rate']<=summary[key(2,32,800)]['emergence_rate']
endpoints['E12_d4_monotone']=summary[key(4,16,200)]['emergence_rate']<=summary[key(4,16,400)]['emergence_rate']<=summary[key(4,16,800)]['emergence_rate']
above=pd.concat([df[(df.bottleneck_dim==2)&(df.hidden_width==32)&(df.steps==800)],df[(df.bottleneck_dim==4)&(df.hidden_width==16)&(df.steps==800)]])
endpoints['E13_above_probe']=float(above.probe_accuracy.mean())>=.98
endpoints['E14_above_patch']=float(above.patch_accuracy.mean())>=.98
endpoints['E15_above_action']=float(above.action_accuracy.mean())>=.99
# d4 must reach any given observed emergence rate no later than d2 over tested levels.
d2=[summary[key(2,32,s)]['emergence_rate'] for s in [200,400,800]];d4=[summary[key(4,16,s)]['emergence_rate'] for s in [200,400,800]]
endpoints['E16_dimension_ordering']=all(b>=a for a,b in zip(d2,d4))
payload={'schema':'rrct.v054.holdout_summary.v1','status':'V054_HOLDOUT_ENDPOINTS_MET' if all(endpoints.values()) else 'V054_HOLDOUT_ENDPOINTS_NOT_MET','all_endpoints_met':all(endpoints.values()),'endpoint_count':len(endpoints),'endpoints':endpoints,'configuration_summaries':summary,'point_count':len(df),'seed_count':int(df.seed.nunique()),'seeds':sorted(int(x) for x in df.seed.unique())}
raw=json.dumps(payload,indent=2,sort_keys=True)+'\n';(ROOT/'holdout_results/HOLDOUT_SUMMARY.json').write_text(raw)
df.to_csv(ROOT/'holdout_results/HOLDOUT_POINTS.csv',index=False)
payload['digest']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest();(ROOT/'holdout_results/HOLDOUT_ANALYSIS.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
print(json.dumps(payload,indent=2,sort_keys=True))
