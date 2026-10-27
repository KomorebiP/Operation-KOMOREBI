"""Least protected rule models and scoped negative derivations.

The input is the same ProofFieldViews snapshot used by the Komorebi Space bridge.
Forward closure avoids enumerating local or global valuation spaces. A negative
witness derives one forbidden node from the declared leaves and positive data.
It is not a counterexample to the mathematical sentence in a node label.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .views import ProofFieldViews


def _nodes(views: ProofFieldViews, values: Iterable[str], name: str) -> frozenset[str]:
    result = frozenset(values)
    if any(type(v) is not str for v in result) or not result <= views.nodes:
        raise ValueError(f"{name} contains invalid or unknown node identifiers")
    return result


@dataclass(frozen=True, slots=True)
class DerivationWitness:
    target: str
    rule_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExtensionResult:
    feasible: bool
    closure: frozenset[str]
    rule_ids: tuple[str, ...]
    obstruction: DerivationWitness | None = None


def _replay(views: ProofFieldViews, positive: frozenset[str], ids: tuple[str, ...], *, require_new: bool = False) -> frozenset[str] | None:
    if type(ids) is not tuple or any(type(i) is not str for i in ids):
        return None
    rules = {r.id: r for r in views.rules}
    current = set(views.leaves | positive)
    for rule_id in ids:
        rule = rules.get(rule_id)
        if rule is None or not rule.premises <= current or (require_new and rule.conclusion in current):
            return None
        current.add(rule.conclusion)
    return frozenset(current)


def verify_derivation(views: ProofFieldViews, positive: Iterable[str], witness: DerivationWitness) -> bool:
    """Replay a finite positive derivation using only certified rules of the snapshot."""
    s = _nodes(views, positive, "positive observations")
    if not isinstance(witness, DerivationWitness) or type(witness.target) is not str or witness.target not in views.nodes:
        return False
    closure = _replay(views, s, witness.rule_ids)
    return closure is not None and witness.target in closure


def verify_extension_obstruction(views: ProofFieldViews, positive: Iterable[str],
                                 negative: Iterable[str], witness: DerivationWitness) -> bool:
    n = _nodes(views, negative, "negative observations")
    return (isinstance(witness, DerivationWitness) and type(witness.target) is str
            and witness.target in n and verify_derivation(views, positive, witness))


def solve_extension(views: ProofFieldViews, *, positive: Iterable[str] = (),
                    negative: Iterable[str] = ()) -> ExtensionResult:
    """Return the least seeded closure and either a model or a forbidden-node witness.

    Rules are scanned to a fixed point. At most |V| successful insertions occur.
    The returned negative subtrace is causally sufficient, not minimum-cost.
    """
    s, n = _nodes(views, positive, "positive observations"), _nodes(views, negative, "negative observations")
    current = set(views.leaves | s)
    parent = {}
    steps = []
    while True:
        before = len(current)
        for rule in views.rules:
            if rule.conclusion not in current and rule.premises <= current:
                current.add(rule.conclusion)
                parent[rule.conclusion] = rule
                steps.append(rule.id)
        if len(current) == before:
            break
    forbidden = sorted(current & n)
    if not forbidden:
        return ExtensionResult(True, frozenset(current), tuple(steps))
    target = forbidden[0]
    needed_rules, pending = set(), [target]
    visited = set()
    while pending:
        v = pending.pop()
        if v in visited:
            continue
        visited.add(v)
        if v not in parent:
            continue
        rule = parent[v]
        needed_rules.add(rule.id)
        pending.extend(sorted(rule.premises))
    witness = DerivationWitness(target, tuple(i for i in steps if i in needed_rules))
    return ExtensionResult(False, frozenset(current), tuple(steps), witness)


def verify_extension_result(views: ProofFieldViews, *, positive: Iterable[str], negative: Iterable[str],
                            result: ExtensionResult) -> bool:
    """Check leastness by replay plus closure, without rerunning the closure solver."""
    s, n = _nodes(views, positive, "positive observations"), _nodes(views, negative, "negative observations")
    if not isinstance(result, ExtensionResult) or type(result.feasible) is not bool or type(result.closure) is not frozenset:
        return False
    replayed = _replay(views, s, result.rule_ids, require_new=True)
    if replayed is None or replayed != result.closure or not views.is_local_model(views.nodes, replayed):
        return False
    if result.feasible:
        return result.obstruction is None and not (replayed & n)
    return result.obstruction is not None and verify_extension_obstruction(views, s, n, result.obstruction)


def extend_partial(views: ProofFieldViews, patch: Iterable[str], true_nodes: Iterable[str]) -> ExtensionResult:
    """Preserve both true and false assignments on a patch, whether or not it is locally valid."""
    u, s = _nodes(views, patch, "patch"), _nodes(views, true_nodes, "true nodes")
    if not s <= u:
        raise ValueError("true nodes must lie in the prescribed patch")
    return solve_extension(views, positive=s, negative=u-s)
