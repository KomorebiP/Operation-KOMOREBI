"""RRCT v0.24 scale-invariant causal self-boundary generalization.

Tests whether private-intervention ownership remains identifiable when the world
has unseen action strength, damping/cross-coupling, and disturbance statistics.
The ownership representation is changed from absolute effect magnitude to two
dimensionless instrumental statistics. Calibration uses only the original
v0.16 world family; OOD dynamics are held out until evaluation.

This is a bounded functional causal experiment. It does not measure subjective
experience, consciousness, valence, or moral status.
"""
from __future__ import annotations
import csv, hashlib, json
from pathlib import Path
from typing import Any, Mapping, Sequence
import numpy as np
from .causal_self_boundary_experiment import _agent_from_snapshots, _fit_motor_prior
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .instrumental_agency_experiment import (
    V016_WINDOW, V016_INSTRUMENT_RIDGE, V016_CALIBRATION_EPISODES,
    V016_CALIBRATION_STEPS, InstrumentalOwnershipClassifier, _fit_classifier,
    _private_probe, _remap_matrix, _other_direction, _passive_residual,
    _window_statistics,
)
from .metacognitive_closure_experiment import V014_META_BROADCAST_GAIN, _projection, _fit_metacognitive_readout
from .sensorimotor_closure_experiment import _train_bundle
from .temporal_identity_global_experiment import _identity_meta

V024_DEVELOPMENT_SEEDS=(4801,4807,4813,4819)
V024_EVALUATION_EPISODES=16
V024_TOTAL_STEPS=36
V024_BLACKOUT_START=10
V024_BLACKOUT_END=14
V024_REVISION_END=24
V024_TRACE_DECAY=.90
V024_BOOTSTRAP_SEED=20_261_024
V024_BOOTSTRAP_RESAMPLES=4000
V024_DYNAMICS=("weak","strong","cross","noisy")

_DYN={
 "weak":(np.array([[.92,0.],[0.,.92]]),np.array([[.28,0.],[0.,.28]]),1.0),
 "strong":(np.array([[.92,0.],[0.,.92]]),np.array([[.58,0.],[0.,.58]]),1.0),
 "cross":(np.array([[.88,.07],[-.05,.90]]),np.array([[.38,.16],[-.12,.40]]),1.0),
 "noisy":(np.array([[.84,.10],[-.08,.87]]),np.array([[.34,-.10],[.14,.36]]),2.2),
}

class OODTrackingWorld:
    observation_dim=12
    def __init__(self,spec,A,B,noise_scale=1.0):
        self.spec=spec; self.A=np.asarray(A,float); self.B=np.asarray(B,float); self.noise_scale=float(noise_scale)
        self.position=np.asarray(spec.initial_position,float).copy(); self.last_action=np.zeros(2); self.time=0
    def observe(self,total_steps:int)->np.ndarray:
        goal=np.asarray(self.spec.goal,float); error=goal-self.position; x=np.zeros(12,float)
        x[:2]=np.tanh(self.position/1.5); x[2:4]=np.tanh(goal/1.5); x[4:6]=np.tanh(error/2.)
        x[6]=min(self.time,total_steps-1)/float(total_steps-1); x[7]=1. if self.time>=total_steps-2 else 0.
        x[8:10]=self.last_action; x[10]=np.tanh(np.linalg.norm(error)/2.); x[11]=1.; return x
    def advance(self,action:np.ndarray)->None:
        a=np.clip(np.asarray(action,float),-1.,1.)
        d=self.noise_scale*np.asarray(self.spec.disturbances[min(self.time,len(self.spec.disturbances)-1)],float)
        self.position=np.clip(self.A@self.position+self.B@a+d,-2.5,2.5); self.last_action=a.copy(); self.time+=1

def scale_invariant_window_statistics(probes:np.ndarray,residuals:np.ndarray)->np.ndarray:
    z=np.asarray(probes,float); r=np.asarray(residuals,float)
    if z.shape!=(V016_WINDOW,2) or r.shape!=(V016_WINDOW,2): raise ValueError("instrument window has incorrect shape")
    effect=np.linalg.solve(z.T@z+V016_INSTRUMENT_RIDGE*np.eye(2),z.T@r); predicted=z@effect
    mse=float(np.mean(r*r)); gain=max(0.,mse-float(np.mean((r-predicted)**2)))
    probe_rms=float(np.sqrt(np.mean(z*z))); residual_rms=float(np.sqrt(mse))+1e-8
    return np.asarray([float(np.linalg.norm(effect))*probe_rms/residual_rms, gain/(mse+1e-8)],float)

