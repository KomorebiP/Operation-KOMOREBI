from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from math import isfinite
from typing import Any, Iterable, Mapping, Sequence


class EvidenceKind(str, Enum):
    FORMAL_PROOF = "formal_proof"
    ASSUMPTION = "assumption"
    EXACT_COMPUTATION = "exact_computation"
    NUMERICAL_EVIDENCE = "numerical_evidence"
    CONJECTURE = "conjecture"
    EXTERNAL_RESULT = "external_result"
    COUNTEREXAMPLE = "counterexample"
    INTERPRETATION = "interpretation"


class NodeKind(str, Enum):
    PREMISE = "premise"
    AXIOM = "axiom"
    EXTERNAL_RESULT = "external_result"
    DEFINITION = "definition"
    CLAIM = "claim"
    LEMMA = "lemma"
    THEOREM = "theorem"
    EXAMPLE = "example"
    COMPUTATION = "computation"
    BOUNDARY_CASE = "boundary_case"
    FAILED_ROUTE = "failed_route"
    CONJECTURE = "conjecture"
    COUNTEREXAMPLE = "counterexample"


LEAF_KINDS = frozenset(
    {
        NodeKind.PREMISE,
        NodeKind.AXIOM,
        NodeKind.EXTERNAL_RESULT,
    }
)


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    id: str
    kind: EvidenceKind
    source: str
    scope: str = ""
    certifies: bool = False
    note: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("evidence id must be nonempty")
        if type(self.certifies) is not bool:
            raise ValueError("certifies must be a boolean")
        if not self.source.strip():
            raise ValueError("evidence source must be nonempty")


@dataclass(frozen=True, slots=True)
class ValueVector:
    verification: float = 0.0
    discovery: float = 0.0
    meaning: float = 0.0
    bridge: float = 0.0
    auditability: float = 0.0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            numeric = float(value)
            if not isfinite(numeric) or numeric < 0:
                raise ValueError(f"{name} value must be finite and nonnegative")

    def total(self) -> float:
        return float(sum(asdict(self).values()))

    def as_dict(self) -> dict[str, float]:
        return {name: float(value) for name, value in asdict(self).items()}

    def __add__(self, other: "ValueVector") -> "ValueVector":
        return ValueVector(
            verification=self.verification + other.verification,
            discovery=self.discovery + other.discovery,
            meaning=self.meaning + other.meaning,
            bridge=self.bridge + other.bridge,
            auditability=self.auditability + other.auditability,
        )

    def __sub__(self, other: "ValueVector") -> "ValueVector":
        values = {
            name: max(0.0, self.as_dict()[name] - other.as_dict()[name])
            for name in self.as_dict()
        }
        return ValueVector(**values)


@dataclass(frozen=True, slots=True)
class CostVector:
    storage: float = 0.0
    audit: float = 0.0
    recovery: float = 0.0
    cognitive: float = 0.0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            numeric = float(value)
            if not isfinite(numeric) or numeric < 0:
                raise ValueError(f"{name} cost must be finite and nonnegative")

    def total(self) -> float:
        return float(sum(asdict(self).values()))

    def as_dict(self) -> dict[str, float]:
        return {name: float(value) for name, value in asdict(self).items()}


@dataclass(frozen=True, slots=True)
class ClaimNode:
    id: str
    label: str
    kind: NodeKind = NodeKind.CLAIM
    values: ValueVector = field(default_factory=ValueVector)
    costs: CostVector = field(default_factory=CostVector)
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("node id must be nonempty")
        if not self.label.strip():
            raise ValueError("node label must be nonempty")


@dataclass(frozen=True, slots=True)
class Justification:
    id: str
    premises: tuple[str, ...]
    conclusion: str
    rule: str
    certified: bool = True
    evidence_ids: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("justification id must be nonempty")
        if type(self.certified) is not bool:
            raise ValueError("certified must be a boolean")
        if not self.conclusion.strip():
            raise ValueError("justification conclusion must be nonempty")
        if not self.rule.strip():
            raise ValueError("justification rule must be nonempty")
        if len(set(self.premises)) != len(self.premises):
            raise ValueError(f"justification {self.id} repeats a premise")
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError(f"justification {self.id} repeats an evidence id")


