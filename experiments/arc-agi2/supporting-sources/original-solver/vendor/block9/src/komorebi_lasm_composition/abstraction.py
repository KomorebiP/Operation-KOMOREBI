"""Typed, corpus-safe abstraction of contiguous composite-program subtrees.

This module deliberately has no dependency on the Block 9 runtime model.  It
accepts mappings as well as objects exposing ``semantic_record`` or
``to_record`` and therefore forms a small, stable boundary between mining and
execution.  Runtime templates contain structure and typed holes only.  Source
identifiers, training hashes, observed hole bindings, grids, and timing belong
to the audit side of :mod:`komorebi_lasm_composition.bank`.
"""
from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
import re
from dataclasses import dataclass, field, replace
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence


PathPart = str | int
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_HOLE_KEY = "$hole"
_GRID_TYPES = {"grid", "canvas", "mask", "value", "any"}
_PANEL_FAMILIES = {"panel_program", "role_panel_program"}
_CROP_FAMILIES = {"crop_bbox", "crop_to_bbox", "crop_bounding_box"}
_COLOR_ROLE_SYMBOLS = {
    "background", "foreground", "least_frequent", "most_frequent", "rarest",
    "dominant", "minimum_foreground", "maximum_foreground", "minfg", "maxfg",
    "separator", "marker", "key", "source", "target", "accent", "border",
    "most", "corner", "zero", "most_foreground", "rarest_foreground",
    "unique_foreground",
}
_DIRECTION_SYMBOLS = {
    "n", "ne", "e", "se", "s", "sw", "w", "nw", "north", "northeast",
    "east", "southeast", "south", "southwest", "west", "northwest", "up",
    "down", "left", "right", "horizontal", "vertical", "row", "column",
    "clockwise", "counterclockwise", "forward", "reverse",
    "h", "v", "both", "col", "diagonal", "main_diagonal", "anti_diagonal",
}
_LAYOUT_HEADS = {
    "equal", "uniform_separator", "legacy_lossless", "select", "pair", "overlay",
    "overlay_ab", "overlay_ba", "count_eq", "count_ge", "tile", "stack", "concat",
    "rows", "columns", "row", "column", "horizontal", "vertical", "forward",
    "reverse", "grid", "panel", "panels", "identity", "id", "fh", "fv", "r90",
    "r180", "r270",
}
_HOLE_TYPES = {
    "bool", "integer", "scalar", "symbol", "direction", "operator_family",
    "record", "sequence", "layout", "recolor_map", "color_role", "value",
}


class PromotionStatus(str, Enum):
    """Lifecycle state of one learned composite abstraction."""

    CANDIDATE = "candidate"
    PROVISIONAL = "provisional"
    STABLE = "stable"
    RETIRED = "retired"


