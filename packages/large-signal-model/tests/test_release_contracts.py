from dataclasses import replace
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from komorebi_pr_lasm import (
    MultiAtlasAnalyzer, MultiAtlasConfig, UltimateLASMPacketizer,
    LASMPacketizerConfig, PacketTree, best_basis, l1_packet_cost,
    color_one_hot, fourier_project, haar2d_forward, haar2d_inverse,
    polyphase2d_analyze, polyphase2d_synthesize, polyphase_project,
    reconstruct_color, LASMProgram, ProjectorResolvedLargeSignalModel,
)
from komorebi_arc3_offline.bayes import BayesianRegression, normalized_probabilities
from komorebi_arc3_offline.lasm_graph import StateTransitionGraph
from komorebi_arc3_offline.lasm_synthetic import generate_program_identification_scenario
from komorebi_arc3_offline.types import ActionCandidate


@pytest.mark.parametrize('shape', [(1,1),(1,7),(7,1),(3,5),(6,10),(8,12),(17,31),(64,64)])
@pytest.mark.parametrize('categorical', [False, True])
def test_exact_atlases_accept_irregular_and_small_shapes(shape, categorical):
    rng = np.random.default_rng(42)
    x = rng.integers(0,16,size=shape) if categorical else rng.normal(size=shape)
    analyzer = MultiAtlasAnalyzer()
    analysis = analyzer.analyze(x)
    assert analysis.shape == shape
    assert max(analysis.reconstruction_residuals().values()) < 2e-12
    assert np.max(np.abs(analysis.tight_frame_synthesis() - x)) < 2e-12
    assert (analysis.color is not None) == categorical
    assert np.isfinite(analyzer.feature_vector(analysis)).all()


@pytest.mark.parametrize('bad', [np.empty((0,2)), np.array([[np.nan]]),np.array([[np.inf]]),
                                    np.array([[1j]]), np.array([['1']]), np.array([[2**54]],dtype=np.int64)])
def test_real_image_contract_rejects_unsupported_data(bad):
    with pytest.raises(ValueError):
        MultiAtlasAnalyzer().analyze(bad)


def test_continuous_data_never_gets_a_lossy_color_atlas():
    analysis = MultiAtlasAnalyzer().analyze(np.full((8,8), 0.25))
    assert analysis.color is None
    assert 'color' not in analysis.available_atlases
    with pytest.raises(ValueError, match='unavailable'):
        analysis.reconstruct('color')
    with pytest.raises(ValueError, match='clipping'):
        color_one_hot(np.full((2,2), 16), 16)
    with pytest.raises(ValueError):
        reconstruct_color(np.full((2,2,2), 0.5))


def test_original_frame_archive_is_not_the_resized_feature_proxy():
    original = np.arange(63).reshape(7,9) % 16
    packets = UltimateLASMPacketizer().resolve(original)
    assert packets.analysis.shape == original.shape
    assert np.array_equal(packets.analysis.reconstruct('spatial'), original)
    assert packets.macro.shape == (48,)
    assert np.isfinite(packets.raw).all()


def test_archive_owns_readonly_coordinate_copies():
    x = np.ones((8,8))
    analysis = MultiAtlasAnalyzer().analyze(x)
    x[:] = 9
    assert np.all(analysis.spatial == 1)
    with pytest.raises(ValueError):
        analysis.spatial[0,0] = 4
    with pytest.raises(TypeError):
        analysis.polyphase2[(0,0)] = np.zeros((4,4))


@pytest.mark.parametrize('bad', [0,-1,1.5,True,np.nan])
def test_polyphase_modulus_is_positive_integer(bad):
    with pytest.raises(ValueError):
        polyphase2d_analyze(np.zeros((2,2)),bad)
    with pytest.raises(ValueError):
        polyphase2d_synthesize({},(2,2),bad)


@pytest.mark.parametrize('phase', [(-1,0),(4,0),(0,4),(0.5,1)])
def test_polyphase_project_rejects_nonresidue_indices(phase):
    with pytest.raises(ValueError):
        polyphase_project(np.ones((4,4)),4,phase)


def test_fourier_projector_rejects_asymmetric_and_nonbinary_masks():
    x=np.arange(16.).reshape(4,4)
    mask=np.zeros_like(x); mask[0,1]=1
    with pytest.raises(ValueError,match='symmetric'):
        fourier_project(x,mask)
    with pytest.raises(ValueError,match='binary'):
        fourier_project(x,np.full_like(x,0.5))
    mask[0,3]=1
    projected=fourier_project(x,mask)
    assert np.allclose(fourier_project(projected,mask),projected,atol=1e-13)


