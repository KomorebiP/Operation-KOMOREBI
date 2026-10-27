"""Worked v1.1 bridge: coherent views, obstructions, and information gain.

Run from repository root with PYTHONPATH=src (or after installing the package).
"""
from __future__ import annotations

from proof_path_theory import (
    FiniteViewSystem, Restriction, analyze_affine_realizations,
    check_obstruction_witness,
)


def main() -> None:
    views = FiniteViewSystem(
        {"A": ("0", "1"), "B": ("0", "1"), "C": ("0", "1")},
        [
            Restriction("A", "B", {"0": "0", "1": "1"}),
            Restriction("B", "C", {"0": "0", "1": "1"}),
        ],
    )
    print("Coherent global views:", len(views.sections()))
    print("Glue:", views.glue(({"A": "1", "B": "1"}, {"B": "1", "C": "1"})))

    report = analyze_affine_realizations(
        dimension=3, compatibility=[(1, 1, 1)], protected=[(1, 0, 0)],
        candidate=(0, 0, 0), observation=[(0, 1, 0)],
    )
    print("Feasible:", report.feasible)
    print("Number of realizations:", report.realization_count)
    print("Observation gain (bits):", report.observation_gain_bits)
    print("Remaining ambiguity (bits):", report.remaining_ambiguity_bits)

    incompatible = analyze_affine_realizations(
        dimension=3, compatibility=[(1, 1, 0)],
        protected=[(1, 0, 0), (0, 1, 0)], candidate=(0, 1, 0),
    )
    assert incompatible.obstruction_witness is not None
    print("Incompatible protected data:", not incompatible.feasible)
    print("Checked obstruction:", check_obstruction_witness(
        dimension=3, compatibility=[(1, 1, 0)],
        protected=[(1, 0, 0), (0, 1, 0)], candidate=(0, 1, 0),
        witness=incompatible.obstruction_witness,
    ))


if __name__ == "__main__":
    main()