def canonical_value(value: Any) -> Any:
    """Convert supported records to a deterministic JSON-compatible value."""
    if isinstance(value, Enum):
        return canonical_value(value.value)
    if dataclasses.is_dataclass(value):
        return canonical_value({
            item.name: getattr(value, item.name) for item in dataclasses.fields(value)
        })
    if isinstance(value, Mapping):
        return {
            str(key): canonical_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [canonical_value(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [canonical_value(item) for item in value]
        return sorted(items, key=canonical_json)
    if isinstance(value, bytes):
        return {"$bytes_hex": value.hex()}
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("non-finite floats are not canonical")
        return value
    if hasattr(value, "item") and callable(value.item):
        try:
            return canonical_value(value.item())
        except (TypeError, ValueError):
            pass
    raise TypeError(f"unsupported canonical value: {type(value).__name__}")


def _deep_freeze(value: Any) -> Any:
    """Recursively detach runtime structure from caller-owned containers."""
    canonical = canonical_value(value)
    if isinstance(canonical, Mapping):
        return MappingProxyType({
            str(key): _deep_freeze(item) for key, item in canonical.items()
        })
    if isinstance(canonical, list):
        return tuple(_deep_freeze(item) for item in canonical)
    return canonical


def canonical_json(value: Any) -> str:
    return json.dumps(
        canonical_value(value), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False,
    )


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _reject_unknown_fields(record: Mapping[str, Any], allowed: set[str], label: str) -> None:
    unknown = set(record) - allowed
    if unknown:
        raise ValueError(f"unknown {label} fields: {sorted(unknown)}")


def _require_fields(record: Mapping[str, Any], required: set[str], label: str) -> None:
    missing = required - set(record)
    if missing:
        raise ValueError(f"missing {label} fields: {sorted(missing)}")


def canonical_training_content_hash(training_content: Any) -> str:
    """Hash canonical training *content*, never a corpus or task alias.

    A sequence of already canonical pair hashes is sorted, wrapped, and hashed
    again so it cannot be confused with a task ID or with the hash of one pair.
    """
    value = canonical_value(training_content)
    if isinstance(value, Mapping):
        for key in ("train", "training", "examples"):
            if key in value:
                value = canonical_value(value[key])
                break
    if isinstance(value, list) and value and all(
        isinstance(item, str) and _HASH_RE.fullmatch(item) for item in value
    ):
        # Demonstration order is not semantic.  Sorting makes a reordered copy
        # of one task the same support source rather than apparent transfer.
        value = {"training_pair_hashes": sorted(value)}
    elif isinstance(value, list) and all(isinstance(item, Mapping) for item in value):
        examples = []
        for item in value:
            if "input" in item and "output" in item:
                examples.append({"input": item["input"], "output": item["output"]})
            else:
                examples.append(item)
        value = {"training_examples": sorted(examples, key=canonical_json)}
    return content_hash({"schema": "komorebi.training_content", "content": value})


def _read_record(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(canonical_value(value))
    for attribute in ("semantic_record", "to_record"):
        if hasattr(value, attribute):
            record = getattr(value, attribute)
            record = record() if callable(record) else record
            if isinstance(record, Mapping):
                result = dict(canonical_value(record))
                # ``semantic_record`` may intentionally omit parameters while
                # the object provides a parsed convenience property.
                if "parameters" not in result and hasattr(value, "parameters"):
                    result["parameters"] = canonical_value(getattr(value, "parameters"))
                for name in (
                    "namespace", "family", "macro_schema", "source_macro_id",
                    "input_type", "output_type", "cost", "status",
                ):
                    if name not in result and hasattr(value, name):
                        result[name] = canonical_value(getattr(value, name))
                return result
    if dataclasses.is_dataclass(value):
        return dict(canonical_value(dataclasses.asdict(value)))
    fields = (
        "namespace", "family", "macro_schema", "parameters_json", "parameters",
        "source_macro_id", "cost", "status", "input_type", "output_type",
    )
    record = {name: getattr(value, name) for name in fields if hasattr(value, name)}
    if record:
        return dict(canonical_value(record))
    raise TypeError("a leaf must be a mapping or expose semantic_record/to_record")


def _parameters(record: Mapping[str, Any]) -> Any:
    if "parameters" in record:
        return canonical_value(record["parameters"])
    raw = record.get("parameters_json", {})
    if isinstance(raw, str):
        try:
            return canonical_value(json.loads(raw))
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError("parameters_json is not canonical JSON") from exc
    return canonical_value(raw)


def _program_leaves(program: Any) -> tuple[Any, ...]:
    if hasattr(program, "leaves"):
        return tuple(getattr(program, "leaves"))
    if isinstance(program, Mapping):
        if "leaves" in program:
            return tuple(program["leaves"])
        if "program" in program:
            return _program_leaves(program["program"])
    if isinstance(program, Sequence) and not isinstance(program, (str, bytes, bytearray)):
        return tuple(program)
    raise TypeError("a composite program must expose an ordered leaves sequence")


def _normalize_type(value: Any, default: str = "grid") -> str:
    text = str(value if value is not None else default).strip().lower()
    return text or default


def _normalize_cost(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("leaf cost must be a positive integer")
    return int(value)


def _types_compose(left: str, right: str) -> bool:
    return left == right or left in {"any", "value"} or right in {"any", "value"}


def _safe_panel_pair(crop: Mapping[str, Any], panel: Mapping[str, Any]) -> bool:
    crop_family = str(crop.get("family", ""))
    panel_family = str(panel.get("family", ""))
    if crop_family not in _CROP_FAMILIES or panel_family not in _PANEL_FAMILIES:
        return False
    if not _types_compose(
        _normalize_type(crop.get("output_type")),
        _normalize_type(panel.get("input_type")),
    ):
        return False
    try:
        crop_parameters = _parameters(crop)
        panel_parameters = _parameters(panel)
    except (TypeError, ValueError):
        return False
    return isinstance(crop_parameters, Mapping) and isinstance(panel_parameters, Mapping)


def _parse_legacy_panel_spec(spec: Any) -> Any:
    """Losslessly normalize known legacy panel specifications when possible."""
    if not isinstance(spec, str):
        return canonical_value(spec)
    equal = re.fullmatch(r"equal:(\d+)x(\d+)", spec)
    if equal:
        return {"kind": "equal", "rows": int(equal.group(1)), "columns": int(equal.group(2))}
    separator = re.fullmatch(r"sep:(\d+):r(.*):c(.*)", spec)
    if separator:
        try:
            rows = ast.literal_eval(separator.group(2))
            columns = ast.literal_eval(separator.group(3))
        except (ValueError, SyntaxError):
            return {"kind": "legacy_lossless", "spec": spec}
        return {
            "kind": "uniform_separator",
            "separator_color": int(separator.group(1)),
            "row_runs": canonical_value(rows),
            "column_runs": canonical_value(columns),
        }
    return {"kind": "legacy_lossless", "spec": spec}


def _panel_payload(record: Mapping[str, Any]) -> dict[str, Any]:
    family = str(record["family"])
    parameters = dict(_parameters(record))
    if family == "panel_program":
        panelization = _parse_legacy_panel_spec(parameters.pop("spec", None))
    else:
        panelization = canonical_value(parameters.pop("panelization", None))
    # ``lowering_family`` makes this normalization injective.  A compiler can
    # always recover the exact source dialect; anti-unification may replace it
    # with a typed hole without retaining its observed alternatives.
    return {
        "lowering_family": family,
        "panelization": panelization,
        "operation": canonical_value(parameters.pop("operation", None)),
        "recolor": canonical_value(parameters.pop("recolor", [])),
        "extra_parameters": canonical_value(parameters),
    }


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, Mapping):
        return {str(key): _tuple_tree(item) for key, item in value.items()}
    return value


def _legacy_panel_spec(panelization: Any) -> str:
    if not isinstance(panelization, Mapping):
        raise ValueError("panel_program requires a mapped semantic panelization")
    kind = panelization.get("kind")
    if kind == "equal":
        rows = panelization.get("rows")
        columns = panelization.get("columns")
        if (
            isinstance(rows, bool) or not isinstance(rows, int) or rows < 1
            or isinstance(columns, bool) or not isinstance(columns, int) or columns < 1
        ):
            raise ValueError("equal panelization needs positive integer dimensions")
        return f"equal:{rows}x{columns}"
    if kind == "uniform_separator":
        color = panelization.get("separator_color")
        if isinstance(color, bool) or not isinstance(color, int) or not 0 <= color <= 9:
            raise ValueError("separator panelization needs a color in 0..9")
        rows = _tuple_tree(panelization.get("row_runs", ()))
        columns = _tuple_tree(panelization.get("column_runs", ()))
        if not isinstance(rows, tuple) or not isinstance(columns, tuple):
            raise ValueError("separator runs must be finite sequences")
        return f"sep:{color}:r{rows!r}:c{columns!r}"
    if kind == "legacy_lossless":
        spec = panelization.get("spec")
        if not isinstance(spec, str) or not spec:
            raise ValueError("lossless legacy panelization needs its specification")
        return spec
    raise ValueError("unsupported panel_program panelization")


def _lower_panel_payload(payload: Any) -> tuple[str, dict[str, Any]]:
    """Lower the reversible semantic bridge to an executable Block 6 leaf."""
    if not isinstance(payload, Mapping):
        raise TypeError("semantic panel payload must be a mapping")
    required = {
        "lowering_family", "panelization", "operation", "recolor", "extra_parameters",
    }
    if set(payload) != required:
        raise ValueError("semantic panel payload fields do not match its schema")
    family = payload["lowering_family"]
    if family not in _PANEL_FAMILIES:
        raise ValueError("semantic panel payload has an unknown lowering family")
    extras = payload["extra_parameters"]
    if not isinstance(extras, Mapping):
        raise TypeError("semantic panel extra parameters must be a mapping")
    parameters = dict(canonical_value(extras))
    if family == "panel_program":
        parameters["spec"] = _legacy_panel_spec(payload["panelization"])
    else:
        panelization = payload["panelization"]
        if not isinstance(panelization, (list, tuple)) or not panelization:
            raise ValueError("role_panel_program needs a role panelization sequence")
        parameters["panelization"] = canonical_value(panelization)
    parameters["operation"] = canonical_value(payload["operation"])
    parameters["recolor"] = canonical_value(payload["recolor"])
    return str(family), dict(canonical_value(parameters))


def normalize_leaf_record(
    leaf: Any,
    *,
    previous_leaf: Any | None = None,
) -> dict[str, Any]:
    """Return the task-independent semantic record for one leaf.

    ``crop_bbox -> panel_program`` and ``crop_bbox -> role_panel_program`` are
    represented by one reversible semantic panel-render leaf only when the
    pair is type-compatible and both parameter payloads parse as mappings.
    """
    record = _read_record(leaf)
    family = str(record.get("family", "")).strip()
    if not family:
        raise ValueError("leaf family must be nonempty")
    previous = _read_record(previous_leaf) if previous_leaf is not None else None
    panel_pair = previous is not None and _safe_panel_pair(previous, record)
    normalized = {
        "namespace": str(record.get("namespace", "primitive")),
        "family": "render_extracted_panels" if panel_pair else family,
        "macro_schema": (
            "semantic_panel_extraction" if panel_pair
            else str(record.get("macro_schema") or family)
        ),
        "parameters": _panel_payload(record) if panel_pair else _parameters(record),
        "source_macro_id": (
            None if record.get("source_macro_id") is None
            else str(record.get("source_macro_id"))
        ),
        "input_type": _normalize_type(record.get("input_type")),
        "output_type": _normalize_type(record.get("output_type")),
        "cost": _normalize_cost(record.get("cost", 1)),
        "status": str(record.get("status", "primitive")),
    }
    return dict(canonical_value(normalized))


def normalize_leaf_sequence(leaves: Sequence[Any]) -> tuple[dict[str, Any], ...]:
    result: list[dict[str, Any]] = []
    for index, leaf in enumerate(leaves):
        result.append(normalize_leaf_record(leaf, previous_leaf=leaves[index - 1] if index else None))
    return tuple(result)


def semantic_subtree_schema(leaves: Sequence[Any]) -> str:
    normalized = normalize_leaf_sequence(leaves)
    families = [str(item["family"]) for item in normalized]
    if len(families) >= 2 and families[0] in _CROP_FAMILIES and families[1] == "render_extracted_panels":
        suffix = families[2:]
        return "panel_extraction" + ("_then_" + "_then_".join(suffix) if suffix else "")
    return "compose__" + "__then__".join(
        re.sub(r"[^a-zA-Z0-9_]+", "_", family).strip("_") or "leaf"
        for family in families
    )


def _infer_hole_type(path: Sequence[PathPart], values: Sequence[Any]) -> str:
    joined = ".".join(str(part).lower() for part in path)
    non_null = [value for value in values if value is not None]
    if "recolor" in joined and non_null and all(isinstance(value, list) for value in non_null):
        return "recolor_map"
    if "lowering_family" in joined or "family" in joined or "schema" in joined:
        return "operator_family"
    if any(token in joined for token in ("color", "palette", "recolor", "fill")):
        return "color_role"
    if any(token in joined for token in ("axis", "direction", "orientation", "side")):
        return "direction"
    if any(token in joined for token in ("panel", "layout", "operation", "spec")):
        return "layout"
    if non_null and all(isinstance(value, bool) for value in non_null):
        return "bool"
    if non_null and all(isinstance(value, int) and not isinstance(value, bool) for value in non_null):
        return "integer"
    if non_null and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in non_null):
        return "scalar"
    if non_null and all(isinstance(value, str) for value in non_null):
        return "symbol"
    if non_null and all(isinstance(value, Mapping) for value in non_null):
        return "record"
    if non_null and all(isinstance(value, list) for value in non_null):
        return "sequence"
    return "value"


@dataclass(frozen=True)
class TypedHole:
    """A typed location in a macro body, without any observed binding value."""

    name: str
    value_type: str
    path: tuple[PathPart, ...]
    optional: bool = False
    equal_paths: tuple[tuple[PathPart, ...], ...] = ()
    schema_version: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.path, (str, bytes, bytearray, Mapping)):
            raise TypeError("hole path must be a finite coordinate sequence")
        if isinstance(self.equal_paths, (str, bytes, bytearray, Mapping)):
            raise TypeError("hole equality paths must be a finite sequence")
        if any(isinstance(path, (str, bytes, bytearray, Mapping)) for path in self.equal_paths):
            raise TypeError("each hole equality path must be a coordinate sequence")
        object.__setattr__(self, "path", tuple(self.path))
        object.__setattr__(self, "equal_paths", tuple(
            tuple(path) for path in self.equal_paths
        ))
        if not isinstance(self.name, str) or not self.name or self.name.strip() != self.name:
            raise ValueError("hole name must be a nonempty trimmed string")
        if not isinstance(self.value_type, str) or not self.value_type or self.value_type.strip() != self.value_type:
            raise ValueError("hole type must be a nonempty trimmed string")
        if self.value_type not in _HOLE_TYPES:
            raise ValueError(f"unknown typed-hole value type: {self.value_type}")
        if not self.path:
            raise ValueError("hole path must be nonempty")
        if any(
            isinstance(part, bool) or not isinstance(part, (str, int))
            for path in (self.path,) + self.equal_paths for part in path
        ):
            raise TypeError("hole paths may contain only strings and non-Boolean integers")
        paths = (self.path,) + self.equal_paths
        if len(paths) != len(set(paths)):
            raise ValueError("hole equality paths must be unique")
        if any(not path for path in paths):
            raise ValueError("hole equality paths must be nonempty")
        if not isinstance(self.optional, bool):
            raise TypeError("hole optional flag must be Boolean")
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int) or self.schema_version != 1:
            raise ValueError("unsupported typed-hole schema version")

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_typed_hole",
            "schema_version": 1,
            "name": self.name,
            "value_type": self.value_type,
            "path": list(self.path),
            "equal_paths": [list(path) for path in self.equal_paths],
            "optional": bool(self.optional),
        }

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "TypedHole":
        _reject_unknown_fields(record, {
            "schema", "schema_version", "name", "value_type", "path",
            "equal_paths", "optional",
        }, "typed-hole")
        _require_fields(record, {
            "schema", "schema_version", "name", "value_type", "path",
            "equal_paths", "optional",
        }, "typed-hole")
        if record.get("schema", "komorebi.lasm_typed_hole") != "komorebi.lasm_typed_hole":
            raise ValueError("not a typed-hole record")
        optional = record.get("optional", False)
        schema_version = record.get("schema_version", 1)
        if not isinstance(optional, bool):
            raise TypeError("typed-hole optional must be Boolean")
        if isinstance(schema_version, bool) or not isinstance(schema_version, int):
            raise TypeError("typed-hole schema_version must be an integer")
        return cls(
            name=record["name"],
            value_type=record["value_type"],
            path=tuple(record["path"]),
            optional=optional,
            equal_paths=tuple(tuple(path) for path in record.get("equal_paths", ())),
            schema_version=schema_version,
        )


