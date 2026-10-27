from __future__ import annotations
import csv,json,sys,torch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import nested_workspace_experiment as e

def mean(v):return float(sum(v)/len(v))
def exact():
 b=e.make_batch(8192,torch.Generator().manual_seed(5300001));u=torch.remainder(b['values'][:,0]+b['values'][:,1],1);v=torch.remainder(b['values'][:,2]+b['values'][:,3],1);return bool(torch.allclose(u,b['u'],atol=1e-6) and torch.allclose(v,b['v'],atol=1e-6) and torch.allclose(torch.remainder(u+v,1),b['y'],atol=1e-6))
def main():
 seeds=json.loads((ROOT/'HOLDOUT_SEEDS.json').read_text())['holdout_seeds'];th=json.loads((ROOT/'THRESHOLDS.json').read_text());rs=[];mm={}
 for s in seeds:
  r=json.loads((ROOT/f'results/partial/seed_{s}.json').read_text());mm.update(r.pop('model_manifest'));rs.append(r)
 ep={
 'T01_exact_torus_share_equations':exact(),
 'T02_no_intermediate_workspace_labels':all(not r['full']['uses_intermediate_workspace_labels_for_training'] for r in rs),
 'T03_intact_action_accuracy':all(r['full']['modes']['intact']['action_accuracy']>=th['intact_action_accuracy_min'] for r in rs),
 'T04_local_a_probe':all(r['full']['probes']['local_a_to_u']['strict_accuracy']>=th['probe_accuracy_min'] for r in rs),
 'T05_local_b_probe':all(r['full']['probes']['local_b_to_v']['strict_accuracy']>=th['probe_accuracy_min'] for r in rs),
 'T06_global_probe':all(r['full']['probes']['global_to_y']['strict_accuracy']>=th['probe_accuracy_min'] for r in rs),
 'T07_each_leaf_cut':all(r['full']['modes'][f'leaf_{i}_cut']['action_accuracy']<=th['cut_action_accuracy_max'] for r in rs for i in range(4)),
 'T08_local_a_cut':all(r['full']['modes']['local_a_cut']['action_accuracy']<=th['cut_action_accuracy_max'] for r in rs),
 'T09_local_b_cut':all(r['full']['modes']['local_b_cut']['action_accuracy']<=th['cut_action_accuracy_max'] for r in rs),
 'T10_global_cut':all(r['full']['modes']['global_cut']['action_accuracy']<=th['cut_action_accuracy_max'] for r in rs),
 'T11_topdown_cut':all(r['full']['modes']['topdown_cut']['action_accuracy']<=th['cut_action_accuracy_max'] for r in rs),
 'T12_local_a_patch':all(r['full']['patches']['local_a']['strict_accuracy']>=th['patch_accuracy_min'] for r in rs),
 'T13_local_b_patch':all(r['full']['patches']['local_b']['strict_accuracy']>=th['patch_accuracy_min'] for r in rs),
 'T14_global_patch':all(r['full']['patches']['global']['strict_accuracy']>=th['patch_accuracy_min'] for r in rs),
 'T15_private_route_preserved':all(m['private_accuracy']>=th['private_accuracy_min'] for r in rs for m in r['full']['modes'].values()),
 'T16_one_dimensional_bottleneck_insufficient':all(r['capacity_one']['action_accuracy']<=th['one_dimensional_accuracy_max'] for r in rs),
 'T17_flat_full_access_solves':all(r['flat']['action_accuracy']>=th['flat_accuracy_min'] for r in rs),
 'T18_no_valence_or_self_preservation':all(not r['full']['valence_model_present'] and r['full']['self_preservation_reward']==0.0 for r in rs)}
 ok=all(ep.values());analysis={'schema':'rrct.v053.holdout_analysis.v1','version':e.VERSION,'scientific_status':'terminal_loss_learned_workspace_semantics_in_supplied_hierarchy','execution_mode':'isolated frozen-seed processes','holdout_seeds':seeds,'thresholds':th,'seed_results':rs,'model_manifest':mm,'endpoints':ep,'all_endpoints_met':ok,'claim_boundary':'Terminal-loss learning of workspace semantics inside a supplied hierarchy; no spontaneous hierarchy discovery, brain equivalence, functional awareness, subjective experience, sentience, or valence claim.'};analysis['digest']=e.canonical_digest(analysis)
 summary={'schema':'rrct.v053.summary.v1','version':e.VERSION,'status':'V053_FROZEN_ENDPOINTS_MET' if ok else 'V053_FROZEN_ENDPOINTS_NOT_MET','scientific_status':analysis['scientific_status'],'holdout_seeds':seeds,'endpoint_count':len(ep),'endpoints':ep,'all_endpoints_met':ok,'mean_intact_action_accuracy':mean([r['full']['modes']['intact']['action_accuracy'] for r in rs]),'mean_local_probe_accuracy':mean([.5*(r['full']['probes']['local_a_to_u']['strict_accuracy']+r['full']['probes']['local_b_to_v']['strict_accuracy']) for r in rs]),'mean_global_probe_accuracy':mean([r['full']['probes']['global_to_y']['strict_accuracy'] for r in rs]),'mean_leaf_cut_action_accuracy':mean([r['full']['modes'][f'leaf_{i}_cut']['action_accuracy'] for r in rs for i in range(4)]),'mean_workspace_cut_action_accuracy':mean([r['full']['modes'][m]['action_accuracy'] for r in rs for m in ('local_a_cut','local_b_cut','global_cut','topdown_cut')]),'mean_patch_accuracy':mean([r['full']['patches'][p]['strict_accuracy'] for r in rs for p in ('local_a','local_b','global')]),'mean_one_dimensional_accuracy':mean([r['capacity_one']['action_accuracy'] for r in rs]),'mean_flat_accuracy':mean([r['flat']['action_accuracy'] for r in rs]),'nested_parameter_count':rs[0]['full']['parameter_count'],'capacity_one_parameter_count':rs[0]['capacity_one']['parameter_count'],'flat_parameter_count':rs[0]['flat']['parameter_count'],'uses_intermediate_workspace_labels_for_training':False,'claim_boundary':analysis['claim_boundary'],'analysis_digest':analysis['digest']};summary['digest']=e.canonical_digest(summary)
 (ROOT/'results/analysis.json').write_text(json.dumps(analysis,indent=2,sort_keys=True)+'\n');(ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');(ROOT/'results/MODEL_SHA256.json').write_text(json.dumps(mm,indent=2,sort_keys=True)+'\n')
 rows=[]
 for r in rs:
  for n,m in r['full']['modes'].items():rows.append({'seed':r['seed'],'model':'nested','mode':n,**m})
  rows.append({'seed':r['seed'],'model':'capacity_one','mode':'intact',**r['capacity_one']});rows.append({'seed':r['seed'],'model':'flat','mode':'intact',**r['flat']})
 with (ROOT/'results/modes.csv').open('w',newline='') as h:
  f=sorted({k for row in rows for k in row});w=csv.DictWriter(h,fieldnames=f,extrasaction='ignore');w.writeheader();w.writerows(rows)
 print(json.dumps(summary,indent=2,sort_keys=True));raise SystemExit(0 if ok else 1)
if __name__=='__main__':main()
