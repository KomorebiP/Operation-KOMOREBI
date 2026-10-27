from __future__ import annotations

import itertools
import math
from fractions import Fraction
from typing import Hashable, Iterable, Mapping

import sympy as sp

from .model import DeformationSystem, Direction, JSONValue, ValidationResult


class SequenceTransformSystem(DeformationSystem):
    """Finite exact sequence transforms with relation reduction."""

    name = "sequence-transforms"

    def __init__(self, length: int = 8, value_cap: int = 1_000_000) -> None:
        if length < 2:
            raise ValueError("length must be at least two")
        self.length = length
        self.value_cap = value_cap

    def directions(self, state: tuple[int, ...], depth: int) -> Iterable[Direction]:
        return [
            Direction("difference"),
            Direction("partial_sum"),
            Direction("binomial_transform"),
            Direction("alternating_sign"),
            Direction("reverse"),
        ]

    def apply(self, state: tuple[int, ...], direction: Direction) -> tuple[int, ...]:
        values = tuple(int(value) for value in state)
        if direction.name == "difference":
            return (values[0],) + tuple(values[index] - values[index - 1] for index in range(1, len(values)))
        if direction.name == "partial_sum":
            total = 0
            output: list[int] = []
            for value in values:
                total += value
                output.append(total)
            return tuple(output)
        if direction.name == "binomial_transform":
            output = []
            for n in range(len(values)):
                output.append(sum(math.comb(n, k) * values[k] for k in range(n + 1)))
            return tuple(output)
        if direction.name == "alternating_sign":
            return tuple(((-1) ** index) * value for index, value in enumerate(values))
        if direction.name == "reverse":
            return tuple(reversed(values))
        raise KeyError(direction.name)

    def validate(self, state: tuple[int, ...]) -> ValidationResult:
        if len(state) != self.length:
            return ValidationResult(False, f"sequence length {len(state)} does not equal {self.length}")
        if any(abs(int(value)) > self.value_cap for value in state):
            return ValidationResult(False, "sequence value cap exceeded")
        return ValidationResult(True, "")

    def canonical_key(self, state: tuple[int, ...]) -> Hashable:
        return tuple(int(value) for value in state)

    def invariants(self, state: tuple[int, ...]) -> Mapping[str, JSONValue]:
        values = tuple(int(value) for value in state)
        return {
            "length": len(values),
            "first": values[0],
            "last": values[-1],
            "sum": sum(values),
            "max_absolute": max(abs(value) for value in values),
            "zero_count": sum(value == 0 for value in values),
        }

    def serialize_state(self, state: tuple[int, ...]) -> JSONValue:
        return list(int(value) for value in state)

    def distance(self, left: tuple[int, ...], right: tuple[int, ...]) -> float:
        return float(sum(abs(int(a) - int(b)) for a, b in zip(left, right)))


class GaussianFamilySystem(DeformationSystem):
    """Exact deformations of one dimensional Gaussian parameter pairs."""

    name = "gaussian-family"

    def directions(self, state: tuple[Fraction, Fraction], depth: int) -> Iterable[Direction]:
        mean, variance = state
        directions = [
            Direction("shift_plus_one"),
            Direction("shift_minus_one"),
            Direction("reflect"),
            Direction("convolve_unit"),
            Direction("center"),
            Direction("scale_two"),
        ]
        if variance != 1 or mean != 0:
            directions.append(Direction("standardize"))
        return directions

    def apply(
        self, state: tuple[Fraction, Fraction], direction: Direction
    ) -> tuple[Fraction, Fraction]:
        mean, variance = Fraction(state[0]), Fraction(state[1])
        if direction.name == "shift_plus_one":
            return mean + 1, variance
        if direction.name == "shift_minus_one":
            return mean - 1, variance
        if direction.name == "reflect":
            return -mean, variance
        if direction.name == "convolve_unit":
            return mean, variance + 1
        if direction.name == "center":
            return Fraction(0), variance
        if direction.name == "scale_two":
            return 2 * mean, 4 * variance
        if direction.name == "standardize":
            return Fraction(0), Fraction(1)
        raise KeyError(direction.name)

    def validate(self, state: tuple[Fraction, Fraction]) -> ValidationResult:
        mean, variance = Fraction(state[0]), Fraction(state[1])
        if variance <= 0:
            return ValidationResult(False, "variance must be positive")
        if abs(mean) > 64 or variance > 256:
            return ValidationResult(False, "parameter cap exceeded")
        return ValidationResult(True, "")

    def canonical_key(self, state: tuple[Fraction, Fraction]) -> Hashable:
        mean, variance = Fraction(state[0]), Fraction(state[1])
        return mean.numerator, mean.denominator, variance.numerator, variance.denominator

    def invariants(self, state: tuple[Fraction, Fraction]) -> Mapping[str, JSONValue]:
        mean, variance = Fraction(state[0]), Fraction(state[1])
        entropy = 0.5 * math.log(2 * math.pi * math.e * float(variance))
        return {
            "mean": str(mean),
            "variance": str(variance),
            "standard_deviation": math.sqrt(float(variance)),
            "differential_entropy": entropy,
            "centered": mean == 0,
        }

    def serialize_state(self, state: tuple[Fraction, Fraction]) -> JSONValue:
        mean, variance = Fraction(state[0]), Fraction(state[1])
        return {"mean": str(mean), "variance": str(variance)}

    def distance(
        self,
        left: tuple[Fraction, Fraction],
        right: tuple[Fraction, Fraction],
    ) -> float:
        return math.hypot(float(left[0] - right[0]), float(left[1] - right[1]))


