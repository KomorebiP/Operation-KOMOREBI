import sympy as sp

from seed_refinement.dyadic import delayed_separation_example, resultant_weight, smith_diagonal_solve, valuation


def test_valuation() -> None:
    assert valuation(40, 2) == 3
    assert valuation(81, 3) == 4
    assert valuation(-250, 5) == 3


def test_delayed_separation() -> None:
    data = delayed_separation_example()
    assert data["plus_idempotent"]
    assert data["minus_idempotent"]
    assert data["orthogonal"]
    assert any(value.q == 2 for value in data["plus"])
    assert all(value.q == 1 for value in data["scaled_plus"])


def test_resultant_weight_distinguishes_two() -> None:
    x = sp.Symbol("x")
    f, g = sp.Poly(x - 1, x), sp.Poly(x + 1, x)
    assert resultant_weight(f, g, 2) == (2, 1)
    assert resultant_weight(f, g, 3) == (2, 0)


def test_smith_solvability_and_counts() -> None:
    good = smith_diagonal_solve([0, 1, 3], [1, 2, 8], 2, 6)
    assert good.solvable and good.solution_count == 16
    bad = smith_diagonal_solve([0, 1, 3], [1, 2, 4], 2, 6)
    assert not bad.solvable
    truncated = smith_diagonal_solve([2, 8], [4, 0], 2, 5)
    assert truncated.solvable and truncated.solution_count == 2**7
