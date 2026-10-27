#!/usr/bin/env python3
"""Post-hoc, no-training causal-quotient and D4-loop probe for v0.3.

This script is deliberately scoped to the separate v0.3 hard-QR lineage.  It
loads every frozen ``hard_correct`` primary checkpoint, enumerates every D4
coordinate context whose two primitive maps are in the frozen test split, and
measures:

* the reachable and observable ranks under an explicit SVD tolerance;
* raw-logit and additive-logit-gauge null dimensions;
* D4 identity-loop behavior after one and sixteen repetitions; and
* angular drift separately from radial gain.

It never invokes the trainer and never writes into the extracted archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import torch


PROBE_SCHEMA_VERSION = 1
PROBE_ID = "komorebi-neuralese-v0.3-hard-qr-causal-loop-probe-v0.1.0"
EXPECTED_PACKAGE_VERSION = "0.3.0"
EXPECTED_ARM = "hard_correct"
EXPECTED_MODEL = "linear_hyper_hard"
EXPECTED_PARAMETERIZATION = "qr"
EXPECTED_PRIMARY_PROTOCOL_SHA256 = (
    "ecd48865c7327b39b5d0b2679f2e6fc3e9509a01bce343cfe94b9b237482acaf"
)
EXPECTED_CONTEXT_COUNT = 2_080
RANK_RTOL = 1.0e-7
RANK_ATOL = 1.0e-10
REPEATS = (1, 16)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def array_digest(namespace: str, array: np.ndarray) -> str:
    contiguous = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(namespace.encode("utf-8"))
    digest.update(b"\x00")
    digest.update(str(contiguous.dtype).encode("ascii"))
    digest.update(b"\x00")
    digest.update(json.dumps(list(contiguous.shape), separators=(",", ":")).encode("ascii"))
    digest.update(b"\x00")
    digest.update(contiguous.tobytes(order="C"))
    return digest.hexdigest()


def finite_summary(values: torch.Tensor) -> dict[str, float | int]:
    flat = values.detach().double().reshape(-1).cpu()
    finite = flat[torch.isfinite(flat)]
    if finite.numel() != flat.numel():
        raise RuntimeError("probe metric contains non-finite values")
    quantiles = torch.quantile(
        finite,
        torch.tensor((0.0, 0.05, 0.5, 0.95, 1.0), dtype=torch.float64),
    )
    return {
        "count": int(finite.numel()),
        "minimum": float(quantiles[0]),
        "p05": float(quantiles[1]),
        "median": float(quantiles[2]),
        "mean": float(finite.mean()),
        "p95": float(quantiles[3]),
        "maximum": float(quantiles[4]),
    }


def explicit_svd_rank(
    matrices: torch.Tensor,
    *,
    rtol: float = RANK_RTOL,
    atol: float = RANK_ATOL,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return ranks, singular values, and per-matrix absolute thresholds."""

    singular = torch.linalg.svdvals(matrices.detach().double())
    threshold = torch.maximum(
        torch.full_like(singular[..., 0], float(atol)),
        singular[..., 0] * float(rtol),
    )
    ranks = (singular > threshold[..., None]).sum(dim=-1)
    return ranks, singular, threshold


def state_schema(state: dict[str, Any]) -> dict[str, Any]:
    schema: dict[str, Any] = {}
    for key, value in state.items():
        if torch.is_tensor(value):
            schema[key] = {
                "kind": "tensor",
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "layout": str(value.layout),
                "contiguous": bool(value.is_contiguous()),
            }
        else:
            schema[key] = {
                "kind": "auxiliary",
                "python_type": type(value).__name__,
                "value": value,
            }
    return schema