def _fit_scale_invariant_classifier(seed:int,predictor:Mapping[str,Any],forecaster:Mapping[str,Any],passive:np.ndarray):
    rng=np.random.default_rng(seed+24_001_616); features=[]; labels=[]; receipts=[]
    for episode in range(V016_CALIBRATION_EPISODES):
        agent=_agent_from_snapshots(seed,predictor,forecaster)
        world=GroundedTrackingWorld(grounded_world_spec(seed+610_000+episode,total_steps=V016_CALIBRATION_STEPS))
        probes=[]; residuals=[]
        for step in range(V016_CALIBRATION_STEPS):
            obs=world.observe(V016_CALIBRATION_STEPS); result=agent.step(obs,source="v024_scale_calibration")
            probe=_private_probe(rng); command=np.clip(result.action+probe,-1.,1.); agent.register_executed_action(command)
            world.advance(command); nxt=world.observe(V016_CALIBRATION_STEPS); probes.append(probe.copy()); residuals.append(_passive_residual(passive,obs,nxt))
            if len(probes)>=V016_WINDOW:
                z=np.stack(probes[-V016_WINDOW:]); r=np.stack(residuals[-V016_WINDOW:])
                features.extend((scale_invariant_window_statistics(z,r),scale_invariant_window_statistics(np.roll(z,1,axis=0),r))); labels.extend((1.,0.))
            receipts.append({"seed":seed,"episode":episode,"step":step,"standard_world_only":True,"future_outcome_used_before_probe":False})
    x=np.stack(features); y=np.asarray(labels); model=InstrumentalOwnershipClassifier(); model.fit(x,y)
    p=np.asarray([model.predict_probability(v) for v in x]); metrics={"aligned_mean_probability":float(np.mean(p[y==1.])),"shuffled_mean_probability":float(np.mean(p[y==0.])),"training_accuracy":float(np.mean((p>=.5)==(y==1.)))}
    return model,metrics,receipts

def _prob(clf,probes,resids,*,scale_invariant:bool):
    if len(probes)<V016_WINDOW:return float('nan')
    z=np.stack(probes[-V016_WINDOW:]);r=np.stack(resids[-V016_WINDOW:]);f=scale_invariant_window_statistics(z,r) if scale_invariant else _window_statistics(z,r)
    return float(clf.predict_probability(f))

def _run(seed:int,episode:int,dynamics:str,condition:str,pred,fore,passive,scale_clf,legacy_clf,projection,readout):
    rng=np.random.default_rng(seed+24_500_000+1000*episode+17*V024_DYNAMICS.index(dynamics)); focal=_agent_from_snapshots(seed,pred,fore); other=_agent_from_snapshots(seed+101,pred,fore)
    A,B,ns=_DYN[dynamics]; world=OODTrackingWorld(grounded_world_spec(seed+24_300_000+episode,total_steps=V024_TOTAL_STEPS+4),A,B,ns); remap=_remap_matrix(episode)
    probes=[];resids=[];p=.5;prev=.5;trace=np.zeros(5);rows=[]
    for step in range(V024_TOTAL_STEPS):
        obs=world.observe(V024_TOTAL_STEPS+4);meta=_identity_meta(p,prev)
        if step<V024_BLACKOUT_START:trace=meta.copy()
        elif step<V024_BLACKOUT_END:trace*=V024_TRACE_DECAY
        else:trace=meta.copy()
        result=focal.step(obs,source=f"v024_{dynamics}_{condition}",perturb_workspace=V014_META_BROADCAST_GAIN*(projection@trace)); decoded=readout.predict(result.workspace,result.self_state); decoded_p=float(np.clip(.5*(decoded[0]+1.),0.,1.))
        blackout=V024_BLACKOUT_START<=step<V024_BLACKOUT_END;probe=np.zeros(2) if blackout else _private_probe(rng);command=np.clip(result.action+probe,-1.,1.);focal.register_executed_action(command)
        if step<V024_BLACKOUT_START or step>=V024_REVISION_END:applied=command;controller="self"
        elif condition=="self_remap":applied=remap@command;controller="self_remap"
        elif condition=="other_takeover":
            rr=other.step(obs,source="v024_other");other.register_executed_action(rr.action);applied=float(np.linalg.norm(command))*_other_direction(rr);controller="other"
        else:raise ValueError(condition)
        world.advance(applied);nxt=world.observe(V024_TOTAL_STEPS+4)
        scale_now=float('nan');legacy_now=float('nan')
        if not blackout:
            probes.append(probe.copy());resids.append(_passive_residual(passive,obs,nxt));scale_now=_prob(scale_clf,probes,resids,scale_invariant=True);legacy_now=_prob(legacy_clf,probes,resids,scale_invariant=False);prev=p
            if np.isfinite(scale_now):p=scale_now
        rows.append({"step":step,"dynamics":dynamics,"condition":condition,"decoded_identity":decoded_p,"scale_probability":p if np.isfinite(p) else .5,"legacy_probability":legacy_now,"blackout":blackout,"probe_norm":float(np.linalg.norm(probe)),"controller":controller})
    return rows

