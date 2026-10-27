#!/usr/bin/env python3
"""Post-hoc radial-mechanism audit for the frozen learned checkpoints.

This file is intentionally separate from the registered gate run.  It was
specified after the registered results were inspected and therefore carries
no confirmatory status.
"""

from __future__ import annotations

import json
import itertools
from pathlib import Path
from typing import Any

import numpy as np

from core import canonical_maps, conjugate_maps, encode_tables, run_batch, sample_batch
from run_probe import PREREGISTRATION, load_inputs, summary


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "results" / "POSTHOC_NUMERIC_MECHANISM.json"


def operator_spectrum(checkpoint: Any, seed: int, episodes: int = 64) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    batch = sample_batch(rng, episodes, 0, family="d4")
    codes = encode_tables(checkpoint.weights, batch.tables, np.float64)
    matrices = codes.reshape(-1, 8, 8)
    radii = np.asarray(
        [np.max(np.abs(np.linalg.eigvals(matrix))) for matrix in matrices],
        dtype=np.float64,
    )
    norms = np.asarray(
        [np.linalg.norm(matrix, ord=2) for matrix in matrices], dtype=np.float64
    )
    return {
        "episode_count": episodes,
        "operator_count": int(matrices.shape[0]),
        "spectral_radius": summary(radii),
        "euclidean_operator_2_norm": summary(norms),
        "all_sampled_operators_strict_euclidean_contractions": bool(np.max(norms) < 1.0),
        "warning": "Individual or sampled operator spectra are not a certified joint spectral radius outside this finite audited set.",
    }


def d4_support_reconstruction(checkpoint: Any, probe_seed: int) -> dict[str, Any]:
    """Reconstruct support, not exact stored episode receipts, from frozen config."""

    config = checkpoint.metadata["config"]
    full_support: set[bytes] = set()
    canonical = canonical_maps("d4")
    for permutation in itertools.permutations(range(8)):
        phi = np.asarray(permutation, dtype=np.int64)[None, :]
        maps = conjugate_maps(canonical, phi)[0]
        full_support.add(maps.tobytes())
        full_support.add(maps[::-1].tobytes())

    rng = np.random.default_rng(10_000 + int(config["seed"]))
    observed: set[bytes] = set()
    for _ in range(int(config["steps"])):
        length = int(rng.integers(1, int(config["train_max_length"]) + 1))
        batch = sample_batch(rng, int(config["batch_size"]), length, family="d4")
        observed.update(pair.tobytes() for pair in batch.maps)

    probe = sample_batch(
        np.random.default_rng(probe_seed), 64, 0, family="d4"
    )
    probe_keys = {pair.tobytes() for pair in probe.maps}
    return {
        "method": "deterministic source-generator RNG reconstruction from frozen config; not stored episode receipts",
        "full_ordered_d4_table_pair_support": len(full_support),
        "unique_ordered_pairs_in_reconstructed_training_stream": len(observed),
        "training_stream_exhausts_finite_table_pair_support": observed == full_support,
        "unique_registered_probe_pairs": len(probe_keys),
        "registered_probe_pairs_seen_in_reconstructed_training_stream": len(
            probe_keys & observed
        ),
        "registered_probe_support_overlap_fraction": len(probe_keys & observed)
        / max(len(probe_keys), 1),
        "interpretation": "The registered episodes are post-training resamples within task support, not held-out table-pair generalization.",
    }


def projective_underflow(
    checkpoint: Any,
    seed: int,
    depths: tuple[int, ...] = (8, 16, 32, 64),
    examples: int = 512,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    output: dict[str, Any] = {}
    for depth in depths:
        batch = sample_batch(rng, examples, depth, family="d4")
        with np.errstate(over="ignore", invalid="ignore", under="ignore"):
            raw_hidden, raw_logits = run_batch(
                checkpoint.weights,
                batch,
                normalize_each_step=False,
                dtype=np.float32,
            )
            projective_hidden, projective_logits = run_batch(
                checkpoint.weights,
                batch,
                normalize_each_step=True,
                dtype=np.float32,
            )
        del projective_hidden
        raw_finite = np.isfinite(raw_hidden).all(axis=1) & np.isfinite(raw_logits).all(axis=1)
        raw_nonzero_state = np.any(raw_hidden != np.float32(0.0), axis=1)
        raw_nonzero_logits = np.any(raw_logits != np.float32(0.0), axis=1)
        raw_valid = raw_finite & raw_nonzero_state & raw_nonzero_logits
        raw_prediction = np.argmax(raw_logits, axis=1)
        projective_prediction = np.argmax(projective_logits, axis=1)
        raw_norm = np.linalg.norm(raw_hidden.astype(np.float64), axis=1)
        nonzero_norm = raw_norm[raw_norm > 0.0]
        output[str(depth)] = {
            "examples": examples,
            "raw_finite_fraction": float(np.mean(raw_finite)),
            "raw_nonzero_state_fraction": float(np.mean(raw_nonzero_state)),
            "raw_nonzero_logits_fraction": float(np.mean(raw_nonzero_logits)),
            "raw_valid_execution_fraction": float(np.mean(raw_valid)),
            "raw_accuracy_with_invalid_as_incorrect": float(
                np.mean((raw_prediction == batch.target) & raw_valid)
            ),
            "raw_accuracy_conditioned_on_valid": (
                float(np.mean(raw_prediction[raw_valid] == batch.target[raw_valid]))
                if np.any(raw_valid)
                else None
            ),
            "projective_accuracy": float(np.mean(projective_prediction == batch.target)),
            "raw_projective_agreement_with_invalid_as_incorrect": float(
                np.mean((raw_prediction == projective_prediction) & raw_valid)
            ),
            "raw_log10_l2_norm_when_nonzero": (
                summary(np.log10(nonzero_norm)) if nonzero_norm.size else None
            ),
        }
    return {
        "dtype": "float32",
        "backend": "NumPy emulation in source operation order; not bitwise PyTorch parity",
        "depths": output,
        "interpretation": "Zero states or zero logits are invalid executions, not class-zero predictions. Float64 continuation may preserve the same mathematical ray after float32 execution has underflowed.",
    }


def main() -> int:
    preregistration = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    checkpoints = load_inputs(preregistration)
    result: dict[str, Any] = {
        "schema": "komorebi.neuralese.causal_completion.posthoc_numeric.v1",
        "version": "0.2.1",
        "author": "Komorebi P.",
        "status": "post_hoc_after_registered_results_were_inspected",
        "no_retraining": True,
        "operator_spectra": {},
        "projective_checkpoint_underflow": {},
        "support_reconstruction": {},
    }
    for arm, by_seed in checkpoints.items():
        result["operator_spectra"][arm] = {
            str(seed): operator_spectrum(checkpoint, 970_000 + seed)
            for seed, checkpoint in by_seed.items()
        }
    for seed, checkpoint in checkpoints["projective_terminal"].items():
        result["projective_checkpoint_underflow"][str(seed)] = projective_underflow(
            checkpoint, 980_000 + seed
        )
        result["support_reconstruction"][str(seed)] = d4_support_reconstruction(
            checkpoint, 910_000 + 1000 * seed
        )
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.name, "status": "complete"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
