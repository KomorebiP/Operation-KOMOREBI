"""RRCT v0.22 persistent temporal-self trace experiment.

v0.18-v0.21 made causal temporal identity globally accessible and increasingly
well calibrated, but exploratory interruption showed that the representation
collapsed when fresh identity broadcasts stopped. v0.22 tests a bounded
metacognitive continuity trace: a finite, decaying state updated only from the
already-earned identity/uncertainty broadcast and internally rebroadcast during
a short evidence blackout.

During the blackout there are no private motor probes and the causal ownership
classifier is frozen. Thus persistence cannot be attributed to fresh causal
self evidence. No ground-truth identity bit enters the trace.

This is a functional persistence experiment only. It does not measure
phenomenal consciousness, subjective experience, sentience, valence, or moral
status.
"""
from __future__ import annotations
import copy,csv,hashlib,json
from pathlib import Path
from typing import Any,Mapping,Sequence
import numpy as np
from .causal_self_boundary_experiment import _agent_from_snapshots,_fit_motor_prior
from .grounded_control_experiment import GroundedTrackingWorld,grounded_world_spec
from .instrumental_agency_experiment import V016_WINDOW,_fit_classifier,_other_direction,_passive_residual,_private_probe,_remap_matrix,_window_statistics
from .metacognitive_closure_experiment import V014_META_BROADCAST_GAIN,_projection
from .sensorimotor_closure_experiment import _train_bundle
from .temporal_identity_global_experiment import _identity_meta
from .self_calibrating_access_experiment import _fit_self_calibrating_readout
from .general_self_access_experiment import _evaluate_probability

V022_DEVELOPMENT_SEEDS=(4501,4507,4513,4519)
V022_EVALUATION_EPISODES=24
V022_PREHISTORY_STEPS=10
V022_POST_STEPS=14
V022_EVIDENCE_END=9
V022_BLACKOUT_START=10
V022_TRACE_DECAY=0.90
V022_BOOTSTRAP_SEED=20_261_022
V022_BOOTSTRAP_RESAMPLES=4000
V022_ARMS=("continuous","trace","no_trace","trace_lesion")
V022_BRANCHES=("causal_continuation","state_matched_impostor")

def _ownership(clf,probes,resids):
 if len(probes)<V016_WINDOW:return float('nan')
 return float(clf.predict_probability(_window_statistics(np.stack(probes[-V016_WINDOW:]),np.stack(resids[-V016_WINDOW:]))))

def _run_branch(*,seed,episode,branch,arm,focal_pre,other_pre,world_pre,passive,classifier,projection,readout):
 rng=np.random.default_rng(seed+22_220_000+1000*episode)
 agent=copy.deepcopy(focal_pre);other=copy.deepcopy(other_pre);world=copy.deepcopy(world_pre)
 if branch=="causal_continuation":agent.reset()
 remap=_remap_matrix(episode);probes=[];resids=[];p=.5;prev=.5;trace=np.zeros(5);rows=[];total=V022_PREHISTORY_STEPS+V022_POST_STEPS+4
 for step in range(V022_POST_STEPS):
  obs=world.observe(total);meta=_identity_meta(p,prev)
  if step<=V022_EVIDENCE_END: trace=meta.copy()
  else: trace*=V022_TRACE_DECAY
  if arm=="continuous":used=meta
  elif arm=="trace":used=trace
  elif arm in ("no_trace","trace_lesion"): used=meta if step<=V022_EVIDENCE_END else np.zeros(5)
  else:raise ValueError(arm)
  result=agent.step(obs,source=f"v022_{arm}_{branch}",perturb_workspace=V014_META_BROADCAST_GAIN*(projection@used))
  decoded=readout.predict(result.workspace,result.self_state);dp=float(np.clip(.5*(decoded[0]+1),0,1))
  if step<=V022_EVIDENCE_END:
   probe=_private_probe(rng)
  else:
   probe=np.zeros(2)
  command=np.clip(result.action+probe,-1,1);agent.register_executed_action(command)
  if branch=="causal_continuation":applied=remap@command
  else:
   other_result=other.step(obs,source="v022_other_controller");other.register_executed_action(other_result.action);applied=float(np.linalg.norm(command))*_other_direction(other_result)
  world.advance(applied);nxt=world.observe(total)
  if step<=V022_EVIDENCE_END:
   probes.append(probe.copy());resids.append(_passive_residual(passive,obs,nxt));new=_ownership(classifier,probes,resids);prev=p
   if np.isfinite(new):p=new
  rows.append({"seed":seed,"episode":episode,"step":step,"branch":branch,"arm":arm,"decoded_identity":dp,"frozen_ownership":p,
               "trace_identity":float(.5*(trace[0]+1)),"blackout":step>=V022_BLACKOUT_START,"private_probe_norm":float(np.linalg.norm(probe)),
               "fresh_identity_evidence":step<=V022_EVIDENCE_END,"identity_truth_used":False})
 return rows

