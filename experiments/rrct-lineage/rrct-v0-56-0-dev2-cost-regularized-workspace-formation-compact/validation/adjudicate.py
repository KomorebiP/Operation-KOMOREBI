from __future__ import annotations
import csv,json,pathlib,sys
import numpy as np
import torch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import workspace_formation as wf

LAMBDAS=(0.0,0.01,0.03,0.05,0.08,0.12,0.16,0.20,0.22,0.24,0.26,0.30,0.40)

def aggregate(rows):
 def mean(k): return float(np.mean([float(r[k]) for r in rows]))
 return {
  'seed_count':len(rows),'mean_task_accuracy':mean('task_accuracy'),'minimum_task_accuracy':min(float(r['task_accuracy']) for r in rows),
  'mean_route_accuracy':mean('route_accuracy'),'minimum_route_accuracy':min(float(r['route_accuracy']) for r in rows),
  'mean_cost':mean('mean_cost'),'mean_oracle_cost':mean('oracle_cost'),'mean_excess_cost':mean('excess_cost'),
  'maximum_absolute_excess_cost':max(abs(float(r['excess_cost'])) for r in rows),
  'mean_shuffled_cue_task_accuracy':mean('shuffled_cue_task_accuracy') if 'shuffled_cue_task_accuracy' in rows[0] else None,
  'mean_shuffled_cue_route_accuracy':mean('shuffled_cue_route_accuracy') if 'shuffled_cue_route_accuracy' in rows[0] else None,
  'mean_dissolution_accuracy':mean('dissolution_accuracy') if 'dissolution_accuracy' in rows[0] else None,
  'mean_graph_switch_accuracy':mean('graph_switch_accuracy') if 'graph_switch_accuracy' in rows[0] else None,
  'mean_route_patch_change_rate':mean('route_patch_change_rate') if 'route_patch_change_rate' in rows[0] else None,
  'route_by_task':np.mean(np.asarray([r['route_by_task'] for r in rows],float),axis=0).tolist(),
  'accuracy_by_task':np.mean(np.asarray([r['accuracy_by_task'] for r in rows],float),axis=0).tolist() if 'accuracy_by_task' in rows[0] else None,
 }