@pytest.mark.parametrize('levels', [-1,1.5,True,1000])
def test_haar_depth_rejects_invalid_values_without_allocating(levels):
    with pytest.raises(ValueError):
        haar2d_forward(np.ones((8,8)),levels)


def test_maximal_common_dyadic_depth_without_padding():
    x=np.arange(60.).reshape(6,10)
    assert np.allclose(haar2d_inverse(haar2d_forward(x)),x,atol=1e-12)
    with pytest.raises(ValueError):
        haar2d_forward(x,2)


@pytest.mark.parametrize('value', [np.nan,np.inf,-1.0])
def test_tight_weights_are_finite_nonnegative(value):
    a=MultiAtlasAnalyzer().analyze(np.zeros((4,4)))
    w={n:1.0 for n in a.available_atlases if n!='color'};w['spatial']=value
    with pytest.raises(ValueError):
        a.tight_frame_synthesis(w)


def test_extreme_uniform_tight_weights_do_not_overflow_or_underflow():
    a=MultiAtlasAnalyzer().analyze(np.arange(16.).reshape(4,4))
    for value in [1e-300,1e300]:
        w={n:value for n in ('spatial','fourier','haar','polyphase2','polyphase4')}
        assert np.allclose(a.tight_frame_synthesis(w),a.spatial,atol=1e-12)


@pytest.mark.parametrize('pruning', [{'':np.ones(2)}, {'0':np.ones(4)}, ('','0'), ('0','0','1'), ('bad',)])
def test_pruning_must_be_complete_correctly_shaped_and_nonoverlapping(pruning):
    tree=PacketTree.analyze(np.arange(8.),3)
    with pytest.raises(ValueError):
        tree.synthesize(pruning)


def _prunings(path, depth):
    out=[(path,)]
    if depth:
        out += [l+r for l in _prunings(path+'0',depth-1) for r in _prunings(path+'1',depth-1)]
    return out


def test_best_basis_matches_exhaustive_complete_antichains():
    tree=PacketTree.analyze(np.random.default_rng(12).normal(size=16),4)
    selected=best_basis(tree,cost=l1_packet_cost,packet_penalty=0.13)
    prunings=_prunings('',4)
    assert len(prunings)==677
    costs=[sum(l1_packet_cost(tree.coefficients[p],0.13) for p in paths) for paths in prunings]
    assert selected.total_cost == pytest.approx(min(costs),rel=1e-13)
    for paths in prunings:
        assert np.max(np.abs(tree.synthesize(paths)-tree.coefficients['']))<1e-12


def test_nonfinite_cost_is_rejected():
    with pytest.raises(ValueError,match='cost'):
        best_basis(PacketTree.analyze(np.arange(8.),3),cost=lambda a,b:np.nan)


@pytest.mark.parametrize('weights', [np.array([np.nan,0]),np.array([-np.inf,-np.inf]),np.array([[0,1]])])
def test_undefined_probabilities_raise(weights):
    with pytest.raises(ValueError):
        normalized_probabilities(weights)


def test_logprob_normalization_extreme_and_infinite_weights():
    assert np.array_equal(normalized_probabilities(np.array([0.,-np.inf])),[1.,0.])
    assert np.array_equal(normalized_probabilities(np.array([np.inf,0.,np.inf])),[.5,0.,.5])
    p=normalized_probabilities(np.array([-1e6,-1e6-1]))
    assert p.sum()==pytest.approx(1.) and np.isfinite(p).all()


@pytest.mark.parametrize('kwargs', [{'prior_precision':0},{'shape':1},{'scale':0},{'scale':np.nan}])
def test_invalid_regression_prior_rejected(kwargs):
    with pytest.raises(ValueError):
        BayesianRegression(**kwargs)


def test_regression_rejects_nonfinite_and_malformed_data():
    model=BayesianRegression()
    for x,y in [(np.empty((0,2)),np.empty((0,1))),
                (np.ones((4,2)),np.ones((3,1))),
                (np.ones((4,2)),np.full((4,1),np.inf))]:
        with pytest.raises(ValueError): model.fit(x,y)
    fit=model.fit(np.ones((4,2)),np.ones((4,1)))
    with pytest.raises(ValueError): fit.predict(np.ones(3))
    with pytest.raises(ValueError): fit.predictive_log_likelihood(np.ones((4,2)),np.ones((4,2)))


