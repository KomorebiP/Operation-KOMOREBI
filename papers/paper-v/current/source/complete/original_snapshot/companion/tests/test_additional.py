import numpy as np
import pytest

from projector_signal.edges import (
    estimated_edge_reconstruct_1d,
    estimated_edge_reconstruct_2d,
    fft_lowpass_1d,
    fft_lowpass_2d,
    mask_iou,
    rmse,
)
from projector_signal.experiments import make_disk_2d, make_signal_1d, sparse_haar_packet_reconstruction
from projector_signal.filterbanks import haar_packet_analyze, haar_packet_synthesize
from projector_signal.polyphase import polyphase_analyze, polyphase_convolution, polyphase_synthesize, refinement_children
from projector_signal.smith import project_coefficients, root_filter_project


def test_channel_lengths_cover_input() -> None:
    x = np.arange(103)
    for order in (2, 3, 7, 16):
        channels = polyphase_analyze(x, order)
        assert sum(map(len, channels)) == len(x)
        assert np.array_equal(polyphase_synthesize(channels, order, len(x)), x)


def test_refinement_children_partition() -> None:
    for coarse, fine in ((2, 8), (3, 12), (5, 20)):
        children = [set(refinement_children(coarse, fine, r)) for r in range(coarse)]
        assert set.union(*children) == set(range(fine))
        assert sum(len(a & b) for i, a in enumerate(children) for b in children[i + 1 :]) == 0


def test_complex_polyphase_convolution() -> None:
    rng = np.random.default_rng(101)
    x = rng.normal(size=19) + 1j * rng.normal(size=19)
    h = rng.normal(size=9) + 1j * rng.normal(size=9)
    assert np.max(np.abs(np.convolve(x, h) - polyphase_convolution(x, h, 4))) < 3e-12


def test_incomplete_wavelet_tree_rejected() -> None:
    packets = haar_packet_analyze(np.arange(16.0), 2)
    packets.pop("11")
    with pytest.raises(ValueError):
        haar_packet_synthesize(packets)


def test_estimated_1d_improves_global_case() -> None:
    case = make_signal_1d(512)
    global_recon = fft_lowpass_1d(case["signal"], 16)
    estimated, mask, _ = estimated_edge_reconstruct_1d(case["signal"], 16)
    assert rmse(case["signal"], estimated) < rmse(case["signal"], global_recon)
    assert mask_iou(case["mask"], mask) > 0.95


def test_estimated_2d_improves_global_case() -> None:
    case = make_disk_2d(128)
    global_recon = fft_lowpass_2d(case["image"], 12)
    estimated, mask, _ = estimated_edge_reconstruct_2d(case["image"], 12)
    assert rmse(case["image"], estimated) < rmse(case["image"], global_recon)
    assert mask_iou(case["mask"], mask) > 0.95


def test_mask_symmetric_difference_norm_identity() -> None:
    a = np.zeros(100, dtype=bool); a[20:60] = True
    b = np.zeros(100, dtype=bool); b[25:70] = True
    for p in (1, 2, 4):
        lhs = np.linalg.norm(a.astype(float) - b.astype(float), ord=p)
        rhs = np.logical_xor(a, b).sum() ** (1 / p)
        assert abs(lhs - rhs) < 1e-12


def test_root_filter_matches_coefficient_projection() -> None:
    rng = np.random.default_rng(102)
    coeffs = rng.normal(size=19) + 1j * rng.normal(size=19)
    z = np.array([0.1 + 0.2j, -0.3 + 0.1j, 0.5 - 0.05j])
    def evaluate(value):
        out = np.zeros_like(value, dtype=complex)
        for c in coeffs[::-1]:
            out = out * value + c
        return out
    for order in (2, 3, 4, 5):
        for phase in range(order):
            projected = project_coefficients(coeffs, order, phase)
            direct = np.zeros_like(z, dtype=complex)
            for c in projected[::-1]:
                direct = direct * z + c
            filtered = root_filter_project(evaluate, z, order, phase)
            assert np.max(np.abs(direct - filtered)) < 2e-10


def test_sparse_packet_reconstruction_count() -> None:
    case = make_signal_1d(256)
    centered = case["signal"] - case["signal"].mean()
    reconstructed, count = sparse_haar_packet_reconstruction(centered, depth=4, keep=40)
    assert count == 40
    assert reconstructed.shape == centered.shape


def test_sparse_packet_full_reconstruction() -> None:
    case = make_signal_1d(256)
    centered = case["signal"] - case["signal"].mean()
    reconstructed, count = sparse_haar_packet_reconstruction(centered, depth=4, keep=256)
    assert count == 256
    assert np.max(np.abs(reconstructed - centered)) < 2e-15
