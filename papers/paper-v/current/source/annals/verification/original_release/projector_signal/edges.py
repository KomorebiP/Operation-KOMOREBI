from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from scipy import ndimage


def fft_lowpass_1d(x: Sequence[float], modes: int) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    spectrum = np.fft.fft(arr)
    frequencies = np.fft.fftfreq(len(arr)) * len(arr)
    return np.real(np.fft.ifft(spectrum * (np.abs(frequencies) <= modes)))


def fft_lowpass_2d(image: np.ndarray, cutoff: int) -> np.ndarray:
    arr = np.asarray(image, dtype=float)
    spectrum = np.fft.fftshift(np.fft.fft2(arr))
    h, w = arr.shape
    yy, xx = np.ogrid[:h, :w]
    cy, cx = h // 2, w // 2
    mask = (np.abs(yy - cy) <= cutoff) & (np.abs(xx - cx) <= cutoff)
    return np.real(np.fft.ifft2(np.fft.ifftshift(spectrum * mask)))


def exact_edge_reconstruct_1d(smooth: Sequence[float], edge_packet: Sequence[float], modes: int) -> np.ndarray:
    return fft_lowpass_1d(smooth, modes) + np.asarray(edge_packet, dtype=float)


def exact_edge_reconstruct_2d(smooth: np.ndarray, edge_packet: np.ndarray, cutoff: int) -> np.ndarray:
    return fft_lowpass_2d(smooth, cutoff) + np.asarray(edge_packet, dtype=float)


def otsu_threshold(values: np.ndarray, bins: int = 256) -> float:
    arr = np.asarray(values, dtype=float).ravel()
    lo, hi = float(arr.min()), float(arr.max())
    if np.isclose(lo, hi):
        return lo
    hist, edges = np.histogram(arr, bins=bins, range=(lo, hi))
    centers = (edges[:-1] + edges[1:]) / 2.0
    prob = hist.astype(float) / max(hist.sum(), 1)
    omega = np.cumsum(prob)
    mu = np.cumsum(prob * centers)
    variance = (mu[-1] * omega - mu) ** 2 / np.maximum(omega * (1.0 - omega), 1e-15)
    return float(centers[int(np.argmax(variance))])


def estimate_packet_1d(signal: Sequence[float], coarse_modes: int = 8) -> np.ndarray:
    """Estimate one positive-contrast binary packet by intensity separation.

    ``coarse_modes`` is retained in the API for experiment compatibility.  The
    estimator deliberately has a narrow claim: it is a two-class positive-contrast
    segmentation, not a universal edge detector.
    """
    arr = np.asarray(signal, dtype=float)
    mask = arr > otsu_threshold(arr)
    labels, count = ndimage.label(mask)
    if count:
        sizes = ndimage.sum(mask, labels, range(1, count + 1))
        keep = [int(np.argmax(sizes)) + 1]
        mask = np.isin(labels, keep)
    return ndimage.binary_closing(mask, structure=np.ones(5)).astype(bool)


def _periodic_harmonic_inpaint_1d(signal: np.ndarray, mask: np.ndarray, iterations: int = 800) -> np.ndarray:
    outside = ~mask
    u = signal.copy()
    u[mask] = float(np.mean(signal[outside])) if np.any(outside) else 0.0
    for _ in range(iterations):
        previous = u.copy()
        average = 0.5 * (np.roll(previous, 1) + np.roll(previous, -1))
        u[mask] = average[mask]
        u[outside] = signal[outside]
    return u


def estimated_edge_reconstruct_1d(
    signal: Sequence[float], modes: int, coarse_modes: int = 8
) -> tuple[np.ndarray, np.ndarray, float]:
    arr = np.asarray(signal, dtype=float)
    mask = estimate_packet_1d(arr, coarse_modes)
    background = _periodic_harmonic_inpaint_1d(arr, mask)
    smooth_est = fft_lowpass_1d(background, modes)
    amplitude = float(np.median(arr[mask] - smooth_est[mask])) if np.any(mask) else 0.0
    return smooth_est + amplitude * mask.astype(float), mask, amplitude


def estimate_packet_2d(image: np.ndarray, coarse_cutoff: int = 8, min_fraction: float = 0.002) -> np.ndarray:
    """Estimate positive-contrast binary packets by Otsu separation and topology cleanup."""
    arr = np.asarray(image, dtype=float)
    candidate = arr > otsu_threshold(arr)
    candidate = ndimage.binary_opening(candidate, structure=np.ones((3, 3)))
    labels, count = ndimage.label(candidate)
    if count:
        sizes = ndimage.sum(candidate, labels, range(1, count + 1))
        keep = [i + 1 for i, size in enumerate(sizes) if size >= min_fraction * arr.size]
        if not keep:
            keep = [int(np.argmax(sizes)) + 1]
        candidate = np.isin(labels, keep)
    candidate = ndimage.binary_fill_holes(candidate)
    return ndimage.binary_closing(candidate, structure=np.ones((3, 3))).astype(bool)


def harmonic_inpaint_2d(image: np.ndarray, mask: np.ndarray, iterations: int = 900) -> np.ndarray:
    arr, mask = np.asarray(image, dtype=float), np.asarray(mask, dtype=bool)
    outside = ~mask
    u = arr.copy()
    u[mask] = float(np.mean(arr[outside])) if np.any(outside) else 0.0
    for _ in range(iterations):
        previous = u.copy()
        average = (
            np.roll(previous, 1, axis=0)
            + np.roll(previous, -1, axis=0)
            + np.roll(previous, 1, axis=1)
            + np.roll(previous, -1, axis=1)
        ) / 4.0
        u[mask], u[outside] = average[mask], arr[outside]
    return u


def estimated_edge_reconstruct_2d(
    image: np.ndarray, cutoff: int, coarse_cutoff: int = 8
) -> tuple[np.ndarray, np.ndarray, float]:
    arr = np.asarray(image, dtype=float)
    mask = estimate_packet_2d(arr, coarse_cutoff)
    background = harmonic_inpaint_2d(arr, mask)
    smooth_est = fft_lowpass_2d(background, cutoff)
    amplitude = float(np.median(arr[mask] - smooth_est[mask])) if np.any(mask) else 0.0
    return smooth_est + amplitude * mask.astype(float), mask, amplitude


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((np.asarray(a) - np.asarray(b)) ** 2)))


def mask_iou(a: np.ndarray, b: np.ndarray) -> float:
    aa, bb = np.asarray(a, dtype=bool), np.asarray(b, dtype=bool)
    union = np.logical_or(aa, bb).sum()
    return float(np.logical_and(aa, bb).sum() / union) if union else 1.0


def boundary_band(mask: np.ndarray, width: int = 3) -> np.ndarray:
    mask = np.asarray(mask, dtype=bool)
    return np.logical_xor(
        ndimage.binary_dilation(mask, iterations=width),
        ndimage.binary_erosion(mask, iterations=width),
    )
