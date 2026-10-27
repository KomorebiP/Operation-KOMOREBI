from __future__ import annotations

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

import komorebi_neuralese.train as train_module
from komorebi_neuralese.models import (
    LearnedSPDMetric,
    LinearHyperMetricOperatorRNN,
    LinearHyperOperatorRNN,
    build_model,
)
from komorebi_neuralese.train import (
    TrainConfig,
    anonymous_composition_loss,
    compose_operator_codes,
    compose_visible_maps,
    intrinsic_isometry_loss,
    train_arm,
)


class ExactPermutationEncoder(LinearHyperOperatorRNN):
    """Encode supplied transition tables as exact column-state operators."""

    def __init__(self) -> None:
        super().__init__(hidden_dim=8)
        self.encoded_batches: list[torch.Tensor] = []

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        self.encoded_batches.append(tables.detach().clone())
        return tables.transpose(-1, -2)


def _shift_batch(shifts: tuple[int, ...]) -> tuple[torch.Tensor, torch.Tensor]:
    base = torch.arange(8)
    maps = []
    for shift in shifts:
        maps.append(torch.stack(((base + shift) % 8, base), dim=0))
    integer_maps = torch.stack(maps, dim=0)
    tables = F.one_hot(integer_maps, num_classes=8).float()
    return integer_maps, tables


def test_spd_metric_is_bounded_trace_free_scale_fixed_and_positive() -> None:
    metric = LearnedSPDMetric(5, log_frobenius_bound=1.25).double()
    generator = torch.Generator().manual_seed(3)
    with torch.no_grad():
        metric.raw_log_metric.copy_(100.0 * torch.randn(5, 5, generator=generator, dtype=torch.float64))

    log_metric = metric.log_matrix()
    matrix = metric.matrix()
    whitener, inverse = metric.factors()

    assert torch.allclose(log_metric, log_metric.T, atol=1e-12, rtol=0.0)
    assert abs(float(log_metric.trace().detach())) < 1e-11
    assert float(torch.linalg.matrix_norm(log_metric, ord="fro").detach()) <= 1.25 + 1e-12
    assert torch.linalg.eigvalsh(matrix).min().detach() > 0.0
    sign, logabsdet = torch.linalg.slogdet(matrix)
    assert sign == 1
    assert abs(float(logabsdet.detach())) < 1e-10
    assert torch.allclose(whitener.T @ whitener, matrix, atol=1e-10, rtol=1e-10)
    assert torch.allclose(whitener @ inverse, torch.eye(5, dtype=torch.float64), atol=1e-10, rtol=1e-10)
    assert float(metric.condition_number().detach()) <= np.exp(2.5) + 1e-10


def test_learned_and_fixed_whitening_round_trip_vectors_and_operators() -> None:
    generator = torch.Generator().manual_seed(5)
    learned = LinearHyperMetricOperatorRNN(hidden_dim=4).double()
    with torch.no_grad():
        learned.learned_metric.raw_log_metric.copy_(
            torch.randn(4, 4, generator=generator, dtype=torch.float64)
        )
    hidden = torch.randn(7, 4, generator=generator, dtype=torch.float64)
    operators = torch.randn(7, 3, 4, 4, generator=generator, dtype=torch.float64)
    assert torch.allclose(learned.unwhiten_hidden(learned.whiten_hidden(hidden)), hidden, atol=1e-9, rtol=1e-9)
    assert torch.allclose(
        learned.unwhiten_operators(learned.whiten_operators(operators)),
        operators,
        atol=1e-9,
        rtol=1e-9,
    )

    fixed = LinearHyperOperatorRNN(hidden_dim=4).double()
    assert torch.equal(fixed.whiten_hidden(hidden), hidden)
    assert torch.equal(fixed.whiten_operators(operators), operators)
    assert torch.equal(fixed.metric_matrix(), torch.eye(4, dtype=torch.float64))


def test_intrinsic_isometry_loss_uses_learned_metric_and_has_metric_gradient() -> None:
    generator = torch.Generator().manual_seed(7)
    model = LinearHyperMetricOperatorRNN(hidden_dim=3).double()
    with torch.no_grad():
        model.learned_metric.raw_log_metric.copy_(
            0.4 * torch.randn(3, 3, generator=generator, dtype=torch.float64)
        )
    whitener, inverse = model.metric_factors()
    q, _ = torch.linalg.qr(torch.randn(3, 3, generator=generator, dtype=torch.float64))
    intrinsic_isometry = inverse @ q @ whitener
    exact_loss = intrinsic_isometry_loss(model, intrinsic_isometry.reshape(1, 1, 3, 3))
    distorted_loss = intrinsic_isometry_loss(model, (1.25 * intrinsic_isometry).reshape(1, 1, 3, 3))
    assert float(exact_loss.detach()) < 1e-20
    assert float(distorted_loss.detach()) > 1e-2

    arbitrary_codes = torch.randn(4, 2, 3, 3, generator=generator, dtype=torch.float64)
    loss = intrinsic_isometry_loss(model, arbitrary_codes)
    loss.backward()
    gradient = model.learned_metric.raw_log_metric.grad
    assert gradient is not None
    assert torch.isfinite(gradient).all()
    assert float(gradient.norm()) > 1e-8


