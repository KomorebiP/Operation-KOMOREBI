"""Applicability-driven composition routing for PR-LASM Block 10.

Block 9 continued a prefix only when its last family appeared in a short
hand-written whitelist.  This module replaces that rule with finite evidence:

* target-aware proposal is confined to labelled demonstrations;
* proposed actions are frozen as target-free executable records;
* a finite state/receipt corpus is partitioned by action consequences;
* every returned route replays exactly on all demonstrations; and
* held-out inputs are executed only after programs are frozen, with one exact
  behavior class required for commitment.

Exact grids remain authoritative.  Capsules and gauges can quotient routing
evidence, but they cannot manufacture or substitute a raster state.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import json
from numbers import Integral
from typing import Any, Mapping, Sequence

from komorebi_lasm_composition.model import (
    Grid,
    canonical_json,
    canonical_value,
    sha256_record,
    validate_grid,
)
from komorebi_lasm_composition.stages import verified_inherited_macro_ids
from komorebi_lasm_composition.task import TrainingTask, sanitize_training_task

from .transition_corpus import (
    CorpusAction,
    TransitionCorpus,
    TransitionCorpusLimits,
    build_transition_corpus,
    guard_matches,
    grid_feature_map,
)


def _positive_int(value: object, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    result = int(value)
    if result < (0 if allow_zero else 1):
        qualifier = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{label} must be {qualifier}")
    return result


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _state_hash(state: Any) -> str:
    for name in ("state_hash", "content_hash"):
        value = getattr(state, name, None)
        if callable(value):
            value = value()
        if isinstance(value, str):
            return _digest(value, "state hash")
    to_record = getattr(state, "to_record", None)
    return sha256_record(to_record() if callable(to_record) else repr(state))


def _receipt_action(receipt: Any) -> str:
    value = getattr(receipt, "action", None)
    if not isinstance(value, str):
        raise TypeError("action receipt lacks a string action")
    return value


def _receipt_source(receipt: Any) -> str:
    value = getattr(receipt, "source_state_hash", None)
    return _digest(value, "receipt source_state_hash")


def _receipt_applicable(receipt: Any) -> bool:
    value = getattr(receipt, "applicable", None)
    if not isinstance(value, bool):
        raise TypeError("receipt applicable field must be Boolean")
    return value


def _content_hash(value: Any) -> str:
    for name in ("content_hash", "contract_hash", "capsule_hash", "witness_hash"):
        item = getattr(value, name, None)
        if callable(item):
            item = item()
        if isinstance(item, str) and len(item) == 64:
            return item
    to_record = getattr(value, "to_record", None)
    return sha256_record(to_record() if callable(to_record) else repr(value))


@dataclass(frozen=True, slots=True)
class RoutingLimits:
    """Outer compilation limits; the embedded corpus remains independently finite."""

    max_depth: int = 3
    max_states: int = 256
    max_actions: int = 256
    max_proposals_per_state: int = 128
    max_transitions: int = 1_024
    max_receipts: int = 8_192
    max_counterfactual_states: int = 128
    max_leaf_executions: int = 16_384
    max_total_cost: int = 24
    max_detours_per_route: int = 1
    allow_semantic_detours: bool = True
    include_block9_seeds: bool = True
    include_tools: bool = True
    require_unique_test_behavior: bool = True

    def __post_init__(self) -> None:
        for name in (
            "max_depth", "max_states", "max_actions", "max_proposals_per_state",
            "max_transitions", "max_receipts", "max_counterfactual_states",
            "max_leaf_executions", "max_total_cost",
        ):
            _positive_int(getattr(self, name), name)
        _positive_int(self.max_detours_per_route, "max_detours_per_route", allow_zero=True)
        for name in (
            "allow_semantic_detours", "include_block9_seeds", "include_tools",
            "require_unique_test_behavior",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be Boolean")
        if self.max_depth > 8:
            raise ValueError("routing depth is hard-capped at eight")
        if self.max_actions > 512 or self.max_proposals_per_state > 512:
            raise ValueError("action and proposal limits are hard-capped at 512")

    @classmethod
    def normalize(cls, limits: object | None) -> "RoutingLimits":
        if limits is None:
            return cls()
        if isinstance(limits, cls):
            return limits
        defaults = cls()
        values = {
            name: getattr(limits, name, getattr(defaults, name))
            for name in cls.__dataclass_fields__
        }
        # Legacy CompositionLimits calls the search-state capacity a frontier.
        if hasattr(limits, "max_frontier") and not hasattr(limits, "max_states"):
            values["max_states"] = max(64, int(getattr(limits, "max_frontier")))
        if hasattr(limits, "max_expansions"):
            expansion = int(getattr(limits, "max_expansions"))
            if not hasattr(limits, "max_transitions"):
                values["max_transitions"] = expansion
            if not hasattr(limits, "max_leaf_executions"):
                values["max_leaf_executions"] = expansion
        return cls(**values)

    def corpus_limits(self) -> TransitionCorpusLimits:
        return TransitionCorpusLimits(
            max_depth=self.max_depth,
            max_states=self.max_states,
            max_actions=self.max_actions,
            max_proposals_per_state=self.max_proposals_per_state,
            max_transitions=self.max_transitions,
            max_receipts=self.max_receipts,
            max_counterfactual_states=self.max_counterfactual_states,
            max_leaf_executions=self.max_leaf_executions,
            max_total_cost=self.max_total_cost,
            max_detours_per_route=self.max_detours_per_route,
            allow_semantic_detours=self.allow_semantic_detours,
        )


@dataclass(frozen=True, slots=True)
class RoutedProgram:
    """A target-free ordered action program with sealed training evidence."""

    actions: tuple[CorpusAction, ...]
    contract_hashes: tuple[str, ...]
    training_hashes: tuple[str, ...]
    bank_bundle_id: str
    corpus_id: str
    contains_detour: bool = False
    schema_version: int = 1
    contract_records_json: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "actions", tuple(self.actions))
        object.__setattr__(self, "contract_hashes", tuple(self.contract_hashes))
        object.__setattr__(self, "training_hashes", tuple(self.training_hashes))
        object.__setattr__(self, "contract_records_json", tuple(self.contract_records_json))
        if not self.actions or len(self.actions) != len(self.contract_hashes):
            raise ValueError("a routed program requires one contract per action")
        if not all(isinstance(action, CorpusAction) for action in self.actions):
            raise TypeError("program actions must be CorpusAction records")
        for index, value in enumerate(self.contract_hashes):
            _digest(value, f"contract_hashes[{index}]")
        for index, value in enumerate(self.training_hashes):
            _digest(value, f"training_hashes[{index}]")
        if self.contract_records_json and len(self.contract_records_json) != len(self.actions):
            raise ValueError("embedded contract records must match the action count")
        if self.contract_records_json:
            from .model import ActionContract

            for index, (encoded, action, expected_hash) in enumerate(zip(
                self.contract_records_json, self.actions, self.contract_hashes,
            )):
                if not isinstance(encoded, str):
                    raise TypeError(f"contract_records_json[{index}] must be a string")
                try:
                    record = json.loads(encoded)
                except json.JSONDecodeError as error:
                    raise ValueError(f"contract_records_json[{index}] is invalid JSON") from error
                if not isinstance(record, dict) or canonical_json(record) != encoded:
                    raise ValueError(f"contract_records_json[{index}] must encode a canonical object")
                contract = ActionContract.from_record(record)
                if not contract.certified:
                    raise ValueError("a routed program cannot embed an uncertified contract")
                if contract.action != action.action_id:
                    raise ValueError("embedded contract does not authorize its routed action")
                if contract.contract_hash != expected_hash:
                    raise ValueError("embedded contract hash does not match the sealed hash")
        _digest(self.bank_bundle_id, "bank_bundle_id")
        _digest(self.corpus_id, "corpus_id")
        if not isinstance(self.contains_detour, bool):
            raise TypeError("contains_detour must be Boolean")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    @property
    def total_cost(self) -> int:
        return sum(action.cost for action in self.actions)

    @property
    def depth(self) -> int:
        return len(self.actions)

    @property
    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.routed_program_semantics",
            "schema_version": self.schema_version,
            "action_ids": [action.action_id for action in self.actions],
            "actions": [action.semantic_record for action in self.actions],
            "input_type": "grid",
            "output_type": "grid",
        }

    @property
    def semantic_hash(self) -> str:
        return sha256_record(self.semantic_record)

    @property
    def syntax_hash(self) -> str:
        return sha256_record({
            **self.semantic_record,
            "guards": [action.guard for action in self.actions],
            "contract_hashes": list(self.contract_hashes),
            "contract_records": [json.loads(value) for value in self.contract_records_json],
        })

    def to_record(self) -> dict[str, Any]:
        record = {
            **self.semantic_record,
            "action_records": [action.to_record() for action in self.actions],
            "contract_hashes": list(self.contract_hashes),
            "contract_records": [json.loads(value) for value in self.contract_records_json],
            "training_hashes": list(self.training_hashes),
            "bank_bundle_id": self.bank_bundle_id,
            "corpus_id": self.corpus_id,
            "contains_detour": self.contains_detour,
            "total_cost": self.total_cost,
            "depth": self.depth,
            "semantic_hash": self.semantic_hash,
            "syntax_hash": self.syntax_hash,
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class RoutingTrace:
    root_states: int
    continued_states: int
    proposals_considered: int
    accepted_transitions: int
    capsule_abstentions: int
    capsule_collisions: int
    gauge_quotient_merges: int
    actual_leaf_executions: int
    exact_programs: int
    behavior_classes: int
    counterfactual_states: int = 0
    semantic_detours: int = 0
    contract_count: int = 0
    initial_capsule_hash: str = ""
    refined_capsule_hash: str = ""
    limit_reached: str = ""
    rejection_counts: tuple[tuple[str, int], ...] = ()
    schema_version: int = 1
    behavior_quotient_merges: int = 0

    def __post_init__(self) -> None:
        object.__setattr__(self, "rejection_counts", tuple((str(name), int(count)) for name, count in self.rejection_counts))
        for name in (
            "root_states", "continued_states", "proposals_considered",
            "accepted_transitions", "capsule_abstentions", "capsule_collisions",
            "gauge_quotient_merges", "behavior_quotient_merges",
            "actual_leaf_executions", "exact_programs",
            "behavior_classes", "counterfactual_states", "semantic_detours",
            "contract_count",
        ):
            _positive_int(getattr(self, name), name, allow_zero=True)
        if self.initial_capsule_hash:
            _digest(self.initial_capsule_hash, "initial_capsule_hash")
        if self.refined_capsule_hash:
            _digest(self.refined_capsule_hash, "refined_capsule_hash")
        if not isinstance(self.limit_reached, str):
            raise TypeError("limit_reached must be a string")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    # Short compatibility aliases requested by the architecture ledger.
    @property
    def proposals(self) -> int:
        return self.proposals_considered

    @property
    def transitions(self) -> int:
        return self.accepted_transitions

    def to_record(self) -> dict[str, Any]:
        record = {
            "schema": "komorebi.lasm_action.routing_trace",
            "schema_version": self.schema_version,
            "root_states": self.root_states,
            "continued_states": self.continued_states,
            "proposals_considered": self.proposals_considered,
            "accepted_transitions": self.accepted_transitions,
            "capsule_abstentions": self.capsule_abstentions,
            "capsule_collisions": self.capsule_collisions,
            "gauge_quotient_merges": self.gauge_quotient_merges,
            "behavior_quotient_merges": self.behavior_quotient_merges,
            "actual_leaf_executions": self.actual_leaf_executions,
            "exact_programs": self.exact_programs,
            "behavior_classes": self.behavior_classes,
            "counterfactual_states": self.counterfactual_states,
            "semantic_detours": self.semantic_detours,
            "contract_count": self.contract_count,
            "initial_capsule_hash": self.initial_capsule_hash,
            "refined_capsule_hash": self.refined_capsule_hash,
            "limit_reached": self.limit_reached,
            "rejection_counts": {name: count for name, count in self.rejection_counts},
        }
        record["content_hash"] = sha256_record(record)
        return record


def _state_features(state: Any) -> Mapping[str, Any]:
    ambient = getattr(state, "ambient", None)
    features = getattr(ambient, "features", None)
    if isinstance(features, Mapping):
        return features
    grid = getattr(state, "grid", None)
    return grid_feature_map(grid)


_INITIAL_FEATURES = (
    "square",
    "uniform",
    "palette_size",
    "background_unique_mode",
    "foreground_cells",
    "components4",
    "components8",
    "bbox_height",
    "bbox_width",
    "foreground_touches_border",
    "uniform_border",
    "symmetric_h",
    "symmetric_v",
)


def _feature_capsule(corpus: TransitionCorpus) -> Any:
    from .model import PredictiveCapsule

    groups: dict[str, list[str]] = defaultdict(list)
    for state in corpus.states:
        features = _state_features(state)
        signature = canonical_json({name: features.get(name) for name in _INITIAL_FEATURES})
        groups[signature].append(_state_hash(state))
    blocks = tuple(
        tuple(sorted(values))
        for _, values in sorted(groups.items())
    )
    return PredictiveCapsule(
        blocks=blocks,
        feature_names=tuple(sorted(_INITIAL_FEATURES)),
        origin="target_free_grid_features",
        complete=True,
    )


def _witnesses(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    records = getattr(value, "witnesses", None)
    if records is not None:
        return tuple(records)
    return (value,)


def _witness_kind(witness: Any) -> str:
    for name in ("kind", "witness_kind", "collision_kind"):
        value = getattr(witness, name, None)
        if isinstance(value, str):
            return value
    to_record = getattr(witness, "to_record", None)
    if callable(to_record):
        record = to_record()
        if isinstance(record, Mapping):
            for name in ("kind", "witness_kind", "collision_kind"):
                if isinstance(record.get(name), str):
                    return str(record[name])
    return "unknown"


def _witness_action(witness: Any) -> str:
    value = getattr(witness, "action", None)
    if isinstance(value, str):
        return value
    to_record = getattr(witness, "to_record", None)
    if callable(to_record):
        record = to_record()
        if isinstance(record, Mapping) and isinstance(record.get("action"), str):
            return str(record["action"])
    return ""


def _complete_action_ids(corpus: TransitionCorpus) -> tuple[str, ...]:
    """Actions having an explicit receipt on every materialized state.

    Missing receipts are unknown, never silently interpreted as disabled.
    The successor-domain check is already enforced by capsule auditing.
    """

    states = {_state_hash(state) for state in corpus.states}
    sources_by_action: dict[str, set[str]] = defaultdict(set)
    known_successor = set(states)
    invalid: set[str] = set()
    for receipt in corpus.receipts:
        action = _receipt_action(receipt)
        sources_by_action[action].add(_receipt_source(receipt))
        if _receipt_applicable(receipt):
            successor = getattr(receipt, "successor_state_hash", "")
            if not isinstance(successor, str) or successor not in known_successor:
                invalid.add(action)
    return tuple(sorted(
        action.action_id
        for action in corpus.actions
        if action.action_id not in invalid
        and sources_by_action.get(action.action_id, set()) == states
    ))


def _capsule_hash(capsule: Any) -> str:
    value = getattr(capsule, "capsule_hash", None)
    if callable(value):
        value = value()
    if isinstance(value, str):
        return _digest(value, "capsule hash")
    return _content_hash(capsule)


def infer_action_contracts(
    corpus: TransitionCorpus,
    *,
    capsule: Any | None = None,
) -> tuple[Any, ...]:
    """Infer finite action contracts from exact receipts.

    When no capsule is supplied, the coarsest action-congruent partition is
    computed from the finite corpus.  This guarantees the three declared
    finite conditions while retaining any unresolved evidence as witnesses.
    It does not claim universal applicability outside the sampled corpus.
    """

    if not isinstance(corpus, TransitionCorpus):
        raise TypeError("corpus must be a TransitionCorpus")
    from .capsule import audit_action_congruence, coarsest_action_congruent_partition
    complete_actions = _complete_action_ids(corpus)
    if not complete_actions:
        return ()
    selected = capsule
    if selected is None:
        selected = coarsest_action_congruent_partition(
            corpus.states,
            corpus.receipts,
            action_alphabet=complete_actions,
            closed_world=False,
        )
    audit = audit_action_congruence(
        selected,
        corpus.states,
        corpus.receipts,
        action_alphabet=complete_actions,
        closed_world=False,
    )
    # Preserve the audit's completeness bit.  Reconstructing contracts from
    # witnesses alone would falsely certify a singleton block whose enabled
    # successor was omitted by a bounded corpus.
    contracts = tuple(getattr(audit, "contracts", ()))
    return tuple(sorted(contracts, key=lambda value: str(getattr(value, "action", ""))))


def _infer_guard(action: CorpusAction, corpus: TransitionCorpus) -> dict[str, Any]:
    state_by_hash = {_state_hash(state): state for state in corpus.states}
    relevant = [receipt for receipt in corpus.receipts if _receipt_action(receipt) == action.action_id]
    positives = [state_by_hash[_receipt_source(receipt)] for receipt in relevant if _receipt_applicable(receipt) and _receipt_source(receipt) in state_by_hash]
    negatives = [state_by_hash[_receipt_source(receipt)] for receipt in relevant if not _receipt_applicable(receipt) and _receipt_source(receipt) in state_by_hash]
    if not positives:
        return {"equals": {}, "mode": "abstain", "positive_support": 0, "negative_support": len(negatives)}
    positive_features = [_state_features(state) for state in positives]
    negative_features = [_state_features(state) for state in negatives]
    # Greedy finite set cover over recurrent target-free coordinates.  Exact
    # dimensions and background color are intentionally omitted to avoid
    # literal task-local guards unless the executor itself requires them.
    candidates: list[tuple[str, Any, frozenset[int]]] = []
    for name in _INITIAL_FEATURES:
        values = [features.get(name) for features in positive_features]
        if not values or any(canonical_value(value) != canonical_value(values[0]) for value in values[1:]):
            continue
        excluded = frozenset(
            index
            for index, features in enumerate(negative_features)
            if canonical_value(features.get(name)) != canonical_value(values[0])
        )
        if excluded:
            candidates.append((name, values[0], excluded))
    remaining = set(range(len(negative_features)))
    equals: dict[str, Any] = {}
    while remaining:
        ranked = sorted(
            candidates,
            key=lambda item: (-len(remaining.intersection(item[2])), item[0], canonical_json(item[1])),
        )
        if not ranked or not remaining.intersection(ranked[0][2]):
            break
        name, value, excluded = ranked[0]
        equals[name] = canonical_value(value)
        remaining.difference_update(excluded)
        candidates = [item for item in candidates if item[0] != name]
    mode = "feature_guard" if not remaining else "executable_precondition"
    return {
        "equals": equals,
        "mode": mode,
        "positive_support": len(positives),
        "negative_support": len(negatives),
        "unresolved_negative_collisions": len(remaining),
    }


def _contract_valid(contract: Any) -> bool:
    certified = getattr(contract, "certified", None)
    if isinstance(certified, bool):
        return certified
    return bool(
        getattr(contract, "complete", False)
        and getattr(contract, "readout_congruent", False)
        and getattr(contract, "applicability_congruent", False)
        and getattr(contract, "successor_congruent", False)
        and not tuple(getattr(contract, "witness_hashes", ()))
    )


def _bank_id(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Mapping):
        return value.get("bank_id")
    return getattr(value, "bank_id", None)


def _bank_bundle_id(
    block6_bank_record: Mapping[str, Any] | None,
    block8_bank_record: Mapping[str, Any] | None,
    abstraction_bank: Any | None,
) -> str:
    return sha256_record({
        "block6": _bank_id(block6_bank_record),
        "block8": _bank_id(block8_bank_record),
        "block9": _bank_id(abstraction_bank),
    })


def _verify_action_bank_authorization(
    action: CorpusAction,
    *,
    block6_ids: frozenset[str],
    block8_ids: frozenset[str],
) -> None:
    if action.kind != "leaf":
        return
    payload = action.payload
    namespace = str(payload.get("namespace", ""))
    source_macro_id = str(payload.get("source_macro_id", ""))
    if namespace == "block6" and source_macro_id not in block6_ids:
        raise PermissionError("routed Block 6 action is not in the supplied stable bank")
    if namespace == "block8" and source_macro_id not in block8_ids:
        raise PermissionError("routed Block 8 action is not in the supplied stable bank")


def _execute_actions(actions: Sequence[CorpusAction], grid: Grid) -> tuple[Grid, int]:
    state = validate_grid(grid)
    executions = 0
    for action in actions:
        guard = action.guard
        if guard:
            mode = guard.get("mode", "feature_guard")
            if mode == "abstain" or mode not in {"feature_guard", "executable_precondition"}:
                raise ValueError("action applicability contract abstained")
            if not guard_matches(guard, state):
                raise ValueError("action applicability guard rejected the state")
        # Successful target-free execution is the final executable
        # precondition.  Do it once: CorpusAction.applicable would otherwise
        # execute a leaf/tool a second time merely as a probe.
        executions += 1
        state = action.execute(state)
    return state, executions


def _program_order(program: RoutedProgram) -> tuple[Any, ...]:
    return (program.total_cost, program.depth, program.semantic_hash, program.syntax_hash)


def _irreducible(
    actions: Sequence[CorpusAction],
    inputs: Sequence[Grid],
    targets: Sequence[Grid],
) -> tuple[bool, int]:
    """Reject any exact proper order-preserving action subsequence."""

    count = len(actions)
    if count < 2:
        return True, 0
    if count > 8:
        raise ValueError("irreducibility is hard-capped at eight actions")
    executions = 0
    for mask in range(1, (1 << count) - 1):
        outputs: list[Grid] = []
        valid = True
        for source in inputs:
            state = source
            for index, action in enumerate(actions):
                if not mask & (1 << index):
                    continue
                try:
                    state, used = _execute_actions((action,), state)
                    executions += used
                except (AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
                    valid = False
                    break
            if not valid:
                break
            outputs.append(state)
        if valid and tuple(outputs) == tuple(targets):
            return False, executions
    return True, executions


def _initial_collision_audit(corpus: TransitionCorpus) -> tuple[Any, tuple[Any, ...]]:
    from .capsule import audit_action_congruence

    initial = _feature_capsule(corpus)
    complete_actions = _complete_action_ids(corpus)
    witnesses = _witnesses(audit_action_congruence(
        initial,
        corpus.states,
        corpus.receipts,
        action_alphabet=complete_actions,
        closed_world=False,
    ))
    return initial, witnesses


def _coarsest_capsule(corpus: TransitionCorpus) -> Any:
    from .capsule import coarsest_action_congruent_partition

    complete_actions = _complete_action_ids(corpus)
    return coarsest_action_congruent_partition(
        corpus.states,
        corpus.receipts,
        action_alphabet=complete_actions,
        closed_world=False,
    )


def _seed_block9_programs(
    sanitized: TrainingTask,
    *,
    block6_bank_record: Mapping[str, Any] | None,
    block8_bank_record: Mapping[str, Any] | None,
    abstraction_bank: Any | None,
    enabled: bool,
) -> tuple[Any, ...]:
    if not enabled or block6_bank_record is None or block8_bank_record is None:
        return ()
    try:
        from komorebi_lasm_composition.compiler import compile_programs

        programs, _ = compile_programs(
            sanitized,
            block6_bank_record=block6_bank_record,
            block8_bank_record=block8_bank_record,
            abstraction_bank=abstraction_bank,
        )
        return tuple(programs)
    except (AssertionError, KeyError, PermissionError, RuntimeError, TypeError, ValueError, OverflowError):
        return ()


def compile_routed_programs(
    task: Mapping[str, Any] | TrainingTask,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
    abstraction_bank: Any | None = None,
    limits: object | None = None,
) -> tuple[tuple[RoutedProgram, ...], RoutingTrace]:
    """Compile exact action routes and require one held-out behavior class.

    Candidate generation observes only training pairs.  After routes and
    contracts are frozen, sanitized test *inputs* are executed to quotient
    behavior.  Attached test outputs cannot affect this function.
    """

    bounded = RoutingLimits.normalize(limits)
    sanitized = sanitize_training_task(task)
    seeds = _seed_block9_programs(
        sanitized,
        block6_bank_record=block6_bank_record,
        block8_bank_record=block8_bank_record,
        abstraction_bank=abstraction_bank,
        enabled=bounded.include_block9_seeds,
    )
    corpus = build_transition_corpus(
        sanitized,
        bounded.corpus_limits(),
        block6_bank_record=block6_bank_record,
        block8_bank_record=block8_bank_record,
        seed_programs=seeds,
        include_tools=bounded.include_tools,
    )
    initial_capsule, initial_witnesses = _initial_collision_audit(corpus)
    refined_capsule = _coarsest_capsule(corpus)
    contracts = infer_action_contracts(corpus, capsule=refined_capsule)
    contract_by_action = {
        str(getattr(contract, "action")): contract for contract in contracts
    }
    action_by_id = corpus.action_by_id
    bank_bundle = _bank_bundle_id(block6_bank_record, block8_bank_record, abstraction_bank)
    rejection_counts: Counter[str] = Counter()
    abstentions = 0
    replay_executions = 0
    compiled: dict[str, RoutedProgram] = {}

    for route in corpus.exact_routes:
        selected_actions: list[CorpusAction] = []
        contract_hashes: list[str] = []
        contract_records_json: list[str] = []
        authorized = True
        for action_id in route.action_ids:
            action = action_by_id.get(action_id)
            contract = contract_by_action.get(action_id)
            if action is None or contract is None or not _contract_valid(contract):
                authorized = False
                abstentions += 1
                rejection_counts["missing_or_incongruent_contract"] += 1
                break
            guard = _infer_guard(action, corpus)
            if guard.get("mode") == "abstain":
                authorized = False
                abstentions += 1
                rejection_counts["no_positive_applicability_support"] += 1
                break
            to_record = getattr(contract, "to_record", None)
            if not callable(to_record):
                authorized = False
                abstentions += 1
                rejection_counts["unserializable_contract"] += 1
                break
            try:
                encoded_contract = canonical_json(to_record())
            except (KeyError, TypeError, ValueError, OverflowError):
                authorized = False
                abstentions += 1
                rejection_counts["unserializable_contract"] += 1
                break
            selected_actions.append(action.with_guard(guard))
            contract_hashes.append(_content_hash(contract))
            contract_records_json.append(encoded_contract)
        if not authorized:
            continue
        program = RoutedProgram(
            actions=tuple(selected_actions),
            contract_hashes=tuple(contract_hashes),
            training_hashes=sanitized.training_hashes,
            bank_bundle_id=bank_bundle,
            corpus_id=corpus.corpus_id,
            contract_records_json=tuple(contract_records_json),
            contains_detour=route.contains_detour,
        )
        try:
            outputs = []
            for grid in sanitized.training_inputs:
                output, count = _execute_actions(program.actions, grid)
                replay_executions += count
                outputs.append(output)
            if tuple(outputs) != sanitized.training_outputs:
                rejection_counts["demonstration_replay"] += 1
                continue
        except (AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            rejection_counts["demonstration_runtime"] += 1
            continue
        irreducible, used = _irreducible(
            program.actions,
            sanitized.training_inputs,
            sanitized.training_outputs,
        )
        replay_executions += used
        if not irreducible:
            rejection_counts["reducible_program"] += 1
            continue
        prior = compiled.get(program.semantic_hash)
        if prior is None or _program_order(program) < _program_order(prior):
            compiled[program.semantic_hash] = program

    # Freeze programs before exposing them to test inputs.  Behavior quotient
    # is exact: a gauge-equivalent but raster-distinct output remains ambiguous
    # unless an explicit inverse output gauge proves a unique transport.
    behavior_groups: dict[str, list[RoutedProgram]] = defaultdict(list)
    gauge_groups: dict[str, set[str]] = defaultdict(set)
    for program in sorted(compiled.values(), key=_program_order):
        try:
            test_outputs: list[Grid] = []
            for grid in sanitized.test_inputs:
                output, count = _execute_actions(program.actions, grid)
                replay_executions += count
                test_outputs.append(output)
        except (AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            rejection_counts["test_applicability_abstention"] += 1
            abstentions += 1
            continue
        exact_behavior = sha256_record(tuple(test_outputs))
        behavior_groups[exact_behavior].append(program)
        try:
            from .gauge import canonical_gauge_orbit

            canonical_outputs = tuple(
                canonical_gauge_orbit(output).canonical_grid for output in test_outputs
            )
            gauge_groups[sha256_record(canonical_outputs)].add(exact_behavior)
        except (ImportError, AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            gauge_groups[exact_behavior].add(exact_behavior)

    # Exact duplicates merge safely.  Raster-distinct members of one gauge
    # orbit are measured but deliberately not collapsed without a transport.
    representatives = tuple(
        min(group, key=_program_order)
        for _, group in sorted(behavior_groups.items())
    )
    exact_merges = sum(max(0, len(group) - 1) for group in behavior_groups.values())
    gauge_ambiguities = sum(max(0, len(values) - 1) for values in gauge_groups.values())
    if gauge_ambiguities:
        rejection_counts["gauge_equivalent_but_raster_distinct"] += gauge_ambiguities
    result = tuple(sorted(representatives, key=_program_order))
    if bounded.require_unique_test_behavior and len(result) != 1:
        if len(result) > 1:
            rejection_counts["ambiguous_test_behaviors"] += len(result)
            abstentions += 1
        result = ()

    continued_batches = {
        transition.source_state_hashes
        for transition in corpus.transitions
        if transition.source_state_hashes != corpus.root_state_hashes
    }
    trace = RoutingTrace(
        root_states=len(corpus.root_state_hashes),
        continued_states=len(continued_batches),
        proposals_considered=corpus.proposals_considered,
        accepted_transitions=corpus.accepted_transitions,
        capsule_abstentions=abstentions,
        capsule_collisions=len(initial_witnesses),
        # Gauge signatures are diagnostic unless an explicit invertible
        # output transport authorizes the merge.  None is used here.
        gauge_quotient_merges=0,
        behavior_quotient_merges=exact_merges,
        actual_leaf_executions=corpus.actual_leaf_executions + replay_executions,
        exact_programs=len(compiled),
        behavior_classes=len(behavior_groups),
        counterfactual_states=corpus.counterfactual_states,
        semantic_detours=corpus.semantic_detours,
        contract_count=len(contracts),
        initial_capsule_hash=_capsule_hash(initial_capsule),
        refined_capsule_hash=_capsule_hash(refined_capsule),
        limit_reached=corpus.limit_reached,
        rejection_counts=tuple(sorted(rejection_counts.items())),
    )
    return result, trace


def execute_routed_program(
    program: RoutedProgram,
    grid: object,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
    abstraction_bank: Any | None = None,
) -> Grid:
    """Execute a sealed route under the exact bank bundle used to compile it."""

    if not isinstance(program, RoutedProgram):
        raise TypeError("program must be a RoutedProgram")
    supplied_bundle = _bank_bundle_id(block6_bank_record, block8_bank_record, abstraction_bank)
    if supplied_bundle != program.bank_bundle_id:
        raise PermissionError("routed program is not bound to the supplied bank bundle")
    block6_ids, block8_ids = verified_inherited_macro_ids(
        block6_bank_record=block6_bank_record,
        block8_bank_record=block8_bank_record,
    )
    for action in program.actions:
        _verify_action_bank_authorization(
            action,
            block6_ids=block6_ids,
            block8_ids=block8_ids,
        )
    if not program.contract_records_json:
        raise PermissionError("routed program lacks embedded action-contract evidence")
    from .model import ActionContract

    for encoded, expected_hash, action in zip(
        program.contract_records_json, program.contract_hashes, program.actions,
    ):
        contract = ActionContract.from_record(json.loads(encoded))
        if (
            not contract.certified
            or contract.action != action.action_id
            or contract.contract_hash != expected_hash
        ):
            raise PermissionError("routed action contract failed runtime verification")
    result, _ = _execute_actions(program.actions, validate_grid(grid))
    return result


__all__ = [
    "RoutedProgram",
    "RoutingLimits",
    "RoutingTrace",
    "compile_routed_programs",
    "execute_routed_program",
    "infer_action_contracts",
]
