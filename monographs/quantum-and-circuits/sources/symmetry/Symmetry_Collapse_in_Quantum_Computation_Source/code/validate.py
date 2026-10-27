from __future__ import annotations

from math import comb
import numpy as np

from symmetry_packets import (
    PacketPlan,
    boson_fixed_number_dimension,
    circuit_leakage_bound,
    fermion_fixed_number_dimension,
    hypercube_quotient,
    log2_binomial,
    moving_frame_demo,
    qubit_commutant_parameter_count,
    residue_basis,
    simulate_fixed_weight_demo,
    symmetric_subspace_dimension,
    weight_basis,
)


def main() -> None:
    for n in range(1, 13):
        assert sum(len(weight_basis(n, k)) for k in range(n + 1)) == 2**n
        for k in range(n + 1):
            assert len(weight_basis(n, k)) == comb(n, k)
        assert len(residue_basis(n, 2, 0)) + len(residue_basis(n, 2, 1)) == 2**n
        assert symmetric_subspace_dimension(n, 2) == n + 1

    assert boson_fixed_number_dimension(10, 2) == 55
    assert fermion_fixed_number_dimension(10, 2) == 45

    q = hypercube_quotient(8)
    assert np.allclose(q, q.T)
    assert np.count_nonzero(q) == 16

    assert abs(circuit_leakage_bound([0.01, 0.02, 0.03]) - 0.06) < 1e-14

    for n in range(1, 30):
        for k in range(n + 1):
            assert abs(log2_binomial(n, k) - np.log2(comb(n, k))) < 2e-11
        count = qubit_commutant_parameter_count(n)
        assert count <= (n // 2 + 1) * (n + 1) ** 2

    moving_error = moving_frame_demo(seed=17)
    print(f"moving-frame reconstruction error = {moving_error:.3e}")
    assert moving_error < 2e-12

    for n, k in [(6, 1), (8, 2), (10, 2)]:
        error = simulate_fixed_weight_demo(n, k, seed=n + k)
        print(f"n={n}, k={k}: reconstruction error = {error:.3e}")
        assert error < 2e-12

    print("all validation checks passed")


if __name__ == "__main__":
    main()
