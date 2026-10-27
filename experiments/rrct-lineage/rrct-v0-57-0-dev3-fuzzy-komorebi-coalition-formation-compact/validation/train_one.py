from __future__ import annotations
import argparse,pathlib,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import fuzzy_komorebi as fk
p=argparse.ArgumentParser();p.add_argument('kind',choices=('fuzzy','hard','direct'));p.add_argument('seed',type=int);a=p.parse_args()
config=fk.TrainConfig(steps=2000,batch_size=512,hidden=128,noise_std=.03,learning_rate=.003,membership_cost=.001)
t=time.time();m,c=fk.train_model(a.kind,a.seed,config=config);r=fk.evaluate_model(m,fk.deterministic_seed(f'v057-dev2-eval:{a.seed}'),cases=16000)
fk.save_model(ROOT/f'models/development/{a.kind}_{a.seed}.pt',m,kind=a.kind,seed=a.seed,curve=c)
fk.write_json(ROOT/f'results/development/{a.kind}_{a.seed}.json',{'schema':'rrct.v057.development_model.v2','kind':a.kind,'seed':a.seed,'config':config.__dict__,'curve':c,'result':r})
print(a.seed,a.kind,f"mse={r['mse']:.6g}",f"acc={r['strict_accuracy']:.4f}",f"novel={r['novel_blend_mse']:.6g}",f"seconds={time.time()-t:.1f}",flush=True)
