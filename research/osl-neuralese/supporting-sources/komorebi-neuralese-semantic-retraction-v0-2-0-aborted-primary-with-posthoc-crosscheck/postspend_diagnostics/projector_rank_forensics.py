#!/usr/bin/env python3
"""Post-spend, parameter-only forensics for the aborted anchor-projector audit.

This script deliberately does not construct any context, path, continuation, or
behavioral evaluation bank.  Its output cannot repair or replace the frozen
primary run.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import platform
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from primary_probe import run_semantic_retraction_probe as probe  # noqa: E402


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def max_abs(value: np.ndarray) -> float:
    return float(np.max(np.abs(value)))


def residual_norms(value: np.ndarray) -> dict[str, float]:
    widened = value.astype(np.float64, copy=False)
    return {
        "maximum_absolute_entry": max_abs(widened),
        "frobenius_norm": float(np.linalg.norm(widened, ord="fro")),
        "operator_2_norm": float(np.linalg.norm(widened, ord=2)),
    }


def canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )


def publish_new_json(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite diagnostic: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = canonical_json_bytes(payload)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path, follow_symlinks=False)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def analyze_model(model: torch.nn.Module) -> dict[str, Any]:
    anchors_native = model.state_anchors().detach().cpu().numpy()
    metric_native = model.invariant_metric().detach().cpu().numpy()
    if anchors_native.dtype != np.float32 or metric_native.dtype != np.float32:
        raise TypeError("expected native float32 anchors and metric")

    anchors = anchors_native.astype(np.float64).T
    metric = metric_native.astype(np.float64)
    antisymmetry = max_abs(metric - metric.T)
    metric = 0.5 * (metric + metric.T)
    eigenvalues = np.linalg.eigvalsh(metric)
    gram = anchors.T @ metric @ anchors
    gram_singular = np.linalg.svd(gram, compute_uv=False)
    lower = np.linalg.cholesky(metric)
    whitener = lower.T
    whitened = whitener @ anchors
    left, whitened_singular, _ = np.linalg.svd(whitened, full_matrices=False)
    orthonormal = left[:, :8]
    projector64 = np.linalg.solve(
        whitener, orthonormal @ orthonormal.T @ whitener
    )
    projector32 = projector64.astype(np.float32)
    projector32_widened = projector32.astype(np.float64)

    p64_singular = np.linalg.svd(projector64, compute_uv=False)
    p32_singular = np.linalg.svd(projector32_widened, compute_uv=False)
    eps32_tolerance = float(
        max(projector32.shape) * np.finfo(np.float32).eps * p32_singular[0]
    )
    eps64_tolerance = float(
        max(projector32.shape) * np.finfo(np.float64).eps * p32_singular[0]
    )
    p64_default_tolerance = float(
        max(projector64.shape) * np.finfo(np.float64).eps * p64_singular[0]
    )
    native32_rank = int(np.linalg.matrix_rank(projector32))
    widened_default_rank = int(np.linalg.matrix_rank(projector32_widened))
    explicit_eps32_rank = int(np.count_nonzero(p32_singular > eps32_tolerance))

    idempotence64 = projector32_widened @ projector32_widened - projector32_widened
    self_adjointness64 = projector32_widened.T @ metric - metric @ projector32_widened
    anchor_residual64 = projector32_widened @ anchors - anchors
    idempotence32 = projector32 @ projector32 - projector32
    self_adjointness32 = projector32.T @ metric_native - metric_native @ projector32
    anchor_residual32 = projector32 @ anchors_native.T - anchors_native.T
    trace_error = abs(float(np.trace(projector32_widened)) - 8.0)
    direct = anchors @ np.linalg.solve(gram, anchors.T @ metric)
    direct_difference = projector64 - direct

    tolerance = 1e-5
    conjuncts = {
        "post_cast_rank_equals_eight": widened_default_rank == 8,
        "trace_error_at_most_1e_minus_5": trace_error <= tolerance,
        "idempotence_at_most_1e_minus_5": max_abs(idempotence64) <= tolerance,
        "g_self_adjointness_at_most_1e_minus_5": max_abs(self_adjointness64)
        <= tolerance,
        "anchor_preservation_at_most_1e_minus_5": max_abs(anchor_residual64)
        <= tolerance,
    }
    substantive = {key: value for key, value in conjuncts.items() if "rank" not in key}

    runner_exception: str | None = None
    try:
        probe.construct_anchor_projector(model)
    except RuntimeError as error:
        runner_exception = str(error)

    return {
        "input_geometry": {
            "anchor_shape_model_native": list(anchors_native.shape),
            "anchor_rank_float64_default": int(np.linalg.matrix_rank(anchors)),
            "anchor_singular_values": np.linalg.svd(anchors, compute_uv=False).tolist(),
            "metric_maximum_absolute_difference_from_identity": max_abs(
                metric - np.eye(metric.shape[0])
            ),
            "metric_maximum_antisymmetric_entry_before_symmetrization": antisymmetry,
            "metric_eigenvalues": eigenvalues.tolist(),
            "metric_condition_number": float(eigenvalues[-1] / eigenvalues[0]),
            "anchor_gram_singular_values": gram_singular.tolist(),
            "anchor_gram_condition_number": float(
                gram_singular[0] / gram_singular[-1]
            ),
            "anchor_gram_relative_1e_minus_8_rank": int(
                np.count_nonzero(gram_singular > 1e-8 * gram_singular[0])
            ),
            "whitened_anchor_singular_values": whitened_singular.tolist(),
        },
        "projector_spectra_and_ranks": {
            "projector64_singular_values": p64_singular.tolist(),
            "projector32_widened_singular_values": p32_singular.tolist(),
            "projector64_default_rank": int(np.linalg.matrix_rank(projector64)),
            "projector32_native_default_rank": native32_rank,
            "projector32_widened_default_rank_used_by_frozen_runner": widened_default_rank,
            "projector32_explicit_eps32_rank": explicit_eps32_rank,
            "projector64_default_rank_tolerance": p64_default_tolerance,
            "projector32_native_or_explicit_eps32_tolerance": eps32_tolerance,
            "projector32_widened_default_eps64_tolerance": eps64_tolerance,
            "sigma8": float(p32_singular[7]),
            "sigma9": float(p32_singular[8]),
            "sigma12": float(p32_singular[11]),
            "sigma8_to_sigma9_ratio": float(p32_singular[7] / p32_singular[8]),
        },
        "post_cast_residuals": {
            "trace": float(np.trace(projector32_widened)),
            "trace_error_from_eight": trace_error,
            "float64_audit_arithmetic": {
                "idempotence": residual_norms(idempotence64),
                "g_self_adjointness": residual_norms(self_adjointness64),
                "anchor_preservation": residual_norms(anchor_residual64),
            },
            "native_float32_arithmetic": {
                "idempotence": residual_norms(idempotence32),
                "g_self_adjointness": residual_norms(self_adjointness32),
                "anchor_preservation": residual_norms(anchor_residual32),
            },
            "maximum_absolute_projector32_minus_projector64": max_abs(
                projector32_widened - projector64
            ),
            "whitened_svd_vs_direct_formula": residual_norms(direct_difference),
        },
        "frozen_runner_audit": {
            "runner_exception": runner_exception,
            "conjuncts": conjuncts,
            "pass": all(conjuncts.values()),
            "all_non_rank_conjuncts_pass": all(substantive.values()),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", required=True, type=Path)
    parser.add_argument("--archive", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()

    package = arguments.package.resolve(strict=True)
    archive = arguments.archive.resolve(strict=True)
    output = arguments.output.resolve(strict=False)
    spend = PROJECT_ROOT / "primary_probe" / "EVALUATION_BANK_SPENT.json"
    if not spend.is_file():
        raise RuntimeError("post-spend diagnostic requires the durable spend marker")
    if output.is_relative_to(PROJECT_ROOT / "primary_probe" / "RESULTS.bundle"):
        raise RuntimeError("diagnostic must stay outside the frozen result bundle")

    api = probe.import_v04_api(package)
    verified, seal = probe.verify_checkpoint_census(package)
    rows: list[dict[str, Any]] = []
    for checkpoint in verified:
        loaded = probe.load_one_verified_checkpoint(checkpoint, seal, api)
        geometry = analyze_model(loaded["model"])
        rows.append(
            {
                "arm": loaded["arm"],
                "seed": loaded["seed"],
                "model_family": loaded["model_family"],
                "checkpoint_sha256": loaded["checkpoint_sha256"],
                "loaded_state_dict_digest": loaded["loaded_state_dict_digest"],
                **geometry,
            }
        )
        del loaded
        gc.collect()

    only_dtype_rank_failure = all(
        row["frozen_runner_audit"]["runner_exception"]
        == "anchor projector audit failed"
        and not row["frozen_runner_audit"]["conjuncts"][
            "post_cast_rank_equals_eight"
        ]
        and row["frozen_runner_audit"]["all_non_rank_conjuncts_pass"]
        and row["projector_spectra_and_ranks"]["projector32_native_default_rank"]
        == 8
        and row["projector_spectra_and_ranks"]["projector32_explicit_eps32_rank"]
        == 8
        for row in rows
    )
    payload: dict[str, Any] = {
        "schema": "komorebi.neuralese.semantic_retraction.postspend_projector_forensics.v1",
        "version": "0.2.0",
        "author": "Komorebi P.",
        "status": "POSTSPEND_PARAMETER_ONLY_DIAGNOSTIC",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "epistemic_boundary": {
            "prospective": False,
            "evaluation_context_path_or_continuation_bank_used": False,
            "learned_checkpoint_parameters_loaded": True,
            "behavioral_outputs_generated": False,
            "can_repair_or_rehabilitate_primary_result": False,
            "can_award_primary_labels": False,
            "primary_bank_remains_irrevocably_spent": True,
        },
        "provenance": {
            "source_archive_path": str(archive),
            "source_archive_sha256": sha256_file(archive),
            "extracted_package_manifest_sha256": sha256_file(package / "MANIFEST.json"),
            "spend_receipt_sha256": sha256_file(spend),
            "frozen_analysis_protocol_sha256": sha256_file(
                PROJECT_ROOT / "ANALYSIS_PROTOCOL.md"
            ),
            "frozen_primary_implementation_sha256": sha256_file(
                PROJECT_ROOT / "primary_probe" / "run_semantic_retraction_probe.py"
            ),
            "frozen_primary_contract_sha256": sha256_file(
                PROJECT_ROOT / "primary_probe" / "PROTOCOL.json"
            ),
            "diagnostic_script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": "cpu",
        },
        "method": {
            "scope": "sealed checkpoint parameters and anchor/metric geometry only",
            "projector_construction": "exact frozen whitened-SVD formula",
            "frozen_rank_operation": "matrix_rank(float32_projector.astype(float64)) with NumPy default float64 tolerance",
            "comparison_rank_operation": "native float32 default and explicit max(m,n)*eps32*sigma1 tolerance",
            "residual_tolerance": 1e-5,
            "cells": 12,
        },
        "summary": {
            "all_cells_loaded_and_bound": len(rows) == 12,
            "all_cells_fail_frozen_runner_projector_audit": all(
                not row["frozen_runner_audit"]["pass"] for row in rows
            ),
            "all_cells_pass_every_non_rank_conjunct": all(
                row["frozen_runner_audit"]["all_non_rank_conjuncts_pass"]
                for row in rows
            ),
            "all_cells_native_float32_rank_eight": all(
                row["projector_spectra_and_ranks"][
                    "projector32_native_default_rank"
                ]
                == 8
                for row in rows
            ),
            "all_cells_explicit_eps32_rank_eight": all(
                row["projector_spectra_and_ranks"]["projector32_explicit_eps32_rank"]
                == 8
                for row in rows
            ),
            "all_cells_only_failure_is_dtype_mismatched_default_rank": only_dtype_rank_failure,
            "classification": (
                "DTYPE_TOLERANCE_FALSE_REJECTION"
                if only_dtype_rank_failure
                else "MIXED_OR_UNRESOLVED_PROJECTOR_FAILURE"
            ),
            "does_not_change_primary_status": "ABORTED_INVALID_NO_COMMIT",
        },
        "cells": rows,
    }
    publish_new_json(output, payload)
    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": sha256_file(output),
                "bytes": output.stat().st_size,
                "summary": payload["summary"],
                "compact_cells": [
                    {
                        "arm": row["arm"],
                        "seed": row["seed"],
                        "widened_rank": row["projector_spectra_and_ranks"][
                            "projector32_widened_default_rank_used_by_frozen_runner"
                        ],
                        "native_rank": row["projector_spectra_and_ranks"][
                            "projector32_native_default_rank"
                        ],
                        "eps32_rank": row["projector_spectra_and_ranks"][
                            "projector32_explicit_eps32_rank"
                        ],
                        "sigma9": row["projector_spectra_and_ranks"]["sigma9"],
                        "trace_error": row["post_cast_residuals"][
                            "trace_error_from_eight"
                        ],
                        "max_idempotence": row["post_cast_residuals"][
                            "float64_audit_arithmetic"
                        ]["idempotence"]["maximum_absolute_entry"],
                        "max_self_adjointness": row["post_cast_residuals"][
                            "float64_audit_arithmetic"
                        ]["g_self_adjointness"]["maximum_absolute_entry"],
                        "max_anchor_residual": row["post_cast_residuals"][
                            "float64_audit_arithmetic"
                        ]["anchor_preservation"]["maximum_absolute_entry"],
                    }
                    for row in rows
                ],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