@dataclass(frozen=True)
class LeafTemplate:
    """One typed leaf in an anti-unified contiguous composition."""

    namespace: str
    family: str
    macro_schema: str
    parameter_template: Any = field(default_factory=dict)
    holes: tuple[TypedHole, ...] = ()
    source_macro_id: str | None = None
    input_type: str = "grid"
    output_type: str = "grid"
    cost: int = 1
    status: str = "primitive"
    schema_version: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.holes, (str, bytes, bytearray, Mapping)):
            raise TypeError("leaf holes must be a finite sequence")
        object.__setattr__(self, "parameter_template", _deep_freeze(self.parameter_template))
        object.__setattr__(self, "holes", tuple(self.holes))
        for label, value in (
            ("namespace", self.namespace), ("family", self.family),
            ("macro_schema", self.macro_schema), ("input_type", self.input_type),
            ("output_type", self.output_type),
        ):
            if not isinstance(value, str) or not value or value.strip() != value:
                raise ValueError(f"leaf {label} must be nonempty and trimmed")
        if self.source_macro_id is not None and not isinstance(self.source_macro_id, str):
            raise TypeError("source_macro_id must be a string or None")
        if not all(isinstance(hole, TypedHole) for hole in self.holes):
            raise TypeError("leaf holes must be TypedHole records")
        names = [hole.name for hole in self.holes]
        if len(names) != len(set(names)):
            raise ValueError("leaf hole names must be unique")
        markers = set(_hole_markers(self.parameter_template))
        if markers != set(names):
            raise ValueError("leaf hole declarations do not match template markers")
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int) or self.schema_version != 1:
            raise ValueError("unsupported leaf-template schema version")
        if isinstance(self.cost, bool) or not isinstance(self.cost, int) or self.cost < 1:
            raise ValueError("leaf-template cost must be a positive integer")
        if self.status not in {"primitive", "candidate", "provisional", "stable"}:
            raise ValueError("leaf-template status is not executable")

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composite_leaf_template",
            "schema_version": 1,
            "namespace": self.namespace,
            "family": self.family,
            "macro_schema": self.macro_schema,
            "parameter_template": canonical_value(self.parameter_template),
            "holes": [hole.to_record() for hole in self.holes],
            "source_macro_id": self.source_macro_id,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "cost": int(self.cost),
            "status": self.status,
        }

    @property
    def leaf_id(self) -> str:
        return content_hash(self.identity_record)

    def to_record(self) -> dict[str, Any]:
        record = {**self.identity_record, "leaf_id": self.leaf_id}
        record["content_hash"] = content_hash(record)
        return record

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "LeafTemplate":
        _reject_unknown_fields(record, {
            "schema", "schema_version", "namespace", "family", "macro_schema",
            "parameter_template", "holes", "source_macro_id", "input_type",
            "output_type", "cost", "status", "leaf_id", "content_hash",
        }, "leaf-template")
        _require_fields(record, {
            "schema", "schema_version", "namespace", "family", "macro_schema",
            "parameter_template", "holes", "source_macro_id", "input_type",
            "output_type", "cost", "status",
        }, "leaf-template")
        if record.get("schema") != "komorebi.lasm_composite_leaf_template":
            raise ValueError("not a composite leaf-template record")
        result = cls(
            namespace=record["namespace"], family=record["family"],
            macro_schema=record["macro_schema"],
            parameter_template=canonical_value(record.get("parameter_template", {})),
            holes=tuple(TypedHole.from_record(item) for item in record.get("holes", ())),
            source_macro_id=record["source_macro_id"],
            input_type=record["input_type"],
            output_type=record["output_type"],
            cost=record.get("cost", 1),
            status=record["status"],
            schema_version=record.get("schema_version", 1),
        )
        if record.get("leaf_id") not in (None, result.leaf_id):
            raise ValueError("leaf ID mismatch")
        if "content_hash" in record:
            payload = {key: value for key, value in record.items() if key != "content_hash"}
            if str(record["content_hash"]) != content_hash(payload):
                raise ValueError("leaf content hash mismatch")
        return result

    def instantiate(self, bindings: Mapping[str, Any]) -> dict[str, Any]:
        parameters = _substitute(self.parameter_template, bindings, self.holes)
        family = self.family
        macro_schema = self.macro_schema
        source_macro_id = self.source_macro_id
        if family == "render_extracted_panels":
            family, parameters = _lower_panel_payload(parameters)
            macro_schema = family
            if source_macro_id is None:
                source_macro_id = content_hash({
                    "schema": "komorebi.lasm_semantic_panel_adapter",
                    "schema_version": 1,
                    "family": family,
                })
        return {
            "namespace": self.namespace,
            "family": family,
            "macro_schema": macro_schema,
            "parameters": parameters,
            "source_macro_id": source_macro_id,
            "input_type": self.input_type,
            "output_type": self.output_type,
            "cost": int(self.cost),
            "status": self.status,
        }


