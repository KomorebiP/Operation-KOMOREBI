from __future__ import annotations

import hashlib
import io
import json
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from . import atlas
from ._version import __version__

Array = NDArray[np.float64]
ResidualStorage = Literal["dense", "sparse", "none"]
DecodeMode = Literal["raw", "bounded", "exact"]

FORMAT_NAME = "komorebi-am-spd-model"
SCHEMA_VERSION = 2
SUPPORTED_SCHEMA_VERSIONS = {1, 2}


def _json_safe(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value


def _tuple_tree(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_tuple_tree(item) for item in value)
    if isinstance(value, dict):
        return {key: _tuple_tree(item) for key, item in value.items()}
    return value


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _array_payload(value: np.ndarray) -> bytes:
    buffer = io.BytesIO()
    np.save(buffer, np.asarray(value), allow_pickle=False)
    return buffer.getvalue()


def _read_array(payload: bytes) -> np.ndarray:
    return np.load(io.BytesIO(payload), allow_pickle=False)


def _nonnegative_integer(value: Any) -> bool:
    return isinstance(value, (int, np.integer)) and not isinstance(value, (bool, np.bool_)) and value >= 0


def _validate_array(
    name: str,
    value: Any,
    errors: list[str],
    *,
    shape: tuple[int, ...] | None = None,
    ndim: int | None = None,
    integer: bool = False,
) -> np.ndarray | None:
    if not isinstance(value, np.ndarray):
        errors.append(f"{name} must be a NumPy array")
        return None
    valid = True
    if integer:
        numeric = np.issubdtype(value.dtype, np.integer)
    else:
        numeric = np.issubdtype(value.dtype, np.number) and not np.issubdtype(value.dtype, np.complexfloating)
    if not numeric:
        errors.append(f"{name} must contain {'integer' if integer else 'real numeric'} values")
        valid = False
    elif not np.isfinite(value).all():
        errors.append(f"{name} contains non-finite values")
        valid = False
    if shape is not None and value.shape != shape:
        errors.append(f"{name} has the wrong shape: expected {shape}, got {value.shape}")
        valid = False
    if ndim is not None and value.ndim != ndim:
        errors.append(f"{name} must have {ndim} dimensions")
        valid = False
    return value if valid else None


def _validate_packet_records(records: Any, errors: list[str], *, label: str = "packet_specs") -> None:
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        errors.append(f"{label} must be a list of objects")
        return
    parameter_counts = {
        "constant": 0, "dct": 2, "mask": 1, "morph": 3, "affine": 5,
        "radial": 4, "masked_poly": 2, "masked_dct": 3, "soft_mask": 3,
        "combine": 3, "quadtree": 4, "edge_ribbon": 2,
    }
    for position, record in enumerate(records):
        kind = record.get("kind")
        params = record.get("params", [])
        try:
            if not isinstance(kind, str) or kind not in parameter_counts:
                raise ValueError("unknown packet kind")
            if not isinstance(params, (list, tuple)) or len(params) != parameter_counts[kind]:
                raise ValueError("wrong parameter count")
            if any(isinstance(value, (bool, np.bool_)) or not isinstance(value, (str, int, float, np.integer, np.floating)) or
                   (not isinstance(value, str) and not np.isfinite(value)) for value in params):
                raise ValueError("invalid packet parameter")
            if not _nonnegative_integer(record.get("depth", 0)):
                raise ValueError("invalid depth")
            complexity = float(record.get("complexity", 1.0))
            if not np.isfinite(complexity) or complexity <= 0:
                raise ValueError("invalid complexity")
            spec = _packet_spec_from_record(record)
            if record.get("key", spec.key) != spec.key:
                raise ValueError("packet key does not match its specification")
        except (KeyError, TypeError, ValueError, OverflowError) as exc:
            errors.append(f"{label} record {position} is invalid: {exc}")


def _validate_metrics(name: str, mapping: Any, errors: list[str]) -> None:
    if not isinstance(mapping, dict):
        errors.append(f"{name} must be an object")
        return
    for key, value in mapping.items():
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            errors.append(f"{name}.{key} must be numeric")
            continue
        # A perfect reconstruction has infinite PSNR by definition.
        if not np.isfinite(number) and not (name == "metrics" and key == "psnr" and number == np.inf):
            errors.append(f"{name}.{key} contains a non-finite value")


def _validate_closure_arrays(model: Any, errors: list[str]) -> tuple[int, int, int] | None:
    value = _validate_array("reconstruction", model.reconstruction, errors, ndim=3)
    shape = tuple(value.shape) if value is not None else None
    if shape is not None and any(length < 1 for length in shape):
        errors.append("reconstruction dimensions must be positive")
        shape = None
    try:
        threshold = float(model.residual_threshold)
    except (TypeError, ValueError, OverflowError):
        threshold = float("nan")
    if not np.isfinite(threshold) or threshold < 0:
        errors.append("residual_threshold must be finite and nonnegative")
    for name in ("parameter_count", "packet_count"):
        if not _nonnegative_integer(getattr(model, name)):
            errors.append(f"{name} must be a nonnegative integer")
    if model.residual_storage == "dense":
        if model.archive_residual is None:
            errors.append("dense residual is missing")
        else:
            _validate_array("archive_residual", model.archive_residual, errors, shape=shape, ndim=3)
    elif model.residual_storage == "sparse":
        if model.residual_indices is None or model.residual_values is None:
            errors.append("sparse residual arrays are missing")
        else:
            indices = _validate_array("residual_indices", model.residual_indices, errors, ndim=2, integer=True)
            values = _validate_array("residual_values", model.residual_values, errors, ndim=2)
            if indices is not None and indices.shape[1] != 2:
                errors.append("residual_indices must have shape N x 2")
                indices = None
            if values is not None and shape is not None and values.shape[1] != shape[2]:
                errors.append("residual_values must have shape N x C")
            if indices is not None and values is not None and len(indices) != len(values):
                errors.append("sparse residual index and value counts differ")
            if indices is not None and indices.size and shape is not None:
                if np.any(indices < 0) or np.any(indices[:, 0] >= shape[0]) or np.any(indices[:, 1] >= shape[1]):
                    errors.append("sparse residual indices are outside the image bounds")
                if len(np.unique(indices, axis=0)) != len(indices):
                    errors.append("sparse residual indices contain duplicate coordinates")
    elif model.residual_storage != "none":
        errors.append(f"unknown residual storage: {model.residual_storage}")
    if model.input_image is not None:
        _validate_array("input_image", model.input_image, errors, shape=shape, ndim=3)
    _validate_metrics("metrics", model.metrics, errors)
    return shape  # type: ignore[return-value]


def _read_manifest(archive: zipfile.ZipFile, format_name: str, schema_versions: set[int]) -> dict[str, Any]:
    names = archive.namelist()
    if len(names) != len(set(names)):
        raise ValueError("model archive contains duplicate member names")
    if "manifest.json" not in names:
        raise ValueError("model archive is missing manifest.json")
    manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
    if not isinstance(manifest, dict) or manifest.get("format") != format_name:
        raise ValueError("not a supported AM-SPD model archive")
    schema = manifest.get("schema_version")
    if not _nonnegative_integer(schema) or schema not in schema_versions:
        raise ValueError(f"unsupported model schema version: {schema}")
    if format_name == FORMAT_NAME:
        if not {"selected_method", "parameter_count", "packet_count"}.issubset(manifest):
            raise ValueError("model metadata is missing its method or component counts")
        if not isinstance(manifest["selected_method"], str):
            raise ValueError("selected_method must be a string")
    try:
        threshold = float(manifest.get("residual_threshold", 0.0))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("residual_threshold must be finite and nonnegative") from exc
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("residual_threshold must be finite and nonnegative")
    metric_errors: list[str] = []
    for name in ("metrics", "candidate_rmse"):
        if name in manifest:
            _validate_metrics(name, manifest[name], metric_errors)
    if metric_errors:
        raise ValueError("model metrics validation failed: " + "; ".join(metric_errors))
    for name in ("parameter_count", "packet_count"):
        if name in manifest and not _nonnegative_integer(manifest[name]):
            raise ValueError(f"{name} must be a nonnegative integer")
    for name in ("config", "metrics", "candidate_rmse", "provenance", "search_state", "tiled_config"):
        if name in manifest and not isinstance(manifest[name], dict):
            raise ValueError(f"model metadata {name} must be an object")
    for name in ("packet_specs", "packet_history", "singular_modes", "lagrange_tree_selections",
                 "exact_tree_selections", "exact_frontier", "portfolio_trials", "replacement_blocks",
                 "tile_records", "tile_models"):
        if name in manifest and (not isinstance(manifest[name], list) or any(not isinstance(item, dict) for item in manifest[name])):
            raise ValueError(f"model metadata {name} must be a list of objects")
    return manifest


def _read_manifest_arrays(archive: zipfile.ZipFile, manifest: dict[str, Any]) -> dict[str, np.ndarray]:
    records = manifest.get("arrays", {})
    if not isinstance(records, dict):
        raise ValueError("model arrays metadata must be an object")
    arrays: dict[str, np.ndarray] = {}
    names = set(archive.namelist())
    for name, record in records.items():
        if not isinstance(record, dict) or not {"path", "shape", "dtype", "sha256"}.issubset(record):
            raise ValueError(f"model array metadata is incomplete: {name}")
        filename = record["path"]
        if not isinstance(filename, str) or filename not in names:
            raise ValueError(f"model array is missing: {filename}")
        payload = archive.read(filename)
        if _sha256(payload) != record["sha256"]:
            raise ValueError(f"model array checksum mismatch: {name}")
        value = _read_array(payload)
        if not isinstance(value, np.ndarray):
            raise ValueError(f"model array payload is not an NPY array: {name}")
        if list(value.shape) != record["shape"]:
            raise ValueError(f"model array shape mismatch: {name}")
        if str(value.dtype) != record["dtype"]:
            raise ValueError(f"model array dtype mismatch: {name}")
        if name in {"residual_indices", "search_seed_ids"}:
            if not np.issubdtype(value.dtype, np.integer):
                raise ValueError(f"model array {name} must contain integer values")
        elif not np.issubdtype(value.dtype, np.number) or np.issubdtype(value.dtype, np.complexfloating):
            raise ValueError(f"model array {name} must contain real numeric values")
        if not np.isfinite(value).all():
            raise ValueError(f"model array contains non-finite values: {name}")
        if "nbytes" in record and (not _nonnegative_integer(record["nbytes"]) or record["nbytes"] != value.nbytes):
            raise ValueError(f"model array byte count mismatch: {name}")
        arrays[name] = value
    return arrays


def _stack(values: list[np.ndarray], trailing_shape: tuple[int, ...]) -> np.ndarray:
    if values:
        return np.stack([np.asarray(value, dtype=np.float64) for value in values])
    return np.empty((0, *trailing_shape), dtype=np.float64)


def _packet_spec_record(spec: Any) -> dict[str, Any]:
    return {
        "key": str(spec.key),
        "kind": str(spec.kind),
        "params": _json_safe(spec.params),
        "parent": str(spec.parent),
        "depth": int(spec.depth),
        "complexity": float(spec.complexity),
    }


def _packet_spec_from_record(record: dict[str, Any]) -> atlas.PacketSpec:
    return atlas.PacketSpec(
        kind=str(record["kind"]),
        params=tuple(_tuple_tree(record.get("params", []))),
        parent=str(record.get("parent", "")),
        depth=int(record.get("depth", 0)),
        complexity=float(record.get("complexity", 1.0)),
    )


def _packet_selection_from_record(record: dict[str, Any]) -> atlas.PacketSelection:
    return atlas.PacketSelection(
        iteration=int(record.get("iteration", 0)),
        spec_key=str(record.get("spec_key", "")),
        kind=str(record.get("kind", "unknown")),
        parent=str(record.get("parent", "")),
        depth=int(record.get("depth", 0)),
        complexity=float(record.get("complexity", 1.0)),
        gain=float(record.get("gain", 0.0)),
        score=float(record.get("score", 0.0)),
        residual_norm=float(record.get("residual_norm", 0.0)),
        packet_count=int(record.get("packet_count", 0)),
        seed_id=int(record["seed_id"]) if record.get("seed_id") is not None else None,
    )


def _tree_selection_record(selection: Any) -> dict[str, Any]:
    region = selection.region
    model = selection.model
    return {
        "region": {
            "y0": int(region.y0),
            "x0": int(region.x0),
            "y1": int(region.y1),
            "x1": int(region.x1),
            "depth": int(region.depth),
            "source": str(region.source),
        },
        "model": {
            "orientation": str(model.orientation),
            "rank": int(model.rank),
            "parameter_count": int(model.parameter_count),
            "error_squared": float(model.error_squared),
            "singular_values": [float(value) for value in model.singular_values],
            "direction_count": len(model.directions),
        },
    }


def _block_record(block: Any) -> dict[str, Any]:
    region = block.region
    return {
        "iteration": int(block.iteration),
        "region": {
            "y0": int(region.y0),
            "x0": int(region.x0),
            "y1": int(region.y1),
            "x1": int(region.x1),
            "depth": int(region.depth),
            "source": str(region.source),
        },
        "orientation": str(block.orientation),
        "rank": int(block.rank),
        "parameter_count": int(block.parameter_count),
        "gain": float(block.gain),
        "score": float(block.score),
        "singular_values": [float(value) for value in block.singular_values],
    }


def _encode_residual(
    residual: Array,
    storage: ResidualStorage,
    threshold: float,
) -> tuple[Array | None, NDArray[np.int64] | None, Array | None, float]:
    if storage not in {"dense", "sparse", "none"}:
        raise ValueError(f"unsupported residual storage: {storage}")
    if not np.isfinite(threshold) or threshold < 0:
        raise ValueError("residual_threshold must be finite and nonnegative")
    if storage == "dense":
        return np.asarray(residual, dtype=np.float64).copy(), None, None, 0.0
    if storage == "sparse":
        value = np.asarray(residual, dtype=np.float64)
        magnitude = np.max(np.abs(value), axis=2)
        indices = np.argwhere(magnitude > threshold).astype(np.int64)
        values = (
            value[indices[:, 0], indices[:, 1]].copy()
            if indices.size
            else np.empty((0, value.shape[2]), dtype=np.float64)
        )
        return None, indices, values, float(threshold)
    return None, None, None, 0.0


@dataclass
class AMSpdModel:
    """Portable AM-SPD decomposition archive.

    Schema 2 adds the finite candidate frontier, generator seed masks,
    quadtree leaves, and random-generator state required for exact continuation
    of a packet search. Schema-1 models remain readable and can be continued as
    deterministic warm starts when packet atoms and exact source data exist.
    """

    reconstruction: Array
    selected_method: str
    parameter_count: int
    packet_count: int
    config: dict[str, Any]
    metrics: dict[str, float]
    candidate_rmse: dict[str, float]
    schema_version: int = SCHEMA_VERSION
    residual_storage: ResidualStorage = "dense"
    residual_threshold: float = 0.0
    archive_residual: Array | None = None
    residual_indices: NDArray[np.int64] | None = None
    residual_values: Array | None = None
    input_image: Array | None = None
    core_atoms: Array | None = None
    core_coefficients: Array | None = None
    singular_directions: Array | None = None
    singular_coefficients: Array | None = None
    lagrange_directions: Array | None = None
    exact_directions: Array | None = None
    replacement_directions: Array | None = None
    search_seed_masks: Array | None = None
    search_seed_ids: NDArray[np.int64] | None = None
    packet_specs: list[dict[str, Any]] = field(default_factory=list)
    packet_history: list[dict[str, Any]] = field(default_factory=list)
    singular_modes: list[dict[str, Any]] = field(default_factory=list)
    lagrange_tree_selections: list[dict[str, Any]] = field(default_factory=list)
    exact_tree_selections: list[dict[str, Any]] = field(default_factory=list)
    exact_frontier: list[dict[str, Any]] = field(default_factory=list)
    portfolio_trials: list[dict[str, Any]] = field(default_factory=list)
    replacement_blocks: list[dict[str, Any]] = field(default_factory=list)
    search_state: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_result(
        cls,
        result: Any,
        *,
        residual_storage: ResidualStorage = "dense",
        residual_threshold: float = 0.0,
        include_input: bool = False,
        include_atoms: bool = True,
        include_directions: bool = True,
        provenance: dict[str, Any] | None = None,
    ) -> AMSpdModel:
        reconstruction = np.asarray(result.reconstruction, dtype=np.float64)
        residual = np.asarray(result.archive_residual, dtype=np.float64)
        if reconstruction.shape != residual.shape:
            raise ValueError("reconstruction and residual shapes differ")
        dense_residual, residual_indices, residual_values, effective_threshold = _encode_residual(
            residual,
            residual_storage,
            residual_threshold,
        )

        core = result.core_result
        singular = result.singular_result
        lagrange = result.lagrange_tree_result
        exact = result.exact_tree_result

        core_atoms = None
        core_coefficients = None
        packet_specs: list[dict[str, Any]] = []
        packet_history: list[dict[str, Any]] = []
        search_seed_masks = None
        search_seed_ids = None
        search_state: dict[str, Any] = {}
        if core is not None:
            packet_specs = [_packet_spec_record(spec) for spec in core.active_specs]
            packet_history = [_json_safe(asdict(item)) for item in core.history]
            if include_atoms:
                core_atoms = _stack(list(core.active_atoms), reconstruction.shape[:2])
                core_coefficients = np.asarray(core.coefficients, dtype=np.float64).copy()
            if core.search_state is not None and include_atoms:
                state = core.search_state
                seed_ids = np.array(sorted(state.seed_masks), dtype=np.int64)
                search_seed_ids = seed_ids
                search_seed_masks = (
                    np.stack([np.asarray(state.seed_masks[int(seed_id)], dtype=np.float64) for seed_id in seed_ids])
                    if len(seed_ids)
                    else np.empty((0, *reconstruction.shape[:2]), dtype=np.float64)
                )
                search_state = {
                    "exact": True,
                    "candidate_specs": [_packet_spec_record(spec) for spec in state.candidate_specs],
                    "seed_metadata": {
                        str(seed_id): _json_safe(metadata) for seed_id, metadata in state.seed_metadata.items()
                    },
                    "next_seed_id": int(state.next_seed_id),
                    "selected_seed_ids": [int(seed_id) for seed_id in state.selected_seed_ids],
                    "quadtree_leaves": [list(map(int, rectangle)) for rectangle in state.quadtree_leaves],
                    "random_state": _json_safe(state.random_state),
                }
            elif include_atoms:
                search_state = {"exact": False, "compatibility": "warm-start-frontier-rebuild"}

        singular_modes: list[dict[str, Any]] = []
        singular_directions = None
        singular_coefficients = None
        if singular is not None:
            singular_modes = [_json_safe(asdict(mode)) for mode in singular.modes]
            if include_directions:
                singular_directions = _stack(list(singular.directions), reconstruction.shape)
                singular_coefficients = np.asarray(singular.coefficients, dtype=np.float64).copy()

        lagrange_selections: list[dict[str, Any]] = []
        lagrange_directions = None
        if lagrange is not None:
            lagrange_selections = [_tree_selection_record(item) for item in lagrange.tree_selections]
            if include_directions:
                lagrange_directions = _stack(list(lagrange.directions), reconstruction.shape)

        exact_selections: list[dict[str, Any]] = []
        exact_frontier: list[dict[str, Any]] = []
        exact_directions = None
        if exact is not None:
            exact_selections = [_tree_selection_record(item) for item in exact.selections]
            exact_frontier = [
                {
                    "parameter_count": int(state.parameter_count),
                    "error_squared": float(state.error_squared),
                    "selection_count": len(state.selections),
                }
                for state in exact.frontier
            ]
            if include_directions:
                exact_directions = _stack(list(exact.directions), reconstruction.shape)

        portfolio_trials: list[dict[str, Any]] = []
        replacement_blocks: list[dict[str, Any]] = []
        replacement_directions = None
        selected_seed = result.selected_method.split(":", 1)[1] if result.selected_method.startswith("portfolio:") else None
        selected_portfolio = None
        for portfolio in result.portfolios:
            portfolio_trials.extend(_json_safe(asdict(trial)) for trial in portfolio.trials)
            if selected_seed is not None and portfolio.seed == selected_seed:
                selected_portfolio = portfolio
        if selected_portfolio is not None and selected_portfolio.replacement is not None:
            replacement_blocks = [_block_record(item) for item in selected_portfolio.replacement.blocks]
            if include_directions:
                replacement_directions = _stack(list(selected_portfolio.replacement.directions), reconstruction.shape)

        combined_provenance = dict(provenance or {})
        metadata = getattr(result, "run_metadata", None)
        if metadata:
            combined_provenance.setdefault("run_metadata", _json_safe(metadata))

        return cls(
            reconstruction=reconstruction.copy(),
            selected_method=str(result.selected_method),
            parameter_count=int(result.parameter_count),
            packet_count=int(result.packet_count),
            config=_json_safe(asdict(result.config)),
            metrics={key: float(value) for key, value in result.metrics.items()},
            candidate_rmse={key: float(value) for key, value in result.candidate_rmse.items()},
            schema_version=SCHEMA_VERSION,
            residual_storage=residual_storage,
            residual_threshold=effective_threshold,
            archive_residual=dense_residual,
            residual_indices=residual_indices,
            residual_values=residual_values,
            input_image=np.asarray(result.input_image, dtype=np.float64).copy() if include_input else None,
            core_atoms=core_atoms,
            core_coefficients=core_coefficients,
            singular_directions=singular_directions,
            singular_coefficients=singular_coefficients,
            lagrange_directions=lagrange_directions,
            exact_directions=exact_directions,
            replacement_directions=replacement_directions,
            search_seed_masks=search_seed_masks,
            search_seed_ids=search_seed_ids,
            packet_specs=packet_specs,
            packet_history=packet_history,
            singular_modes=singular_modes,
            lagrange_tree_selections=lagrange_selections,
            exact_tree_selections=exact_selections,
            exact_frontier=exact_frontier,
            portfolio_trials=portfolio_trials,
            replacement_blocks=replacement_blocks,
            search_state=search_state,
            provenance=_json_safe(combined_provenance),
        )

    @classmethod
    def from_legacy_archive(
        cls,
        path: str | Path,
        *,
        residual_storage: ResidualStorage = "dense",
        residual_threshold: float = 0.0,
    ) -> AMSpdModel:
        """Convert a version 0.1.x result ``.npz`` archive to schema 2."""

        source = Path(path)
        with np.load(source, allow_pickle=False) as archive:
            required = {"input_image", "reconstruction", "archive_residual", "summary_json"}
            missing = required - set(archive.files)
            if missing:
                raise ValueError(f"legacy archive is missing: {', '.join(sorted(missing))}")
            input_image = np.asarray(archive["input_image"], dtype=np.float64)
            reconstruction = np.asarray(archive["reconstruction"], dtype=np.float64)
            residual = np.asarray(archive["archive_residual"], dtype=np.float64)
            summary = json.loads(str(np.asarray(archive["summary_json"]).item()))
        if input_image.shape != reconstruction.shape or residual.shape != reconstruction.shape:
            raise ValueError("legacy archive arrays have inconsistent shapes")
        dense_residual, residual_indices, residual_values, effective_threshold = _encode_residual(
            residual,
            residual_storage,
            residual_threshold,
        )
        return cls(
            reconstruction=reconstruction,
            selected_method=str(summary.get("selected_method", "legacy")),
            parameter_count=int(summary.get("parameter_count", 0)),
            packet_count=int(summary.get("packet_count", 0)),
            config=dict(summary.get("config", {})),
            metrics={str(key): float(value) for key, value in summary.get("metrics", {}).items()},
            candidate_rmse={str(key): float(value) for key, value in summary.get("candidate_rmse", {}).items()},
            schema_version=SCHEMA_VERSION,
            residual_storage=residual_storage,
            residual_threshold=effective_threshold,
            archive_residual=dense_residual,
            residual_indices=residual_indices,
            residual_values=residual_values,
            input_image=input_image,
            search_state={"exact": False, "compatibility": "legacy-result-has-no-packet-state"},
            provenance={
                "converted_from": "am-spd-0.1.x-npz",
                "source_name": source.name,
                "structured_components_available": False,
            },
        )

    @property
    def shape(self) -> tuple[int, int, int]:
        return tuple(int(value) for value in self.reconstruction.shape)  # type: ignore[return-value]

    @property
    def has_residual_closure(self) -> bool:
        return self.residual_storage in {"dense", "sparse"}

    @property
    def has_exact_closure(self) -> bool:
        return self.has_residual_closure and self.residual_threshold == 0.0

    @property
    def supports_resume(self) -> bool:
        has_source = self.input_image is not None or self.has_exact_closure
        return bool(has_source and self.core_atoms is not None and self.packet_specs)

    @property
    def resume_state_quality(self) -> str:
        if not self.supports_resume:
            return "unavailable"
        if bool(self.search_state.get("exact")):
            # Reusing the stored input preserves the exact floating-point
            # objective as well as the exact candidate frontier. When the
            # source is reconstructed from residual closure, the frontier is
            # exact but the source can differ by one rounding unit.
            return "exact" if self.input_image is not None else "frontier-exact"
        return "warm"

    def residual(self) -> Array:
        if self.residual_storage == "dense":
            if self.archive_residual is None:
                raise ValueError("dense residual is missing")
            return np.asarray(self.archive_residual, dtype=np.float64).copy()
        if self.residual_storage == "sparse":
            if self.residual_indices is None or self.residual_values is None:
                raise ValueError("sparse residual arrays are missing")
            value = np.zeros(self.shape, dtype=np.float64)
            if self.residual_indices.size:
                value[self.residual_indices[:, 0], self.residual_indices[:, 1]] = self.residual_values
            return value
        raise ValueError("this model does not contain residual closure data")

    def decode(self, mode: DecodeMode = "bounded") -> Array:
        if mode == "raw":
            return np.asarray(self.reconstruction, dtype=np.float64).copy()
        if mode == "bounded":
            return np.clip(np.asarray(self.reconstruction, dtype=np.float64), 0.0, 1.0)
        if mode == "exact":
            if not self.has_exact_closure:
                raise ValueError("this model does not contain an unthresholded exact residual closure")
            return np.asarray(self.reconstruction, dtype=np.float64) + self.residual()
        raise ValueError(f"unsupported decode mode: {mode}")

    def source_image(self) -> Array:
        if self.input_image is not None:
            return np.asarray(self.input_image, dtype=np.float64).copy()
        if self.has_exact_closure:
            return self.decode("exact")
        raise ValueError("resuming requires the stored input or an exact residual closure")

    @property
    def exact_identity_error(self) -> float | None:
        if self.input_image is None or not self.has_exact_closure:
            return None
        return float(np.max(np.abs(self.input_image - self.decode("exact"))))

    def to_core_result(self, image: Array | None = None) -> atlas.ReconstructionResult:
        """Reconstruct the packet-core state required for continued search."""

        verification = self.verify()
        if not verification["passed"]:
            raise ValueError("model validation failed: " + "; ".join(verification["errors"]))
        source = atlas.ensure_image(image if image is not None else self.source_image())
        if not self.supports_resume:
            raise ValueError("model lacks packet atoms, packet specifications, or exact source data")
        if self.core_atoms is None:
            raise ValueError("model does not contain core packet atoms")
        specs = [_packet_spec_from_record(record) for record in self.packet_specs]
        atoms = [np.asarray(atom, dtype=np.float64).copy() for atom in self.core_atoms]
        if len(specs) != len(atoms):
            raise ValueError("model packet atom and specification counts differ")
        matrix = np.column_stack([atom.reshape(-1) for atom in atoms])
        if self.core_coefficients is not None:
            coefficients = np.asarray(self.core_coefficients, dtype=np.float64).copy()
            if coefficients.shape != (len(atoms), source.shape[2]):
                raise ValueError("model core coefficient array has the wrong shape")
        else:
            coefficients = np.linalg.lstsq(matrix, source.reshape(-1, source.shape[2]), rcond=1e-10)[0]
        reconstruction = (matrix @ coefficients).reshape(source.shape)
        residual = source - reconstruction
        history = [_packet_selection_from_record(record) for record in self.packet_history]
        residual_norms = [float(np.linalg.norm(source))]
        residual_norms.extend(float(item.residual_norm) for item in history)
        if not history:
            residual_norms.append(float(np.linalg.norm(residual)))

        packet_search_state = None
        if self.search_state.get("exact"):
            if self.search_seed_masks is None or self.search_seed_ids is None:
                raise ValueError("exact resume metadata is present but its seed masks are missing")
            seed_masks = {
                int(seed_id): np.asarray(mask, dtype=np.float64).copy()
                for seed_id, mask in zip(self.search_seed_ids, self.search_seed_masks, strict=True)
            }
            seed_metadata = {
                int(seed_id): dict(metadata)
                for seed_id, metadata in self.search_state.get("seed_metadata", {}).items()
            }
            packet_search_state = atlas.PacketSearchState(
                candidate_specs=[
                    _packet_spec_from_record(record)
                    for record in self.search_state.get("candidate_specs", [])
                ],
                seed_masks=seed_masks,
                seed_metadata=seed_metadata,
                next_seed_id=int(self.search_state.get("next_seed_id", max(seed_masks, default=-1) + 1)),
                selected_seed_ids=[int(value) for value in self.search_state.get("selected_seed_ids", [])],
                quadtree_leaves=[
                    tuple(map(int, rectangle)) for rectangle in self.search_state.get("quadtree_leaves", [])
                ],
                random_state=dict(self.search_state.get("random_state", {})),
            )

        return atlas.ReconstructionResult(
            reconstruction=reconstruction,
            residual=residual,
            coefficients=coefficients,
            active_specs=specs,
            active_atoms=atoms,
            history=history,
            snapshots={len(specs): reconstruction.copy()},
            residual_norms=residual_norms,
            runtime_seconds=0.0,
            exact_archive_residual=residual.copy(),
            search_state=packet_search_state,
        )

    def resume(
        self,
        additional_packets: int = 8,
        *,
        target_packet_budget: int | None = None,
        method: str | None = None,
        config=None,
    ):
        """Continue the packet search represented by this model."""
        from .api import resume_model

        return resume_model(
            self,
            config,
            additional_packets=additional_packets,
            target_packet_budget=target_packet_budget,
            method=method,
        )

    def summary(self) -> dict[str, Any]:
        return {
            "format": FORMAT_NAME,
            "schema_version": self.schema_version,
            "current_schema_version": SCHEMA_VERSION,
            "library_version": __version__,
            "shape": list(self.shape),
            "selected_method": self.selected_method,
            "parameter_count": self.parameter_count,
            "packet_count": self.packet_count,
            "residual_storage": self.residual_storage,
            "residual_threshold": self.residual_threshold,
            "has_residual_closure": self.has_residual_closure,
            "has_exact_closure": self.has_exact_closure,
            "includes_input": self.input_image is not None,
            "exact_identity_error": self.exact_identity_error,
            "supports_resume": self.supports_resume,
            "resume_state_quality": self.resume_state_quality,
            "metrics": dict(self.metrics),
            "candidate_rmse": dict(self.candidate_rmse),
            "component_counts": {
                "packet_specs": len(self.packet_specs),
                "packet_history": len(self.packet_history),
                "singular_modes": len(self.singular_modes),
                "lagrange_tree_selections": len(self.lagrange_tree_selections),
                "exact_tree_selections": len(self.exact_tree_selections),
                "exact_frontier_states": len(self.exact_frontier),
                "portfolio_trials": len(self.portfolio_trials),
                "replacement_blocks": len(self.replacement_blocks),
                "search_candidates": len(self.search_state.get("candidate_specs", [])),
                "search_seed_masks": 0 if self.search_seed_ids is None else len(self.search_seed_ids),
            },
            "config": _json_safe(self.config),
            "provenance": _json_safe(self.provenance),
        }

    def packet_table(self) -> list[dict[str, Any]]:
        history_by_key = {str(row.get("spec_key")): row for row in self.packet_history}
        rows: list[dict[str, Any]] = []
        for index, spec in enumerate(self.packet_specs):
            row = {"index": index, **spec}
            history = history_by_key.get(str(spec.get("key")))
            if history is not None:
                row.update(
                    {
                        f"selection_{key}": value
                        for key, value in history.items()
                        if key not in {"spec_key", "kind", "parent", "depth", "complexity"}
                    }
                )
            rows.append(row)
        return rows

    def tree_table(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for optimizer, selections in (
            ("lagrange", self.lagrange_tree_selections),
            ("exact_budget", self.exact_tree_selections),
        ):
            for index, selection in enumerate(selections):
                rows.append({"optimizer": optimizer, "index": index, **selection})
        return rows

    def verify(self) -> dict[str, Any]:
        errors: list[str] = []
        if not _nonnegative_integer(self.schema_version) or self.schema_version not in SUPPORTED_SCHEMA_VERSIONS:
            errors.append(f"unsupported schema version: {self.schema_version}")
        shape = _validate_closure_arrays(self, errors)
        _validate_metrics("candidate_rmse", self.candidate_rmse, errors)
        for name in ("config", "search_state", "provenance"):
            if not isinstance(getattr(self, name), dict):
                errors.append(f"{name} must be an object")
        for name in ("packet_specs", "packet_history", "singular_modes", "lagrange_tree_selections",
                     "exact_tree_selections", "exact_frontier", "portfolio_trials", "replacement_blocks"):
            records = getattr(self, name)
            if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
                errors.append(f"{name} must be a list of objects")
        _validate_packet_records(self.packet_specs, errors)
        if isinstance(self.search_state, dict) and "exact" in self.search_state and not isinstance(self.search_state["exact"], bool):
            errors.append("search_state.exact must be a boolean")
        if shape is not None:
            if self.core_atoms is not None:
                atoms = _validate_array("core_atoms", self.core_atoms, errors, ndim=3)
                if atoms is not None and atoms.shape[1:] != shape[:2]:
                    errors.append("core_atoms have the wrong spatial shape")
                if atoms is not None and isinstance(self.packet_specs, list) and len(atoms) != len(self.packet_specs):
                    errors.append("core atom count does not match packet specification count")
            if self.core_coefficients is not None:
                if self.core_atoms is None:
                    errors.append("core coefficients require stored core atoms")
                else:
                    count = self.core_atoms.shape[0] if isinstance(self.core_atoms, np.ndarray) and self.core_atoms.ndim else 0
                    _validate_array("core_coefficients", self.core_coefficients, errors, shape=(count, shape[2]))
            for name in ("singular_directions", "lagrange_directions", "exact_directions", "replacement_directions"):
                value = getattr(self, name)
                if value is not None:
                    directions = _validate_array(name, value, errors, ndim=4)
                    if directions is not None and directions.shape[1:] != shape:
                        errors.append(f"{name} have the wrong image shape")
            if self.singular_coefficients is not None:
                # Singular completion stores coefficients for the core basis and
                # its added directions, so their length is not the mode count.
                _validate_array("singular_coefficients", self.singular_coefficients, errors, ndim=1)
            if self.search_seed_ids is not None or self.search_seed_masks is not None:
                if self.search_seed_ids is None or self.search_seed_masks is None:
                    errors.append("search seed ids and masks must be stored together")
                else:
                    seed_ids = _validate_array("search_seed_ids", self.search_seed_ids, errors, ndim=1, integer=True)
                    masks = _validate_array("search_seed_masks", self.search_seed_masks, errors, ndim=3)
                    if seed_ids is not None and (np.any(seed_ids < 0) or len(np.unique(seed_ids)) != len(seed_ids)):
                        errors.append("search seed ids must be unique and nonnegative")
                    if masks is not None and masks.shape[1:] != shape[:2]:
                        errors.append("search seed masks have the wrong spatial shape")
                    if seed_ids is not None and masks is not None and len(seed_ids) != len(masks):
                        errors.append("search seed id and mask counts differ")
        if isinstance(self.search_state, dict) and self.search_state.get("exact"):
            self._verify_search_state(shape, errors)
        # Decode only after structural validation. A malformed sparse residual
        # should produce a failed report, never an indexing exception.
        if not errors:
            identity_error = self.exact_identity_error
            if identity_error is not None and (not np.isfinite(identity_error) or identity_error > 1e-10):
                errors.append(f"exact closure identity error is too large: {identity_error:.3e}")
        summary = self.summary() if not errors else {
            "format": FORMAT_NAME,
            "schema_version": self.schema_version,
            "shape": list(np.shape(self.reconstruction)),
        }
        return {"passed": not errors, "errors": errors, "summary": summary}

    def _verify_search_state(self, shape: tuple[int, int, int] | None, errors: list[str]) -> None:
        if self.search_seed_ids is None or self.search_seed_masks is None:
            errors.append("exact resume state requires search seed ids and masks")
            return
        if not isinstance(self.search_seed_ids, np.ndarray) or self.search_seed_ids.ndim != 1:
            return
        seeds = set(int(value) for value in self.search_seed_ids) if np.issubdtype(self.search_seed_ids.dtype, np.integer) else set()
        state = self.search_state
        next_id = state.get("next_seed_id")
        if not _nonnegative_integer(next_id) or next_id <= max(seeds, default=-1):
            errors.append("exact resume next_seed_id must exceed every stored seed id")
        selected = state.get("selected_seed_ids", [])
        if not isinstance(selected, list) or any(not _nonnegative_integer(value) or value not in seeds for value in selected):
            errors.append("exact resume selected_seed_ids must reference stored seeds")
        elif len(set(selected)) != len(selected):
            errors.append("exact resume selected_seed_ids contain duplicates")
        metadata = state.get("seed_metadata", {})
        if not isinstance(metadata, dict):
            errors.append("exact resume seed_metadata must be an object")
        else:
            for seed_id, record in metadata.items():
                try:
                    known = int(seed_id) in seeds
                except (TypeError, ValueError, OverflowError):
                    known = False
                if not known or not isinstance(record, dict):
                    errors.append("exact resume seed_metadata must reference stored seeds and object records")
                    break
        candidates = state.get("candidate_specs")
        _validate_packet_records(candidates, errors, label="exact resume candidate_specs")
        if not isinstance(candidates, list) or any(not isinstance(record, dict) for record in candidates):
            errors.append("exact resume candidate_specs must be a list of objects")
        else:
            for record in candidates:
                try:
                    spec = _packet_spec_from_record(record)
                    if not isinstance(record.get("kind"), str) or not isinstance(record.get("params", []), (list, tuple)):
                        raise ValueError("invalid packet specification")
                    if not _nonnegative_integer(record.get("depth", 0)) or not np.isfinite(spec.complexity) or spec.complexity <= 0:
                        raise ValueError("invalid packet depth or complexity")
                    if record.get("key", spec.key) != spec.key:
                        raise ValueError("packet key does not match its specification")
                    if spec.kind in {"mask", "morph", "affine", "radial", "masked_poly", "masked_dct", "soft_mask", "edge_ribbon"}:
                        if not spec.params or not _nonnegative_integer(spec.params[0]) or spec.params[0] not in seeds:
                            raise ValueError("packet references an absent seed")
                    if spec.kind == "combine" and (len(spec.params) != 3 or any(not _nonnegative_integer(value) or value not in seeds for value in spec.params[:2])):
                        raise ValueError("combined packet references an absent seed")
                except (KeyError, TypeError, ValueError, OverflowError):
                    errors.append("exact resume candidate_specs contain an invalid packet specification")
                    break
        leaves = state.get("quadtree_leaves", [])
        if not isinstance(leaves, list):
            errors.append("exact resume quadtree_leaves must be a list")
        else:
            for rectangle in leaves:
                valid = isinstance(rectangle, (list, tuple)) and len(rectangle) == 4 and all(_nonnegative_integer(value) for value in rectangle)
                if valid and shape is not None:
                    y0, x0, y1, x1 = rectangle
                    valid = 0 <= y0 < y1 <= shape[0] and 0 <= x0 < x1 <= shape[1]
                if not valid:
                    errors.append("exact resume quadtree leaves are invalid or outside the image")
                    break
        random_state = state.get("random_state")
        try:
            if not isinstance(random_state, dict):
                raise ValueError("random_state must be an object")
            generator = np.random.PCG64()
            generator.state = random_state
        except (TypeError, ValueError, KeyError, OverflowError):
            errors.append("exact resume random_state is invalid")

    def _arrays(self) -> dict[str, np.ndarray]:
        arrays: dict[str, np.ndarray] = {"reconstruction": np.asarray(self.reconstruction, dtype=np.float64)}
        optional = {
            "archive_residual": self.archive_residual,
            "residual_indices": self.residual_indices,
            "residual_values": self.residual_values,
            "input_image": self.input_image,
            "core_atoms": self.core_atoms,
            "core_coefficients": self.core_coefficients,
            "singular_directions": self.singular_directions,
            "singular_coefficients": self.singular_coefficients,
            "lagrange_directions": self.lagrange_directions,
            "exact_directions": self.exact_directions,
            "replacement_directions": self.replacement_directions,
            "search_seed_masks": self.search_seed_masks,
            "search_seed_ids": self.search_seed_ids,
        }
        arrays.update({name: np.asarray(value) for name, value in optional.items() if value is not None})
        return arrays

    def _serialization_payloads(self) -> tuple[dict[str, Any], dict[str, bytes]]:
        verification = self.verify()
        if not verification["passed"]:
            raise ValueError("model validation failed: " + "; ".join(verification["errors"]))
        array_manifest: dict[str, dict[str, Any]] = {}
        payloads: dict[str, bytes] = {}
        for name, value in self._arrays().items():
            payload = _array_payload(value)
            filename = f"arrays/{name}.npy"
            payloads[filename] = payload
            array_manifest[name] = {
                "path": filename,
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "sha256": _sha256(payload),
                "nbytes": int(value.nbytes),
            }
        manifest = {
            "format": FORMAT_NAME,
            "schema_version": SCHEMA_VERSION,
            "library_version": __version__,
            "selected_method": self.selected_method,
            "parameter_count": self.parameter_count,
            "packet_count": self.packet_count,
            "residual_storage": self.residual_storage,
            "residual_threshold": self.residual_threshold,
            "config": _json_safe(self.config),
            "metrics": _json_safe(self.metrics),
            "candidate_rmse": _json_safe(self.candidate_rmse),
            "packet_specs": _json_safe(self.packet_specs),
            "packet_history": _json_safe(self.packet_history),
            "singular_modes": _json_safe(self.singular_modes),
            "lagrange_tree_selections": _json_safe(self.lagrange_tree_selections),
            "exact_tree_selections": _json_safe(self.exact_tree_selections),
            "exact_frontier": _json_safe(self.exact_frontier),
            "portfolio_trials": _json_safe(self.portfolio_trials),
            "replacement_blocks": _json_safe(self.replacement_blocks),
            "search_state": _json_safe(self.search_state),
            "provenance": _json_safe(self.provenance),
            "arrays": array_manifest,
        }
        return manifest, payloads

    def to_bytes(self) -> bytes:
        manifest, payloads = self._serialization_payloads()
        manifest_payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr("manifest.json", manifest_payload)
            for filename, payload in payloads.items():
                archive.writestr(filename, payload)
        return buffer.getvalue()

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        if destination.suffix.lower() != ".amspd":
            destination = destination.with_suffix(destination.suffix + ".amspd" if destination.suffix else ".amspd")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(self.to_bytes())
        return destination

    @classmethod
    def from_bytes(cls, payload: bytes) -> AMSpdModel:
        try:
            with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
                manifest = _read_manifest(archive, FORMAT_NAME, SUPPORTED_SCHEMA_VERSIONS)
                schema_version = manifest["schema_version"]
                arrays = _read_manifest_arrays(archive, manifest)
        except (zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, EOFError) as exc:
            raise ValueError(f"invalid AM-SPD model archive: {exc}") from exc
        if "reconstruction" not in arrays:
            raise ValueError("AM-SPD model is missing its reconstruction")
        model = cls(
            reconstruction=np.asarray(arrays["reconstruction"], dtype=np.float64),
            selected_method=str(manifest["selected_method"]),
            parameter_count=int(manifest["parameter_count"]),
            packet_count=int(manifest["packet_count"]),
            config=dict(manifest.get("config", {})),
            metrics={str(key): float(value) for key, value in manifest.get("metrics", {}).items()},
            candidate_rmse={str(key): float(value) for key, value in manifest.get("candidate_rmse", {}).items()},
            schema_version=schema_version,
            residual_storage=str(manifest.get("residual_storage", "none")),  # type: ignore[arg-type]
            residual_threshold=float(manifest.get("residual_threshold", 0.0)),
            archive_residual=np.asarray(arrays["archive_residual"], dtype=np.float64) if "archive_residual" in arrays else None,
            residual_indices=np.asarray(arrays["residual_indices"], dtype=np.int64) if "residual_indices" in arrays else None,
            residual_values=np.asarray(arrays["residual_values"], dtype=np.float64) if "residual_values" in arrays else None,
            input_image=np.asarray(arrays["input_image"], dtype=np.float64) if "input_image" in arrays else None,
            core_atoms=np.asarray(arrays["core_atoms"], dtype=np.float64) if "core_atoms" in arrays else None,
            core_coefficients=np.asarray(arrays["core_coefficients"], dtype=np.float64) if "core_coefficients" in arrays else None,
            singular_directions=np.asarray(arrays["singular_directions"], dtype=np.float64) if "singular_directions" in arrays else None,
            singular_coefficients=np.asarray(arrays["singular_coefficients"], dtype=np.float64) if "singular_coefficients" in arrays else None,
            lagrange_directions=np.asarray(arrays["lagrange_directions"], dtype=np.float64) if "lagrange_directions" in arrays else None,
            exact_directions=np.asarray(arrays["exact_directions"], dtype=np.float64) if "exact_directions" in arrays else None,
            replacement_directions=np.asarray(arrays["replacement_directions"], dtype=np.float64) if "replacement_directions" in arrays else None,
            search_seed_masks=np.asarray(arrays["search_seed_masks"], dtype=np.float64) if "search_seed_masks" in arrays else None,
            search_seed_ids=np.asarray(arrays["search_seed_ids"], dtype=np.int64) if "search_seed_ids" in arrays else None,
            packet_specs=list(manifest.get("packet_specs", [])),
            packet_history=list(manifest.get("packet_history", [])),
            singular_modes=list(manifest.get("singular_modes", [])),
            lagrange_tree_selections=list(manifest.get("lagrange_tree_selections", [])),
            exact_tree_selections=list(manifest.get("exact_tree_selections", [])),
            exact_frontier=list(manifest.get("exact_frontier", [])),
            portfolio_trials=list(manifest.get("portfolio_trials", [])),
            replacement_blocks=list(manifest.get("replacement_blocks", [])),
            search_state=dict(manifest.get("search_state", {})),
            provenance=dict(manifest.get("provenance", {})),
        )
        verification = model.verify()
        if not verification["passed"]:
            raise ValueError("loaded model failed validation: " + "; ".join(verification["errors"]))
        return model

    @classmethod
    def load(cls, path: str | Path) -> AMSpdModel:
        return cls.from_bytes(Path(path).read_bytes())
