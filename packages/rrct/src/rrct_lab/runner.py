from __future__ import annotations

import copy
import importlib
import inspect
import json
import pathlib
import os
import tracemalloc
from typing import Any

from .config import config_without_runtime_paths, validate_config
from .contracts import enforce_contract
from .exceptions import RRCTLabError
from .orchestration import RunContext, stable_checkpoint_digest
from .registry import get_experiment
from .results import create_run_directory, write_result_bundle
from .safety import enforce
from .utils import Timer, atomic_write_json, digest_object


def project_root() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parents[2]


def _load_json_object(path: pathlib.Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RRCTLabError(f"cannot validate {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise RRCTLabError(f"cannot validate {label}: {path} is not a JSON object")
    return payload


def _existing_completed_summary(
    run_dir: pathlib.Path,
    requested_config: dict[str, Any],
) -> dict[str, Any] | None:
    path = run_dir / "summary.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(payload, dict):
        return None
    if payload.get("status") != "completed":
        return None

    resolved_path = run_dir / "resolved_config.json"
    if not resolved_path.is_file():
        raise RRCTLabError(
            "cannot reuse a completed run without its resolved configuration"
        )
    resolved_config = _load_json_object(resolved_path, "completed-run configuration")
    requested_digest = stable_checkpoint_digest(requested_config)
    resolved_digest = stable_checkpoint_digest(resolved_config)
    if resolved_digest != requested_digest:
        raise RRCTLabError(
            "completed-run configuration digest does not match the requested resume"
        )
    if payload.get("config_digest") != digest_object(resolved_config):
        raise RRCTLabError("completed-run summary configuration digest is invalid")

    state_path = run_dir / "run_state.json"
    if not state_path.is_file():
        raise RRCTLabError("cannot reuse a completed run without run_state.json")
    run_state = _load_json_object(state_path, "completed-run state")
    if run_state.get("config_digest") != requested_digest:
        raise RRCTLabError("completed-run state configuration digest is invalid")
    if run_state.get("status") != "completed":
        raise RRCTLabError("completed-run summary is not backed by completed run state")

    checkpoint_path = run_dir / "checkpoints/latest.json"
    if checkpoint_path.is_file():
        checkpoint = _load_json_object(checkpoint_path, "completed-run checkpoint")
        if checkpoint.get("config_digest") != requested_digest:
            raise RRCTLabError("completed-run checkpoint configuration digest is invalid")
        if checkpoint.get("state_digest") != digest_object(checkpoint.get("state", {})):
            raise RRCTLabError("completed-run checkpoint state digest is invalid")

    payload["run_directory"] = str(run_dir)
    payload["resumed_without_reexecution"] = True
    return payload


def _call_experiment(function: Any, config: dict[str, Any], context: RunContext) -> Any:
    signature = inspect.signature(function)
    if "context" in signature.parameters:
        return function(config, context=context)
    return function(config)


def run_config(
    config: dict[str, Any],
    *,
    resume_directory: pathlib.Path | None = None,
) -> list[dict[str, Any]]:
    validate_config(config)
    root = project_root()
    output_root = enforce(config, root)
    family = str(config["experiment"]["family"])
    spec = get_experiment(family)
    module = importlib.import_module(spec.module)
    function = getattr(module, spec.function)
    repetitions = int(config["run"].get("repetitions", 1))
    if resume_directory is not None and repetitions != 1:
        raise RRCTLabError("resuming an explicit run directory requires run.repetitions=1")
    summaries: list[dict[str, Any]] = []
    base_seed = int(config["run"]["seed"])
    for repetition in range(repetitions):
        local = copy.deepcopy(config)
        local["run"]["seed"] = base_seed + repetition
        name = str(local["run"].get("name", family))
        if repetitions > 1:
            name = f"{name}_rep{repetition:03d}"
        local["run"]["name"] = name
        if resume_directory is not None:
            local["run"]["resume"] = True
        contract = enforce_contract(local, family)
        resume = bool(local["run"].get("resume", False))
        run_dir = (
            resume_directory.resolve()
            if resume_directory is not None
            else create_run_directory(
                output_root,
                name,
                int(local["run"]["seed"]),
                bool(local["run"].get("overwrite", False)),
                resume=resume,
            )
        )
        run_dir.mkdir(parents=True, exist_ok=True)
        if resume:
            existing = _existing_completed_summary(run_dir, local)
            if existing is not None:
                summaries.append(existing)
                continue
        atomic_write_json(run_dir / "feature_contract.json", contract)

        # Preserve the exact configuration used for a resumable run before execution starts.
        atomic_write_json(run_dir / "resolved_config.json", local)
        threads = int(local.get("runtime", {}).get("threads", 0))
        if threads > 0:
            os.environ["OMP_NUM_THREADS"] = str(threads)
            os.environ["MKL_NUM_THREADS"] = str(threads)
            os.environ["OPENBLAS_NUM_THREADS"] = str(threads)
        tracemalloc.start()
        context = RunContext.create(run_dir, local)
        context.checkpoint(
            context.resume_step,
            context.resume_state or {"phase": "starting"},
            {"resumed": context.resumed},
            force=True,
        )
        try:
            with Timer() as timer:
                result = _call_experiment(function, local, context)
            context.check_limits()
        except BaseException as exc:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            failure = {
                "schema": "rrct.lab.run_failure.v1",
                "family": family,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "config_digest": digest_object(config_without_runtime_paths(local)),
                "peak_python_memory_mb": peak / (1024.0 * 1024.0),
                "resume_step": context.resume_step,
            }
            atomic_write_json(run_dir / "failure.json", failure)
            context.mark_failed(f"{type(exc).__name__}: {exc}")
            raise

        partial = contract.get("partial_nondefault", [])
        unsupported = contract.get("unsupported_nondefault", [])
        for key in partial:
            result.warnings.append(f"{key} is only partially implemented for {family}")
        for key in unsupported:
            result.warnings.append(f"{key} is not used by {family}")
        if bool(local["run"].get("fail_on_warning", False)) and result.warnings:
            context.mark_failed("warnings rejected by run.fail_on_warning")
            raise RRCTLabError(
                "run.fail_on_warning=true and warnings were emitted: "
                + "; ".join(result.warnings)
            )

        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        result.metrics.setdefault("wall_time_seconds", timer.elapsed)
        result.metrics.setdefault("peak_python_memory_mb", peak / (1024.0 * 1024.0))
        result.metadata.setdefault("experiment_spec", spec.title)
        result.metadata.setdefault("tags", list(local.get("run", {}).get("tags", [])))
        result.metadata.setdefault(
            "reproducibility_digest", stable_checkpoint_digest(local)
        )
        result.metadata.setdefault("feature_contract", contract)
        result.metadata.setdefault("resumed", context.resumed)
        result.metadata.setdefault("resume_count", context.resume_count)
        summary = write_result_bundle(run_dir, local, result, timer.elapsed)
        summary["run_directory"] = str(run_dir)
        final_step = int(
            result.metadata.get(
                "final_step", result.metrics.get("episodes_completed", context.resume_step)
            )
        )
        if result.status == "completed":
            if bool(local["run"].get("checkpoint_on_completion", True)):
                context.mark_completed(final_step, result.metrics)
            else:
                context.mark_completed_without_checkpoint(final_step)
        else:
            context.mark_interrupted(final_step, f"experiment status={result.status}")
        summaries.append(summary)
    return summaries
