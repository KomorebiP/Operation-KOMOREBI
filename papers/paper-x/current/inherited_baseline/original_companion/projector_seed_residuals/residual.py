from __future__ import annotations

from collections import defaultdict
from typing import Hashable, Iterable, Sequence


def _normalize_object(obj: int | Sequence[int], modulus: int) -> int | tuple[int, ...]:
    if isinstance(obj, int):
        return obj % modulus
    return tuple(int(x) % modulus for x in obj)


def partition_by_residual(
    objects: Iterable[int | Sequence[int]], p: int
) -> dict[int | tuple[int, ...], list[int | tuple[int, ...]]]:
    """Partition finite integral coordinates by their unique reduction modulo p."""
    if p < 2:
        raise ValueError("p must be at least two")
    out: dict[int | tuple[int, ...], list[int | tuple[int, ...]]] = defaultdict(list)
    for obj in objects:
        normalized = _normalize_object(obj, p)
        out[normalized].append(obj if isinstance(obj, int) else tuple(int(x) for x in obj))
    return dict(out)


def compatible_residue_tower(residues: Sequence[int], p: int) -> bool:
    """Check x_{m+1} == x_m modulo p^m for m=1,... ."""
    if p < 2:
        raise ValueError("p must be at least two")
    for m in range(1, len(residues)):
        if residues[m] % (p**m) != residues[m - 1] % (p**m):
            return False
    return True


def reconstruct_digits(residues: Sequence[int], p: int) -> list[int]:
    """Recover the first len(residues) p-adic digits of a compatible tower."""
    if not compatible_residue_tower(residues, p):
        raise ValueError("residue tower is not compatible")
    digits: list[int] = []
    for m, residue in enumerate(residues, start=1):
        digits.append((int(residue) // (p ** (m - 1))) % p)
    return digits


def first_separation_depth(a: int, b: int, p: int, max_depth: int = 32) -> int | None:
    """First m >= 1 for which a and b differ modulo p^m."""
    for m in range(1, max_depth + 1):
        if a % (p**m) != b % (p**m):
            return m
    return None


def full_digit_levels(p: int, depth: int, dimension: int = 1) -> list[list[tuple[int, ...]]]:
    """The full p-adic digit forest through a finite depth."""
    if p < 2 or depth < 1 or dimension < 1:
        raise ValueError("invalid p, depth, or dimension")
    levels: list[list[tuple[int, ...]]] = []
    for m in range(1, depth + 1):
        modulus = p**m
        if dimension == 1:
            levels.append([(x,) for x in range(modulus)])
        else:
            current: list[tuple[int, ...]] = [()]
            for _ in range(dimension):
                current = [prefix + (x,) for prefix in current for x in range(modulus)]
            levels.append(current)
    return levels


def positive_depth_perturbation_preserves_root(a: int, correction: int, p: int) -> bool:
    return (a + p * correction) % p == a % p
