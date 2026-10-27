"""Finite predictive quotients and collision-driven capsule refinement.

For a finite transition table, :func:`coarsest_action_congruent_partition`
implements deterministic partition refinement.  Its fixed point is the
coarsest partition that preserves readouts, action applicability, and the
successor equivalence class of every enabled action.  This is deliberately a
discrete oracle: no linear projector or unverified approximation is implied.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Iterable, Mapping, Sequence

from .canonical import canonical_json, canonical_value, content_hash, require_trimmed
from .model import (
    ActionContract,
    ActionReceipt,
    CongruenceAudit,
    LeakageWitness,
    PredictiveCapsule,
    RefinementProposal,
    StaticTransitionState,
)


_MISSING = {"$missing": True}


def _state_table(
    states: Mapping[str, StaticTransitionState] | Sequence[StaticTransitionState],
) -> dict[str, StaticTransitionState]:
    values = tuple(states.values()) if isinstance(states, Mapping) else tuple(states)
    if not values:
        raise ValueError("the finite transition system needs at least one state")
    result: dict[str, StaticTransitionState] = {}
    for index, state in enumerate(values):
        if not isinstance(state, StaticTransitionState):
            raise TypeError(f"states[{index}] must be a StaticTransitionState")
        previous = result.get(state.state_hash)
        if previous is not None:
            if previous.to_record() != state.to_record():
                raise ValueError(
                    "one target-free state identity has inconsistent readouts or contents"
                )
            continue
        result[state.state_hash] = state
    return {key: result[key] for key in sorted(result)}


def _receipt_table(
    receipts: Sequence[ActionReceipt],
) -> dict[tuple[str, str], ActionReceipt]:
    result: dict[tuple[str, str], ActionReceipt] = {}
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, ActionReceipt):
            raise TypeError(f"receipts[{index}] must be an ActionReceipt")
        key = (receipt.source_state_hash, receipt.action)
        previous = result.get(key)
        if previous is not None:
            previous_semantics = (
                previous.applicable,
                previous.successor_state_hash,
                canonical_json(previous.parameters),
            )
            receipt_semantics = (
                receipt.applicable,
                receipt.successor_state_hash,
                canonical_json(receipt.parameters),
            )
            if previous_semantics != receipt_semantics:
                raise ValueError(
                    "nondeterministic receipts for one (state, action) coordinate"
                )
            # Evidence provenance is nonsemantic.  Retain a deterministic
            # representative when the same transition was observed twice.
            result[key] = min(
                (previous, receipt), key=lambda item: item.receipt_hash
            )
            continue
        result[key] = receipt
    return result


def _alphabet(
    table: Mapping[tuple[str, str], ActionReceipt],
    action_alphabet: Iterable[str] | None,
) -> tuple[str, ...]:
    if action_alphabet is None:
        return tuple(sorted({action for _, action in table}))
    actions = tuple(sorted(set(
        require_trimmed(action, f"action_alphabet[{index}]")
        for index, action in enumerate(action_alphabet)
    )))
    return actions


def _receipt_observation(
    receipt_table: Mapping[tuple[str, str], ActionReceipt],
    state_hash: str,
    action: str,
    *,
    closed_world: bool,
) -> tuple[bool | None, str, bool]:
    receipt = receipt_table.get((state_hash, action))
    if receipt is None:
        if closed_world:
            return False, "", False
        return None, "", False
    return receipt.applicable, receipt.successor_state_hash, True


def _validate_receipt_domain(
    states: Mapping[str, StaticTransitionState],
    receipts: Mapping[tuple[str, str], ActionReceipt],
) -> None:
    for (source_hash, action), receipt in receipts.items():
        if source_hash not in states:
            raise ValueError(f"receipt source for action {action!r} is not in the state set")
        if (
            receipt.applicable
            and receipt.successor_state_hash
            and receipt.successor_state_hash not in states
        ):
            raise ValueError(
                f"receipt successor for action {action!r} is not in the state set"
            )


def coarsest_action_congruent_partition(
    states: Mapping[str, StaticTransitionState] | Sequence[StaticTransitionState],
    receipts: Sequence[ActionReceipt],
    *,
    action_alphabet: Iterable[str] | None = None,
    closed_world: bool = True,
) -> PredictiveCapsule:
    """Return the exact coarsest action-congruent finite partition.

    With ``closed_world=True`` (the default), an absent receipt means the
    action is disabled.  With ``closed_world=False``, missing receipts remain
    a distinct unknown observation.  A named successor must occur in
    ``states``.  An enabled receipt whose bounded collection omitted its
    successor is retained as ``unknown_successor`` and makes the returned
    capsule incomplete; it can guide routing but cannot certify a contract.
    """

    state_map = _state_table(states)
    receipt_map = _receipt_table(tuple(receipts))
    actions = _alphabet(receipt_map, action_alphabet)
    _validate_receipt_domain(state_map, receipt_map)

    # Moore initialization: goal/readout sufficiency is mandatory, so states
    # with distinct readouts can never begin in the same candidate block.
    initial: dict[str, list[str]] = {}
    for state_hash, state in state_map.items():
        initial.setdefault(canonical_json(state.readout), []).append(state_hash)
    blocks = tuple(sorted(tuple(sorted(values)) for values in initial.values()))

    while True:
        class_by_state = {
            state_hash: block_index
            for block_index, block in enumerate(blocks)
            for state_hash in block
        }
        refined: dict[str, list[str]] = {}
        for state_hash, state in state_map.items():
            action_signature: list[Any] = []
            for action in actions:
                applicable, successor_hash, observed = _receipt_observation(
                    receipt_map, state_hash, action, closed_world=closed_world
                )
                if applicable is None:
                    action_signature.append([action, "unknown"])
                elif not applicable:
                    action_signature.append(
                        [action, "disabled" if observed or closed_world else "unknown"]
                    )
                else:
                    action_signature.append(
                        [action, "enabled", class_by_state[successor_hash]]
                        if successor_hash
                        else [action, "enabled", "unknown_successor"]
                    )
            signature = canonical_json(
                {"readout": state.readout, "actions": action_signature}
            )
            refined.setdefault(signature, []).append(state_hash)
        next_blocks = tuple(
            sorted(tuple(sorted(values)) for values in refined.values())
        )
        if next_blocks == blocks:
            break
        blocks = next_blocks

    capsule = PredictiveCapsule(
        blocks=blocks,
        feature_names=(),
        origin="finite_coarsest_action_congruent_oracle",
        complete=(closed_world or all(
            (state_hash, action) in receipt_map
            for state_hash in state_map
            for action in actions
        )) and all(
            not receipt.applicable or bool(receipt.successor_state_hash)
            for receipt in receipt_map.values()
        ),
    )
    # An implementation regression in refinement is a safety issue.  Audit the
    # fixed point independently before returning it.
    audit = audit_action_congruence(
        capsule,
        tuple(state_map.values()),
        tuple(receipt_map.values()),
        action_alphabet=actions,
        closed_world=closed_world,
    )
    if any(
        witness.kind in {"readout", "applicability", "successor"}
        for witness in audit.witnesses
    ):
        raise RuntimeError("coarsest-partition oracle produced a leaking capsule")
    return capsule


coarsest_partition_oracle = coarsest_action_congruent_partition
finite_coarsest_partition = coarsest_action_congruent_partition


def _feature_value(state: StaticTransitionState, feature_name: str) -> Any:
    """Read a target-free feature by dotted path from runtime then ambient data."""

    if feature_name in state.runtime_values:
        return state.runtime_values[feature_name]
    if feature_name in state.ambient.features:
        return state.ambient.features[feature_name]
    path = feature_name.split(".")
    roots: tuple[Any, ...] = (state.runtime_values, state.ambient.features)
    for root in roots:
        current: Any = root
        found = True
        for part in path:
            if not isinstance(current, Mapping) or part not in current:
                found = False
                break
            current = current[part]
        if found:
            return current
    return _MISSING


def capsule_from_features(
    states: Mapping[str, StaticTransitionState] | Sequence[StaticTransitionState],
    feature_names: Iterable[str],
    *,
    origin: str = "target_free_feature_projection",
) -> PredictiveCapsule:
    """Partition finite states using only named target-free coordinates."""

    state_map = _state_table(states)
    names = tuple(sorted(set(
        require_trimmed(name, f"feature_names[{index}]")
        for index, name in enumerate(feature_names)
    )))
    groups: dict[str, list[str]] = {}
    for state_hash, state in state_map.items():
        signature = canonical_json(
            [[name, _feature_value(state, name)] for name in names]
        )
        groups.setdefault(signature, []).append(state_hash)
    return PredictiveCapsule(
        blocks=tuple(tuple(sorted(values)) for values in groups.values()),
        feature_names=names,
        origin=origin,
        complete=True,
    )


def _witness(
    *,
    kind: str,
    capsule: PredictiveCapsule,
    left: str,
    right: str,
    block_index: int,
    action: str = "",
    left_observation: Any = None,
    right_observation: Any = None,
    details: Mapping[str, Any] | None = None,
) -> LeakageWitness:
    return LeakageWitness(
        kind=kind,
        capsule_hash=capsule.capsule_hash,
        left_state_hash=left,
        right_state_hash=right,
        action=action,
        left_observation=left_observation,
        right_observation=right_observation,
        block_index=block_index,
        details={} if details is None else details,
    )


def audit_action_congruence(
    capsule: PredictiveCapsule,
    states: Mapping[str, StaticTransitionState] | Sequence[StaticTransitionState],
    receipts: Sequence[ActionReceipt],
    *,
    action_alphabet: Iterable[str] | None = None,
    closed_world: bool = True,
) -> CongruenceAudit:
    """Audit readout, applicability, and successor congruence independently."""

    if not isinstance(capsule, PredictiveCapsule):
        raise TypeError("capsule must be a PredictiveCapsule")
    state_map = _state_table(states)
    receipt_map = _receipt_table(tuple(receipts))
    actions = _alphabet(receipt_map, action_alphabet)
    _validate_receipt_domain(state_map, receipt_map)

    capsule_states = set(capsule.state_hashes)
    supplied_states = set(state_map)
    unknown = capsule_states - supplied_states
    if unknown:
        raise ValueError("capsule contains states absent from the audit state set")
    if capsule.complete and capsule_states != supplied_states:
        raise ValueError("a complete capsule must cover exactly the audit state set")

    witnesses: list[LeakageWitness] = []
    readout_witness_hashes: list[str] = []
    per_action_witnesses: dict[str, list[LeakageWitness]] = {
        action: [] for action in actions
    }
    successor_class = {
        state_hash: capsule.block_index(state_hash) for state_hash in capsule_states
    }

    # Unary incompleteness witnesses are distinct from binary collisions.  A
    # missing observation cannot be repaired merely by splitting a block, and
    # must remain visible even when its source block is a singleton.
    for state_hash in sorted(capsule_states):
        for action in actions:
            enabled, successor_hash, observed = _receipt_observation(
                receipt_map, state_hash, action, closed_world=closed_world
            )
            block_index = successor_class[state_hash]
            if not observed and not closed_world:
                item = _witness(
                    kind="missing_receipt",
                    capsule=capsule,
                    left=state_hash,
                    right=state_hash,
                    block_index=block_index,
                    action=action,
                    left_observation="missing",
                    right_observation="missing",
                )
                witnesses.append(item)
                per_action_witnesses[action].append(item)
            elif enabled is True and (
                not successor_hash or successor_hash not in successor_class
            ):
                item = _witness(
                    kind="missing_successor",
                    capsule=capsule,
                    left=state_hash,
                    right=state_hash,
                    block_index=block_index,
                    action=action,
                    left_observation=successor_hash or "missing",
                    right_observation=successor_hash or "missing",
                )
                witnesses.append(item)
                per_action_witnesses[action].append(item)

    for block_index, block in enumerate(capsule.blocks):
        for left, right in combinations(block, 2):
            left_state = state_map[left]
            right_state = state_map[right]
            if canonical_json(left_state.readout) != canonical_json(right_state.readout):
                item = _witness(
                    kind="readout",
                    capsule=capsule,
                    left=left,
                    right=right,
                    block_index=block_index,
                    left_observation=left_state.readout,
                    right_observation=right_state.readout,
                )
                witnesses.append(item)
                readout_witness_hashes.append(item.witness_hash)

            for action in actions:
                left_enabled, left_successor, left_observed = _receipt_observation(
                    receipt_map, left, action, closed_world=closed_world
                )
                right_enabled, right_successor, right_observed = _receipt_observation(
                    receipt_map, right, action, closed_world=closed_world
                )
                if not closed_world and (not left_observed or not right_observed):
                    # Unary witnesses above already retain the missing
                    # evidence.  No binary claim is sound until both receipts
                    # are present.
                    continue
                if left_enabled != right_enabled:
                    item = _witness(
                        kind="applicability",
                        capsule=capsule,
                        left=left,
                        right=right,
                        block_index=block_index,
                        action=action,
                        left_observation=left_enabled,
                        right_observation=right_enabled,
                    )
                    witnesses.append(item)
                    per_action_witnesses[action].append(item)
                    continue
                if left_enabled is True:
                    if (
                        not left_successor
                        or not right_successor
                        or left_successor not in successor_class
                        or right_successor not in successor_class
                    ):
                        # Unary witnesses above already retain the missing
                        # successor evidence.
                        continue
                    if successor_class[left_successor] != successor_class[right_successor]:
                        item = _witness(
                            kind="successor",
                            capsule=capsule,
                            left=left,
                            right=right,
                            block_index=block_index,
                            action=action,
                            left_observation={
                                "state": left_successor,
                                "block": successor_class[left_successor],
                            },
                            right_observation={
                                "state": right_successor,
                                "block": successor_class[right_successor],
                            },
                        )
                        witnesses.append(item)
                        per_action_witnesses[action].append(item)

    table_complete = (closed_world or all(
        (state_hash, action) in receipt_map
        for state_hash in capsule_states
        for action in actions
    )) and all(
        not receipt.applicable or (
            bool(receipt.successor_state_hash)
            and receipt.successor_state_hash in successor_class
        )
        for (state_hash, action), receipt in receipt_map.items()
        if state_hash in capsule_states and action in actions
    )
    readout_ok = not readout_witness_hashes
    contracts: list[ActionContract] = []
    for action in actions:
        action_witnesses = per_action_witnesses[action]
        kinds = {item.kind for item in action_witnesses}
        all_hashes = tuple(sorted(
            set(readout_witness_hashes).union(
                item.witness_hash for item in action_witnesses
            )
        ))
        contracts.append(
            ActionContract(
                action=action,
                capsule_hash=capsule.capsule_hash,
                covered_state_hashes=tuple(sorted(capsule_states)),
                readout_congruent=readout_ok,
                applicability_congruent=not kinds.intersection(
                    {"applicability", "missing_receipt"}
                ),
                successor_congruent=not kinds.intersection(
                    {"successor", "missing_successor"}
                ),
                witness_hashes=all_hashes,
                complete=table_complete,
            )
        )

    unique_witnesses = {
        witness.witness_hash: witness for witness in witnesses
    }
    return CongruenceAudit(
        capsule_hash=capsule.capsule_hash,
        contracts=tuple(contracts),
        witnesses=tuple(unique_witnesses.values()),
        covered_state_hashes=tuple(sorted(capsule_states)),
        action_alphabet=actions,
    )


audit_congruence = audit_action_congruence
audit_capsule = audit_action_congruence


def _candidate_feature_names(states: Mapping[str, StaticTransitionState]) -> tuple[str, ...]:
    names: set[str] = set()
    for state in states.values():
        names.update(state.runtime_values)
        names.update(state.ambient.features)
    return tuple(sorted(names))


def refine_capsule_from_collisions(
    capsule: PredictiveCapsule,
    states: Mapping[str, StaticTransitionState] | Sequence[StaticTransitionState],
    receipts: Sequence[ActionReceipt],
    *,
    candidate_features: Iterable[str] | None = None,
    action_alphabet: Iterable[str] | None = None,
    closed_world: bool = True,
) -> RefinementProposal:
    """Greedily split leaking pairs with the smallest available feature set.

    Features are target-free by construction: they are read only from
    ``runtime_values`` or :class:`AmbientPacket`.  The algorithm is a finite
    deterministic set-cover heuristic, not a claim of globally minimal feature
    selection.  Any pair that no available feature separates remains explicit
    in ``unresolved_witness_hashes`` and the resulting capsule is incomplete.
    """

    state_map = _state_table(states)
    audit = audit_action_congruence(
        capsule,
        tuple(state_map.values()),
        receipts,
        action_alphabet=action_alphabet,
        closed_world=closed_world,
    )
    candidates = (
        _candidate_feature_names(state_map)
        if candidate_features is None
        else tuple(sorted(set(
            require_trimmed(name, f"candidate_features[{index}]")
            for index, name in enumerate(candidate_features)
        )))
    )
    candidates = tuple(name for name in candidates if name not in capsule.feature_names)
    unresolved = {item.witness_hash: item for item in audit.witnesses}
    selected: list[str] = []

    while unresolved:
        coverage: list[tuple[int, str, set[str]]] = []
        for name in candidates:
            if name in selected:
                continue
            covered = {
                witness_hash
                for witness_hash, witness in unresolved.items()
                if canonical_json(_feature_value(state_map[witness.left_state_hash], name))
                != canonical_json(_feature_value(state_map[witness.right_state_hash], name))
            }
            if covered:
                coverage.append((len(covered), name, covered))
        if not coverage:
            break
        # Largest collision coverage, lexicographically smallest deterministic tie-break.
        coverage.sort(key=lambda item: (-item[0], item[1]))
        _, chosen, covered = coverage[0]
        selected.append(chosen)
        for witness_hash in covered:
            unresolved.pop(witness_hash, None)

    new_blocks: list[tuple[str, ...]] = []
    for block in capsule.blocks:
        groups: dict[str, list[str]] = {}
        for state_hash in block:
            state = state_map[state_hash]
            signature = canonical_json(
                [[name, _feature_value(state, name)] for name in selected]
            )
            groups.setdefault(signature, []).append(state_hash)
        new_blocks.extend(tuple(sorted(values)) for values in groups.values())

    return RefinementProposal(
        base_capsule_hash=capsule.capsule_hash,
        witness_hashes=tuple(sorted(item.witness_hash for item in audit.witnesses)),
        added_features=tuple(sorted(selected)),
        refined_blocks=tuple(new_blocks),
        unresolved_witness_hashes=tuple(sorted(unresolved)),
    )


refine_capsule = refine_capsule_from_collisions
collision_driven_refinement = refine_capsule_from_collisions


def oracle_refinement_gap(
    candidate: PredictiveCapsule,
    oracle: PredictiveCapsule,
) -> tuple[tuple[str, str], ...]:
    """Return candidate-equal state pairs separated by the exact oracle."""

    if set(candidate.state_hashes) != set(oracle.state_hashes):
        raise ValueError("candidate and oracle must cover the same finite state set")
    collisions: list[tuple[str, str]] = []
    for block in candidate.blocks:
        for left, right in combinations(block, 2):
            if oracle.block_index(left) != oracle.block_index(right):
                collisions.append((left, right))
    return tuple(collisions)


__all__ = [
    "coarsest_action_congruent_partition",
    "coarsest_partition_oracle",
    "finite_coarsest_partition",
    "capsule_from_features",
    "audit_action_congruence",
    "audit_congruence",
    "audit_capsule",
    "refine_capsule_from_collisions",
    "refine_capsule",
    "collision_driven_refinement",
    "oracle_refinement_gap",
]