@dataclass(frozen=True)
class CompositeMacroTemplate:
    """A promoted, typed, genuinely multi-leaf contiguous subtree."""

    name: str
    semantic_schema: str
    leaves: tuple[LeafTemplate, ...]
    holes: tuple[TypedHole, ...]
    status: PromotionStatus = PromotionStatus.CANDIDATE
    support_count: int = 0
    wrong_activation_count: int = 0
    minimum_support: int = 2
    rank: int = 1
    dependencies: tuple[str, ...] = ()
    expanded_leaf_count: int = 0
    description: str = ""
    schema_version: int = 1

    def __post_init__(self) -> None:
        for label, value in (
            ("leaves", self.leaves), ("holes", self.holes),
            ("dependencies", self.dependencies),
        ):
            if isinstance(value, (str, bytes, bytearray, Mapping)):
                raise TypeError(f"composite {label} must be a finite sequence")
        object.__setattr__(self, "leaves", tuple(self.leaves))
        object.__setattr__(self, "holes", tuple(self.holes))
        object.__setattr__(self, "dependencies", tuple(self.dependencies))
        if not isinstance(self.name, str) or not self.name or self.name.strip() != self.name:
            raise ValueError("macro name must be nonempty and trimmed")
        if not isinstance(self.semantic_schema, str) or not self.semantic_schema or self.semantic_schema.strip() != self.semantic_schema:
            raise ValueError("semantic schema must be nonempty and trimmed")
        if not isinstance(self.description, str):
            raise TypeError("macro description must be a string")
        if not isinstance(self.status, PromotionStatus):
            raise TypeError("macro status must be a PromotionStatus")
        if len(self.leaves) < 2:
            raise ValueError("a composite abstraction must contain at least two leaves")
        if self.minimum_support != 2:
            raise ValueError("Block 9 uses the fixed stable-support threshold of two")
        for label, value in (
            ("support_count", self.support_count),
            ("wrong_activation_count", self.wrong_activation_count),
            ("minimum_support", self.minimum_support), ("rank", self.rank),
            ("expanded_leaf_count", self.expanded_leaf_count),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{label} must be an integer")
        if self.support_count < 0 or self.wrong_activation_count < 0:
            raise ValueError("evidence counts cannot be negative")
        if self.rank < 1:
            raise ValueError("composite rank must be positive")
        if any(not isinstance(dependency, str) for dependency in self.dependencies):
            raise TypeError("dependency IDs must be strings")
        if len(self.dependencies) != len(set(self.dependencies)):
            raise ValueError("dependency IDs must be unique")
        if not all(isinstance(leaf, LeafTemplate) for leaf in self.leaves):
            raise TypeError("composite leaves must be LeafTemplate records")
        if not all(isinstance(hole, TypedHole) for hole in self.holes):
            raise TypeError("composite holes must be TypedHole records")
        names = [hole.name for hole in self.holes]
        if len(names) != len(set(names)):
            raise ValueError("composite hole names must be unique")
        leaf_names = {hole.name for leaf in self.leaves for hole in leaf.holes}
        if leaf_names != set(names):
            raise ValueError("composite holes must equal the union of leaf holes")
        for left, right in zip(self.leaves, self.leaves[1:]):
            if not _types_compose(left.output_type, right.input_type):
                raise ValueError(
                    f"noncomposable leaf types: {left.output_type!r} -> {right.input_type!r}"
                )
        if self.status is PromotionStatus.STABLE:
            if self.support_count < 2:
                raise ValueError("stable composite lacks two distinct content sources")
            if self.wrong_activation_count:
                raise ValueError("stable composite has a wrong activation")
        if self.status is PromotionStatus.RETIRED and not self.wrong_activation_count:
            raise ValueError("retired composite must record a wrong activation")
        if self.expanded_leaf_count == 0:
            object.__setattr__(self, "expanded_leaf_count", len(self.leaves))
        if self.expanded_leaf_count < len(self.leaves):
            raise ValueError("expanded leaf count cannot be smaller than local leaf count")
        if isinstance(self.schema_version, bool) or not isinstance(self.schema_version, int) or self.schema_version != 1:
            raise ValueError("unsupported composite-template schema version")

    @property
    def input_type(self) -> str:
        return self.leaves[0].input_type

    @property
    def output_type(self) -> str:
        return self.leaves[-1].output_type

    @property
    def identity_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_composite_macro_template",
            "schema_version": 1,
            "name": self.name,
            "semantic_schema": self.semantic_schema,
            "leaves": [leaf.identity_record for leaf in self.leaves],
            "holes": [hole.to_record() for hole in self.holes],
            "rank": int(self.rank),
            "dependencies": list(self.dependencies),
            "expanded_leaf_count": int(self.expanded_leaf_count),
            "input_type": self.input_type,
            "output_type": self.output_type,
        }

    @property
    def macro_id(self) -> str:
        return content_hash(self.identity_record)

    def with_evidence(self, *, support_count: int, wrong_activation_count: int) -> "CompositeMacroTemplate":
        if (
            isinstance(support_count, bool) or not isinstance(support_count, int)
            or isinstance(wrong_activation_count, bool) or not isinstance(wrong_activation_count, int)
        ):
            raise TypeError("evidence counts must be integers")
        status = _status(support_count, wrong_activation_count, self.minimum_support)
        return replace(
            self, support_count=support_count,
            wrong_activation_count=wrong_activation_count, status=status,
        )

    def to_runtime_record(self) -> dict[str, Any]:
        record = {
            **self.identity_record,
            "macro_id": self.macro_id,
            "status": self.status.value,
            "support_count": int(self.support_count),
            "wrong_activation_count": int(self.wrong_activation_count),
            "minimum_support": 2,
            "description": self.description,
        }
        record["content_hash"] = content_hash(record)
        return record

    to_record = to_runtime_record

    @classmethod
    def from_runtime_record(cls, record: Mapping[str, Any]) -> "CompositeMacroTemplate":
        _reject_unknown_fields(record, {
            "schema", "schema_version", "name", "semantic_schema", "leaves",
            "holes", "rank", "dependencies", "expanded_leaf_count", "input_type",
            "output_type", "macro_id", "status", "support_count",
            "wrong_activation_count", "minimum_support", "description", "content_hash",
        }, "composite-macro")
        _require_fields(record, {
            "schema", "schema_version", "name", "semantic_schema", "leaves",
            "holes", "rank", "dependencies", "expanded_leaf_count", "input_type",
            "output_type", "macro_id", "status", "support_count",
            "wrong_activation_count", "minimum_support", "description", "content_hash",
        }, "composite-macro")
        if record.get("schema") != "komorebi.lasm_composite_macro_template":
            raise ValueError("not a composite macro-template record")
        raw_status = record["status"]
        if not isinstance(raw_status, str):
            raise TypeError("composite macro status must be a string")
        result = cls(
            name=record["name"], semantic_schema=record["semantic_schema"],
            leaves=tuple(LeafTemplate.from_record(item) for item in record["leaves"]),
            holes=tuple(TypedHole.from_record(item) for item in record.get("holes", ())),
            status=PromotionStatus(raw_status),
            support_count=record.get("support_count", 0),
            wrong_activation_count=record.get("wrong_activation_count", 0),
            minimum_support=record.get("minimum_support", 2),
            rank=record.get("rank", 1),
            dependencies=tuple(record["dependencies"]),
            expanded_leaf_count=record.get("expanded_leaf_count", 0),
            description=record["description"],
            schema_version=record.get("schema_version", 1),
        )
        if record.get("macro_id") not in (None, result.macro_id):
            raise ValueError("composite macro ID mismatch")
        if record.get("input_type", result.input_type) != result.input_type:
            raise ValueError("composite macro input type mismatch")
        if record.get("output_type", result.output_type) != result.output_type:
            raise ValueError("composite macro output type mismatch")
        if record["expanded_leaf_count"] != result.expanded_leaf_count:
            raise ValueError("composite macro expanded leaf count was noncanonical")
        if "content_hash" in record:
            payload = {key: value for key, value in record.items() if key != "content_hash"}
            if str(record["content_hash"]) != content_hash(payload):
                raise ValueError("composite macro content hash mismatch")
        return result