def execute_relation(
    operators: torch.Tensor,
    word: Iterable[int],
    repeats: int,
    embeddings: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Execute float32 matrix-vector steps and compose their matrix product."""

    batch, _, dimension, _ = operators.shape
    product = torch.eye(
        dimension,
        dtype=operators.dtype,
        device=operators.device,
    ).unsqueeze(0).expand(batch, -1, -1).clone()
    endpoints = embeddings.unsqueeze(0).expand(batch, -1, -1).clone()
    for _ in range(repeats):
        for operator in word:
            product = torch.bmm(operators[:, operator], product)
            endpoints = torch.einsum(
                "bij,bsj->bsi",
                operators[:, operator],
                endpoints,
            )
    return product, endpoints


def relation_metrics(
    product: torch.Tensor,
    endpoints: torch.Tensor,
    embeddings: torch.Tensor,
    decoder: torch.Tensor,
) -> dict[str, Any]:
    contexts, dimension, _ = product.shape
    starts = embeddings.unsqueeze(0).expand(contexts, -1, -1)
    initial_logits = torch.einsum("oi,bsi->bso", decoder, starts)
    endpoint_logits = torch.einsum("oi,bsi->bso", decoder, endpoints)
    identity = torch.eye(
        dimension,
        dtype=product.dtype,
        device=product.device,
    ).unsqueeze(0).expand_as(product)

    initial_norm = torch.linalg.vector_norm(starts, dim=-1).clamp_min(1.0e-30)
    endpoint_norm = torch.linalg.vector_norm(endpoints, dim=-1).clamp_min(1.0e-30)
    cosine = (starts * endpoints).sum(dim=-1) / (initial_norm * endpoint_norm)
    angle = torch.acos(cosine.clamp(-1.0, 1.0))
    signed_log_gain = torch.log(endpoint_norm / initial_norm)
    hidden_relative = torch.linalg.vector_norm(endpoints - starts, dim=-1) / initial_norm
    logit_relative = torch.linalg.vector_norm(
        endpoint_logits - initial_logits,
        dim=-1,
    ) / torch.linalg.vector_norm(initial_logits, dim=-1).clamp_min(1.0e-30)
    predictions = endpoint_logits.argmax(dim=-1)
    targets = torch.arange(dimension, device=product.device).unsqueeze(0)

    return {
        "contexts": int(contexts),
        "starts_per_context": int(dimension),
        "trajectories": int(contexts * dimension),
        "endpoint_return_accuracy": float((predictions == targets).float().mean()),
        "ambient_identity_residual_normalized_frobenius": finite_summary(
            torch.linalg.matrix_norm(product - identity, ord="fro", dim=(-2, -1))
            / dimension**0.5
        ),
        "hidden_return_relative_l2": finite_summary(hidden_relative),
        "decoded_logit_return_relative_l2": finite_summary(logit_relative),
        "oriented_directional_angle_radians": finite_summary(angle),
        "signed_log_radial_gain": finite_summary(signed_log_gain),
        "absolute_log_radial_gain": finite_summary(signed_log_gain.abs()),
    }


def checkpoint_paths(primary_dir: Path, seeds: list[int]) -> tuple[list[Path], list[Path]]:
    directory = primary_dir / "checkpoints" / EXPECTED_ARM
    expected = [directory / f"seed_{seed}.pt" for seed in seeds]
    observed = sorted(directory.glob("*.pt"))
    return expected, observed


def probe_seed(
    *,
    archive_root: Path,
    primary_dir: Path,
    protocol: dict[str, Any],
    protocol_sha256: str,
    tables: torch.Tensor,
    seed: int,
) -> dict[str, Any]:
    from komorebi_neuralese.algebra import D4_RELATIONS
    from komorebi_neuralese.models import build_model

    checkpoint_path = primary_dir / "checkpoints" / EXPECTED_ARM / f"seed_{seed}.pt"
    record_path = primary_dir / "arms" / EXPECTED_ARM / f"seed_{seed}.json"
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    record = json.loads(record_path.read_text(encoding="utf-8"))

    for key, expected in (
        ("package_version", EXPECTED_PACKAGE_VERSION),
        ("arm", EXPECTED_ARM),
        ("seed", seed),
        ("protocol_digest", protocol_sha256),
    ):
        if checkpoint.get(key) != expected:
            raise RuntimeError(
                f"checkpoint {checkpoint_path} has {key}={checkpoint.get(key)!r}; "
                f"expected {expected!r}"
            )
        if record.get(key) != expected:
            raise RuntimeError(
                f"record {record_path} has {key}={record.get(key)!r}; expected {expected!r}"
            )
    if checkpoint.get("config") != record.get("config"):
        raise RuntimeError(f"checkpoint/record config mismatch for seed {seed}")

    config = checkpoint["config"]
    if config.get("model_name") != EXPECTED_MODEL:
        raise RuntimeError(f"seed {seed} is not the expected hard-QR model")
    if config.get("orthogonal_parameterization") != EXPECTED_PARAMETERIZATION:
        raise RuntimeError(f"seed {seed} does not use sign-canonical QR")

    model = build_model(
        str(config["model_name"]),
        operator_init_std=float(config["operator_init_std"]),
        orthogonal_parameterization=str(config["orthogonal_parameterization"]),
    )
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    model.eval()

    with torch.no_grad():
        operators = model.encode_operators(tables)
        embeddings = model.state_embedding.weight.detach()
        decoder = model.decoder.weight.detach()

        embedding_rank, embedding_singular, embedding_threshold = explicit_svd_rank(
            embeddings
        )
        decoder_rank, decoder_singular, decoder_threshold = explicit_svd_rank(decoder)

        # Argmax is invariant to an additive common logit.  These seven
        # independent contrasts are the maximal linear observer that removes
        # that gauge.  Positive radial scaling is nonlinear/projective and is
        # audited separately rather than being called a linear null space.
        contrasts = torch.cat(
            (torch.eye(7, dtype=decoder.dtype), -torch.ones(7, 1, dtype=decoder.dtype)),
            dim=1,
        )
        contrast_decoder = contrasts @ decoder
        contrast_rank, contrast_singular, contrast_threshold = explicit_svd_rank(
            contrast_decoder
        )
        contrast_observability_h1 = torch.cat(
            (
                contrast_decoder.unsqueeze(0).expand(operators.shape[0], -1, -1),
                torch.matmul(contrast_decoder, operators[:, 0]),
                torch.matmul(contrast_decoder, operators[:, 1]),
            ),
            dim=1,
        )
        h1_ranks, h1_singular, h1_thresholds = explicit_svd_rank(
            contrast_observability_h1
        )

        identity = torch.eye(8, dtype=operators.dtype).expand(
            operators.shape[0] * operators.shape[1], -1, -1
        )
        flat_operators = operators.reshape(-1, 8, 8)
        orthogonality_defect = torch.linalg.matrix_norm(
            flat_operators.transpose(-1, -2) @ flat_operators - identity,
            ord="fro",
            dim=(-2, -1),
        ) / 8**0.5

        initial_logits = embeddings @ decoder.T
        initial_decode_accuracy = float(
            (initial_logits.argmax(dim=-1) == torch.arange(8)).float().mean()
        )

        relations: dict[str, Any] = {}
        for relation_name, word in D4_RELATIONS.items():
            repeats: dict[str, Any] = {}
            for repeat in REPEATS:
                product, endpoints = execute_relation(
                    operators,
                    word,
                    repeat,
                    embeddings,
                )
                repeats[str(repeat)] = relation_metrics(
                    product,
                    endpoints,
                    embeddings,
                    decoder,
                )
            relations[relation_name] = {
                "canonical_word": list(word),
                "matrix_order": "left multiplication; text [a,b,c] executes M_c @ M_b @ M_a",
                "repeats": repeats,
            }

    relative_checkpoint = checkpoint_path.relative_to(archive_root).as_posix()
    relative_record = record_path.relative_to(archive_root).as_posix()
    return {
        "seed": seed,
        "checkpoint": {
            "path": relative_checkpoint,
            "raw_file_sha256": sha256_file(checkpoint_path),
            "bytes": checkpoint_path.stat().st_size,
            "state_schema": state_schema(checkpoint["state_dict"]),
            "metadata": {
                key: checkpoint.get(key)
                for key in (
                    "package_version",
                    "protocol_id",
                    "analysis_status",
                    "code_digest",
                    "protocol_digest",
                    "coordinate_split_digest",
                    "arm",
                    "seed",
                )
            },
            "config": config,
        },
        "primary_record": {
            "path": relative_record,
            "raw_file_sha256": sha256_file(record_path),
            "bytes": record_path.stat().st_size,
        },
        "initial_decode_accuracy": initial_decode_accuracy,
        "rank_audit": {
            "embedding_reachable_span": {
                "rank": int(embedding_rank),
                "dimension": 8,
                "null_dimension": int(8 - embedding_rank),
                "singular_values": [float(value) for value in embedding_singular],
                "absolute_threshold": float(embedding_threshold),
            },
            "raw_decoder_h0": {
                "rank": int(decoder_rank),
                "dimension": 8,
                "null_dimension": int(8 - decoder_rank),
                "singular_values": [float(value) for value in decoder_singular],
                "absolute_threshold": float(decoder_threshold),
            },
            "argmax_additive_gauge_contrast_h0": {
                "rank": int(contrast_rank),
                "dimension": 8,
                "null_dimension": int(8 - contrast_rank),
                "singular_values": [float(value) for value in contrast_singular],
                "absolute_threshold": float(contrast_threshold),
            },
            "argmax_additive_gauge_observability_h1": {
                "context_count": int(operators.shape[0]),
                "rank_histogram": {
                    str(int(rank)): int((h1_ranks == rank).sum())
                    for rank in torch.unique(h1_ranks)
                },
                "minimum_rank": int(h1_ranks.min()),
                "maximum_rank": int(h1_ranks.max()),
                "minimum_smallest_singular_value": float(h1_singular[:, -1].min()),
                "median_smallest_singular_value": float(h1_singular[:, -1].median()),
                "maximum_absolute_threshold": float(h1_thresholds.max()),
                "null_dimension_upper_bound_after_h1": int(8 - h1_ranks.min()),
            },
            "causal_quotient": {
                "reachable_dimension": int(embedding_rank),
                "raw_logit_infinite_horizon_null_dimension": (
                    0 if int(decoder_rank) == 8 else None
                ),
                "raw_logit_quotient_dimension": (
                    int(embedding_rank) if int(decoder_rank) == 8 else None
                ),
                "argmax_contrast_infinite_horizon_null_dimension_upper_bound": int(
                    8 - h1_ranks.min()
                ),
                "argmax_contrast_quotient_dimension_lower_bound": int(h1_ranks.min()),
            },
        },
        "hard_qr_integrity": {
            "metric": "fixed_identity",
            "operator_instances": int(flat_operators.shape[0]),
            "normalized_orthogonality_defect": finite_summary(orthogonality_defect),
        },
        "relations": relations,
    }


def aggregate_seed_results(seeds: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "seed_count": len(seeds),
        "all_embedding_spans_full_rank": all(
            item["rank_audit"]["embedding_reachable_span"]["rank"] == 8
            for item in seeds
        ),
        "all_raw_decoders_full_rank": all(
            item["rank_audit"]["raw_decoder_h0"]["rank"] == 8 for item in seeds
        ),
        "all_test_contexts_contrast_observable_by_h1": all(
            item["rank_audit"]["argmax_additive_gauge_observability_h1"][
                "minimum_rank"
            ]
            == 8
            for item in seeds
        ),
        "relations": {},
    }
    for relation in ("r4", "f2", "frfr"):
        relation_result: dict[str, Any] = {}
        for repeat in REPEATS:
            entries = [
                item["relations"][relation]["repeats"][str(repeat)] for item in seeds
            ]
            accuracies = np.asarray(
                [entry["endpoint_return_accuracy"] for entry in entries], dtype=np.float64
            )
            median_angles = np.asarray(
                [entry["oriented_directional_angle_radians"]["median"] for entry in entries],
                dtype=np.float64,
            )
            maximum_radial = np.asarray(
                [entry["absolute_log_radial_gain"]["maximum"] for entry in entries],
                dtype=np.float64,
            )
            relation_result[str(repeat)] = {
                "per_seed_endpoint_accuracy": [float(value) for value in accuracies],
                "endpoint_accuracy_seed_mean": float(accuracies.mean()),
                "endpoint_accuracy_seed_minimum": float(accuracies.min()),
                "endpoint_accuracy_seed_maximum": float(accuracies.max()),
                "per_seed_median_directional_angle_radians": [
                    float(value) for value in median_angles
                ],
                "median_angle_seed_mean": float(median_angles.mean()),
                "median_angle_seed_minimum": float(median_angles.min()),
                "median_angle_seed_maximum": float(median_angles.max()),
                "maximum_absolute_log_radial_gain_across_seeds": float(
                    maximum_radial.max()
                ),
            }
        result["relations"][relation] = relation_result
    return result


def run_probe(archive_root: Path) -> dict[str, Any]:
    archive_root = archive_root.resolve()
    source_dir = archive_root / "src"
    if not source_dir.is_dir():
        raise FileNotFoundError(f"missing source directory: {source_dir}")
    sys.path.insert(0, str(source_dir))

    from komorebi_neuralese.algebra import canonical_maps, conjugate_maps
    from komorebi_neuralese.data import _eligible_coordinate_permutations
    from komorebi_neuralese.splits import audit_coordinate_splits, maps_all_in_split

    protocol_path = archive_root / "protocols" / "V0_3_STAGE_A_PRIMARY.json"
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol_sha256 = sha256_file(protocol_path)
    if protocol_sha256 != EXPECTED_PRIMARY_PROTOCOL_SHA256:
        raise RuntimeError(
            f"primary protocol digest {protocol_sha256} does not match frozen v0.3 digest"
        )
    seeds = [int(seed) for seed in protocol["seeds"]]
    if seeds != list(range(300, 312)):
        raise RuntimeError(f"unexpected primary seed census: {seeds}")
    arm = protocol["arms"].get(EXPECTED_ARM)
    if not isinstance(arm, dict) or arm.get("model_name") != EXPECTED_MODEL:
        raise RuntimeError("frozen protocol has no expected hard_correct hard-QR arm")

    primary_dir = archive_root / "results" / "v0.3.0" / "stage_a_primary_v3"
    expected_checkpoints, observed_checkpoints = checkpoint_paths(primary_dir, seeds)
    missing = [path for path in expected_checkpoints if not path.is_file()]
    unexpected = sorted(set(observed_checkpoints) - set(expected_checkpoints))
    if missing or unexpected:
        raise RuntimeError(
            f"checkpoint census mismatch; missing={missing}, unexpected={unexpected}"
        )

    coordinate_audit = audit_coordinate_splits()
    if not coordinate_audit.passed:
        raise RuntimeError("frozen coordinate-split audit failed")
    phis = _eligible_coordinate_permutations("d4", "test")
    maps = conjugate_maps(canonical_maps("d4"), phis)
    if phis.shape != (EXPECTED_CONTEXT_COUNT, 8):
        raise RuntimeError(f"expected {EXPECTED_CONTEXT_COUNT} test D4 contexts, got {phis.shape}")
    split_membership = maps_all_in_split(maps, "test")
    if not isinstance(split_membership, np.ndarray) or not bool(split_membership.all()):
        raise RuntimeError("D4 context census includes a primitive outside the test split")
    tables_numpy = np.eye(8, dtype=np.float32)[maps]
    tables = torch.from_numpy(tables_numpy)
    _, observable_context_multiplicities = np.unique(
        maps.reshape(maps.shape[0], -1),
        axis=0,
        return_counts=True,
    )

    torch.set_num_threads(1)
    seed_results = [
        probe_seed(
            archive_root=archive_root,
            primary_dir=primary_dir,
            protocol=protocol,
            protocol_sha256=protocol_sha256,
            tables=tables,
            seed=seed,
        )
        for seed in seeds
    ]

    reproducibility_path = (
        archive_root
        / "results"
        / "v0.3.0"
        / "stage_a_reproducibility"
        / "REPRODUCIBILITY.json"
    )
    reproducibility = json.loads(reproducibility_path.read_text(encoding="utf-8"))
    if not reproducibility.get("overall_passed"):
        raise RuntimeError("canonical seed-300 reproducibility receipt is not passing")
    canonical_digest = reproducibility["validation"][
        "original_canonical_checkpoint_sha256"
    ]

    return {
        "schema_version": PROBE_SCHEMA_VERSION,
        "probe_id": PROBE_ID,
        "analysis_status": "posthoc_diagnostic_no_retraining",
        "lineage": {
            "package": "Komorebi_Neuralese_Operator_Workspace_v0.3.0",
            "package_version": EXPECTED_PACKAGE_VERSION,
            "stage": "Stage A primary",
            "arm": EXPECTED_ARM,
            "architecture": EXPECTED_MODEL,
            "operator_parameterization": "sign-canonicalized reduced QR",
            "latent_metric": "fixed identity",
            "separate_from": [
                "v0.2 soft-isometry lineage",
                "v0.4 packet-closure lineage",
            ],
        },
        "claim_boundary": (
            "This is a deterministic post-hoc mechanism audit of frozen learned "
            "checkpoints. It is not a retraining result, a preregistered gate, evidence "
            "of spontaneous Neuralese, or a claim about natural-language-model internals."
        ),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": "cpu",
            "torch_threads": torch.get_num_threads(),
        },
        "rank_tolerance": {
            "dtype": "float64 SVD of frozen float32 tensors/operators",
            "relative": RANK_RTOL,
            "absolute": RANK_ATOL,
            "formula": "rank = count(sigma_i > max(atol, rtol * sigma_max))",
        },
        "source_integrity": {
            "archive_root": str(archive_root),
            "primary_protocol": protocol_path.relative_to(archive_root).as_posix(),
            "primary_protocol_sha256": protocol_sha256,
            "coordinate_split_digest": coordinate_audit.digest,
            "coordinate_split_audit_passed": coordinate_audit.passed,
            "canonical_replayed_checkpoint_seed": 300,
            "canonical_replayed_checkpoint_normalized_sha256": canonical_digest,
            "checkpoint_census": {
                "expected": len(expected_checkpoints),
                "observed": len(observed_checkpoints),
                "missing": [],
                "unexpected": [],
                "seeds": seeds,
            },
        },
        "context_census": {
            "family": "d4",
            "coordinate_split": "test",
            "primitive_maps_must_both_be_in_split": True,
            "eligible_coordinate_permutations": int(phis.shape[0]),
            "coordinate_contexts": int(phis.shape[0]),
            "unique_ordered_observable_map_pairs": int(
                observable_context_multiplicities.shape[0]
            ),
            "observable_map_pair_multiplicity_histogram": {
                str(int(value)): int((observable_context_multiplicities == value).sum())
                for value in np.unique(observable_context_multiplicities)
            },
            "context_weighting_note": (
                "All 2,080 eligible coordinate permutations are retained. Each of the "
                "260 unique ordered observable (r,f) map pairs occurs exactly eight "
                "times, so permutation-uniform and unique-pair-uniform summaries agree."
            ),
            "starts_per_context": 8,
            "trajectories_per_seed_per_relation_repeat": int(phis.shape[0] * 8),
            "coordinate_permutations_sha256": array_digest(
                "v0.3-probe/test-d4-phis", phis.astype("<i8", copy=False)
            ),
            "canonical_ordered_maps_sha256": array_digest(
                "v0.3-probe/test-d4-maps", maps.astype("<i8", copy=False)
            ),
            "canonical_operator_order": ["r", "f"],
            "visible_slot_randomization": (
                "not enumerated because canonical r/f codes are selected after slot "
                "unmasking; swapping the two visible slots is algebraically redundant"
            ),
        },
        "relation_repeats": list(REPEATS),
        "seeds": seed_results,
        "aggregate": aggregate_seed_results(seed_results),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive-root",
        type=Path,
        required=True,
        help="Extracted Komorebi_Neuralese_Operator_Workspace_v0.3.0 directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination JSON path outside the extracted archive",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_probe(args.archive_root)
    output = args.output.resolve()
    archive_root = args.archive_root.resolve()
    try:
        output.relative_to(archive_root)
    except ValueError:
        pass
    else:
        raise RuntimeError("refusing to write probe output inside the extracted archive")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "pass",
                "output": str(output),
                "checkpoint_count": result["source_integrity"]["checkpoint_census"][
                    "observed"
                ],
                "context_count": result["context_census"]["coordinate_contexts"],
                "all_raw_decoders_full_rank": result["aggregate"][
                    "all_raw_decoders_full_rank"
                ],
                "all_test_contexts_contrast_observable_by_h1": result["aggregate"][
                    "all_test_contexts_contrast_observable_by_h1"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
