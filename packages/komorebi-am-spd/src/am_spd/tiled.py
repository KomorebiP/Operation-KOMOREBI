from __future__ import annotations

import io
import json
import time
import zipfile
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

from . import atlas
from ._version import __version__
from .api import AMSpdConfig, AMSpdResult, reconstruct
from .model import (
    AMSpdModel,
    DecodeMode,
    ResidualStorage,
    _array_payload,
    _encode_residual,
    _json_safe,
    _nonnegative_integer,
    _read_manifest,
    _read_manifest_arrays,
    _sha256,
    _validate_closure_arrays,
)

Array = NDArray[np.float64]
BlendMode = Literal["cosine", "linear", "uniform"]

TILED_FORMAT_NAME = "komorebi-am-spd-tiled-model"
TILED_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class TiledConfig:
    """Spatial tiling and overlap-blending configuration."""

    tile_size: int = 128
    overlap: int = 16
    blend: BlendMode = "cosine"
    workers: int = 1

    def __post_init__(self) -> None:
        if not _nonnegative_integer(self.tile_size) or self.tile_size < 8:
            raise ValueError("tile_size must be at least 8")
        if not _nonnegative_integer(self.overlap):
            raise ValueError("overlap must be nonnegative")
        if self.overlap >= self.tile_size:
            raise ValueError("overlap must be smaller than tile_size")
        if self.blend not in {"cosine", "linear", "uniform"}:
            raise ValueError(f"unsupported blend mode: {self.blend}")
        if not _nonnegative_integer(self.workers) or self.workers < 1:
            raise ValueError("workers must be at least 1")


@dataclass(frozen=True)
class TileRegion:
    index: int
    y0: int
    x0: int
    y1: int
    x1: int
    top_overlap: int = 0
    bottom_overlap: int = 0
    left_overlap: int = 0
    right_overlap: int = 0

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    def record(self) -> dict[str, int]:
        return {key: int(value) for key, value in asdict(self).items()}


@dataclass
class TiledAMSpdResult:
    input_image: Array
    reconstruction: Array
    archive_residual: Array
    config: AMSpdConfig
    tiled_config: TiledConfig
    regions: list[TileRegion]
    tile_results: list[AMSpdResult]
    metrics: dict[str, float]
    runtime_seconds: float

    @property
    def exact_identity_error(self) -> float:
        return float(np.max(np.abs(self.input_image - (self.reconstruction + self.archive_residual))))

    @property
    def parameter_count(self) -> int:
        return int(sum(result.parameter_count for result in self.tile_results))

    @property
    def packet_count(self) -> int:
        return int(sum(result.packet_count for result in self.tile_results))

    def bounded_reconstruction(self) -> Array:
        return atlas.bounded_synthesis(self.reconstruction)

    def exact_reconstruction(self) -> Array:
        return self.reconstruction + self.archive_residual

    def summary(self) -> dict[str, Any]:
        return {
            "mode": "tiled",
            "shape": list(self.input_image.shape),
            "tile_count": len(self.regions),
            "parameter_count": self.parameter_count,
            "packet_count": self.packet_count,
            "exact_identity_error": self.exact_identity_error,
            "runtime_seconds": self.runtime_seconds,
            "metrics": {key: float(value) for key, value in self.metrics.items()},
            "config": asdict(self.config),
            "tiled_config": asdict(self.tiled_config),
            "tiles": [
                {
                    "region": region.record(),
                    "summary": result.summary(),
                }
                for region, result in zip(self.regions, self.tile_results, strict=True)
            ],
        }

    def to_model(
        self,
        *,
        residual_storage: ResidualStorage = "sparse",
        residual_threshold: float = 0.0,
        include_input: bool = False,
        include_tile_models: bool = True,
        include_atoms: bool = True,
        include_directions: bool = True,
        provenance: dict[str, Any] | None = None,
    ) -> TiledAMSpdModel:
        return TiledAMSpdModel.from_result(
            self,
            residual_storage=residual_storage,
            residual_threshold=residual_threshold,
            include_input=include_input,
            include_tile_models=include_tile_models,
            include_atoms=include_atoms,
            include_directions=include_directions,
            provenance=provenance,
        )

    def save_model(self, path: str | Path, **kwargs: Any) -> Path:
        return self.to_model(**kwargs).save(path)


