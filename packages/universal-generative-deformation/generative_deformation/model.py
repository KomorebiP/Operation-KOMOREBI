from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Hashable, Iterable, Mapping, Sequence


JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]


@dataclass(frozen=True, slots=True)
class Direction:
    """One admissible abstract direction from a particular object.

    A direction may represent a tangent vector, rewrite rule, operator,
    parameterized deformation, projection, quotient, coordinate change, or any
    other primitive move declared by the system.  The same name may carry
    different parameters at different vertices.
    """

    name: str
    parameter: JSONValue = None
    cost: float = 1.0
    family: str | None = None
    resolution: float | None = None
    metadata: Mapping[str, JSONValue] = field(default_factory=dict)

    def label(self) -> str:
        if self.parameter is None:
            return self.name
        return f"{self.name}({self.parameter})"


@dataclass(frozen=True, slots=True)
class ValidationResult:
    valid: bool
    reason: str = ""


class DeformationSystem(ABC):
    """Interface for a state-dependent deformation grammar.

    The crucial method is ``directions(state, depth)``.  Each child is queried
    again after it is created, so the outgoing direction space may change from
    vertex to vertex.  This is the executable form of "every direction from
    every direction".
    """

    name: str = "deformation-system"

    @abstractmethod
    def directions(self, state: Any, depth: int) -> Iterable[Direction]:
        """Return every direction exposed by the declared grammar at ``state``.

        Infinite or continuous families should be represented lazily or by a
        certified finite cover at the requested depth.
        """

    @abstractmethod
    def apply(self, state: Any, direction: Direction) -> Any:
        """Apply one direction and return the child object."""

    @abstractmethod
    def canonical_key(self, state: Any) -> Hashable:
        """Return a relation-reduced key used to quotient equivalent paths."""

    def validate(self, state: Any) -> ValidationResult:
        return ValidationResult(True, "")

    def invariants(self, state: Any) -> Mapping[str, JSONValue]:
        return {}

    def serialize_state(self, state: Any) -> JSONValue:
        return repr(state)

    def distance(self, left: Any, right: Any) -> float:
        raise NotImplementedError(f"{type(self).__name__} does not define a metric")


@dataclass(slots=True)
class ForestNode:
    id: int
    key: Hashable
    state: Any
    min_depth: int
    first_parent: int | None
    first_direction: Direction | None
    first_path_id: int
    path_cost: float
    invariants: Mapping[str, JSONValue]


@dataclass(slots=True)
class ForestEdge:
    source: int
    target: int
    direction: Direction
    first_depth: int
    multiplicity: int = 1


@dataclass(slots=True)
class PathRecord:
    id: int
    node_id: int
    depth: int
    parent_path_id: int | None
    direction: Direction | None
    cost: float
    labels: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ExplorationConfig:
    max_depth: int = 5
    max_paths: int = 10000
    max_nodes: int = 10000
    max_edges: int = 50000
    strategy: str = "breadth_first"
    keep_invalid: bool = False
    per_path_direction_limit: int | None = None

    def __post_init__(self) -> None:
        if self.max_depth < 0:
            raise ValueError("max_depth must be nonnegative")
        if min(self.max_paths, self.max_nodes, self.max_edges) < 1:
            raise ValueError("exploration limits must be positive")
        if self.strategy not in {"breadth_first", "lowest_cost"}:
            raise ValueError("strategy must be 'breadth_first' or 'lowest_cost'")


@dataclass(frozen=True, slots=True)
class InteractionRule:
    """Optional multi-input operation for the operadic hyperforest extension."""

    name: str
    arity: int
    cost: float = 1.0
    metadata: Mapping[str, JSONValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.arity < 2:
            raise ValueError("interaction arity must be at least two")


class InteractionSystem(ABC):
    @abstractmethod
    def admissible(self, rule: InteractionRule, states: Sequence[Any]) -> bool:
        ...

    @abstractmethod
    def apply_interaction(self, rule: InteractionRule, states: Sequence[Any]) -> Any:
        ...
