from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from torch.nn import functional as F


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.hard_operator import (
    ExactTableOracle,
    HardMetricOperatorRNN,
    HardOperatorRNN,
    LearnedDiagonalMetric,
    canonical_qr_orthogonal,
    cayley_orthogonal,
    hard_operator_health_metrics,
    matrix_exp_orthogonal,
    orthogonalize,
    polar_orthogonal,
)

from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.models import LinearHyperOperatorRNN, build_model, parameter_count
from komorebi_neuralese.train import TrainConfig, intrinsic_isometry_loss, train_arm


def _exact_table_encoder(model: HardOperatorRNN) -> None:
    """Make raw(T) exactly T.T and install the one-hot state solution."""
    dimension = model.hidden_dim
    assert dimension == 8
    with torch.no_grad():
        model.operator_encoder.weight.zero_()
        for row in range(dimension):
            for column in range(dimension):
                output_index = row * dimension + column
                input_index = column * dimension + row
                model.operator_encoder.weight[output_index, input_index] = 1.0
        model.state_embedding.weight.copy_(torch.eye(dimension, dtype=model.state_embedding.weight.dtype))
        model.decoder.weight.copy_(torch.eye(dimension, dtype=model.decoder.weight.dtype))


def test_soft_and_hard_arms_share_exact_parameter_initialization() -> None:
    torch.manual_seed(1701)
    soft = build_model("linear_hyper", operator_init_std=0.08)
    torch.manual_seed(1701)
    hard = build_model(
        "linear_hyper_hard",
        operator_init_std=0.08,
        orthogonal_parameterization="qr",
    )
    soft_parameters = dict(soft.named_parameters())
    hard_parameters = dict(hard.named_parameters())
    assert soft_parameters.keys() == hard_parameters.keys()
    assert all(
        torch.equal(soft_parameters[name], hard_parameters[name])
        for name in soft_parameters
    )


def test_exact_table_oracle_executes_without_trainable_parameters() -> None:
    batch = EpisodeGenerator(1702, coordinate_split="test").sample(64, 129, family="random")
    oracle = ExactTableOracle()
    trace = oracle.run(batch.tables, batch.op_slots, batch.start)
    assert sum(parameter.numel() for parameter in oracle.parameters()) == 0
    assert torch.equal(trace.logits.argmax(dim=1), batch.target)
    initial_norm = trace.hidden[0].norm(dim=1)
    final_norm = trace.hidden[-1].norm(dim=1)
    assert torch.equal(initial_norm, final_norm)


@pytest.mark.parametrize(
    "projection",
    (canonical_qr_orthogonal, matrix_exp_orthogonal, cayley_orthogonal, polar_orthogonal),
)
def test_every_projection_is_numerically_orthogonal(projection) -> None:
    generator = torch.Generator().manual_seed(101)
    raw = torch.randn(19, 8, 8, generator=generator, dtype=torch.float64)
    projected = projection(raw)
    identity = torch.eye(8, dtype=torch.float64)
    defect = projected.transpose(-1, -2) @ projected - identity
    assert float(defect.abs().max()) < 2e-12
    assert torch.allclose(torch.linalg.svdvals(projected), torch.ones(19, 8, dtype=torch.float64), atol=2e-12)


def test_qr_and_polar_cover_both_determinant_components() -> None:
    positive = torch.eye(8, dtype=torch.float64)
    negative = positive.clone()
    negative[0, 0] = -1.0
    raw = torch.stack((positive, negative))
    for projection in (canonical_qr_orthogonal, polar_orthogonal):
        determinants = torch.linalg.det(projection(raw))
        assert torch.allclose(determinants, torch.tensor([1.0, -1.0], dtype=torch.float64), atol=1e-12)

    # The connected skew maps are deliberately SO-only.
    for projection in (matrix_exp_orthogonal, cayley_orthogonal):
        assert torch.all(torch.linalg.det(projection(raw)) > 0.999999999999)


def test_exponential_can_reach_minus_one_eigenvalues_but_cayley_cannot() -> None:
    generator = torch.zeros(2, 2, dtype=torch.float64)
    generator[0, 1] = -torch.pi
    generator[1, 0] = torch.pi
    exponential = matrix_exp_orthogonal(generator)
    cayley = cayley_orthogonal(generator)
    assert torch.allclose(exponential, -torch.eye(2, dtype=torch.float64), atol=2e-14)
    assert not torch.allclose(cayley, -torch.eye(2, dtype=torch.float64), atol=1e-2)


