import sys
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import access_repair as ar
import evaluate_access as ea

def test_parent_copied_and_legacy_equal():
    torch.set_num_threads(1);m=ar.load(ROOT/'inputs'/'v05_A_random.pt')
    x,a=ea.evaluate(m,'swap_conjugation',4,19313,n=16)
    y,b=ea.evaluate(m,'swap_conjugation',4,19313,n=16,legacy=True)
    assert x['metrics']==y['metrics']
    for k in a:assert np.array_equal(a[k],b[k])

def test_memory_scatter_and_score():
    torch.set_num_threads(1);m=ar.load(ROOT/'inputs'/'v05_B_random.pt')
    _,a=ea.evaluate(m,'random_nonidentity',3,19317,n=24)
    for n in range(24):
        for j in range(4):
            for agent in range(2):
                code=int(a['recalled_pair'][n,j,agent]);i,k=a['pairs'][n,j]
                assert a['memory_bits'][n,agent,i]==code%2
                assert a['memory_bits'][n,agent,k]==code//2
    assert ea.metrics(a)['exact_work']==np.mean(a['pred'][:,0,:]==a['target'][:,0,None])

def test_heldout_length_and_family_marking():
    torch.set_num_threads(1);m=ar.load(ROOT/'inputs'/'v05_A_random.pt')
    r,a=ea.evaluate(m,'commuting_flips',48,32,n=8)
    assert r['untrained_length'] and r['named_generator_excluded_from_training']
    assert np.all(a['arguments'][:,0]==0) and np.all(a['arguments'][:,1]==0)
