from __future__ import annotations

import json
import argparse
from pathlib import Path

import numpy as np

from multispace_core import (
    adjusted_overlap,
    balanced_basis,
    consensus_basis,
    gram_from_samples,
    overlap,
    pairwise_overlap_matrix,
    pca_basis,
    persistent_basis,
    predictive_basis,
    random_overlap_null,
)


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate multi-space estimators on planted and null systems")
    parser.add_argument("--output", default="synthetic_validation_results.json")
    return parser.parse_args()


def planted_positive(seed: int = 610001) -> dict:
    rng = np.random.default_rng(seed)
    n, d, rank = 1800, 48, 4
    truth, _ = np.linalg.qr(rng.normal(size=(d, rank)), mode="reduced")
    source = rng.normal(size=(n, d))
    latent = source @ truth
    future_update = 2.0 * latent @ truth.T + 0.20 * rng.normal(size=(n, d))
    future = 0.25 * source + 1.75 * latent @ truth.T + 0.20 * rng.normal(size=(n, d))
    incoming = 1.5 * rng.normal(size=(n, rank)) @ truth.T + 0.20 * rng.normal(size=(n, d))
    read_gram = 4.0 * (truth @ truth.T) + 0.05 * np.eye(d)

    p, _ = predictive_basis(source, future_update, rank)
    t, _ = persistent_basis(source, future, rank)
    c, _ = pca_basis(incoming, rank)
    o, _ = np.linalg.eigh(read_gram)
    o, _ = pca_basis(rng.multivariate_normal(np.zeros(d), read_gram, size=n), rank)
    b, _ = balanced_basis(gram_from_samples(incoming), read_gram, rank)
    verbal = truth + 0.025 * rng.normal(size=truth.shape)
    verbal, _ = np.linalg.qr(verbal, mode="reduced")
    consensus, spectrum = consensus_basis([p, t, c, o, b], rank)

    shuffled = future_update[rng.permutation(n)]
    p_shuffled, _ = predictive_basis(source, shuffled, rank)
    null = random_overlap_null(consensus, rank, 128, seed + 1)

    return {
        "truth_consensus_overlap": overlap(truth, consensus),
        "verbal_consensus_overlap": overlap(verbal, consensus),
        "verbal_consensus_adjusted": adjusted_overlap(verbal, consensus),
        "shuffled_predictive_truth_overlap": overlap(p_shuffled, truth),
        "consensus_spectrum": spectrum.tolist(),
        "random_null_mean": null["mean"],
        "bases": {"V": verbal, "P": p, "T": t, "C": c, "O": o, "B": b, "W": consensus},
    }


def independent_null(seed: int = 610002) -> dict:
    rng = np.random.default_rng(seed)
    n, d, rank = 1600, 48, 4
    source = rng.normal(size=(n, d))
    future_update = rng.normal(size=(n, d))
    future = rng.normal(size=(n, d))
    incoming = rng.normal(size=(n, d))
    random_read = rng.normal(size=(d, d))
    read_gram = random_read.T @ random_read
    p, _ = predictive_basis(source, future_update, rank)
    t, _ = persistent_basis(source, future, rank)
    c, _ = pca_basis(incoming, rank)
    o, _ = pca_basis(rng.multivariate_normal(np.zeros(d), read_gram, size=n), rank)
    b, _ = balanced_basis(gram_from_samples(incoming), read_gram, rank)
    consensus, _ = consensus_basis([p, t, c, o, b], rank)
    verbal, _ = np.linalg.qr(rng.normal(size=(d, rank)), mode="reduced")
    return {"verbal_consensus_overlap": overlap(verbal, consensus)}


def main() -> int:
    args = parse_args()
    positive = planted_positive()
    null = independent_null()
    names, matrix = pairwise_overlap_matrix(positive.pop("bases"))

    checks = {
        "truth_recovered": positive["truth_consensus_overlap"] >= 0.85,
        "verbal_converges": positive["verbal_consensus_overlap"] >= 0.85,
        "shuffle_breaks_prediction": positive["shuffled_predictive_truth_overlap"] <= 0.35,
        "null_does_not_fake_convergence": null["verbal_consensus_overlap"] <= 0.35,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "positive": positive,
        "independent_null": null,
        "overlap_names": names,
        "overlap_matrix": matrix.tolist(),
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"V061_SYNTHETIC_MULTISPACE={result['status']}")
    for name, passed in checks.items():
        print(f"{name.upper()}={passed}")
    print(f"POSITIVE_V_W_OVERLAP={positive['verbal_consensus_overlap']:.6f}")
    print(f"NULL_V_W_OVERLAP={null['verbal_consensus_overlap']:.6f}")
    print(f"RESULT_FILE={output}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