def main()->int:
 receipt=json.loads((ROOT/'validation/HOLDOUT_SEED_SELECTION.json').read_text()); primary=[json.loads((ROOT/'results'/f'primary_seed_{s}.json').read_text()) for s in receipt['primary_seeds']]; primary_agg=aggregate(primary)
 edge=[]
 for lam in LAMBDAS:
  rows=[json.loads((ROOT/'results'/f'edge_l{lam:.2f}_seed_{s}.json').read_text()) for s in receipt['edge_seeds']]; a=aggregate(rows); a['lambda_cost']=lam; edge.append(a)
 naive=[json.loads((ROOT/'results'/f'naive_seed_{s}.json').read_text()) for s in receipt['edge_seeds']]
 naive_agg=aggregate(naive)
 gold=[r for r in edge if r['mean_task_accuracy']>=0.99 and r['mean_route_accuracy']>=0.99]; band=[min(r['lambda_cost'] for r in gold),max(r['lambda_cost'] for r in gold)] if gold else []
 first_under=next((r for r in edge if r['lambda_cost']>0.12 and r['mean_task_accuracy']<0.99),None)
 sample=wf.sample_batch(120000,torch.Generator().manual_seed(560562),0.0); losses=wf.route_losses(sample['routes'],sample['target']); break_even={}
 for task in range(6):
  if task==0: value=None
  else:
   mask=sample['task_ids']==task; value=float((losses[mask,0]-losses[mask,task]).mean())/float(wf.ROUTE_COSTS[task]-wf.ROUTE_COSTS[0])
  break_even[wf.TASK_NAMES[task]]=value
 endpoints={
  'E01_all_seed_task_accuracy':all(r['task_accuracy']>=0.995 for r in primary),'E02_all_seed_route_accuracy':all(r['route_accuracy']>=0.995 for r in primary),'E03_all_seed_cost_optimal':all(abs(r['excess_cost'])<=0.01 for r in primary),
  'E04_all_task_route_accuracy':all(primary_agg['route_by_task'][i][i]>=0.995 for i in range(6)),'E05_local_closure':primary_agg['route_by_task'][0][0]>=0.995,'E06_flat_depth_one':primary_agg['route_by_task'][1][1]>=0.995,
  'E07_pair_graph_01_23':primary_agg['route_by_task'][2][2]>=0.995,'E08_pair_graph_02_13':primary_agg['route_by_task'][3][3]>=0.995,'E09_pair_graph_03_12':primary_agg['route_by_task'][4][4]>=0.995,'E10_overlap_full_route':primary_agg['route_by_task'][5][5]>=0.995,
  'E11_shuffle_route_failure':primary_agg['mean_shuffled_cue_route_accuracy']<=0.30,'E12_shuffle_task_failure':primary_agg['mean_shuffled_cue_task_accuracy']<=0.55,'E13_workspace_dissolution':primary_agg['mean_dissolution_accuracy']>=0.995,'E14_graph_switching':primary_agg['mean_graph_switch_accuracy']>=0.995,'E15_route_patch_causal':primary_agg['mean_route_patch_change_rate']>=0.70,
  'E16_zero_cost_overformation':edge[0]['mean_task_accuracy']>=0.99 and edge[0]['mean_excess_cost']>=0.70,'E17_high_cost_underformation':next(r for r in edge if r['lambda_cost']==0.30)['mean_task_accuracy']<=0.90,'E18_nonempty_goldilocks_band':bool(band) and band[0]<=0.05 and band[1]>=0.16,
  'E19_overlap_fails_first':first_under is not None and first_under['route_by_task'][5][5]<0.99 and all(first_under['route_by_task'][i][i]>=0.99 for i in range(5)),'E20_break_even_consistency':first_under is not None and abs(first_under['lambda_cost']-break_even['overlap'])<=0.06,
  'E21_router_no_task_index':all(not r['router_uses_task_ids'] for r in primary),'E22_no_valence_or_self_preservation':all(not r['valence_model_present'] and r['self_preservation_reward']==0 for r in primary),'E23_naive_router_overbuilds':naive_agg['mean_task_accuracy']>=0.99 and naive_agg['mean_excess_cost']>=0.50,
 }
 analysis={'schema':'rrct.v056.workspace_formation_analysis.v2','version':'0.56.0.dev2','status':'V056_CONFIRMATION_ENDPOINTS_MET' if all(endpoints.values()) else 'V056_CONFIRMATION_ENDPOINTS_NOT_MET','all_endpoints_met':all(endpoints.values()),'endpoint_count':len(endpoints),'endpoints':endpoints,'primary_seeds':receipt['primary_seeds'],'edge_seeds':receipt['edge_seeds'],'primary':primary_agg,'cost_edge':edge,'goldilocks_cost_band':band,'first_underformation':first_under,'break_even_lambda':break_even,'naive_expected_loss_control':naive_agg,'task_names':list(wf.TASK_NAMES),'route_names':list(wf.ROUTE_NAMES),'route_costs':wf.ROUTE_COSTS.tolist(),'claim_boundary':'Task-conditioned selection over a supplied route library and supplied public dependency signature. No graph invention or awareness claim.'}
 (ROOT/'results/ANALYSIS.json').write_text(json.dumps(analysis,indent=2,sort_keys=True)+'\n')
 with (ROOT/'results/COST_EDGE.csv').open('w',newline='') as f:
  keys=['lambda_cost','mean_task_accuracy','mean_route_accuracy','mean_cost','mean_oracle_cost','mean_excess_cost']; w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows([{k:r[k] for k in keys} for r in edge])
 print(json.dumps({'status':analysis['status'],'passed':sum(endpoints.values()),'total':len(endpoints),'band':band,'first_under':None if first_under is None else first_under['lambda_cost'],'overlap_break_even':break_even['overlap']},sort_keys=True)); return 0 if all(endpoints.values()) else 1
if __name__=='__main__': raise SystemExit(main())