class QubitGateSystem(DeformationSystem):
    """Exact projective qubit orbit represented by Bloch-axis states.

    The fixed Clifford grammar generated by H, S, X, and Z preserves the six
    Pauli eigenstates.  Global phase has already been quotiented out, so the
    state is the exact Bloch vector (x, y, z) with one coordinate equal to
    plus or minus one and the other two zero.
    """

    name = "qubit-gates"

    def directions(self, state: tuple[int, int, int], depth: int) -> Iterable[Direction]:
        return [Direction(name, cost=1.0) for name in ("H", "S", "X", "Z")]

    def apply(self, state: tuple[int, int, int], direction: Direction) -> tuple[int, int, int]:
        x, y, z = (int(value) for value in state)
        if direction.name == "X":
            return x, -y, -z
        if direction.name == "Z":
            return -x, -y, z
        if direction.name == "H":
            return z, -y, x
        if direction.name == "S":
            return -y, x, z
        raise KeyError(direction.name)

    def validate(self, state: tuple[int, int, int]) -> ValidationResult:
        values = tuple(int(value) for value in state)
        if len(values) != 3 or sum(value * value for value in values) != 1:
            return ValidationResult(False, "state is not one of the six projective Pauli eigenstates")
        return ValidationResult(True, "")

    def canonical_key(self, state: tuple[int, int, int]) -> Hashable:
        return tuple(int(value) for value in state)

    def bloch(self, state: tuple[int, int, int]) -> tuple[float, float, float]:
        return tuple(float(value) for value in state)  # type: ignore[return-value]

    def invariants(self, state: tuple[int, int, int]) -> Mapping[str, JSONValue]:
        x, y, z = self.bloch(state)
        return {"bloch_x": x, "bloch_y": y, "bloch_z": z, "purity": 1.0}

    def serialize_state(self, state: tuple[int, int, int]) -> JSONValue:
        x, y, z = (int(value) for value in state)
        labels = {
            (0, 0, 1): "|0>",
            (0, 0, -1): "|1>",
            (1, 0, 0): "|+>",
            (-1, 0, 0): "|->",
            (0, 1, 0): "|+i>",
            (0, -1, 0): "|-i>",
        }
        return {"label": labels[(x, y, z)], "bloch": [x, y, z]}

    def distance(self, left: tuple[int, int, int], right: tuple[int, int, int]) -> float:
        dot = sum(int(a) * int(b) for a, b in zip(left, right))
        overlap = math.sqrt(max(0.0, (1.0 + dot) / 2.0))
        return math.acos(min(1.0, max(0.0, overlap)))


MatrixState = tuple[tuple[int, int], tuple[int, int]]


def _matmul(left: MatrixState, right: MatrixState) -> MatrixState:
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


def _matadd(left: MatrixState, right: MatrixState) -> MatrixState:
    return tuple(
        tuple(left[i][j] + right[i][j] for j in range(2)) for i in range(2)
    )  # type: ignore[return-value]


def _matsub(left: MatrixState, right: MatrixState) -> MatrixState:
    return tuple(
        tuple(left[i][j] - right[i][j] for j in range(2)) for i in range(2)
    )  # type: ignore[return-value]