def test_posterior_scale_uses_stable_residual_identity():
    rng=np.random.default_rng(5); x=rng.normal(size=(60,4)); y=x@rng.normal(size=(4,3))*1e7
    reg=BayesianRegression(prior_precision=.01)
    fitted=reg.fit(x,y)
    residual=y-x@fitted.coefficient_mean.T
    expected=reg.scale+.5*(np.sum(residual**2,axis=0)+reg.prior_precision*np.sum(fitted.coefficient_mean**2,axis=1))
    assert np.allclose(fitted.posterior_scale,expected,rtol=1e-12)
    assert np.isfinite(fitted.log_evidence)


def test_nondeterministic_edges_never_form_replay_recommendations():
    g=StateTransitionGraph();a=ActionCandidate(1)
    for target in ['b','c']:
        g.record('a',a,target,reward=1,level_delta=1,terminal_win=True,terminal_loss=False)
    assert g.known_outcome('a',a) is None
    assert g.progressing_action('a') is None
    assert g.winning_action('a') is None
    assert g.shortest_path('a',{'b','c'}) is None
    assert ('a',a.identity()) not in g.incoming['b']


def test_mixed_win_loss_not_a_guaranteed_winning_action():
    g=StateTransitionGraph();a=ActionCandidate(1)
    g.record('a',a,'b',reward=1,level_delta=1,terminal_win=True,terminal_loss=False)
    g.record('a',a,'b',reward=-1,level_delta=0,terminal_win=False,terminal_loss=True)
    assert g.winning_action('a') is None


def _records():
    return generate_program_identification_scenario('linear-fourier',steps=35,seed=4).transitions


def test_fit_compares_the_same_outputs_and_refits_all_records():
    records=_records();p=LASMProgram('small','linear','macro','fourier',state_rank=8)
    q=replace(p,name='large',state_rank=12)
    model=ProjectorResolvedLargeSignalModel(programs=(p,q),minimum_records=10)
    fitted=model.fit(records)
    assert len(fitted)==2
    assert model.fit_report['scored_output_count']==13
    assert model.fit_report['status']=='fit'
    assert all(f.regression.posterior_shape==model.regression.shape+.5*len(records) for f in fitted)
    for f in fitted:
        assert np.isfinite(f.predictive_score)


def test_fitting_failures_are_visible_not_silently_dropped():
    records=list(_records());bad=replace(records[0],action_features=np.full(20,np.nan));records[0]=bad
    p=LASMProgram('bad-design','linear','macro','fourier',state_rank=12)
    model=ProjectorResolvedLargeSignalModel(programs=(p,))
    assert model.fit(records)==()
    report=model.posterior_summary()['fit_report']
    assert report['status']=='all_candidates_failed'
    assert 'bad-design' in report['failed_candidates']


def test_duplicate_program_names_and_typo_families_rejected():
    p=LASMProgram('same','linear','macro','fourier')
    with pytest.raises(ValueError): ProjectorResolvedLargeSignalModel(programs=(p,p))
    with pytest.raises(ValueError): replace(p,family='liner')


def test_cli_self_check_and_user_input_error(tmp_path):
    command=[sys.executable,'-m','komorebi_pr_lasm']
    env={**os.environ, 'PYTHONPATH': os.pathsep.join(str(p) for p in sys.path if p)}
    p=subprocess.run(command+['self-check'],capture_output=True,text=True,env=env)
    assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)['status']=='PASS'
    path=tmp_path/'values.npy';np.save(path,np.arange(7.))
    p=subprocess.run(command+['analyze',str(path)],capture_output=True,text=True,env=env)
    assert p.returncode==0,p.stderr
    assert json.loads(p.stdout)['shape']==[7]
    np.save(path,np.array([np.nan]))
    p=subprocess.run(command+['analyze',str(path)],capture_output=True,text=True,env=env)
    assert p.returncode==2
    assert json.loads(p.stdout)['status']=='ERROR'


def test_benchmark_split_uses_exact_integer_row_counts(tmp_path):
    from komorebi_arc3_offline.lasm_benchmark import run_operator_benchmark
    rows = run_operator_benchmark(tmp_path, steps=84, seed=11)
    assert len(rows) == 7
    assert all(row["train_rows"] == 84 and row["test_rows"] == 36 for row in rows)
