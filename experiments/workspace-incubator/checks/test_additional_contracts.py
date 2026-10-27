import sys
from pathlib import Path
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import access_repair as ar
import distributed_readout_control as dc
from audit_results import recursive_equal

def test_checkpoint_resume_state_exact(tmp_path):
    parent=ROOT/'inputs/v05_A_random.pt'
    ar.train(parent,tmp_path/'full','access',4431,steps=4,batch=8)
    ar.train(parent,tmp_path/'split','access',4431,steps=4,batch=8,stop=2)
    ar.train(parent,tmp_path/'split','access',4431,steps=4,batch=8,resume=True)
    a=torch.load(tmp_path/'full/checkpoint.pt',weights_only=False);b=torch.load(tmp_path/'split/checkpoint.pt',weights_only=False)
    assert recursive_equal(a,b)
    # PyTorch pickle memoization of optimizer string keys differs after loading.
    # Loaded computation state and every tensor payload, not file bytes, are the resume contract.
    import zipfile
    with zipfile.ZipFile(tmp_path/'full/checkpoint.pt') as za, zipfile.ZipFile(tmp_path/'split/checkpoint.pt') as zb:
        for key in za.namelist():
            if '/data/' in key: assert za.read(key)==zb.read(key)

def test_bounded_distributed_codec():
    rng=np.random.default_rng(37);a=rng.normal(size=(32,64));b=rng.normal(size=(32,64));W=rng.normal(size=(128,8));bias=rng.normal(size=8)
    ma=dc.sender(a,W[:64],bias);mb=dc.sender(b,W[64:],bias)
    assert np.all(np.abs(ma)<1) and np.all(np.abs(mb)<1)
    s=np.concatenate((a,b),1)@W+bias
    np.testing.assert_allclose(dc.receiver(a,W[:64],bias,mb),s,atol=1e-11,rtol=0)
    np.testing.assert_allclose(dc.receiver(b,W[64:],bias,ma),s,atol=1e-11,rtol=0)

def test_calibrated_has_original_base():
    for lineage in 'AB':
        parent=torch.load(ROOT/f'inputs/v05_{lineage}_random.pt',weights_only=False)
        child=ar.load(ROOT/f'runs/{lineage}_calibrated/checkpoint.pt')
        assert all(torch.equal(v,child.base.state_dict()[k]) for k,v in parent['model'].items())

def test_primary_and_secondary_bounds_are_distinct():
    import json
    main=json.loads((ROOT/'runs/eval_A_access/result.json').read_text())
    second=json.loads((ROOT/'runs/eval_A_calibrated/result.json').read_text())
    assert main['swap_conjugation_L48_intact_d1']['untrained_length'] is True
    assert second['swap_conjugation_L48_intact_d1']['untrained_length'] is False
    assert second['swap_conjugation_L96_intact_d1']['untrained_length'] is True


def test_full_training_replay_checkpoint_bytes():
    assert (ROOT/'runs/A_access/checkpoint.pt').read_bytes()==(ROOT/'runs/A_access_replay/checkpoint.pt').read_bytes()
