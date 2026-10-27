from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.delayed_return_training import (
    delayed_return_regularizer,
    ordered_prefix_products,
    q_to_p_return_energy,
    soft_observability_split,
)


DTYPE = torch.float64


def _invertible(dimension: int, seed: int) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    matrix = torch.randn(dimension, dimension, generator=generator, dtype=DTYPE)
    return matrix + 2.5 * torch.eye(dimension, dtype=DTYPE)


def _spd(dimension: int, seed: int) -> torch.Tensor:
    factor = _invertible(dimension, seed)
    return factor.transpose(0, 1) @ factor


def test_soft_split_has_no_asserted_nullspace_and_accepts_full_rank() -> None:
    rank_deficient = torch.tensor([[2.0, 0.0, 0.0]], dtype=DTYPE)
    split = soft_observability_split(rank_deficient, threshold=0.25, floor=0.03)

    identity = torch.eye(3, dtype=DTYPE)
    assert torch.allclose(split.observed + split.weakly_observed, identity)
    assert torch.all(torch.linalg.eigvalsh(split.observed_chart) > 0)
    assert torch.all(torch.linalg.eigvalsh(split.observed_chart) < 1)
    assert torch.all(torch.linalg.eigvalsh(split.weakly_observed_chart) > 0)
    assert torch.all(torch.linalg.eigvalsh(split.weakly_observed_chart) < 1)
    assert torch.linalg.matrix_norm(split.observed_chart @ split.observed_chart - split.observed_chart) > 0

    full_rank = soft_observability_split(torch.eye(3, dtype=DTYPE), threshold=0.25, floor=0.03)
    assert torch.all(torch.linalg.eigvalsh(full_rank.observed_chart) > 0.5)
    assert torch.all(torch.linalg.eigvalsh(full_rank.weakly_observed_chart) > 0)


def test_context_batch_produces_distinct_state_dependent_splits() -> None:
    observations = torch.tensor(
        [[[2.0, 0.0]], [[0.0, 2.0]]],
        dtype=DTYPE,
    )
    split = soft_observability_split(observations, threshold=0.1, floor=0.01)

    assert split.observed.shape == (2, 2, 2)
    assert split.observed_chart[0, 0, 0] > split.observed_chart[0, 1, 1]
    assert split.observed_chart[1, 1, 1] > split.observed_chart[1, 0, 0]


def test_ordered_products_use_recurrent_application_order() -> None:
    first = torch.tensor([[1.0, 2.0], [0.0, 1.0]], dtype=DTYPE)
    second = torch.tensor([[2.0, 0.0], [1.0, 1.0]], dtype=DTYPE)
    third = torch.tensor([[1.0, -1.0], [0.0, 3.0]], dtype=DTYPE)
    products = ordered_prefix_products(torch.stack((first, second, third)))

    assert torch.allclose(products[0], first)
    assert torch.allclose(products[1], second @ first)
    assert torch.allclose(products[2], third @ second @ first)


def test_delayed_q_to_p_return_distinguishes_mixing_from_no_return() -> None:
    split = soft_observability_split(
        torch.tensor([[1.0, 0.0]], dtype=DTYPE),
        threshold=1e-4,
        floor=1e-4,
    )
    identity = torch.eye(2, dtype=DTYPE)
    swap = torch.tensor([[0.0, 1.0], [1.0, 0.0]], dtype=DTYPE)

    no_return = delayed_return_regularizer(
        torch.stack((identity, identity)), split, delays=(2,)
    )
    mixing = delayed_return_regularizer(
        torch.stack((identity, swap)), split, delays=(2,)
    )

    assert float(no_return.loss) < 1e-6
    assert float(mixing.loss) > 0.99


def test_end_context_can_reveal_a_previously_weak_direction() -> None:
    start = soft_observability_split(
        torch.tensor([[1.0, 0.0]], dtype=DTYPE), threshold=1e-4, floor=1e-4
    )
    end = soft_observability_split(
        torch.tensor([[0.0, 1.0]], dtype=DTYPE), threshold=1e-4, floor=1e-4
    )
    identity = torch.eye(2, dtype=DTYPE)

    same_context = q_to_p_return_energy(identity, start, start)
    changed_context = q_to_p_return_energy(identity, start, end)

    assert float(same_context.fraction) < 1e-6
    assert float(changed_context.fraction) > 0.99


