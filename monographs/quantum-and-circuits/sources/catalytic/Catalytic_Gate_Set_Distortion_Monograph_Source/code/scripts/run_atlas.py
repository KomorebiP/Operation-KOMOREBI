#!/usr/bin/env python3
"""Run the finite experiments used in the monograph and write JSON results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from catalytic_gate_atlas import exact_affine_toffoli_census, exact_clifford_census, verify_canonical_atom


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/atlas_results.json"))
    parser.add_argument("--full-clifford-3", action="store_true", help="include the 1,451,520-element three-qubit Clifford census")
    args = parser.parse_args()

    results: dict[str, object] = {
        "linear_atom": [verify_canonical_atom(modulus) for modulus in (2, 3, 5, 8)],
        "affine_toffoli": [
            exact_affine_toffoli_census(3, entangling_cost=False),
            exact_affine_toffoli_census(3, entangling_cost=True),
        ],
        "clifford": [],
    }
    clifford_results = results["clifford"]
    assert isinstance(clifford_results, list)
    for qubits in (1, 2):
        clifford_results.append(exact_clifford_census(qubits, entangling_cost=False))
        clifford_results.append(exact_clifford_census(qubits, entangling_cost=True))
    if args.full_clifford_3:
        clifford_results.extend(
            [
                exact_clifford_census(3, entangling_cost=False),
                exact_clifford_census(3, entangling_cost=False, include_swap=True),
                exact_clifford_census(3, entangling_cost=True),
            ]
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