@dataclass(frozen=True)
class SubtreeOccurrence:
    """Audit-time occurrence; identifiers never enter a runtime template."""

    leaves: tuple[dict[str, Any], ...]
    training_content_hash: str
    correct: bool = True
    start: int = 0
    stop: int = 0
    audit_id: str | None = None
    program_id: str | None = None

    def __post_init__(self) -> None:
        if len(self.leaves) < 2:
            raise ValueError("subtree occurrence must contain at least two leaves")
        if not _HASH_RE.fullmatch(self.training_content_hash):
            raise ValueError("training content identity must be a lowercase SHA-256 hash")
        if not isinstance(self.correct, bool):
            raise TypeError("occurrence correctness must be Boolean")
        for label, value in (("start", self.start), ("stop", self.stop)):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise TypeError(f"occurrence {label} must be a nonnegative integer")
        if self.stop and self.stop - self.start != len(self.leaves):
            raise ValueError("occurrence interval does not match leaf count")

    @property
    def shape_key(self) -> str:
        return _shape_key(self.leaves)

    def to_audit_record(self) -> dict[str, Any]:
        return {
            "schema": "komorebi.lasm_subtree_occurrence_audit",
            "schema_version": 1,
            "shape_key": self.shape_key,
            "training_content_hash": self.training_content_hash,
            "correct": bool(self.correct),
            "start": int(self.start),
            "stop": int(self.stop or self.start + len(self.leaves)),
            "audit_id": self.audit_id,
            "program_id": self.program_id,
        }


def _hole_markers(value: Any) -> tuple[str, ...]:
    result: list[str] = []
    if isinstance(value, Mapping):
        if _HOLE_KEY in value:
            result.append(str(value[_HOLE_KEY]))
        else:
            for item in value.values():
                result.extend(_hole_markers(item))
    elif isinstance(value, (list, tuple)):
        for item in value:
            result.extend(_hole_markers(item))
    return tuple(result)


