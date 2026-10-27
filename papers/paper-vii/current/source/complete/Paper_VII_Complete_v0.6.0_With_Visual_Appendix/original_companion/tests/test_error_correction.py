import numpy as np

from projector_quantum_calculus.basic import ketbra
from projector_quantum_calculus.codes import (
    bit_flip_channel,
    bit_flip_code_projector,
    bit_flip_errors,
    bit_flip_recovery,
    encode_logical_state,
    knill_laflamme_residual,
    syndrome_projectors,
)


def test_syndrome_projectors() -> None:
    projectors = syndrome_projectors()
    assert np.linalg.norm(sum(projectors) - np.eye(8)) < 1e-12
    for i, p in enumerate(projectors):
        assert np.linalg.norm(p @ p - p) < 1e-12
        for q in projectors[:i]:
            assert np.linalg.norm(p @ q) < 1e-12


def test_knill_laflamme_bit_flip_code() -> None:
    _, residual = knill_laflamme_residual(bit_flip_code_projector(), bit_flip_errors())
    assert residual < 1e-12


def test_exact_bit_flip_recovery() -> None:
    state = encode_logical_state(np.sqrt(0.37), np.sqrt(0.63) * np.exp(0.41j))
    rho = ketbra(state)
    corrupted = bit_flip_channel(rho, [0.70, 0.08, 0.11, 0.11])
    recovered = bit_flip_recovery(corrupted)
    assert np.linalg.norm(recovered - rho) < 1e-12
