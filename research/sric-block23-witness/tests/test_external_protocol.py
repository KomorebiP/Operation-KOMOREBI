import numpy as np
from block23.external.fake_runtime import FakeLatentAdapter
from block23.external.interventions import norm_matched_noise,permute_trace,truncate_trace,zero_trace
from block23.external.preflight import run_preflight
from block23.external.protocol import PilotTask

def task():return PilotTask('t','A synthetic logical question','True',('s1','s2'),'f',{'proof_depth':2})

def test_fake_adapter_exact_replay_and_interventions(tmp_path):
 a=FakeLatentAdapter();t=task();x,y=a.replay(t);assert x.answer_loss==y.answer_loss;assert np.array_equal(x.trace,y.trace)
 assert zero_trace(x.trace).shape==x.trace.shape
 assert truncate_trace(x.trace,2).shape==x.trace.shape
 assert permute_trace(x.trace,list(reversed(range(len(x.trace))))).shape==x.trace.shape
 n=norm_matched_noise(x.trace,3);assert np.allclose(np.linalg.norm(n,axis=1),np.linalg.norm(x.trace,axis=1))

def test_preflight_does_not_claim_real_execution(tmp_path):
 lock=tmp_path/'lock.json';lock.write_text('{"files":{}}')
 r=run_preflight(None,None,lock);assert not r['real_checkpoint_executed'];assert r['status']=='ADAPTER_VALIDATED_REAL_EXECUTION_BLOCKED';assert 'checkpoint_missing' in r['blockers']
