"""Exploratory RRCT v0.23 persistent-but-revisable temporal-self experiment.

Tests whether a causally earned self trace can persist through an evidence blackout,
yet revise when fresh private-intervention evidence contradicts continuity. A matched
self-remap condition preserves causal control despite embodiment change; an
other-takeover condition breaks causal control. No identity truth bit is available
to the trace or ownership classifier.
"""
from __future__ import annotations
import copy
from typing import Any, Mapping, Sequence
import numpy as np
import csv, json, hashlib
from pathlib import Path
from .causal_self_boundary_experiment import _agent_from_snapshots, _fit_motor_prior
from .grounded_control_experiment import GroundedTrackingWorld, grounded_world_spec
from .instrumental_agency_experiment import (
    V016_WINDOW, _fit_classifier, _other_direction, _passive_residual,
    _private_probe, _remap_matrix, _window_statistics,
)
from .metacognitive_closure_experiment import V014_META_BROADCAST_GAIN, _projection
from .sensorimotor_closure_experiment import _train_bundle
from .temporal_identity_global_experiment import _identity_meta
from .self_calibrating_access_experiment import _fit_self_calibrating_readout

V023_PRE_STEPS=10
V023_BLACKOUT_START=10
V023_BLACKOUT_END=14
V023_REVISION_END=24
V023_TOTAL_STEPS=36
V023_TRACE_DECAY=0.90
V023_DEVELOPMENT_SEEDS=(4601,4607,4613,4619)
V023_EVALUATION_EPISODES=24
V023_BOOTSTRAP_SEED=20_261_023
V023_BOOTSTRAP_RESAMPLES=4000
V023_CONDITIONS=("self_remap","other_takeover")
V023_ARMS=("revisable","rigid","no_trace")

def _ownership(clf, probes, resids):
    if len(probes)<V016_WINDOW: return float('nan')
    return float(clf.predict_probability(_window_statistics(np.stack(probes[-V016_WINDOW:]), np.stack(resids[-V016_WINDOW:]))))

def _run_condition(*, seed:int, episode:int, condition:str, arm:str, pred:Mapping[str,Any], fore:Mapping[str,Any], passive, clf, projection, readout):
    rng=np.random.default_rng(seed+23_000_000+1000*episode)
    agent=_agent_from_snapshots(seed,pred,fore)
    other=_agent_from_snapshots(seed+101,pred,fore)
    world=GroundedTrackingWorld(grounded_world_spec(seed+23_300_000+episode,total_steps=V023_TOTAL_STEPS+4))
    remap=_remap_matrix(episode)
    probes=[];resids=[];p=.5;prev=.5;trace=np.zeros(5);rows=[]
    for step in range(V023_TOTAL_STEPS):
        obs=world.observe(V023_TOTAL_STEPS+4)
        meta=_identity_meta(p,prev)
        if step < V023_BLACKOUT_START:
            trace=meta.copy()
        elif step < V023_BLACKOUT_END:
            trace*=V023_TRACE_DECAY
        else:
            if arm=="revisable": trace=meta.copy()
            elif arm=="rigid": trace=trace.copy()
            elif arm=="no_trace": trace=np.zeros(5)
            else: raise ValueError(arm)
        if arm=="no_trace" and step>=V023_BLACKOUT_START:
            used=np.zeros(5)
        else:
            used=trace
        result=agent.step(obs,source=f"v023_{arm}_{condition}",perturb_workspace=V014_META_BROADCAST_GAIN*(projection@used))
        decoded=readout.predict(result.workspace,result.self_state)
        dp=float(np.clip(.5*(decoded[0]+1),0,1))
        blackout=V023_BLACKOUT_START<=step<V023_BLACKOUT_END
        probe=np.zeros(2) if blackout else _private_probe(rng)
        command=np.clip(result.action+probe,-1,1)
        agent.register_executed_action(command)
        # Before the switch and after restoration, focal control is normal.
        if step < V023_BLACKOUT_START or step >= V023_REVISION_END:
            applied=command; controller="self"
        elif condition=="self_remap":
            applied=remap@command; controller="self_remap"
        elif condition=="other_takeover":
            orr=other.step(obs,source="v023_other")
            other.register_executed_action(orr.action)
            applied=float(np.linalg.norm(command))*_other_direction(orr); controller="other"
        else: raise ValueError(condition)
        world.advance(applied); nxt=world.observe(V023_TOTAL_STEPS+4)
        if not blackout:
            probes.append(probe.copy());resids.append(_passive_residual(passive,obs,nxt))
            new=_ownership(clf,probes,resids);prev=p
            if np.isfinite(new):p=new
        rows.append({
            "step":step,"condition":condition,"arm":arm,"decoded_identity":dp,
            "ownership":p,"trace_identity":float(.5*(trace[0]+1)),"blackout":blackout,
            "probe_norm":float(np.linalg.norm(probe)),"controller":controller,
            "identity_truth_used":False,
        })
    return rows

