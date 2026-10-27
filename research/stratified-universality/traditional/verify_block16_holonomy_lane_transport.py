from __future__ import annotations

"""Deterministic exact regression for Block 16 holonomy-twisted lane transport.

The suite checks finite permutation realizations and rational cyclic group
algebra identities using only Python integers, with cyclotomic denominators cleared exactly.
It is an implementation regression for selected displayed formulas. It is not
a replacement for the proofs and not an external validation of the theorem.
"""

from dataclasses import dataclass
from itertools import combinations, permutations
from math import gcd
from pathlib import Path
import json
import random
import sys
from typing import Callable, Hashable, Iterable, Sequence


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
GENERATED = ROOT / "generated"
RESULTS.mkdir(exist_ok=True)
GENERATED.mkdir(exist_ok=True)

RESULT_PATH = RESULTS / "block16_holonomy_lane_transport_validation.json"
COUNTS_PATH = GENERATED / "block16_counts.tex"
TABLE_PATH = GENERATED / "block16_validation_table.tex"
SOURCE_PATH = ROOT / "block16_section.tex"

SEED = 20260831

# Filled after the deterministic suite was frozen. A mismatch is a release
# failure because it means the executed validation surface changed.
EXPECTED_COUNTS: dict[str, int] = {
    "group_action_and_orbit_descent": 7780,
    "permutation_intertwiner_basis": 3537,
    "orbital_path_composition": 1212963,
    "selector_controls": 994,
    "equivariant_refinement": 10162,
    "cyclotomic_rational_descent": 109374,
    "source_contract": 13,
}
EXPECTED_TOTAL = 1344823


def remove_stale_outputs() -> None:
    for path in (RESULT_PATH, COUNTS_PATH, TABLE_PATH):
        if path.exists():
            path.unlink()


remove_stale_outputs()


class Ledger:
    def __init__(self) -> None:
        self.counts = {name: 0 for name in EXPECTED_COUNTS}
        self.failures: list[dict[str, str]] = []

    def check(self, condition: bool, label: str, category: str) -> None:
        if category not in self.counts:
            raise KeyError(f"unknown validation category: {category}")
        self.counts[category] += 1
        if not bool(condition):
            self.failures.append({"category": category, "label": label})

    @property
    def total(self) -> int:
        return sum(self.counts.values())


Permutation = tuple[int, ...]
Matrix = list[list[int]]
Element = Hashable


def identity_permutation(n: int) -> Permutation:
    return tuple(range(n))


def compose_permutations(left: Permutation, right: Permutation) -> Permutation:
    """Return left after right."""

    if len(left) != len(right):
        raise ValueError("permutation-size mismatch")
    return tuple(left[right[i]] for i in range(len(left)))


def inverse_permutation(p: Permutation) -> Permutation:
    inverse = [0] * len(p)
    for i, image in enumerate(p):
        inverse[image] = i
    return tuple(inverse)


def permutation_parity(p: Permutation) -> int:
    inversions = 0
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            inversions += p[i] > p[j]
    return inversions % 2


@dataclass(frozen=True)
class FiniteGroup:
    name: str
    elements: tuple[Element, ...]
    identity_index: int
    multiplication: tuple[tuple[int, ...], ...]
    actions: dict[str, tuple[Permutation, ...]]


def make_group(
    name: str,
    elements: Sequence[Element],
    multiply: Callable[[Element, Element], Element],
    identity: Element,
    action_builders: dict[str, Callable[[Element], Permutation]],
) -> FiniteGroup:
    element_tuple = tuple(elements)
    index = {element: i for i, element in enumerate(element_tuple)}
    multiplication = tuple(
        tuple(index[multiply(a, b)] for b in element_tuple) for a in element_tuple
    )
    actions = {
        action_name: tuple(builder(element) for element in element_tuple)
        for action_name, builder in action_builders.items()
    }
    return FiniteGroup(
        name=name,
        elements=element_tuple,
        identity_index=index[identity],
        multiplication=multiplication,
        actions=actions,
    )


