import numpy as np

from seed_refinement.projectors import (
    analyze_residues,
    crt_index,
    residue_projectors,
    root_of_unity_projectors,
    synthesize_residues,
    verify_crt_factorization,
    verify_refinement,
)


def test_packet_analysis_synthesis() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(size=101)
    for modulus in range(1, 17):
        assert np.array_equal(synthesize_residues(analyze_residues(x, modulus)), x)


def test_residue_projectors() -> None:
    for modulus in (2, 3, 4, 5, 8, 12):
        ps = residue_projectors(77, modulus)
        assert np.array_equal(sum(ps), np.eye(77, dtype=int))
        for i, p in enumerate(ps):
            assert np.array_equal(p @ p, p)
            for j, q in enumerate(ps):
                if i != j:
                    assert not np.any(p @ q)


def test_refinement() -> None:
    for coarse, fine in [(2, 4), (2, 8), (3, 6), (3, 12), (4, 8), (4, 12), (6, 12)]:
        assert verify_refinement(137, coarse, fine) == 0.0


def test_root_of_unity_projectors() -> None:
    for order in range(1, 11):
        ps = root_of_unity_projectors(order)
        assert np.linalg.norm(sum(ps) - np.eye(order)) < 1e-9
        for i, p in enumerate(ps):
            assert np.linalg.norm(p @ p - p) < 1e-9
            for j, q in enumerate(ps):
                if i != j:
                    assert np.linalg.norm(p @ q) < 1e-9


def test_crt() -> None:
    for a, b in [(2, 3), (4, 3), (8, 3), (4, 5), (8, 5)]:
        for r in range(a):
            for s in range(b):
                j = crt_index(a, b, r, s)
                assert j % a == r
                assert j % b == s
        assert verify_crt_factorization(3 * a * b + 1, a, b) == 0.0
