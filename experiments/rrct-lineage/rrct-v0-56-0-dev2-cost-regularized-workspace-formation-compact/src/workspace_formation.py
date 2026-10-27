from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

TAU = 2.0 * math.pi
PAIRINGS = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
TASK_NAMES = ("local", "flat", "pair_01_23", "pair_02_13", "pair_03_12", "overlap")
ROUTE_NAMES = ("local", "flat", "pair_01_23", "pair_02_13", "pair_03_12", "full_overlap")
ROUTE_COSTS = torch.tensor((0.0, 1.0, 2.5, 2.5, 2.5, 4.0))

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def deterministic_seed(label: str) -> int:
    digest = hashlib.sha256(label.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % 2_000_000_000 + 1


def phase(value: torch.Tensor) -> torch.Tensor:
    return torch.stack((torch.cos(TAU * value), torch.sin(TAU * value)), dim=-1)


def _projection() -> torch.Tensor:
    generator = torch.Generator().manual_seed(deterministic_seed("rrct.v056.dev2.cue-projection"))
    matrix = torch.randn(10, 12, generator=generator)
    return matrix / torch.linalg.vector_norm(matrix, dim=0, keepdim=True).clamp_min(1e-8)


CUE_PROJECTION = _projection()


def task_signatures() -> torch.Tensor:
    signatures = torch.zeros(6, 10)
    signatures[0, 9] = 1.0
    signatures[1, :6] = 1.0
    signatures[1, 6] = 1.0
    for task, pairing in enumerate(PAIRINGS, start=2):
        for edge_index, edge in enumerate(EDGES):
            if set(edge) in (set(pairing[0]), set(pairing[1])):
                signatures[task, edge_index] = 1.0
        signatures[task, 6] = 1.0
        signatures[task, 7] = 1.0
    overlap_edges = {(0, 1), (2, 3), (0, 2), (1, 3)}
    for edge_index, edge in enumerate(EDGES):
        if edge in overlap_edges:
            signatures[5, edge_index] = 1.0
    signatures[5, 6:9] = 1.0
    return signatures


SIGNATURES = task_signatures()


def task_cue(task_ids: torch.Tensor, noise: torch.Tensor | None = None) -> torch.Tensor:
    cue = torch.tanh(SIGNATURES[task_ids] @ CUE_PROJECTION)
    return cue if noise is None else cue + noise


def local_actions(values: torch.Tensor) -> torch.Tensor:
    return values


def flat_actions(values: torch.Tensor) -> torch.Tensor:
    total = torch.remainder(values.sum(dim=1), 1.0)
    return torch.remainder(values + total[:, None], 1.0)


def pair_actions(values: torch.Tensor, pairing: tuple[tuple[int, int], tuple[int, int]]) -> torch.Tensor:
    left, right = pairing
    u = torch.remainder(values[:, left[0]] + values[:, left[1]], 1.0)
    v = torch.remainder(values[:, right[0]] + values[:, right[1]], 1.0)
    global_state = torch.remainder(u + v, 1.0)
    actions = values.clone()
    actions[:, list(left)] = torch.remainder(values[:, list(left)] + u[:, None] + global_state[:, None], 1.0)
    actions[:, list(right)] = torch.remainder(values[:, list(right)] + v[:, None] + global_state[:, None], 1.0)
    return actions


def overlap_actions(values: torch.Tensor) -> torch.Tensor:
    first = pair_actions(values, PAIRINGS[0])
    second = pair_actions(values, PAIRINGS[1])
    return torch.remainder(first + second - values, 1.0)


def target_actions(values: torch.Tensor, task_ids: torch.Tensor) -> torch.Tensor:
    actions = torch.empty_like(values)
    for task in range(6):
        mask = task_ids == task
        if not mask.any():
            continue
        if task == 0:
            selected = local_actions(values[mask])
        elif task == 1:
            selected = flat_actions(values[mask])
        elif task < 5:
            selected = pair_actions(values[mask], PAIRINGS[task - 2])
        else:
            selected = overlap_actions(values[mask])
        actions[mask] = selected
    return actions


def route_outputs(values: torch.Tensor, task_ids: torch.Tensor) -> torch.Tensor:
    outputs: list[torch.Tensor] = []
    outputs.append(phase(local_actions(values)))

    flat = torch.empty_like(values)
    local_mask = task_ids == 0
    flat[local_mask] = local_actions(values[local_mask])
    flat[~local_mask] = flat_actions(values[~local_mask])
    outputs.append(phase(flat))

    for pairing in PAIRINGS:
        candidate = torch.empty_like(values)
        flat_mask = task_ids == 1
        other_mask = ~(local_mask | flat_mask)
        candidate[local_mask] = local_actions(values[local_mask])
        candidate[flat_mask] = flat_actions(values[flat_mask])
        candidate[other_mask] = pair_actions(values[other_mask], pairing)
        outputs.append(phase(candidate))

    outputs.append(phase(target_actions(values, task_ids)))
    return torch.stack(outputs, dim=1)


def sample_batch(n: int, generator: torch.Generator, noise_std: float = 0.08) -> dict[str, torch.Tensor]:
    values = torch.rand(n, 4, generator=generator)
    task_ids = torch.randint(0, 6, (n,), generator=generator)
    noise = torch.randn(n, 12, generator=generator) * noise_std
    return {
        "values": values,
        "task_ids": task_ids,
        "cue": task_cue(task_ids, noise),
        "target": phase(target_actions(values, task_ids)),
        "routes": route_outputs(values, task_ids),
    }


def route_losses(routes: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return (1.0 - (routes * target[:, None]).sum(dim=-1)).mean(dim=-1)


class Router(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(12, 32),
            nn.Tanh(),
            nn.Linear(32, 32),
            nn.Tanh(),
            nn.Linear(32, 6),
        )

    def forward(self, cue: torch.Tensor) -> torch.Tensor:
        return self.network(cue)


def _new_router(seed: int) -> Router:
    torch.manual_seed(seed)
    router = Router()
    nn.init.zeros_(router.network[-1].weight)
    nn.init.zeros_(router.network[-1].bias)
    return router


def train_counterfactual(
    seed: int,
    *,
    lambda_cost: float,
    steps: int = 300,
    batch_size: int = 512,
    noise_std: float = 0.08,
    target_temperature: float = 0.05,
) -> Router:
    router = _new_router(seed)
    optimizer = torch.optim.AdamW(router.parameters(), lr=0.004, weight_decay=1e-5)
    generator = torch.Generator().manual_seed(seed ^ 0xC0A1)
    for _ in range(steps):
        batch = sample_batch(batch_size, generator, noise_std)
        scores = route_losses(batch["routes"], batch["target"]) + lambda_cost * ROUTE_COSTS
        counterfactual_target = F.softmax(-scores / target_temperature, dim=-1)
        log_probability = F.log_softmax(router(batch["cue"]), dim=-1)
        loss = -(counterfactual_target.detach() * log_probability).sum(dim=-1).mean()
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    return router


def train_naive(
    seed: int,
    *,
    lambda_cost: float,
    steps: int = 400,
    batch_size: int = 512,
    noise_std: float = 0.08,
) -> Router:
    router = _new_router(seed)
    optimizer = torch.optim.AdamW(router.parameters(), lr=0.005, weight_decay=1e-5)
    generator = torch.Generator().manual_seed(seed ^ 0x5A17)
    for _ in range(steps):
        batch = sample_batch(batch_size, generator, noise_std)
        probability = F.softmax(router(batch["cue"]), dim=-1)
        losses = route_losses(batch["routes"], batch["target"])
        loss = (probability * losses).sum(dim=-1).mean() + lambda_cost * (probability * ROUTE_COSTS).sum(dim=-1).mean()
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    return router


def strict_accuracy(prediction: torch.Tensor, target: torch.Tensor, threshold: float = 0.99) -> float:
    return float(((prediction * target).sum(dim=-1) >= threshold).float().mean().item())


@dataclass(frozen=True)
class Evaluation:
    task_accuracy: float
    route_accuracy: float
    mean_cost: float
    oracle_cost: float
    excess_cost: float
    route_by_task: tuple[tuple[float, ...], ...]
    accuracy_by_task: tuple[float, ...]


def evaluate(router: Router, batch: dict[str, torch.Tensor]) -> Evaluation:
    with torch.no_grad():
        route = router(batch["cue"]).argmax(dim=-1)
        prediction = batch["routes"][torch.arange(len(route)), route]
    route_by_task: list[tuple[float, ...]] = []
    accuracy_by_task: list[float] = []
    for task in range(6):
        mask = batch["task_ids"] == task
        distribution = torch.bincount(route[mask], minlength=6).float() / mask.sum()
        route_by_task.append(tuple(float(value) for value in distribution))
        accuracy_by_task.append(strict_accuracy(prediction[mask], batch["target"][mask]))
    mean_cost = float(ROUTE_COSTS[route].mean().item())
    oracle_cost = float(ROUTE_COSTS[batch["task_ids"]].mean().item())
    return Evaluation(
        task_accuracy=strict_accuracy(prediction, batch["target"]),
        route_accuracy=float((route == batch["task_ids"]).float().mean().item()),
        mean_cost=mean_cost,
        oracle_cost=oracle_cost,
        excess_cost=mean_cost - oracle_cost,
        route_by_task=tuple(route_by_task),
        accuracy_by_task=tuple(accuracy_by_task),
    )


@dataclass(frozen=True)
class SeedResult:
    schema: str
    seed: int
    lambda_cost: float
    task_accuracy: float
    route_accuracy: float
    mean_cost: float
    oracle_cost: float
    excess_cost: float
    route_by_task: tuple[tuple[float, ...], ...]
    accuracy_by_task: tuple[float, ...]
    shuffled_cue_task_accuracy: float
    shuffled_cue_route_accuracy: float
    dissolution_accuracy: float
    graph_switch_accuracy: float
    route_patch_change_rate: float
    router_uses_task_ids: bool
    candidate_graphs_supplied: bool
    task_specification_supplied: bool
    valence_model_present: bool
    self_preservation_reward: float


def evaluate_seed(
    seed: int,
    *,
    lambda_cost: float = 0.12,
    evaluation_cases: int = 20000,
    noise_std: float = 0.08,
) -> SeedResult:
    router = train_counterfactual(seed, lambda_cost=lambda_cost, noise_std=noise_std)
    evaluation = sample_batch(
        evaluation_cases,
        torch.Generator().manual_seed(deterministic_seed(f"{seed}:evaluation")),
        noise_std,
    )
    metric = evaluate(router, evaluation)
    with torch.no_grad():
        selected = router(evaluation["cue"]).argmax(dim=-1)
        prediction = evaluation["routes"][torch.arange(evaluation_cases), selected]

    permutation = torch.randperm(
        evaluation_cases,
        generator=torch.Generator().manual_seed(deterministic_seed(f"{seed}:shuffle")),
    )
    with torch.no_grad():
        shuffled_route = router(evaluation["cue"][permutation]).argmax(dim=-1)
        shuffled_prediction = evaluation["routes"][torch.arange(evaluation_cases), shuffled_route]

    transition_generator = torch.Generator().manual_seed(deterministic_seed(f"{seed}:transition"))
    previous_task = torch.randint(0, 6, (12000,), generator=transition_generator)
    current_task = torch.randint(0, 6, (12000,), generator=transition_generator)
    transition_noise = torch.randn(12000, 12, generator=transition_generator) * noise_std
    with torch.no_grad():
        current_route = router(task_cue(current_task, transition_noise)).argmax(dim=-1)
    dissolution_mask = (previous_task != 0) & (current_task == 0)
    switch_mask = previous_task != current_task

    patch_map = torch.tensor((0, 0, 3, 4, 2, 0))
    patched_route = patch_map[evaluation["task_ids"]]
    patched_prediction = evaluation["routes"][torch.arange(evaluation_cases), patched_route]
    patch_mask = evaluation["task_ids"] != 0
    changed = (patched_prediction[patch_mask] * prediction[patch_mask]).sum(dim=-1).mean(dim=-1) < 0.99

    return SeedResult(
        schema="rrct.v056.workspace_formation_seed.v2",
        seed=seed,
        lambda_cost=lambda_cost,
        task_accuracy=metric.task_accuracy,
        route_accuracy=metric.route_accuracy,
        mean_cost=metric.mean_cost,
        oracle_cost=metric.oracle_cost,
        excess_cost=metric.excess_cost,
        route_by_task=metric.route_by_task,
        accuracy_by_task=metric.accuracy_by_task,
        shuffled_cue_task_accuracy=strict_accuracy(shuffled_prediction, evaluation["target"]),
        shuffled_cue_route_accuracy=float((shuffled_route == evaluation["task_ids"]).float().mean().item()),
        dissolution_accuracy=float((current_route[dissolution_mask] == 0).float().mean().item()),
        graph_switch_accuracy=float((current_route[switch_mask] == current_task[switch_mask]).float().mean().item()),
        route_patch_change_rate=float(changed.float().mean().item()),
        router_uses_task_ids=False,
        candidate_graphs_supplied=True,
        task_specification_supplied=True,
        valence_model_present=False,
        self_preservation_reward=0.0,
    )


def jsonable(result: SeedResult) -> dict[str, object]:
    return asdict(result)