def cyclic_group(m: int) -> FiniteGroup:
    if m < 1:
        raise ValueError("cyclic order must be positive")
    action_builders: dict[str, Callable[[Element], Permutation]] = {
        "trivial_1": lambda h: (0,),
        f"regular_{m}": lambda h, m=m: tuple(
            (i + int(h)) % m for i in range(m)
        ),
        f"trivial_{m}": lambda h, m=m: tuple(range(m)),
    }
    proper_divisors = [n for n in range(2, m) if m % n == 0]
    if proper_divisors:
        n = proper_divisors[0]
        action_builders[f"quotient_{n}"] = (
            lambda h, n=n: tuple((i + int(h)) % n for i in range(n))
        )
    if m >= 4 and m % 2 == 0:
        action_builders[f"step2_{m}"] = (
            lambda h, m=m: tuple((i + 2 * int(h)) % m for i in range(m))
        )
    return make_group(
        f"C{m}",
        list(range(m)),
        lambda a, b: (int(a) + int(b)) % m,
        0,
        action_builders,
    )


def dihedral_group(m: int) -> FiniteGroup:
    if m < 2:
        raise ValueError("dihedral polygon size must be at least two")
    elements = [(r, s) for s in (0, 1) for r in range(m)]

    def multiply(a: Element, b: Element) -> Element:
        r, s = a  # type: ignore[misc]
        t, u = b  # type: ignore[misc]
        return ((r + (-1 if s else 1) * t) % m, (s + u) % 2)

    builders: dict[str, Callable[[Element], Permutation]] = {}
    for n in range(1, min(m, 8) + 1):
        if m % n != 0:
            continue
        builders[f"vertices_mod_{n}"] = (
            lambda h, n=n: tuple(
                (int(h[0]) + (-1 if int(h[1]) else 1) * i) % n
                for i in range(n)
            )
        )
    builders[f"two_copies_vertices_{m}"] = (
        lambda h, m=m: tuple(
            copy * m
            + (int(h[0]) + (-1 if int(h[1]) else 1) * i) % m
            for copy in range(2)
            for i in range(m)
        )
    )
    return make_group(f"D{m}", elements, multiply, (0, 0), builders)


def symmetric_group(n: int, even_only: bool = False) -> FiniteGroup:
    all_elements = tuple(permutations(range(n)))
    elements = tuple(p for p in all_elements if not even_only or permutation_parity(p) == 0)
    identity = identity_permutation(n)
    name = f"A{n}" if even_only else f"S{n}"

    subsets_by_size: dict[int, tuple[tuple[int, ...], ...]] = {
        k: tuple(combinations(range(n), k)) for k in range(1, min(3, n) + 1)
    }

    builders: dict[str, Callable[[Element], Permutation]] = {
        f"points_{n}": lambda h, n=n: tuple(int(h[i]) for i in range(n)),  # type: ignore[index]
        "trivial_1": lambda h: (0,),
    }
    for k, subsets in subsets_by_size.items():
        subset_index = {subset: i for i, subset in enumerate(subsets)}
        builders[f"subsets_{n}_{k}"] = (
            lambda h, subsets=subsets, subset_index=subset_index: tuple(
                subset_index[tuple(sorted(int(h[i]) for i in subset))]  # type: ignore[index]
                for subset in subsets
            )
        )
    if not even_only:
        builders["sign_2"] = lambda h: (
            (permutation_parity(h), 1 - permutation_parity(h))  # type: ignore[arg-type]
            if permutation_parity(h) == 1  # type: ignore[arg-type]
            else (0, 1)
        )

    return make_group(
        name,
        elements,
        lambda a, b: compose_permutations(a, b),  # type: ignore[arg-type]
        identity,
        builders,
    )