def _run_episode(seed,episode,pred,fore,passive,classifier,projection,readout):
 rng=np.random.default_rng(seed+22_000_000+episode);total=V022_PREHISTORY_STEPS+V022_POST_STEPS+4
 focal=_agent_from_snapshots(seed,pred,fore);other=_agent_from_snapshots(seed+101,pred,fore);world=GroundedTrackingWorld(grounded_world_spec(seed+22_200_000+episode,total_steps=total))
 for step in range(V022_PREHISTORY_STEPS):
  obs=world.observe(total);fr=focal.step(obs,source="v022_pre_focal");orr=other.step(obs,source="v022_pre_other");z=_private_probe(rng);cmd=np.clip(fr.action+z,-1,1);focal.register_executed_action(cmd);other.register_executed_action(orr.action);world.advance(cmd)
 out=[]
 for arm in V022_ARMS:
  for branch in V022_BRANCHES:out+=_run_branch(seed=seed,episode=episode,branch=branch,arm=arm,focal_pre=focal,other_pre=other,world_pre=world,passive=passive,classifier=classifier,projection=projection,readout=readout)
 return out

def run_persistent_self_trace_seed(seed:int)->dict[str,Any]:
 seed=int(seed)
 if seed not in V022_DEVELOPMENT_SEEDS:raise ValueError('seed is not part of frozen v0.22 set')
 pred,fore,*_=_train_bundle(seed);passive,_,_,motor_receipts=_fit_motor_prior(seed);clf,clf_metrics,clf_receipts=_fit_classifier(seed,pred,fore,passive);projection=_projection(seed);readout,readout_metrics,readout_receipts=_fit_self_calibrating_readout(seed,pred,fore,passive,clf,projection)
 rows=[]
 for ep in range(V022_EVALUATION_EPISODES):rows+=_run_episode(seed,ep,pred,fore,passive,clf,projection,readout)
 blackout=[r for r in rows if r['blackout']]
 task_rows=[]
 for r in blackout:
  truth=1 if r['branch']=='causal_continuation' else 0
  metrics=_evaluate_probability(float(r['decoded_identity']),truth,seed=seed,episode=int(r['episode']),step=int(r['step']))
  task_rows.append({**{k:r[k] for k in ('seed','episode','step','branch','arm')},'truth':truth,**metrics})
 def m(arm,branch,field='decoded_identity',final=False):
  vals=[float(r[field]) for r in blackout if r['arm']==arm and r['branch']==branch and (not final or r['step']==V022_POST_STEPS-1)];return float(np.mean(vals))
 def tm(arm,field):return float(np.mean([float(r[field]) for r in task_rows if r['arm']==arm]))
 ts=m('trace','causal_continuation')-m('trace','state_matched_impostor');cs=m('continuous','causal_continuation')-m('continuous','state_matched_impostor');ns=m('no_trace','causal_continuation')-m('no_trace','state_matched_impostor');ls=m('trace_lesion','causal_continuation')-m('trace_lesion','state_matched_impostor')
 summary={"seed":seed,"trace_causal_identity":m('trace','causal_continuation'),"trace_impostor_identity":m('trace','state_matched_impostor'),"trace_separation":ts,"trace_final_separation":m('trace','causal_continuation',final=True)-m('trace','state_matched_impostor',final=True),"continuous_separation":cs,"no_trace_separation":ns,"lesion_separation":ls,"trace_to_continuous_ratio":ts/(cs+1e-12),"trace_provenance_accuracy":tm('trace','provenance_accuracy'),"no_trace_provenance_accuracy":tm('no_trace','provenance_accuracy'),"trace_model_error":tm('trace','model_arbitration_normalized_error'),"no_trace_model_error":tm('no_trace','model_arbitration_normalized_error'),"trace_continuation_accuracy":tm('trace','continuation_accuracy'),"no_trace_continuation_accuracy":tm('no_trace','continuation_accuracy'),"blackout_probe_norm":float(np.mean([r['private_probe_norm'] for r in blackout])),"selfcal_ownership_r2":float(readout_metrics['selfcal_ownership_r2']),"selfcal_uncertainty_r2":float(readout_metrics['selfcal_uncertainty_r2']),"aligned_mean_probability":float(clf_metrics['aligned_mean_probability']),"shuffled_mean_probability":float(clf_metrics['shuffled_mean_probability']),"integrity":bool(all(not r['identity_truth_used'] and (not r['blackout'] or (not r['fresh_identity_evidence'] and r['private_probe_norm']==0.0)) for r in rows))}
 return {'seed':seed,'seed_summary':summary,'rows':rows,'task_rows':task_rows,'motor_receipts':motor_receipts,'classifier_receipts':clf_receipts,'readout_receipts':readout_receipts}

