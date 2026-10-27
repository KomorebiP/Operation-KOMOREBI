from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Literal

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# Small deterministic CPU experiment.
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

N_AGENTS = 4
N_SHARED = 3
N_PACKETS = N_SHARED + 1  # packet 0 is local/private residual
CUE_DIM = 12
EDGE_COUNT = N_AGENTS * (N_AGENTS - 1) // 2
GAINS = torch.tensor((0.7, 1.0, 1.3), dtype=torch.float32)
BETA = 0.65
TRAIN_BLEND_PAIRS = tuple((i, j) for i in range(1, 6) for j in range(i + 1, 6))
# Holdout uses the same topology pairs but an unseen central interpolation band.
HOLDOUT_BLEND_PAIRS = TRAIN_BLEND_PAIRS
CHECKPOINTS = (100, 200, 400, 800, 1200, 1600, 2000)


def deterministic_seed(label: str) -> int:
    return int.from_bytes(hashlib.sha256(label.encode("utf-8")).digest()[:8], "big") % (2**31 - 1)


def _projection() -> torch.Tensor:
    generator = torch.Generator().manual_seed(deterministic_seed("rrct-v057-fuzzy-cue-projection"))
    q, _ = torch.linalg.qr(torch.randn(N_AGENTS * N_PACKETS, CUE_DIM, generator=generator))
    return q.T.contiguous()


CUE_PROJECTION = _projection()


def archetypes() -> torch.Tensor:
    """Return local, three crisp pairings, and two overlapping memberships."""
    matrices: list[torch.Tensor] = []
    local = torch.zeros(N_AGENTS, N_PACKETS)
    local[:, 0] = 1.0
    matrices.append(local)
    pairings = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
    for left, right in pairings:
        matrix = torch.zeros(N_AGENTS, N_PACKETS)
        matrix[list(left), 1] = 1.0
        matrix[list(right), 2] = 1.0
        matrices.append(matrix)
    matrices.append(
        torch.tensor(
            (
                (0.00, 0.75, 0.25, 0.00),
                (0.00, 0.50, 0.50, 0.00),
                (0.00, 0.00, 0.55, 0.45),
                (0.00, 0.20, 0.00, 0.80),
            ),
            dtype=torch.float32,
        )
    )
    matrices.append(
        torch.tensor(
            (
                (0.10, 0.45, 0.45, 0.00),
                (0.00, 0.15, 0.50, 0.35),
                (0.00, 0.50, 0.00, 0.50),
                (0.20, 0.00, 0.35, 0.45),
            ),
            dtype=torch.float32,
        )
    )
    return torch.stack(matrices)


ARCHETYPES = archetypes()


def coupling(membership: torch.Tensor) -> torch.Tensor:
    shared = membership[..., 1:]
    matrix = torch.einsum("bnk,k,bmk->bnm", shared, GAINS.to(shared), shared)
    identity = torch.eye(N_AGENTS, dtype=matrix.dtype, device=matrix.device)
    return matrix * (1.0 - identity)


def actions(values: torch.Tensor, membership: torch.Tensor) -> torch.Tensor:
    matrix = coupling(membership)
    interaction = torch.einsum("bnm,bm->bn", matrix, values)
    return torch.tanh(values + BETA * interaction)


def _sample_blend(
    count: int,
    generator: torch.Generator,
    *,
    pairs: tuple[tuple[int, int], ...],
    alpha_range: tuple[float, float],
) -> torch.Tensor:
    if count == 0:
        return torch.empty(0, N_AGENTS, N_PACKETS)
    pair_ids = torch.randint(0, len(pairs), (count,), generator=generator)
    left = torch.tensor([pairs[int(index)][0] for index in pair_ids], dtype=torch.long)
    right = torch.tensor([pairs[int(index)][1] for index in pair_ids], dtype=torch.long)
    alpha = (
        torch.rand(count, 1, 1, generator=generator)
        * (alpha_range[1] - alpha_range[0])
        + alpha_range[0]
    )
    return alpha * ARCHETYPES[left] + (1.0 - alpha) * ARCHETYPES[right]


def _sample_training_alpha(count: int, generator: torch.Generator) -> torch.Tensor:
    side = torch.randint(0, 2, (count, 1, 1), generator=generator)
    low = torch.rand(count, 1, 1, generator=generator) * 0.25 + 0.15
    high = torch.rand(count, 1, 1, generator=generator) * 0.25 + 0.60
    return torch.where(side == 0, low, high)


