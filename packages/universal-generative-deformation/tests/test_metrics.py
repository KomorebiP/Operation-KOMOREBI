import math

import pytest

from generative_deformation.metrics import (
    branching_entropy,
    geometric_tree_partition,
    growth_series,
    propagated_cover_error,
    summable_step_tail,
    weighted_partition_function,
)


def test_branching_entropy_binary() -> None:
    counts = {depth: 2**depth for depth in range(1, 9)}
    assert abs(branching_entropy(counts) - math.log(2)) < 1e-12


def test_growth_series() -> None:
    assert growth_series({0: 1, 1: 2, 2: 4}, 0.5) == 3


def test_weighted_partition_function() -> None:
    value = weighted_partition_function([0, 1, 2], 1)
    assert abs(value - (1 + math.exp(-1) + math.exp(-2))) < 1e-12


def test_geometric_partition_converges_above_threshold() -> None:
    assert math.isfinite(geometric_tree_partition(3, 1.0, 2.0))


def test_geometric_partition_diverges_below_threshold() -> None:
    assert math.isinf(geometric_tree_partition(3, 1.0, 1.0))


def test_propagated_cover_error_matches_recursion() -> None:
    error = propagated_cover_error([2, 2], [1, 1], [0.1, 0.1])
    assert abs(error - 0.3) < 1e-12


def test_cover_error_rejects_bad_lengths() -> None:
    with pytest.raises(ValueError):
        propagated_cover_error([1], [1, 1], [0.1])


def test_summable_tail() -> None:
    assert abs(summable_step_tail([0.5, 0.25, 0.125], 1) - 0.375) < 1e-12
