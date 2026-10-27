from __future__ import annotations

import datetime as dt
import pathlib
from dataclasses import dataclass, field
from typing import Any

from .metrics import functional_profile
from .utils import atomic_write_json, digest_object, scalarize, write_csv


@dataclass
class ExperimentResult:
    family: str
    status: str
    metrics: dict[str, Any]
    rows: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def create_run_directory(
    output_root: pathlib.Path,
    name: str,
    seed: int,
    overwrite: bool,
    resume: bool = False,
) -> pathlib.Path:
    safe = "".join(character if character.isalnum() or character in "-_." else "_" for character in name)
    base = output_root / f"{safe}_seed{seed}"
    if resume and base.exists():
        base.mkdir(parents=True, exist_ok=True)
        return base
    if overwrite:
        base.mkdir(parents=True, exist_ok=True)
        return base
    candidate = base
    index = 1
    while candidate.exists():
        candidate = output_root / f"{safe}_seed{seed}_{index:03d}"
        index += 1
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def write_result_bundle(
    run_dir: pathlib.Path,
    config: dict[str, Any],
    result: ExperimentResult,
    elapsed_seconds: float,
) -> dict[str, Any]:
    metrics = scalarize(result.metrics)
    profile = functional_profile(metrics)
    summary = {
        "schema": "rrct.lab.run_summary.v1",
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "family": result.family,
        "status": result.status,
        "elapsed_seconds": elapsed_seconds,
        "config_digest": digest_object(config),
        "metrics": metrics,
        "functional_profile": profile,
        "warnings": result.warnings,
        "artifacts": result.artifacts,
        "metadata": scalarize(result.metadata),
    }
    atomic_write_json(run_dir / "resolved_config.json", config)
    atomic_write_json(run_dir / "summary.json", summary)
    atomic_write_json(run_dir / "functional_profile.json", profile)
    write_csv(run_dir / "metrics.csv", [{"metric": key, "value": value} for key, value in metrics.items() if isinstance(value, (int, float, str, bool))])
    if result.rows:
        write_csv(run_dir / "rows.csv", result.rows)
    if result.warnings:
        (run_dir / "warnings.txt").write_text("\n".join(result.warnings) + "\n", encoding="utf-8")
    return summary
