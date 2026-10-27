"""Deterministic temporal shadow benchmark for Block 10.

This module is a *synthetic causal audit*.  It is deliberately separate from
the static ARC corpus and must not be interpreted as an ARC-AGI-3 score.  The
small worlds below exercise six contracts suggested by the Astra analysis:

* a hidden mode that is visible only in an earlier cue;
* a recurrent counter;
* object permanence through occlusion;
* an explicitly announced rule change;
* palette/D4 gauge transport; and
* causally irrelevant observation noise.

The benchmark crosses two controlled factors: a fixed versus refined capsule
and stateless versus persistent execution.  Refinements are learned only from
calibration episodes by materializing finite leakage witnesses.  Every action
is committed in an immutable, hash-sealed pre-action receipt before its actual
successor is exposed.  ``TemporalRunState`` is canonical JSON with a verified
content hash, so a run can be stopped, restored in a fresh process, and
continued without Python object identity or hidden process state.

Exact world state remains authoritative throughout.  Capsules are routing and
prediction records; they never replace the underlying deterministic episode.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

from .canonical import (
    canonical_json,
    canonical_value,
    content_hash,
    decode_json_bytes,
    require_nonnegative_int,
    require_sha256,
    require_trimmed,
)


TEMPORAL_SCHEMA_VERSION = 1
TEMPORAL_AUDIT_SCOPE = "synthetic_causal_audit_only"
TEMPORAL_CLAIM_BOUNDARY = (
    "Synthetic deterministic shadow benchmark; not an ARC-AGI-3 score, "
    "private-evaluation result, or interactive-environment claim."
)


class EpisodeKind(str, Enum):
    HIDDEN_MODE = "hidden_mode"
    COUNTER = "counter"
    OBJECT_PERMANENCE = "object_permanence"
    RULE_CHANGE = "rule_change"
    GAUGE = "gauge"
    NOISE = "noise"


class EpisodeSplit(str, Enum):
    CALIBRATION = "calibration"
    EVALUATION = "evaluation"


class CapsuleRegime(str, Enum):
    FIXED = "fixed"
    REFINED = "refined"


class MemoryRegime(str, Enum):
    STATELESS = "stateless"
    PERSISTENT = "persistent"


class PredictionStatus(str, Enum):
    UNIQUE = "unique"
    UNKNOWN = "unknown"
    AMBIGUOUS = "ambiguous"


class RunPhase(str, Enum):
    CALIBRATION = "calibration"
    EVALUATION = "evaluation"
    COMPLETE = "complete"


_FEATURES = (
    "remembered_mode",
    "counter_mod_3",
    "object_location",
    "active_rule",
)
_NORMALIZERS = ("drop_causal_noise", "palette_roles", "d4_local_frame")
_PLACEHOLDER_PREFIX = "$obs."


def _enum_value(enum_type: type[Enum], value: object, label: str) -> Any:
    try:
        return enum_type(value)
    except (TypeError, ValueError) as error:
        allowed = ", ".join(sorted(str(item.value) for item in enum_type))
        raise ValueError(f"{label} must be one of {allowed}") from error


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must be a mapping")
    for key in value:
        if not isinstance(key, str):
            raise TypeError(f"{label} keys must be strings")
    return value


def _exact_fields(
    record: Mapping[str, Any], required: set[str], label: str
) -> None:
    missing = required - set(record)
    unknown = set(record) - required
    if missing:
        raise ValueError(f"missing {label} fields: {sorted(missing)}")
    if unknown:
        raise ValueError(f"unknown {label} fields: {sorted(unknown)}")


def _canonical_object_json(value: Mapping[str, Any], label: str) -> str:
    frozen = canonical_json(value)
    decoded = decode_json_bytes(frozen)
    if not isinstance(decoded, Mapping):
        raise TypeError(f"{label} must encode an object")
    return frozen


def _decode_object(text: str, label: str) -> dict[str, Any]:
    require_trimmed(text, label)
    value = decode_json_bytes(text)
    if not isinstance(value, Mapping):
        raise TypeError(f"{label} must encode a JSON object")
    if canonical_json(value) != text:
        raise ValueError(f"{label} must use canonical JSON")
    return dict(value)


@dataclass(frozen=True, slots=True)
class Behavior:
    """One fully rendered causal result."""

    enabled: bool
    readout: str
    successor_class: str

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be Boolean")
        require_trimmed(self.readout, "readout")
        require_trimmed(self.successor_class, "successor_class")

    def to_record(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "readout": self.readout,
            "successor_class": self.successor_class,
        }

    @classmethod
    def from_record(cls, value: object) -> "Behavior":
        record = _mapping(value, "behavior")
        _exact_fields(record, {"enabled", "readout", "successor_class"}, "behavior")
        return cls(
            enabled=record["enabled"],
            readout=record["readout"],
            successor_class=record["successor_class"],
        )


@dataclass(frozen=True, slots=True)
class BehaviorTemplate:
    """A calibration target, optionally expressed in the observation gauge."""

    enabled: bool
    readout: str
    successor_class: str

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be Boolean")
        require_trimmed(self.readout, "template readout")
        require_trimmed(self.successor_class, "template successor_class")
        for value in (self.readout, self.successor_class):
            if value.startswith("$") and not value.startswith(_PLACEHOLDER_PREFIX):
                raise ValueError("only $obs.<field> behavior placeholders are permitted")

    def to_record(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "readout": self.readout,
            "successor_class": self.successor_class,
        }

    @classmethod
    def from_record(cls, value: object) -> "BehaviorTemplate":
        record = _mapping(value, "behavior template")
        _exact_fields(
            record, {"enabled", "readout", "successor_class"}, "behavior template"
        )
        return cls(
            enabled=record["enabled"],
            readout=record["readout"],
            successor_class=record["successor_class"],
        )

    def instantiate(self, observation: Mapping[str, Any]) -> Behavior:
        def resolve(value: str) -> str:
            if not value.startswith(_PLACEHOLDER_PREFIX):
                return value
            key = value[len(_PLACEHOLDER_PREFIX) :]
            if key not in observation:
                raise ValueError(f"missing observation field {key!r} for behavior template")
            rendered = observation[key]
            if isinstance(rendered, bool) or rendered is None:
                return str(rendered).lower() if isinstance(rendered, bool) else "none"
            if not isinstance(rendered, (str, int)):
                raise TypeError("behavior placeholders may render only strings or integers")
            return str(rendered)

        return Behavior(
            enabled=self.enabled,
            readout=resolve(self.readout),
            successor_class=resolve(self.successor_class),
        )


@dataclass(frozen=True, slots=True)
class EpisodeStep:
    """One deterministic observation/action transition."""

    step_id: str
    observation_json: str
    action: str
    expected: Behavior
    template: BehaviorTemplate
    scored: bool = True

    def __post_init__(self) -> None:
        require_trimmed(self.step_id, "step_id")
        _decode_object(self.observation_json, "observation_json")
        require_trimmed(self.action, "action")
        if not isinstance(self.expected, Behavior):
            raise TypeError("expected must be a Behavior")
        if not isinstance(self.template, BehaviorTemplate):
            raise TypeError("template must be a BehaviorTemplate")
        if not isinstance(self.scored, bool):
            raise TypeError("scored must be Boolean")
        if self.template.instantiate(self.observation) != self.expected:
            raise ValueError("behavior template does not render the expected behavior")

    @property
    def observation(self) -> dict[str, Any]:
        return _decode_object(self.observation_json, "observation_json")

    def to_record(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "observation": self.observation,
            "action": self.action,
            "expected": self.expected.to_record(),
            "template": self.template.to_record(),
            "scored": self.scored,
        }

    @classmethod
    def from_record(cls, value: object) -> "EpisodeStep":
        record = _mapping(value, "episode step")
        _exact_fields(
            record,
            {"step_id", "observation", "action", "expected", "template", "scored"},
            "episode step",
        )
        return cls(
            step_id=record["step_id"],
            observation_json=_canonical_object_json(
                _mapping(record["observation"], "observation"), "observation"
            ),
            action=record["action"],
            expected=Behavior.from_record(record["expected"]),
            template=BehaviorTemplate.from_record(record["template"]),
            scored=record["scored"],
        )


@dataclass(frozen=True, slots=True)
class TemporalEpisode:
    episode_id: str
    kind: EpisodeKind
    split: EpisodeSplit
    steps: tuple[EpisodeStep, ...]

    def __post_init__(self) -> None:
        require_trimmed(self.episode_id, "episode_id")
        object.__setattr__(self, "kind", _enum_value(EpisodeKind, self.kind, "kind"))
        object.__setattr__(self, "split", _enum_value(EpisodeSplit, self.split, "split"))
        object.__setattr__(self, "steps", tuple(self.steps))
        if not self.steps:
            raise ValueError("an episode must contain at least one step")
        if not all(isinstance(step, EpisodeStep) for step in self.steps):
            raise TypeError("episode steps must be EpisodeStep records")
        identifiers = [step.step_id for step in self.steps]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("step IDs must be unique within an episode")

    def to_record(self) -> dict[str, Any]:
        return {
            "episode_id": self.episode_id,
            "kind": self.kind.value,
            "split": self.split.value,
            "steps": [step.to_record() for step in self.steps],
        }

    @classmethod
    def from_record(cls, value: object) -> "TemporalEpisode":
        record = _mapping(value, "episode")
        _exact_fields(record, {"episode_id", "kind", "split", "steps"}, "episode")
        if not isinstance(record["steps"], Sequence) or isinstance(
            record["steps"], (str, bytes, bytearray)
        ):
            raise TypeError("episode steps must be a sequence")
        return cls(
            episode_id=record["episode_id"],
            kind=_enum_value(EpisodeKind, record["kind"], "kind"),
            split=_enum_value(EpisodeSplit, record["split"], "split"),
            steps=tuple(EpisodeStep.from_record(item) for item in record["steps"]),
        )


@dataclass(frozen=True, slots=True)
class TemporalSuite:
    episodes: tuple[TemporalEpisode, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "episodes", tuple(self.episodes))
        if not self.episodes:
            raise ValueError("temporal suite cannot be empty")
        if not all(isinstance(episode, TemporalEpisode) for episode in self.episodes):
            raise TypeError("episodes must be TemporalEpisode records")
        identifiers = [episode.episode_id for episode in self.episodes]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("episode IDs must be unique")
        seen_evaluation = False
        kinds_by_split: dict[EpisodeSplit, set[EpisodeKind]] = {
            EpisodeSplit.CALIBRATION: set(),
            EpisodeSplit.EVALUATION: set(),
        }
        for episode in self.episodes:
            if episode.split is EpisodeSplit.EVALUATION:
                seen_evaluation = True
            elif seen_evaluation:
                raise ValueError("all calibration episodes must precede evaluation episodes")
            kinds_by_split[episode.split].add(episode.kind)
        required = set(EpisodeKind)
        for split, observed in kinds_by_split.items():
            if observed != required:
                missing = sorted(item.value for item in required - observed)
                raise ValueError(f"{split.value} split lacks episode kinds {missing}")

    @property
    def suite_id(self) -> str:
        return content_hash(self.semantic_record())

    @property
    def event_count(self) -> int:
        return sum(len(episode.steps) for episode in self.episodes)

    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.temporal_suite",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "scope": TEMPORAL_AUDIT_SCOPE,
            "episodes": [episode.to_record() for episode in self.episodes],
        }

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record(), "suite_id": self.suite_id}

    @classmethod
    def from_record(cls, value: object) -> "TemporalSuite":
        record = _mapping(value, "temporal suite")
        required = {
            "schema", "schema_version", "scope", "episodes", "suite_id",
        }
        _exact_fields(record, required, "temporal suite")
        if record["schema"] != "komorebi.lasm_action.temporal_suite":
            raise ValueError("unknown temporal-suite schema")
        if record["schema_version"] != TEMPORAL_SCHEMA_VERSION:
            raise ValueError("unsupported temporal-suite schema version")
        if record["scope"] != TEMPORAL_AUDIT_SCOPE:
            raise ValueError("temporal-suite scope mismatch")
        if not isinstance(record["episodes"], Sequence) or isinstance(
            record["episodes"], (str, bytes, bytearray)
        ):
            raise TypeError("temporal-suite episodes must be a sequence")
        result = cls(tuple(
            TemporalEpisode.from_record(item) for item in record["episodes"]
        ))
        if record["suite_id"] != result.suite_id:
            raise ValueError("temporal-suite ID mismatch")
        return result


@dataclass(frozen=True, slots=True)
class TemporalMemory:
    """Only causally observed history; no hidden simulator state is stored."""

    remembered_mode: str | None = None
    counter: int | None = None
    object_location: str | None = None
    active_rule: str | None = None
    event_count: int = 0
    history_hash: str = ""

    def __post_init__(self) -> None:
        for name in ("remembered_mode", "object_location", "active_rule"):
            value = getattr(self, name)
            if value is not None:
                require_trimmed(value, name)
        if self.counter is not None:
            require_nonnegative_int(self.counter, "counter")
        require_nonnegative_int(self.event_count, "event_count")
        require_sha256(self.history_hash, "history_hash", allow_empty=True)

    @classmethod
    def empty(cls) -> "TemporalMemory":
        return cls()

    def feature(self, name: str) -> str | int | None:
        if name == "remembered_mode":
            return self.remembered_mode
        if name == "counter_mod_3":
            return None if self.counter is None else self.counter % 3
        if name == "object_location":
            return self.object_location
        if name == "active_rule":
            return self.active_rule
        raise KeyError(name)

    def to_record(self) -> dict[str, Any]:
        return {
            "remembered_mode": self.remembered_mode,
            "counter": self.counter,
            "object_location": self.object_location,
            "active_rule": self.active_rule,
            "event_count": self.event_count,
            "history_hash": self.history_hash,
        }

    @classmethod
    def from_record(cls, value: object) -> "TemporalMemory":
        record = _mapping(value, "temporal memory")
        required = {
            "remembered_mode", "counter", "object_location", "active_rule",
            "event_count", "history_hash",
        }
        _exact_fields(record, required, "temporal memory")
        return cls(**{key: record[key] for key in required})


def _history_hash(previous: str, event: Mapping[str, Any]) -> str:
    return content_hash({"previous": previous, "event": event})


def _ingest_observation(memory: TemporalMemory, observation: Mapping[str, Any]) -> TemporalMemory:
    display = observation.get("display")
    mode = memory.remembered_mode
    counter = memory.counter
    location = memory.object_location
    rule = memory.active_rule
    if display == "mode_cue":
        mode = require_trimmed(observation.get("mode"), "observed mode")
    elif display == "counter_reset":
        counter = 0
    elif display == "object_visible":
        location = require_trimmed(observation.get("location"), "object location")
    elif display == "rule_cue":
        rule = require_trimmed(observation.get("rule"), "active rule")
    return TemporalMemory(
        remembered_mode=mode,
        counter=counter,
        object_location=location,
        active_rule=rule,
        event_count=memory.event_count,
        history_hash=_history_hash(
            memory.history_hash, {"kind": "observation", "value": observation}
        ),
    )


def _apply_action(
    memory: TemporalMemory,
    observation: Mapping[str, Any],
    action: str,
    actual: Behavior,
) -> TemporalMemory:
    counter = memory.counter
    if observation.get("display") == "pulse" and action == "emit" and actual.enabled:
        counter = 0 if counter is None else counter + 1
    event = {
        "kind": "action",
        "action": action,
        "enabled": actual.enabled,
        "readout": actual.readout,
        "successor_class": actual.successor_class,
    }
    return TemporalMemory(
        remembered_mode=memory.remembered_mode,
        counter=counter,
        object_location=memory.object_location,
        active_rule=memory.active_rule,
        event_count=memory.event_count + 1,
        history_hash=_history_hash(memory.history_hash, event),
    )


@dataclass(frozen=True, slots=True)
class PredictiveCapsule:
    regime: CapsuleRegime
    kind: EpisodeKind
    current_json: str
    history_json: str
    normalizers: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "regime", _enum_value(CapsuleRegime, self.regime, "regime"))
        object.__setattr__(self, "kind", _enum_value(EpisodeKind, self.kind, "kind"))
        _decode_object(self.current_json, "capsule current_json")
        _decode_object(self.history_json, "capsule history_json")
        object.__setattr__(self, "normalizers", tuple(self.normalizers))
        for item in self.normalizers:
            require_trimmed(item, "normalizer")

    @property
    def current(self) -> dict[str, Any]:
        return _decode_object(self.current_json, "capsule current_json")

    @property
    def history(self) -> dict[str, Any]:
        return _decode_object(self.history_json, "capsule history_json")

    def semantic_record(self) -> dict[str, Any]:
        return {
            "regime": self.regime.value,
            "kind": self.kind.value,
            "current": self.current,
            "history": self.history,
            "normalizers": list(self.normalizers),
        }

    @property
    def capsule_hash(self) -> str:
        return content_hash(self.semantic_record())

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record(), "capsule_hash": self.capsule_hash}


def build_capsule(
    kind: EpisodeKind,
    observation: Mapping[str, Any],
    memory: TemporalMemory,
    regime: CapsuleRegime,
    refinement_features: Iterable[str] = (),
) -> PredictiveCapsule:
    """Build one deterministic capsule without reading a transition target."""

    kind = _enum_value(EpisodeKind, kind, "kind")
    regime = _enum_value(CapsuleRegime, regime, "regime")
    current = dict(canonical_value(observation))
    history: dict[str, Any] = {}
    normalizers: tuple[str, ...] = ()
    if regime is CapsuleRegime.REFINED:
        normalizers = _NORMALIZERS
        current.pop("noise", None)
        current.pop("noise_id", None)
        if kind is EpisodeKind.GAUGE and current.get("display") == "gauge_target":
            mark = current.pop("mark_color", None)
            background = current.pop("background_color", None)
            current.pop("marker_direction", None)
            current.pop("frame_rotation", None)
            current["mark_role"] = "foreground"
            current["background_role"] = "background"
            current["colors_distinct"] = mark != background
            current["direction_role"] = "forward"
        requested = tuple(dict.fromkeys(refinement_features))
        unknown = sorted(set(requested) - set(_FEATURES))
        if unknown:
            raise ValueError(f"unknown refinement features: {unknown}")
        for feature in requested:
            value = memory.feature(feature)
            if value is not None:
                history[feature] = value
    return PredictiveCapsule(
        regime=regime,
        kind=kind,
        current_json=_canonical_object_json(current, "capsule current"),
        history_json=_canonical_object_json(history, "capsule history"),
        normalizers=normalizers,
    )


@dataclass(frozen=True, slots=True)
class LeakageWitness:
    witness_id: str
    capsule_hash: str
    action: str
    left_event: str
    right_event: str
    kind: EpisodeKind
    violated_contracts: tuple[str, ...]
    candidate_features: tuple[str, ...]

    def __post_init__(self) -> None:
        require_sha256(self.witness_id, "witness_id")
        require_sha256(self.capsule_hash, "capsule_hash")
        require_trimmed(self.action, "action")
        require_trimmed(self.left_event, "left_event")
        require_trimmed(self.right_event, "right_event")
        object.__setattr__(self, "kind", _enum_value(EpisodeKind, self.kind, "kind"))
        object.__setattr__(self, "violated_contracts", tuple(self.violated_contracts))
        object.__setattr__(self, "candidate_features", tuple(self.candidate_features))
        if not self.violated_contracts:
            raise ValueError("a leakage witness must violate at least one contract")

    def to_record(self) -> dict[str, Any]:
        return {
            "witness_id": self.witness_id,
            "capsule_hash": self.capsule_hash,
            "action": self.action,
            "left_event": self.left_event,
            "right_event": self.right_event,
            "kind": self.kind.value,
            "violated_contracts": list(self.violated_contracts),
            "candidate_features": list(self.candidate_features),
        }


@dataclass(frozen=True, slots=True)
class RefinementProposal:
    feature: str
    repaired_witnesses: tuple[str, ...]
    remaining_witnesses: int
    accepted: bool
    reason: str

    def __post_init__(self) -> None:
        if self.feature not in _FEATURES:
            raise ValueError("refinement proposal uses an unknown feature")
        object.__setattr__(self, "repaired_witnesses", tuple(self.repaired_witnesses))
        for witness_id in self.repaired_witnesses:
            require_sha256(witness_id, "repaired witness ID")
        require_nonnegative_int(self.remaining_witnesses, "remaining_witnesses")
        if not isinstance(self.accepted, bool):
            raise TypeError("accepted must be Boolean")
        require_trimmed(self.reason, "refinement reason")

    def to_record(self) -> dict[str, Any]:
        return {
            "feature": self.feature,
            "repaired_witnesses": list(self.repaired_witnesses),
            "repaired_count": len(self.repaired_witnesses),
            "remaining_witnesses": self.remaining_witnesses,
            "accepted": self.accepted,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class RefinementArchive:
    witnesses: tuple[LeakageWitness, ...]
    proposals: tuple[RefinementProposal, ...]
    accepted_features: tuple[str, ...]
    unresolved_witnesses: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "witnesses", tuple(self.witnesses))
        object.__setattr__(self, "proposals", tuple(self.proposals))
        object.__setattr__(self, "accepted_features", tuple(self.accepted_features))
        object.__setattr__(self, "unresolved_witnesses", tuple(self.unresolved_witnesses))
        if len(self.accepted_features) != len(set(self.accepted_features)):
            raise ValueError("accepted refinement features must be unique")
        unknown = set(self.accepted_features) - set(_FEATURES)
        if unknown:
            raise ValueError(f"unknown accepted refinement features: {sorted(unknown)}")
        known_ids = {witness.witness_id for witness in self.witnesses}
        if not set(self.unresolved_witnesses) <= known_ids:
            raise ValueError("unresolved witness IDs must belong to the archive")

    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.refinement_archive",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "calibration_only": True,
            "witnesses": [item.to_record() for item in self.witnesses],
            "proposals": [item.to_record() for item in self.proposals],
            "accepted_features": list(self.accepted_features),
            "unresolved_witnesses": list(self.unresolved_witnesses),
            "normalizers": list(_NORMALIZERS),
            "noise_features_promoted": 0,
        }

    @property
    def archive_id(self) -> str:
        return content_hash(self.semantic_record())

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record(), "archive_id": self.archive_id}


@dataclass(frozen=True, slots=True)
class EvaluationConfig:
    capsule_regime: CapsuleRegime
    memory_regime: MemoryRegime

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "capsule_regime", _enum_value(CapsuleRegime, self.capsule_regime, "capsule_regime")
        )
        object.__setattr__(
            self, "memory_regime", _enum_value(MemoryRegime, self.memory_regime, "memory_regime")
        )

    @property
    def config_id(self) -> str:
        return f"{self.capsule_regime.value}__{self.memory_regime.value}"

    def to_record(self) -> dict[str, str]:
        return {
            "capsule_regime": self.capsule_regime.value,
            "memory_regime": self.memory_regime.value,
            "config_id": self.config_id,
        }

    @classmethod
    def from_record(cls, value: object) -> "EvaluationConfig":
        record = _mapping(value, "evaluation config")
        _exact_fields(record, {"capsule_regime", "memory_regime", "config_id"}, "evaluation config")
        result = cls(record["capsule_regime"], record["memory_regime"])
        if record["config_id"] != result.config_id:
            raise ValueError("evaluation config ID mismatch")
        return result


@dataclass(frozen=True, slots=True)
class ModelRule:
    key: str
    templates_json: tuple[str, ...]

    def __post_init__(self) -> None:
        require_sha256(self.key, "model rule key")
        object.__setattr__(self, "templates_json", tuple(self.templates_json))
        if tuple(sorted(set(self.templates_json))) != self.templates_json:
            raise ValueError("model templates must be unique and canonically sorted")
        for text in self.templates_json:
            value = decode_json_bytes(text)
            BehaviorTemplate.from_record(value)
            if canonical_json(value) != text:
                raise ValueError("model templates must use canonical JSON")

    def to_record(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "templates": [decode_json_bytes(text) for text in self.templates_json],
        }

    @classmethod
    def from_record(cls, value: object) -> "ModelRule":
        record = _mapping(value, "model rule")
        _exact_fields(record, {"key", "templates"}, "model rule")
        if not isinstance(record["templates"], Sequence) or isinstance(
            record["templates"], (str, bytes, bytearray)
        ):
            raise TypeError("model templates must be a sequence")
        return cls(
            key=record["key"],
            templates_json=tuple(canonical_json(item) for item in record["templates"]),
        )


@dataclass(frozen=True, slots=True)
class ActionReceipt:
    """Tamper-evident commitment created before the transition is revealed."""

    run_id: str
    episode_id: str
    step_index: int
    action: str
    snapshot_hash: str
    capsule_hash: str
    prediction_status: PredictionStatus
    prediction: Behavior | None
    seal_hash: str

    def __post_init__(self) -> None:
        require_sha256(self.run_id, "run_id")
        require_trimmed(self.episode_id, "episode_id")
        require_nonnegative_int(self.step_index, "step_index")
        require_trimmed(self.action, "action")
        require_sha256(self.snapshot_hash, "snapshot_hash")
        require_sha256(self.capsule_hash, "capsule_hash")
        object.__setattr__(
            self, "prediction_status", _enum_value(PredictionStatus, self.prediction_status, "prediction_status")
        )
        if self.prediction is not None and not isinstance(self.prediction, Behavior):
            raise TypeError("prediction must be a Behavior or None")
        if (self.prediction_status is PredictionStatus.UNIQUE) != (self.prediction is not None):
            raise ValueError("only unique predictions may carry a behavior")
        require_sha256(self.seal_hash, "seal_hash")
        if self.seal_hash != content_hash(self._seal_payload()):
            raise ValueError("pre-action receipt seal mismatch")

    def _seal_payload(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.pre_action_receipt",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "sealed_before_transition": True,
            "run_id": self.run_id,
            "episode_id": self.episode_id,
            "step_index": self.step_index,
            "action": self.action,
            "snapshot_hash": self.snapshot_hash,
            "capsule_hash": self.capsule_hash,
            "prediction_status": self.prediction_status.value,
            "prediction": None if self.prediction is None else self.prediction.to_record(),
        }

    @classmethod
    def seal(
        cls,
        *,
        run_id: str,
        episode_id: str,
        step_index: int,
        action: str,
        snapshot_hash: str,
        capsule_hash: str,
        prediction_status: PredictionStatus,
        prediction: Behavior | None,
    ) -> "ActionReceipt":
        payload = {
            "schema": "komorebi.lasm_action.pre_action_receipt",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "sealed_before_transition": True,
            "run_id": run_id,
            "episode_id": episode_id,
            "step_index": step_index,
            "action": action,
            "snapshot_hash": snapshot_hash,
            "capsule_hash": capsule_hash,
            "prediction_status": _enum_value(
                PredictionStatus, prediction_status, "prediction_status"
            ).value,
            "prediction": None if prediction is None else prediction.to_record(),
        }
        return cls(
            run_id=run_id,
            episode_id=episode_id,
            step_index=step_index,
            action=action,
            snapshot_hash=snapshot_hash,
            capsule_hash=capsule_hash,
            prediction_status=prediction_status,
            prediction=prediction,
            seal_hash=content_hash(payload),
        )

    def verify(self) -> bool:
        return self.seal_hash == content_hash(self._seal_payload())

    def to_record(self) -> dict[str, Any]:
        return {**self._seal_payload(), "seal_hash": self.seal_hash}

    @classmethod
    def from_record(cls, value: object) -> "ActionReceipt":
        record = _mapping(value, "pre-action receipt")
        required = {
            "schema", "schema_version", "sealed_before_transition", "run_id",
            "episode_id", "step_index", "action", "snapshot_hash", "capsule_hash",
            "prediction_status", "prediction", "seal_hash",
        }
        _exact_fields(record, required, "pre-action receipt")
        if record["schema"] != "komorebi.lasm_action.pre_action_receipt":
            raise ValueError("unknown pre-action receipt schema")
        if record["schema_version"] != TEMPORAL_SCHEMA_VERSION:
            raise ValueError("unsupported pre-action receipt schema version")
        if record["sealed_before_transition"] is not True:
            raise ValueError("receipt was not marked as sealed before transition")
        return cls(
            run_id=record["run_id"],
            episode_id=record["episode_id"],
            step_index=record["step_index"],
            action=record["action"],
            snapshot_hash=record["snapshot_hash"],
            capsule_hash=record["capsule_hash"],
            prediction_status=record["prediction_status"],
            prediction=None if record["prediction"] is None else Behavior.from_record(record["prediction"]),
            seal_hash=record["seal_hash"],
        )


PreActionReceipt = ActionReceipt


@dataclass(frozen=True, slots=True)
class ActionOutcome:
    receipt_hash: str
    actual: Behavior
    prediction_exact: bool
    outcome_hash: str

    def __post_init__(self) -> None:
        require_sha256(self.receipt_hash, "receipt_hash")
        if not isinstance(self.actual, Behavior):
            raise TypeError("actual must be a Behavior")
        if not isinstance(self.prediction_exact, bool):
            raise TypeError("prediction_exact must be Boolean")
        require_sha256(self.outcome_hash, "outcome_hash")
        if self.outcome_hash != content_hash(self._payload()):
            raise ValueError("action outcome hash mismatch")

    def _payload(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.action_outcome",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "receipt_hash": self.receipt_hash,
            "actual": self.actual.to_record(),
            "prediction_exact": self.prediction_exact,
        }

    @classmethod
    def reveal(cls, receipt: ActionReceipt, actual: Behavior) -> "ActionOutcome":
        if not receipt.verify():
            raise ValueError("cannot reveal an outcome for an invalid receipt")
        exact = receipt.prediction is not None and receipt.prediction == actual
        payload = {
            "schema": "komorebi.lasm_action.action_outcome",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "receipt_hash": receipt.seal_hash,
            "actual": actual.to_record(),
            "prediction_exact": exact,
        }
        return cls(receipt.seal_hash, actual, exact, content_hash(payload))

    def to_record(self) -> dict[str, Any]:
        return {**self._payload(), "outcome_hash": self.outcome_hash}

    @classmethod
    def from_record(cls, value: object) -> "ActionOutcome":
        record = _mapping(value, "action outcome")
        required = {
            "schema", "schema_version", "receipt_hash", "actual",
            "prediction_exact", "outcome_hash",
        }
        _exact_fields(record, required, "action outcome")
        if record["schema"] != "komorebi.lasm_action.action_outcome":
            raise ValueError("unknown action outcome schema")
        if record["schema_version"] != TEMPORAL_SCHEMA_VERSION:
            raise ValueError("unsupported action outcome schema version")
        return cls(
            receipt_hash=record["receipt_hash"],
            actual=Behavior.from_record(record["actual"]),
            prediction_exact=record["prediction_exact"],
            outcome_hash=record["outcome_hash"],
        )


@dataclass(frozen=True, slots=True)
class TemporalEventRecord:
    split: EpisodeSplit
    kind: EpisodeKind
    episode_id: str
    step_id: str
    step_index: int
    action: str
    scored: bool
    receipt: ActionReceipt
    outcome: ActionOutcome

    def __post_init__(self) -> None:
        object.__setattr__(self, "split", _enum_value(EpisodeSplit, self.split, "split"))
        object.__setattr__(self, "kind", _enum_value(EpisodeKind, self.kind, "kind"))
        require_trimmed(self.episode_id, "episode_id")
        require_trimmed(self.step_id, "step_id")
        require_nonnegative_int(self.step_index, "step_index")
        require_trimmed(self.action, "action")
        if not isinstance(self.scored, bool):
            raise TypeError("scored must be Boolean")
        if not isinstance(self.receipt, ActionReceipt):
            raise TypeError("receipt must be an ActionReceipt")
        if not isinstance(self.outcome, ActionOutcome):
            raise TypeError("outcome must be an ActionOutcome")
        if self.receipt.episode_id != self.episode_id:
            raise ValueError("event episode does not match its receipt")
        if self.receipt.step_index != self.step_index:
            raise ValueError("event step index does not match its receipt")
        if self.receipt.action != self.action:
            raise ValueError("event action does not match its receipt")
        if self.outcome.receipt_hash != self.receipt.seal_hash:
            raise ValueError("event outcome does not reference its receipt")
        expected_exact = (
            self.receipt.prediction is not None
            and self.receipt.prediction == self.outcome.actual
        )
        if self.outcome.prediction_exact != expected_exact:
            raise ValueError("event outcome exactness disagrees with receipt and actual")

    def to_record(self) -> dict[str, Any]:
        return {
            "split": self.split.value,
            "kind": self.kind.value,
            "episode_id": self.episode_id,
            "step_id": self.step_id,
            "step_index": self.step_index,
            "action": self.action,
            "scored": self.scored,
            "receipt": self.receipt.to_record(),
            "outcome": self.outcome.to_record(),
        }

    @classmethod
    def from_record(cls, value: object) -> "TemporalEventRecord":
        record = _mapping(value, "temporal event")
        required = {
            "split", "kind", "episode_id", "step_id", "step_index", "action", "scored",
            "receipt", "outcome",
        }
        _exact_fields(record, required, "temporal event")
        return cls(
            split=record["split"],
            kind=record["kind"],
            episode_id=record["episode_id"],
            step_id=record["step_id"],
            step_index=record["step_index"],
            action=record["action"],
            scored=record["scored"],
            receipt=ActionReceipt.from_record(record["receipt"]),
            outcome=ActionOutcome.from_record(record["outcome"]),
        )


def _rules_record(rules: Sequence[ModelRule]) -> list[dict[str, Any]]:
    return [rule.to_record() for rule in rules]


@dataclass(frozen=True, slots=True)
class TemporalRunState:
    """Complete continuation state; safe to serialize between processes."""

    config: EvaluationConfig
    suite_id: str
    archive_id: str
    run_id: str
    phase: RunPhase
    episode_index: int
    step_index: int
    memory: TemporalMemory
    refinement_features: tuple[str, ...]
    rules: tuple[ModelRule, ...]
    transcript: tuple[TemporalEventRecord, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.config, EvaluationConfig):
            raise TypeError("config must be an EvaluationConfig")
        require_sha256(self.suite_id, "suite_id")
        require_sha256(self.archive_id, "archive_id")
        require_sha256(self.run_id, "run_id")
        object.__setattr__(self, "phase", _enum_value(RunPhase, self.phase, "phase"))
        require_nonnegative_int(self.episode_index, "episode_index")
        require_nonnegative_int(self.step_index, "step_index")
        if not isinstance(self.memory, TemporalMemory):
            raise TypeError("memory must be TemporalMemory")
        object.__setattr__(self, "refinement_features", tuple(self.refinement_features))
        object.__setattr__(self, "rules", tuple(self.rules))
        object.__setattr__(self, "transcript", tuple(self.transcript))
        if tuple(sorted(self.rules, key=lambda item: item.key)) != self.rules:
            raise ValueError("model rules must be sorted by key")
        if len({rule.key for rule in self.rules}) != len(self.rules):
            raise ValueError("model rule keys must be unique")
        for event in self.transcript:
            if event.receipt.run_id != self.run_id:
                raise ValueError("transcript receipt belongs to another run")

    def semantic_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_action.temporal_run_state",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "scope": TEMPORAL_AUDIT_SCOPE,
            "config": self.config.to_record(),
            "suite_id": self.suite_id,
            "archive_id": self.archive_id,
            "run_id": self.run_id,
            "phase": self.phase.value,
            "episode_index": self.episode_index,
            "step_index": self.step_index,
            "memory": self.memory.to_record(),
            "refinement_features": list(self.refinement_features),
            "rules": _rules_record(self.rules),
            "transcript": [event.to_record() for event in self.transcript],
        }

    @property
    def state_hash(self) -> str:
        return content_hash(self.semantic_record())

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record(), "state_hash": self.state_hash}

    def to_json(self) -> str:
        return canonical_json(self.to_record())

    @classmethod
    def from_record(cls, value: object) -> "TemporalRunState":
        record = _mapping(value, "temporal run state")
        required = {
            "schema", "schema_version", "scope", "config", "suite_id", "archive_id",
            "run_id", "phase", "episode_index", "step_index", "memory",
            "refinement_features", "rules", "transcript", "state_hash",
        }
        _exact_fields(record, required, "temporal run state")
        if record["schema"] != "komorebi.lasm_action.temporal_run_state":
            raise ValueError("unknown temporal run-state schema")
        if record["schema_version"] != TEMPORAL_SCHEMA_VERSION:
            raise ValueError("unsupported temporal run-state schema version")
        if record["scope"] != TEMPORAL_AUDIT_SCOPE:
            raise ValueError("temporal run-state scope mismatch")
        for name in ("refinement_features", "rules", "transcript"):
            if not isinstance(record[name], Sequence) or isinstance(
                record[name], (str, bytes, bytearray)
            ):
                raise TypeError(f"{name} must be a sequence")
        result = cls(
            config=EvaluationConfig.from_record(record["config"]),
            suite_id=record["suite_id"],
            archive_id=record["archive_id"],
            run_id=record["run_id"],
            phase=record["phase"],
            episode_index=record["episode_index"],
            step_index=record["step_index"],
            memory=TemporalMemory.from_record(record["memory"]),
            refinement_features=tuple(record["refinement_features"]),
            rules=tuple(ModelRule.from_record(item) for item in record["rules"]),
            transcript=tuple(TemporalEventRecord.from_record(item) for item in record["transcript"]),
        )
        if record["state_hash"] != result.state_hash:
            raise ValueError("temporal run-state hash mismatch")
        return result

    @classmethod
    def from_json(cls, value: bytes | bytearray | str) -> "TemporalRunState":
        return cls.from_record(decode_json_bytes(value))


@dataclass(frozen=True, slots=True)
class KindMetrics:
    kind: EpisodeKind
    scored: int
    exact: int
    abstained: int
    ambiguous: int
    unknown: int

    def to_record(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "scored": self.scored,
            "exact": self.exact,
            "incorrect": self.scored - self.exact,
            "abstained": self.abstained,
            "ambiguous": self.ambiguous,
            "unknown": self.unknown,
            "accuracy": 0.0 if self.scored == 0 else self.exact / self.scored,
        }


@dataclass(frozen=True, slots=True)
class TemporalEvaluation:
    config: EvaluationConfig
    scored: int
    exact: int
    abstained: int
    ambiguous: int
    unknown: int
    control_scored: int
    control_exact: int
    causal_scored: int
    causal_exact: int
    applicability_exact: int
    readout_exact: int
    successor_exact: int
    kind_metrics: tuple[KindMetrics, ...]
    receipt_count: int
    verified_receipts: int
    transcript_hash: str
    final_state_hash: str

    @property
    def accuracy(self) -> float:
        return 0.0 if self.scored == 0 else self.exact / self.scored

    def to_record(self) -> dict[str, Any]:
        return {
            "config": self.config.to_record(),
            "scored": self.scored,
            "exact": self.exact,
            "incorrect": self.scored - self.exact,
            "abstained": self.abstained,
            "ambiguous": self.ambiguous,
            "unknown": self.unknown,
            "accuracy": self.accuracy,
            "visible_control": {
                "scored": self.control_scored,
                "exact": self.control_exact,
                "accuracy": (
                    0.0
                    if self.control_scored == 0
                    else self.control_exact / self.control_scored
                ),
            },
            "causal_challenge": {
                "scored": self.causal_scored,
                "exact": self.causal_exact,
                "accuracy": (
                    0.0
                    if self.causal_scored == 0
                    else self.causal_exact / self.causal_scored
                ),
            },
            "contract_exactness": {
                "action_applicability": self.applicability_exact,
                "goal_readout": self.readout_exact,
                "successor_congruence": self.successor_exact,
                "denominator": self.scored,
            },
            "kind_metrics": [item.to_record() for item in self.kind_metrics],
            "receipt_count": self.receipt_count,
            "verified_receipts": self.verified_receipts,
            "all_receipts_verified": self.receipt_count == self.verified_receipts,
            "transcript_hash": self.transcript_hash,
            "final_state_hash": self.final_state_hash,
        }


@dataclass(frozen=True, slots=True)
class ContinuationVerification:
    config_id: str
    checkpoint_events: int
    serialized_state_hash: str
    uninterrupted_final_hash: str
    resumed_final_hash: str
    byte_stable: bool
    continuation_equivalent: bool

    def to_record(self) -> dict[str, Any]:
        return {
            "config_id": self.config_id,
            "checkpoint_events": self.checkpoint_events,
            "serialized_state_hash": self.serialized_state_hash,
            "uninterrupted_final_hash": self.uninterrupted_final_hash,
            "resumed_final_hash": self.resumed_final_hash,
            "byte_stable": self.byte_stable,
            "continuation_equivalent": self.continuation_equivalent,
        }


@dataclass(frozen=True, slots=True)
class TemporalBenchmarkResult:
    suite_id: str
    archive: RefinementArchive
    evaluations: tuple[TemporalEvaluation, ...]
    continuations: tuple[ContinuationVerification, ...]

    def __post_init__(self) -> None:
        require_sha256(self.suite_id, "suite_id")
        object.__setattr__(self, "evaluations", tuple(self.evaluations))
        object.__setattr__(self, "continuations", tuple(self.continuations))

    @property
    def result_id(self) -> str:
        return content_hash(self.semantic_record())

    def semantic_record(self) -> dict[str, Any]:
        matrix: dict[str, dict[str, Any]] = {}
        for evaluation in self.evaluations:
            row = matrix.setdefault(evaluation.config.capsule_regime.value, {})
            row[evaluation.config.memory_regime.value] = {
                "exact": evaluation.exact,
                "scored": evaluation.scored,
                "accuracy": evaluation.accuracy,
                "abstained": evaluation.abstained,
            }
        return {
            "schema": "komorebi.lasm_action.temporal_shadow_audit",
            "schema_version": TEMPORAL_SCHEMA_VERSION,
            "scope": TEMPORAL_AUDIT_SCOPE,
            "claim_boundary": TEMPORAL_CLAIM_BOUNDARY,
            "suite_id": self.suite_id,
            "refinement_archive": self.archive.to_record(),
            "factorial_matrix": matrix,
            "evaluations": [item.to_record() for item in self.evaluations],
            "fresh_process_continuations": [item.to_record() for item in self.continuations],
            "all_fresh_process_replays_exact": all(
                item.byte_stable and item.continuation_equivalent
                for item in self.continuations
            ),
        }

    def to_record(self) -> dict[str, Any]:
        return {**self.semantic_record(), "result_id": self.result_id}


@dataclass(frozen=True, slots=True)
class _PreparedSample:
    event_id: str
    kind: EpisodeKind
    action: str
    capsule_hash: str
    template: BehaviorTemplate
    features_json: str

    @property
    def features(self) -> dict[str, Any]:
        return _decode_object(self.features_json, "prepared features")


def _step(
    step_id: str,
    observation: Mapping[str, Any],
    action: str,
    enabled: bool,
    readout: str,
    successor: str,
    *,
    scored: bool,
    template_readout: str | None = None,
    template_successor: str | None = None,
) -> EpisodeStep:
    expected = Behavior(enabled, readout, successor)
    template = BehaviorTemplate(
        enabled,
        readout if template_readout is None else template_readout,
        successor if template_successor is None else template_successor,
    )
    return EpisodeStep(
        step_id=step_id,
        observation_json=_canonical_object_json(observation, "observation"),
        action=action,
        expected=expected,
        template=template,
        scored=scored,
    )


def _visible_control(kind: EpisodeKind, suffix: str) -> EpisodeStep:
    return _step(
        f"control_{suffix}",
        {"display": "visible_control", "signal": kind.value},
        "echo",
        True,
        f"control:{kind.value}",
        "control_done",
        scored=True,
    )


def _hidden_episode(identifier: str, split: EpisodeSplit, mode: str) -> TemporalEpisode:
    if mode == "amber":
        behavior = (True, "left", "opened")
    elif mode == "teal":
        behavior = (False, "blocked", "closed")
    else:
        raise ValueError("unknown hidden mode")
    return TemporalEpisode(identifier, EpisodeKind.HIDDEN_MODE, split, (
        _step(
            "cue", {"display": "mode_cue", "mode": mode}, "observe",
            True, "mode_seen", "armed", scored=False,
        ),
        _visible_control(EpisodeKind.HIDDEN_MODE, mode),
        _step(
            "gate", {"display": "gate", "glyph": "diamond"}, "advance",
            *behavior, scored=True,
        ),
    ))


def _counter_episode(identifier: str, split: EpisodeSplit, length: int = 6) -> TemporalEpisode:
    names = ("zero", "one", "two")
    steps = [
        _step(
            "reset", {"display": "counter_reset"}, "observe",
            True, "counter_reset", "ready", scored=False,
        ),
        _visible_control(EpisodeKind.COUNTER, identifier),
    ]
    for index in range(length):
        steps.append(_step(
            f"pulse_{index}", {"display": "pulse", "glyph": "dot"}, "emit",
            True, names[index % 3], f"counter:{(index + 1) % 3}", scored=True,
        ))
    return TemporalEpisode(identifier, EpisodeKind.COUNTER, split, tuple(steps))


def _object_episode(
    identifier: str, split: EpisodeSplit, location: str
) -> TemporalEpisode:
    return TemporalEpisode(identifier, EpisodeKind.OBJECT_PERMANENCE, split, (
        _step(
            "visible", {"display": "object_visible", "location": location}, "observe",
            True, "object_tracked", "occlusion_next", scored=False,
        ),
        _visible_control(EpisodeKind.OBJECT_PERMANENCE, location),
        _step(
            "occluded", {"display": "occluded", "cover": "solid"}, "locate",
            True, location, f"found:{location}", scored=True,
        ),
    ))


def _rule_episode(identifier: str, split: EpisodeSplit, order: Sequence[str]) -> TemporalEpisode:
    steps: list[EpisodeStep] = [_visible_control(EpisodeKind.RULE_CHANGE, identifier)]
    for index, rule in enumerate(order):
        steps.append(_step(
            f"cue_{index}", {"display": "rule_cue", "rule": rule}, "observe",
            True, "rule_seen", "rule_active", scored=False,
        ))
        for bit in (0, 1):
            output = bit if rule == "identity" else 1 - bit
            steps.append(_step(
                f"query_{index}_{bit}", {"display": "bit", "bit": bit}, "apply_rule",
                True, str(output), "mapped", scored=True,
            ))
    return TemporalEpisode(identifier, EpisodeKind.RULE_CHANGE, split, tuple(steps))


def _gauge_episode(
    identifier: str,
    split: EpisodeSplit,
    mark: int,
    background: int,
    direction: str,
    rotation: int,
) -> TemporalEpisode:
    return TemporalEpisode(identifier, EpisodeKind.GAUGE, split, (
        _visible_control(EpisodeKind.GAUGE, identifier),
        _step(
            "target",
            {
                "display": "gauge_target",
                "mark_color": mark,
                "background_color": background,
                "marker_direction": direction,
                "frame_rotation": rotation,
            },
            "select_forward",
            True,
            str(mark),
            direction,
            scored=True,
            template_readout="$obs.mark_color",
            template_successor="$obs.marker_direction",
        ),
    ))


def _noise_episode(
    identifier: str, split: EpisodeSplit, signal: str, noise: int
) -> TemporalEpisode:
    readout = "A" if signal == "alpha" else "B"
    return TemporalEpisode(identifier, EpisodeKind.NOISE, split, (
        _visible_control(EpisodeKind.NOISE, identifier),
        _step(
            "signal", {"display": "noisy_signal", "signal": signal, "noise": noise},
            "classify", True, readout, "classified", scored=True,
        ),
    ))


def build_temporal_shadow_suite() -> TemporalSuite:
    """Create the finite benchmark.  No external data or randomness is used."""

    calibration = (
        _hidden_episode("cal_hidden_amber", EpisodeSplit.CALIBRATION, "amber"),
        _hidden_episode("cal_hidden_teal", EpisodeSplit.CALIBRATION, "teal"),
        _counter_episode("cal_counter", EpisodeSplit.CALIBRATION),
        _object_episode("cal_object_north", EpisodeSplit.CALIBRATION, "north"),
        _object_episode("cal_object_south", EpisodeSplit.CALIBRATION, "south"),
        _rule_episode(
            "cal_rule", EpisodeSplit.CALIBRATION, ("identity", "invert")
        ),
        _gauge_episode("cal_gauge_n", EpisodeSplit.CALIBRATION, 1, 0, "north", 0),
        _gauge_episode("cal_gauge_e", EpisodeSplit.CALIBRATION, 2, 0, "east", 1),
        _noise_episode("cal_noise_a1", EpisodeSplit.CALIBRATION, "alpha", 11),
        _noise_episode("cal_noise_a2", EpisodeSplit.CALIBRATION, "alpha", 23),
        _noise_episode("cal_noise_b1", EpisodeSplit.CALIBRATION, "beta", 12),
        _noise_episode("cal_noise_b2", EpisodeSplit.CALIBRATION, "beta", 24),
    )
    evaluation = (
        _hidden_episode("eval_hidden_teal", EpisodeSplit.EVALUATION, "teal"),
        _hidden_episode("eval_hidden_amber", EpisodeSplit.EVALUATION, "amber"),
        _counter_episode("eval_counter", EpisodeSplit.EVALUATION),
        _object_episode("eval_object_south", EpisodeSplit.EVALUATION, "south"),
        _object_episode("eval_object_north", EpisodeSplit.EVALUATION, "north"),
        _rule_episode(
            "eval_rule", EpisodeSplit.EVALUATION, ("invert", "identity")
        ),
        _gauge_episode("eval_gauge_s", EpisodeSplit.EVALUATION, 7, 4, "south", 2),
        _gauge_episode("eval_gauge_w", EpisodeSplit.EVALUATION, 9, 3, "west", 3),
        _noise_episode("eval_noise_a", EpisodeSplit.EVALUATION, "alpha", 99),
        _noise_episode("eval_noise_b", EpisodeSplit.EVALUATION, "beta", 98),
    )
    return TemporalSuite(calibration + evaluation)


build_temporal_benchmark = build_temporal_shadow_suite


def _prepared_calibration_samples(suite: TemporalSuite) -> tuple[_PreparedSample, ...]:
    samples: list[_PreparedSample] = []
    for episode in suite.episodes:
        if episode.split is not EpisodeSplit.CALIBRATION:
            continue
        memory = TemporalMemory.empty()
        for step_index, step in enumerate(episode.steps):
            observation = step.observation
            memory = _ingest_observation(memory, observation)
            capsule = build_capsule(
                episode.kind, observation, memory, CapsuleRegime.REFINED, ()
            )
            features = {
                name: memory.feature(name)
                for name in _FEATURES
                if memory.feature(name) is not None
            }
            samples.append(_PreparedSample(
                event_id=f"{episode.episode_id}:{step_index}:{step.step_id}",
                kind=episode.kind,
                action=step.action,
                capsule_hash=capsule.capsule_hash,
                template=step.template,
                features_json=_canonical_object_json(features, "prepared features"),
            ))
            memory = _apply_action(memory, observation, step.action, step.expected)
    return tuple(samples)


def _make_witness(left: _PreparedSample, right: _PreparedSample) -> LeakageWitness:
    contracts: list[str] = []
    if left.template.enabled != right.template.enabled:
        contracts.append("action_applicability")
    if left.template.readout != right.template.readout:
        contracts.append("goal_readout")
    if left.template.successor_class != right.template.successor_class:
        contracts.append("successor_congruence")
    candidates = tuple(
        name for name in _FEATURES
        if left.features.get(name) != right.features.get(name)
        and left.features.get(name) is not None
        and right.features.get(name) is not None
    )
    payload = {
        "capsule_hash": left.capsule_hash,
        "action": left.action,
        "left_event": left.event_id,
        "right_event": right.event_id,
        "kind": left.kind.value,
        "violated_contracts": contracts,
        "candidate_features": list(candidates),
    }
    return LeakageWitness(
        witness_id=content_hash(payload),
        capsule_hash=left.capsule_hash,
        action=left.action,
        left_event=left.event_id,
        right_event=right.event_id,
        kind=left.kind,
        violated_contracts=tuple(contracts),
        candidate_features=candidates,
    )


def discover_leakage_refinements(
    suite: TemporalSuite | None = None,
) -> RefinementArchive:
    """Greedily repair all calibration collisions with observed history fields.

    Gauge and noise normalization are checked by coalescing calibration states;
    neither literal palette coordinates nor noise identifiers are candidates for
    promotion.  Evaluation episodes are never inspected here.
    """

    suite = build_temporal_shadow_suite() if suite is None else suite
    samples = _prepared_calibration_samples(suite)
    groups: dict[tuple[str, str], list[_PreparedSample]] = {}
    for sample in samples:
        groups.setdefault((sample.capsule_hash, sample.action), []).append(sample)
    witnesses: list[LeakageWitness] = []
    for key in sorted(groups):
        group = groups[key]
        for left_index, left in enumerate(group):
            for right in group[left_index + 1 :]:
                if left.template != right.template:
                    witnesses.append(_make_witness(left, right))
    witnesses.sort(key=lambda item: item.witness_id)

    unresolved = {item.witness_id for item in witnesses}
    by_id = {item.witness_id: item for item in witnesses}
    accepted: list[str] = []
    proposals: list[RefinementProposal] = []
    priority = {name: index for index, name in enumerate(_FEATURES)}
    while unresolved:
        coverage = {
            feature: tuple(sorted(
                witness_id for witness_id in unresolved
                if feature in by_id[witness_id].candidate_features
            ))
            for feature in _FEATURES if feature not in accepted
        }
        feature, repaired = min(
            coverage.items(),
            key=lambda item: (-len(item[1]), priority[item[0]]),
        )
        if not repaired:
            break
        unresolved.difference_update(repaired)
        accepted.append(feature)
        proposals.append(RefinementProposal(
            feature=feature,
            repaired_witnesses=repaired,
            remaining_witnesses=len(unresolved),
            accepted=True,
            reason="smallest trusted observed-history split repairing calibration leakage",
        ))
    return RefinementArchive(
        witnesses=tuple(witnesses),
        proposals=tuple(proposals),
        accepted_features=tuple(accepted),
        unresolved_witnesses=tuple(sorted(unresolved)),
    )


def _rule_key(capsule: PredictiveCapsule, action: str) -> str:
    return content_hash({"capsule": capsule.semantic_record(), "action": action})


def _observe_rule(
    rules: tuple[ModelRule, ...], key: str, template: BehaviorTemplate
) -> tuple[ModelRule, ...]:
    table = {rule.key: set(rule.templates_json) for rule in rules}
    table.setdefault(key, set()).add(canonical_json(template.to_record()))
    return tuple(
        ModelRule(rule_key, tuple(sorted(table[rule_key])))
        for rule_key in sorted(table)
    )


def _predict(
    rules: Sequence[ModelRule],
    key: str,
    observation: Mapping[str, Any],
) -> tuple[PredictionStatus, Behavior | None]:
    rule = next((item for item in rules if item.key == key), None)
    if rule is None:
        return PredictionStatus.UNKNOWN, None
    if len(rule.templates_json) != 1:
        return PredictionStatus.AMBIGUOUS, None
    template = BehaviorTemplate.from_record(decode_json_bytes(rule.templates_json[0]))
    return PredictionStatus.UNIQUE, template.instantiate(observation)


def start_temporal_evaluation(
    config: EvaluationConfig,
    *,
    suite: TemporalSuite | None = None,
    archive: RefinementArchive | None = None,
) -> TemporalRunState:
    suite = build_temporal_shadow_suite() if suite is None else suite
    archive = discover_leakage_refinements(suite) if archive is None else archive
    features = (
        archive.accepted_features
        if config.capsule_regime is CapsuleRegime.REFINED
        else ()
    )
    run_id = content_hash({
        "suite_id": suite.suite_id,
        "archive_id": archive.archive_id,
        "config": config.to_record(),
    })
    return TemporalRunState(
        config=config,
        suite_id=suite.suite_id,
        archive_id=archive.archive_id,
        run_id=run_id,
        phase=RunPhase.CALIBRATION,
        episode_index=0,
        step_index=0,
        memory=TemporalMemory.empty(),
        refinement_features=features,
        rules=(),
        transcript=(),
    )


def _next_phase(suite: TemporalSuite, episode_index: int) -> RunPhase:
    if episode_index >= len(suite.episodes):
        return RunPhase.COMPLETE
    return RunPhase(suite.episodes[episode_index].split.value)


def _cursor_event_count(
    suite: TemporalSuite, episode_index: int, step_index: int
) -> int:
    if episode_index > len(suite.episodes):
        raise ValueError("episode cursor exceeds suite length")
    if episode_index == len(suite.episodes):
        if step_index != 0:
            raise ValueError("complete cursor must have step index zero")
        return suite.event_count
    if step_index >= len(suite.episodes[episode_index].steps):
        raise ValueError("step cursor exceeds episode length")
    return sum(
        len(episode.steps) for episode in suite.episodes[:episode_index]
    ) + step_index


def advance_temporal_evaluation(
    state: TemporalRunState,
    *,
    suite: TemporalSuite | None = None,
    archive: RefinementArchive | None = None,
    max_events: int | None = None,
) -> TemporalRunState:
    """Advance a run functionally; evaluation outcomes never update the model."""

    suite = build_temporal_shadow_suite() if suite is None else suite
    archive = discover_leakage_refinements(suite) if archive is None else archive
    if state.suite_id != suite.suite_id:
        raise ValueError("continuation state belongs to another temporal suite")
    if state.archive_id != archive.archive_id:
        raise ValueError("continuation state belongs to another refinement archive")
    expected_run_id = content_hash({
        "suite_id": suite.suite_id,
        "archive_id": archive.archive_id,
        "config": state.config.to_record(),
    })
    if state.run_id != expected_run_id:
        raise ValueError("continuation run ID does not match its configuration")
    expected_features = (
        archive.accepted_features
        if state.config.capsule_regime is CapsuleRegime.REFINED
        else ()
    )
    if state.refinement_features != expected_features:
        raise ValueError("continuation refinement feature contract mismatch")
    if len(state.transcript) != _cursor_event_count(
        suite, state.episode_index, state.step_index
    ):
        raise ValueError("continuation transcript length does not match its cursor")
    if state.phase is not _next_phase(suite, state.episode_index):
        raise ValueError("continuation phase does not match its cursor")
    if max_events is not None:
        require_nonnegative_int(max_events, "max_events")
    remaining = max_events
    current = state
    while current.phase is not RunPhase.COMPLETE and (remaining is None or remaining > 0):
        if current.episode_index >= len(suite.episodes):
            raise ValueError("non-complete state points beyond the episode suite")
        episode = suite.episodes[current.episode_index]
        if current.phase.value != episode.split.value:
            raise ValueError("continuation phase does not match its episode")
        if current.step_index >= len(episode.steps):
            raise ValueError("continuation step points beyond its episode")
        step = episode.steps[current.step_index]
        observation = step.observation
        base_memory = (
            TemporalMemory.empty()
            if current.config.memory_regime is MemoryRegime.STATELESS
            else current.memory
        )
        pre_memory = _ingest_observation(base_memory, observation)
        capsule = build_capsule(
            episode.kind,
            observation,
            pre_memory,
            current.config.capsule_regime,
            current.refinement_features,
        )
        key = _rule_key(capsule, step.action)
        status, prediction = _predict(current.rules, key, observation)
        snapshot_hash = content_hash({
            "prior_state_hash": current.state_hash,
            "episode_id": episode.episode_id,
            "step_index": current.step_index,
            "pre_action_memory": pre_memory.to_record(),
            "capsule_hash": capsule.capsule_hash,
        })
        receipt = ActionReceipt.seal(
            run_id=current.run_id,
            episode_id=episode.episode_id,
            step_index=current.step_index,
            action=step.action,
            snapshot_hash=snapshot_hash,
            capsule_hash=capsule.capsule_hash,
            prediction_status=status,
            prediction=prediction,
        )
        # The target is exposed only after the immutable receipt above exists.
        actual = step.expected
        outcome = ActionOutcome.reveal(receipt, actual)
        event = TemporalEventRecord(
            split=episode.split,
            kind=episode.kind,
            episode_id=episode.episode_id,
            step_id=step.step_id,
            step_index=current.step_index,
            action=step.action,
            scored=step.scored,
            receipt=receipt,
            outcome=outcome,
        )
        rules = current.rules
        if episode.split is EpisodeSplit.CALIBRATION:
            rules = _observe_rule(rules, key, step.template)
        post_memory = (
            TemporalMemory.empty()
            if current.config.memory_regime is MemoryRegime.STATELESS
            else _apply_action(pre_memory, observation, step.action, actual)
        )
        next_episode = current.episode_index
        next_step = current.step_index + 1
        if next_step == len(episode.steps):
            next_episode += 1
            next_step = 0
            post_memory = TemporalMemory.empty()
        current = TemporalRunState(
            config=current.config,
            suite_id=current.suite_id,
            archive_id=current.archive_id,
            run_id=current.run_id,
            phase=_next_phase(suite, next_episode),
            episode_index=next_episode,
            step_index=next_step,
            memory=post_memory,
            refinement_features=current.refinement_features,
            rules=rules,
            transcript=current.transcript + (event,),
        )
        if remaining is not None:
            remaining -= 1
    return current


resume_temporal_evaluation = advance_temporal_evaluation


def evaluate_temporal_state(state: TemporalRunState) -> TemporalEvaluation:
    if state.phase is not RunPhase.COMPLETE:
        raise ValueError("temporal evaluation is not complete")
    evaluation_events = [
        event for event in state.transcript
        if event.split is EpisodeSplit.EVALUATION and event.scored
    ]
    by_kind: list[KindMetrics] = []
    for kind in EpisodeKind:
        events = [event for event in evaluation_events if event.kind is kind]
        by_kind.append(KindMetrics(
            kind=kind,
            scored=len(events),
            exact=sum(event.outcome.prediction_exact for event in events),
            abstained=sum(event.receipt.prediction is None for event in events),
            ambiguous=sum(
                event.receipt.prediction_status is PredictionStatus.AMBIGUOUS
                for event in events
            ),
            unknown=sum(
                event.receipt.prediction_status is PredictionStatus.UNKNOWN
                for event in events
            ),
        ))
    exact = sum(event.outcome.prediction_exact for event in evaluation_events)
    ambiguous = sum(
        event.receipt.prediction_status is PredictionStatus.AMBIGUOUS
        for event in evaluation_events
    )
    unknown = sum(
        event.receipt.prediction_status is PredictionStatus.UNKNOWN
        for event in evaluation_events
    )
    control_events = [
        event for event in evaluation_events if event.step_id.startswith("control_")
    ]
    causal_events = [
        event for event in evaluation_events if not event.step_id.startswith("control_")
    ]
    return TemporalEvaluation(
        config=state.config,
        scored=len(evaluation_events),
        exact=exact,
        abstained=ambiguous + unknown,
        ambiguous=ambiguous,
        unknown=unknown,
        control_scored=len(control_events),
        control_exact=sum(event.outcome.prediction_exact for event in control_events),
        causal_scored=len(causal_events),
        causal_exact=sum(event.outcome.prediction_exact for event in causal_events),
        applicability_exact=sum(
            event.receipt.prediction is not None
            and event.receipt.prediction.enabled == event.outcome.actual.enabled
            for event in evaluation_events
        ),
        readout_exact=sum(
            event.receipt.prediction is not None
            and event.receipt.prediction.readout == event.outcome.actual.readout
            for event in evaluation_events
        ),
        successor_exact=sum(
            event.receipt.prediction is not None
            and event.receipt.prediction.successor_class
            == event.outcome.actual.successor_class
            for event in evaluation_events
        ),
        kind_metrics=tuple(by_kind),
        receipt_count=len(state.transcript),
        verified_receipts=sum(event.receipt.verify() for event in state.transcript),
        transcript_hash=content_hash([event.to_record() for event in state.transcript]),
        final_state_hash=state.state_hash,
    )


def execute_temporal_configuration(
    config: EvaluationConfig,
    *,
    suite: TemporalSuite | None = None,
    archive: RefinementArchive | None = None,
) -> TemporalRunState:
    suite = build_temporal_shadow_suite() if suite is None else suite
    archive = discover_leakage_refinements(suite) if archive is None else archive
    start = start_temporal_evaluation(config, suite=suite, archive=archive)
    return advance_temporal_evaluation(start, suite=suite, archive=archive)


def run_temporal_configuration(
    config: EvaluationConfig,
    *,
    suite: TemporalSuite | None = None,
    archive: RefinementArchive | None = None,
) -> TemporalEvaluation:
    return evaluate_temporal_state(
        execute_temporal_configuration(config, suite=suite, archive=archive)
    )


def serialize_temporal_state(state: TemporalRunState) -> str:
    return state.to_json()


def restore_temporal_state(value: bytes | bytearray | str) -> TemporalRunState:
    return TemporalRunState.from_json(value)


def continue_serialized_temporal_run(value: bytes | bytearray | str) -> str:
    """Fresh-interpreter entry point for the built-in deterministic suite.

    The function consumes and emits only canonical JSON.  A release audit can
    invoke it in a newly spawned Python interpreter without sharing an object,
    cache, mutable registry, or module-global run state with the producer.
    """

    suite = build_temporal_shadow_suite()
    archive = discover_leakage_refinements(suite)
    restored = restore_temporal_state(value)
    completed = advance_temporal_evaluation(
        restored, suite=suite, archive=archive
    )
    return serialize_temporal_state(completed)


def _history_bearing_checkpoint(suite: TemporalSuite) -> int:
    """Stop after an evaluation cue, while its memory is still required."""

    preceding = 0
    for episode in suite.episodes:
        if (
            episode.split is EpisodeSplit.EVALUATION
            and episode.kind is EpisodeKind.HIDDEN_MODE
        ):
            # The hidden-mode cue is first.  Restoring here proves that a fresh
            # process receives the observed mode from the snapshot rather than
            # from module globals or a replay of the episode prefix.
            return preceding + 1
        preceding += len(episode.steps)
    raise ValueError("suite contains no evaluation hidden-mode episode")


def verify_fresh_process_continuation(
    config: EvaluationConfig,
    *,
    suite: TemporalSuite | None = None,
    archive: RefinementArchive | None = None,
    checkpoint_events: int | None = None,
) -> ContinuationVerification:
    suite = build_temporal_shadow_suite() if suite is None else suite
    archive = discover_leakage_refinements(suite) if archive is None else archive
    if checkpoint_events is None:
        checkpoint_events = _history_bearing_checkpoint(suite)
    require_nonnegative_int(checkpoint_events, "checkpoint_events")
    if checkpoint_events >= suite.event_count:
        raise ValueError("checkpoint must precede run completion")
    uninterrupted = execute_temporal_configuration(config, suite=suite, archive=archive)
    partial = advance_temporal_evaluation(
        start_temporal_evaluation(config, suite=suite, archive=archive),
        suite=suite,
        archive=archive,
        max_events=checkpoint_events,
    )
    encoded = serialize_temporal_state(partial)
    restored = restore_temporal_state(encoded)
    byte_stable = serialize_temporal_state(restored) == encoded
    resumed = advance_temporal_evaluation(restored, suite=suite, archive=archive)
    return ContinuationVerification(
        config_id=config.config_id,
        checkpoint_events=checkpoint_events,
        serialized_state_hash=partial.state_hash,
        uninterrupted_final_hash=uninterrupted.state_hash,
        resumed_final_hash=resumed.state_hash,
        byte_stable=byte_stable,
        continuation_equivalent=(uninterrupted.state_hash == resumed.state_hash),
    )


def run_temporal_shadow_benchmark() -> TemporalBenchmarkResult:
    """Run the controlled 2x2 audit and fresh-process replay checks."""

    suite = build_temporal_shadow_suite()
    archive = discover_leakage_refinements(suite)
    configs = tuple(
        EvaluationConfig(capsule, memory)
        for capsule in CapsuleRegime
        for memory in MemoryRegime
    )
    evaluations = tuple(
        run_temporal_configuration(config, suite=suite, archive=archive)
        for config in configs
    )
    continuations = tuple(
        verify_fresh_process_continuation(
            config, suite=suite, archive=archive,
        )
        for config in configs
    )
    result = TemporalBenchmarkResult(
        suite_id=suite.suite_id,
        archive=archive,
        evaluations=evaluations,
        continuations=continuations,
    )
    matrix = {
        evaluation.config.config_id: evaluation for evaluation in result.evaluations
    }
    fixed_stateless = matrix["fixed__stateless"]
    fixed_persistent = matrix["fixed__persistent"]
    refined_stateless = matrix["refined__stateless"]
    refined_persistent = matrix["refined__persistent"]
    if fixed_stateless.exact != fixed_persistent.exact:
        raise AssertionError("fixed capsule unexpectedly consumed persistence")
    if refined_stateless.exact <= fixed_stateless.exact:
        raise AssertionError("normalization control did not improve static transfer")
    if refined_persistent.exact <= refined_stateless.exact:
        raise AssertionError("persistent refined capsule did not improve temporal transfer")
    if refined_persistent.exact != refined_persistent.scored:
        raise AssertionError("refined persistent control did not recover every synthetic target")
    if archive.unresolved_witnesses:
        raise AssertionError("calibration leakage remained after refinement")
    if not all(item.byte_stable and item.continuation_equivalent for item in continuations):
        raise AssertionError("fresh-process temporal continuation mismatch")
    return result


run_temporal_benchmark = run_temporal_shadow_benchmark


def temporal_shadow_audit_record() -> dict[str, Any]:
    """Return the complete audit as detached canonical JSON-compatible data."""

    return canonical_value(run_temporal_shadow_benchmark().to_record())


__all__ = [
    "TEMPORAL_SCHEMA_VERSION",
    "TEMPORAL_AUDIT_SCOPE",
    "TEMPORAL_CLAIM_BOUNDARY",
    "EpisodeKind",
    "EpisodeSplit",
    "CapsuleRegime",
    "MemoryRegime",
    "PredictionStatus",
    "RunPhase",
    "Behavior",
    "BehaviorTemplate",
    "EpisodeStep",
    "TemporalEpisode",
    "TemporalSuite",
    "TemporalMemory",
    "PredictiveCapsule",
    "LeakageWitness",
    "RefinementProposal",
    "RefinementArchive",
    "EvaluationConfig",
    "ModelRule",
    "ActionReceipt",
    "PreActionReceipt",
    "ActionOutcome",
    "TemporalEventRecord",
    "TemporalRunState",
    "KindMetrics",
    "TemporalEvaluation",
    "ContinuationVerification",
    "TemporalBenchmarkResult",
    "build_capsule",
    "build_temporal_shadow_suite",
    "build_temporal_benchmark",
    "discover_leakage_refinements",
    "start_temporal_evaluation",
    "advance_temporal_evaluation",
    "resume_temporal_evaluation",
    "evaluate_temporal_state",
    "execute_temporal_configuration",
    "run_temporal_configuration",
    "serialize_temporal_state",
    "restore_temporal_state",
    "continue_serialized_temporal_run",
    "verify_fresh_process_continuation",
    "run_temporal_shadow_benchmark",
    "run_temporal_benchmark",
    "temporal_shadow_audit_record",
]