def _anti_unify(
    values: Sequence[Any],
    path: tuple[PathPart, ...],
    holes: list[TypedHole],
    equality_classes: dict[str, int],
) -> Any:
    values = [canonical_value(value) for value in values]
    first = values[0]
    if all(value == first for value in values[1:]):
        return first
    if all(isinstance(value, Mapping) for value in values):
        keys = set(values[0])
        if all(set(value) == keys for value in values[1:]):
            return {
                str(key): _anti_unify(
                    [value[key] for value in values], path + (str(key),), holes,
                    equality_classes,
                )
                for key in sorted(keys, key=str)
            }
    if all(isinstance(value, list) for value in values):
        lengths = {len(value) for value in values}
        if len(lengths) == 1:
            return [
                _anti_unify(
                    [value[index] for value in values], path + (index,), holes,
                    equality_classes,
                )
                for index in range(next(iter(lengths)))
            ]
    value_type = _infer_hole_type(path, values)
    optional = any(value is None for value in values)
    equality_key = canonical_json({
        "value_type": value_type, "optional": optional, "observations": values,
    })
    if equality_key in equality_classes:
        index = equality_classes[equality_key]
        prior = holes[index]
        holes[index] = replace(prior, equal_paths=prior.equal_paths + (path,))
        return {_HOLE_KEY: prior.name, "type": prior.value_type}
    name = f"h{len(holes)}"
    holes.append(TypedHole(
        name=name, value_type=value_type, path=path,
        optional=optional,
    ))
    equality_classes[equality_key] = len(holes) - 1
    return {_HOLE_KEY: name, "type": value_type}


def _shape_key(leaves: Sequence[Mapping[str, Any]]) -> str:
    return canonical_json({
        "length": len(leaves),
        "semantic_schema": semantic_subtree_schema(leaves),
        "leaves": [{
            "namespace": leaf.get("namespace", "primitive"),
            "family": leaf["family"],
            "macro_schema": leaf.get("macro_schema", leaf["family"]),
            "input_type": leaf.get("input_type", "grid"),
            "output_type": leaf.get("output_type", "grid"),
            "status": leaf.get("status", "primitive"),
        } for leaf in leaves],
    })


def _status(support: int, wrong: int, minimum_support: int = 2) -> PromotionStatus:
    if wrong:
        return PromotionStatus.RETIRED
    if support >= minimum_support:
        return PromotionStatus.STABLE
    if support:
        return PromotionStatus.PROVISIONAL
    return PromotionStatus.CANDIDATE


def extract_contiguous_subtrees(
    program: Any,
    *,
    training_content: Any | None = None,
    training_content_hash: str | None = None,
    correct: bool = True,
    minimum_leaves: int = 2,
    maximum_leaves: int | None = None,
    audit_id: str | None = None,
    program_id: str | None = None,
) -> tuple[SubtreeOccurrence, ...]:
    """Enumerate every contiguous multi-leaf window, not merely prefixes."""
    if isinstance(minimum_leaves, bool) or not isinstance(minimum_leaves, int):
        raise TypeError("minimum_leaves must be an integer")
    if maximum_leaves is not None and (
        isinstance(maximum_leaves, bool) or not isinstance(maximum_leaves, int)
    ):
        raise TypeError("maximum_leaves must be an integer or None")
    if not isinstance(correct, bool):
        raise TypeError("correct must be Boolean")
    if minimum_leaves < 2:
        raise ValueError("minimum_leaves must be at least two")
    raw_leaves = _program_leaves(program)
    maximum = len(raw_leaves) if maximum_leaves is None else min(maximum_leaves, len(raw_leaves))
    if maximum < minimum_leaves:
        return ()
    if training_content is not None:
        computed = canonical_training_content_hash(training_content)
        if training_content_hash is not None and training_content_hash != computed:
            raise ValueError("provided training content hash does not match canonical content")
        training_content_hash = computed
    if training_content_hash is None:
        hashes = getattr(program, "training_hashes", None)
        if hashes is None and isinstance(program, Mapping):
            hashes = program.get("training_hashes")
        if hashes is None:
            raise ValueError("canonical training content or its verified hash is required")
        training_content_hash = canonical_training_content_hash(tuple(hashes))
    if not _HASH_RE.fullmatch(str(training_content_hash)):
        raise ValueError("training content identity must be a lowercase SHA-256 hash")
    result: list[SubtreeOccurrence] = []
    for length in range(minimum_leaves, maximum + 1):
        for start in range(0, len(raw_leaves) - length + 1):
            stop = start + length
            normalized = normalize_leaf_sequence(raw_leaves[start:stop])
            result.append(SubtreeOccurrence(
                leaves=normalized, training_content_hash=str(training_content_hash),
                correct=correct, start=start, stop=stop,
                audit_id=audit_id, program_id=program_id,
            ))
    return tuple(result)


def anti_unify_subtrees(
    occurrences: Sequence[SubtreeOccurrence],
    *,
    name: str | None = None,
    minimum_support: int = 2,
) -> CompositeMacroTemplate:
    """Anti-unify same-shape contiguous occurrences into a typed template."""
    if not occurrences:
        raise ValueError("anti-unification requires at least one occurrence")
    if minimum_support != 2:
        raise ValueError("Block 9 stable support is fixed at two")
    shape_keys = {item.shape_key for item in occurrences}
    if len(shape_keys) != 1:
        raise ValueError("subtree occurrences have incompatible semantic shapes")
    exact_hashes = {item.training_content_hash for item in occurrences if item.correct}
    wrong_hashes = {item.training_content_hash for item in occurrences if not item.correct}
    all_leaves = [item.leaves for item in occurrences]
    holes: list[TypedHole] = []
    equality_classes: dict[str, int] = {}
    parameter_templates: list[Any] = []
    for index in range(len(all_leaves[0])):
        records = [leaves[index] for leaves in all_leaves]
        parameter_template = _anti_unify(
            [record["parameters"] for record in records],
            ("leaves", index, "parameters"), holes, equality_classes,
        )
        parameter_templates.append(parameter_template)
    holes_by_name = {hole.name: hole for hole in holes}
    leaf_templates: list[LeafTemplate] = []
    for index in range(len(all_leaves[0])):
        records = [leaves[index] for leaves in all_leaves]
        parameter_template = parameter_templates[index]
        marker_names = set(_hole_markers(parameter_template))
        local_holes = tuple(
            holes_by_name[name] for name in sorted(marker_names)
        )
        first = records[0]
        source_ids = {record.get("source_macro_id") for record in records}
        common_source_id = next(iter(source_ids)) if len(source_ids) == 1 else None
        costs = {int(record.get("cost", 1)) for record in records}
        statuses = {str(record.get("status", "primitive")) for record in records}
        if len(statuses) != 1:
            raise ValueError("anti-unification cannot merge different leaf lifecycle statuses")
        leaf_templates.append(LeafTemplate(
            namespace=str(first["namespace"]), family=str(first["family"]),
            macro_schema=str(first["macro_schema"]),
            parameter_template=parameter_template, holes=local_holes,
            source_macro_id=common_source_id,
            input_type=str(first["input_type"]), output_type=str(first["output_type"]),
            cost=max(costs),
            status=next(iter(statuses)),
        ))
    schema = semantic_subtree_schema(all_leaves[0])
    macro_name = name or schema
    wrong = len(wrong_hashes)
    support = len(exact_hashes)
    return CompositeMacroTemplate(
        name=macro_name, semantic_schema=schema, leaves=tuple(leaf_templates),
        holes=tuple(holes), status=_status(support, wrong, minimum_support),
        support_count=support, wrong_activation_count=wrong,
        minimum_support=minimum_support, rank=1,
        expanded_leaf_count=len(leaf_templates),
        description="Typed anti-unification of a contiguous multi-leaf program subtree.",
    )


