import numpy as np
import pytest

from seed_refinement.smith_chart import (
    gamma_from_impedance,
    impedance_from_gamma,
    phase_transform,
    polyphase_orbit,
    smith_weight,
)


def test_cayley_inverse() -> None:
    values = [0.5 + 0.2j, 1.0 + 0j, 3.2 - 1.1j, 0.1 + 2.0j]
    for z in values:
        assert abs(impedance_from_gamma(gamma_from_impedance(z)) - z) < 1e-12


def test_two_phase_is_impedance_inversion() -> None:
    for z in [0.5 + 0.2j, 2.5 + 0.7j, 0.1 + 1.4j]:
        assert abs(phase_transform(z, 2, 1) - 1 / z) < 1e-12


def test_orbit_has_constant_gamma_radius() -> None:
    for order in (2, 4, 8, 16, 32):
        orbit = polyphase_orbit(0.73, order)
        radii = np.array([abs(gamma_from_impedance(z)) for z in orbit])
        assert np.max(abs(radii - 0.73)) < 1e-12


def test_smith_weight_symmetry() -> None:
    for gamma in [0.1 + 0.2j, 0.4 - 0.3j, -0.2 + 0.7j]:
        assert abs(smith_weight(gamma) - smith_weight(-gamma)) < 1e-12


def test_polyphase_order_contract_is_explicit() -> None:
    for order in (0, -1, 1.5, True):
        with pytest.raises(ValueError, match="positive integer"):
            polyphase_orbit(0.4, order)  # type: ignore[arg-type]