def _boot(v,salt):
 x=np.asarray(v,float);rng=np.random.default_rng(V022_BOOTSTRAP_SEED+salt);d=np.empty(V022_BOOTSTRAP_RESAMPLES)
 for i in range(len(d)):d[i]=float(np.mean(x[rng.integers(0,len(x),size=len(x))]))
 return float(np.quantile(d,.025)),float(np.quantile(d,.975))
def aggregate_persistent_self_trace_results(parts:Sequence[Mapping[str,Any]],output:str|Path)->dict[str,Any]:
 by={int(p['seed']):p for p in parts}
 if tuple(sorted(by))!=tuple(sorted(V022_DEVELOPMENT_SEEDS)):raise ValueError('parts must contain exactly frozen v0.22 seeds')
 d=Path(output);d.mkdir(parents=True,exist_ok=True)
 if any(d.iterdir()):raise FileExistsError('output directory must be empty')
 seeds=[by[s]['seed_summary'] for s in V022_DEVELOPMENT_SEEDS];rows=[r for s in V022_DEVELOPMENT_SEEDS for r in by[s]['rows']];tasks=[r for s in V022_DEVELOPMENT_SEEDS for r in by[s]['task_rows']];keys=[k for k in seeds[0] if k not in {'seed','integrity'}];f={k:[float(r[k]) for r in seeds] for k in keys};ci={k:_boot(v,i) for i,(k,v) in enumerate(f.items())};means={k:float(np.mean(v)) for k,v in f.items()}
 gates={"trace_causal_high":ci['trace_causal_identity'][0]>.75,"trace_impostor_low":ci['trace_impostor_identity'][1]<.30,"persistent_separation":ci['trace_separation'][0]>.50,"final_persistence":ci['trace_final_separation'][0]>.40,"near_continuous":ci['trace_to_continuous_ratio'][0]>.65,"no_trace_collapses":max(abs(ci['no_trace_separation'][0]),abs(ci['no_trace_separation'][1]))<.20,"lesion_collapses":max(abs(ci['lesion_separation'][0]),abs(ci['lesion_separation'][1]))<.20,"trace_functional_routing":ci['trace_provenance_accuracy'][0]>.85 and ci['trace_continuation_accuracy'][0]>.85,"trace_beats_no_trace_routing":ci['trace_provenance_accuracy'][0]>ci['no_trace_provenance_accuracy'][1]+.25,"trace_confidence_use":ci['trace_model_error'][1]<.25 and ci['trace_model_error'][1]+.15<ci['no_trace_model_error'][0],"no_fresh_probe":ci['blackout_probe_norm'][1]<1e-12,"readout_and_classifier_replicate":ci['selfcal_ownership_r2'][0]>.90 and ci['selfcal_uncertainty_r2'][0]>.80 and ci['aligned_mean_probability'][0]>.75 and ci['shuffled_mean_probability'][1]<.25,"integrity":all(bool(r['integrity']) for r in seeds)}
 out={'schema':'rrct.v022.persistent_self_trace.v1','seeds':list(V022_DEVELOPMENT_SEEDS),'means':means,'bootstrap_95':{k:list(v) for k,v in ci.items()},'gates':gates,'all_primary_gates_pass':bool(all(gates.values())),'interpretation_limit':'Functional evidence about short-timescale persistence of globally accessible causal temporal-self content during an evidence blackout. Not evidence of phenomenal consciousness or subjective experience.'}
 def wc(name,x):
  with (d/name).open('w',newline='',encoding='utf-8') as h:w=csv.DictWriter(h,fieldnames=list(x[0]));w.writeheader();w.writerows(x)
 wc('persistent_self_trace_seed_summaries.csv',seeds);wc('persistent_self_trace_rows.csv',rows);wc('persistent_self_trace_task_rows.csv',tasks);(d/'persistent_self_trace_summary.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');hs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.iterdir()) if p.is_file()};(d/'artifact_sha256.json').write_text(json.dumps(hs,indent=2,sort_keys=True)+'\n');return out
__all__=['V022_DEVELOPMENT_SEEDS','run_persistent_self_trace_seed','aggregate_persistent_self_trace_results']
