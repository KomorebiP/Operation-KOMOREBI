"""Continuous diagnostics for RRCT gain and causal-closure sweeps.

The functions in this module summarize measured response surfaces.  They do
not label any point a phase transition or a critical point.  Such an
interpretation requires an experimental protocol, uncertainty estimates, and
independent evidence beyond these descriptive quantities.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]


@dataclass(frozen=True)
class WidestPathClosureDetails:
    """Auditable max-min closure result.

    ``capacity_matrix`` is backed by immutable bytes.  Its off-diagonal entries
    are the full directed widest-path capacities.  Its diagonal is exactly
    zero by convention because self-pairs are excluded from closure strength.
    ``weakest_pair`` uses deterministic lexicographic tie-breaking.
    """

    strength: float
    raw_strength: float
    capacity_matrix: FloatArray
    weakest_pair: tuple[int, int]
    normalization: float

    def __post_init__(self) -> None:
        for name in ("strength", "raw_strength"):
            value = float(getattr(self, name))
            if not np.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and nonnegative")
            object.__setattr__(self, name, value)
        normalization = float(self.normalization)
        if not np.isfinite(normalization) or normalization <= 0.0:
            raise ValueError("normalization must be finite and positive")
        object.__setattr__(self, "normalization", normalization)

        matrix = np.asarray(self.capacity_matrix, dtype=np.float64)
        if (
            matrix.ndim != 2
            or matrix.shape[0] != matrix.shape[1]
            or matrix.shape[0] < 2
        ):
            raise ValueError("capacity_matrix must be square with at least two nodes")
        if not np.all(np.isfinite(matrix)) or np.any(matrix < 0.0):
            raise ValueError("capacity_matrix must be finite and nonnegative")
        matrix = matrix.copy()
        np.fill_diagonal(matrix, 0.0)
        immutable = np.frombuffer(
            np.ascontiguousarray(matrix).tobytes(), dtype=np.float64
        ).reshape(matrix.shape)
        object.__setattr__(self, "capacity_matrix", immutable)

        pair = tuple(int(index) for index in self.weakest_pair)
        if len(pair) != 2 or pair[0] == pair[1] or any(
            index < 0 or index >= matrix.shape[0] for index in pair
        ):
            raise ValueError("weakest_pair must contain two distinct valid indices")
        object.__setattr__(self, "weakest_pair", pair)

    @property
    def normalized_strength(self) -> float:
        """Explicit alias for :attr:`strength`."""

        return self.strength


@dataclass(frozen=True)
class DirectedWidestPathCutCertificate:
    """Finite certificate for a directed widest-path bottleneck.

    Starting at ``source``, ``reachable_set`` contains exactly the vertices
    reachable using only direct edges whose weights are *strictly greater*
    than ``raw_capacity``.  ``target`` is outside that set.  ``cut_edges``
    lists every original directed edge from the reachable side to its
    complement in lexicographic order, including zero-weight edges.  Every
    such edge has weight at most ``raw_capacity``.  These facts certify that
    no source-to-target path can have bottleneck capacity greater than the
    reported value.

    The source/target pair is the lexicographically first weakest ordered pair
    returned by :func:`widest_path_closure_details`.
    """

    source: int
    target: int
    raw_capacity: float
    reachable_set: tuple[int, ...]
    cut_edges: tuple[tuple[int, int, float], ...]
    node_count: int

    def __post_init__(self) -> None:
        node_count = int(self.node_count)
        if node_count < 2 or node_count != self.node_count:
            raise ValueError("node_count must be an integer of at least two")
        object.__setattr__(self, "node_count", node_count)

        source = int(self.source)
        target = int(self.target)
        if (
            source != self.source
            or target != self.target
            or source == target
            or source < 0
            or target < 0
            or source >= node_count
            or target >= node_count
        ):
            raise ValueError("source and target must be distinct valid node indices")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "target", target)

        raw_capacity = float(self.raw_capacity)
        if not np.isfinite(raw_capacity) or raw_capacity < 0.0:
            raise ValueError("raw_capacity must be finite and nonnegative")
        object.__setattr__(self, "raw_capacity", raw_capacity)

        reachable = tuple(int(index) for index in self.reachable_set)
        if (
            reachable != tuple(sorted(set(reachable)))
            or any(index < 0 or index >= node_count for index in reachable)
            or source not in reachable
            or target in reachable
        ):
            raise ValueError(
                "reachable_set must be sorted, unique, valid, contain source, "
                "and exclude target"
            )
        object.__setattr__(self, "reachable_set", reachable)

        parsed_edges: list[tuple[int, int, float]] = []
        for edge in self.cut_edges:
            if len(edge) != 3:
                raise ValueError("every cut edge must be (source, target, weight)")
            edge_source = int(edge[0])
            edge_target = int(edge[1])
            weight = float(edge[2])
            if (
                edge_source != edge[0]
                or edge_target != edge[1]
                or edge_source not in reachable
                or edge_target in reachable
                or edge_source == edge_target
            ):
                raise ValueError("cut edge endpoints do not cross the reported cut")
            if (
                not np.isfinite(weight)
                or weight < 0.0
                or weight > raw_capacity
            ):
                raise ValueError(
                    "cut edge weights must be finite, nonnegative, and no "
                    "greater than raw_capacity"
                )
            parsed_edges.append((edge_source, edge_target, weight))

        parsed = tuple(parsed_edges)
        if parsed != tuple(sorted(parsed, key=lambda item: (item[0], item[1]))):
            raise ValueError("cut_edges must be in lexicographic endpoint order")
        expected_pairs = tuple(
            (edge_source, edge_target)
            for edge_source in reachable
            for edge_target in range(node_count)
            if edge_target not in reachable
        )
        if tuple((edge[0], edge[1]) for edge in parsed) != expected_pairs:
            raise ValueError("cut_edges must list every forward edge exactly once")
        object.__setattr__(self, "cut_edges", parsed)

    @property
    def weakest_pair(self) -> tuple[int, int]:
        """Return the certified weakest ordered pair."""

        return (self.source, self.target)


def _finite_vector(values: ArrayLike, name: str) -> FloatArray:
    """Return a nonempty finite one-dimensional float vector."""

    vector = np.asarray(values, dtype=np.float64)
    if vector.ndim != 1 or vector.size == 0:
        raise ValueError(f"{name} must be a nonempty one-dimensional array")
    if not np.all(np.isfinite(vector)):
        raise ValueError(f"{name} must contain only finite values")
    return vector


def _sorted_gain_series(
    gains: ArrayLike,
    *responses: ArrayLike,
) -> tuple[FloatArray, ...]:
    """Validate paired series and return them in strictly increasing gain order."""

    gain_vector = _finite_vector(gains, "gains")
    response_vectors = tuple(
        _finite_vector(response, f"response[{index}]")
        for index, response in enumerate(responses)
    )
    if any(response.shape != gain_vector.shape for response in response_vectors):
        raise ValueError("every response must have the same shape as gains")
    order = np.argsort(gain_vector, kind="stable")
    sorted_gains = gain_vector[order]
    if sorted_gains.size > 1 and np.any(np.diff(sorted_gains) <= 0.0):
        raise ValueError("gains must be unique")
    return (sorted_gains, *(response[order] for response in response_vectors))


def widest_path_closure_details(
    effects: ArrayLike,
    *,
    normalize: float = 1.0,
) -> WidestPathClosureDetails:
    """Return an auditable directed max-min widest-path closure.

    ``effects[i, j]`` is the nonnegative direct causal effect from node ``i``
    to node ``j``.  The max-min Floyd-Warshall recurrence computes the strongest
    bottleneck path for each ordered pair.  Raw strength is the minimum of
    those path capacities over all off-diagonal ordered pairs; ``strength`` is
    raw strength divided by ``normalize``.  A disconnected directed pair
    therefore makes both strengths zero.  Before normalization, this is the continuous margin for
    strong connectivity: away from exact ties, thresholded edges
    ``effects[i,j] > tau`` form a strongly connected graph exactly when the
    raw closure strength is greater than ``tau``.  Normalization only divides
    this margin and never clips it.

    The returned capacity matrix uses zero on the diagonal as an explicit
    exclusion convention.  The weakest pair is the lexicographically first
    ordered pair attaining raw strength.
    """

    matrix = np.asarray(effects, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("effects must be a square two-dimensional array")
    if matrix.shape[0] < 2:
        raise ValueError("effects must contain at least two nodes")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("effects must contain only finite values")
    if np.any(matrix < 0.0):
        raise ValueError("effects must be nonnegative")
    if not np.isfinite(normalize) or normalize <= 0.0:
        raise ValueError("normalize must be finite and positive")

    internal_capacity = matrix.copy()
    np.fill_diagonal(internal_capacity, np.inf)
    for intermediate in range(internal_capacity.shape[0]):
        through = np.minimum(
            internal_capacity[:, intermediate, None],
            internal_capacity[None, intermediate, :],
        )
        internal_capacity = np.maximum(internal_capacity, through)

    pairs = tuple(
        (source, target)
        for source in range(internal_capacity.shape[0])
        for target in range(internal_capacity.shape[0])
        if source != target
    )
    pair_capacities = np.asarray(
        [internal_capacity[source, target] for source, target in pairs],
        dtype=np.float64,
    )
    weakest_index = int(np.argmin(pair_capacities))
    raw_strength = float(pair_capacities[weakest_index])
    strength = raw_strength / float(normalize)
    if not np.isfinite(strength):
        raise ValueError("normalization produced a nonfinite strength")

    returned_capacity = internal_capacity.copy()
    np.fill_diagonal(returned_capacity, 0.0)
    return WidestPathClosureDetails(
        strength=strength,
        raw_strength=raw_strength,
        capacity_matrix=returned_capacity,
        weakest_pair=pairs[weakest_index],
        normalization=float(normalize),
    )


def widest_path_closure_strength(
    effects: ArrayLike,
    *,
    normalize: float = 1.0,
) -> float:
    """Return normalized widest-path strength from the auditable details API."""

    return widest_path_closure_details(effects, normalize=normalize).strength


def widest_path_cut_certificate(
    effects: ArrayLike,
) -> DirectedWidestPathCutCertificate:
    """Return a deterministic directed cut certificate for closure strength.

    The returned cut is constructed at the raw capacity of the weakest pair.
    Reachability uses the strict threshold ``effects > raw_capacity``.  The
    target is consequently unreachable, and every forward edge across the cut
    is no stronger than the reported capacity.  Together with the widest path
    computed by :func:`widest_path_closure_details`, this supplies matching
    lower- and upper-bound witnesses for the global closure bottleneck.
    """

    details = widest_path_closure_details(effects)
    matrix = np.asarray(effects, dtype=np.float64)
    source, target = details.weakest_pair
    capacity = details.raw_strength

    reachable = {source}
    frontier = [source]
    while frontier:
        current = frontier.pop(0)
        for candidate in range(matrix.shape[0]):
            if (
                candidate != current
                and candidate not in reachable
                and matrix[current, candidate] > capacity
            ):
                reachable.add(candidate)
                frontier.append(candidate)

    reachable_set = tuple(sorted(reachable))
    if target in reachable:
        raise RuntimeError("widest-path cut construction violated its invariant")
    cut_edges = tuple(
        (edge_source, edge_target, float(matrix[edge_source, edge_target]))
        for edge_source in reachable_set
        for edge_target in range(matrix.shape[0])
        if edge_target not in reachable
    )
    return DirectedWidestPathCutCertificate(
        source=source,
        target=target,
        raw_capacity=capacity,
        reachable_set=reachable_set,
        cut_edges=cut_edges,
        node_count=matrix.shape[0],
    )


def interaction_residual(surface: ArrayLike) -> FloatArray:
    """Remove both axis-zero baselines from a two-dimensional response surface.

    For row coordinate ``r`` and column coordinate ``c``, the result is

    ``f(r,c) - f(r,0) - f(0,c) + f(0,0)``.

    Thus the first row and first column are the zero baselines and vanish from
    the returned interaction surface.
    """

    array = np.asarray(surface, dtype=np.float64)
    if array.ndim != 2 or 0 in array.shape:
        raise ValueError("surface must be a nonempty two-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError("surface must contain only finite values")
    residual = array - array[:, [0]] - array[[0], :] + array[0, 0]
    # Enforce exact baseline zeros even when large values would leave a few
    # roundoff bits after cancellation.
    residual[0, :] = 0.0
    residual[:, 0] = 0.0
    return np.asarray(residual, dtype=np.float64)


def hysteresis_area(
    gains: ArrayLike,
    upward: ArrayLike,
    downward: ArrayLike,
    *,
    normalize: bool = True,
) -> float:
    """Integrate the absolute separation between upward and downward ramps.

    Unique gains may be supplied in any order; paired responses are reordered
    with them before trapezoidal integration.  If ``normalize`` is true, area
    is divided by gain span times the combined response range.  Degenerate
    zero-span or zero-range cases safely return zero.
    """

    sorted_gains, sorted_upward, sorted_downward = _sorted_gain_series(
        gains, upward, downward
    )
    separation = np.abs(sorted_upward - sorted_downward)
    if sorted_gains.size < 2:
        area = 0.0
    else:
        widths = np.diff(sorted_gains)
        area = float(
            np.sum(0.5 * widths * (separation[:-1] + separation[1:]))
        )
    if not normalize:
        return area

    gain_span = float(sorted_gains[-1] - sorted_gains[0])
    combined_min = float(min(np.min(sorted_upward), np.min(sorted_downward)))
    combined_max = float(max(np.max(sorted_upward), np.max(sorted_downward)))
    response_range = combined_max - combined_min
    denominator = gain_span * response_range
    if denominator <= 0.0:
        return 0.0
    return area / denominator


def max_slope_interval(
    gains: ArrayLike,
    response: ArrayLike,
) -> tuple[tuple[float, float], float]:
    """Return the interval of greatest absolute finite-difference slope.

    The signed slope is returned with the ordered gain interval.  This is a
    descriptive steepest-interval statistic and deliberately makes no claim
    that the selected interval is critical.
    """

    sorted_gains, sorted_response = _sorted_gain_series(gains, response)
    if sorted_gains.size < 2:
        raise ValueError("at least two unique gains are required")
    slopes = np.diff(sorted_response) / np.diff(sorted_gains)
    index = int(np.argmax(np.abs(slopes)))
    interval = (float(sorted_gains[index]), float(sorted_gains[index + 1]))
    return interval, float(slopes[index])


__all__ = [
    "DirectedWidestPathCutCertificate",
    "WidestPathClosureDetails",
    "hysteresis_area",
    "interaction_residual",
    "max_slope_interval",
    "widest_path_closure_details",
    "widest_path_closure_strength",
    "widest_path_cut_certificate",
]
