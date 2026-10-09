from __future__ import annotations

import csv
import json
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

from . import atlas
from .api import AMSpdConfig, reconstruct
from .io import save_image

BUILTIN_CASES = ("synthetic_geometry", "synthetic_text_curves", "camera", "astronaut")
METHODS = ("core", "spd", "tree", "portfolio")


@dataclass(frozen=True)
class BenchmarkRecord:
    case: str
    method: str
    preset: str
    size: int
    runtime_seconds: float
    selected_method: str
    packet_count: int
    parameter_count: int
    exact_identity_error: float
    rmse: float
    psnr: float
    ssim: float
    edge_rmse: float
    max_local_range_violation: float
    mean_local_range_violation: float
    fraction_outside_local_range: float


def _write_csv(path: Path, records: list[BenchmarkRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(records[0])))
        writer.writeheader()
        writer.writerows(asdict(record) for record in records)


def run_builtin_benchmark(
    output_dir: str | Path,
    *,
    cases: Iterable[str] | None = None,
    methods: Iterable[str] | None = None,
    preset: str = "quick",
    size: int = 24,
    save_models: bool = False,
    include_input_in_models: bool = False,
) -> dict[str, object]:
    if size < 8:
        raise ValueError("benchmark size must be at least 8")
    if preset not in {"quick", "paper-scale", "paper"}:
        raise ValueError("preset must be quick or paper-scale")
    selected_cases = tuple(cases or BUILTIN_CASES)
    selected_methods = tuple(methods or METHODS)
    unknown_cases = sorted(set(selected_cases) - set(BUILTIN_CASES))
    unknown_methods = sorted(set(selected_methods) - set(METHODS))
    if unknown_cases:
        raise ValueError(f"unknown benchmark cases: {', '.join(unknown_cases)}")
    if unknown_methods:
        raise ValueError(f"unknown benchmark methods: {', '.join(unknown_methods)}")

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    images = atlas.benchmark_images(size)
    records: list[BenchmarkRecord] = []
    summaries: dict[str, dict[str, object]] = {}

    for case in selected_cases:
        case_dir = destination / case
        case_dir.mkdir(parents=True, exist_ok=True)
        image = images[case]
        save_image(case_dir / "input.png", image)
        summaries[case] = {}
        for method in selected_methods:
            config = AMSpdConfig.quick(method) if preset == "quick" else AMSpdConfig.paper_scale(method)
            started = time.perf_counter()
            result = reconstruct(image, config)
            runtime = time.perf_counter() - started
            output_image = save_image(case_dir / f"{method}.png", result.bounded_reconstruction())
            summary_path = case_dir / f"{method}.json"
            summary_path.write_text(json.dumps(result.summary(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            model_path = None
            if save_models:
                model_path = result.save_model(
                    case_dir / f"{method}.amspd",
                    residual_storage="sparse",
                    include_input=include_input_in_models,
                    provenance={
                        "mode": "builtin-benchmark",
                        "case": case,
                        "preset": "paper-scale" if preset == "paper" else preset,
                    },
                )
            metrics = result.metrics
            record = BenchmarkRecord(
                case=case,
                method=method,
                preset="paper-scale" if preset == "paper" else preset,
                size=size,
                runtime_seconds=runtime,
                selected_method=result.selected_method,
                packet_count=result.packet_count,
                parameter_count=result.parameter_count,
                exact_identity_error=result.exact_identity_error,
                rmse=float(metrics["rmse"]),
                psnr=float(metrics["psnr"]),
                ssim=float(metrics["ssim"]),
                edge_rmse=float(metrics["edge_rmse"]),
                max_local_range_violation=float(metrics["max_local_range_violation"]),
                mean_local_range_violation=float(metrics["mean_local_range_violation"]),
                fraction_outside_local_range=float(metrics["fraction_outside_local_range"]),
            )
            records.append(record)
            summaries[case][method] = {
                "record": asdict(record),
                "image": str(output_image),
                "summary": str(summary_path),
                "model": str(model_path) if model_path is not None else None,
            }

    _write_csv(destination / "benchmark.csv", records)
    report: dict[str, object] = {
        "preset": "paper-scale" if preset == "paper" else preset,
        "size": size,
        "cases": selected_cases,
        "methods": selected_methods,
        "records": [asdict(record) for record in records],
        "artifacts": summaries,
    }
    (destination / "benchmark.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
