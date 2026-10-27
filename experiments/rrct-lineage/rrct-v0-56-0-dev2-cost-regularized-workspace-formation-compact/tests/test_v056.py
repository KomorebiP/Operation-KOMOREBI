from __future__ import annotations
import pathlib, sys
import torch
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import workspace_formation as wf

def test_route_capabilities() -> None:
    batch=wf.sample_batch(30000,torch.Generator().manual_seed(91),0.0)
    losses=wf.route_losses(batch['routes'],batch['target'])
    for task in range(6):
        mask=batch['task_ids']==task
        assert float(losses[mask,task].mean())<1e-5
        assert float(losses[mask,5].mean())<1e-5
    assert float(losses[batch['task_ids']==5,:5].mean())>0.90

def test_primary_selector() -> None:
    result=wf.evaluate_seed(560991,evaluation_cases=10000)
    assert result.task_accuracy>=0.999
    assert result.route_accuracy>=0.999
    assert abs(result.excess_cost)<=1e-8

def test_cost_edge_controls() -> None:
    batch=wf.sample_batch(12000,torch.Generator().manual_seed(2041),0.08)
    no_cost=wf.evaluate(wf.train_counterfactual(561001,lambda_cost=0.0),batch)
    assert no_cost.task_accuracy>=0.999 and no_cost.excess_cost>=0.70
    high=wf.evaluate(wf.train_counterfactual(561002,lambda_cost=0.30),batch)
    assert high.task_accuracy<=0.90

def test_cue_and_dynamic_controls() -> None:
    result=wf.evaluate_seed(561003,evaluation_cases=10000)
    assert result.shuffled_cue_route_accuracy<=0.30
    assert result.shuffled_cue_task_accuracy<=0.55
    assert result.dissolution_accuracy>=0.999
    assert result.graph_switch_accuracy>=0.999
    assert result.route_patch_change_rate>=0.70
