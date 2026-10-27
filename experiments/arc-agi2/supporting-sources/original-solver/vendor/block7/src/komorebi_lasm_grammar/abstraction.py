"""Typed anti-unification and scope selection for persistent grammar macros."""
from __future__ import annotations

import json
from collections import defaultdict
from typing import Any, Iterable, Mapping, Sequence

from komorebi_lasm_compiler.model import canonical_json, canonical_value, sha256_record

from .model import (
    CompressionCertificate,
    HoleSpec,
    MacroEvidence,
    MacroScope,
    MacroStatus,
    MacroTemplate,
)


# Scope selection is a language-level policy, not a corpus-learned task-ID table.
# Most families express one stable semantic mechanism while their parameters bind
# roles from the current demonstrations.  Families with known heterogeneous control
# modes are partitioned at a narrower semantic control level.
_CONTROL_FIELDS: dict[str, tuple[str, ...]] = {
    "block_reduce": ("mode",),
    "phase_chain_recolor": ("direction", "period", "residues"),
}


def infer_hole_type(path: Sequence[str], values: Sequence[Any]) -> str:
    """Infer a conservative semantic type for an anti-unification hole."""
    key = path[-1].lower() if path else "value"
    joined = ".".join(part.lower() for part in path)
    if any(token in joined for token in ("color", "recolor", "sequence", "palette", "fill_role", "background_role")):
        return "color_role"
    if any(token in joined for token in ("direction", "axis", "orientation", "toward", "side")):
        return "direction"
    if any(token in joined for token in ("pattern", "panelization", "layout", "spec", "operation", "base")):
        return "layout"
    if any(token in joined for token in ("mask", "support", "selection", "policy", "key")):
        return "selector"
    non_null = [value for value in values if value is not None]
    if non_null and all(isinstance(value, bool) for value in non_null):
        return "bool"
    if non_null and all(isinstance(value, int) and not isinstance(value, bool) for value in non_null):
        return "integer"
    if non_null and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in non_null):
        return "scalar"
    if non_null and all(isinstance(value, str) for value in non_null):
        return "symbol"
    if non_null and all(isinstance(value, (list, tuple)) for value in non_null):
        return "sequence"
    if non_null and all(isinstance(value, Mapping) for value in non_null):
        return "record"
    return "value"


def abstraction_descriptor(family: str, parameters: Mapping[str, Any]) -> tuple[MacroScope, dict[str, Any], str]:
    """Return the predetermined semantic abstraction key for one program."""
    controls = {
        field: canonical_value(parameters.get(field))
        for field in _CONTROL_FIELDS.get(family, ())
    }
    scope = MacroScope.CONTROL if controls else MacroScope.FAMILY
    payload = {
        "scope": scope.value,
        "family": str(family),
        "controls": controls,
    }
    return scope, controls, sha256_record(payload)


def abstraction_key(family: str, parameters: Mapping[str, Any]) -> str:
    scope, controls, _ = abstraction_descriptor(family, parameters)
    return canonical_json({"scope": scope.value, "family": family, "controls": controls})


def _anti_unify(values: Sequence[Any], path: tuple[str, ...], holes: list[HoleSpec]) -> Any:
    if not values:
        raise ValueError("anti-unification requires values")
    canonical = [canonical_value(value) for value in values]
    first = canonical[0]
    if all(value == first for value in canonical[1:]):
        return first

    if all(isinstance(value, Mapping) for value in canonical):
        keys = set(canonical[0])
        if all(set(value) == keys for value in canonical[1:]):
            return {
                str(key): _anti_unify([value[key] for value in canonical], path + (str(key),), holes)
                for key in sorted(keys, key=str)
            }

    if all(isinstance(value, list) for value in canonical):
        lengths = {len(value) for value in canonical}
        if len(lengths) == 1:
            length = next(iter(lengths))
            return [
                _anti_unify([value[index] for value in canonical], path + (str(index),), holes)
                for index in range(length)
            ]

    name = f"h{len(holes)}"
    value_type = infer_hole_type(path, canonical)
    holes.append(HoleSpec(name=name, path=path, value_type=value_type, optional=any(value is None for value in canonical)))
    return {"$hole": name, "type": value_type}


