from __future__ import annotations

import torch


def metric_sqrt(metric: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    eigenvalues, eigenvectors = torch.linalg.eigh(metric)
    if float(eigenvalues.min()) <= 0:
        raise ValueError("metric must be positive definite")
    sqrt = (eigenvectors * eigenvalues.sqrt().unsqueeze(0)) @ eigenvectors.transpose(0, 1)
    inverse = (eigenvectors * eigenvalues.rsqrt().unsqueeze(0)) @ eigenvectors.transpose(0, 1)
    return sqrt, inverse


def metric_norm(hidden: torch.Tensor, metric: torch.Tensor | None = None) -> torch.Tensor:
    if metric is None:
        return torch.linalg.vector_norm(hidden, dim=-1)
    squared = torch.einsum("...i,ij,...j->...", hidden, metric, hidden).clamp_min(0)
    return squared.sqrt()


def normalize_ray(hidden: torch.Tensor, metric: torch.Tensor | None = None, eps: float = 1e-12) -> torch.Tensor:
    norm = metric_norm(hidden, metric).clamp_min(eps)
    return hidden / norm.unsqueeze(-1)


def positive_projective_distance(
    left: torch.Tensor,
    right: torch.Tensor,
    metric: torch.Tensor | None = None,
    eps: float = 1e-12,
) -> torch.Tensor:
    left_unit = normalize_ray(left, metric, eps)
    right_unit = normalize_ray(right, metric, eps)
    if metric is None:
        cosine = (left_unit * right_unit).sum(dim=-1)
    else:
        cosine = torch.einsum("...i,ij,...j->...", left_unit, metric, right_unit)
    cosine = cosine.clamp(-1.0, 1.0)
    return torch.acos(cosine)


def tangent_projector(unit_state: torch.Tensor, metric: torch.Tensor) -> torch.Tensor:
    """Project onto the G-tangent hyperplane at a G-unit state."""

    identity = torch.eye(unit_state.shape[-1], dtype=unit_state.dtype, device=unit_state.device)
    covector = unit_state @ metric.transpose(0, 1)
    return identity - unit_state.unsqueeze(-1) @ covector.unsqueeze(-2)


def projective_tangent_jacobian(
    operator: torch.Tensor,
    unit_state: torch.Tensor,
    metric: torch.Tensor,
    eps: float = 1e-12,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Derivative of z -> normalize_G(M z), plus its normalized endpoint."""

    endpoint_raw = (operator @ unit_state.unsqueeze(-1)).squeeze(-1)
    scale = metric_norm(endpoint_raw, metric).clamp_min(eps)
    endpoint = endpoint_raw / scale.unsqueeze(-1)
    projector = tangent_projector(endpoint, metric)
    jacobian = projector @ operator / scale[..., None, None]
    return jacobian, endpoint


def metric_operator_norm(operator: torch.Tensor, metric: torch.Tensor) -> torch.Tensor:
    sqrt, inverse = metric_sqrt(metric)
    whitened = sqrt @ operator @ inverse
    return torch.linalg.svdvals(whitened)[..., 0]
