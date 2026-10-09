from __future__ import annotations

import csv
import hashlib
import json
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, replace
from numbers import Integral
from pathlib import Path

from ._version import __version__
from .api import AMSpdConfig, reconstruct
from .io import load_image, save_image
from .tiled import TiledConfig, tiled_reconstruct

SUPPORTED_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")


@dataclass(frozen=True)
class BatchRecord:
    index: int
    input: str
    input_sha256: str
    output: str | None
    summary: str | None
    model: str | None
    status: str
    mode: str
    runtime_seconds: float
    selected_method: str | None
    packet_count: int | None
    parameter_count: int | None
    rmse: float | None
    ssim: float | None
    exact_identity_error: float | None
    error: str | None = None
    run_fingerprint: str = ""


@dataclass
class BatchResult:
    input_root: Path
    output_root: Path
    records: list[BatchRecord]
    runtime_seconds: float
    run_fingerprint: str

    @property
    def passed(self) -> bool:
        return all(record.status in {"completed", "skipped"} for record in self.records)

    def summary(self) -> dict[str, object]:
        return {
            "operation": "batch-reconstruction",
            "input_root": str(self.input_root),
            "output_root": str(self.output_root),
            "runtime_seconds": self.runtime_seconds,
            "run_fingerprint": self.run_fingerprint,
            "passed": self.passed,
            "counts": {
                "total": len(self.records),
                "completed": sum(record.status == "completed" for record in self.records),
                "skipped": sum(record.status == "skipped" for record in self.records),
                "failed": sum(record.status == "failed" for record in self.records),
            },
            "records": [asdict(record) for record in self.records],
        }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _matching_summary(path: Path, digest: str, run_fingerprint: str) -> dict[str, object] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError):
        return None
    batch = payload.get("batch") if isinstance(payload, dict) else None
    if (
        isinstance(batch, dict)
        and batch.get("input_sha256") == digest
        and batch.get("run_fingerprint") == run_fingerprint
        and batch.get("mode") in ("single", "tiled")
    ):
        return batch
    return None


def discover_images(
    source: str | Path,
    *,
    recursive: bool = True,
    suffixes: Iterable[str] = SUPPORTED_IMAGE_SUFFIXES,
) -> tuple[Path, list[Path]]:
    root = Path(source).resolve()
    normalized = {suffix.lower() if str(suffix).startswith(".") else f".{str(suffix).lower()}" for suffix in suffixes}
    if root.is_file():
        if root.suffix.lower() not in normalized:
            raise ValueError(f"unsupported image suffix: {root.suffix}")
        return root.parent, [root]
    if not root.is_dir():
        raise FileNotFoundError(root)
    iterator = root.rglob("*") if recursive else root.glob("*")
    paths = sorted(path for path in iterator if path.is_file() and path.suffix.lower() in normalized)
    if not paths:
        raise ValueError(f"no supported image files were found under {root}")
    return root, paths