def anti_unify_parameters(parameter_records: Sequence[Mapping[str, Any]]) -> tuple[Any, tuple[HoleSpec, ...]]:
    """Anti-unify parameter dictionaries without retaining observed values."""
    if not parameter_records:
        return {}, ()
    holes: list[HoleSpec] = []
    template = _anti_unify(list(parameter_records), (), holes)
    return template, tuple(holes)


def _serialized_size(value: Any) -> int:
    return len(canonical_json(value).encode("utf-8"))


def compression_certificate(
    family: str,
    parameter_records: Sequence[Mapping[str, Any]],
    template: Any,
    holes: Sequence[HoleSpec],
) -> CompressionCertificate:
    """Compute a deterministic finite description-length proxy.

    The proxy is deliberately reported rather than used as an unconditional
    promotion requirement.  Sparse but strongly transferring mechanisms may be
    scientifically useful before they become a byte-level compression win.
    """
    raw_records = [{"family": family, "parameters": canonical_value(record)} for record in parameter_records]
    raw_bytes = sum(_serialized_size(record) for record in raw_records)
    macro_record = {
        "family": family,
        "parameter_template": canonical_value(template),
        "holes": [hole.to_record() for hole in holes],
    }
    macro_bytes = _serialized_size(macro_record)
    # Each source program needs only its hole bindings once a template exists.
    # Approximate bindings by the parameter payload minus common template syntax.
    instantiation_bytes = sum(max(1, _serialized_size(record) // 2) for record in parameter_records)
    return CompressionCertificate(
        raw_bytes=raw_bytes,
        macro_bytes=macro_bytes,
        instantiation_bytes=instantiation_bytes,
        compression_gain_bytes=raw_bytes - macro_bytes - instantiation_bytes,
        source_program_count=len(parameter_records),
    )


def build_macro_template(evidence: MacroEvidence, minimum_support: int = 2) -> MacroTemplate:
    template, holes = anti_unify_parameters(evidence.parameter_records)
    status: MacroStatus
    if evidence.wrong_count:
        status = MacroStatus.RETIRED
    elif evidence.exact_source_tasks >= minimum_support:
        status = MacroStatus.STABLE
    elif evidence.exact_source_tasks:
        status = MacroStatus.PROVISIONAL
    else:
        status = MacroStatus.CANDIDATE
    evidence_digest = sha256_record({
        "scope": evidence.scope.value,
        "family": evidence.family,
        "controls": canonical_value(evidence.controls),
        "activation_count": evidence.activation_count,
        "exact_count": evidence.exact_count,
        "wrong_count": evidence.wrong_count,
        "exact_source_tasks": evidence.exact_source_tasks,
        "source_signatures": sorted(evidence.source_signatures),
    })
    return MacroTemplate(
        family=evidence.family,
        scope=evidence.scope,
        controls=dict(evidence.controls),
        parameter_template=template,
        holes=holes,
        status=status,
        exact_source_tasks=evidence.exact_source_tasks,
        activation_count=evidence.activation_count,
        wrong_activation_count=evidence.wrong_count,
        minimum_support=minimum_support,
        compression=compression_certificate(evidence.family, evidence.parameter_records, template, holes),
        evidence_digest=evidence_digest,
        description=(
            "A role-bound grammar abstraction promoted from repeated exact program executions. "
            "Literal task identifiers and source output grids are excluded from the runtime bank."
        ),
    )


def exact_signature_key(signature: str) -> str:
    return sha256_record({"scope": MacroScope.EXACT.value, "signature": str(signature)})


__all__ = [
    "abstraction_descriptor",
    "abstraction_key",
    "anti_unify_parameters",
    "build_macro_template",
    "compression_certificate",
    "exact_signature_key",
    "infer_hole_type",
]
