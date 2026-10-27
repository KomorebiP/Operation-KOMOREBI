import numpy as np
from sric_real_lrm.interventions import derangement, norm_matched_noise, permute_trace


def test_permutation_is_derangement_and_deterministic():
    first = derangement(6, "task", 11)
    second = derangement(6, "task", 11)
    assert np.array_equal(first, second)
    assert np.all(first != np.arange(6))


def test_norm_matched_noise_preserves_step_norms():
    trace = np.arange(24, dtype=float).reshape(6, 4) + 1
    noise = norm_matched_noise(trace, "task", 9)
    assert np.allclose(np.linalg.norm(noise, axis=1), np.linalg.norm(trace, axis=1))
    assert not np.allclose(noise, trace)


def test_permuted_trace_changes_order_not_rows():
    trace = np.arange(24, dtype=float).reshape(6, 4)
    changed = permute_trace(trace, "task", 9)
    assert not np.array_equal(trace, changed)
    assert sorted(map(tuple, trace)) == sorted(map(tuple, changed))
