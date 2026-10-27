"""Independent finite brute-force checks for the new realization bridge."""
from __future__ import annotations

from itertools import product
import random

import pytest

from proof_path_theory import (
    FiniteViewSystem,
    Restriction,
    analyze_affine_realizations,
    check_obstruction_witness,
)


def test_edge_cover_gluing_and_global_sections():
    system = FiniteViewSystem(
        {"v0": ("0", "1"), "v1": ("0", "1"), "v2": ("0", "1")},
        [
            Restriction("v0", "v1", {"0": "0", "1": "1"}),
            Restriction("v1", "v2", {"0": "0", "1": "1"}),
        ],
    )
    assert system.covers_arrows((("v0", "v1"), ("v1", "v2")))
    assert system.glue(({"v0": "1", "v1": "1"}, {"v1": "1", "v2": "1"})) == {"v0": "1", "v1": "1", "v2": "1"}
    assert len(system.sections()) == 2
    with pytest.raises(ValueError, match="disagree"):
        system.glue(({"v0": "0", "v1": "0"}, {"v1": "1", "v2": "1"}))


def test_object_cover_not_arrow_cover():
    system = FiniteViewSystem(
        {"v0": ("0", "1"), "v1": ("0", "1")},
        [Restriction("v0", "v1", {"0": "0", "1": "1"})],
    )
    assert not system.covers_arrows((("v0",), ("v1",)))
    with pytest.raises(ValueError, match="cover"):
        system.glue(({"v0": "0"}, {"v1": "1"}))
    assert not system.is_coherent({"v0": "0", "v1": "1"})


def test_obstructed_parity_analogue_with_witness():
    # y1=y0, protected y0=0, y1=1 cannot both be imposed by one
    # observation map on x, so instead use the 3-variable system
    # y0=y1 and P(y)=(y0,y1), x=(0,1,0).
    a = [(1, 1, 0)]
    p = [(1, 0, 0), (0, 1, 0)]
    report = analyze_affine_realizations(
        dimension=3, compatibility=a, protected=p, candidate=(0, 1, 0),
    )
    assert not report.feasible
    assert report.realization_count == 0
    assert report.obstruction_witness is not None
    assert check_obstruction_witness(
        dimension=3, compatibility=a, protected=p, candidate=(0, 1, 0),
        witness=report.obstruction_witness,
    )
    assert not check_obstruction_witness(
        dimension=3, compatibility=a, protected=p, candidate=(0, 1, 0),
        witness=(0, 0, 0),
    )


def test_entropy_observation_rank():
    # One relation and y0 fixed leave exactly one binary bit.
    result = analyze_affine_realizations(
        dimension=3,
        compatibility=[(1, 1, 1)],
        protected=[(1, 0, 0)],
        candidate=(0, 0, 0),
        observation=[(0, 1, 0)],
    )
    assert result.feasible and result.solution is not None
    assert result.realization_count == 2
    assert result.ambiguity_dimension == 1
    assert result.observation_gain_bits == 1
    assert result.remaining_ambiguity_bits == 0


def _satisfies(rows, vector, rhs):
    return all(sum(a * b for a, b in zip(row, vector)) % 2 == y
               for row, y in zip(rows, rhs))


def test_random_exact_crosscheck_and_fiber_sizes():
    rng = random.Random(20261018)
    for n in range(1, 6):
        for _ in range(40):
            a = [tuple(rng.randrange(2) for _ in range(n)) for _ in range(rng.randrange(0, n + 2))]
            p = [tuple(rng.randrange(2) for _ in range(n)) for _ in range(rng.randrange(0, n + 2))]
            q = [tuple(rng.randrange(2) for _ in range(n)) for _ in range(rng.randrange(0, n + 2))]
            x = tuple(rng.randrange(2) for _ in range(n))
            rhs = [0] * len(a) + [sum(u * v for u, v in zip(row, x)) % 2 for row in p]
            sols = [y for y in product((0, 1), repeat=n) if _satisfies(a + p, y, rhs)]
            result = analyze_affine_realizations(
                dimension=n, compatibility=a, protected=p, candidate=x, observation=q,
            )
            assert result.feasible == bool(sols)
            assert result.realization_count == len(sols)
            if sols:
                assert result.obstruction_witness is None
                assert result.solution in sols
                assert len(result.ambiguity_basis) == result.ambiguity_dimension
                observed = {
                    tuple(sum(u * v for u, v in zip(row, y)) % 2 for row in q)
                    for y in sols
                }
                assert len(observed) == 2 ** result.observation_gain_bits
                multiplicities = [
                    sum(tuple(sum(u * v for u, v in zip(row, y)) % 2 for row in q) == ob for y in sols)
                    for ob in observed
                ]
                assert set(multiplicities) == {2 ** result.remaining_ambiguity_bits}
            else:
                assert result.obstruction_witness is not None
                assert check_obstruction_witness(
                    dimension=n, compatibility=a, protected=p, candidate=x,
                    witness=result.obstruction_witness,
                )


def test_input_guards():
    with pytest.raises(ValueError):
        analyze_affine_realizations(dimension=2, compatibility=[(1, 0, 1)], protected=[], candidate=(0, 0))
    with pytest.raises(ValueError):
        analyze_affine_realizations(dimension=2, compatibility=[], protected=[], candidate=(0, 2))
    with pytest.raises(ValueError):
        FiniteViewSystem({"a": ["0"], "b": ["0"]}, [Restriction("a", "b", {"1": "0"})])


def test_refuted_branch_does_not_block_alternative_certified_proof():
    from proof_path_theory import ClaimNode, NodeKind, Justification, ProofField

    field = ProofField(
        nodes=[
            ClaimNode("A", "Premise", NodeKind.PREMISE),
            ClaimNode("Lbad", "Rejected intermediate lemma", NodeKind.FAILED_ROUTE),
            ClaimNode("G", "Target", NodeKind.THEOREM),
        ],
        justifications=[
            Justification("attempt", ("A",), "Lbad", "candidate step", certified=False),
            Justification("bad_end", ("Lbad",), "G", "candidate continuation", certified=False),
            Justification("good_end", ("A",), "G", "certified alternative", certified=True),
        ],
        premises=("A",),
        targets=("G",),
    )
    assert "G" in field.derive(certified_only=True)
    assert "Lbad" not in field.derive(certified_only=True)
    assert len(field.certified_subfield().justifications) == 1