def mine_composite_templates(
    sources: Iterable[Any],
    *,
    minimum_leaves: int = 2,
    maximum_leaves: int | None = None,
    minimum_support: int = 2,
) -> tuple[CompositeMacroTemplate, ...]:
    """Mine and anti-unify all compatible contiguous subtree occurrences.

    Each source may be a :class:`SubtreeOccurrence`, a mapping containing an
    ``occurrences`` sequence, or a mapping/tuple with a program, canonical
    training content/hash, correctness, and optional audit identifiers.
    """
    occurrences: list[SubtreeOccurrence] = []
    for source in sources:
        if isinstance(source, SubtreeOccurrence):
            occurrences.append(source)
            continue
        if isinstance(source, Mapping) and "occurrences" in source:
            occurrences.extend(source["occurrences"])
            continue
        if isinstance(source, Mapping):
            program = source.get("program", source)
            kwargs = {
                "training_content": source.get("training_content"),
                "training_content_hash": source.get("training_content_hash"),
                "correct": bool(source.get("correct", True)),
                "audit_id": source.get("audit_id", source.get("task_id")),
                "program_id": source.get("program_id"),
            }
        elif isinstance(source, tuple) and 2 <= len(source) <= 4:
            program = source[0]
            identity = source[1]
            kwargs = {
                "training_content": None,
                "training_content_hash": identity if isinstance(identity, str) and _HASH_RE.fullmatch(identity) else None,
                "correct": bool(source[2]) if len(source) >= 3 else True,
                "audit_id": source[3] if len(source) >= 4 else None,
                "program_id": None,
            }
            if kwargs["training_content_hash"] is None:
                kwargs["training_content"] = identity
        else:
            program = source
            kwargs = {
                "training_content": None, "training_content_hash": None,
                "correct": True, "audit_id": None, "program_id": None,
            }
        occurrences.extend(extract_contiguous_subtrees(
            program, minimum_leaves=minimum_leaves, maximum_leaves=maximum_leaves,
            **kwargs,
        ))
    grouped: dict[str, list[SubtreeOccurrence]] = {}
    for occurrence in occurrences:
        grouped.setdefault(occurrence.shape_key, []).append(occurrence)
    # It is possible for two source encodings to normalize to the same identity.
    # Merge their evidence without letting duplicate aliases count twice.
    merged: dict[str, tuple[CompositeMacroTemplate, set[str], set[str]]] = {}
    for _, group in sorted(grouped.items()):
        template = anti_unify_subtrees(group)
        exact = {item.training_content_hash for item in group if item.correct}
        wrong = {item.training_content_hash for item in group if not item.correct}
        if template.macro_id in merged:
            old, exact_old, wrong_old = merged[template.macro_id]
            exact_old.update(exact)
            wrong_old.update(wrong)
            merged[template.macro_id] = (old, exact_old, wrong_old)
        else:
            merged[template.macro_id] = (template, set(exact), set(wrong))
    result = [template.with_evidence(support_count=len(exact), wrong_activation_count=len(wrong))
              for template, exact, wrong in merged.values()]
    return tuple(sorted(result, key=lambda item: (item.semantic_schema, item.macro_id)))


def _role_symbol(value: str) -> str:
    lowered = value.strip().lower()
    for prefix in ("role:", "color_role:"):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix):]
    return lowered


def _valid_color_role_symbol(value: str) -> bool:
    lowered = value.strip().lower()
    if _role_symbol(lowered) in _COLOR_ROLE_SYMBOLS:
        return True
    for prefix in ("literal:", "color:"):
        if lowered.startswith(prefix):
            suffix = lowered[len(prefix):]
            return suffix.isdigit() and 0 <= int(suffix) <= 9
    return False


def _layout_head(value: str) -> str:
    return re.split(r"[:|]", value.strip().lower(), maxsplit=1)[0]


def _valid_layout(value: Any, depth: int = 0) -> bool:
    if depth > 12:
        return False
    if isinstance(value, str):
        return _layout_head(value) in _LAYOUT_HEADS
    if isinstance(value, Mapping):
        if not value:
            return False
        head = value.get("kind", value.get("operation", value.get("layout")))
        if head is None or not _valid_layout(head, depth + 1):
            return False
        return all(_valid_layout_item(item, depth + 1) for item in value.values())
    if isinstance(value, (list, tuple)):
        if not value or not isinstance(value[0], str) or _layout_head(value[0]) not in _LAYOUT_HEADS:
            return False
        return all(_valid_layout_item(item, depth + 1) for item in value[1:])
    return False


def _valid_layout_item(value: Any, depth: int) -> bool:
    if value is None or isinstance(value, bool):
        return value is None
    if isinstance(value, int):
        return -30 <= value <= 30
    if isinstance(value, str):
        return bool(re.fullmatch(r"[A-Za-z0-9_.:+|=-]{1,128}", value))
    if isinstance(value, Mapping):
        return depth <= 12 and all(
            isinstance(key, str) and _valid_layout_item(item, depth + 1)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return depth <= 12 and len(value) <= 64 and all(
            _valid_layout_item(item, depth + 1) for item in value
        )
    return False


def validate_typed_binding(value: Any, value_type: str) -> bool:
    """Check a hole binding against the closed Block 9 runtime contract."""
    if value_type not in _HOLE_TYPES:
        return False
    if value is None:
        return False
    if value_type == "bool":
        return isinstance(value, bool)
    if value_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type == "scalar":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if value_type in {"symbol", "direction", "operator_family"}:
        if not isinstance(value, str):
            return False
        if value_type == "direction":
            return value.strip().lower() in _DIRECTION_SYMBOLS
        if value_type == "operator_family":
            # Family-valued holes currently arise only from the reversible
            # semantic panel bridge.  New registries must extend this closed
            # set explicitly before their abstractions can activate.
            return value in _PANEL_FAMILIES
        return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_.:+|=-]{0,127}", value))
    if value_type == "record":
        return isinstance(value, Mapping) and bool(value)
    if value_type == "sequence":
        return isinstance(value, (list, tuple)) and len(value) <= 256
    if value_type == "layout":
        return _valid_layout(value)
    if value_type == "recolor_map":
        if not isinstance(value, (list, tuple)) or len(value) > 10:
            return False
        seen: set[int] = set()
        for pair in value:
            if not isinstance(pair, (list, tuple)) or len(pair) != 2:
                return False
            source, target = pair
            if (
                isinstance(source, bool) or not isinstance(source, int)
                or isinstance(target, bool) or not isinstance(target, int)
                or not 0 <= source <= 9 or not 0 <= target <= 9
                or source in seen
            ):
                return False
            seen.add(source)
        return True
    if value_type == "color_role":
        return (
            isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 9
        ) or (
            isinstance(value, str) and _valid_color_role_symbol(value)
        )
    if value_type == "value":
        if isinstance(value, bool):
            return True
        if isinstance(value, int):
            return -900 <= value <= 900
        if isinstance(value, float):
            return value == value and value not in (float("inf"), float("-inf"))
        if isinstance(value, str):
            return len(value) <= 256 and not any(ord(character) < 32 for character in value)
        if isinstance(value, (list, tuple)):
            return len(value) <= 256 and all(validate_typed_binding(item, "value") for item in value)
        if isinstance(value, Mapping):
            return len(value) <= 256 and all(
                isinstance(key, str) and validate_typed_binding(item, "value")
                for key, item in value.items()
            )
    return False


