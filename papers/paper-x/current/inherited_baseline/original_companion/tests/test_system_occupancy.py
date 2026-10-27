import sympy as sp

from projector_seed_residuals.occupancy import joint_projector, projector_trace_rank
from projector_seed_residuals.system import (
    LocalSpineRecord,
    recover_multiplicities,
    select_frobenius_separators,
    spine_is_compatible,
)


def test_common_spine() -> None:
    polynomials = ((1, -3, 2), (1, 1, 5))
    records = [LocalSpineRecord(p, polynomials, (0, 1), "det", ("u", "s")) for p in (3, 5, 7)]
    assert spine_is_compatible(records)
    changed = records + [LocalSpineRecord(11, ((1, -3, 2), (1, 2, 5)), (0, 1), "det", ("u", "s"))]
    assert not spine_is_compatible(changed)


def test_frobenius_separation_and_multiplicity_recovery() -> None:
    rows = [[1, 1, 1], [1, 2, 3], [2, 1, 0], [3, 0, 1]]
    selected = select_frobenius_separators(rows, 3)
    matrix = [rows[i] for i in selected]
    target = (2, 0, 1)
    observed = [sum(row[j] * target[j] for j in range(3)) for row in matrix]
    assert recover_multiplicities(matrix, observed, capacities=(3, 2, 2)) == target


def test_invalid_multiplicity_rejected() -> None:
    try:
        recover_multiplicities([[1, 0], [0, 2]], [1, 1])
    except ValueError as exc:
        assert "integers" in str(exc)
    else:
        raise AssertionError("half-integral multiplicity should be rejected")


def test_joint_projector_trace_is_rank() -> None:
    diagonal_data = [
        ([1, 1, 1, 2, 2, 2], 1),
        ([3, 3, 4, 3, 4, 4], 3),
        ([5, 6, 5, 5, 5, 6], 5),
        ([7, 8, 7, 7, 8, 8], 8),
    ]
    operators = []
    targets = []
    spectra = []
    expected = [3, 2, 1, 0]
    for item, expected_rank in zip(diagonal_data, expected, strict=True):
        diagonal, target = item
        operators.append(sp.diag(*diagonal))
        targets.append(target)
        spectra.append(sorted(set(diagonal)))
        projector = joint_projector(operators, targets, spectra)
        trace, rank = projector_trace_rank(projector)
        assert trace == rank == expected_rank
        assert projector * projector == projector