class MatrixDeformationSystem(DeformationSystem):
    name = "matrix-deformation"

    def __init__(self, entry_cap: int = 512) -> None:
        self.entry_cap = entry_cap
        self.swap: MatrixState = ((0, 1), (1, 0))
        self.j: MatrixState = ((0, -1), (1, 0))

    def directions(self, state: MatrixState, depth: int) -> Iterable[Direction]:
        return [
            Direction("transpose"),
            Direction("negate"),
            Direction("square"),
            Direction("conjugate_swap"),
            Direction("symmetrize"),
            Direction("commutator_J"),
            Direction("adjugate"),
        ]

    def apply(self, state: MatrixState, direction: Direction) -> MatrixState:
        a, b = state[0]
        c, d = state[1]
        if direction.name == "transpose":
            return ((a, c), (b, d))
        if direction.name == "negate":
            return ((-a, -b), (-c, -d))
        if direction.name == "square":
            return _matmul(state, state)
        if direction.name == "conjugate_swap":
            return _matmul(_matmul(self.swap, state), self.swap)
        if direction.name == "symmetrize":
            return _matadd(state, ((a, c), (b, d)))
        if direction.name == "commutator_J":
            return _matsub(_matmul(self.j, state), _matmul(state, self.j))
        if direction.name == "adjugate":
            return ((d, -b), (-c, a))
        raise KeyError(direction.name)

    def validate(self, state: MatrixState) -> ValidationResult:
        if len(state) != 2 or any(len(row) != 2 for row in state):
            return ValidationResult(False, "state is not a 2 by 2 matrix")
        if any(abs(int(value)) > self.entry_cap for row in state for value in row):
            return ValidationResult(False, "matrix entry cap exceeded")
        return ValidationResult(True, "")

    def canonical_key(self, state: MatrixState) -> Hashable:
        return tuple(int(value) for row in state for value in row)

    def invariants(self, state: MatrixState) -> Mapping[str, JSONValue]:
        a, b = state[0]
        c, d = state[1]
        determinant = a * d - b * c
        return {
            "trace": a + d,
            "determinant": determinant,
            "rank": 2 if determinant != 0 else (1 if any(value != 0 for row in state for value in row) else 0),
            "symmetric": b == c,
            "frobenius_squared": sum(value * value for row in state for value in row),
        }

    def serialize_state(self, state: MatrixState) -> JSONValue:
        return [list(state[0]), list(state[1])]

    def distance(self, left: MatrixState, right: MatrixState) -> float:
        return math.sqrt(sum((left[i][j] - right[i][j]) ** 2 for i in range(2) for j in range(2)))


Point = tuple[Fraction, Fraction]
ShapeState = tuple[Point, ...]