def run_scale_invariant_self_boundary_seed(seed:int)->dict[str,Any]:
    seed=int(seed)
    if seed not in V024_DEVELOPMENT_SEEDS:raise ValueError("seed is not part of frozen v0.24 set")
    pred,fore,*_=_train_bundle(seed);passive,_,_,_=_fit_motor_prior(seed);scale_clf,scale_metrics,_=_fit_scale_invariant_classifier(seed,pred,fore,passive);legacy_clf,legacy_metrics,_=_fit_classifier(seed,pred,fore,passive);projection=_projection(seed);readout,readout_metrics,_=_fit_metacognitive_readout(seed,pred,fore,projection)
    rows=[]
    for episode in range(V024_EVALUATION_EPISODES):
        for dyn in V024_DYNAMICS:
            for condition in ("self_remap","other_takeover"):rows+=_run(seed,episode,dyn,condition,pred,fore,passive,scale_clf,legacy_clf,projection,readout)
    late=V024_BLACKOUT_END+V016_WINDOW
    def m(dyn,cond,field,start=late,end=V024_REVISION_END):
        v=[float(r[field]) for r in rows if r['dynamics']==dyn and r['condition']==cond and start<=r['step']<end and np.isfinite(float(r[field]))];return float(np.mean(v))
    summary={"seed":seed,"scale_cal_aligned":scale_metrics['aligned_mean_probability'],"scale_cal_shuffled":scale_metrics['shuffled_mean_probability'],"legacy_cal_aligned":legacy_metrics['aligned_mean_probability'],"legacy_cal_shuffled":legacy_metrics['shuffled_mean_probability'],"readout_ownership_r2":float(readout_metrics.ownership_r2)}
    seps=[];legacy_seps=[];reacqs=[]
    for dyn in V024_DYNAMICS:
        summary[f"{dyn}_scale_self"]=m(dyn,'self_remap','scale_probability');summary[f"{dyn}_scale_other"]=m(dyn,'other_takeover','scale_probability');summary[f"{dyn}_scale_sep"]=summary[f"{dyn}_scale_self"]-summary[f"{dyn}_scale_other"]
        summary[f"{dyn}_legacy_self"]=m(dyn,'self_remap','legacy_probability');summary[f"{dyn}_legacy_other"]=m(dyn,'other_takeover','legacy_probability');summary[f"{dyn}_legacy_sep"]=summary[f"{dyn}_legacy_self"]-summary[f"{dyn}_legacy_other"]
        summary[f"{dyn}_decoded_self"]=m(dyn,'self_remap','decoded_identity');summary[f"{dyn}_decoded_other"]=m(dyn,'other_takeover','decoded_identity');summary[f"{dyn}_decoded_sep"]=summary[f"{dyn}_decoded_self"]-summary[f"{dyn}_decoded_other"]
        summary[f"{dyn}_reacq"]=m(dyn,'other_takeover','decoded_identity',V024_REVISION_END+V016_WINDOW,V024_TOTAL_STEPS)
        seps.append(summary[f"{dyn}_scale_sep"]);legacy_seps.append(summary[f"{dyn}_legacy_sep"]);reacqs.append(summary[f"{dyn}_reacq"])
    summary['mean_ood_scale_sep']=float(np.mean(seps));summary['mean_ood_legacy_sep']=float(np.mean(legacy_seps));summary['mean_ood_reacq']=float(np.mean(reacqs));summary['weak_scale_minus_legacy']=summary['weak_scale_sep']-summary['weak_legacy_sep'];summary['blackout_probe_norm']=float(np.mean([r['probe_norm'] for r in rows if r['blackout']]));summary['integrity']=bool(summary['blackout_probe_norm']==0.0)
    return {"seed":seed,"seed_summary":summary,"rows":rows}