def _substitute(template: Any, bindings: Mapping[str, Any], holes: Sequence[TypedHole]) -> Any:
    specifications = {hole.name: hole for hole in holes}

    def visit(value: Any) -> Any:
        if isinstance(value, Mapping):
            if _HOLE_KEY in value:
                name = str(value[_HOLE_KEY])
                specification = specifications[name]
                if name not in bindings:
                    if specification.optional:
                        return None
                    raise ValueError(f"missing binding for {name}")
                binding = canonical_value(bindings[name])
                if binding is None and specification.optional:
                    return None
                if not validate_typed_binding(binding, specification.value_type):
                    raise TypeError(f"binding {name} does not have type {specification.value_type}")
                return binding
            return {str(key): visit(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [visit(item) for item in value]
        return canonical_value(value)

    return visit(template)


def _path_value(root: Any, path: Sequence[PathPart]) -> Any:
    value = root
    for part in path:
        if isinstance(value, Mapping):
            if part not in value:
                raise ValueError(f"hole path is absent at {part!r}")
            value = value[part]
        elif isinstance(value, (list, tuple)):
            if isinstance(part, bool) or not isinstance(part, int):
                raise ValueError("sequence hole path coordinate must be an integer")
            try:
                value = value[part]
            except IndexError as exc:
                raise ValueError("hole path sequence coordinate is out of range") from exc
        else:
            raise ValueError("hole path descends through a scalar")
    return canonical_value(value)


def extract_template_bindings(
    template: CompositeMacroTemplate,
    occurrence_or_leaves: SubtreeOccurrence | Sequence[Any],
) -> dict[str, Any]:
    """Bind a template from current content while enforcing hole equalities."""
    leaves = (
        occurrence_or_leaves.leaves
        if isinstance(occurrence_or_leaves, SubtreeOccurrence)
        else normalize_leaf_sequence(occurrence_or_leaves)
    )
    if len(leaves) != len(template.leaves):
        raise ValueError("binding source has the wrong subtree length")
    for actual, expected in zip(leaves, template.leaves):
        if (
            actual["namespace"] != expected.namespace
            or actual["family"] != expected.family
            or actual["macro_schema"] != expected.macro_schema
            or actual["input_type"] != expected.input_type
            or actual["output_type"] != expected.output_type
        ):
            raise ValueError("binding source does not match the template shape")
    root = {"leaves": list(leaves)}
    result: dict[str, Any] = {}
    for hole in template.holes:
        value = _path_value(root, hole.path)
        for equal_path in hole.equal_paths:
            if _path_value(root, equal_path) != value:
                raise ValueError(f"equality constraint for hole {hole.name} is violated")
        if value is None and hole.optional:
            continue
        if not validate_typed_binding(value, hole.value_type):
            raise TypeError(f"source value for {hole.name} violates type {hole.value_type}")
        result[hole.name] = value
    return result


def self_validate_abstraction() -> dict[str, Any]:
    """Run deterministic, dependency-free invariants used by package smoke tests."""
    leaves_a = [
        {"namespace": "primitive", "family": "identity", "parameters": {}},
        {"namespace": "primitive", "family": "crop_bbox", "parameters": {}},
        {"namespace": "compiler", "family": "panel_program", "parameters": {
            "spec": "equal:2x1", "operation": "select:0|id", "recolor": [[0, 0]],
        }},
        {"namespace": "primitive", "family": "rotate", "parameters": {"turns": 1}},
    ]
    leaves_b = [
        {"namespace": "primitive", "family": "identity", "parameters": {}},
        {"namespace": "primitive", "family": "crop_bbox", "parameters": {}},
        {"namespace": "compiler", "family": "role_panel_program", "parameters": {
            "panelization": ["equal", 2, 1], "operation": ["select", 0, "id"],
            "recolor": [[0, 0]],
        }},
        {"namespace": "primitive", "family": "rotate", "parameters": {"turns": 3}},
    ]
    hash_a = canonical_training_content_hash({"train": "a"})
    hash_b = canonical_training_content_hash({"train": "b"})
    windows = extract_contiguous_subtrees(leaves_a, training_content_hash=hash_a)
    assert len(windows) == 6  # all length-2, length-3, and length-4 windows
    pair_a = next(item for item in windows if item.start == 1 and len(item.leaves) == 2)
    pair_b = next(item for item in extract_contiguous_subtrees(
        leaves_b, training_content_hash=hash_b,
    ) if item.start == 1 and len(item.leaves) == 2)
    template = anti_unify_subtrees((pair_a, pair_b))
    assert template.semantic_schema == "panel_extraction"
    assert template.status is PromotionStatus.STABLE and template.support_count == 2
    alias = replace(pair_a, audit_id="alias")
    aliased = anti_unify_subtrees((pair_a, alias))
    assert aliased.support_count == 1 and aliased.status is PromotionStatus.PROVISIONAL
    mutable_parameters = {"nested": [1, 2]}
    immutable_leaf = LeafTemplate(
        "primitive", "immutability_probe", "immutability_probe", mutable_parameters,
    )
    leaf_id = immutable_leaf.leaf_id
    mutable_parameters["nested"][0] = 9
    assert immutable_leaf.leaf_id == leaf_id
    assert canonical_value(immutable_leaf.parameter_template) == {"nested": [1, 2]}
    mutable_leaves = [immutable_leaf, LeafTemplate(
        "primitive", "immutability_probe_2", "immutability_probe_2", {},
    )]
    mutable_dependencies: list[str] = []
    immutable_macro = CompositeMacroTemplate(
        "immutability_probe", "immutability_probe", mutable_leaves, [],
        dependencies=mutable_dependencies,
    )
    macro_id = immutable_macro.macro_id
    mutable_leaves.clear()
    mutable_dependencies.append("mutated")
    assert immutable_macro.macro_id == macro_id and len(immutable_macro.leaves) == 2
    return {
        "contiguous_windows": len(windows),
        "panel_schema": template.semantic_schema,
        "distinct_support": template.support_count,
        "alias_support": aliased.support_count,
        "deep_immutability": True,
        "passed": True,
    }


__all__ = [
    "CompositeMacroTemplate", "LeafTemplate", "PromotionStatus", "SubtreeOccurrence",
    "TypedHole", "anti_unify_subtrees", "canonical_json", "canonical_training_content_hash",
    "canonical_value", "content_hash", "extract_contiguous_subtrees",
    "extract_template_bindings", "mine_composite_templates", "normalize_leaf_record", "normalize_leaf_sequence",
    "self_validate_abstraction", "semantic_subtree_schema", "validate_typed_binding",
]
