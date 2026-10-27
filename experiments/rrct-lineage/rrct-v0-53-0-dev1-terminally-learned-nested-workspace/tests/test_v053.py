import pathlib,sys,torch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import nested_workspace_experiment as e

def test_shares():
 b=e.make_batch(4096,torch.Generator().manual_seed(53001));u=torch.remainder(b['values'][:,0]+b['values'][:,1],1);v=torch.remainder(b['values'][:,2]+b['values'][:,3],1);assert torch.allclose(u,b['u'],atol=1e-6);assert torch.allclose(v,b['v'],atol=1e-6);assert torch.allclose(torch.remainder(u+v,1),b['y'],atol=1e-6)
def test_terminal_latents_and_patches():
 m=e.train_nested_model(53011);r=e.evaluate_nested_model(m,53011,e.EvaluationConfig(2048,4096,2048));assert r['modes']['intact']['action_accuracy']>=.99;assert min(x['strict_accuracy'] for x in r['probes'].values())>=.99;assert min(x['strict_accuracy'] for x in r['patches'].values())>=.99;assert not r['uses_intermediate_workspace_labels_for_training']
def test_cuts():
 m=e.train_nested_model(53012);r=e.evaluate_nested_model(m,53012,e.EvaluationConfig(1024,2048,1024));
 for n in ('local_a_cut','local_b_cut','global_cut','topdown_cut'): assert r['modes'][n]['action_accuracy']<=.15 and r['modes'][n]['private_accuracy']==1.0