def test_explicit_chart_makes_return_exactly_coordinate_covariant() -> None:
    generator = torch.Generator().manual_seed(1211)
    dimension = 4
    chart = _invertible(dimension, 213)
    coordinate_change = _invertible(dimension, 217)
    coordinate_inverse = torch.linalg.inv(coordinate_change)
    observation = torch.randn(3, dimension, generator=generator, dtype=DTYPE)
    operators = torch.randn(3, dimension, dimension, generator=generator, dtype=DTYPE)

    split = soft_observability_split(observation, chart=chart, threshold=0.7, floor=0.02)
    transformed_split = soft_observability_split(
        observation @ coordinate_inverse,
        chart=chart @ coordinate_inverse,
        threshold=0.7,
        floor=0.02,
    )
    transformed_operators = coordinate_change @ operators @ coordinate_inverse

    original = delayed_return_regularizer(operators, split, delays=(2, 3))
    transformed = delayed_return_regularizer(
        transformed_operators, transformed_split, delays=(2, 3)
    )

    expected_observed = coordinate_change @ split.observed @ coordinate_inverse
    assert torch.allclose(transformed_split.observed, expected_observed, atol=2e-12, rtol=2e-12)
    assert torch.allclose(transformed.per_delay, original.per_delay, atol=2e-12, rtol=2e-12)
    assert torch.allclose(transformed.loss, original.loss, atol=2e-12, rtol=2e-12)


def test_metric_derived_charts_are_coordinate_covariant() -> None:
    generator = torch.Generator().manual_seed(223)
    dimension = 3
    metric = _spd(dimension, 227)
    coordinate_change = _invertible(dimension, 229)
    coordinate_inverse = torch.linalg.inv(coordinate_change)
    transformed_metric = coordinate_inverse.transpose(0, 1) @ metric @ coordinate_inverse
    observation = torch.randn(2, dimension, generator=generator, dtype=DTYPE)
    operators = torch.randn(4, dimension, dimension, generator=generator, dtype=DTYPE)

    original_split = soft_observability_split(
        observation, metric=metric, threshold=0.4, floor=0.015
    )
    transformed_split = soft_observability_split(
        observation @ coordinate_inverse,
        metric=transformed_metric,
        threshold=0.4,
        floor=0.015,
    )
    transformed_operators = coordinate_change @ operators @ coordinate_inverse

    original = delayed_return_regularizer(operators, original_split, delays=(2, 4))
    transformed = delayed_return_regularizer(
        transformed_operators, transformed_split, delays=(2, 4)
    )
    assert torch.allclose(transformed.per_delay, original.per_delay, atol=3e-11, rtol=3e-11)
    assert torch.allclose(transformed.raw_per_delay, original.raw_per_delay, atol=3e-10, rtol=3e-11)


def test_state_dependent_end_split_sequence_and_delay_weights() -> None:
    start = soft_observability_split(
        torch.tensor([[1.0, 0.0]], dtype=DTYPE), threshold=0.01, floor=0.01
    )
    reveal_y = soft_observability_split(
        torch.tensor([[0.0, 1.0]], dtype=DTYPE), threshold=0.01, floor=0.01
    )
    operators = torch.eye(2, dtype=DTYPE).repeat(3, 1, 1)
    result = delayed_return_regularizer(
        operators,
        start,
        end_splits=(start, reveal_y, start),
        delays=(2, 3),
        delay_weights=(1.0, 0.0),
    )

    assert result.delays == (2, 3)
    assert result.per_delay[0] > 0.95
    assert result.per_delay[1] < 1e-3
    assert torch.allclose(result.loss, result.per_delay[0])


def test_regularizer_is_differentiable_through_operators_and_split() -> None:
    generator = torch.Generator().manual_seed(233)
    operators = torch.randn(2, 4, 3, 3, generator=generator, dtype=DTYPE).requires_grad_()
    observation = torch.randn(2, 2, 3, generator=generator, dtype=DTYPE).requires_grad_()
    split = soft_observability_split(observation, threshold=0.5, floor=0.02)
    result = delayed_return_regularizer(
        operators,
        split,
        delays=(2, 3, 4),
        delay_weights=(0.2, 0.3, 0.5),
    )
    result.loss.backward()

    assert result.loss.ndim == 0
    assert operators.grad is not None and torch.isfinite(operators.grad).all()
    assert observation.grad is not None and torch.isfinite(observation.grad).all()
    assert torch.linalg.vector_norm(operators.grad) > 0
    assert torch.linalg.vector_norm(observation.grad) > 0


def test_invalid_geometry_and_delays_fail_closed() -> None:
    observation = torch.eye(2, dtype=DTYPE)
    with pytest.raises(ValueError, match="positive definite"):
        soft_observability_split(observation, metric=torch.diag(torch.tensor([1.0, -1.0])))
    with pytest.raises(ValueError, match="between zero and one half"):
        soft_observability_split(observation, floor=0.0)

    split = soft_observability_split(observation)
    operators = torch.eye(2, dtype=DTYPE).repeat(2, 1, 1)
    with pytest.raises(ValueError, match="no delayed products"):
        delayed_return_regularizer(operators[:1], split)
    with pytest.raises(ValueError, match="one split per step"):
        delayed_return_regularizer(operators, split, end_splits=(split,))
