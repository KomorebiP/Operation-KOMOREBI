from __future__ import annotations
import pathlib, sys
import torch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import fuzzy_komorebi as fk


def test_fuzzy_packet_partition_and_reconstruction() -> None:
    batch=fk.sample_batch(512,torch.Generator().manual_seed(17),split='holdout')
    metrics=fk.fuzzy_packet_diagnostics(batch['membership'],seed=23)
    assert metrics['maximum_partition_error']<1e-6
    assert metrics['minimum_packet_eigenvalue']>=-1e-7
    assert metrics['maximum_block_reconstruction_relative_error']<1e-6
    assert metrics['maximum_permutation_transport_error']<1e-6


def test_hard_oracle_is_exact_on_crisp_and_limited_on_fuzzy() -> None:
    batch=fk.sample_batch(12000,torch.Generator().manual_seed(31),split='holdout',noise_std=0.0)
    hard=fk.actions(batch['values'],fk.crispify(batch['membership']))
    error=((hard-batch['target'])**2).mean(-1)
    assert float(error[batch['family']==0].max())<1e-8
    assert float(error[batch['family']==3].mean())>0.01


def test_small_fuzzy_model_beats_hard_membership_on_overlap() -> None:
    config=fk.TrainConfig(steps=400,batch_size=512)
    fuzzy,_=fk.train_model('fuzzy',570091,config=config,checkpoints=())
    hard,_=fk.train_model('hard',570091,config=config,checkpoints=())
    fuzzy_result=fk.evaluate_model(fuzzy,570992,cases=6000)
    hard_result=fk.evaluate_model(hard,570992,cases=6000)
    assert fuzzy_result['novel_blend_mse'] < 0.25*hard_result['novel_blend_mse']
    assert fuzzy_result['private_routine_accuracy']==1.0


def test_fuzzy_packet_defect_separates_crisp_from_overlap() -> None:
    config=fk.TrainConfig(steps=600,batch_size=512)
    model,_=fk.train_model('fuzzy',570123,config=config,checkpoints=())
    result=fk.evaluate_model(model,570321,cases=8000)
    assert result['crisp_idempotence_defect'] < result['novel_blend_idempotence_defect']
    assert result['idempotence_target_correlation'] > 0.60
