from __future__ import annotations
import argparse,json,pathlib,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import fuzzy_komorebi as fk

p=argparse.ArgumentParser()
p.add_argument('variant',choices=('fuzzy','hard','direct','crystal'))
p.add_argument('seed',type=int)
a=p.parse_args()
kind='fuzzy' if a.variant=='crystal' else a.variant
config=fk.TrainConfig(
    steps=2000,
    batch_size=512,
    hidden=128,
    noise_std=0.03,
    learning_rate=0.003,
    membership_cost=0.001,
    idempotence_cost=0.02 if a.variant=='crystal' else 0.0,
)
started=time.time()
model,curve=fk.train_model(kind,a.seed,config=config)
evaluation_seed=fk.deterministic_seed(f'rrct.v057.dev3.holdout-evaluation:{a.seed}')
result=fk.evaluate_model(model,evaluation_seed,cases=24000)
model_path=ROOT/f'models/holdout/{a.variant}_{a.seed}.pt'
fk.save_model(model_path,model,kind=kind,seed=a.seed,curve=curve)
payload={
    'schema':'rrct.v057.holdout_model.v1',
    'variant':a.variant,
    'kind':kind,
    'seed':a.seed,
    'evaluation_seed':evaluation_seed,
    'config':config.__dict__,
    'curve':curve,
    'result':result,
    'elapsed_seconds':time.time()-started,
}
fk.write_json(ROOT/f'results/holdout/{a.variant}_{a.seed}.json',payload)
print(a.variant,a.seed,f"mse={result['mse']:.6g}",f"novel={result['novel_blend_mse']:.6g}",f"acc={result['strict_accuracy']:.4f}",flush=True)