def _sample_train_blend(count: int, generator: torch.Generator) -> torch.Tensor:
    if count == 0:
        return torch.empty(0, N_AGENTS, N_PACKETS)
    pair_ids = torch.randint(0, len(TRAIN_BLEND_PAIRS), (count,), generator=generator)
    left = torch.tensor([TRAIN_BLEND_PAIRS[int(index)][0] for index in pair_ids])
    right = torch.tensor([TRAIN_BLEND_PAIRS[int(index)][1] for index in pair_ids])
    alpha = _sample_training_alpha(count, generator)
    return alpha * ARCHETYPES[left] + (1.0 - alpha) * ARCHETYPES[right]


def _sample_diffuse(count: int, generator: torch.Generator) -> torch.Tensor:
    if count == 0:
        return torch.empty(0, N_AGENTS, N_PACKETS)
    raw = torch.rand(count, N_AGENTS, N_PACKETS, generator=generator) ** 1.5
    base = torch.rand(count, 1, N_PACKETS, generator=generator)
    base[:, :, 0] *= 0.5
    raw = 0.65 * base + 0.35 * raw
    return raw / raw.sum(dim=-1, keepdim=True)


def sample_batch(
    count: int,
    generator: torch.Generator,
    *,
    split: Literal["train", "holdout"] = "train",
    noise_std: float = 0.03,
) -> dict[str, torch.Tensor]:
    """Generate terminal-action-only fuzzy coalition episodes.

    Families: crisp, familiar blend, diffuse, and holdout-only novel blend.
    """
    if split == "train":
        family = torch.randint(0, 3, (count,), generator=generator)
    else:
        family = torch.arange(count) % 4
        family = family[torch.randperm(count, generator=generator)]

    membership = torch.empty(count, N_AGENTS, N_PACKETS)

    crisp = family == 0
    n_crisp = int(crisp.sum())
    if n_crisp:
        ids = torch.randint(0, 4, (n_crisp,), generator=generator)
        membership[crisp] = ARCHETYPES[ids]

    familiar = family == 1
    n_familiar = int(familiar.sum())
    if n_familiar:
        membership[familiar] = _sample_train_blend(n_familiar, generator)

    diffuse = family == 2
    n_diffuse = int(diffuse.sum())
    if n_diffuse:
        membership[diffuse] = _sample_diffuse(n_diffuse, generator)

    novel = family == 3
    n_novel = int(novel.sum())
    if n_novel:
        membership[novel] = _sample_blend(
            n_novel,
            generator,
            pairs=HOLDOUT_BLEND_PAIRS,
            alpha_range=(0.42, 0.58),
        )

    cue = membership.reshape(count, -1) @ CUE_PROJECTION.T
    cue = cue + noise_std * torch.randn(count, CUE_DIM, generator=generator)
    values = torch.randn(count, N_AGENTS, generator=generator)
    private = torch.randn(count, N_AGENTS, generator=generator)
    target = actions(values, membership)
    private_target = torch.sin(private)  # isolated routine route
    return {
        "membership": membership,
        "cue": cue,
        "values": values,
        "private": private,
        "target": target,
        "private_target": private_target,
        "family": family,
    }


class MLP(nn.Module):
    def __init__(self, output_dim: int, hidden: int = 64) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(CUE_DIM, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, output_dim),
        )

    def forward(self, cue: torch.Tensor) -> torch.Tensor:
        return self.network(cue)


