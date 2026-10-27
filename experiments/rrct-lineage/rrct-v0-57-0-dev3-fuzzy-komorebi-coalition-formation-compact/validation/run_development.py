from __future__ import annotations
import pathlib, statistics, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import fuzzy_komorebi as fk

seeds=(57101,57103,57107,57109)
config=fk.TrainConfig(steps=2000,batch_size=512,hidden=128,noise_std=0.03,learning_rate=0.003,membership_cost=0.001)
rows=[]
for seed in seeds:
    seed_row={'seed':seed,'models':{}}
    for kind in ('fuzzy','hard','direct'):
        started=time.time()
        model,curve=fk.train_model(kind,seed,config=config)
        result=fk.evaluate_model(model,fk.deterministic_seed(f'v057-dev2-eval:{seed}'),cases=16000)
        fk.save_model(ROOT/f'models/development/{kind}_{seed}.pt',model,kind=kind,seed=seed,curve=curve)
        fk.write_json(ROOT/f'results/development/{kind}_{seed}.json',{'schema':'rrct.v057.development_model.v2','kind':kind,'seed':seed,'config':config.__dict__,'curve':curve,'result':result})
        seed_row['models'][kind]={'curve':curve,'result':result,'seconds':time.time()-started}
        print(seed,kind,f"mse={result['mse']:.6g}",f"acc={result['strict_accuracy']:.4f}",f"novel={result['novel_blend_mse']:.6g}",flush=True)
    rows.append(seed_row)
summary={}
for kind in ('fuzzy','hard','direct'):
    rs=[row['models'][kind]['result'] for row in rows]
    summary[kind]={key:statistics.mean(float(r[key]) for r in rs) for key in ('mse','strict_accuracy','crisp_mse','familiar_blend_mse','diffuse_mse','novel_blend_mse')}
    if kind=='fuzzy':
        summary[kind].update({
            'membership_mse':statistics.mean(float(r['membership_mse']) for r in rs),
            'coupling_mse':statistics.mean(float(r['coupling_mse']) for r in rs),
            'idempotence_target_correlation':statistics.mean(float(r['idempotence_target_correlation']) for r in rs),
            'membership_effect_correlation':statistics.mean(float(r['causal_membership']['membership_effect_correlation']) for r in rs),
            'top_to_bottom_effect_ratio':statistics.mean(float(r['causal_membership']['top_to_bottom_effect_ratio']) for r in rs),
        })
fk.write_json(ROOT/'results/DEVELOPMENT.json',{'schema':'rrct.v057.development.v2','seeds':seeds,'config':config.__dict__,'summary':summary,'rows':rows})
print('SUMMARY',summary,flush=True)
