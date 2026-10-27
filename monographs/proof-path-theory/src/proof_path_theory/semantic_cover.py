"""Certified semantic covers, including redundant whole-support constraints.

The graph, leaves and original rule contents stay fixed. A cover may omit a
rule's whole support only if the rules seen by its patches entail that rule.
Failure returns matching local data with no global model, not merely a failed
search. The finite checker is separate from the closure-based producer.
"""
from __future__ import annotations
from copy import copy
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence
from .views import ProofFieldViews
from .extension import DerivationWitness, solve_extension, verify_derivation


@dataclass(frozen=True, slots=True)
class RuleEntailment:
    rule_id: str
    witness: DerivationWitness


@dataclass(frozen=True, slots=True)
class SemanticCoverResult:
    sufficient: bool
    entailments: tuple[RuleEntailment, ...] = ()
    failed_rule: str | None = None
    countermodel: frozenset[str] | None = None


def _visible(views: ProofFieldViews, patches: Sequence[Iterable[str]]):
    ps = tuple(views._patch(p) for p in patches)
    if frozenset().union(*ps) != views.nodes:
        raise ValueError("semantic cover requires node coverage")
    # An independent snapshot with the same immutable nodes/leaves and a subset
    # of its immutable rule records. This never changes the source view system.
    visible = copy(views)
    visible.rules = tuple(r for r in views.rules if any(r.support <= p for p in ps))
    return ps, visible


def analyze_semantic_cover(views: ProofFieldViews, patches: Sequence[Iterable[str]]) -> SemanticCoverResult:
    """Entail all original rules using only the rules whose supports are visible."""
    _, visible = _visible(views, patches)
    records = []
    for rule in views.rules:
        result = solve_extension(visible, positive=rule.premises)
        if rule.conclusion not in result.closure:
            return SemanticCoverResult(False, failed_rule=rule.id, countermodel=result.closure)
        records.append(RuleEntailment(rule.id, DerivationWitness(rule.conclusion, result.rule_ids)))
    return SemanticCoverResult(True, tuple(records))


def verify_semantic_cover(views: ProofFieldViews, patches: Sequence[Iterable[str]],
                          result: SemanticCoverResult) -> bool:
    """Replay positive derivations or directly check the negative model.

    This function does not call the producer or run a closure search.
    """
    ps, visible = _visible(views, patches)
    if not isinstance(result, SemanticCoverResult) or type(result.sufficient) is not bool:
        return False
    if type(result.entailments) is not tuple:
        return False
    rules = {r.id: r for r in views.rules}
    if result.sufficient:
        if result.failed_rule is not None or result.countermodel is not None:
            return False
        if any(not isinstance(e, RuleEntailment) or type(e.rule_id) is not str
               for e in result.entailments):
            return False
        ids = [e.rule_id for e in result.entailments]
        if len(ids) != len(set(ids)) or set(ids) != set(rules):
            return False
        for e in result.entailments:
            r = rules[e.rule_id]
            if (not isinstance(e.witness, DerivationWitness) or e.witness.target != r.conclusion
                    or not verify_derivation(visible, r.premises, e.witness)):
                return False
        return True
    if result.entailments or type(result.failed_rule) is not str or result.failed_rule not in rules:
        return False
    t = result.countermodel
    if type(t) is not frozenset or any(type(v) is not str for v in t) or not t <= views.nodes:
        return False
    r = rules[result.failed_rule]
    return (visible.is_local_model(visible.nodes, t) and r.premises <= t and r.conclusion not in t
            and all(views.is_local_model(p, t & p) for p in ps))


def glue_semantic(views: ProofFieldViews, patches: Sequence[Iterable[str]],
                   true_sets: Sequence[Iterable[str]], certificate: SemanticCoverResult) -> frozenset[str]:
    """Assemble matching data under an independently checked semantic-cover certificate."""
    ps, _ = _visible(views, patches)
    if not verify_semantic_cover(views, ps, certificate) or not certificate.sufficient:
        raise ValueError("a valid positive semantic-cover certificate is required")
    if len(ps) != len(true_sets):
        raise ValueError("one local valuation is required per patch")
    ts = tuple(frozenset(t) for t in true_sets)
    if any(not views.is_local_model(p,t) for p,t in zip(ps,ts)):
        raise ValueError("an assignment is not a local model")
    if any(ts[i] & ps[j] != ts[j] & ps[i] for i,j in combinations(range(len(ps)),2)):
        raise ValueError("local valuations disagree on an overlap")
    answer = frozenset().union(*ts)
    if not views.is_local_model(views.nodes,answer):
        raise AssertionError("semantic cover failed to preserve the global rule model")
    return answer