class ProofField:
    """Finite typed acyclic justification hypergraph.

    A justification is conjunctive in its premise set. Multiple justifications
    with the same conclusion are alternative derivations. The certified
    subfield contains only justifications marked as certified.
    """

    def __init__(
        self,
        nodes: Sequence[ClaimNode],
        justifications: Sequence[Justification],
        *,
        premises: Iterable[str] = (),
        targets: Iterable[str] = (),
        evidence: Sequence[EvidenceRecord] = (),
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.nodes: dict[str, ClaimNode] = {}
        for node in nodes:
            if node.id in self.nodes:
                raise ValueError(f"duplicate node id: {node.id}")
            self.nodes[node.id] = node

        self.evidence: dict[str, EvidenceRecord] = {}
        for record in evidence:
            if record.id in self.evidence:
                raise ValueError(f"duplicate evidence id: {record.id}")
            self.evidence[record.id] = record

        self.justifications: dict[str, Justification] = {}
        for justification in justifications:
            if justification.id in self.justifications:
                raise ValueError(f"duplicate justification id: {justification.id}")
            self.justifications[justification.id] = justification

        self.premises = frozenset(premises)
        self.targets = frozenset(targets)
        self.metadata = dict(metadata or {})
        self._validate_references()
        self._topological_order = self._compute_topological_order()

    def _validate_references(self) -> None:
        unknown_premises = self.premises.difference(self.nodes)
        if unknown_premises:
            raise ValueError(f"unknown premises: {sorted(unknown_premises)}")
        unknown_targets = self.targets.difference(self.nodes)
        if unknown_targets:
            raise ValueError(f"unknown targets: {sorted(unknown_targets)}")
        for node_id in self.premises:
            if self.nodes[node_id].kind not in LEAF_KINDS:
                raise ValueError(
                    f"required premise {node_id} must have a leaf node kind"
                )
        for justification in self.justifications.values():
            if justification.conclusion not in self.nodes:
                raise ValueError(
                    f"justification {justification.id} has unknown conclusion "
                    f"{justification.conclusion}"
                )
            for premise in justification.premises:
                if premise not in self.nodes:
                    raise ValueError(
                        f"justification {justification.id} has unknown premise {premise}"
                    )
            for evidence_id in justification.evidence_ids:
                if evidence_id not in self.evidence:
                    raise ValueError(
                        f"justification {justification.id} cites unknown evidence "
                        f"{evidence_id}"
                    )

    def _compute_topological_order(self) -> tuple[str, ...]:
        indegree = {node_id: 0 for node_id in self.nodes}
        children: dict[str, set[str]] = {node_id: set() for node_id in self.nodes}
        for justification in self.justifications.values():
            for premise in justification.premises:
                if justification.conclusion not in children[premise]:
                    children[premise].add(justification.conclusion)
                    indegree[justification.conclusion] += 1
        queue = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
        order: list[str] = []
        while queue:
            node_id = queue.pop(0)
            order.append(node_id)
            for child in sorted(children[node_id]):
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)
                    queue.sort()
        if len(order) != len(self.nodes):
            raise ValueError("proof field contains a directed dependency cycle")
        return tuple(order)

    @property
    def topological_order(self) -> tuple[str, ...]:
        return self._topological_order

    def incoming(
        self,
        node_id: str,
        *,
        certified_only: bool = False,
    ) -> tuple[Justification, ...]:
        if node_id not in self.nodes:
            raise KeyError(node_id)
        records = [
            justification
            for justification in self.justifications.values()
            if justification.conclusion == node_id
            and (justification.certified or not certified_only)
        ]
        return tuple(sorted(records, key=lambda item: item.id))

    def outgoing(
        self,
        node_id: str,
        *,
        certified_only: bool = False,
    ) -> tuple[Justification, ...]:
        if node_id not in self.nodes:
            raise KeyError(node_id)
        records = [
            justification
            for justification in self.justifications.values()
            if node_id in justification.premises
            and (justification.certified or not certified_only)
        ]
        return tuple(sorted(records, key=lambda item: item.id))

    def is_admissible_leaf(self, node_id: str) -> bool:
        if node_id not in self.nodes:
            raise KeyError(node_id)
        return node_id in self.premises or self.nodes[node_id].kind in LEAF_KINDS

    def dependency_edges(self, *, certified_only: bool = False) -> tuple[tuple[str, str], ...]:
        edges = {
            (premise, justification.conclusion)
            for justification in self.justifications.values()
            if justification.certified or not certified_only
            for premise in justification.premises
        }
        return tuple(sorted(edges))

    def descendants(
        self,
        starts: Iterable[str],
        *,
        certified_only: bool = False,
        include_starts: bool = True,
    ) -> frozenset[str]:
        start_set = set(starts)
        unknown = start_set.difference(self.nodes)
        if unknown:
            raise KeyError(sorted(unknown)[0])
        adjacency: dict[str, set[str]] = {node_id: set() for node_id in self.nodes}
        for left, right in self.dependency_edges(certified_only=certified_only):
            adjacency[left].add(right)
        seen: set[str] = set()
        stack = list(start_set)
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            stack.extend(adjacency[node_id].difference(seen))
        if not include_starts:
            seen.difference_update(start_set)
        return frozenset(seen)

    def ancestors(
        self,
        starts: Iterable[str],
        *,
        certified_only: bool = False,
        include_starts: bool = True,
    ) -> frozenset[str]:
        start_set = set(starts)
        unknown = start_set.difference(self.nodes)
        if unknown:
            raise KeyError(sorted(unknown)[0])
        reverse: dict[str, set[str]] = {node_id: set() for node_id in self.nodes}
        for left, right in self.dependency_edges(certified_only=certified_only):
            reverse[right].add(left)
        seen: set[str] = set()
        stack = list(start_set)
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            stack.extend(reverse[node_id].difference(seen))
        if not include_starts:
            seen.difference_update(start_set)
        return frozenset(seen)

    def derive(
        self,
        *,
        selected_nodes: Iterable[str] | None = None,
        selected_justifications: Iterable[str] | None = None,
        certified_only: bool = True,
    ) -> frozenset[str]:
        node_set = set(self.nodes if selected_nodes is None else selected_nodes)
        unknown_nodes = node_set.difference(self.nodes)
        if unknown_nodes:
            raise KeyError(sorted(unknown_nodes)[0])
        justification_set = set(
            self.justifications
            if selected_justifications is None
            else selected_justifications
        )
        unknown_justifications = justification_set.difference(self.justifications)
        if unknown_justifications:
            raise KeyError(sorted(unknown_justifications)[0])

        derived = {
            node_id
            for node_id in node_set
            if self.is_admissible_leaf(node_id)
        }
        for node_id in self.topological_order:
            if node_id not in node_set or node_id in derived:
                continue
            for justification in self.incoming(
                node_id,
                certified_only=certified_only,
            ):
                if justification.id not in justification_set:
                    continue
                if all(premise in derived for premise in justification.premises):
                    derived.add(node_id)
                    break
        return frozenset(derived)

    def certified_subfield(self) -> "ProofField":
        return ProofField(
            tuple(self.nodes.values()),
            tuple(
                justification
                for justification in self.justifications.values()
                if justification.certified
            ),
            premises=self.premises,
            targets=self.targets,
            evidence=tuple(self.evidence.values()),
            metadata=self.metadata,
        )

    def total_values(self, nodes: Iterable[str] | None = None) -> ValueVector:
        node_ids = self.nodes.keys() if nodes is None else nodes
        total = ValueVector()
        for node_id in node_ids:
            if node_id not in self.nodes:
                raise KeyError(node_id)
            total = total + self.nodes[node_id].values
        return total

    def total_costs(self, nodes: Iterable[str] | None = None) -> CostVector:
        node_ids = self.nodes.keys() if nodes is None else nodes
        storage = audit = recovery = cognitive = 0.0
        for node_id in node_ids:
            if node_id not in self.nodes:
                raise KeyError(node_id)
            costs = self.nodes[node_id].costs
            storage += costs.storage
            audit += costs.audit
            recovery += costs.recovery
            cognitive += costs.cognitive
        return CostVector(storage, audit, recovery, cognitive)