def _seed_result(seed:int, episodes:int):
    pred,fore,*_=_train_bundle(seed)
    passive,_,_,_=_fit_motor_prior(seed)
    clf,clf_metrics,_=_fit_classifier(seed,pred,fore,passive)
    projection=_projection(seed)
    readout,readout_metrics,_=_fit_self_calibrating_readout(seed,pred,fore,passive,clf,projection)
    rows=[]
    for ep in range(episodes):
        for condition in V023_CONDITIONS:
            for arm in V023_ARMS:
                rows += _run_condition(seed=seed,episode=ep,condition=condition,arm=arm,pred=pred,fore=fore,passive=passive,clf=clf,projection=projection,readout=readout)
    def mean(condition,arm,start,end,field="decoded_identity"):
        vals=[r[field] for r in rows if r['condition']==condition and r['arm']==arm and start<=r['step']<end]
        return float(np.mean(vals))
    out={"seed":seed}
    # last four blackout steps actually all blackout, compare persistence high in both conditions
    out["blackout_self_remap"]=mean("self_remap","revisable",V023_BLACKOUT_START,V023_BLACKOUT_END)
    out["blackout_other_takeover"]=mean("other_takeover","revisable",V023_BLACKOUT_START,V023_BLACKOUT_END)
    # late revision: allow full 8-probe window to replace pre-switch evidence
    late_start=V023_BLACKOUT_END+V016_WINDOW
    out["revised_self_remap"]=mean("self_remap","revisable",late_start,V023_REVISION_END)
    out["revised_other_takeover"]=mean("other_takeover","revisable",late_start,V023_REVISION_END)
    out["revised_separation"]=out["revised_self_remap"]-out["revised_other_takeover"]
    out["rigid_other_takeover"]=mean("other_takeover","rigid",late_start,V023_REVISION_END)
    out["reacquired_other_takeover"]=mean("other_takeover","revisable",V023_REVISION_END+V016_WINDOW,V023_TOTAL_STEPS)
    out["remap_after_restore"]=mean("self_remap","revisable",V023_REVISION_END+V016_WINDOW,V023_TOTAL_STEPS)
    out["blackout_probe_norm"]=float(np.mean([r['probe_norm'] for r in rows if r['blackout']]))
    out["aligned_mean_probability"]=float(clf_metrics['aligned_mean_probability'])
    out["shuffled_mean_probability"]=float(clf_metrics['shuffled_mean_probability'])
    out["selfcal_ownership_r2"]=float(readout_metrics['selfcal_ownership_r2'])
    out["integrity"]=bool(all(not r["identity_truth_used"] and (not r["blackout"] or r["probe_norm"]==0.0) for r in rows))
    return out,rows

def exploratory_seed(seed:int, episodes:int=8):
    return _seed_result(int(seed), int(episodes))

def run_revisable_self_trace_seed(seed:int)->dict[str,Any]:
    seed=int(seed)
    if seed not in V023_DEVELOPMENT_SEEDS:
        raise ValueError("seed is not part of frozen v0.23 set")
    summary, rows = _seed_result(seed, V023_EVALUATION_EPISODES)
    return {"seed":seed,"seed_summary":summary,"rows":rows}