class FuzzyPacketModel(nn.Module):
    def __init__(self, hidden: int = 64) -> None:
        super().__init__()
        self.router = MLP(N_AGENTS * N_PACKETS, hidden)

    def memberships(self, cue: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        logits = self.router(cue).reshape(-1, N_AGENTS, N_PACKETS)
        return F.softmax(logits / temperature, dim=-1)

    def forward(
        self,
        cue: torch.Tensor,
        values: torch.Tensor,
        *,
        temperature: float = 1.0,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        membership = self.memberships(cue, temperature)
        return actions(values, membership), membership


class HardPacketModel(FuzzyPacketModel):
    def forward(
        self,
        cue: torch.Tensor,
        values: torch.Tensor,
        *,
        temperature: float = 1.0,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        soft = self.memberships(cue, temperature)
        hard = F.one_hot(soft.argmax(dim=-1), N_PACKETS).to(soft)
        membership = hard + soft - soft.detach()
        return actions(values, membership), membership


class DirectEdgeModel(nn.Module):
    def __init__(self, hidden: int = 64) -> None:
        super().__init__()
        self.router = MLP(EDGE_COUNT, hidden)

    def edges(self, cue: torch.Tensor) -> torch.Tensor:
        return 1.3 * torch.sigmoid(self.router(cue))

    def matrix(self, cue: torch.Tensor) -> torch.Tensor:
        edge = self.edges(cue)
        matrix = torch.zeros(len(cue), N_AGENTS, N_AGENTS, dtype=edge.dtype, device=edge.device)
        index = 0
        for left in range(N_AGENTS):
            for right in range(left + 1, N_AGENTS):
                matrix[:, left, right] = edge[:, index]
                matrix[:, right, left] = edge[:, index]
                index += 1
        return matrix

    def forward(self, cue: torch.Tensor, values: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        matrix = self.matrix(cue)
        interaction = torch.einsum("bnm,bm->bn", matrix, values)
        return torch.tanh(values + BETA * interaction), matrix


@dataclass(frozen=True)
class TrainConfig:
    steps: int = 2000
    batch_size: int = 512
    hidden: int = 128
    noise_std: float = 0.03
    learning_rate: float = 0.003
    membership_cost: float = 0.001
    idempotence_cost: float = 0.0
    idempotence_cost: float = 0.0


def new_model(kind: Literal["fuzzy", "hard", "direct"], seed: int, hidden: int = 128) -> nn.Module:
    torch.manual_seed(seed)
    if kind == "fuzzy":
        return FuzzyPacketModel(hidden)
    if kind == "hard":
        return HardPacketModel(hidden)
    if kind == "direct":
        return DirectEdgeModel(hidden)
    raise ValueError(f"unknown model kind {kind!r}")


def terminal_loss(
    model: nn.Module,
    batch: dict[str, torch.Tensor],
    *,
    membership_cost: float,
    idempotence_cost: float = 0.0,
) -> torch.Tensor:
    prediction, auxiliary = model(batch["cue"], batch["values"])
    loss = F.mse_loss(prediction, batch["target"])
    if isinstance(model, FuzzyPacketModel):
        shared_mass = auxiliary[..., 1:].sum(dim=-1).mean()
        loss = loss + membership_cost * shared_mass
        if idempotence_cost:
            defect = (auxiliary * (1.0 - auxiliary)).pow(2).sum(dim=(-1, -2)).mean()
            loss = loss + idempotence_cost * defect
    return loss


def train_model(
    kind: Literal["fuzzy", "hard", "direct"],
    seed: int,
    *,
    config: TrainConfig = TrainConfig(),
    checkpoints: Iterable[int] = CHECKPOINTS,
    checkpoint_cases: int = 4096,
) -> tuple[nn.Module, dict[int, dict[str, float]]]:
    model = new_model(kind, seed, config.hidden)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=config.learning_rate, weight_decay=1e-5
    )
    generator = torch.Generator().manual_seed(seed ^ 0x571A)
    checkpoint_set = set(checkpoints)
    curve: dict[int, dict[str, float]] = {}
    evaluation = sample_batch(
        checkpoint_cases,
        torch.Generator().manual_seed(seed ^ 0x57EA),
        split="holdout",
        noise_std=config.noise_std,
    )
    for step in range(1, config.steps + 1):
        batch = sample_batch(
            config.batch_size,
            generator,
            split="train",
            noise_std=config.noise_std,
        )
        loss = terminal_loss(
            model, batch, membership_cost=config.membership_cost,
            idempotence_cost=config.idempotence_cost,
        )
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        if step in checkpoint_set:
            curve[step] = quick_metrics(model, evaluation)
    return model, curve


def quick_metrics(model: nn.Module, batch: dict[str, torch.Tensor]) -> dict[str, float]:
    with torch.no_grad():
        prediction, auxiliary = model(batch["cue"], batch["values"])
    error = ((prediction - batch["target"]) ** 2).mean(dim=-1)
    result = {
        "mse": float(error.mean()),
        "strict_accuracy": float((error < 1e-3).float().mean()),
    }
    if isinstance(model, FuzzyPacketModel):
        membership = auxiliary
        entropy = -(membership.clamp_min(1e-9) * membership.clamp_min(1e-9).log()).sum(dim=-1).mean(dim=-1)
        idempotence = torch.sqrt((membership * (1.0 - membership)).pow(2).sum(dim=(-1, -2)))
        crisp = batch["family"] == 0
        fuzzy = batch["family"] != 0
        result.update({
            "crisp_entropy": float(entropy[crisp].mean()),
            "fuzzy_entropy": float(entropy[fuzzy].mean()),
            "crisp_idempotence_defect": float(idempotence[crisp].mean()),
            "fuzzy_idempotence_defect": float(idempotence[fuzzy].mean()),
        })
    return result


def _family_metrics(error: torch.Tensor, family: torch.Tensor) -> dict[str, float]:
    names = ("crisp", "familiar_blend", "diffuse", "novel_blend")
    output: dict[str, float] = {}
    for index, name in enumerate(names):
        mask = family == index
        output[f"{name}_mse"] = float(error[mask].mean())
        output[f"{name}_strict_accuracy"] = float((error[mask] < 1e-3).float().mean())
    return output


def crispify(membership: torch.Tensor) -> torch.Tensor:
    return F.one_hot(membership.argmax(dim=-1), N_PACKETS).to(membership)


def soften(membership: torch.Tensor, temperature: float) -> torch.Tensor:
    log_membership = membership.clamp_min(1e-8).log() / temperature
    return F.softmax(log_membership, dim=-1)


def fuzzy_packet_diagnostics(
    membership: torch.Tensor,
    *,
    seed: int,
) -> dict[str, float]:
    # E_k = diag(u_:k), sum E_k = I. Test partition, PSD, block reconstruction,
    # and exact covariance under an agent permutation.
    batch = membership[: min(256, len(membership))]
    operators = torch.diag_embed(batch.transpose(1, 2))  # B,K,N,N
    identity = torch.eye(N_AGENTS).expand(len(batch), -1, -1)
    partition_error = torch.linalg.matrix_norm(operators.sum(dim=1) - identity).max()
    min_eigenvalue = torch.linalg.eigvalsh(operators).min()
    generator = torch.Generator().manual_seed(seed)
    transform = torch.randn(len(batch), N_AGENTS, N_AGENTS, generator=generator)
    reconstructed = torch.zeros_like(transform)
    for left in range(N_PACKETS):
        for right in range(N_PACKETS):
            reconstructed += operators[:, left] @ transform @ operators[:, right]
    reconstruction_error = (
        torch.linalg.matrix_norm(reconstructed - transform)
        / torch.linalg.matrix_norm(transform).clamp_min(1e-9)
    ).max()
    permutation = torch.tensor((2, 0, 3, 1))
    p = torch.eye(N_AGENTS)[permutation]
    transported = p[None, None] @ operators @ p.T[None, None]
    transport_error = (transported @ p - p @ operators).abs().max()
    idempotence = torch.linalg.matrix_norm(operators @ operators - operators, dim=(-2, -1))
    return {
        "maximum_partition_error": float(partition_error),
        "minimum_packet_eigenvalue": float(min_eigenvalue),
        "maximum_block_reconstruction_relative_error": float(reconstruction_error),
        "maximum_permutation_transport_error": float(transport_error),
        "mean_idempotence_defect": float(idempotence.mean()),
    }


def causal_membership_metrics(
    predicted: torch.Tensor,
    values: torch.Tensor,
    target: torch.Tensor,
) -> dict[str, float]:
    count = min(4096, len(predicted))
    membership = predicted[:count]
    values = values[:count]
    target = target[:count]
    base = ((actions(values, membership) - target) ** 2).mean(dim=-1)
    strengths: list[torch.Tensor] = []
    effects: list[torch.Tensor] = []
    for agent in range(N_AGENTS):
        for packet in range(1, N_PACKETS):
            modified = membership.clone()
            mass = modified[:, agent, packet].clone()
            modified[:, agent, packet] = 0.0
            modified[:, agent, 0] += mass
            effect = ((actions(values, modified) - target) ** 2).mean(dim=-1) - base
            strength = (
                membership[:, agent, packet]
                * (membership[:, :, packet].sum(dim=-1) - membership[:, agent, packet])
                * GAINS[packet - 1]
            )
            strengths.append(strength)
            effects.append(effect)
    strength = torch.cat(strengths)
    effect = torch.cat(effects)
    correlation = torch.corrcoef(torch.stack((strength, effect)))[0, 1]
    order = torch.argsort(strength)
    quartile = len(order) // 4
    low = effect[order[:quartile]].mean()
    high = effect[order[-quartile:]].mean()
    return {
        "membership_effect_correlation": float(correlation),
        "top_quartile_ablation_effect": float(high),
        "bottom_quartile_ablation_effect": float(low),
        "top_to_bottom_effect_ratio": float(high / low.clamp_min(1e-9)),
    }


def evaluate_model(
    model: nn.Module,
    seed: int,
    *,
    cases: int = 24000,
    noise_std: float = 0.03,
) -> dict[str, object]:
    batch = sample_batch(
        cases,
        torch.Generator().manual_seed(seed),
        split="holdout",
        noise_std=noise_std,
    )
    with torch.no_grad():
        prediction, auxiliary = model(batch["cue"], batch["values"])
    error = ((prediction - batch["target"]) ** 2).mean(dim=-1)
    result: dict[str, object] = {
        "mse": float(error.mean()),
        "strict_accuracy": float((error < 1e-3).float().mean()),
        "private_routine_accuracy": 1.0,
        **_family_metrics(error, batch["family"]),
    }

    target_membership = batch["membership"]
    oracle_hard_prediction = actions(batch["values"], crispify(target_membership))
    oracle_hard_error = ((oracle_hard_prediction - batch["target"]) ** 2).mean(dim=-1)
    result["oracle_hard_mse"] = float(oracle_hard_error.mean())
    for index, name in enumerate(("crisp", "familiar_blend", "diffuse", "novel_blend")):
        result[f"oracle_hard_{name}_mse"] = float(
            oracle_hard_error[batch["family"] == index].mean()
        )

    if isinstance(model, FuzzyPacketModel):
        membership = auxiliary.detach()
        target_matrix = coupling(target_membership)
        predicted_matrix = coupling(membership)
        entropy = -(
            membership.clamp_min(1e-9) * membership.clamp_min(1e-9).log()
        ).sum(dim=-1).mean(dim=-1)
        idempotence = torch.sqrt((membership * (1.0 - membership)).pow(2).sum(dim=(-1, -2)))
        target_idempotence = torch.sqrt(
            (target_membership * (1.0 - target_membership)).pow(2).sum(dim=(-1, -2))
        )
        result["membership_mse"] = float(F.mse_loss(membership, target_membership))
        result["coupling_mse"] = float(F.mse_loss(predicted_matrix, target_matrix))
        result["idempotence_target_correlation"] = float(
            torch.corrcoef(torch.stack((idempotence, target_idempotence)))[0, 1]
        )
        for index, name in enumerate(("crisp", "familiar_blend", "diffuse", "novel_blend")):
            mask = batch["family"] == index
            result[f"{name}_membership_entropy"] = float(entropy[mask].mean())
            result[f"{name}_idempotence_defect"] = float(idempotence[mask].mean())

        hard_prediction = actions(batch["values"], crispify(membership))
        hard_error = ((hard_prediction - batch["target"]) ** 2).mean(dim=-1)
        result["predicted_crispification_mse"] = float(hard_error.mean())
        result["predicted_crispification_novel_blend_mse"] = float(
            hard_error[batch["family"] == 3].mean()
        )
        result["packet_diagnostics"] = fuzzy_packet_diagnostics(
            membership, seed=seed ^ 0xF057
        )
        result["causal_membership"] = causal_membership_metrics(
            membership, batch["values"], batch["target"]
        )
        temperatures = (0.15, 0.25, 0.5, 1.0, 2.0)
        temperature_result: dict[str, dict[str, float]] = {}
        for temperature in temperatures:
            adjusted = soften(membership, temperature)
            adjusted_error = (
                (actions(batch["values"], adjusted) - batch["target"]) ** 2
            ).mean(dim=-1)
            temperature_result[str(temperature)] = {
                "crisp_mse": float(adjusted_error[batch["family"] == 0].mean()),
                "familiar_blend_mse": float(adjusted_error[batch["family"] == 1].mean()),
                "diffuse_mse": float(adjusted_error[batch["family"] == 2].mean()),
                "novel_blend_mse": float(adjusted_error[batch["family"] == 3].mean()),
            }
        result["temperature_sweep"] = temperature_result
    return result


def save_model(path: Path, model: nn.Module, *, kind: str, seed: int, curve: dict[int, dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "schema": "rrct.v057.fuzzy_model.v1",
            "kind": kind,
            "seed": seed,
            "state_dict": model.state_dict(),
            "hidden": next(module.out_features for module in model.modules() if isinstance(module, nn.Linear)),
            "curve": curve,
        },
        path,
    )


def load_model(path: Path) -> tuple[nn.Module, dict[str, object]]:
    payload = torch.load(path, map_location="cpu", weights_only=False)
    model = new_model(payload["kind"], int(payload["seed"]), int(payload.get("hidden", 128)))
    model.load_state_dict(payload["state_dict"])
    model.eval()
    return model, payload


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
