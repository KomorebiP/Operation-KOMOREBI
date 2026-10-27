from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from typing import Callable

import numpy as np

from rrct_lab.jspace import (
    JacobianFrame,
    MovingJacobianFrame,
    activation_variance_fraction,
    discover_jacobian_frame,
    jacobian_energy_capture,
    measure_jacobian_frame,
    projector_idempotence_defect,
    report_r2,
)


def _raises(error_type: type[BaseException], action: Callable[[], object]) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(f"expected {error_type.__name__}")


def test_discovery_projection_metrics_and_immutability() -> None:
    jacobian = np.array(
        [
            [3.0, 0.0, 0.0, 0.0],
            [0.0, 2.0, 0.0, 0.0],
        ]
    )
    frame = discover_jacobian_frame(jacobian, rank=2, top_k=1)
    assert frame.rank == 2
    assert frame.basis.shape == (4, 2)
    assert frame.frame_vectors.shape == (4, 2)
    hidden = np.array([1.0, 2.0, 3.0, 4.0])
    np.testing.assert_allclose(frame.project(hidden), [1.0, 2.0, 0.0, 0.0])
    np.testing.assert_allclose(frame.ablate(hidden), [0.0, 0.0, 3.0, 4.0])
    batch = np.array(
        [
            [1.0, 0.0, 2.0, 0.0],
            [0.0, 1.0, 0.0, 2.0],
            [-1.0, 2.0, 1.0, -1.0],
        ]
    )
    targets = batch @ jacobian.T
    metrics = measure_jacobian_frame(frame, batch, targets)
    assert metrics.projector_idempotence_defect < 1e-14
    assert metrics.jacobian_energy_capture == 1.0
    assert 0.0 < metrics.activation_variance_fraction < 1.0
    assert metrics.report_r2 == 1.0
    assert projector_idempotence_defect(frame.projector) < 1e-14
    assert jacobian_energy_capture(jacobian, frame.projector) == 1.0
    assert activation_variance_fraction(batch, frame.projector) == (
        metrics.activation_variance_fraction
    )
    assert report_r2(jacobian, batch, targets) == 1.0

    _raises(ValueError, lambda: frame.average_jacobian.__setitem__((0, 0), 4.0))
    _raises(ValueError, lambda: frame.basis.setflags(write=True))
    _raises(FrozenInstanceError, lambda: setattr(frame, "top_k", 2))


def test_sparse_nonnegative_code_reconstruction_and_swap() -> None:
    frame = discover_jacobian_frame(np.eye(3), rank=3, top_k=2)
    hidden = np.array([3.0, 2.0, -1.0])
    code = frame.sparse_code(hidden)
    np.testing.assert_array_equal(code, [3.0, 2.0, 0.0])
    assert np.count_nonzero(code) == 2
    assert np.all(code >= 0.0)
    support, coefficients = frame.sparse_content(hidden)
    assert support == (0, 1)
    assert coefficients == (3.0, 2.0)
    np.testing.assert_array_equal(frame.reconstruct(code), code)

    swapped = frame.swap(hidden, 0, 2)
    np.testing.assert_allclose(swapped, [0.0, 2.0, 3.0])
    np.testing.assert_array_equal(frame.swap(hidden, 2, 0), hidden)
    np.testing.assert_array_equal(frame.swap(hidden, 0, 0), hidden)
    _raises(ValueError, lambda: frame.reconstruct([1.0, -1.0, 0.0]))
    _raises(ValueError, lambda: frame.sparse_code(hidden, top_k=4))
    _raises(ValueError, lambda: frame.swap(hidden, 3, 0))

    truncated = discover_jacobian_frame(
        np.diag([3.0, 2.0, 1.0]), rank=2, top_k=2
    )
    reconstructed = truncated.reconstruct([1.0, 2.0, 3.0])
    np.testing.assert_allclose(
        truncated.ablate(reconstructed), np.zeros(3), atol=1e-14
    )
    np.testing.assert_array_equal(
        truncated.sparse_code([0.0, 0.0, 7.0]), np.zeros(3)
    )
    truncated_hidden = np.array([3.0, 2.0, 7.0])
    truncated_swapped = truncated.swap(truncated_hidden, 0, 1)
    np.testing.assert_allclose(
        truncated.ablate(truncated_swapped),
        truncated.ablate(truncated_hidden),
        atol=1e-14,
    )