def _boot(values:Sequence[float], salt:int)->tuple[float,float]:
    x=np.asarray(values,float); rng=np.random.default_rng(V023_BOOTSTRAP_SEED+int(salt)); draws=np.empty(V023_BOOTSTRAP_RESAMPLES)
    for i in range(len(draws)):
        draws[i]=float(np.mean(x[rng.integers(0,len(x),size=len(x))]))
    return float(np.quantile(draws,.025)),float(np.quantile(draws,.975))

def aggregate_revisable_self_trace_results(parts:Sequence[Mapping[str,Any]], output:str|Path)->dict[str,Any]:
    by={int(p["seed"]):p for p in parts}
    if tuple(sorted(by))!=tuple(sorted(V023_DEVELOPMENT_SEEDS)):
        raise ValueError("parts must contain exactly frozen v0.23 seeds")
    d=Path(output); d.mkdir(parents=True,exist_ok=True)
    if any(d.iterdir()): raise FileExistsError("output directory must be empty")
    seeds=[by[s]["seed_summary"] for s in V023_DEVELOPMENT_SEEDS]
    rows=[r for s in V023_DEVELOPMENT_SEEDS for r in by[s]["rows"]]
    numeric=[k for k,v in seeds[0].items() if k not in {"seed","integrity"} and isinstance(v,(int,float,np.floating))]
    values={k:[float(r[k]) for r in seeds] for k in numeric}; means={k:float(np.mean(v)) for k,v in values.items()}; cis={k:_boot(v,i) for i,(k,v) in enumerate(values.items())}
    revision_adv=[float(r["rigid_other_takeover"]-r["revised_other_takeover"]) for r in seeds]
    means["revision_advantage_over_rigid"]=float(np.mean(revision_adv)); cis["revision_advantage_over_rigid"]=_boot(revision_adv,99)
    gates={
      "blackout_self_persists":cis["blackout_self_remap"][0]>.65,
      "blackout_takeover_prior_persists":cis["blackout_other_takeover"][0]>.65,
      "remap_preserves_identity":cis["revised_self_remap"][0]>.80,
      "takeover_revokes_identity":cis["revised_other_takeover"][1]<.30,
      "post_evidence_separation":cis["revised_separation"][0]>.55,
      "rigid_trace_false_self":cis["rigid_other_takeover"][0]>.55,
      "revision_beats_rigid":cis["revision_advantage_over_rigid"][0]>.40,
      "self_reacquired_after_restore":cis["reacquired_other_takeover"][0]>.60,
      "remap_restoration_high":cis["remap_after_restore"][0]>.85,
      "blackout_has_no_private_probes":cis["blackout_probe_norm"][1]<1e-12,
      "classifier_replicates":cis["aligned_mean_probability"][0]>.85 and cis["shuffled_mean_probability"][1]<.15,
      "workspace_readout_replicates":cis["selfcal_ownership_r2"][0]>.85,
      "integrity":all(bool(r["integrity"]) for r in seeds),
    }
    result={"schema":"rrct.v023.revisable_self_trace.v1","seeds":list(V023_DEVELOPMENT_SEEDS),"means":means,"bootstrap_95":{k:list(v) for k,v in cis.items()},"gates":gates,"all_primary_gates_pass":bool(all(gates.values())),"interpretation_limit":"Functional evidence about persistence and causal revision of a temporal self-model. Not evidence of phenomenal consciousness or subjective experience."}
    with (d/"revisable_self_trace_seed_summaries.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(seeds[0].keys()));w.writeheader();w.writerows(seeds)
    with (d/"revisable_self_trace_rows.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    (d/"revisable_self_trace_summary.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    hashes={}
    for q in sorted(d.iterdir()):
        if q.is_file(): hashes[q.name]=hashlib.sha256(q.read_bytes()).hexdigest()
    (d/"artifact_sha256.json").write_text(json.dumps(hashes,indent=2,sort_keys=True)+"\n")
    return result