@dataclass
class TiledAMSpdModel:
    reconstruction: Array
    config: dict[str, Any]
    tiled_config: dict[str, Any]
    metrics: dict[str, float]
    parameter_count: int
    packet_count: int
    tile_records: list[dict[str, Any]]
    residual_storage: ResidualStorage = "sparse"
    residual_threshold: float = 0.0
    archive_residual: Array | None = None
    residual_indices: NDArray[np.int64] | None = None
    residual_values: Array | None = None
    input_image: Array | None = None
    tile_models: list[AMSpdModel] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    schema_version: int = TILED_SCHEMA_VERSION

    @classmethod
    def from_result(
        cls,
        result: TiledAMSpdResult,
        *,
        residual_storage: ResidualStorage = "sparse",
        residual_threshold: float = 0.0,
        include_input: bool = False,
        include_tile_models: bool = True,
        include_atoms: bool = True,
        include_directions: bool = True,
        provenance: dict[str, Any] | None = None,
    ) -> TiledAMSpdModel:
        dense, indices, values, effective_threshold = _encode_residual(
            result.archive_residual,
            residual_storage,
            residual_threshold,
        )
        tile_records: list[dict[str, Any]] = []
        tile_models: list[AMSpdModel] = []
        for region, tile_result in zip(result.regions, result.tile_results, strict=True):
            tile_records.append({"region": region.record(), "summary": tile_result.summary()})
            if include_tile_models:
                tile_models.append(
                    AMSpdModel.from_result(
                        tile_result,
                        residual_storage="sparse",
                        residual_threshold=0.0,
                        include_input=include_input,
                        include_atoms=include_atoms,
                        include_directions=include_directions,
                        provenance={"mode": "embedded-tile", "region": region.record()},
                    )
                )
        return cls(
            reconstruction=np.asarray(result.reconstruction, dtype=np.float64).copy(),
            config=_json_safe(asdict(result.config)),
            tiled_config=_json_safe(asdict(result.tiled_config)),
            metrics={key: float(value) for key, value in result.metrics.items()},
            parameter_count=result.parameter_count,
            packet_count=result.packet_count,
            tile_records=tile_records,
            residual_storage=residual_storage,
            residual_threshold=effective_threshold,
            archive_residual=dense,
            residual_indices=indices,
            residual_values=values,
            input_image=np.asarray(result.input_image, dtype=np.float64).copy() if include_input else None,
            tile_models=tile_models,
            provenance=_json_safe(provenance or {}),
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
        return (self.input_image is not None or self.has_exact_closure) and bool(self.tile_models) and len(self.tile_models) == len(self.tile_records) and all(
            model.supports_resume for model in self.tile_models
        )

    @property
    def resume_state_quality(self) -> str:
        if not self.supports_resume:
            return "unavailable"
        qualities = {model.resume_state_quality for model in self.tile_models}
        if qualities == {"exact"}:
            return "exact"
        if qualities <= {"exact", "frontier-exact"}:
            return "frontier-exact"
        return "warm"

    def resume(
        self,
        additional_packets: int = 8,
        *,
        target_packet_budget: int | None = None,
        method: str | None = None,
        config: AMSpdConfig | None = None,
        workers: int | None = None,
    ) -> TiledAMSpdResult:
        """Continue every embedded tile checkpoint and reblend the image."""

        return resume_tiled_model(
            self,
            additional_packets=additional_packets,
            target_packet_budget=target_packet_budget,
            method=method,
            config=config,
            workers=workers,
        )

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
        raise ValueError("this tiled model does not contain residual closure data")

    def decode(self, mode: DecodeMode = "bounded") -> Array:
        if mode == "raw":
            return np.asarray(self.reconstruction, dtype=np.float64).copy()
        if mode == "bounded":
            return atlas.bounded_synthesis(self.reconstruction)
        if mode == "exact":
            if not self.has_exact_closure:
                raise ValueError("this tiled model does not contain an unthresholded exact residual closure")
            return np.asarray(self.reconstruction, dtype=np.float64) + self.residual()
        raise ValueError(f"unsupported decode mode: {mode}")

    @property
    def exact_identity_error(self) -> float | None:
        if self.input_image is None or not self.has_exact_closure:
            return None
        return float(np.max(np.abs(self.input_image - self.decode("exact"))))

    def summary(self) -> dict[str, Any]:
        return {
            "format": TILED_FORMAT_NAME,
            "schema_version": self.schema_version,
            "library_version": __version__,
            "shape": list(self.shape),
            "tile_count": len(self.tile_records),
            "embedded_tile_models": len(self.tile_models),
            "parameter_count": self.parameter_count,
            "packet_count": self.packet_count,
            "residual_storage": self.residual_storage,
            "residual_threshold": self.residual_threshold,
            "has_exact_closure": self.has_exact_closure,
            "includes_input": self.input_image is not None,
            "supports_resume": self.supports_resume,
            "resume_state_quality": self.resume_state_quality,
            "exact_identity_error": self.exact_identity_error,
            "metrics": dict(self.metrics),
            "config": _json_safe(self.config),
            "tiled_config": _json_safe(self.tiled_config),
            "provenance": _json_safe(self.provenance),
        }

    def tile_table(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for index, record in enumerate(self.tile_records):
            region = dict(record.get("region", {}))
            summary = dict(record.get("summary", {}))
            rows.append(
                {
                    "index": index,
                    **region,
                    "selected_method": summary.get("selected_method"),
                    "parameter_count": summary.get("parameter_count"),
                    "packet_count": summary.get("packet_count"),
                    "rmse": dict(summary.get("metrics", {})).get("rmse"),
                }
            )
        return rows

    def verify(self) -> dict[str, Any]:
        errors: list[str] = []
        if self.schema_version != TILED_SCHEMA_VERSION:
            errors.append(f"unsupported tiled-model schema version: {self.schema_version}")
        shape = _validate_closure_arrays(self, errors)
        try:
            TiledConfig(**self.tiled_config)
        except (TypeError, ValueError) as exc:
            errors.append(f"invalid tiled configuration: {exc}")
        if not isinstance(self.config, dict) or not isinstance(self.provenance, dict):
            errors.append("config and provenance must be objects")
        if not isinstance(self.tile_records, list):
            errors.append("tile_records must be a list")
        if not isinstance(self.tile_models, list) or any(not isinstance(model, AMSpdModel) for model in self.tile_models):
            errors.append("tile_models must be a list of AMSpdModel objects")
        if shape is None or not isinstance(self.tile_records, list) or not isinstance(self.tile_models, list):
            return {"passed": False, "errors": errors, "summary": {"format": TILED_FORMAT_NAME}}

        coverage = np.zeros(self.shape[:2], dtype=bool) if self.reconstruction.ndim == 3 else None
        seen_indices: set[int] = set()
        region_records: list[dict[str, int] | None] = []
        required = {
            "index",
            "y0",
            "x0",
            "y1",
            "x1",
            "top_overlap",
            "bottom_overlap",
            "left_overlap",
            "right_overlap",
        }
        for position, record in enumerate(self.tile_records):
            raw = record.get("region") if isinstance(record, dict) else None
            if not isinstance(raw, dict) or not required.issubset(raw):
                errors.append(f"tile record {position} has an incomplete region")
                region_records.append(None)
                continue
            try:
                if any(not _nonnegative_integer(raw[key]) for key in required):
                    raise ValueError("region data must be nonnegative integers")
                region = {key: int(raw[key]) for key in required}
            except (TypeError, ValueError):
                errors.append(f"tile record {position} contains non-integer region data")
                region_records.append(None)
                continue
            region_records.append(region)
            index = region["index"]
            if index in seen_indices:
                errors.append(f"tile index {index} is duplicated")
            seen_indices.add(index)
            y0, x0, y1, x1 = region["y0"], region["x0"], region["y1"], region["x1"]
            if not (0 <= y0 < y1 <= self.shape[0] and 0 <= x0 < x1 <= self.shape[1]):
                errors.append(f"tile record {position} is outside the image bounds")
                continue
            height, width = y1 - y0, x1 - x0
            overlaps = (
                region["top_overlap"],
                region["bottom_overlap"],
                region["left_overlap"],
                region["right_overlap"],
            )
            if any(value < 0 for value in overlaps):
                errors.append(f"tile record {position} has a negative overlap")
            if overlaps[0] > height or overlaps[1] > height or overlaps[2] > width or overlaps[3] > width:
                errors.append(f"tile record {position} has an overlap larger than its support")
            if coverage is not None:
                coverage[y0:y1, x0:x1] = True
        if coverage is not None and self.tile_records and not bool(np.all(coverage)):
            errors.append("tile records do not cover the full reconstruction")
        if not self.tile_records:
            errors.append("tiled model has no tile records")

        record_parameter_counts: list[int] = []
        record_packet_counts: list[int] = []
        for position, record in enumerate(self.tile_records):
            summary = record.get("summary", {}) if isinstance(record, dict) else {}
            if not isinstance(summary, dict):
                errors.append(f"tile record {position} has an invalid summary")
                continue
            for key, destination in (
                ("parameter_count", record_parameter_counts),
                ("packet_count", record_packet_counts),
            ):
                value = summary.get(key)
                if value is None:
                    continue
                try:
                    if not _nonnegative_integer(value):
                        raise ValueError("counts must be nonnegative integers")
                    parsed = int(value)
                except (TypeError, ValueError):
                    errors.append(f"tile record {position} has an invalid {key}")
                    continue
                if parsed < 0:
                    errors.append(f"tile record {position} has a negative {key}")
                destination.append(parsed)
        if len(record_parameter_counts) == len(self.tile_records) and sum(record_parameter_counts) != self.parameter_count:
            errors.append("parameter_count does not match the tile-record total")
        if len(record_packet_counts) == len(self.tile_records) and sum(record_packet_counts) != self.packet_count:
            errors.append("packet_count does not match the tile-record total")

        if self.tile_models and len(self.tile_models) != len(self.tile_records):
            errors.append("embedded tile-model count differs from tile-record count")
        for position, model in enumerate(self.tile_models):
            if not isinstance(model, AMSpdModel):
                continue
            verification = model.verify()
            if not verification["passed"]:
                errors.append(f"embedded tile model {position} failed validation")
            if verification["passed"] and position < len(region_records) and region_records[position] is not None:
                region = region_records[position]
                assert region is not None
                expected_shape = (
                    region["y1"] - region["y0"],
                    region["x1"] - region["x0"],
                    self.shape[2],
                )
                if model.shape != expected_shape:
                    errors.append(
                        f"embedded tile model {position} has shape {model.shape}, expected {expected_shape}"
                    )
        if self.tile_models and all(
            isinstance(model, AMSpdModel) and _nonnegative_integer(model.parameter_count) and isinstance(model.packet_specs, list)
            for model in self.tile_models
        ):
            embedded_parameter_count = sum(model.parameter_count for model in self.tile_models)
            embedded_packet_count = sum(len(model.packet_specs) for model in self.tile_models)
            if embedded_parameter_count != self.parameter_count:
                errors.append("parameter_count does not match the embedded tile-model total")
            if embedded_packet_count != self.packet_count:
                errors.append("packet_count does not match the embedded tile-model total")

        if not errors:
            identity_error = self.exact_identity_error
            if identity_error is not None and (not np.isfinite(identity_error) or identity_error > 1e-10):
                errors.append(f"exact closure identity error is too large: {identity_error:.3e}")
        summary = self.summary() if not errors else {"format": TILED_FORMAT_NAME, "shape": list(shape)}
        return {"passed": not errors, "errors": errors, "summary": summary}

    def _arrays(self) -> dict[str, np.ndarray]:
        arrays: dict[str, np.ndarray] = {"reconstruction": np.asarray(self.reconstruction, dtype=np.float64)}
        optional = {
            "archive_residual": self.archive_residual,
            "residual_indices": self.residual_indices,
            "residual_values": self.residual_values,
            "input_image": self.input_image,
        }
        arrays.update({name: np.asarray(value) for name, value in optional.items() if value is not None})
        return arrays

    def to_bytes(self) -> bytes:
        verification = self.verify()
        if not verification["passed"]:
            raise ValueError("tiled model validation failed: " + "; ".join(verification["errors"]))
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
            }
        tile_manifest: list[dict[str, Any]] = []
        for index, model in enumerate(self.tile_models):
            payload = model.to_bytes()
            filename = f"tiles/tile_{index:05d}.amspd"
            payloads[filename] = payload
            tile_manifest.append({"path": filename, "sha256": _sha256(payload), "nbytes": len(payload)})
        manifest = {
            "format": TILED_FORMAT_NAME,
            "schema_version": TILED_SCHEMA_VERSION,
            "library_version": __version__,
            "config": _json_safe(self.config),
            "tiled_config": _json_safe(self.tiled_config),
            "metrics": _json_safe(self.metrics),
            "parameter_count": self.parameter_count,
            "packet_count": self.packet_count,
            "tile_records": _json_safe(self.tile_records),
            "residual_storage": self.residual_storage,
            "residual_threshold": self.residual_threshold,
            "provenance": _json_safe(self.provenance),
            "arrays": array_manifest,
            "tile_models": tile_manifest,
        }
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr("manifest.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
            for filename, payload in payloads.items():
                archive.writestr(filename, payload)
        return buffer.getvalue()

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        if destination.suffix.lower() != ".amspdt":
            destination = destination.with_suffix(destination.suffix + ".amspdt" if destination.suffix else ".amspdt")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(self.to_bytes())
        return destination

    @classmethod
    def from_bytes(cls, payload: bytes) -> TiledAMSpdModel:
        try:
            with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
                manifest = _read_manifest(archive, TILED_FORMAT_NAME, {TILED_SCHEMA_VERSION})
                arrays = _read_manifest_arrays(archive, manifest)
                names = set(archive.namelist())
                tile_models: list[AMSpdModel] = []
                for record in manifest.get("tile_models", []):
                    if not {"path", "sha256"}.issubset(record):
                        raise ValueError("embedded tile-model metadata is incomplete")
                    filename = record["path"]
                    if not isinstance(filename, str) or filename not in names:
                        raise ValueError(f"embedded tile model is missing: {filename}")
                    tile_payload = archive.read(filename)
                    if _sha256(tile_payload) != record["sha256"]:
                        raise ValueError(f"embedded tile model checksum mismatch: {filename}")
                    if "nbytes" in record and record["nbytes"] != len(tile_payload):
                        raise ValueError(f"embedded tile-model byte count mismatch: {filename}")
                    tile_models.append(AMSpdModel.from_bytes(tile_payload))
        except (zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, EOFError) as exc:
            raise ValueError(f"invalid tiled AM-SPD model archive: {exc}") from exc
        if "reconstruction" not in arrays:
            raise ValueError("tiled AM-SPD model is missing its reconstruction")
        model = cls(
            reconstruction=np.asarray(arrays["reconstruction"], dtype=np.float64),
            config=dict(manifest.get("config", {})),
            tiled_config=dict(manifest.get("tiled_config", {})),
            metrics={str(key): float(value) for key, value in manifest.get("metrics", {}).items()},
            parameter_count=int(manifest.get("parameter_count", 0)),
            packet_count=int(manifest.get("packet_count", 0)),
            tile_records=list(manifest.get("tile_records", [])),
            residual_storage=str(manifest.get("residual_storage", "none")),  # type: ignore[arg-type]
            residual_threshold=float(manifest.get("residual_threshold", 0.0)),
            archive_residual=np.asarray(arrays["archive_residual"], dtype=np.float64) if "archive_residual" in arrays else None,
            residual_indices=np.asarray(arrays["residual_indices"], dtype=np.int64) if "residual_indices" in arrays else None,
            residual_values=np.asarray(arrays["residual_values"], dtype=np.float64) if "residual_values" in arrays else None,
            input_image=np.asarray(arrays["input_image"], dtype=np.float64) if "input_image" in arrays else None,
            tile_models=tile_models,
            provenance=dict(manifest.get("provenance", {})),
        )
        verification = model.verify()
        if not verification["passed"]:
            raise ValueError("loaded tiled model failed validation: " + "; ".join(verification["errors"]))
        return model

    @classmethod
    def load(cls, path: str | Path) -> TiledAMSpdModel:
        return cls.from_bytes(Path(path).read_bytes())


def _axis_starts(length: int, tile_size: int, overlap: int) -> list[int]:
    effective = min(length, tile_size)
    if length <= effective:
        return [0]
    stride = effective - overlap
    if stride <= 0:
        raise ValueError("effective tile stride must be positive")
    starts = list(range(0, length - effective + 1, stride))
    final_start = length - effective
    if starts[-1] != final_start:
        starts.append(final_start)
    return starts


def tile_regions(height: int, width: int, config: TiledConfig) -> list[TileRegion]:
    if not _nonnegative_integer(height) or not _nonnegative_integer(width) or height < 8 or width < 8:
        raise ValueError("tiled AM-SPD requires image height and width of at least 8 pixels")
    y_size = min(height, config.tile_size)
    x_size = min(width, config.tile_size)
    y_starts = _axis_starts(height, y_size, min(config.overlap, max(0, y_size - 1)))
    x_starts = _axis_starts(width, x_size, min(config.overlap, max(0, x_size - 1)))
    regions: list[TileRegion] = []
    index = 0
    for yi, y0 in enumerate(y_starts):
        y1 = min(height, y0 + y_size)
        top = max(0, (y_starts[yi - 1] + y_size) - y0) if yi > 0 else 0
        bottom = max(0, y1 - y_starts[yi + 1]) if yi + 1 < len(y_starts) else 0
        for xi, x0 in enumerate(x_starts):
            x1 = min(width, x0 + x_size)
            left = max(0, (x_starts[xi - 1] + x_size) - x0) if xi > 0 else 0
            right = max(0, x1 - x_starts[xi + 1]) if xi + 1 < len(x_starts) else 0
            regions.append(TileRegion(index, y0, x0, y1, x1, top, bottom, left, right))
            index += 1
    return regions


def _ramp(length: int, mode: BlendMode) -> Array:
    if length <= 0:
        return np.empty(0, dtype=np.float64)
    if mode == "uniform":
        return np.ones(length, dtype=np.float64)
    t = (np.arange(length, dtype=np.float64) + 1.0) / (length + 1.0)
    if mode == "linear":
        return t
    return 0.5 - 0.5 * np.cos(np.pi * t)


def blend_window(region: TileRegion, mode: BlendMode) -> Array:
    y = np.ones(region.height, dtype=np.float64)
    x = np.ones(region.width, dtype=np.float64)
    if region.top_overlap:
        y[: region.top_overlap] = _ramp(region.top_overlap, mode)
    if region.bottom_overlap:
        y[-region.bottom_overlap :] = _ramp(region.bottom_overlap, mode)[::-1]
    if region.left_overlap:
        x[: region.left_overlap] = _ramp(region.left_overlap, mode)
    if region.right_overlap:
        x[-region.right_overlap :] = _ramp(region.right_overlap, mode)[::-1]
    return y[:, None] * x[None, :]


def tiled_reconstruct(
    image: Array,
    config: AMSpdConfig | None = None,
    tiled_config: TiledConfig | None = None,
) -> TiledAMSpdResult:
    """Reconstruct a finite image by overlap-blending independent AM-SPD tiles."""

    value = atlas.ensure_image(image)
    settings = config or AMSpdConfig.quick("core")
    tiles = tiled_config or TiledConfig()
    regions = tile_regions(value.shape[0], value.shape[1], tiles)
    started = time.perf_counter()

    def fit(region: TileRegion) -> tuple[int, AMSpdResult]:
        tile = value[region.y0 : region.y1, region.x0 : region.x1]
        tile_settings = replace(settings, random_seed=settings.random_seed + region.index)
        return region.index, reconstruct(tile, tile_settings)

    if tiles.workers == 1:
        indexed = [fit(region) for region in regions]
    else:
        with ThreadPoolExecutor(max_workers=tiles.workers) as executor:
            indexed = list(executor.map(fit, regions))
    result_by_index = {index: result for index, result in indexed}
    tile_results = [result_by_index[region.index] for region in regions]

    accumulator = np.zeros_like(value)
    weight_sum = np.zeros(value.shape[:2], dtype=np.float64)
    for region, result in zip(regions, tile_results, strict=True):
        weight = blend_window(region, tiles.blend)
        accumulator[region.y0 : region.y1, region.x0 : region.x1] += result.reconstruction * weight[..., None]
        weight_sum[region.y0 : region.y1, region.x0 : region.x1] += weight
    if np.any(weight_sum <= 0.0):
        raise RuntimeError("tile blending left uncovered pixels")
    reconstruction = accumulator / weight_sum[..., None]
    residual = value - reconstruction
    runtime = time.perf_counter() - started
    return TiledAMSpdResult(
        input_image=value,
        reconstruction=reconstruction,
        archive_residual=residual,
        config=settings,
        tiled_config=tiles,
        regions=regions,
        tile_results=tile_results,
        metrics=atlas.image_metrics(value, atlas.bounded_synthesis(reconstruction)),
        runtime_seconds=runtime,
    )


def resume_tiled_model(
    model: TiledAMSpdModel | str | Path,
    *,
    additional_packets: int = 8,
    target_packet_budget: int | None = None,
    method: str | None = None,
    config: AMSpdConfig | None = None,
    workers: int | None = None,
) -> TiledAMSpdResult:
    """Continue every embedded tile checkpoint and reblend the image.

    A target packet budget is interpreted per tile. Schema-2 tile checkpoints
    reproduce uninterrupted packet selection when their search settings remain
    unchanged.
    """

    from .api import config_from_mapping, resume_model

    loaded = TiledAMSpdModel.load(model) if isinstance(model, (str, Path)) else model
    if not isinstance(loaded, TiledAMSpdModel):
        raise TypeError("model must be a TiledAMSpdModel or a path to one")
    verification = loaded.verify()
    if not verification["passed"]:
        raise ValueError("tiled model validation failed: " + "; ".join(verification["errors"]))
    if not loaded.supports_resume:
        raise ValueError("tiled model cannot be resumed; save it with embedded tile models")
    if loaded.input_image is not None:
        source = np.asarray(loaded.input_image, dtype=np.float64).copy()
    elif loaded.has_exact_closure:
        source = loaded.decode("exact")
    else:
        raise ValueError("tiled model requires its source image or exact residual closure for continuation")

    regions = [
        TileRegion(**{key: int(value) for key, value in dict(record["region"]).items()})
        for record in loaded.tile_records
    ]
    if len(regions) != len(loaded.tile_models):
        raise ValueError("tile record and embedded-model counts differ")
    base_config = config_from_mapping(loaded.config)
    tiled_config = TiledConfig(**loaded.tiled_config)
    if workers is not None:
        tiled_config = replace(tiled_config, workers=workers)

    def continue_tile(item: tuple[TileRegion, AMSpdModel]) -> tuple[int, AMSpdResult]:
        region, tile_model = item
        tile_settings = None
        if config is not None:
            tile_original = config_from_mapping(tile_model.config)
            seed_offset = tile_original.random_seed - base_config.random_seed
            tile_settings = replace(
                config,
                method=method or config.method,
                random_seed=config.random_seed + seed_offset,
            )
        return region.index, resume_model(
            tile_model,
            tile_settings,
            additional_packets=additional_packets,
            target_packet_budget=target_packet_budget,
            method=method,
        )

    pairs = list(zip(regions, loaded.tile_models, strict=True))
    started = time.perf_counter()
    if tiled_config.workers == 1:
        indexed = [continue_tile(item) for item in pairs]
    else:
        with ThreadPoolExecutor(max_workers=tiled_config.workers) as executor:
            indexed = list(executor.map(continue_tile, pairs))
    by_index = {index: result for index, result in indexed}
    tile_results = [by_index[region.index] for region in regions]

    accumulator = np.zeros_like(source)
    weight_sum = np.zeros(source.shape[:2], dtype=np.float64)
    for region, result in zip(regions, tile_results, strict=True):
        weight = blend_window(region, tiled_config.blend)
        accumulator[region.y0 : region.y1, region.x0 : region.x1] += result.reconstruction * weight[..., None]
        weight_sum[region.y0 : region.y1, region.x0 : region.x1] += weight
    if np.any(weight_sum <= 0.0):
        raise RuntimeError("tile blending left uncovered pixels")
    reconstruction = accumulator / weight_sum[..., None]
    residual = source - reconstruction
    target = target_packet_budget or max(
        len(tile_model.packet_specs) + additional_packets for tile_model in loaded.tile_models
    )
    result_config = replace(
        config or base_config,
        method=method or (config.method if config is not None else base_config.method),
        packet_budget=int(target),
    )
    return TiledAMSpdResult(
        input_image=source,
        reconstruction=reconstruction,
        archive_residual=residual,
        config=result_config,
        tiled_config=tiled_config,
        regions=regions,
        tile_results=tile_results,
        metrics=atlas.image_metrics(source, atlas.bounded_synthesis(reconstruction)),
        runtime_seconds=time.perf_counter() - started,
    )


def archive_format(path: str | Path) -> str:
    try:
        with zipfile.ZipFile(Path(path), "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise ValueError("model archive contains duplicate member names")
            if "manifest.json" not in names:
                raise ValueError("model archive is missing manifest.json")
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            if not isinstance(manifest, dict) or not isinstance(manifest.get("format"), str):
                raise ValueError("model archive manifest must contain a format string")
            return manifest["format"]
    except (zipfile.BadZipFile, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"invalid AM-SPD model archive: {exc}") from exc


def load_model_archive(path: str | Path) -> AMSpdModel | TiledAMSpdModel:
    format_name = archive_format(path)
    if format_name == TILED_FORMAT_NAME:
        return TiledAMSpdModel.load(path)
    if format_name == "komorebi-am-spd-model":
        return AMSpdModel.load(path)
    raise ValueError(f"unsupported model archive format: {format_name or 'unknown'}")


def compare_model_archives(paths: Sequence[str | Path]) -> dict[str, Any]:
    if len(paths) < 2:
        raise ValueError("compare_model_archives requires at least two models")
    loaded = [(Path(path), load_model_archive(path)) for path in paths]
    records: list[dict[str, Any]] = []
    for path, model in loaded:
        summary = model.summary()
        records.append(
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "format": summary["format"],
                "shape": summary["shape"],
                "parameter_count": summary.get("parameter_count"),
                "packet_count": summary.get("packet_count"),
                "has_exact_closure": summary.get("has_exact_closure"),
                "metrics": summary.get("metrics", {}),
            }
        )
    pairwise: list[dict[str, Any]] = []
    for left_index in range(len(loaded)):
        for right_index in range(left_index + 1, len(loaded)):
            left_path, left = loaded[left_index]
            right_path, right = loaded[right_index]
            record: dict[str, Any] = {
                "left": str(left_path),
                "right": str(right_path),
                "same_shape": left.shape == right.shape,
            }
            if left.shape == right.shape:
                raw_delta = left.decode("raw") - right.decode("raw")
                bounded_delta = left.decode("bounded") - right.decode("bounded")
                record.update(
                    {
                        "raw_rmse": float(np.sqrt(np.mean(raw_delta * raw_delta))),
                        "raw_max_abs": float(np.max(np.abs(raw_delta))),
                        "bounded_rmse": float(np.sqrt(np.mean(bounded_delta * bounded_delta))),
                    }
                )
                if left.has_exact_closure and right.has_exact_closure:
                    exact_delta = left.decode("exact") - right.decode("exact")
                    record["exact_rmse"] = float(np.sqrt(np.mean(exact_delta * exact_delta)))
            pairwise.append(record)
    return {"models": records, "pairwise": pairwise}