def test_qr_exact_table_solution_is_faithful_for_all_states_and_both_slots() -> None:
    model = HardOperatorRNN(hidden_dim=8, parameterization="qr").double()
    _exact_table_encoder(model)
    starts = torch.arange(8)
    for family_index, family in enumerate(("d4", "c8", "mixed_cycle", "random")):
        episode = EpisodeGenerator(200 + family_index).sample(
            1,
            0,
            family=family,
            coordinate_split="dev",
        )
        tables = episode.tables.expand(8, -1, -1, -1).double()
        maps = episode.maps.expand(8, -1, -1)
        for slot in range(2):
            slots = torch.full((8, 1), slot, dtype=torch.long)
            prediction = model(tables, slots, starts).argmax(dim=1)
            expected = maps[:, slot].gather(1, starts[:, None]).squeeze(1)
            assert torch.equal(prediction, expected), (family, slot)


def test_zero_raw_encoder_cannot_collapse_projected_operator_norm() -> None:
    model = HardOperatorRNN(hidden_dim=8, parameterization="qr").double()
    with torch.no_grad():
        model.operator_encoder.weight.zero_()
    batch = EpisodeGenerator(301).sample(7, 0, coordinate_split="train")
    codes = model.encode_operators(batch.tables.double())
    identity = torch.eye(8, dtype=torch.float64).expand_as(codes)
    assert torch.equal(codes, identity)
    assert torch.equal(torch.linalg.matrix_norm(codes, ord="fro", dim=(-2, -1)), torch.full((7, 2), 8**0.5, dtype=torch.float64))


@pytest.mark.parametrize(
    ("dtype", "depth", "tolerance"),
    ((torch.float32, 2048, 2e-3), (torch.float64, 4096, 2e-9)),
)
def test_deep_recurrence_preserves_intrinsic_norm(dtype, depth: int, tolerance: float) -> None:
    torch.manual_seed(401)
    model = HardMetricOperatorRNN(hidden_dim=8, parameterization="qr").to(dtype=dtype)
    with torch.no_grad():
        model.learned_metric.raw_log_metric.normal_(std=3.0)
    episode = EpisodeGenerator(402).sample(4, depth, family="random", coordinate_split="test")
    codes = model.encode_operators(episode.tables.to(dtype=dtype))
    hidden = model.initial_hidden(episode.start)
    metric = model.metric_matrix()
    initial_norm = torch.einsum("bi,ij,bj->b", hidden, metric, hidden).sqrt()
    rows = torch.arange(hidden.shape[0])
    with torch.no_grad():
        for step in range(depth):
            selected = codes[rows, episode.op_slots[:, step]]
            hidden = model.step_hidden(hidden, selected)
    final_norm = torch.einsum("bi,ij,bj->b", hidden, metric, hidden).sqrt()
    assert float((final_norm / initial_norm - 1.0).abs().max().detach()) < tolerance


def test_learned_diagonal_metric_is_bounded_spd_scale_fixed_and_cheap() -> None:
    metric = LearnedDiagonalMetric(8, log_frobenius_bound=1.5).double()
    with torch.no_grad():
        metric.raw_log_metric.copy_(torch.linspace(-100.0, 100.0, 8, dtype=torch.float64))
    log_matrix = metric.log_matrix()
    matrix = metric.matrix()
    whitener, inverse = metric.factors()
    assert abs(float(log_matrix.trace().detach())) < 1e-12
    assert float(torch.linalg.matrix_norm(log_matrix, ord="fro").detach()) <= 1.5 + 1e-12
    assert float(torch.linalg.eigvalsh(matrix).min().detach()) > 0.0
    sign, logabsdet = torch.linalg.slogdet(matrix)
    assert sign == 1.0
    assert abs(float(logabsdet.detach())) < 1e-12
    assert torch.allclose(whitener.T @ whitener, matrix, atol=1e-12)
    assert torch.allclose(whitener @ inverse, torch.eye(8, dtype=torch.float64), atol=1e-12)
    assert metric.raw_log_metric.numel() == 8


def test_learned_metric_codes_are_exactly_g_isometric_and_gradients_flow() -> None:
    torch.manual_seed(501)
    model = HardMetricOperatorRNN(hidden_dim=8, parameterization="qr").double()
    with torch.no_grad():
        model.learned_metric.raw_log_metric.normal_(std=0.5)
    episode = EpisodeGenerator(502).sample(16, 3, coordinate_split="train")
    trace = model.run(episode.tables.double(), episode.op_slots, episode.start)
    codes = trace.operator_codes
    assert codes is not None
    assert float(intrinsic_isometry_loss(model, codes).detach()) < 1e-28

    loss = F.cross_entropy(trace.logits, episode.target)
    loss.backward()
    for parameter in (model.operator_encoder.weight, model.learned_metric.raw_log_metric):
        assert parameter.grad is not None
        assert torch.isfinite(parameter.grad).all()
        assert float(parameter.grad.norm()) > 1e-10


