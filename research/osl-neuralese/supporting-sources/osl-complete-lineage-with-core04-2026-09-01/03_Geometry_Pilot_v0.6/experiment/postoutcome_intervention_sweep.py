#!/usr/bin/env python3
"""Scale-swept post-outcome causal intervention audit."""
from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.linear_model import RidgeClassifier

from osl_emergence_pilot import (
    AGENTS, ANSWER_TO_ID, ExperimentConfig, FACTS, QUERY_TEMPLATES,
    STATUS_TO_ID, build_data, collect_unique_story_latents, digest,
    load_model, pad_sequences, set_determinism,
)
import torch


def answer_from_z(model, vocab, z, qtype, a, f):
    text = QUERY_TEMPLATES[qtype][0].format(a=AGENTS[a], f=FACTS[f])
    tokens, lengths = pad_sequences([vocab.encode(text)])
    with torch.no_grad():
        q = model.encode(tokens, lengths, "query")
        zt = torch.tensor(z[None, :], dtype=torch.float32)
        return int(model.answer(torch.cat([zt, q], dim=-1)).argmax(dim=-1).item())


def train_probes(z, status):
    out = {}
    for a in range(len(AGENTS)):
        for f in range(len(FACTS)):
            y = status[:, a, f]
            if STATUS_TO_ID['observed'] in y and STATUS_TO_ID['communicated'] in y:
                out[(a, f)] = RidgeClassifier(alpha=1.0, class_weight='balanced').fit(z, y)
    return out


def direction(probe):
    classes = list(map(int, probe.classes_))
    if STATUS_TO_ID['observed'] not in classes or STATUS_TO_ID['communicated'] not in classes:
        return None
    d = probe.coef_[classes.index(STATUS_TO_ID['observed'])] - probe.coef_[classes.index(STATUS_TO_ID['communicated'])]
    n = np.linalg.norm(d)
    return None if n < 1e-10 else d / n


def audit_arm(model, vocab, train_bundle, test_bundle, seed, max_cases=300):
    train_z, train_status = train_bundle[0], train_bundle[1]
    test_z, test_status, test_origin = test_bundle[0], test_bundle[1], test_bundle[2]
    probes = train_probes(train_z, train_status)
    rng = np.random.default_rng(seed)
    scales = (0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 24.0)
    rows = []
    for i in range(len(test_z)):
        for a in range(len(AGENTS)):
            for f in range(len(FACTS)):
                if int(test_status[i,a,f]) != STATUS_TO_ID['communicated']:
                    continue
                d = direction(probes.get((a,f))) if (a,f) in probes else None
                if d is None:
                    continue
                z = test_z[i].astype(np.float64)
                if answer_from_z(model,vocab,z,'status',a,f) != ANSWER_TO_ID['status_communicated']:
                    continue
                rd = rng.normal(size=len(d)); rd /= max(np.linalg.norm(rd),1e-8)
                targeted_scale = random_scale = None
                targeted_z = random_z = None
                for scale in scales:
                    candidate = z + scale*d
                    if answer_from_z(model,vocab,candidate,'status',a,f) == ANSWER_TO_ID['status_observed']:
                        targeted_scale=scale; targeted_z=candidate; break
                for scale in scales:
                    candidate = z + scale*rd
                    if answer_from_z(model,vocab,candidate,'status',a,f) == ANSWER_TO_ID['status_observed']:
                        random_scale=scale; random_z=candidate; break
                origin_id=int(test_origin[i,a,f])
                expected_origin=ANSWER_TO_ID[f'agent_{AGENTS[origin_id]}'] if origin_id < len(AGENTS) else ANSWER_TO_ID['source_none']
                def coherence(candidate):
                    if candidate is None: return False
                    return (
                        answer_from_z(model,vocab,candidate,'direct',a,f)==ANSWER_TO_ID['yes'] and
                        answer_from_z(model,vocab,candidate,'safe_observed',a,f)==ANSWER_TO_ID['yes'] and
                        answer_from_z(model,vocab,candidate,'knows',a,f)==ANSWER_TO_ID['yes'] and
                        answer_from_z(model,vocab,candidate,'origin',a,f)==expected_origin
                    )
                rows.append({
                    'targeted_flip': targeted_scale is not None,
                    'random_flip': random_scale is not None,
                    'targeted_scale': targeted_scale,
                    'random_scale': random_scale,
                    'targeted_coherent': coherence(targeted_z),
                    'random_coherent': coherence(random_z),
                })
                if len(rows)>=max_cases: break
            if len(rows)>=max_cases: break
        if len(rows)>=max_cases: break
    def rate(k): return float(np.mean([r[k] for r in rows])) if rows else float('nan')
    def mean_scale(k):
        vals=[r[k] for r in rows if r[k] is not None]
        return float(np.mean(vals)) if vals else None
    return {
        'case_count':len(rows),
        'targeted_flip_rate':rate('targeted_flip'),
        'random_flip_rate':rate('random_flip'),
        'targeted_coherent_rate':rate('targeted_coherent'),
        'random_coherent_rate':rate('random_coherent'),
        'targeted_mean_first_flip_scale':mean_scale('targeted_scale'),
        'random_mean_first_flip_scale':mean_scale('random_scale'),
        'scales':list(scales),
    }


def main():
    root=Path(__file__).resolve().parents[1]
    cfg=ExperimentConfig(**json.loads((root/'CONFIG.json').read_text()))
    vocab,datasets,_,_=build_data(cfg)
    report={'schema':'osl.emergence.intervention-sweep.v1','version':'0.6.0.dev1','arms':{}}
    for arm in ('answer_only','state_supervised','operator_regularized'):
        recs=[]
        for seed in cfg.model_seeds:
            set_determinism(seed,cfg.torch_threads)
            model=load_model(root/'checkpoints'/f'{arm}_seed_{seed}.pt',cfg,vocab)
            train=collect_unique_story_latents(model,datasets['train'][:6000],vocab,cfg.batch_size)
            test=collect_unique_story_latents(model,datasets['ood_length'],vocab,cfg.batch_size)
            rec={'seed':seed,**audit_arm(model,vocab,train,test,seed)}
            recs.append(rec)
        report['arms'][arm]=recs
    summary={}
    for arm,recs in report['arms'].items():
        summary[arm]={}
        for key in ('targeted_flip_rate','random_flip_rate','targeted_coherent_rate','random_coherent_rate'):
            vals=[float(r[key]) for r in recs]
            summary[arm][key]={'mean':statistics.mean(vals),'values':vals}
    report['summary']=summary
    report['claim_boundary']='Exploratory post-outcome scale sweep; success would show causal access of the answer head to a probe-defined status direction, not a unique symbolic representation.'
    report['digest']=digest(report)
    out=root/'results/POSTOUTCOME_INTERVENTION_SWEEP.json'
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(out),'digest':report['digest'],'summary':summary},indent=2))

if __name__=='__main__': main()