def test_spectral_selection_and_validation_guards() -> None:
    jacobian = np.diag([4.0, 1.0, 0.01])
    frame = discover_jacobian_frame(
        jacobian, spectral_threshold=0.2, top_k=1
    )
    assert frame.rank == 2
    assert np.isclose(
        jacobian_energy_capture(jacobian, frame.projector), 17.0 / 17.0001
    )

    _raises(ValueError, lambda: discover_jacobian_frame(jacobian))
    _raises(
        ValueError,
        lambda: discover_jacobian_frame(
            jacobian, rank=2, spectral_threshold=0.1
        ),
    )
    _raises(ValueError, lambda: discover_jacobian_frame(jacobian, rank=4))
    _raises(
        ValueError,
        lambda: discover_jacobian_frame(
            np.diag([1.0, 0.0, 0.0]), rank=2, top_k=1
        ),
    )
    _raises(
        ValueError,
        lambda: discover_jacobian_frame(jacobian, spectral_threshold=1.0),
    )
    _raises(ValueError, lambda: discover_jacobian_frame(np.zeros((2, 3)), rank=1))
    _raises(
        ValueError,
        lambda: discover_jacobian_frame([[1.0, np.nan]], rank=1),
    )
    _raises(ValueError, lambda: frame.project([1.0, 2.0]))
    _raises(ValueError, lambda: frame.project([1.0, 2.0, np.inf]))
    _raises(ValueError, lambda: report_r2(jacobian, np.eye(3), np.ones((3, 3))))


def test_moving_frame_orientation_and_json_exact_resume() -> None:
    initial = np.array(
        [
            [3.0, 0.0, 0.0],
            [0.0, 2.0, 0.0],
        ]
    )
    moving = MovingJacobianFrame(initial, decay=0.75, rank=2, top_k=1)
    previous_basis = moving.frame.basis.copy()
    angle = 0.08
    observed = np.array(
        [
            [3.0 * np.cos(angle), 3.0 * np.sin(angle), 0.0],
            [-2.0 * np.sin(angle), 2.0 * np.cos(angle), 0.0],
        ]
    )
    moving.update(observed)
    assert moving.updates == 1
    orientation = np.diag(previous_basis.T @ moving.frame.basis)
    assert np.all(orientation > 0.99)

    encoded = json.dumps(moving.state_dict(), sort_keys=True)
    decoded = json.loads(encoded)
    restored = MovingJacobianFrame.from_state_dict(decoded)
    assert restored.state_dict() == decoded

    loaded = MovingJacobianFrame(initial, decay=0.1, rank=1, top_k=1)
    loaded.load_state_dict(decoded)
    assert loaded.state_dict() == decoded

    next_observation = np.array(
        [
            [2.8, 0.4, 0.0],
            [-0.2, 2.2, 0.0],
        ]
    )
    continued = moving.update(next_observation)
    replayed = restored.update(next_observation)
    np.testing.assert_array_equal(
        continued.average_jacobian, replayed.average_jacobian
    )
    np.testing.assert_array_equal(continued.basis, replayed.basis)
    np.testing.assert_array_equal(
        continued.singular_values, replayed.singular_values
    )
    assert moving.state_dict() == restored.state_dict()

    corrupted = json.loads(encoded)
    corrupted["basis"][0][0] = 0.5
    _raises(ValueError, lambda: MovingJacobianFrame.from_state_dict(corrupted))
    _raises(ValueError, lambda: moving.update(np.ones((3, 2))))


if __name__ == "__main__":
    test_discovery_projection_metrics_and_immutability()
    test_sparse_nonnegative_code_reconstruction_and_swap()
    test_spectral_selection_and_validation_guards()
    test_moving_frame_orientation_and_json_exact_resume()
    print("test_jspace_core: 4 direct tests passed")
