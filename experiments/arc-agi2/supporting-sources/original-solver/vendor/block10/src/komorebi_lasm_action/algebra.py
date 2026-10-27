"""Mechanically safe normalization of finite PR-LASM program words.

This module separates three very different claims:

* ``MECHANICAL`` relations are consequences of exact built-in actions (the D4
  group, total coordinate translations, and finite bijections with preserved
  guards).
* ``FINITE_EXHAUSTIVE`` relations were checked over one explicitly declared,
  closed finite state domain and may be used only when that exact domain digest
  is supplied again.
* ``METAMORPHIC`` and ``OBSERVED`` evidence can guide routing but is never an
  authorization to rewrite executable programs.

In particular, a partial identity is not deleted: removing it would erase its
applicability guard and violate action congruence even though its values agree
where it is defined.
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass
from enum import Enum
from numbers import Integral
from typing import Any, Callable, Iterable, Mapping, Sequence, TypeAlias

from .canonical import (
    canonical_json,
    canonical_value,
    sha256_record,
)

from .gauge import D4_NAMES, compose_d4, inverse_d4, normalize_d4_name


SCHEMA_VERSION = 1
MAX_NORMALIZATION_STEPS = 10_000

StateExecutor: TypeAlias = Callable[["ActionAtom", object], object]
_LOCALLY_VERIFIED_CERTIFICATE_IDS: set[str] = set()


def _canonical_parameters(value: Mapping[str, Any]) -> str:
    if not isinstance(value, Mapping):
        raise TypeError("action parameters must be a mapping")
    return canonical_json(value)


def _reject_json_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON number {token!r} is forbidden")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _decode_canonical_parameters(parameters_json: object) -> dict[str, Any]:
    if not isinstance(parameters_json, str) or not parameters_json:
        raise ValueError("parameters_json must be nonempty text")
    try:
        value = json.loads(
            parameters_json,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, TypeError) as error:
        raise ValueError("parameters_json must contain valid JSON") from error
    if not isinstance(value, dict):
        raise TypeError("parameters_json must encode a JSON object")
    if canonical_json(value) != parameters_json:
        raise ValueError("parameters_json must use canonical sorted compact JSON")
    return value


class AlgebraError(ValueError):
    """Base class for rejected algebra operations."""


class AlgebraTypeError(AlgebraError):
    """A program word is not type composable."""


class UntrustedRelationError(AlgebraError):
    """A requested rewrite lacks an actionable exact certificate."""


class NormalizationLimitError(AlgebraError):
    """Canonical normalization exceeded its deterministic step budget."""


class TrustTier(str, Enum):
    MECHANICAL = "mechanical"
    FINITE_EXHAUSTIVE = "finite_exhaustive"
    METAMORPHIC = "metamorphic"
    OBSERVED = "observed"


class RelationKind(str, Enum):
    IDENTITY = "identity"
    INVERSE = "inverse"
    IDEMPOTENT = "idempotent"
    COMMUTES = "commutes"


def _require_name(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty and trimmed")
    if any(ord(character) < 33 or ord(character) > 126 for character in value):
        raise ValueError(f"{label} must contain printable non-whitespace ASCII")
    return value


def _require_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{label} must be a SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as error:
        raise ValueError(f"{label} must be a SHA-256 hex digest") from error
    return value.lower()


def _exact_fields(record: object, fields: set[str], label: str) -> Mapping[str, object]:
    if not isinstance(record, Mapping):
        raise TypeError(f"{label} must be a mapping")
    if set(record) != fields:
        missing = sorted(fields - set(record))
        unknown = sorted(set(record) - fields)
        raise ValueError(f"invalid {label} fields; missing={missing}, unknown={unknown}")
    return record


_MECHANICAL_GAUGE_TYPES = {
    "d4": "grid",
    "coordinate_translation": "cell_set",
    "palette_bijection": "grid",
    "object_renaming": "object_graph",
}


def _validate_mechanical_builtin(
    namespace: str,
    name: str,
    input_type: str,
    output_type: str,
    parameters: Mapping[str, Any],
) -> None:
    """Reject nominal built-ins outside their exact trusted semantics.

    Mechanical rewrites are justified by these concrete actions, not merely
    by a caller-selected namespace/name pair.  In particular, coordinate
    translation is total on an unbounded ``cell_set``; it is not a mechanical
    group action on a clipped finite ``grid``.
    """

    if namespace != "gauge" or name not in _MECHANICAL_GAUGE_TYPES:
        return
    expected_type = _MECHANICAL_GAUGE_TYPES[name]
    if input_type != expected_type or output_type != expected_type:
        raise AlgebraTypeError(
            f"mechanical gauge action {name!r} requires "
            f"{expected_type!r} -> {expected_type!r}"
        )
    if name == "d4":
        if set(parameters) != {"transform"}:
            raise AlgebraError("D4 atom requires exactly the transform parameter")
        normalize_d4_name(parameters["transform"])
        return
    if name == "coordinate_translation":
        if set(parameters) != {"offset"}:
            raise AlgebraError(
                "coordinate translation requires exactly the offset parameter"
            )
        offset = parameters["offset"]
        if (
            not isinstance(offset, list)
            or len(offset) != 2
            or any(
                isinstance(item, bool) or not isinstance(item, Integral)
                for item in offset
            )
        ):
            raise AlgebraError(
                "coordinate translation offset must contain two integers"
            )
        return

    if set(parameters) != {"mapping"} or not isinstance(
        parameters["mapping"], list
    ):
        raise AlgebraError(f"{name} requires exactly one mapping parameter")
    pairs: list[tuple[object, object]] = []
    for pair in parameters["mapping"]:
        if not isinstance(pair, list) or len(pair) != 2:
            raise AlgebraError(f"{name} mapping entries must be pairs")
        source, target = pair
        if name == "palette_bijection":
            if (
                isinstance(source, bool)
                or not isinstance(source, Integral)
                or isinstance(target, bool)
                or not isinstance(target, Integral)
                or not 0 <= int(source) <= 9
                or not 0 <= int(target) <= 9
            ):
                raise AlgebraError("palette bijection colors must lie in 0..9")
            source, target = int(source), int(target)
        else:
            source = _require_name(source, "source object label")
            target = _require_name(target, "target object label")
        pairs.append((source, target))
    if not pairs:
        raise AlgebraError(f"{name} mapping must not be empty")
    if len({source for source, _ in pairs}) != len(pairs):
        raise AlgebraError(f"{name} sources must be unique")
    if len({target for _, target in pairs}) != len(pairs):
        raise AlgebraError(f"{name} targets must be unique")


@dataclass(frozen=True, slots=True)
class ActionAtom:
    """One immutable typed action invocation."""

    namespace: str
    name: str
    input_type: str
    output_type: str
    parameters_json: str = "{}"
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "namespace", _require_name(self.namespace, "namespace"))
        object.__setattr__(self, "name", _require_name(self.name, "action name"))
        object.__setattr__(self, "input_type", _require_name(self.input_type, "input type"))
        object.__setattr__(self, "output_type", _require_name(self.output_type, "output type"))
        parameters = _decode_canonical_parameters(self.parameters_json)
        _validate_mechanical_builtin(
            self.namespace,
            self.name,
            self.input_type,
            self.output_type,
            parameters,
        )
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    @classmethod
    def from_parameters(
        cls,
        namespace: str,
        name: str,
        input_type: str,
        output_type: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> "ActionAtom":
        return cls(
            namespace=namespace,
            name=name,
            input_type=input_type,
            output_type=output_type,
            parameters_json=_canonical_parameters(parameters or {}),
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return _decode_canonical_parameters(self.parameters_json)

    def to_record(self) -> dict[str, object]:
        return {
            "input_type": self.input_type,
            "name": self.name,
            "namespace": self.namespace,
            "output_type": self.output_type,
            "parameters": self.parameters,
            "schema_version": self.schema_version,
        }

    @classmethod
    def from_record(cls, record: object) -> "ActionAtom":
        body = _exact_fields(
            record,
            {"input_type", "name", "namespace", "output_type", "parameters", "schema_version"},
            "action atom record",
        )
        if isinstance(body["schema_version"], bool) or body["schema_version"] != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        parameters = body["parameters"]
        if not isinstance(parameters, Mapping):
            raise TypeError("action parameters must be a mapping")
        return cls.from_parameters(
            body["namespace"],  # type: ignore[arg-type]
            body["name"],  # type: ignore[arg-type]
            body["input_type"],  # type: ignore[arg-type]
            body["output_type"],  # type: ignore[arg-type]
            parameters,
        )

    @property
    def signature(self) -> str:
        return sha256_record(self.to_record())

    @property
    def canonical_key(self) -> str:
        return canonical_json(self.to_record())


@dataclass(frozen=True, slots=True)
class ProgramWord:
    """A finite, exactly type-checked sequence of actions."""

    atoms: tuple[ActionAtom, ...]
    empty_type: str = "grid"

    def __post_init__(self) -> None:
        if isinstance(self.atoms, (str, bytes)) or not isinstance(self.atoms, Sequence):
            raise TypeError("program atoms must be a sequence")
        normalized = tuple(self.atoms)
        if any(not isinstance(atom, ActionAtom) for atom in normalized):
            raise TypeError("program entries must be ActionAtom values")
        object.__setattr__(self, "atoms", normalized)
        object.__setattr__(self, "empty_type", _require_name(self.empty_type, "empty type"))
        for index, (left, right) in enumerate(zip(normalized, normalized[1:])):
            if left.output_type != right.input_type:
                raise AlgebraTypeError(
                    f"word type mismatch at {index}: {left.output_type!r} != {right.input_type!r}"
                )
        if normalized:
            # ``empty_type`` is operational only after a word cancels fully;
            # canonicalize away caller-selected values on nonempty words.
            object.__setattr__(self, "empty_type", normalized[0].input_type)

    @property
    def input_type(self) -> str:
        return self.atoms[0].input_type if self.atoms else self.empty_type

    @property
    def output_type(self) -> str:
        return self.atoms[-1].output_type if self.atoms else self.empty_type

    def to_record(self) -> dict[str, object]:
        return {
            "atoms": [atom.to_record() for atom in self.atoms],
            "empty_type": self.empty_type,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "schema_version": SCHEMA_VERSION,
        }

    @classmethod
    def from_record(cls, record: object) -> "ProgramWord":
        body = _exact_fields(
            record,
            {"atoms", "empty_type", "input_type", "output_type", "schema_version"},
            "program word record",
        )
        if isinstance(body["schema_version"], bool) or body["schema_version"] != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        atoms_record = body["atoms"]
        if isinstance(atoms_record, (str, bytes)) or not isinstance(atoms_record, Sequence):
            raise TypeError("program atoms record must be a sequence")
        word = cls(tuple(ActionAtom.from_record(item) for item in atoms_record), body["empty_type"])  # type: ignore[arg-type]
        if body["input_type"] != word.input_type or body["output_type"] != word.output_type:
            raise ValueError("program record boundary types do not match its atoms")
        return word

    @property
    def content_hash(self) -> str:
        return sha256_record(self.to_record())


def d4_atom(transform: object, *, value_type: str = "grid") -> ActionAtom:
    return ActionAtom.from_parameters(
        "gauge", "d4", value_type, value_type, {"transform": normalize_d4_name(transform)}
    )


def coordinate_translation_atom(
    row_delta: object,
    column_delta: object,
    *,
    value_type: str = "cell_set",
) -> ActionAtom:
    if isinstance(row_delta, bool) or not isinstance(row_delta, Integral):
        raise TypeError("row_delta must be an integer")
    if isinstance(column_delta, bool) or not isinstance(column_delta, Integral):
        raise TypeError("column_delta must be an integer")
    return ActionAtom.from_parameters(
        "gauge",
        "coordinate_translation",
        value_type,
        value_type,
        {"offset": [int(row_delta), int(column_delta)]},
    )


def palette_bijection_atom(
    mapping: Mapping[int, int] | Sequence[Sequence[int]],
    *,
    value_type: str = "grid",
) -> ActionAtom:
    items = mapping.items() if isinstance(mapping, Mapping) else mapping
    normalized: list[tuple[int, int]] = []
    for pair in items:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise TypeError("palette entries must be two-element sequences")
        source, target = pair
        if (
            isinstance(source, bool)
            or not isinstance(source, Integral)
            or isinstance(target, bool)
            or not isinstance(target, Integral)
        ):
            raise TypeError("palette entries must contain integer colors")
        source_int, target_int = int(source), int(target)
        if not 0 <= source_int <= 9 or not 0 <= target_int <= 9:
            raise ValueError("palette colors must lie in 0..9")
        normalized.append((source_int, target_int))
    if not normalized:
        raise ValueError("palette bijection must not be empty")
    if len({source for source, _ in normalized}) != len(normalized):
        raise ValueError("palette sources must be unique")
    if len({target for _, target in normalized}) != len(normalized):
        raise ValueError("palette targets must be unique")
    return ActionAtom.from_parameters(
        "gauge",
        "palette_bijection",
        value_type,
        value_type,
        {"mapping": [list(pair) for pair in sorted(normalized)]},
    )


def object_renaming_atom(
    mapping: Mapping[str, str] | Sequence[Sequence[str]],
    *,
    value_type: str = "object_graph",
) -> ActionAtom:
    items = mapping.items() if isinstance(mapping, Mapping) else mapping
    normalized: list[tuple[str, str]] = []
    for pair in items:
        if not isinstance(pair, (tuple, list)) or len(pair) != 2:
            raise TypeError("object-renaming entries must be pairs")
        normalized.append(
            (_require_name(pair[0], "source label"), _require_name(pair[1], "target label"))
        )
    if not normalized:
        raise ValueError("object renaming must not be empty")
    if len({source for source, _ in normalized}) != len(normalized):
        raise ValueError("object-renaming sources must be unique")
    if len({target for _, target in normalized}) != len(normalized):
        raise ValueError("object-renaming targets must be unique")
    return ActionAtom.from_parameters(
        "gauge",
        "object_renaming",
        value_type,
        value_type,
        {"mapping": [list(pair) for pair in sorted(normalized)]},
    )


def _is_kind(atom: ActionAtom, name: str) -> bool:
    return atom.namespace == "gauge" and atom.name == name and atom.input_type == atom.output_type


def _d4_parameter(atom: ActionAtom) -> str | None:
    if not _is_kind(atom, "d4"):
        return None
    parameters = atom.parameters
    if set(parameters) != {"transform"}:
        raise AlgebraError("D4 atom requires exactly the transform parameter")
    return normalize_d4_name(parameters["transform"])


def _translation_parameter(atom: ActionAtom) -> tuple[int, int] | None:
    if not _is_kind(atom, "coordinate_translation"):
        return None
    parameters = atom.parameters
    if set(parameters) != {"offset"}:
        raise AlgebraError("coordinate translation requires exactly the offset parameter")
    value = parameters["offset"]
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(isinstance(item, bool) or not isinstance(item, Integral) for item in value)
    ):
        raise AlgebraError("coordinate translation offset must contain two integers")
    return int(value[0]), int(value[1])


def _mapping_parameter(atom: ActionAtom, name: str) -> tuple[tuple[object, object], ...] | None:
    if not _is_kind(atom, name):
        return None
    parameters = atom.parameters
    if set(parameters) != {"mapping"} or not isinstance(parameters["mapping"], list):
        raise AlgebraError(f"{name} requires exactly one mapping parameter")
    result: list[tuple[object, object]] = []
    for pair in parameters["mapping"]:
        if not isinstance(pair, list) or len(pair) != 2:
            raise AlgebraError(f"{name} mapping entries must be pairs")
        result.append((pair[0], pair[1]))
    if len({source for source, _ in result}) != len(result):
        raise AlgebraError(f"{name} sources must be unique")
    if len({target for _, target in result}) != len(result):
        raise AlgebraError(f"{name} targets must be unique")
    return tuple(sorted(result))


def _compose_bijections(
    first: tuple[tuple[object, object], ...],
    second: tuple[tuple[object, object], ...],
) -> tuple[tuple[object, object], ...] | None:
    first_map, second_map = dict(first), dict(second)
    # Containment of the first image in the second domain preserves the exact
    # applicability guard of the two-action word; extra second-domain entries
    # are unreachable and therefore irrelevant.
    if not set(first_map.values()).issubset(second_map):
        return None
    return tuple(sorted((source, second_map[middle]) for source, middle in first_map.items()))


def mechanical_identity(atom: ActionAtom) -> bool:
    """Whether deleting this atom preserves values *and* applicability."""

    d4 = _d4_parameter(atom)
    if d4 is not None:
        return d4 == "id"
    translation = _translation_parameter(atom)
    if translation is not None:
        return translation == (0, 0)
    palette = _mapping_parameter(atom, "palette_bijection")
    if palette is not None:
        # A partial identity remains an applicability guard and is not erased.
        return {source for source, _ in palette} == set(range(10)) and all(
            source == target for source, target in palette
        )
    return False


def mechanical_inverse(left: ActionAtom, right: ActionAtom) -> bool:
    if left.input_type != right.output_type or left.output_type != right.input_type:
        return False
    left_d4, right_d4 = _d4_parameter(left), _d4_parameter(right)
    if left_d4 is not None and right_d4 is not None:
        return inverse_d4(left_d4) == right_d4
    left_translation = _translation_parameter(left)
    right_translation = _translation_parameter(right)
    if left_translation is not None and right_translation is not None:
        return tuple(a + b for a, b in zip(left_translation, right_translation)) == (0, 0)
    left_palette = _mapping_parameter(left, "palette_bijection")
    right_palette = _mapping_parameter(right, "palette_bijection")
    if left_palette is not None and right_palette is not None:
        # Only total ARC-color permutations can cancel to the global identity.
        if {source for source, _ in left_palette} != set(range(10)):
            return False
        composed = _compose_bijections(left_palette, right_palette)
        return composed is not None and all(source == target for source, target in composed)
    return False


def mechanical_idempotent(atom: ActionAtom) -> bool:
    # This predicate denotes a globally reusable idempotence law.  Guarded
    # finite bijections are instead composed explicitly, preserving their
    # partial domain in the replacement atom.
    return mechanical_identity(atom)


def mechanical_commutes(left: ActionAtom, right: ActionAtom) -> bool:
    if (
        left.input_type != left.output_type
        or right.input_type != right.output_type
        or left.input_type != right.input_type
    ):
        return False
    left_d4, right_d4 = _d4_parameter(left), _d4_parameter(right)
    if left_d4 is not None and right_d4 is not None:
        return compose_d4(left_d4, right_d4) == compose_d4(right_d4, left_d4)
    left_translation = _translation_parameter(left)
    right_translation = _translation_parameter(right)
    if left_translation is not None and right_translation is not None:
        return True
    left_palette = _mapping_parameter(left, "palette_bijection")
    right_palette = _mapping_parameter(right, "palette_bijection")
    if left_palette is not None and right_palette is not None:
        forward = _compose_bijections(left_palette, right_palette)
        backward = _compose_bijections(right_palette, left_palette)
        return forward is not None and forward == backward
    # A spatial D4 action changes positions only; a color bijection changes
    # values only.  The color guard is invariant under permutation of cells.
    if (left_d4 is not None and right_palette is not None) or (
        left_palette is not None and right_d4 is not None
    ):
        return True
    return False


@dataclass(frozen=True, slots=True)
class RelationCertificate:
    """Evidence for one exact-signature relation.

    Public construction and decoding are safe because actionability does not
    derive from the record's claim alone.  A finite certificate must also have
    been replay-verified by this process.  Mechanical certificates are
    rejected; built-in mechanical relations are recognized directly.
    """

    kind: RelationKind
    left_signature: str
    right_signature: str | None
    trust_tier: TrustTier
    domain_digest: str
    evidence_digest: str
    checked_cases: int
    applicable_cases: int
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.kind, RelationKind):
            try:
                object.__setattr__(self, "kind", RelationKind(self.kind))
            except (TypeError, ValueError) as error:
                raise ValueError("unknown relation kind") from error
        object.__setattr__(self, "left_signature", _require_digest(self.left_signature, "left signature"))
        if self.kind in {RelationKind.INVERSE, RelationKind.COMMUTES}:
            if self.right_signature is None:
                raise ValueError(f"{self.kind.value} relation requires a right signature")
            object.__setattr__(self, "right_signature", _require_digest(self.right_signature, "right signature"))
        elif self.right_signature is not None:
            raise ValueError(f"{self.kind.value} relation must not have a right signature")
        if not isinstance(self.trust_tier, TrustTier):
            try:
                object.__setattr__(self, "trust_tier", TrustTier(self.trust_tier))
            except (TypeError, ValueError) as error:
                raise ValueError("unknown trust tier") from error
        if self.trust_tier == TrustTier.MECHANICAL:
            raise ValueError("mechanical relations are built in and cannot be asserted by a record")
        object.__setattr__(self, "domain_digest", _require_digest(self.domain_digest, "domain digest"))
        object.__setattr__(self, "evidence_digest", _require_digest(self.evidence_digest, "evidence digest"))
        for label in ("checked_cases", "applicable_cases"):
            value = getattr(self, label)
            if isinstance(value, bool) or not isinstance(value, Integral) or int(value) < 0:
                raise ValueError(f"{label} must be a nonnegative integer")
            object.__setattr__(self, label, int(value))
        if self.checked_cases <= 0 or self.applicable_cases <= 0:
            raise ValueError("a relation certificate requires checked and applicable cases")
        if self.applicable_cases > self.checked_cases:
            raise ValueError("applicable cases cannot exceed checked cases")
        if isinstance(self.schema_version, bool) or self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")

    def to_record(self) -> dict[str, object]:
        return {
            "applicable_cases": self.applicable_cases,
            "checked_cases": self.checked_cases,
            "domain_digest": self.domain_digest,
            "evidence_digest": self.evidence_digest,
            "kind": self.kind.value,
            "left_signature": self.left_signature,
            "right_signature": self.right_signature,
            "schema_version": self.schema_version,
            "trust_tier": self.trust_tier.value,
        }

    @classmethod
    def from_record(cls, record: object) -> "RelationCertificate":
        body = _exact_fields(
            record,
            {
                "applicable_cases", "checked_cases", "domain_digest", "evidence_digest",
                "kind", "left_signature", "right_signature", "schema_version", "trust_tier",
            },
            "relation certificate record",
        )
        return cls(
            kind=body["kind"],  # type: ignore[arg-type]
            left_signature=body["left_signature"],  # type: ignore[arg-type]
            right_signature=body["right_signature"],  # type: ignore[arg-type]
            trust_tier=body["trust_tier"],  # type: ignore[arg-type]
            domain_digest=body["domain_digest"],  # type: ignore[arg-type]
            evidence_digest=body["evidence_digest"],  # type: ignore[arg-type]
            checked_cases=body["checked_cases"],  # type: ignore[arg-type]
            applicable_cases=body["applicable_cases"],  # type: ignore[arg-type]
            schema_version=body["schema_version"],  # type: ignore[arg-type]
        )

    @property
    def certificate_id(self) -> str:
        return sha256_record(self.to_record())

    def actionable(self, *, domain_digest: str | None) -> bool:
        return (
            self.trust_tier == TrustTier.FINITE_EXHAUSTIVE
            and domain_digest is not None
            and self.domain_digest == domain_digest
        )


@dataclass(frozen=True, slots=True)
class RelationRegistry:
    certificates: tuple[RelationCertificate, ...] = ()

    def __post_init__(self) -> None:
        if isinstance(self.certificates, (str, bytes)) or not isinstance(self.certificates, Sequence):
            raise TypeError("certificates must be a sequence")
        if any(not isinstance(item, RelationCertificate) for item in self.certificates):
            raise TypeError("registry entries must be RelationCertificate values")
        by_id = {item.certificate_id: item for item in self.certificates}
        if len(by_id) != len(self.certificates):
            raise ValueError("relation certificates must be unique")
        object.__setattr__(self, "certificates", tuple(by_id[key] for key in sorted(by_id)))

    def with_certificate(self, certificate: RelationCertificate) -> "RelationRegistry":
        if not isinstance(certificate, RelationCertificate):
            raise TypeError("certificate must be a RelationCertificate")
        return RelationRegistry(self.certificates + (certificate,))

    def actionable(
        self,
        *,
        domain_digest: str | None,
        allow_finite_exhaustive: bool,
    ) -> tuple[RelationCertificate, ...]:
        if not allow_finite_exhaustive:
            return ()
        if domain_digest is None:
            raise UntrustedRelationError(
                "finite exhaustive rewriting requires the exact closed-domain digest"
            )
        digest = _require_digest(domain_digest, "domain digest")
        return tuple(
            certificate
            for certificate in self.certificates
            if certificate.actionable(domain_digest=digest)
            and certificate.certificate_id in _LOCALLY_VERIFIED_CERTIFICATE_IDS
        )

    def to_record(self) -> dict[str, object]:
        body = {
            "certificates": [item.to_record() for item in self.certificates],
            "schema_version": SCHEMA_VERSION,
        }
        return {**body, "content_hash": sha256_record(body)}

    @classmethod
    def from_record(cls, record: object) -> "RelationRegistry":
        body = _exact_fields(
            record,
            {"certificates", "content_hash", "schema_version"},
            "relation registry record",
        )
        expected_hash = _require_digest(body["content_hash"], "registry content hash")
        hash_body = {"certificates": body["certificates"], "schema_version": body["schema_version"]}
        if expected_hash != sha256_record(hash_body):
            raise ValueError("relation registry content hash does not match its contents")
        if isinstance(body["schema_version"], bool) or body["schema_version"] != SCHEMA_VERSION:
            raise ValueError(f"schema_version must equal {SCHEMA_VERSION}")
        records = body["certificates"]
        if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
            raise TypeError("registry certificates must be a sequence")
        return cls(tuple(RelationCertificate.from_record(item) for item in records))


def finite_domain_digest(states: Iterable[object]) -> str:
    """Hash a finite state set after exact canonical deduplication."""

    records = sorted({canonical_json(state) for state in states})
    if not records:
        raise ValueError("finite domain must contain at least one state")
    return sha256_record({"canonical_states": records, "closed": True})


def certificate_is_locally_verified(certificate: RelationCertificate) -> bool:
    if not isinstance(certificate, RelationCertificate):
        raise TypeError("certificate must be a RelationCertificate")
    return certificate.certificate_id in _LOCALLY_VERIFIED_CERTIFICATE_IDS


def _attempt_word(
    executor: StateExecutor,
    atoms: Sequence[ActionAtom],
    state: object,
) -> tuple[bool, object]:
    current = state
    for atom in atoms:
        try:
            # Preserve the executor's exact runtime type between actions.  Only
            # the terminal observation is canonicalized for comparison/hash.
            current = executor(atom, current)
        except Exception as error:
            return False, {"error": type(error).__name__}
    return True, canonical_value(current)


def certify_finite_relation(
    kind: RelationKind | str,
    left: ActionAtom,
    states: Iterable[object],
    executor: StateExecutor,
    *,
    right: ActionAtom | None = None,
    closed_domain: bool = False,
) -> RelationCertificate:
    """Exhaustively test one relation on an explicitly supplied finite domain.

    ``closed_domain=False`` records only ``OBSERVED`` evidence and therefore
    cannot authorize normalization.  The verifier compares applicability as
    well as outputs, which is essential for partial actions.
    """

    try:
        relation = kind if isinstance(kind, RelationKind) else RelationKind(kind)
    except (TypeError, ValueError) as error:
        raise ValueError("unknown relation kind") from error
    if not isinstance(left, ActionAtom):
        raise TypeError("left must be an ActionAtom")
    if relation in {RelationKind.INVERSE, RelationKind.COMMUTES}:
        if not isinstance(right, ActionAtom):
            raise TypeError(f"{relation.value} certification requires a right atom")
    elif right is not None:
        raise ValueError(f"{relation.value} certification does not accept a right atom")
    if not callable(executor):
        raise TypeError("executor must be callable")
    if relation in {RelationKind.IDENTITY, RelationKind.IDEMPOTENT}:
        if left.input_type != left.output_type:
            raise AlgebraTypeError(f"{relation.value} requires an endomorphism")
    elif relation == RelationKind.INVERSE:
        assert right is not None
        if left.input_type != right.output_type or left.output_type != right.input_type:
            raise AlgebraTypeError("inverse actions must have opposite boundary types")
    else:
        assert relation == RelationKind.COMMUTES and right is not None
        if not (
            left.input_type == left.output_type == right.input_type == right.output_type
        ):
            raise AlgebraTypeError("commuting actions must be endomorphisms of one type")

    # Deduplicate by canonical identity while preserving each representative's
    # runtime type for the supplied executor.
    canonical_states = {canonical_json(state): state for state in states}
    if not canonical_states:
        raise ValueError("relation certification requires at least one state")
    ordered_states = tuple(canonical_states[key] for key in sorted(canonical_states))
    domain = finite_domain_digest(ordered_states)
    if closed_domain:
        relevant_atoms = (left,) if right is None else (left, right)
        domain_keys = set(canonical_states)
        for state in ordered_states:
            for atom in relevant_atoms:
                try:
                    successor = executor(atom, state)
                except Exception:
                    # A partial action may be disabled on a domain member.
                    continue
                if canonical_json(successor) not in domain_keys:
                    raise AlgebraError(
                        "finite exhaustive domain is not closed under a certified action"
                    )
    rows: list[dict[str, object]] = []
    applicable_cases = 0
    for state in ordered_states:
        if relation == RelationKind.IDENTITY:
            actual = _attempt_word(executor, (left,), state)
            expected = (True, canonical_value(state))
        elif relation == RelationKind.INVERSE:
            assert right is not None
            forward = _attempt_word(executor, (left, right), state)
            backward = _attempt_word(executor, (right, left), state)
            expected = (True, canonical_value(state))
            if forward != expected or backward != expected:
                raise AlgebraError("inverse relation failed exact finite verification")
            actual = forward
        elif relation == RelationKind.IDEMPOTENT:
            actual = _attempt_word(executor, (left, left), state)
            expected = _attempt_word(executor, (left,), state)
        else:
            assert relation == RelationKind.COMMUTES and right is not None
            actual = _attempt_word(executor, (left, right), state)
            expected = _attempt_word(executor, (right, left), state)
        if actual != expected:
            raise AlgebraError(
                f"{relation.value} relation failed exact finite verification"
            )
        if actual[0]:
            applicable_cases += 1
        rows.append(
            {
                "actual": actual,
                "expected": expected,
                "state_hash": sha256_record(state),
            }
        )
    if applicable_cases == 0:
        raise AlgebraError("relation has no applicable case in the supplied domain")
    evidence = sha256_record(
        {
            "domain": domain,
            "kind": relation.value,
            "left": left.signature,
            "right": right.signature if right is not None else None,
            "rows": rows,
        }
    )
    certificate = RelationCertificate(
        kind=relation,
        left_signature=left.signature,
        right_signature=right.signature if right is not None else None,
        trust_tier=(TrustTier.FINITE_EXHAUSTIVE if closed_domain else TrustTier.OBSERVED),
        domain_digest=domain,
        evidence_digest=evidence,
        checked_cases=len(ordered_states),
        applicable_cases=applicable_cases,
    )
    _LOCALLY_VERIFIED_CERTIFICATE_IDS.add(certificate.certificate_id)
    return certificate


def replay_verify_certificate(
    certificate: RelationCertificate,
    left: ActionAtom,
    states: Iterable[object],
    executor: StateExecutor,
    *,
    right: ActionAtom | None = None,
) -> RelationCertificate:
    """Re-establish trust in a decoded finite certificate by exact replay."""

    if not isinstance(certificate, RelationCertificate):
        raise TypeError("certificate must be a RelationCertificate")
    if certificate.trust_tier != TrustTier.FINITE_EXHAUSTIVE:
        raise UntrustedRelationError("only finite exhaustive certificates can be replay-authorized")
    replayed = certify_finite_relation(
        certificate.kind,
        left,
        states,
        executor,
        right=right,
        closed_domain=True,
    )
    if replayed.certificate_id != certificate.certificate_id:
        _LOCALLY_VERIFIED_CERTIFICATE_IDS.discard(replayed.certificate_id)
        _LOCALLY_VERIFIED_CERTIFICATE_IDS.discard(certificate.certificate_id)
        raise UntrustedRelationError("certificate replay does not match the persisted record")
    return replayed


@dataclass(frozen=True, slots=True)
class RewriteStep:
    rule: str
    trust_tier: TrustTier
    before: tuple[str, ...]
    after: tuple[str, ...]
    certificate_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule", _require_name(self.rule, "rewrite rule"))
        if not isinstance(self.trust_tier, TrustTier):
            raise TypeError("rewrite trust tier must be a TrustTier")
        if not self.before:
            raise ValueError("rewrite step must consume at least one atom")
        for digest in self.before + self.after:
            _require_digest(digest, "atom signature")
        if self.certificate_id:
            object.__setattr__(self, "certificate_id", _require_digest(self.certificate_id, "certificate ID"))
        elif self.trust_tier != TrustTier.MECHANICAL:
            raise ValueError("non-mechanical rewrites require a certificate ID")

    def to_record(self) -> dict[str, object]:
        return {
            "after": list(self.after),
            "before": list(self.before),
            "certificate_id": self.certificate_id,
            "rule": self.rule,
            "trust_tier": self.trust_tier.value,
        }


@dataclass(frozen=True, slots=True)
class NormalizationReceipt:
    original: ProgramWord
    normalized: ProgramWord
    steps: tuple[RewriteStep, ...]
    required_domain_digest: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.original, ProgramWord) or not isinstance(self.normalized, ProgramWord):
            raise TypeError("normalization endpoints must be ProgramWord values")
        if self.original.input_type != self.normalized.input_type or self.original.output_type != self.normalized.output_type:
            raise AlgebraTypeError("normalization changed the program's boundary type")
        if any(not isinstance(step, RewriteStep) for step in self.steps):
            raise TypeError("normalization steps must be RewriteStep values")
        if self.required_domain_digest is not None:
            object.__setattr__(
                self,
                "required_domain_digest",
                _require_digest(self.required_domain_digest, "required domain digest"),
            )

    @property
    def used_scoped_relation(self) -> bool:
        return any(step.trust_tier == TrustTier.FINITE_EXHAUSTIVE for step in self.steps)

    def to_record(self) -> dict[str, object]:
        body = {
            "normalized_hash": self.normalized.content_hash,
            "original_hash": self.original.content_hash,
            "required_domain_digest": self.required_domain_digest,
            "schema_version": SCHEMA_VERSION,
            "steps": [step.to_record() for step in self.steps],
        }
        return {**body, "content_hash": sha256_record(body)}


def _same_boundary_replacement(
    consumed: Sequence[ActionAtom], replacement: Sequence[ActionAtom]
) -> bool:
    if not consumed:
        return False
    before_input, before_output = consumed[0].input_type, consumed[-1].output_type
    if not replacement:
        return before_input == before_output
    return replacement[0].input_type == before_input and replacement[-1].output_type == before_output


def _builtin_pair_reduction(
    left: ActionAtom, right: ActionAtom
) -> tuple[tuple[ActionAtom, ...], str] | None:
    if left.output_type != right.input_type:
        return None
    left_d4, right_d4 = _d4_parameter(left), _d4_parameter(right)
    if left_d4 is not None and right_d4 is not None and left.input_type == right.output_type:
        result = compose_d4(left_d4, right_d4)
        replacement = () if result == "id" else (d4_atom(result, value_type=left.input_type),)
        return replacement, "d4_group_composition"

    left_translation = _translation_parameter(left)
    right_translation = _translation_parameter(right)
    if (
        left_translation is not None
        and right_translation is not None
        and left.input_type == right.output_type
    ):
        row = left_translation[0] + right_translation[0]
        column = left_translation[1] + right_translation[1]
        replacement = (
            ()
            if (row, column) == (0, 0)
            else (coordinate_translation_atom(row, column, value_type=left.input_type),)
        )
        return replacement, "translation_group_composition"

    for name, factory in (
        ("palette_bijection", palette_bijection_atom),
        ("object_renaming", object_renaming_atom),
    ):
        left_mapping = _mapping_parameter(left, name)
        right_mapping = _mapping_parameter(right, name)
        if left_mapping is None or right_mapping is None or left.input_type != right.output_type:
            continue
        composed = _compose_bijections(left_mapping, right_mapping)
        if composed is None:
            return None
        # Preserve a partial identity as an explicit guard.  Total palettes may
        # disappear; object-label universes are open, so their guards remain.
        if (
            name == "palette_bijection"
            and {source for source, _ in composed} == set(range(10))
            and all(source == target for source, target in composed)
        ):
            replacement = ()
        else:
            replacement = (factory(composed, value_type=left.input_type),)
        return replacement, f"{name}_composition"
    return None


def _certificate_match(
    certificate: RelationCertificate,
    left: ActionAtom,
    right: ActionAtom | None = None,
) -> bool:
    if certificate.left_signature != left.signature:
        return False
    if certificate.kind in {RelationKind.IDENTITY, RelationKind.IDEMPOTENT}:
        return right is None
    return right is not None and certificate.right_signature == right.signature


def normalize_program_word(
    word: ProgramWord | Sequence[ActionAtom],
    *,
    registry: RelationRegistry | None = None,
    domain_digest: str | None = None,
    allow_finite_exhaustive: bool = False,
    max_steps: int = MAX_NORMALIZATION_STEPS,
    empty_type: str = "grid",
) -> NormalizationReceipt:
    """Return a canonical word and an auditable sequence of exact rewrites."""

    original = word if isinstance(word, ProgramWord) else ProgramWord(tuple(word), empty_type)
    working_empty_type = (
        original.input_type
        if original.input_type == original.output_type
        else original.empty_type
    )
    if isinstance(max_steps, bool) or not isinstance(max_steps, Integral) or int(max_steps) <= 0:
        raise ValueError("max_steps must be a positive integer")
    registry = registry or RelationRegistry()
    if not isinstance(registry, RelationRegistry):
        raise TypeError("registry must be a RelationRegistry")
    certificates = registry.actionable(
        domain_digest=domain_digest,
        allow_finite_exhaustive=allow_finite_exhaustive,
    )
    required_domain = (
        _require_digest(domain_digest, "domain digest")
        if allow_finite_exhaustive and domain_digest is not None
        else None
    )

    atoms = list(original.atoms)
    steps: list[RewriteStep] = []

    def apply(index: int, width: int, replacement: Sequence[ActionAtom], rule: str, tier: TrustTier, certificate_id: str = "") -> None:
        nonlocal atoms
        consumed = tuple(atoms[index : index + width])
        replacement_tuple = tuple(replacement)
        if not _same_boundary_replacement(consumed, replacement_tuple):
            raise AlgebraTypeError(f"rewrite {rule!r} changes its boundary type")
        before = tuple(atom.signature for atom in consumed)
        after = tuple(atom.signature for atom in replacement_tuple)
        atoms[index : index + width] = replacement_tuple
        # Revalidate the entire short word at the trust boundary.
        ProgramWord(tuple(atoms), working_empty_type)
        steps.append(RewriteStep(rule, tier, before, after, certificate_id))
        if len(steps) > int(max_steps):
            raise NormalizationLimitError("program-word normalization exceeded its step budget")

    while True:
        changed = False

        # Group/bijection composition strictly decreases word length.
        for index in range(len(atoms) - 1):
            reduction = _builtin_pair_reduction(atoms[index], atoms[index + 1])
            if reduction is not None:
                replacement, rule = reduction
                apply(index, 2, replacement, rule, TrustTier.MECHANICAL)
                changed = True
                break
        if changed:
            continue

        # Delete only globally total mechanical identities.
        for index, atom in enumerate(atoms):
            if mechanical_identity(atom):
                apply(index, 1, (), "mechanical_identity", TrustTier.MECHANICAL)
                changed = True
                break
        if changed:
            continue

        # Scoped finite relations.  Their certificate domain describes the
        # program's *input* states, not arbitrary states reached by a prefix.
        # Without a separate prefix-reachability certificate, applying one at
        # a later index would be unsound: an earlier atom may leave the finite
        # domain on which the relation was proved.  Consequently scoped rules
        # are considered only at index zero.  Length-decreasing rules run
        # before swaps.
        for certificate in certificates:
            if certificate.kind == RelationKind.IDENTITY:
                if atoms and _certificate_match(certificate, atoms[0]):
                    apply(0, 1, (), "certified_identity", certificate.trust_tier, certificate.certificate_id)
                    changed = True
            elif certificate.kind == RelationKind.IDEMPOTENT:
                if (
                    len(atoms) >= 2
                    and atoms[0].signature == atoms[1].signature
                    and _certificate_match(certificate, atoms[0])
                ):
                    apply(0, 2, (atoms[0],), "certified_idempotence", certificate.trust_tier, certificate.certificate_id)
                    changed = True
            elif certificate.kind == RelationKind.INVERSE:
                if len(atoms) >= 2 and (
                    _certificate_match(certificate, atoms[0], atoms[1])
                    or _certificate_match(certificate, atoms[1], atoms[0])
                ):
                    apply(0, 2, (), "certified_inverse", certificate.trust_tier, certificate.certificate_id)
                    changed = True
            if changed:
                break
        if changed:
            continue

        # Mechanical commutation and certified commutation are oriented by the
        # canonical atom key, so each step strictly decreases lexicographic order.
        for index in range(len(atoms) - 1):
            left, right = atoms[index], atoms[index + 1]
            if left.canonical_key <= right.canonical_key:
                continue
            if mechanical_commutes(left, right):
                apply(index, 2, (right, left), "mechanical_commutation", TrustTier.MECHANICAL)
                changed = True
                break
            certificate = (
                next(
                    (
                        item
                        for item in certificates
                        if item.kind == RelationKind.COMMUTES
                        and (
                            _certificate_match(item, left, right)
                            or _certificate_match(item, right, left)
                        )
                    ),
                    None,
                )
                if index == 0
                else None
            )
            if certificate is not None:
                apply(index, 2, (right, left), "certified_commutation", certificate.trust_tier, certificate.certificate_id)
                changed = True
                break
        if not changed:
            break

    normalized = ProgramWord(tuple(atoms), working_empty_type)
    # A domain digest is a requirement only if a scoped rule was actually used.
    if not any(step.trust_tier == TrustTier.FINITE_EXHAUSTIVE for step in steps):
        required_domain = None
    return NormalizationReceipt(original, normalized, tuple(steps), required_domain)


def program_word_behavior(
    word: ProgramWord | Sequence[ActionAtom],
    state: object,
    executor: StateExecutor,
    *,
    empty_type: str = "grid",
) -> object:
    """Execute a word through a caller-supplied exact atom interpreter."""

    program = word if isinstance(word, ProgramWord) else ProgramWord(tuple(word), empty_type)
    if not callable(executor):
        raise TypeError("executor must be callable")
    current = state
    for atom in program.atoms:
        current = executor(atom, current)
    return current


def check_normalization_metamorphisms(
    receipt: NormalizationReceipt,
    states: Iterable[object],
    executor: StateExecutor,
    *,
    domain_digest: str | None = None,
) -> dict[str, object]:
    """Verify applicability and output equality of a normalization receipt."""

    if not isinstance(receipt, NormalizationReceipt):
        raise TypeError("receipt must be a NormalizationReceipt")
    if receipt.required_domain_digest is not None:
        if domain_digest is None or _require_digest(domain_digest, "domain digest") != receipt.required_domain_digest:
            raise UntrustedRelationError("normalization receipt is scoped to another finite domain")
    values = tuple(states)
    if not values:
        raise ValueError("normalization metamorphisms require at least one state")
    if (
        receipt.required_domain_digest is not None
        and finite_domain_digest(values) != receipt.required_domain_digest
    ):
        raise UntrustedRelationError(
            "supplied states do not equal the receipt's certified finite domain"
        )
    rows: list[dict[str, object]] = []
    passed = True
    for state in values:
        original = _attempt_word(executor, receipt.original.atoms, state)
        normalized = _attempt_word(executor, receipt.normalized.atoms, state)
        equal = original == normalized
        passed = passed and equal
        rows.append(
            {
                "equal": equal,
                "normalized": normalized,
                "original": original,
                "state_hash": sha256_record(state),
            }
        )
    body = {
        "normalized_hash": receipt.normalized.content_hash,
        "original_hash": receipt.original.content_hash,
        "passed": passed,
        "rows": rows,
    }
    return {**body, "content_hash": sha256_record(body)}


def d4_relation_table() -> dict[str, object]:
    """Return the exact built-in D4 identity/inverse/commutation ledger."""

    body = {
        "commuting_pairs": [
            [left, right]
            for left, right in itertools.combinations_with_replacement(D4_NAMES, 2)
            if compose_d4(left, right) == compose_d4(right, left)
        ],
        "identity": "id",
        "inverses": {name: inverse_d4(name) for name in D4_NAMES},
        "schema_version": SCHEMA_VERSION,
        "trust_tier": TrustTier.MECHANICAL.value,
    }
    return {**body, "content_hash": sha256_record(body)}


__all__ = [
    "ActionAtom",
    "AlgebraError",
    "AlgebraTypeError",
    "MAX_NORMALIZATION_STEPS",
    "NormalizationLimitError",
    "NormalizationReceipt",
    "ProgramWord",
    "RelationCertificate",
    "RelationKind",
    "RelationRegistry",
    "RewriteStep",
    "TrustTier",
    "UntrustedRelationError",
    "certify_finite_relation",
    "certificate_is_locally_verified",
    "check_normalization_metamorphisms",
    "coordinate_translation_atom",
    "d4_atom",
    "d4_relation_table",
    "finite_domain_digest",
    "mechanical_commutes",
    "mechanical_idempotent",
    "mechanical_identity",
    "mechanical_inverse",
    "normalize_program_word",
    "object_renaming_atom",
    "palette_bijection_atom",
    "program_word_behavior",
    "replay_verify_certificate",
]
