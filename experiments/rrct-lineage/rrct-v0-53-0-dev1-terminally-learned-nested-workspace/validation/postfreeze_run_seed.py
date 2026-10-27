from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
import torch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import nested_workspace_experiment as e

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def simple(m,seed):
 b=e.make_batch(e.EvaluationConfig().holdout_cases,torch.Generator().manual_seed(seed^0x1D1D))
 with torch.no_grad():o=m(b['leaf_phase'],b['private'])
 return {'action_cosine':e.mean_phase_cosine(o['action_phase'],b['action_phase']),'action_accuracy':e.strict_phase_accuracy(o['action_phase'],b['action_phase']),'private_accuracy':float((o['private_logits'].argmax(-1)==b['private']).float().mean().item()),'parameter_count':m.parameter_count()}
def main():
 p=argparse.ArgumentParser();p.add_argument('seed',type=int);seed=p.parse_args().seed
 frozen=json.loads((ROOT/'HOLDOUT_SEEDS.json').read_text())['holdout_seeds'];assert seed in frozen
 (ROOT/'models').mkdir(exist_ok=True);(ROOT/'results/partial').mkdir(parents=True,exist_ok=True)
 full=e.train_nested_model(seed,2,2);fr=e.evaluate_nested_model(full,seed);fp=ROOT/f'models/nested_seed_{seed}.pt';fsha=e.save_model(full,fp,{'seed':seed,'model':'nested','local_dim':2,'global_dim':2,'train_config':e.TrainConfig().__dict__})
 cap=e.train_nested_model(seed^0x111,1,1);cr=simple(cap,seed^0x111);cp=ROOT/f'models/capacity1_seed_{seed}.pt';csha=e.save_model(cap,cp,{'seed':seed^0x111,'model':'capacity_one','local_dim':1,'global_dim':1,'train_config':e.TrainConfig().__dict__})
 flat=e.train_flat_model(seed);flr=e.evaluate_flat_model(flat,seed);flp=ROOT/f'models/flat_seed_{seed}.pt';torch.save({'version':e.VERSION,'metadata':{'seed':seed,'model':'flat','train_config':e.TrainConfig().__dict__},'state_dict':flat.state_dict()},flp)
 mm={fp.name:{'sha256':fsha,'size_bytes':fp.stat().st_size},cp.name:{'sha256':csha,'size_bytes':cp.stat().st_size},flp.name:{'sha256':sha(flp),'size_bytes':flp.stat().st_size}}
 r={'seed':seed,'full':fr,'capacity_one':cr,'flat':flr,'model_manifest':mm};r['digest']=e.canonical_digest(r);path=ROOT/f'results/partial/seed_{seed}.json';path.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'seed':seed,'intact':fr['modes']['intact']['action_accuracy'],'capacity_one':cr['action_accuracy'],'flat':flr['action_accuracy'],'local_probe':min(fr['probes']['local_a_to_u']['strict_accuracy'],fr['probes']['local_b_to_v']['strict_accuracy']),'global_probe':fr['probes']['global_to_y']['strict_accuracy']},sort_keys=True))
if __name__=='__main__': main()