def test_composition_uses_reversed_latent_matrix_order() -> None:
    a = torch.tensor([[1.0, 1.0], [0.0, 1.0]])
    b = torch.tensor([[1.0, 0.0], [1.0, 1.0]])
    codes = torch.stack((a, b), dim=0).unsqueeze(0)
    word = torch.tensor([[0, 1]])
    observed = compose_operator_codes(codes, word)
    assert torch.equal(observed[0], b @ a)
    assert not torch.equal(observed[0], a @ b)


def test_visible_map_composition_matches_sequential_execution() -> None:
    rotation = torch.tensor([1, 2, 3, 4, 5, 6, 7, 0])
    reflection = torch.tensor([0, 7, 6, 5, 4, 3, 2, 1])
    maps = torch.stack((rotation, reflection)).unsqueeze(0)
    word = torch.tensor([[0, 1, 0]])
    observed = compose_visible_maps(maps, word)[0]
    expected = rotation[reflection[rotation]]
    assert torch.equal(observed, expected)


def test_composition_targets_are_filtered_before_independent_encoding(monkeypatch: pytest.MonkeyPatch) -> None:
    maps, tables = _shift_batch((1, 2, 3, 4))
    words = {2: torch.tensor([[0, 1], [0, 1], [0, 1], [0, 1]])}
    model = ExactPermutationEncoder()
    primitive_codes = model.encode_operators(tables)
    model.encoded_batches.clear()

    monkeypatch.setattr(
        train_module,
        "map_split",
        lambda mapping: "train" if int(mapping[0]) in {1, 3} else "test",
    )
    loss = anonymous_composition_loss(
        model,
        tables,
        maps,
        primitive_codes,
        np.random.default_rng(11),
        min_length=2,
        max_length=2,
        words_by_length=words,
    )

    assert float(loss) == 0.0
    assert len(model.encoded_batches) == 1
    encoded_targets = model.encoded_batches[0]
    assert encoded_targets.shape == (2, 1, 8, 8)
    target_maps = encoded_targets[:, 0].argmax(dim=-1)
    assert set(target_maps[:, 0].tolist()) == {1, 3}


def test_shuffled_composition_target_is_a_genuine_negative_control(monkeypatch: pytest.MonkeyPatch) -> None:
    maps, tables = _shift_batch((1, 2, 3, 4))
    words = {2: torch.tensor([[0, 1], [0, 1], [0, 1], [0, 1]])}
    monkeypatch.setattr(train_module, "map_split", lambda mapping: "train")
    model = ExactPermutationEncoder()
    primitive_codes = model.encode_operators(tables)

    correct = anonymous_composition_loss(
        model,
        tables,
        maps,
        primitive_codes,
        np.random.default_rng(13),
        min_length=2,
        max_length=2,
        words_by_length=words,
    )
    shuffled = anonymous_composition_loss(
        model,
        tables,
        maps,
        primitive_codes,
        np.random.default_rng(13),
        min_length=2,
        max_length=2,
        shuffled_targets=True,
        shuffle_rng=np.random.default_rng(17),
        words_by_length=words,
    )
    assert float(correct) == 0.0
    assert float(shuffled) > 0.1


def test_metric_model_builder_and_auxiliary_training_smoke() -> None:
    model = build_model("linear_hyper_metric", max_length=4)
    assert isinstance(model, LinearHyperMetricOperatorRNN)
    initial_log_parameter = model.learned_metric.raw_log_metric.detach().clone()
    config = TrainConfig(
        model_name="linear_hyper_metric",
        regime="metric",
        seed=19,
        steps=2,
        batch_size=16,
        train_max_length=2,
        max_eval_length=4,
        learning_rate=1e-3,
        metric_isometry_weight=0.1,
        composition_weight=0.1,
        composition_min_length=2,
        composition_max_length=2,
        device="cpu",
    )
    trained = train_arm(model, config)
    assert np.isfinite(trained.final_loss)
    assert len(trained.trajectory) == 2
    assert all(np.isfinite(item["metric_isometry_loss"]) for item in trained.trajectory)
    assert all(np.isfinite(item["composition_loss"]) for item in trained.trajectory)
    assert not torch.equal(initial_log_parameter, model.learned_metric.raw_log_metric.detach())
