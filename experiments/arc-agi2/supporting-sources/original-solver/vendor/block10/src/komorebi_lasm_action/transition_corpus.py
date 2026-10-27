"""Finite transition-corpus construction for Block 10.

This module is the labelled, training-only half of action routing.  It may use
demonstration targets to *propose and certify* an action, but every action is
frozen as a target-free executable record before it enters the corpus.  Test
outputs are structurally discarded by :func:`sanitize_training_task`.

The corpus contains exact raster states.  Capsules and gauges are indices over
those states; neither is allowed to replace the authoritative grids.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, replace
import json
from numbers import Integral
from typing import Any, Callable, Iterable, Literal, Mapping, Sequence

from komorebi_lasm_composition.model import (
    Grid,
    LeafInvocation,
    canonical_json,
    canonical_value,
    sha256_record,
    validate_grid,
)
from komorebi_lasm_composition.residual import (
    certify_transition,
    derive_example_residual,
    derive_residual_batch,
    infer_background,
)
from komorebi_lasm_composition.stages import (
    execute_leaf,
    propose_atomic_stages,
    propose_endpoint_closers,
)
from komorebi_lasm_composition.task import TrainingTask, sanitize_training_task


ActionKind = Literal["leaf", "tool"]
TransitionKind = Literal[
    "monotone",
    "shape_correction",
    "semantic_detour",
    "detour_recovery",
    "seed_prefix",
    "counterfactual",
]

_ACTION_KINDS = frozenset({"leaf", "tool"})
_TRANSITION_KINDS = frozenset({
    "monotone",
    "shape_correction",
    "semantic_detour",
    "detour_recovery",
    "seed_prefix",
    "counterfactual",
})


def _positive_int(value: object, label: str, *, allow_zero: bool = False) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise TypeError(f"{label} must be an integer")
    result = int(value)
    minimum = 0 if allow_zero else 1
    if result < minimum:
        qualifier = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{label} must be {qualifier}")
    return result


def _trimmed(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{label} must be a nonempty trimmed string")
    return value


def _digest(value: object, label: str) -> str:
    text = _trimmed(value, label)
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")
    return text


def _record_without_hashes(record: Mapping[str, Any]) -> dict[str, Any]:
    """Remove derivable hashes before re-validating an executable payload."""

    return {
        str(key): canonical_value(value)
        for key, value in record.items()
        if key not in {"content_hash", "semantic_hash", "syntax_hash", "tool_id"}
    }


def _leaf_from_record(record: Mapping[str, Any]) -> LeafInvocation:
    required = {
        "namespace", "family", "macro_schema", "parameters",
        "source_macro_id", "cost", "status",
    }
    if not required.issubset(record):
        missing = sorted(required - set(record))
        raise ValueError(f"leaf action payload is missing {missing}")
    parameters = record["parameters"]
    if not isinstance(parameters, Mapping):
        raise TypeError("leaf action parameters must be a mapping")
    return LeafInvocation.from_parameters(
        namespace=str(record["namespace"]),  # type: ignore[arg-type]
        family=str(record["family"]),
        macro_schema=str(record["macro_schema"]),
        parameters=dict(parameters),
        source_macro_id=str(record["source_macro_id"]),
        cost=int(record["cost"]),
        status=str(record["status"]),
    )


def _tool_from_record(record: Mapping[str, Any]) -> Any:
    """Reconstruct a tool without depending on one in-progress constructor."""

    from . import tools as tool_module

    tool_type = getattr(tool_module, "ToolProgram", None)
    if tool_type is None:
        raise RuntimeError("ToolProgram is unavailable")
    constructor = getattr(tool_type, "from_record", None)
    if callable(constructor):
        return constructor(record)
    parameters = record.get("parameters", {})
    if not isinstance(parameters, Mapping):
        raise TypeError("tool parameters must be a mapping")
    from_parameters = getattr(tool_type, "from_parameters", None)
    if callable(from_parameters):
        return from_parameters(
            selector=str(record.get("selector", "global")),
            relation=str(record.get("relation", "none")),
            geometry=str(record.get("geometry", "identity")),
            effect=str(record.get("effect", "identity")),
            closure=str(record.get("closure", "once")),
            parameters=dict(parameters),
            cost=int(record.get("cost", 1)),
        )
    parameters_json = record.get("parameters_json", canonical_json(parameters))
    return tool_type(
        selector=str(record.get("selector", "global")),
        relation=str(record.get("relation", "none")),
        geometry=str(record.get("geometry", "identity")),
        effect=str(record.get("effect", "identity")),
        closure=str(record.get("closure", "once")),
        parameters_json=str(parameters_json),
        cost=int(record.get("cost", 1)),
    )


@dataclass(frozen=True, slots=True)
class CorpusAction:
    """A canonical target-free executable action."""

    kind: ActionKind
    payload_json: str
    cost: int
    guard_json: str = "{}"
    schema_version: int = 1

    def __post_init__(self) -> None:
        if self.kind not in _ACTION_KINDS:
            raise ValueError("unknown corpus action kind")
        _positive_int(self.cost, "action cost")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")
        for label, encoded in (("payload_json", self.payload_json), ("guard_json", self.guard_json)):
            if not isinstance(encoded, str):
                raise TypeError(f"{label} must be a string")
            try:
                decoded = json.loads(encoded)
            except json.JSONDecodeError as error:
                raise ValueError(f"{label} must contain valid JSON") from error
            if not isinstance(decoded, dict):
                raise TypeError(f"{label} must encode an object")
            if canonical_json(decoded) != encoded:
                raise ValueError(f"{label} must use canonical JSON")

    @classmethod
    def from_leaf(cls, leaf: LeafInvocation) -> "CorpusAction":
        if not isinstance(leaf, LeafInvocation):
            raise TypeError("leaf must be a LeafInvocation")
        payload = {
            "namespace": leaf.namespace,
            "family": leaf.family,
            "macro_schema": leaf.macro_schema,
            "parameters": leaf.parameters_record,
            "source_macro_id": leaf.source_macro_id,
            "cost": int(leaf.cost),
            "status": leaf.status,
        }
        return cls("leaf", canonical_json(payload), int(leaf.cost))

    @classmethod
    def from_tool(cls, tool: Any) -> "CorpusAction":
        to_record = getattr(tool, "to_record", None)
        if not callable(to_record):
            raise TypeError("tool must expose to_record()")
        record = to_record()
        if not isinstance(record, Mapping):
            raise TypeError("tool record must be a mapping")
        payload = _record_without_hashes(record)
        return cls("tool", canonical_json(payload), int(getattr(tool, "cost", payload.get("cost", 1))))

    @property
    def payload(self) -> dict[str, Any]:
        value = json.loads(self.payload_json)
        assert isinstance(value, dict)
        return value

    @property
    def guard(self) -> dict[str, Any]:
        value = json.loads(self.guard_json)
        assert isinstance(value, dict)
        return value

    @property
    def semantic_record(self) -> dict[str, Any]:
        # The guard is evidence/authorization, not action semantics.
        return {
            "schema": "komorebi.lasm_action.corpus_action_semantics",
            "schema_version": self.schema_version,
            "kind": self.kind,
            "payload": self.payload,
            "input_type": "grid",
            "output_type": "grid",
        }

    @property
    def action_id(self) -> str:
        return sha256_record(self.semantic_record)

    def with_guard(self, guard: Mapping[str, Any]) -> "CorpusAction":
        return replace(self, guard_json=canonical_json(guard))

    def execute(self, grid: object) -> Grid:
        source = validate_grid(grid)
        if self.kind == "leaf":
            return validate_grid(execute_leaf(_leaf_from_record(self.payload), source))
        from .tools import execute_tool

        return validate_grid(execute_tool(_tool_from_record(self.payload), source))

    def applicable(self, grid: object) -> bool:
        source = validate_grid(grid)
        if self.guard:
            mode = self.guard.get("mode", "feature_guard")
            if mode == "abstain" or mode not in {"feature_guard", "executable_precondition"}:
                return False
            if not guard_matches(self.guard, source):
                return False
        if self.kind == "tool":
            try:
                from .tools import tool_applicable
            except ImportError:
                tool_applicable = None
            if callable(tool_applicable):
                try:
                    return bool(tool_applicable(_tool_from_record(self.payload), source))
                except (KeyError, RuntimeError, TypeError, ValueError, OverflowError):
                    return False
        try:
            self.execute(source)
            return True
        except (AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            return False

    def to_record(self) -> dict[str, Any]:
        record = {
            **self.semantic_record,
            "action_id": self.action_id,
            "cost": int(self.cost),
            "guard": self.guard,
        }
        record["content_hash"] = sha256_record(record)
        return record


def grid_feature_map(grid: object) -> dict[str, Any]:
    """Return small target-free coordinates suitable for applicability guards.

    Raw hashes, chronology, task identifiers, and one-use names are deliberately
    absent.  These features may route an action but never replace ``grid``.
    """

    source = validate_grid(grid)
    height, width = len(source), len(source[0])
    counts = Counter(value for row in source for value in row)
    maximum = max(counts.values())
    backgrounds = sorted(color for color, count in counts.items() if count == maximum)
    background = backgrounds[0]
    foreground = {(row, column) for row in range(height) for column in range(width) if source[row][column] != background}

    def components(connectivity: int) -> int:
        remaining = set(foreground)
        total = 0
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if connectivity == 8:
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        while remaining:
            total += 1
            stack = [remaining.pop()]
            while stack:
                row, column = stack.pop()
                for dy, dx in directions:
                    neighbor = (row + dy, column + dx)
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        stack.append(neighbor)
        return total

    border = list(source[0]) + list(source[-1])
    if height > 2:
        border += [source[row][0] for row in range(1, height - 1)]
        border += [source[row][-1] for row in range(1, height - 1)]
    if foreground:
        rows = [cell[0] for cell in foreground]
        columns = [cell[1] for cell in foreground]
        bbox = (max(rows) - min(rows) + 1, max(columns) - min(columns) + 1)
        touches = any(row in {0, height - 1} or column in {0, width - 1} for row, column in foreground)
    else:
        bbox = (0, 0)
        touches = False
    return {
        "height": height,
        "width": width,
        "square": height == width,
        "uniform": len(counts) == 1,
        "palette_size": len(counts),
        "background": background,
        "background_unique_mode": len(backgrounds) == 1,
        "foreground_cells": len(foreground),
        "components4": components(4),
        "components8": components(8),
        "bbox_height": bbox[0],
        "bbox_width": bbox[1],
        "foreground_touches_border": touches,
        "uniform_border": len(set(border)) == 1,
        "symmetric_h": source == tuple(tuple(reversed(row)) for row in source),
        "symmetric_v": source == tuple(reversed(source)),
    }


def guard_matches(guard: Mapping[str, Any], grid: object) -> bool:
    features = grid_feature_map(grid)
    required = guard.get("equals", {})
    if not isinstance(required, Mapping):
        return False
    for name, expected in required.items():
        if name not in features or canonical_value(features[name]) != canonical_value(expected):
            return False
    return True


@dataclass(frozen=True, slots=True)
class BatchTransition:
    source_state_hashes: tuple[str, ...]
    action_id: str
    successor_state_hashes: tuple[str, ...]
    kind: TransitionKind
    depth: int
    exact_after: bool
    effect_signature: tuple[str, ...] = ()
    schema_version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_state_hashes", tuple(self.source_state_hashes))
        object.__setattr__(self, "successor_state_hashes", tuple(self.successor_state_hashes))
        object.__setattr__(self, "effect_signature", tuple(self.effect_signature))
        if not self.source_state_hashes or len(self.source_state_hashes) != len(self.successor_state_hashes):
            raise ValueError("a batch transition requires equal nonempty state vectors")
        for index, value in enumerate(self.source_state_hashes):
            _digest(value, f"source_state_hashes[{index}]")
        for index, value in enumerate(self.successor_state_hashes):
            _digest(value, f"successor_state_hashes[{index}]")
        _digest(self.action_id, "action_id")
        if self.kind not in _TRANSITION_KINDS:
            raise ValueError("unknown transition kind")
        _positive_int(self.depth, "transition depth")
        if not isinstance(self.exact_after, bool):
            raise TypeError("exact_after must be Boolean")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    @property
    def transition_id(self) -> str:
        return sha256_record(self.identity_record)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.batch_transition",
            "schema_version": self.schema_version,
            "source_state_hashes": list(self.source_state_hashes),
            "action_id": self.action_id,
            "successor_state_hashes": list(self.successor_state_hashes),
            "kind": self.kind,
            "depth": int(self.depth),
            "exact_after": self.exact_after,
            "effect_signature": list(self.effect_signature),
        }

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "transition_id": self.transition_id}
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class CertifiedRoute:
    action_ids: tuple[str, ...]
    transition_ids: tuple[str, ...]
    total_cost: int
    contains_detour: bool = False
    schema_version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(self, "action_ids", tuple(self.action_ids))
        object.__setattr__(self, "transition_ids", tuple(self.transition_ids))
        if not self.action_ids or len(self.action_ids) != len(self.transition_ids):
            raise ValueError("a route requires equal nonempty action and transition vectors")
        for index, value in enumerate(self.action_ids):
            _digest(value, f"action_ids[{index}]")
        for index, value in enumerate(self.transition_ids):
            _digest(value, f"transition_ids[{index}]")
        _positive_int(self.total_cost, "route cost")
        if not isinstance(self.contains_detour, bool):
            raise TypeError("contains_detour must be Boolean")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    @property
    def route_id(self) -> str:
        return sha256_record(self.identity_record)

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.certified_route",
            "schema_version": self.schema_version,
            "action_ids": list(self.action_ids),
            "transition_ids": list(self.transition_ids),
            "total_cost": int(self.total_cost),
            "contains_detour": self.contains_detour,
        }

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "route_id": self.route_id}
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class TransitionCorpusLimits:
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

    def __post_init__(self) -> None:
        for name in (
            "max_depth", "max_states", "max_actions", "max_proposals_per_state",
            "max_transitions", "max_receipts", "max_counterfactual_states",
            "max_leaf_executions", "max_total_cost",
        ):
            _positive_int(getattr(self, name), name)
        _positive_int(self.max_detours_per_route, "max_detours_per_route", allow_zero=True)
        if not isinstance(self.allow_semantic_detours, bool):
            raise TypeError("allow_semantic_detours must be Boolean")
        if self.max_depth > 8:
            raise ValueError("transition depth is hard-capped at eight")
        if self.max_actions > 512 or self.max_proposals_per_state > 512:
            raise ValueError("action and proposal limits are hard-capped at 512")

    @classmethod
    def normalize(cls, limits: object | None) -> "TransitionCorpusLimits":
        if limits is None:
            return cls()
        if isinstance(limits, cls):
            return limits
        defaults = cls()
        values: dict[str, Any] = {}
        aliases = {
            "max_states": ("max_states", "max_frontier"),
            "max_actions": ("max_actions", "max_proposals_per_state"),
            "max_transitions": ("max_transitions", "max_expansions"),
            "max_leaf_executions": ("max_leaf_executions", "max_expansions"),
        }
        for name in cls.__dataclass_fields__:
            candidates = aliases.get(name, (name,))
            value = next((getattr(limits, item) for item in candidates if hasattr(limits, item)), getattr(defaults, name))
            values[name] = value
        # A Block 9 frontier is not a safe proxy for total corpus states.
        if not hasattr(limits, "max_states") and hasattr(limits, "max_frontier"):
            values["max_states"] = max(int(values["max_states"]), 64)
        return cls(**values)


@dataclass(frozen=True, slots=True)
class TransitionCorpus:
    states: tuple[Any, ...]
    receipts: tuple[Any, ...]
    actions: tuple[CorpusAction, ...]
    transitions: tuple[BatchTransition, ...]
    exact_routes: tuple[CertifiedRoute, ...]
    training_hashes: tuple[str, ...]
    root_state_hashes: tuple[str, ...]
    proposals_considered: int
    accepted_transitions: int
    actual_leaf_executions: int
    counterfactual_states: int
    semantic_detours: int
    limit_reached: str = ""
    schema_version: int = 1

    def __post_init__(self) -> None:
        for name in ("states", "receipts", "actions", "transitions", "exact_routes", "training_hashes", "root_state_hashes"):
            object.__setattr__(self, name, tuple(getattr(self, name)))
        if not self.states or not self.root_state_hashes:
            raise ValueError("transition corpus needs root states")
        if not all(isinstance(action, CorpusAction) for action in self.actions):
            raise TypeError("actions must contain CorpusAction records")
        if not all(isinstance(value, BatchTransition) for value in self.transitions):
            raise TypeError("transitions must contain BatchTransition records")
        if not all(isinstance(value, CertifiedRoute) for value in self.exact_routes):
            raise TypeError("exact_routes must contain CertifiedRoute records")
        for index, value in enumerate(self.training_hashes):
            _digest(value, f"training_hashes[{index}]")
        for index, value in enumerate(self.root_state_hashes):
            _digest(value, f"root_state_hashes[{index}]")
        for name in (
            "proposals_considered", "accepted_transitions", "actual_leaf_executions",
            "counterfactual_states", "semantic_detours",
        ):
            _positive_int(getattr(self, name), name, allow_zero=True)
        if not isinstance(self.limit_reached, str):
            raise TypeError("limit_reached must be a string")
        if self.schema_version != 1:
            raise ValueError("schema_version must equal 1")

    @property
    def action_by_id(self) -> dict[str, CorpusAction]:
        return {action.action_id: action for action in self.actions}

    @property
    def corpus_id(self) -> str:
        return sha256_record(self.identity_record)

    @property
    def identity_record(self) -> dict[str, Any]:
        def content_id(value: Any) -> str:
            for name in ("content_hash", "state_hash", "receipt_hash"):
                item = getattr(value, name, None)
                if callable(item):
                    item = item()
                if isinstance(item, str) and item:
                    return item
            to_record = getattr(value, "to_record", None)
            return sha256_record(to_record() if callable(to_record) else repr(value))

        return {
            "schema": "komorebi.lasm_action.transition_corpus",
            "schema_version": self.schema_version,
            "states": [content_id(value) for value in self.states],
            "receipts": [content_id(value) for value in self.receipts],
            "actions": [value.action_id for value in self.actions],
            "transitions": [value.transition_id for value in self.transitions],
            "exact_routes": [value.route_id for value in self.exact_routes],
            "training_hashes": list(self.training_hashes),
            "root_state_hashes": list(self.root_state_hashes),
            "proposals_considered": int(self.proposals_considered),
            "accepted_transitions": int(self.accepted_transitions),
            "actual_leaf_executions": int(self.actual_leaf_executions),
            "counterfactual_states": int(self.counterfactual_states),
            "semantic_detours": int(self.semantic_detours),
            "limit_reached": self.limit_reached,
        }

    def to_record(self) -> dict[str, Any]:
        record = {
            **self.identity_record,
            "corpus_id": self.corpus_id,
            "state_records": [value.to_record() for value in self.states],
            "receipt_records": [value.to_record() for value in self.receipts],
            "action_records": [value.to_record() for value in self.actions],
            "transition_records": [value.to_record() for value in self.transitions],
            "route_records": [value.to_record() for value in self.exact_routes],
        }
        record["content_hash"] = sha256_record(record)
        return record


@dataclass(frozen=True, slots=True)
class _BatchNode:
    currents: tuple[Grid, ...]
    state_hashes: tuple[str, ...]
    action_ids: tuple[str, ...]
    transition_ids: tuple[str, ...]
    depth: int
    total_cost: int
    detours: int
    visited: tuple[str, ...]


def _state_hash(state: Any) -> str:
    value = getattr(state, "state_hash", None)
    if callable(value):
        value = value()
    if not isinstance(value, str):
        value = getattr(state, "content_hash", None)
        if callable(value):
            value = value()
    if not isinstance(value, str):
        to_record = getattr(state, "to_record", None)
        value = sha256_record(to_record() if callable(to_record) else repr(state))
    return _digest(value, "state hash")


def _receipt_hash(receipt: Any) -> str:
    for name in ("receipt_hash", "content_hash"):
        value = getattr(receipt, name, None)
        if callable(value):
            value = value()
        if isinstance(value, str):
            return value
    to_record = getattr(receipt, "to_record", None)
    return sha256_record(to_record() if callable(to_record) else repr(receipt))


def _readout(current: Grid, target: Grid, background: int) -> dict[str, Any]:
    residual = derive_example_residual(current, target, background)
    return {
        "shape_matches": residual.current_shape == residual.target_shape,
        "measure": list(residual.measure),
        "obstruction_kinds": list(residual.obstruction_kinds),
        "exact": residual.exact,
    }


def _make_static_state(current: Grid, target: Grid, background: int, origin: str) -> Any:
    from .model import AmbientPacket, StaticTransitionState

    features = grid_feature_map(current)
    ambient = AmbientPacket(
        features=features,
        packet_kind="static",
        # Origin is derivation evidence, not a predictive coordinate.  Keeping
        # provenance constant prevents one raster from acquiring distinct
        # identities merely because two routes reached it.
        provenance=("transition_corpus:static_arc",),
    )
    return StaticTransitionState(
        grid=current,
        readout=_readout(current, target, background),
        ambient=ambient,
        history=(),
        state_name="static_arc",
    )


def _make_receipt(
    source_hash: str,
    action: CorpusAction,
    applicable: bool,
    successor_hash: str = "",
    *,
    evidence_kind: str,
) -> Any:
    from .model import ActionReceipt

    return ActionReceipt(
        source_state_hash=source_hash,
        action=action.action_id,
        applicable=bool(applicable),
        successor_state_hash=successor_hash,
        parameters={"kind": action.kind},
        evidence_kind=evidence_kind,
    )


def _effect_signature(before: Grid, after: Grid) -> str:
    before_shape = (len(before), len(before[0]))
    after_shape = (len(after), len(after[0]))
    if before_shape != after_shape:
        dh = after_shape[0] - before_shape[0]
        dw = after_shape[1] - before_shape[1]
        return f"shape:{(dh > 0) - (dh < 0)}:{(dw > 0) - (dw < 0)}"
    changed = [(left, right) for a, b in zip(before, after) for left, right in zip(a, b) if left != right]
    if not changed:
        return "noop"
    mappings: dict[int, set[int]] = {}
    for left, right in changed:
        mappings.setdefault(left, set()).add(right)
    if all(len(values) == 1 for values in mappings.values()):
        return "recolor:" + canonical_json({str(key): next(iter(values)) for key, values in sorted(mappings.items())})
    before_bg, after_bg = infer_background(before), infer_background(after)
    before_support = sum(value != before_bg for row in before for value in row)
    after_support = sum(value != after_bg for row in after for value in row)
    delta = after_support - before_support
    return f"support:{(delta > 0) - (delta < 0)}"


def _consistent_effect(before: Sequence[Grid], after: Sequence[Grid]) -> tuple[str, ...] | None:
    signatures = tuple(_effect_signature(left, right) for left, right in zip(before, after))
    coarse = tuple(signature.split(":", 1)[0] for signature in signatures)
    if len(set(coarse)) != 1 or coarse[0] == "noop":
        return None
    return signatures


def _execute_batch(action: CorpusAction, grids: Sequence[Grid], counter: list[int], cap: int) -> tuple[Grid, ...] | None:
    outputs: list[Grid] = []
    for grid in grids:
        if counter[0] >= cap:
            return None
        counter[0] += 1
        try:
            outputs.append(action.execute(grid))
        except (AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            return None
    return tuple(outputs)


def _target_aware_actions(
    currents: tuple[Grid, ...],
    targets: tuple[Grid, ...],
    *,
    limit: int,
    block6_bank_record: Mapping[str, Any] | None,
    block8_bank_record: Mapping[str, Any] | None,
    include_tools: bool,
) -> tuple[CorpusAction, ...]:
    actions: dict[str, CorpusAction] = {}
    residual = derive_residual_batch(currents, targets)
    try:
        leaves = propose_atomic_stages(currents, targets, residual, budget=limit)
    except (KeyError, RuntimeError, TypeError, ValueError, OverflowError):
        leaves = ()
    for leaf in leaves:
        action = CorpusAction.from_leaf(leaf)
        actions[action.action_id] = action

    # Endpoint compilation is now attempted at every certified state.  Safety
    # comes from stable-bank provenance, exact replay, and the applicability
    # contract, not the name of the preceding family.
    if block6_bank_record is not None or block8_bank_record is not None:
        try:
            endpoints = propose_endpoint_closers(
                currents,
                targets,
                block6_bank_record=block6_bank_record,
                block8_bank_record=block8_bank_record,
                budget=limit,
            )
        except (KeyError, PermissionError, RuntimeError, TypeError, ValueError, OverflowError):
            endpoints = ()
        for leaf in endpoints:
            action = CorpusAction.from_leaf(leaf)
            actions[action.action_id] = action

    if include_tools:
        try:
            from . import tools as tool_module

            proposer = getattr(tool_module, "propose_tool_programs", None)
            if callable(proposer):
                try:
                    tool_limits_type = getattr(tool_module, "ToolSynthesisLimits")
                    tool_limits = tool_limits_type(
                        max_programs=max(64, min(4_096, limit * 8)),
                        max_executions=max(128, min(16_384, limit * max(1, len(currents)) * 8)),
                        max_candidates=max(1, min(64, limit)),
                    )
                    programs = proposer(currents, targets, tool_limits)
                except (AttributeError, TypeError):
                    programs = proposer(currents, targets)
            else:
                programs = ()
            for program in tuple(programs)[:limit]:
                action = CorpusAction.from_tool(program)
                actions[action.action_id] = action
        except (ImportError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            pass
    return tuple(sorted(actions.values(), key=lambda value: (value.cost, value.kind, value.action_id))[:limit])


def _transition_certificate(
    before: tuple[Grid, ...],
    after: tuple[Grid, ...],
    targets: tuple[Grid, ...],
    backgrounds: tuple[int, ...],
    visited: Sequence[str],
) -> tuple[str, Any] | None:
    modes = ("residual_subset", "shape_correction", "strict_descent")
    for mode in modes:
        try:
            certificate = certify_transition(
                before,
                after,
                targets,
                mode,  # type: ignore[arg-type]
                root_backgrounds=backgrounds,
                visited_state_hashes=visited,
            )
        except (KeyError, RuntimeError, TypeError, ValueError, OverflowError):
            certificate = None
        if certificate is not None:
            kind = "shape_correction" if mode == "shape_correction" else "monotone"
            return kind, certificate
    return None


def _batch_behavior(grids: Sequence[Grid]) -> str:
    return sha256_record(tuple(grids))


def _program_leaves(program: Any) -> tuple[LeafInvocation, ...]:
    leaves = getattr(program, "leaves", ())
    if not isinstance(leaves, Sequence):
        return ()
    return tuple(leaf for leaf in leaves if isinstance(leaf, LeafInvocation))


def build_transition_corpus(
    task: Mapping[str, Any] | TrainingTask,
    limits: object | None = None,
    *,
    block6_bank_record: Mapping[str, Any] | None = None,
    block8_bank_record: Mapping[str, Any] | None = None,
    seed_programs: Sequence[Any] = (),
    include_tools: bool = True,
) -> TransitionCorpus:
    """Build a finite state/action corpus from labelled demonstrations.

    Sources are roots, certified prefixes, bounded counterfactual executions,
    and optional replayed Block 9 prefixes.  A non-monotone transition is
    admitted to the search graph only with a one-step recovery that makes net
    certified progress from the pre-detour state.  Counterfactual states never
    become search prefixes merely because their execution succeeded.
    """

    bounded = TransitionCorpusLimits.normalize(limits)
    sanitized = sanitize_training_task(task)
    targets = sanitized.training_outputs
    backgrounds = tuple(infer_background(grid) for grid in sanitized.training_inputs)
    states: list[Any] = []
    state_cache: dict[tuple[int, str], Any] = {}
    actions: dict[str, CorpusAction] = {}
    transitions: list[BatchTransition] = []
    routes: dict[tuple[str, ...], CertifiedRoute] = {}
    proposal_count = 0
    accepted_count = 0
    detour_count = 0
    execution_counter = [0]
    limit_reached = ""

    def state_for(index: int, grid: Grid, origin: str) -> Any:
        key = (index, sha256_record(grid))
        prior = state_cache.get(key)
        if prior is not None:
            return prior
        if len(states) >= bounded.max_states:
            raise OverflowError("max_states")
        value = _make_static_state(grid, targets[index], backgrounds[index], origin)
        state_cache[key] = value
        states.append(value)
        return value

    try:
        root_states = tuple(state_for(index, grid, "root") for index, grid in enumerate(sanitized.training_inputs))
    except OverflowError as error:
        raise ValueError("max_states is smaller than the demonstration count") from error
    root_hashes = tuple(_state_hash(value) for value in root_states)
    root_behavior = _batch_behavior(sanitized.training_inputs)
    frontier: deque[_BatchNode] = deque((
        _BatchNode(
            currents=sanitized.training_inputs,
            state_hashes=root_hashes,
            action_ids=(),
            transition_ids=(),
            depth=0,
            total_cost=0,
            detours=0,
            visited=(root_behavior,),
        ),
    ))
    best_behavior: dict[str, tuple[int, int]] = {root_behavior: (0, 0)}

    def register_transition(
        node: _BatchNode,
        action: CorpusAction,
        after: tuple[Grid, ...],
        kind: TransitionKind,
        *,
        effect: tuple[str, ...],
        detours: int,
    ) -> _BatchNode | None:
        nonlocal accepted_count, limit_reached
        if len(transitions) >= bounded.max_transitions:
            limit_reached = "max_transitions"
            return None
        if node.total_cost + action.cost > bounded.max_total_cost:
            return None
        try:
            successor_states = tuple(state_for(index, grid, kind) for index, grid in enumerate(after))
        except OverflowError:
            limit_reached = "max_states"
            return None
        exact = after == targets
        transition = BatchTransition(
            source_state_hashes=node.state_hashes,
            action_id=action.action_id,
            successor_state_hashes=tuple(_state_hash(value) for value in successor_states),
            kind=kind,
            depth=node.depth + 1,
            exact_after=exact,
            effect_signature=effect,
        )
        transitions.append(transition)
        accepted_count += 1
        child = _BatchNode(
            currents=after,
            state_hashes=transition.successor_state_hashes,
            action_ids=node.action_ids + (action.action_id,),
            transition_ids=node.transition_ids + (transition.transition_id,),
            depth=node.depth + 1,
            total_cost=node.total_cost + action.cost,
            detours=detours,
            visited=node.visited + (_batch_behavior(after),),
        )
        if exact:
            route = CertifiedRoute(
                action_ids=child.action_ids,
                transition_ids=child.transition_ids,
                total_cost=child.total_cost,
                contains_detour=child.detours > 0,
            )
            prior = routes.get(route.action_ids)
            if prior is None or (route.total_cost, route.route_id) < (prior.total_cost, prior.route_id):
                routes[route.action_ids] = route
        return child

    # Replay caller-supplied Block 9 programs as certified prefixes.  This path
    # never trusts their materialized outputs; it executes every leaf anew.
    for program in tuple(seed_programs):
        leaves = _program_leaves(program)
        if not leaves or len(leaves) > bounded.max_depth:
            continue
        node = frontier[0]
        for leaf in leaves:
            action = CorpusAction.from_leaf(leaf)
            actions.setdefault(action.action_id, action)
            after = _execute_batch(action, node.currents, execution_counter, bounded.max_leaf_executions)
            if after is None:
                break
            certificate = _transition_certificate(node.currents, after, targets, backgrounds, node.visited)
            if certificate is None:
                break
            effect = _consistent_effect(node.currents, after) or tuple(_effect_signature(a, b) for a, b in zip(node.currents, after))
            child = register_transition(node, action, after, "seed_prefix", effect=effect, detours=node.detours)
            if child is None:
                break
            node = child

    while frontier and not limit_reached:
        node = frontier.popleft()
        if node.depth >= bounded.max_depth or node.currents == targets:
            continue
        proposed = _target_aware_actions(
            node.currents,
            targets,
            limit=bounded.max_proposals_per_state,
            block6_bank_record=block6_bank_record,
            block8_bank_record=block8_bank_record,
            include_tools=include_tools,
        )
        for action in proposed:
            if len(actions) >= bounded.max_actions and action.action_id not in actions:
                limit_reached = "max_actions"
                break
            actions.setdefault(action.action_id, action)
            proposal_count += 1
            after = _execute_batch(action, node.currents, execution_counter, bounded.max_leaf_executions)
            if after is None:
                if execution_counter[0] >= bounded.max_leaf_executions:
                    limit_reached = "max_leaf_executions"
                    break
                continue
            behavior = _batch_behavior(after)
            if behavior in node.visited or after == node.currents:
                continue
            effect = _consistent_effect(node.currents, after)
            certificate = _transition_certificate(node.currents, after, targets, backgrounds, node.visited)
            if certificate is not None:
                kind = certificate[0]
                child = register_transition(
                    node,
                    action,
                    after,
                    kind,  # type: ignore[arg-type]
                    effect=effect or tuple(_effect_signature(a, b) for a, b in zip(node.currents, after)),
                    detours=node.detours,
                )
                if child is None or child.currents == targets:
                    continue
                prior = best_behavior.get(behavior)
                rank = (child.total_cost, child.depth)
                if child.depth < bounded.max_depth and (prior is None or rank < prior):
                    best_behavior[behavior] = rank
                    frontier.append(child)
                continue

            # Semantic detours are not accepted on appearance.  They need a
            # uniform typed effect and a bounded recovery action whose net
            # result is certifiably better than the state before the detour.
            if (
                not bounded.allow_semantic_detours
                or node.detours >= bounded.max_detours_per_route
                or node.depth + 2 > bounded.max_depth
                or effect is None
            ):
                continue
            recovery_actions = _target_aware_actions(
                after,
                targets,
                limit=min(32, bounded.max_proposals_per_state),
                block6_bank_record=block6_bank_record,
                block8_bank_record=block8_bank_record,
                include_tools=include_tools,
            )
            recovery_found = False
            for recovery in recovery_actions:
                if len(actions) >= bounded.max_actions and recovery.action_id not in actions:
                    break
                actions.setdefault(recovery.action_id, recovery)
                proposal_count += 1
                final = _execute_batch(recovery, after, execution_counter, bounded.max_leaf_executions)
                if final is None or final == after or _batch_behavior(final) in node.visited:
                    continue
                net = _transition_certificate(node.currents, final, targets, backgrounds, node.visited)
                if net is None:
                    continue
                # A detour must actually enable the recovery.  If the same
                # recovery already makes certified progress at the pre-detour
                # state, the longer word is reducible and is not admitted.
                direct_recovery = _execute_batch(
                    recovery,
                    node.currents,
                    execution_counter,
                    bounded.max_leaf_executions,
                )
                if direct_recovery is not None and _transition_certificate(
                    node.currents,
                    direct_recovery,
                    targets,
                    backgrounds,
                    node.visited,
                ) is not None:
                    continue
                # Admit the detour and its recovery atomically.  A budget
                # boundary must never leave an orphan non-monotone edge in
                # the certified transition graph.
                if len(transitions) + 2 > bounded.max_transitions:
                    limit_reached = "max_transitions"
                    break
                if node.total_cost + action.cost + recovery.cost > bounded.max_total_cost:
                    continue
                required_state_keys = {
                    (index, sha256_record(grid))
                    for grids in (after, final)
                    for index, grid in enumerate(grids)
                }
                missing_state_count = sum(
                    key not in state_cache for key in required_state_keys
                )
                if len(states) + missing_state_count > bounded.max_states:
                    limit_reached = "max_states"
                    break
                detour_node = register_transition(
                    node, action, after, "semantic_detour", effect=effect, detours=node.detours + 1,
                )
                if detour_node is None:
                    break
                recovery_effect = _consistent_effect(after, final) or tuple(_effect_signature(a, b) for a, b in zip(after, final))
                child = register_transition(
                    detour_node,
                    recovery,
                    final,
                    "detour_recovery",
                    effect=recovery_effect,
                    detours=detour_node.detours,
                )
                if child is not None:
                    detour_count += 1
                    recovery_found = True
                    final_behavior = _batch_behavior(final)
                    prior = best_behavior.get(final_behavior)
                    rank = (child.total_cost, child.depth)
                    if child.currents != targets and child.depth < bounded.max_depth and (prior is None or rank < prior):
                        best_behavior[final_behavior] = rank
                        frontier.append(child)
                break
            if recovery_found:
                continue

    # Build action receipts over all certified states plus a bounded set of
    # counterfactual successors.  These executions train applicability and
    # successor congruence but do not retroactively authorize search paths.
    receipts: list[Any] = []
    counterfactual_added = 0
    state_cursor = 0
    ordered_actions = tuple(sorted(actions.values(), key=lambda value: (value.cost, value.kind, value.action_id)))
    while state_cursor < len(states) and len(receipts) < bounded.max_receipts:
        state = states[state_cursor]
        state_cursor += 1
        grid = validate_grid(getattr(state, "grid"))
        # States retain their demonstration index through the cache lookup.
        matching = [key for key, value in state_cache.items() if value is state]
        if not matching:
            continue
        example_index = matching[0][0]
        source_hash = _state_hash(state)
        for action in ordered_actions:
            if len(receipts) >= bounded.max_receipts:
                limit_reached = limit_reached or "max_receipts"
                break
            if execution_counter[0] >= bounded.max_leaf_executions:
                limit_reached = limit_reached or "max_leaf_executions"
                break
            execution_counter[0] += 1
            try:
                successor_grid = action.execute(grid)
                applicable = True
            except (AssertionError, KeyError, RuntimeError, TypeError, ValueError, OverflowError):
                successor_grid = grid
                applicable = False
            successor_hash = ""
            if applicable:
                key = (example_index, sha256_record(successor_grid))
                successor = state_cache.get(key)
                if successor is None and counterfactual_added < bounded.max_counterfactual_states and len(states) < bounded.max_states:
                    successor = state_for(example_index, successor_grid, "counterfactual")
                    counterfactual_added += 1
                if successor is not None:
                    successor_hash = _state_hash(successor)
            try:
                receipts.append(_make_receipt(
                    source_hash,
                    action,
                    applicable,
                    successor_hash,
                    evidence_kind="counterfactual" if state_cursor > len(root_states) else "observed",
                ))
            except ValueError:
                # Compatibility with an older strict receipt constructor.  A
                # known-applicable action with an omitted successor is never
                # recoded as disabled; it simply remains missing evidence.
                if not applicable or successor_hash:
                    raise

    # Deduplicate receipts without changing deterministic first occurrence.
    unique_receipts: dict[str, Any] = {}
    for receipt in receipts:
        unique_receipts.setdefault(_receipt_hash(receipt), receipt)
    route_values = tuple(sorted(routes.values(), key=lambda value: (value.total_cost, len(value.action_ids), value.route_id)))
    return TransitionCorpus(
        states=tuple(states),
        receipts=tuple(unique_receipts.values()),
        actions=ordered_actions,
        transitions=tuple(transitions),
        exact_routes=route_values,
        training_hashes=sanitized.training_hashes,
        root_state_hashes=root_hashes,
        proposals_considered=proposal_count,
        accepted_transitions=accepted_count,
        actual_leaf_executions=execution_counter[0],
        counterfactual_states=counterfactual_added,
        semantic_detours=detour_count,
        limit_reached=limit_reached,
    )


__all__ = [
    "BatchTransition",
    "CertifiedRoute",
    "CorpusAction",
    "TransitionCorpus",
    "TransitionCorpusLimits",
    "build_transition_corpus",
    "grid_feature_map",
    "guard_matches",
]