def _write_csv(path: Path, records: list[BatchRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(asdict(records[0])) if records else list(BatchRecord.__dataclass_fields__)
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(record) for record in records)


def run_batch(
    source: str | Path,
    output_dir: str | Path,
    config: AMSpdConfig | None = None,
    *,
    recursive: bool = True,
    workers: int = 1,
    save_models: bool = False,
    include_input_in_models: bool = False,
    residual_storage: str = "sparse",
    tile_config: TiledConfig | None = None,
    tiled_above: int | None = None,
    save_tile_models: bool = False,
    skip_existing: bool = False,
    fail_fast: bool = False,
) -> BatchResult:
    """Process an image tree and write a machine-readable artifact manifest."""

    if isinstance(workers, bool) or not isinstance(workers, Integral) or workers < 1:
        raise ValueError("workers must be an integer at least 1")
    if tiled_above is not None and (
        isinstance(tiled_above, bool) or not isinstance(tiled_above, Integral) or tiled_above < 8
    ):
        raise ValueError("tiled_above must be an integer at least 8")
    workers = int(workers)
    tiled_above = int(tiled_above) if tiled_above is not None else None
    input_root, paths = discover_images(source, recursive=recursive)
    destination = Path(output_dir).resolve()
    if Path(source).resolve().is_dir():
        if destination == input_root:
            raise ValueError("batch output directory must differ from the source directory")
        if destination.is_relative_to(input_root):
            paths = [path for path in paths if not path.is_relative_to(destination)]
            if not paths:
                raise ValueError(f"no supported image files were found outside the output directory under {input_root}")
    outputs: dict[str, Path] = {}
    for path in paths:
        # The suffix-free layout is retained for existing callers, while paths
        # that would alias on case-insensitive filesystems are rejected upfront.
        output_key = path.relative_to(input_root).with_suffix("").as_posix().casefold()
        if output_key in outputs:
            raise ValueError(f"batch output collision between {outputs[output_key]} and {path}")
        outputs[output_key] = path
    destination.mkdir(parents=True, exist_ok=True)
    settings = config or AMSpdConfig.quick()
    run_specification = {
        "library_version": __version__,
        "config": asdict(settings),
        "recursive": bool(recursive),
        "save_models": bool(save_models),
        "include_input_in_models": bool(include_input_in_models),
        "residual_storage": str(residual_storage),
        "tile_config": asdict(tile_config) if tile_config is not None else None,
        "tiled_above": tiled_above,
        "save_tile_models": bool(save_tile_models),
    }
    run_fingerprint = hashlib.sha256(
        json.dumps(run_specification, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    def process(index_path: tuple[int, Path]) -> BatchRecord:
        index, path = index_path
        relative = path.relative_to(input_root)
        stem = relative.with_suffix("")
        output_path = destination / stem.parent / f"{stem.name}.reconstruction.png"
        summary_path = destination / stem.parent / f"{stem.name}.summary.json"
        model_path = destination / stem.parent / f"{stem.name}.amspd"
        tiled_model_path = destination / stem.parent / f"{stem.name}.amspdt"
        started = time.perf_counter()
        digest = ""
        try:
            digest = _sha256_file(path)
            existing = _matching_summary(summary_path, digest, run_fingerprint) if skip_existing else None
            if existing is not None and output_path.is_file():
                requested_model = None
                if existing["mode"] == "tiled" and (save_models or save_tile_models):
                    requested_model = tiled_model_path
                elif existing["mode"] == "single" and save_models:
                    requested_model = model_path
                if requested_model is None or requested_model.is_file():
                    return BatchRecord(
                        index=index,
                        input=str(path),
                        input_sha256=digest,
                        output=str(output_path),
                        summary=str(summary_path),
                        model=str(requested_model) if requested_model is not None else None,
                        status="skipped",
                        mode="existing",
                        runtime_seconds=0.0,
                        selected_method=None,
                        packet_count=None,
                        parameter_count=None,
                        rmse=None,
                        ssim=None,
                        exact_identity_error=None,
                        run_fingerprint=run_fingerprint,
                    )
            image = load_image(path)
            seed_offset = int.from_bytes(
                hashlib.blake2b(relative.as_posix().encode(), digest_size=4).digest(), "little"
            )
            local_settings = replace(settings, random_seed=int((settings.random_seed + seed_offset) % (2**32 - 1)))
            use_tiles = tile_config is not None and (tiled_above is None or max(image.shape[:2]) > tiled_above)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if use_tiles:
                tiled = tiled_reconstruct(image, local_settings, tile_config)
                save_image(output_path, tiled.bounded_reconstruction())
                model_value: str | None = None
                if save_models or save_tile_models:
                    tiled.save_model(
                        tiled_model_path,
                        residual_storage=residual_storage,
                        include_input=include_input_in_models,
                        include_tile_models=save_tile_models,
                        provenance={
                            "operation": "batch-tiled-reconstruction",
                            "input": str(relative),
                            "input_sha256": digest,
                        },
                    )
                    model_value = str(tiled_model_path)
                payload = {
                    "batch": {
                        "input": str(relative),
                        "input_sha256": digest,
                        "run_fingerprint": run_fingerprint,
                        "mode": "tiled",
                    },
                    "result": tiled.summary(),
                }
                summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                return BatchRecord(
                    index=index,
                    input=str(path),
                    input_sha256=digest,
                    output=str(output_path),
                    summary=str(summary_path),
                    model=model_value,
                    status="completed",
                    mode="tiled",
                    runtime_seconds=time.perf_counter() - started,
                    selected_method=local_settings.method,
                    packet_count=tiled.packet_count,
                    parameter_count=tiled.parameter_count,
                    rmse=float(tiled.metrics["rmse"]),
                    ssim=float(tiled.metrics["ssim"]),
                    exact_identity_error=tiled.exact_identity_error,
                    run_fingerprint=run_fingerprint,
                )

            result = reconstruct(image, local_settings)
            save_image(output_path, result.bounded_reconstruction())
            model_value = None
            if save_models:
                result.save_model(
                    model_path,
                    residual_storage=residual_storage,
                    include_input=include_input_in_models,
                    provenance={
                        "operation": "batch-reconstruction",
                        "input": str(relative),
                        "input_sha256": digest,
                    },
                )
                model_value = str(model_path)
            summary_payload = {
                "batch": {
                    "input": str(relative),
                    "input_sha256": digest,
                    "run_fingerprint": run_fingerprint,
                    "mode": "single",
                },
                "result": result.summary(),
            }
            summary_path.write_text(json.dumps(summary_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            return BatchRecord(
                index=index,
                input=str(path),
                input_sha256=digest,
                output=str(output_path),
                summary=str(summary_path),
                model=model_value,
                status="completed",
                mode="single",
                runtime_seconds=time.perf_counter() - started,
                selected_method=result.selected_method,
                packet_count=result.packet_count,
                parameter_count=result.parameter_count,
                rmse=float(result.metrics["rmse"]),
                ssim=float(result.metrics["ssim"]),
                exact_identity_error=result.exact_identity_error,
                run_fingerprint=run_fingerprint,
            )
        except Exception as exc:  # the manifest intentionally records per-file failures
            if fail_fast:
                raise
            return BatchRecord(
                index=index,
                input=str(path),
                input_sha256=digest,
                output=None,
                summary=None,
                model=None,
                status="failed",
                mode="tiled" if tile_config is not None else "single",
                runtime_seconds=time.perf_counter() - started,
                selected_method=None,
                packet_count=None,
                parameter_count=None,
                rmse=None,
                ssim=None,
                exact_identity_error=None,
                error=f"{type(exc).__name__}: {exc}",
                run_fingerprint=run_fingerprint,
            )

    started = time.perf_counter()
    indexed = list(enumerate(paths))
    if workers == 1:
        records = [process(item) for item in indexed]
    else:
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="am-spd-batch") as executor:
            records = list(executor.map(process, indexed))
    records.sort(key=lambda record: record.index)
    result = BatchResult(
        input_root,
        destination,
        records,
        time.perf_counter() - started,
        run_fingerprint,
    )
    (destination / "batch.json").write_text(
        json.dumps(result.summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    _write_csv(destination / "batch.csv", records)
    return result
