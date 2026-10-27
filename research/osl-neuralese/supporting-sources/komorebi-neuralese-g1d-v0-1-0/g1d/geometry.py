from __future__ import annotations

import math
from typing import Any


def _finite_float(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError("diagnostic geometry produced a nonfinite value")
    return result


def geometry_summary(features: Any, labels: Any) -> dict[str, Any]:
    import torch

    x = features.detach().cpu().double()
    y = labels.detach().cpu().long()
    if x.ndim != 2 or y.ndim != 1 or x.shape[0] != y.shape[0] or x.shape[0] < 2:
        raise ValueError("geometry expects [rows, features] and aligned labels")
    if not bool(torch.isfinite(x).all().item()):
        raise RuntimeError("geometry received nonfinite features")
    mean = x.mean(dim=0, keepdim=True)
    centered = x - mean
    raw_energy = x.square().sum()
    centered_energy = centered.square().sum()
    if centered.shape[1] <= centered.shape[0]:
        covariance = centered.T @ centered
    else:
        covariance = centered @ centered.T
    eigenvalues = torch.linalg.eigvalsh(covariance).clamp_min(0.0).flip(0)
    eigenvalues = eigenvalues / max(1, x.shape[0] - 1)
    total_eigenvalue = eigenvalues.sum()
    maximum_eigenvalue = eigenvalues.max() if eigenvalues.numel() else x.new_zeros(())
    positive = eigenvalues[eigenvalues > max(float(total_eigenvalue) * 1e-12, 1e-18)]
    if float(total_eigenvalue) > 0.0:
        probabilities = positive / positive.sum()
        entropy_rank = torch.exp(-(probabilities * probabilities.log()).sum())
        participation_rank = total_eigenvalue.square() / eigenvalues.square().sum().clamp_min(1e-30)
        stable_rank = total_eigenvalue / maximum_eigenvalue.clamp_min(1e-30)
        top_fraction = maximum_eigenvalue / total_eigenvalue
    else:
        entropy_rank = x.new_zeros(())
        participation_rank = x.new_zeros(())
        stable_rank = x.new_zeros(())
        top_fraction = x.new_zeros(())

    norms = x.norm(dim=1)
    nonzero_norm = norms > 1e-30
    normalized = x / norms.clamp_min(1e-30).unsqueeze(1)
    summed = normalized.sum(dim=0)
    count = x.shape[0]
    cosine_count = int(nonzero_norm.sum().item())
    mean_pairwise_cosine = (
        (summed.square().sum() - cosine_count)
        / (cosine_count * (cosine_count - 1))
        if cosine_count >= 2
        else x.new_zeros(())
    )

    classes = sorted(int(value) for value in torch.unique(y).tolist())
    centroids = []
    within_energy = x.new_zeros(())
    between_energy = x.new_zeros(())
    class_counts: dict[str, int] = {}
    for value in classes:
        group = x[y == value]
        centroid = group.mean(dim=0)
        centroids.append(centroid)
        class_counts[str(value)] = int(group.shape[0])
        within_energy += (group - centroid).square().sum()
        between_energy += group.shape[0] * (centroid - mean.squeeze(0)).square().sum()
    centroid_distances = []
    for left in range(len(centroids)):
        for right in range(left + 1, len(centroids)):
            centroid_distances.append((centroids[left] - centroids[right]).norm())
    within_rms = torch.sqrt(within_energy / max(1, count))
    if centroid_distances:
        centroid_tensor = torch.stack(centroid_distances)
        centroid_min = centroid_tensor.min()
        centroid_mean = centroid_tensor.mean()
    else:
        centroid_min = x.new_zeros(())
        centroid_mean = x.new_zeros(())

    return {
        "rows": int(x.shape[0]),
        "features": int(x.shape[1]),
        "class_counts": class_counts,
        "mean_vector_norm": _finite_float(mean.norm()),
        "mean_row_norm": _finite_float(norms.mean()),
        "centered_rms_norm": _finite_float(torch.sqrt(centered_energy / count)),
        "centered_to_raw_energy_ratio": _finite_float(
            centered_energy / raw_energy.clamp_min(1e-30)
        ),
        "mean_pairwise_cosine": _finite_float(mean_pairwise_cosine),
        "covariance_numerical_rank": int(positive.numel()),
        "covariance_stable_rank": _finite_float(stable_rank),
        "covariance_participation_rank": _finite_float(participation_rank),
        "covariance_entropy_rank": _finite_float(entropy_rank),
        "top_component_variance_fraction": _finite_float(top_fraction),
        "between_class_variance_fraction": _finite_float(
            between_energy / centered_energy.clamp_min(1e-30)
        ),
        "within_class_rms_norm": _finite_float(within_rms),
        "centroid_distance_minimum": _finite_float(centroid_min),
        "centroid_distance_mean": _finite_float(centroid_mean),
        "centroid_minimum_to_within_rms": _finite_float(
            centroid_min / within_rms.clamp_min(1e-30)
        ),
    }


def paired_geometry(left: Any, right: Any) -> dict[str, Any]:
    import torch

    a = left.detach().cpu().double()
    b = right.detach().cpu().double()
    if a.shape != b.shape or a.ndim != 2:
        raise ValueError("paired geometry requires aligned matrices")
    if not bool(torch.isfinite(a).all().item()) or not bool(torch.isfinite(b).all().item()):
        raise RuntimeError("paired geometry received nonfinite values")
    delta = a - b
    left_norm = a.norm(dim=1)
    delta_norm = delta.norm(dim=1)
    cosine = (a * b).sum(dim=1) / (
        a.norm(dim=1).clamp_min(1e-30) * b.norm(dim=1).clamp_min(1e-30)
    )
    centered_a = a - a.mean(dim=0, keepdim=True)
    centered_b = b - b.mean(dim=0, keepdim=True)
    if a.shape[0] <= a.shape[1]:
        gram_a = centered_a @ centered_a.T
        gram_b = centered_b @ centered_b.T
        cross_energy = (gram_a * gram_b).sum()
    else:
        cross_energy = (centered_a.T @ centered_b).square().sum()
        gram_a = centered_a.T @ centered_a
        gram_b = centered_b.T @ centered_b
    linear_cka = cross_energy / torch.sqrt(
        gram_a.square().sum().clamp_min(1e-30)
        * gram_b.square().sum().clamp_min(1e-30)
    )
    centered_dispersion = (a - a.mean(dim=0, keepdim=True)).norm(dim=1).mean()
    return {
        "rows": int(a.shape[0]),
        "mean_l2_difference": _finite_float(delta_norm.mean()),
        "maximum_l2_difference": _finite_float(delta_norm.max()),
        "mean_relative_l2_difference": _finite_float(
            (delta_norm / left_norm.clamp_min(1e-30)).mean()
        ),
        "mean_cosine_similarity": _finite_float(cosine.mean()),
        "linear_cka": _finite_float(linear_cka),
        "difference_to_across_instance_dispersion": _finite_float(
            delta_norm.mean() / centered_dispersion.clamp_min(1e-30)
        ),
    }


def matrix_spectrum(tensor: Any) -> dict[str, Any]:
    import torch

    matrix = tensor.detach().cpu().double()
    if (
        matrix.ndim != 2
        or min(matrix.shape) == 0
        or not bool(torch.isfinite(matrix).all().item())
    ):
        raise ValueError("matrix spectrum requires a finite nonempty rank-two tensor")
    singular = torch.linalg.svdvals(matrix)
    squared = singular.square()
    raw_total = squared.sum()
    if float(raw_total) == 0.0:
        return {
            "shape": [int(value) for value in matrix.shape],
            "frobenius_norm": 0.0,
            "spectral_norm": 0.0,
            "stable_rank": 0.0,
            "entropy_effective_rank": 0.0,
            "top1_energy_fraction": 0.0,
            "top2_energy_fraction": 0.0,
            "rank_for_95pct_energy": 0,
            "rank_for_99pct_energy": 0,
            "largest_singular_values": [
                0.0 for _ in singular[: min(12, singular.numel())]
            ],
        }
    total = raw_total
    cumulative = torch.cumsum(squared, dim=0) / total

    def rank_at(fraction: float) -> int:
        return int(torch.searchsorted(cumulative, cumulative.new_tensor(fraction)).item()) + 1

    probabilities = squared[squared > float(total) * 1e-15]
    probabilities = probabilities / probabilities.sum()
    return {
        "shape": [int(value) for value in matrix.shape],
        "frobenius_norm": _finite_float(torch.sqrt(total)),
        "spectral_norm": _finite_float(singular[0]),
        "stable_rank": _finite_float(total / squared[0].clamp_min(1e-30)),
        "entropy_effective_rank": _finite_float(
            torch.exp(-(probabilities * probabilities.log()).sum())
        ),
        "top1_energy_fraction": _finite_float(squared[0] / total),
        "top2_energy_fraction": _finite_float(squared[:2].sum() / total),
        "rank_for_95pct_energy": rank_at(0.95),
        "rank_for_99pct_energy": rank_at(0.99),
        "largest_singular_values": [
            _finite_float(value) for value in singular[: min(12, singular.numel())]
        ],
    }