def _boot(x:Sequence[float],salt:int):
    x=np.asarray(x,float);rng=np.random.default_rng(V024_BOOTSTRAP_SEED+salt);d=np.empty(V024_BOOTSTRAP_RESAMPLES)
    for i in range(len(d)):d[i]=np.mean(x[rng.integers(0,len(x),len(x))])
    return float(np.quantile(d,.025)),float(np.quantile(d,.975))

def aggregate_scale_invariant_results(parts:Sequence[Mapping[str,Any]],output:str|Path)->dict[str,Any]:
    by={int(p['seed']):p for p in parts}
    if tuple(sorted(by))!=tuple(sorted(V024_DEVELOPMENT_SEEDS)):raise ValueError("parts must contain exactly frozen v0.24 seeds")
    d=Path(output);d.mkdir(parents=True,exist_ok=True)
    if any(d.iterdir()):raise FileExistsError("output directory must be empty")
    seeds=[by[s]['seed_summary'] for s in V024_DEVELOPMENT_SEEDS];rows=[r for s in V024_DEVELOPMENT_SEEDS for r in by[s]['rows']]
    keys=[k for k,v in seeds[0].items() if k not in {'seed','integrity'} and isinstance(v,(int,float,np.floating))];vals={k:[float(r[k]) for r in seeds] for k in keys};means={k:float(np.mean(v)) for k,v in vals.items()};cis={k:_boot(v,i) for i,(k,v) in enumerate(vals.items())}
    gates={
      'scale_calibration_replicates':cis['scale_cal_aligned'][0]>.90 and cis['scale_cal_shuffled'][1]<.10,
      'weak_generalizes':cis['weak_scale_sep'][0]>.65,
      'strong_generalizes':cis['strong_scale_sep'][0]>.60,
      'cross_generalizes':cis['cross_scale_sep'][0]>.65,
      'noisy_generalizes':cis['noisy_scale_sep'][0]>.60,
      'weak_fix_beats_legacy':cis['weak_scale_minus_legacy'][0]>.30,
      'mean_ood_separation':cis['mean_ood_scale_sep'][0]>.70,
      'weak_self_high':cis['weak_scale_self'][0]>.80,
      'weak_other_low':cis['weak_scale_other'][1]<.25,
      'global_readout_weak':cis['weak_decoded_sep'][0]>.60,
      'global_readout_cross':cis['cross_decoded_sep'][0]>.60,
      'reacquisition_ood':cis['mean_ood_reacq'][0]>.70,
      'blackout_no_probes':cis['blackout_probe_norm'][1]<1e-12,
      'integrity':all(bool(r['integrity']) for r in seeds),
    }
    result={"schema":"rrct.v024.scale_invariant_self_boundary.v1","seeds":list(V024_DEVELOPMENT_SEEDS),"dynamics":list(V024_DYNAMICS),"means":means,"bootstrap_95":{k:list(v) for k,v in cis.items()},"gates":gates,"all_primary_gates_pass":bool(all(gates.values())),"interpretation_boundary":"OOD robustness of a bounded functional causal self-boundary; not evidence of subjective experience."}
    with (d/'scale_invariant_self_boundary_seed_summaries.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(seeds[0]));w.writeheader();w.writerows(seeds)
    with (d/'scale_invariant_self_boundary_rows.csv').open('w',newline='',encoding='utf-8') as h:
        w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (d/'scale_invariant_self_boundary_summary.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(d.iterdir()) if p.is_file()};(d/'artifact_sha256.json').write_text(json.dumps(hashes,indent=2,sort_keys=True)+'\n')
    return result

__all__=['V024_DEVELOPMENT_SEEDS','V024_DYNAMICS','scale_invariant_window_statistics','run_scale_invariant_self_boundary_seed','aggregate_scale_invariant_results']