def test_hard_model_remains_train_api_compatible() -> None:
    model = HardMetricOperatorRNN(hidden_dim=8, parameterization="qr")
    assert isinstance(model, LinearHyperOperatorRNN)
    config = TrainConfig(
        model_name="linear_hyper_hard_metric",
        regime="metric",
        seed=601,
        steps=2,
        batch_size=16,
        train_max_length=2,
        max_eval_length=8,
        learning_rate=8e-4,
        grad_clip=1.0,
        metric_isometry_weight=0.0,
        composition_weight=0.1,
        composition_min_length=2,
        composition_max_length=2,
        device="cpu",
    )
    trained = train_arm(model, config)
    assert np.isfinite(trained.final_loss)
    assert len(trained.trajectory) == 2
    assert parameter_count(trained.model) == parameter_count(model)
    assert trained.sampling_audit["word_product_scope"] == "contiguous"
    assert trained.sampling_audit["word_product_split"] == "train"
    assert trained.sampling_audit["accepted_examples"] == 32
    assert trained.sampling_audit["candidate_examples"] >= 32
    assert trained.sampling_audit["sampling_methods"] == ["direct_conditioned_uniform"]
    assert trained.sampling_audit["conditioned_sampler_backend"] == "cached_exact_v1"
    assert trained.sampling_audit["length_schedule"]["independent_of_episode_sampler"] is True
    assert trained.sampling_audit["conditioning_supports"]
    for support in trained.sampling_audit["conditioning_supports"]:
        assert support["exact_acceptance_numerator"] == support["accepted_pairs"]
        assert support["exact_acceptance_denominator"] == support["candidate_pairs"]
        assert len(support["digest"]) == 64
    assert trained.sampling_audit["split_violations"] == 0
    assert trained.sampling_audit["fail_closed"] is True


def test_state_dict_round_trip_preserves_outputs() -> None:
    torch.manual_seed(701)
    source = HardMetricOperatorRNN(parameterization="qr").double()
    with torch.no_grad():
        source.learned_metric.raw_log_metric.normal_(std=0.4)
    target = HardMetricOperatorRNN(parameterization="qr").double()
    target.load_state_dict(copy.deepcopy(source.state_dict()), strict=True)
    episode = EpisodeGenerator(702).sample(11, 7, coordinate_split="dev")
    with torch.no_grad():
        expected = source(episode.tables.double(), episode.op_slots, episode.start)
        observed = target(episode.tables.double(), episode.op_slots, episode.start)
    assert torch.equal(observed, expected)


def test_health_metrics_expose_rank_margin_components_and_hard_defects() -> None:
    model = HardOperatorRNN(parameterization="qr").double()
    _exact_table_encoder(model)
    identity_map = torch.eye(8, dtype=torch.float64)
    odd_map = identity_map.clone()
    odd_map[[0, 1]] = odd_map[[1, 0]]
    tables = torch.stack((identity_map.T, odd_map.T), dim=0).reshape(1, 2, 8, 8)
    health = hard_operator_health_metrics(model, tables)
    assert health["parameterization"] == "qr"
    assert health["determinant_positive_fraction"] == 0.5
    assert health["determinant_negative_fraction"] == 0.5
    assert health["determinant_near_zero_fraction"] == 0.0
    assert health["raw_minimum_singular_value"]["minimum"] > 0.999999999
    assert health["intrinsic_orthogonality_defect"]["maximum"] < 1e-12
    assert health["metric_isometry_defect"]["maximum"] < 1e-12


def test_invalid_shapes_and_parameterizations_fail_closed() -> None:
    with pytest.raises(ValueError, match="unknown orthogonal parameterization"):
        HardOperatorRNN(parameterization="not-a-map")
    with pytest.raises(ValueError, match="square trailing"):
        orthogonalize(torch.randn(2, 3), "qr")
    model = HardOperatorRNN()
    with pytest.raises(ValueError, match="tables must have shape"):
        model.encode_operators(torch.randn(2, 8, 8))

    invalid_training = TrainConfig(
        model_name="linear_hyper_hard",
        regime="terminal",
        seed=1,
        steps=0,
        batch_size=8,
        train_max_length=2,
        max_eval_length=2,
        learning_rate=1e-3,
    )
    with pytest.raises(ValueError, match="steps and batch_size must be positive"):
        train_arm(HardOperatorRNN(), invalid_training)