class AffineShapeSystem(DeformationSystem):
    """Exact affine deformations of a finite point configuration."""

    name = "affine-shape"

    def __init__(self, coordinate_cap: int = 32) -> None:
        self.coordinate_cap = coordinate_cap

    def directions(self, state: ShapeState, depth: int) -> Iterable[Direction]:
        return [
            Direction("rotate_90"),
            Direction("reflect_x"),
            Direction("shear_x"),
            Direction("scale_two"),
            Direction("translate_x"),
            Direction("translate_y"),
        ]

    @staticmethod
    def _map(state: ShapeState, transform: object) -> ShapeState:
        return tuple(transform(point) for point in state)  # type: ignore[misc]

    def apply(self, state: ShapeState, direction: Direction) -> ShapeState:
        if direction.name == "rotate_90":
            return self._map(state, lambda p: (-p[1], p[0]))
        if direction.name == "reflect_x":
            return self._map(state, lambda p: (p[0], -p[1]))
        if direction.name == "shear_x":
            return self._map(state, lambda p: (p[0] + p[1], p[1]))
        if direction.name == "scale_two":
            return self._map(state, lambda p: (2 * p[0], 2 * p[1]))
        if direction.name == "translate_x":
            return self._map(state, lambda p: (p[0] + 1, p[1]))
        if direction.name == "translate_y":
            return self._map(state, lambda p: (p[0], p[1] + 1))
        raise KeyError(direction.name)

    def validate(self, state: ShapeState) -> ValidationResult:
        if len(state) < 3:
            return ValidationResult(False, "shape requires at least three points")
        for x, y in state:
            if abs(x) > self.coordinate_cap or abs(y) > self.coordinate_cap:
                return ValidationResult(False, "coordinate cap exceeded")
        return ValidationResult(True, "")

    def canonical_key(self, state: ShapeState) -> Hashable:
        # Vertex labels are not part of the geometric object in this realization.
        return tuple(sorted((p[0].numerator, p[0].denominator, p[1].numerator, p[1].denominator) for p in state))

    @staticmethod
    def _signed_area(state: ShapeState) -> Fraction:
        total = Fraction(0)
        for index, point in enumerate(state):
            nxt = state[(index + 1) % len(state)]
            total += point[0] * nxt[1] - point[1] * nxt[0]
        return total / 2

    def invariants(self, state: ShapeState) -> Mapping[str, JSONValue]:
        count = Fraction(len(state))
        centroid_x = sum(point[0] for point in state) / count
        centroid_y = sum(point[1] for point in state) / count
        return {
            "point_count": len(state),
            "signed_area": str(self._signed_area(state)),
            "centroid_x": str(centroid_x),
            "centroid_y": str(centroid_y),
        }

    def serialize_state(self, state: ShapeState) -> JSONValue:
        return [[str(point[0]), str(point[1])] for point in state]

    def distance(self, left: ShapeState, right: ShapeState) -> float:
        left_sorted = sorted(left)
        right_sorted = sorted(right)
        if len(left_sorted) != len(right_sorted):
            return float("inf")
        return math.sqrt(
            sum(float((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) for a, b in zip(left_sorted, right_sorted))
        )


GraphState = tuple[tuple[int, ...], ...]


def _graph_edges(state: GraphState) -> list[tuple[int, int]]:
    return [(i, j) for i in range(len(state)) for j in range(i + 1, len(state)) if state[i][j]]


def _graph_from_edges(node_count: int, edges: Iterable[tuple[int, int]]) -> GraphState:
    matrix = [[0 for _ in range(node_count)] for _ in range(node_count)]
    for left, right in edges:
        if left == right:
            continue
        matrix[left][right] = 1
        matrix[right][left] = 1
    return tuple(tuple(row) for row in matrix)


class GraphDeformationSystem(DeformationSystem):
    """Small unlabeled graph deformations with exact brute force canonicalization."""

    name = "graph-deformation"

    def __init__(self, node_cap: int = 6) -> None:
        self.node_cap = node_cap

    def directions(self, state: GraphState, depth: int) -> Iterable[Direction]:
        node_count = len(state)
        edge_count = len(_graph_edges(state))
        directions = [Direction("complement"), Direction("relabel_reverse")]
        if node_count < self.node_cap:
            directions.append(Direction("add_leaf"))
            if edge_count:
                directions.append(Direction("subdivide_first_edge"))
        if 0 < edge_count <= self.node_cap:
            directions.append(Direction("line_graph"))
        return directions

    def apply(self, state: GraphState, direction: Direction) -> GraphState:
        node_count = len(state)
        edges = _graph_edges(state)
        if direction.name == "complement":
            return _graph_from_edges(
                node_count,
                [(i, j) for i in range(node_count) for j in range(i + 1, node_count) if not state[i][j]],
            )
        if direction.name == "relabel_reverse":
            permutation = tuple(reversed(range(node_count)))
            return tuple(tuple(state[permutation[i]][permutation[j]] for j in range(node_count)) for i in range(node_count))
        if direction.name == "add_leaf":
            return _graph_from_edges(node_count + 1, edges + [(0, node_count)])
        if direction.name == "subdivide_first_edge":
            if not edges:
                raise ValueError("graph has no edge to subdivide")
            first = edges[0]
            remaining = [edge for edge in edges if edge != first]
            new_node = node_count
            remaining.extend([(first[0], new_node), (new_node, first[1])])
            return _graph_from_edges(node_count + 1, remaining)
        if direction.name == "line_graph":
            if not edges:
                raise ValueError("line graph of edgeless graph is omitted")
            line_edges = []
            for i, left_edge in enumerate(edges):
                for j, right_edge in enumerate(edges[i + 1 :], start=i + 1):
                    if set(left_edge) & set(right_edge):
                        line_edges.append((i, j))
            return _graph_from_edges(len(edges), line_edges)
        raise KeyError(direction.name)

    def validate(self, state: GraphState) -> ValidationResult:
        node_count = len(state)
        if not 1 <= node_count <= self.node_cap:
            return ValidationResult(False, "graph node cap exceeded")
        if any(len(row) != node_count for row in state):
            return ValidationResult(False, "adjacency matrix is not square")
        for i in range(node_count):
            if state[i][i] != 0:
                return ValidationResult(False, "loops are not allowed")
            for j in range(node_count):
                if state[i][j] not in (0, 1) or state[i][j] != state[j][i]:
                    return ValidationResult(False, "adjacency matrix is not a simple undirected graph")
        return ValidationResult(True, "")

    def canonical_key(self, state: GraphState) -> Hashable:
        node_count = len(state)
        candidates = []
        for permutation in itertools.permutations(range(node_count)):
            candidates.append(tuple(state[permutation[i]][permutation[j]] for i in range(node_count) for j in range(node_count)))
        return node_count, min(candidates)

    @staticmethod
    def _component_count(state: GraphState) -> int:
        node_count = len(state)
        seen: set[int] = set()
        components = 0
        for root in range(node_count):
            if root in seen:
                continue
            components += 1
            stack = [root]
            seen.add(root)
            while stack:
                node = stack.pop()
                for neighbor, connected in enumerate(state[node]):
                    if connected and neighbor not in seen:
                        seen.add(neighbor)
                        stack.append(neighbor)
        return components

    def invariants(self, state: GraphState) -> Mapping[str, JSONValue]:
        degrees = sorted(sum(row) for row in state)
        return {
            "nodes": len(state),
            "edges": len(_graph_edges(state)),
            "degree_sequence": degrees,
            "components": self._component_count(state),
        }

    def serialize_state(self, state: GraphState) -> JSONValue:
        return [list(row) for row in state]

    def distance(self, left: GraphState, right: GraphState) -> float:
        if len(left) != len(right):
            return float(abs(len(left) - len(right)) + max(len(left), len(right)))
        return float(sum(abs(left[i][j] - right[i][j]) for i in range(len(left)) for j in range(len(left))) / 2)


class CongruenceLiftSystem(DeformationSystem):
    """Exact finite level lifting tree for simple polynomial congruences."""

    name = "congruence-lift"

    def __init__(self, prime: int, equation: str = "square_one", depth_cap: int = 8) -> None:
        if prime < 2:
            raise ValueError("prime must be at least two")
        if equation not in {"square_one", "square_zero"}:
            raise ValueError("unsupported equation")
        self.prime = prime
        self.equation = equation
        self.depth_cap = depth_cap

    def polynomial(self, value: int) -> int:
        return value * value - 1 if self.equation == "square_one" else value * value

    def residual_seeds(self) -> list[tuple[int, int]]:
        return [(1, value) for value in range(self.prime) if self.polynomial(value) % self.prime == 0]

    def directions(self, state: tuple[int, int], depth: int) -> Iterable[Direction]:
        level, residue = state
        if level >= self.depth_cap:
            return []
        modulus = self.prime**level
        next_modulus = modulus * self.prime
        directions = []
        for digit in range(self.prime):
            candidate = residue + digit * modulus
            if self.polynomial(candidate) % next_modulus == 0:
                directions.append(Direction("lift_digit", digit, metadata={"next_modulus": next_modulus}))
        return directions

    def apply(self, state: tuple[int, int], direction: Direction) -> tuple[int, int]:
        level, residue = state
        if direction.name != "lift_digit":
            raise KeyError(direction.name)
        digit = int(direction.parameter)
        return level + 1, residue + digit * (self.prime**level)

    def validate(self, state: tuple[int, int]) -> ValidationResult:
        level, residue = int(state[0]), int(state[1])
        if not 1 <= level <= self.depth_cap:
            return ValidationResult(False, "invalid congruence level")
        modulus = self.prime**level
        if not 0 <= residue < modulus:
            return ValidationResult(False, "residue is outside canonical range")
        if self.polynomial(residue) % modulus != 0:
            return ValidationResult(False, "residue does not solve the congruence")
        return ValidationResult(True, "")

    def canonical_key(self, state: tuple[int, int]) -> Hashable:
        return int(state[0]), int(state[1])

    def invariants(self, state: tuple[int, int]) -> Mapping[str, JSONValue]:
        level, residue = int(state[0]), int(state[1])
        modulus = self.prime**level
        derivative_mod_prime = (2 * residue) % self.prime
        return {
            "level": level,
            "modulus": modulus,
            "residue": residue,
            "simple_root": derivative_mod_prime != 0,
        }

    def serialize_state(self, state: tuple[int, int]) -> JSONValue:
        level, residue = int(state[0]), int(state[1])
        return {"level": level, "modulus": self.prime**level, "residue": residue}

    def distance(self, left: tuple[int, int], right: tuple[int, int]) -> float:
        return float(abs(left[1] / (self.prime**left[0]) - right[1] / (self.prime**right[0])))


def path_graph(node_count: int) -> GraphState:
    if node_count < 1:
        raise ValueError("node_count must be positive")
    return _graph_from_edges(node_count, [(index, index + 1) for index in range(node_count - 1)])


def triangle_seed() -> ShapeState:
    return (
        (Fraction(0), Fraction(0)),
        (Fraction(2), Fraction(0)),
        (Fraction(1), Fraction(3, 2)),
    )
