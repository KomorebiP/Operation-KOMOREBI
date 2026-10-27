from __future__ import annotations

from math import gcd
from typing import Sequence

import numpy as np


def residue_masks(length: int, modulus: int) -> list[np.ndarray]:
    if length < 0 or modulus < 1:
        raise ValueError("length must be nonnegative and modulus positive")
    indices = np.arange(length)
    return [(indices % modulus == j) for j in range(modulus)]


def residue_projectors(length: int, modulus: int) -> list[np.ndarray]:
    return [np.diag(mask.astype(int)) for mask in residue_masks(length, modulus)]


def analyze_residues(vector: Sequence[complex], modulus: int) -> list[np.ndarray]:
    if modulus < 1:
        raise ValueError("modulus must be positive")
    x = np.asarray(vector)
    return [x[j::modulus].copy() for j in range(modulus)]


def synthesize_residues(packets: Sequence[Sequence[complex]]) -> np.ndarray:
    if not packets:
        return np.array([], dtype=float)
    modulus = len(packets)
    lengths = [len(packet) for packet in packets]
    if max(lengths) - min(lengths) > 1 or any(
        lengths[j] < lengths[j + 1] for j in range(modulus - 1)
    ):
        raise ValueError("packet lengths are not compatible with residue interleaving")
    length = sum(len(packet) for packet in packets)
    dtype = np.result_type(*[np.asarray(packet).dtype for packet in packets])
    out = np.empty(length, dtype=dtype)
    for j, packet in enumerate(packets):
        out[j::modulus] = np.asarray(packet)
    return out


def refinement_incidence(coarse: int, fine: int) -> np.ndarray:
    if coarse < 1 or fine < 1 or fine % coarse:
        raise ValueError("fine modulus must be a positive multiple of coarse modulus")
    matrix = np.zeros((coarse, fine), dtype=int)
    for s in range(fine):
        matrix[s % coarse, s] = 1
    return matrix


def root_of_unity_projectors(order: int) -> list[np.ndarray]:
    """Character projectors for the cyclic shift representation of C_order."""
    if order < 1:
        raise ValueError("order must be positive")
    shift = np.zeros((order, order), dtype=complex)
    for j in range(order):
        shift[(j + 1) % order, j] = 1.0
    omega = np.exp(2j * np.pi / order)
    projectors: list[np.ndarray] = []
    for phase in range(order):
        p = np.zeros_like(shift)
        power = np.eye(order, dtype=complex)
        for r in range(order):
            p += omega ** (-phase * r) * power
            power = power @ shift
        projectors.append(p / order)
    return projectors


def crt_index(a: int, b: int, residue_a: int, residue_b: int) -> int:
    if a < 1 or b < 1:
        raise ValueError("moduli must be positive")
    if gcd(a, b) != 1:
        raise ValueError("moduli must be coprime")
    residue_a %= a
    residue_b %= b
    # x = residue_a + a*t, choose t modulo b.
    t = ((residue_b - residue_a) * pow(a, -1, b)) % b
    return (residue_a + a * t) % (a * b)


def dyadic_odd_index(power_two: int, odd: int, residue_two: int, residue_odd: int) -> int:
    if power_two < 1 or power_two & (power_two - 1):
        raise ValueError("power_two must be a power of two")
    if odd < 1 or odd % 2 == 0:
        raise ValueError("odd must be positive and odd")
    return crt_index(power_two, odd, residue_two, residue_odd)


def verify_refinement(length: int, coarse: int, fine: int) -> float:
    coarse_p = residue_projectors(length, coarse)
    fine_p = residue_projectors(length, fine)
    incidence = refinement_incidence(coarse, fine)
    residual = 0.0
    for r in range(coarse):
        reconstructed = sum(
            (incidence[r, s] * fine_p[s] for s in range(fine)),
            np.zeros((length, length), dtype=int),
        )
        residual = max(residual, float(np.linalg.norm(reconstructed - coarse_p[r])))
    return residual


def verify_crt_factorization(length: int, a: int, b: int) -> float:
    pa = residue_projectors(length, a)
    pb = residue_projectors(length, b)
    pab = residue_projectors(length, a * b)
    residual = 0.0
    for r in range(a):
        for s in range(b):
            j = crt_index(a, b, r, s)
            residual = max(residual, float(np.linalg.norm(pa[r] @ pb[s] - pab[j])))
    return residual