def klein_four_group() -> FiniteGroup:
    elements = [(a, b) for a in (0, 1) for b in (0, 1)]
    builders: dict[str, Callable[[Element], Permutation]] = {
        "regular_4": lambda h: tuple(
            ((x // 2) ^ int(h[0])) * 2 + ((x % 2) ^ int(h[1]))
            for x in range(4)
        ),
        "first_bit_2": lambda h: (
            int(h[0]),
            1 ^ int(h[0]),
        ),
        "second_bit_2": lambda h: (
            int(h[1]),
            1 ^ int(h[1]),
        ),
        "trivial_2": lambda h: (0, 1),
    }
    return make_group(
        "V4",
        elements,
        lambda a, b: (int(a[0]) ^ int(b[0]), int(a[1]) ^ int(b[1])),  # type: ignore[index]
        (0, 0),
        builders,
    )


def action_size(action: Sequence[Permutation]) -> int:
    if not action:
        raise ValueError("empty action")
    return len(action[0])


def validate_action(group: FiniteGroup, action_name: str, ledger: Ledger) -> None:
    category = "group_action_and_orbit_descent"
    action = group.actions[action_name]
    n = action_size(action)
    identity = identity_permutation(n)
    for element_index, p in enumerate(action):
        ledger.check(
            tuple(sorted(p)) == identity,
            f"{group.name}:{action_name}:permutation:{element_index}",
            category,
        )
        ledger.check(
            compose_permutations(p, inverse_permutation(p)) == identity,
            f"{group.name}:{action_name}:inverse:{element_index}",
            category,
        )
    ledger.check(
        action[group.identity_index] == identity,
        f"{group.name}:{action_name}:identity",
        category,
    )
    for a in range(len(group.elements)):
        for b in range(len(group.elements)):
            product = group.multiplication[a][b]
            ledger.check(
                action[product] == compose_permutations(action[a], action[b]),
                f"{group.name}:{action_name}:hom:{a}:{b}",
                category,
            )


def point_orbits(action: Sequence[Permutation]) -> list[tuple[int, ...]]:
    n = action_size(action)
    unseen = set(range(n))
    orbits: list[tuple[int, ...]] = []
    while unseen:
        seed = min(unseen)
        orbit = tuple(sorted({p[seed] for p in action}))
        unseen.difference_update(orbit)
        orbits.append(orbit)
    return orbits


def pair_orbits(
    target_action: Sequence[Permutation], source_action: Sequence[Permutation]
) -> list[tuple[tuple[int, int], ...]]:
    if len(target_action) != len(source_action):
        raise ValueError("actions must belong to the same group")
    rows = action_size(target_action)
    cols = action_size(source_action)
    unseen = {(a, i) for a in range(rows) for i in range(cols)}
    orbits: list[tuple[tuple[int, int], ...]] = []
    while unseen:
        seed = min(unseen)
        orbit = tuple(
            sorted(
                {
                    (target_action[h][seed[0]], source_action[h][seed[1]])
                    for h in range(len(target_action))
                }
            )
        )
        unseen.difference_update(orbit)
        orbits.append(orbit)
    return orbits


def zero_matrix(rows: int, cols: int) -> Matrix:
    return [[0 for _ in range(cols)] for _ in range(rows)]


def matrix_add(a: Matrix, b: Matrix) -> Matrix:
    if len(a) != len(b) or (a and b and len(a[0]) != len(b[0])):
        raise ValueError("matrix-addition shape mismatch")
    return [[x + y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def matrix_mul(a: Matrix, b: Matrix) -> Matrix:
    rows = len(a)
    middle = len(a[0]) if a else 0
    if len(b) != middle:
        raise ValueError("matrix-multiplication shape mismatch")
    cols = len(b[0]) if b else 0
    out = zero_matrix(rows, cols)
    for r in range(rows):
        for k in range(middle):
            if a[r][k] == 0:
                continue
            for c in range(cols):
                if b[k][c] != 0:
                    out[r][c] += a[r][k] * b[k][c]
    return out


def orbit_indicator(
    orbit: Iterable[tuple[int, int]], rows: int, cols: int
) -> Matrix:
    out = zero_matrix(rows, cols)
    for a, i in orbit:
        out[a][i] = 1
    return out


def invariant_matrix(
    orbits: Sequence[Sequence[tuple[int, int]]],
    rows: int,
    cols: int,
    coefficients: Sequence[int],
) -> Matrix:
    if len(orbits) != len(coefficients):
        raise ValueError("coefficient-count mismatch")
    out = zero_matrix(rows, cols)
    for orbit, coefficient in zip(orbits, coefficients):
        for a, i in orbit:
            out[a][i] = coefficient
    return out


def is_invariant_matrix(
    matrix: Matrix,
    target_action: Sequence[Permutation],
    source_action: Sequence[Permutation],
) -> bool:
    rows = action_size(target_action)
    cols = action_size(source_action)
    if len(matrix) != rows or any(len(row) != cols for row in matrix):
        return False
    for h in range(len(target_action)):
        for a in range(rows):
            for i in range(cols):
                if matrix[target_action[h][a]][source_action[h][i]] != matrix[a][i]:
                    return False
    return True


def select_positions(matrix: Matrix, positions: set[tuple[int, int]]) -> Matrix:
    return [
        [value if (a, i) in positions else 0 for i, value in enumerate(row)]
        for a, row in enumerate(matrix)
    ]


def diagonal_projector(n: int, subset: Iterable[int]) -> Matrix:
    out = zero_matrix(n, n)
    for i in subset:
        out[i][i] = 1
    return out


def conjugate_by_permutation(matrix: Matrix, p: Permutation) -> Matrix:
    n = len(p)
    inverse = inverse_permutation(p)
    return [[matrix[inverse[a]][inverse[i]] for i in range(n)] for a in range(n)]


def assert_orbit_partition(
    universe: set[tuple[int, int]],
    orbits: Sequence[Sequence[tuple[int, int]]],
    label: str,
    ledger: Ledger,
) -> None:
    category = "permutation_intertwiner_basis"
    union: set[tuple[int, int]] = set()
    for index, orbit in enumerate(orbits):
        orbit_set = set(orbit)
        ledger.check(bool(orbit_set), f"{label}:orbit_nonempty:{index}", category)
        ledger.check(
            union.isdisjoint(orbit_set),
            f"{label}:orbit_disjoint:{index}",
            category,
        )
        union.update(orbit_set)
    ledger.check(union == universe, f"{label}:orbit_cover", category)


def validate_orbits_and_intertwiners(
    groups: Sequence[FiniteGroup], ledger: Ledger, rng: random.Random
) -> None:
    for group in groups:
        action_items = sorted(group.actions.items())
        for action_name, action in action_items:
            validate_action(group, action_name, ledger)
            n = action_size(action)
            orbits = point_orbits(action)
            flattened = [point for orbit in orbits for point in orbit]
            ledger.check(
                sorted(flattened) == list(range(n)),
                f"{group.name}:{action_name}:point_orbit_cover",
                "group_action_and_orbit_descent",
            )
            for orbit_index, orbit in enumerate(orbits):
                projector = diagonal_projector(n, orbit)
                for h, permutation in enumerate(action):
                    ledger.check(
                        conjugate_by_permutation(projector, permutation) == projector,
                        f"{group.name}:{action_name}:orbit_projector:{orbit_index}:{h}",
                        "group_action_and_orbit_descent",
                    )
            total_projector = zero_matrix(n, n)
            for orbit in orbits:
                total_projector = matrix_add(total_projector, diagonal_projector(n, orbit))
            ledger.check(
                total_projector == diagonal_projector(n, range(n)),
                f"{group.name}:{action_name}:projector_complete",
                "group_action_and_orbit_descent",
            )

        for target_name, target_action in action_items:
            for source_name, source_action in action_items:
                rows = action_size(target_action)
                cols = action_size(source_action)
                orbits = pair_orbits(target_action, source_action)
                label = f"{group.name}:{target_name}<-{source_name}"
                assert_orbit_partition(
                    {(a, i) for a in range(rows) for i in range(cols)},
                    orbits,
                    label,
                    ledger,
                )

                coefficients = [rng.randint(-7, 7) for _ in orbits]
                matrix = invariant_matrix(orbits, rows, cols, coefficients)
                ledger.check(
                    is_invariant_matrix(matrix, target_action, source_action),
                    f"{label}:random_intertwiner",
                    "permutation_intertwiner_basis",
                )

                reconstructed = zero_matrix(rows, cols)
                for coefficient, orbit in zip(coefficients, orbits):
                    basis = orbit_indicator(orbit, rows, cols)
                    ledger.check(
                        is_invariant_matrix(basis, target_action, source_action),
                        f"{label}:basis_invariant:{orbit[0]}",
                        "permutation_intertwiner_basis",
                    )
                    reconstructed = matrix_add(
                        reconstructed,
                        [[coefficient * value for value in row] for row in basis],
                    )
                ledger.check(
                    reconstructed == matrix,
                    f"{label}:basis_reconstruction",
                    "permutation_intertwiner_basis",
                )

                chosen_orbits = {
                    index for index in range(len(orbits)) if (index + rows + cols) % 2 == 0
                }
                selected_positions = {
                    position
                    for index, orbit in enumerate(orbits)
                    if index in chosen_orbits
                    for position in orbit
                }
                selected = select_positions(matrix, selected_positions)
                ledger.check(
                    is_invariant_matrix(selected, target_action, source_action),
                    f"{label}:orbit_union_selector",
                    "selector_controls",
                )
                residual = [
                    [matrix[a][i] - selected[a][i] for i in range(cols)]
                    for a in range(rows)
                ]
                ledger.check(
                    matrix_add(selected, residual) == matrix,
                    f"{label}:selector_residual_exact",
                    "selector_controls",
                )
                ledger.check(
                    is_invariant_matrix(residual, target_action, source_action),
                    f"{label}:residual_invariant",
                    "selector_controls",
                )

                nontrivial_orbit = next((orbit for orbit in orbits if len(orbit) > 1), None)
                if nontrivial_orbit is not None:
                    endpoint = {nontrivial_orbit[0]}
                    endpoint_matrix = select_positions(
                        invariant_matrix(orbits, rows, cols, [1] * len(orbits)),
                        endpoint,
                    )
                    ledger.check(
                        not is_invariant_matrix(endpoint_matrix, target_action, source_action),
                        f"{label}:noninvariant_endpoint_control",
                        "selector_controls",
                    )


def validate_orbital_composition(
    groups: Sequence[FiniteGroup], ledger: Ledger, rng: random.Random
) -> None:
    for group in groups:
        action_items = sorted(group.actions.items())
        for target_name, target_action in action_items:
            for middle_name, middle_action in action_items:
                for source_name, source_action in action_items:
                    rows = action_size(target_action)
                    middle = action_size(middle_action)
                    cols = action_size(source_action)
                    left_orbits = pair_orbits(target_action, middle_action)
                    right_orbits = pair_orbits(middle_action, source_action)
                    product_orbits = pair_orbits(target_action, source_action)
                    label = (
                        f"{group.name}:{target_name}<-{middle_name}<-{source_name}"
                    )

                    left = invariant_matrix(
                        left_orbits,
                        rows,
                        middle,
                        [rng.randint(-3, 4) for _ in left_orbits],
                    )
                    right = invariant_matrix(
                        right_orbits,
                        middle,
                        cols,
                        [rng.randint(-3, 4) for _ in right_orbits],
                    )
                    product = matrix_mul(left, right)
                    ledger.check(
                        is_invariant_matrix(product, target_action, source_action),
                        f"{label}:random_product_invariant",
                        "orbital_path_composition",
                    )

                    for q_index, q_orbit in enumerate(left_orbits):
                        bq = orbit_indicator(q_orbit, rows, middle)
                        q_set = set(q_orbit)
                        for p_index, p_orbit in enumerate(right_orbits):
                            bp = orbit_indicator(p_orbit, middle, cols)
                            p_set = set(p_orbit)
                            actual = matrix_mul(bq, bp)
                            reconstructed = zero_matrix(rows, cols)
                            for r_index, r_orbit in enumerate(product_orbits):
                                representative = r_orbit[0]
                                coefficient = sum(
                                    1
                                    for j in range(middle)
                                    if (representative[0], j) in q_set
                                    and (j, representative[1]) in p_set
                                )
                                for k, i in r_orbit:
                                    count = sum(
                                        1
                                        for j in range(middle)
                                        if (k, j) in q_set and (j, i) in p_set
                                    )
                                    ledger.check(
                                        count == coefficient,
                                        f"{label}:constant:{q_index}:{p_index}:{r_index}:{k}:{i}",
                                        "orbital_path_composition",
                                    )
                                if coefficient:
                                    basis = orbit_indicator(r_orbit, rows, cols)
                                    reconstructed = matrix_add(
                                        reconstructed,
                                        [
                                            [coefficient * value for value in row]
                                            for row in basis
                                        ],
                                    )
                            ledger.check(
                                reconstructed == actual,
                                f"{label}:basis_product:{q_index}:{p_index}",
                                "orbital_path_composition",
                            )


def product_action_with_trivial_fiber(
    action: Sequence[Permutation], fiber_size: int
) -> tuple[Permutation, ...]:
    n = action_size(action)
    return tuple(
        tuple(p[i] * fiber_size + fiber for i in range(n) for fiber in range(fiber_size))
        for p in action
    )


def validate_equivariant_refinement(
    groups: Sequence[FiniteGroup], ledger: Ledger
) -> None:
    category = "equivariant_refinement"
    for group in groups:
        for action_name, coarse_action in sorted(group.actions.items()):
            coarse_size = action_size(coarse_action)
            for fiber_size in (2, 3):
                fine_action = product_action_with_trivial_fiber(coarse_action, fiber_size)
                fine_size = coarse_size * fiber_size
                rho = tuple(index // fiber_size for index in range(fine_size))
                label = f"{group.name}:{action_name}:fiber{fiber_size}"

                for h in range(len(group.elements)):
                    for fine_index in range(fine_size):
                        ledger.check(
                            rho[fine_action[h][fine_index]]
                            == coarse_action[h][rho[fine_index]],
                            f"{label}:rho_equivariant:{h}:{fine_index}",
                            category,
                        )

                fine_projectors = [
                    diagonal_projector(fine_size, [fine_index])
                    for fine_index in range(fine_size)
                ]
                for coarse_index in range(coarse_size):
                    coarse_on_fine = diagonal_projector(
                        fine_size,
                        [
                            fine_index
                            for fine_index in range(fine_size)
                            if rho[fine_index] == coarse_index
                        ],
                    )
                    summed = zero_matrix(fine_size, fine_size)
                    for fine_index in range(fine_size):
                        if rho[fine_index] == coarse_index:
                            summed = matrix_add(summed, fine_projectors[fine_index])
                    ledger.check(
                        summed == coarse_on_fine,
                        f"{label}:projector_sum:{coarse_index}",
                        category,
                    )

                coarse_orbits = point_orbits(coarse_action)
                fine_orbits = point_orbits(fine_action)
                for coarse_orbit_index, coarse_orbit in enumerate(coarse_orbits):
                    preimage = {
                        fine_index
                        for fine_index in range(fine_size)
                        if rho[fine_index] in coarse_orbit
                    }
                    selected_fine_orbits = [
                        orbit for orbit in fine_orbits if set(orbit).issubset(preimage)
                    ]
                    union = {point for orbit in selected_fine_orbits for point in orbit}
                    ledger.check(
                        union == preimage,
                        f"{label}:orbit_preimage:{coarse_orbit_index}",
                        category,
                    )
                    coarse_orbit_projector = diagonal_projector(fine_size, preimage)
                    fine_orbit_sum = zero_matrix(fine_size, fine_size)
                    for orbit in selected_fine_orbits:
                        fine_orbit_sum = matrix_add(
                            fine_orbit_sum, diagonal_projector(fine_size, orbit)
                        )
                    ledger.check(
                        fine_orbit_sum == coarse_orbit_projector,
                        f"{label}:orbit_projector_refinement:{coarse_orbit_index}",
                        category,
                    )
                    for orbit in selected_fine_orbits:
                        image = {rho[point] for point in orbit}
                        ledger.check(
                            image == set(coarse_orbit),
                            f"{label}:fine_orbit_surjects:{coarse_orbit_index}:{orbit[0]}",
                            category,
                        )


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def mobius(n: int) -> int:
    if n == 1:
        return 1
    prime_count = 0
    remaining = n
    p = 2
    while p * p <= remaining:
        if remaining % p == 0:
            remaining //= p
            prime_count += 1
            if remaining % p == 0:
                return 0
            while remaining % p == 0:
                remaining //= p
        p += 1
    if remaining > 1:
        prime_count += 1
    return -1 if prime_count % 2 else 1


def euler_phi(n: int) -> int:
    return sum(1 for a in range(1, n + 1) if gcd(a, n) == 1)


def ramanujan_sum(q: int, ell: int) -> int:
    common = gcd(q, ell)
    return sum(d * mobius(q // d) for d in divisors(common))


def cyclic_convolution_int(a: Sequence[int], b: Sequence[int]) -> list[int]:
    """Exact cyclic convolution for integer coefficient vectors."""
    if len(a) != len(b):
        raise ValueError("cyclic-convolution size mismatch")
    n = len(a)
    out = [0 for _ in range(n)]
    for i, left in enumerate(a):
        if left == 0:
            continue
        for j, right in enumerate(b):
            if right != 0:
                out[(i + j) % n] += left * right
    return out


def unit_orbits_mod_n(n: int) -> list[tuple[int, ...]]:
    if n == 1:
        return [(0,)]
    units = [a for a in range(n) if gcd(a, n) == 1]
    unseen = set(range(n))
    out: list[tuple[int, ...]] = []
    while unseen:
        seed = min(unseen)
        orbit = tuple(sorted({(a * seed) % n for a in units}))
        unseen.difference_update(orbit)
        out.append(orbit)
    return out


def validate_cyclotomic_descent(ledger: Ledger) -> None:
    category = "cyclotomic_rational_descent"
    moduli = list(range(1, 49)) + [54, 60, 64, 72, 84, 90, 96]
    for n in moduli:
        ds = divisors(n)
        # E_q=(1/n) sum_l c_q(l)g^l.  Clearing the common denominator
        # makes completeness and idempotent orthogonality exact integer tests.
        ramanujan_vectors: dict[int, list[int]] = {
            q: [ramanujan_sum(q, ell) for ell in range(n)] for q in ds
        }
        total = [sum(ramanujan_vectors[q][ell] for q in ds) for ell in range(n)]
        for ell in range(n):
            ledger.check(
                total[ell] == (n if ell == 0 else 0),
                f"N{n}:complete:{ell}",
                category,
            )

        ledger.check(
            sum(euler_phi(q) for q in ds) == n,
            f"N{n}:totient_sum",
            category,
        )
        for q in ds:
            ledger.check(
                ramanujan_vectors[q][0] == euler_phi(q),
                f"N{n}:trace_rank:{q}",
                category,
            )
            for ell in range(n):
                ledger.check(
                    ramanujan_vectors[q][ell]
                    == ramanujan_sum(q, (-ell) % q),
                    f"N{n}:ramanujan_even:{q}:{ell}",
                    category,
                )

        for q in ds:
            for r in ds:
                actual = cyclic_convolution_int(
                    ramanujan_vectors[q], ramanujan_vectors[r]
                )
                for ell in range(n):
                    expected = n * ramanujan_vectors[q][ell] if q == r else 0
                    ledger.check(
                        actual[ell] == expected,
                        f"N{n}:orthogonal:{q}:{r}:{ell}",
                        category,
                    )

        unit_orbits = {frozenset(orbit) for orbit in unit_orbits_mod_n(n)}
        order_classes = {
            frozenset(
                j
                for j in range(n)
                if n // gcd(n, j) == q
            )
            for q in ds
        }
        ledger.check(
            unit_orbits == order_classes,
            f"N{n}:galois_orbits_by_order",
            category,
        )
        ledger.check(
            len(unit_orbits) == len(ds),
            f"N{n}:orbit_count_divisor_count",
            category,
        )


def validate_source_contract(ledger: Ledger) -> None:
    category = "source_contract"
    source = SOURCE_PATH.read_text(encoding="utf-8")
    normalized_source = " ".join(source.split())
    required = [
        "\\label{thm:block16-holonomy-twisted-lane-transport}",
        "\\label{cor:block16-base-fiber-invariant-normal-form}",
        "\\label{thm:block16-orbit-descent}",
        "\\label{thm:block16-permutation-orbital-calculus}",
        "\\label{prop:block16-rational-cyclotomic-orbit-lanes}",
        "matrix local system",
        "simultaneous monodromy image",
        "finest ordinary globally labeled coarsening",
        "endpoint selector",
        "Ramanujan sum",
        "not an external validation record",
        "does not prove convergence for countably infinite lane sums",
    ]
    for phrase in required:
        ledger.check(
            phrase in normalized_source,
            f"source_contains:{phrase}",
            category,
        )
    ledger.check(
        "Nothing in orbit descent turns the factorial step-product into an additive idempotent splitting."
        in normalized_source,
        "source_factorial_boundary",
        category,
    )


def write_outputs(ledger: Ledger, status: str) -> None:
    result = {
        "status": status,
        "seed": SEED,
        "assertions": ledger.total,
        "expected_assertions": EXPECTED_TOTAL,
        "counts": ledger.counts,
        "expected_counts": EXPECTED_COUNTS,
        "failures": ledger.failures,
        "scope": {
            "group_models": [
                "cyclic permutation actions",
                "dihedral permutation actions",
                "Klein four actions",
                "symmetric and alternating actions",
            ],
            "cyclotomic_moduli": list(range(1, 49)) + [54, 60, 64, 72, 84, 90, 96],
            "arithmetic": "exact integer arithmetic with cleared cyclotomic denominators",
            "claim_boundary": "finite implementation regression, not proof or external validation",
        },
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    COUNTS_PATH.write_text(
        "\n".join(
            [
                "% Generated by verify_block16_holonomy_lane_transport.py",
                f"\\newcommand{{\\BlockSixteenValidationAssertions}}{{{ledger.total:,}}}",
                f"\\newcommand{{\\BlockSixteenValidationFailures}}{{{len(ledger.failures):,}}}",
                "",
            ]
        ),
        encoding="utf-8",
    )

    labels = {
        "group_action_and_orbit_descent": "Group actions and object-orbit descent",
        "permutation_intertwiner_basis": "Pair-orbit partitions and intertwiner bases",
        "orbital_path_composition": "Orbital path composition and structure constants",
        "selector_controls": "Compatible selectors and negative controls",
        "equivariant_refinement": "Equivariant refinement and orbit-projector sums",
        "cyclotomic_rational_descent": "Rational cyclotomic orbit projectors",
        "source_contract": "Theorem-source contract",
    }
    rows = [
        "% Generated by verify_block16_holonomy_lane_transport.py",
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Exact finite regression for selected holonomy-twisted lane clauses. The table is an implementation record, not a proof or external validation.}",
        "\\label{tab:block16-validation}",
        "\\begin{tabular}{@{}lr@{}}",
        "\\toprule",
        "Validation family & Exact assertions\\\\",
        "\\midrule",
    ]
    for key in EXPECTED_COUNTS:
        rows.append(f"{labels[key]} & {ledger.counts[key]:,}\\\\")
    rows.extend(
        [
            "\\midrule",
            f"Total selected implementation assertions & {ledger.total:,}\\\\",
            f"Recorded failures & {len(ledger.failures):,}\\\\",
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}",
            "",
        ]
    )
    TABLE_PATH.write_text("\n".join(rows), encoding="utf-8")


def main() -> int:
    ledger = Ledger()
    rng = random.Random(SEED)

    groups: list[FiniteGroup] = [
        *(cyclic_group(m) for m in range(2, 9)),
        dihedral_group(3),
        dihedral_group(4),
        dihedral_group(5),
        klein_four_group(),
        symmetric_group(3),
        symmetric_group(4, even_only=True),
        symmetric_group(4),
    ]

    validate_orbits_and_intertwiners(groups, ledger, rng)
    validate_orbital_composition(groups, ledger, rng)
    validate_equivariant_refinement(groups, ledger)
    validate_cyclotomic_descent(ledger)
    validate_source_contract(ledger)

    if EXPECTED_TOTAL:
        for category, expected in EXPECTED_COUNTS.items():
            if ledger.counts[category] != expected:
                ledger.failures.append(
                    {
                        "category": "release_count_contract",
                        "label": (
                            f"{category}: expected {expected}, observed "
                            f"{ledger.counts[category]}"
                        ),
                    }
                )
        if ledger.total != EXPECTED_TOTAL:
            ledger.failures.append(
                {
                    "category": "release_count_contract",
                    "label": f"total: expected {EXPECTED_TOTAL}, observed {ledger.total}",
                }
            )

    status = "PASS" if not ledger.failures else "FAIL"
    write_outputs(ledger, status)

    print(f"status: {status}")
    print(f"assertions: {ledger.total}")
    print(f"failures: {len(ledger.failures)}")
    for category, count in ledger.counts.items():
        print(f"{category}: {count}")
    if ledger.failures:
        for failure in ledger.failures[:25]:
            print(f"FAIL {failure['category']}: {failure['label']}", file=sys.stderr)
        if len(ledger.failures) > 25:
            print(
                f"... {len(ledger.failures) - 25} additional failures",
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
