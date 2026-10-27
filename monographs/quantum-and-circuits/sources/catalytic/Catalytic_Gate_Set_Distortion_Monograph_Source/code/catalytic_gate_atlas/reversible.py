"""Exact classical reversible experiments: affine gates versus Toffoli."""
from __future__ import annotations

from itertools import combinations

from .algebra import Permutation, perm_compose, perm_identity
from .search import NamedGenerator, breadth_first_distances, defect_distribution, zero_one_distances


def x_gate(n: int, bit: int) -> Permutation:
    return tuple(value ^ (1 << bit) for value in range(1 << n))


def cnot_gate(n: int, control: int, target: int) -> Permutation:
    if control == target:
        raise ValueError("control and target must be distinct")
    output = []
    for value in range(1 << n):
        image = value ^ ((1 << target) if ((value >> control) & 1) else 0)
        output.append(image)
    return tuple(output)


def toffoli_gate(n: int, controls: tuple[int, int], target: int) -> Permutation:
    if target in controls or controls[0] == controls[1]:
        raise ValueError("controls and target must be distinct")
    mask = (1 << controls[0]) | (1 << controls[1])
    output = []
    for value in range(1 << n):
        image = value ^ ((1 << target) if (value & mask) == mask else 0)
        output.append(image)
    return tuple(output)


def affine_generators(n: int, *, entangling_cost: bool = False) -> list[NamedGenerator[Permutation]]:
    generators: list[NamedGenerator[Permutation]] = []
    for bit in range(n):
        generators.append(NamedGenerator(f"X{bit}", x_gate(n, bit), 0 if entangling_cost else 1))
    for control in range(n):
        for target in range(n):
            if control != target:
                generators.append(NamedGenerator(f"CX{control}{target}", cnot_gate(n, control, target), 1))
    return generators


def toffoli_generators(n: int, *, entangling_cost: bool = False) -> list[NamedGenerator[Permutation]]:
    generators = affine_generators(n, entangling_cost=entangling_cost)
    for target in range(n):
        other = [bit for bit in range(n) if bit != target]
        for controls in combinations(other, 2):
            generators.append(NamedGenerator(f"TOF{controls[0]}{controls[1]}>{target}", toffoli_gate(n, controls, target), 1))
    return generators


def exact_affine_toffoli_census(n: int = 3, *, entangling_cost: bool = False) -> dict[str, object]:
    if n > 3:
        raise ValueError("the complete ambient census is intentionally limited to n <= 3")
    identity = perm_identity(1 << n)
    restricted_generators = affine_generators(n, entangling_cost=entangling_cost)
    ambient_generators = toffoli_generators(n, entangling_cost=entangling_cost)
    if entangling_cost:
        restricted = zero_one_distances(identity, restricted_generators, perm_compose)
        ambient = zero_one_distances(identity, ambient_generators, perm_compose)
    else:
        restricted = breadth_first_distances(identity, restricted_generators, perm_compose)
        ambient = breadth_first_distances(identity, ambient_generators, perm_compose)
    distribution = defect_distribution(restricted, ambient)
    return {
        "bits": n,
        "metric": "entangling" if entangling_cost else "total",
        "restricted_group_size": len(restricted),
        "ambient_group_size": len(ambient),
        "restricted_diameter": max(restricted.values()),
        "ambient_diameter": max(ambient.values()),
        "defect_count": sum(distribution.values()),
        "defect_distribution": {f"{a}->{b}": count for (a, b), count in distribution.items()},
        "maximum_defect": max((a - b for a, b in distribution), default=0),
    }
