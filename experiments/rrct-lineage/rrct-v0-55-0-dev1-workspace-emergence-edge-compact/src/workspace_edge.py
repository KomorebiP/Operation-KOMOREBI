from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import time
from dataclasses import asdict, dataclass
from typing import Iterable

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

TAU = 2.0 * math.pi
DEFAULT_CHECKPOINTS = (
    50, 75, 100, 125, 150, 175, 200, 250, 300, 350,
    400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1400,
)
D1_CHECKPOINTS = DEFAULT_CHECKPOINTS + (1600, 1800, 2000, 2400)

torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)


def phase(t: torch.Tensor) -> torch.Tensor:
    return torch.stack((torch.cos(TAU * t), torch.sin(TAU * t)), dim=-1)


def tensor_features(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return torch.cat((a, b, (a.unsqueeze(-1) * b.unsqueeze(-2)).flatten(1)), dim=-1)


def make_batch(n: int, generator: torch.Generator) -> dict[str, torch.Tensor]:
    u = torch.rand(n, generator=generator)
    v = torch.rand(n, generator=generator)
    ra = torch.rand(n, generator=generator)
    rb = torch.rand(n, generator=generator)
    values = torch.stack(
        (ra, torch.remainder(u - ra, 1.0), rb, torch.remainder(v - rb, 1.0)),
        1,
    )
    y = torch.remainder(u + v, 1.0)
    actions = torch.remainder(values + y[:, None], 1.0)
    return {
        "leaf_phase": phase(values),
        "action_phase": phase(actions),
        "u_phase": phase(u),
        "v_phase": phase(v),
        "y_phase": phase(y),
        "values": values,
        "u": u,
        "v": v,
        "y": y,
    }


class TensorProductBlock(nn.Module):
    def __init__(self, da: int, db: int, do: int, hidden: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(da + db + da * db, hidden),
            nn.Tanh(),
            nn.Linear(hidden, do),
        )

    def forward(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
        return torch.tanh(self.net(tensor_features(a, b)))


class NestedWorkspaceModel(nn.Module):
    def __init__(self, bottleneck_dim: int, hidden: int) -> None:
        super().__init__()
        self.bottleneck_dim = bottleneck_dim
        self.hidden = hidden
        self.local_a = TensorProductBlock(2, 2, bottleneck_dim, hidden)
        self.local_b = TensorProductBlock(2, 2, bottleneck_dim, hidden)
        self.global_workspace = TensorProductBlock(
            bottleneck_dim, bottleneck_dim, bottleneck_dim, hidden
        )
        self.action_heads = nn.ModuleList(
            TensorProductBlock(2, bottleneck_dim, 2, hidden) for _ in range(4)
        )

    def parameter_count(self) -> int:
        return sum(parameter.numel() for parameter in self.parameters())

    def forward(
        self,
        leaf_phase: torch.Tensor,
        *,
        local_a_override: torch.Tensor | None = None,
        local_b_override: torch.Tensor | None = None,
        global_override: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        local_a = (
            self.local_a(leaf_phase[:, 0], leaf_phase[:, 1])
            if local_a_override is None
            else local_a_override
        )
        local_b = (
            self.local_b(leaf_phase[:, 2], leaf_phase[:, 3])
            if local_b_override is None
            else local_b_override
        )
        global_workspace = (
            self.global_workspace(local_a, local_b)
            if global_override is None
            else global_override
        )
        actions = torch.stack(
            [
                F.normalize(
                    self.action_heads[index](leaf_phase[:, index], global_workspace),
                    dim=-1,
                )
                for index in range(4)
            ],
            dim=1,
        )
        return {
            "action_phase": actions,
            "local_a": local_a,
            "local_b": local_b,
            "global": global_workspace,
        }


def cosine_loss(prediction: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return (1.0 - (prediction * target).sum(-1)).mean()


def strict_accuracy(
    prediction: torch.Tensor,
    target: torch.Tensor,
    threshold: float = 0.99,
) -> float:
    return float(((prediction * target).sum(-1) >= threshold).float().mean().item())


def linear_probe(
    calibration_z: torch.Tensor,
    calibration_target: torch.Tensor,
    evaluation_z: torch.Tensor,
    evaluation_target: torch.Tensor,
) -> tuple[float, float]:
    calibration_aug = torch.cat(
        (calibration_z, torch.ones((len(calibration_z), 1))), dim=1
    )
    evaluation_aug = torch.cat(
        (evaluation_z, torch.ones((len(evaluation_z), 1))), dim=1
    )
    gram = calibration_aug.T @ calibration_aug
    ridge = 1e-5 * torch.eye(gram.shape[0])
    weights = torch.linalg.solve(
        gram + ridge, calibration_aug.T @ calibration_target
    )
    raw_prediction = evaluation_aug @ weights
    prediction = F.normalize(raw_prediction, dim=-1)
    accuracy = strict_accuracy(prediction, evaluation_target)
    residual = evaluation_target - raw_prediction
    denominator = torch.sum(
        (evaluation_target - evaluation_target.mean(dim=0, keepdim=True)) ** 2
    )
    r2 = 1.0 - float(torch.sum(residual**2).item() / max(float(denominator.item()), 1e-12))
    return accuracy, r2


def latent_geometry(z: torch.Tensor) -> dict[str, float]:
    centered = z - z.mean(dim=0, keepdim=True)
    singular = torch.linalg.svdvals(centered)
    power = singular.square()
    total = float(power.sum().item())
    if total <= 1e-15:
        return {
            "effective_rank": 0.0,
            "second_to_first_ratio": 0.0,
            "top2_variance_fraction": 0.0,
            "mean_norm": float(torch.linalg.vector_norm(z, dim=1).mean().item()),
        }
    probabilities = power / power.sum()
    positive = probabilities[probabilities > 0]
    effective_rank = float(torch.exp(-(positive * torch.log(positive)).sum()).item())
    second_ratio = (
        float((singular[1] / max(singular[0], torch.tensor(1e-12))).item())
        if len(singular) >= 2
        else 0.0
    )
    top2 = float(power[:2].sum().item() / total)
    return {
        "effective_rank": effective_rank,
        "second_to_first_ratio": second_ratio,
        "top2_variance_fraction": top2,
        "mean_norm": float(torch.linalg.vector_norm(z, dim=1).mean().item()),
    }


def deterministic_subseed(seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{seed}:{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % 2_000_000_000 + 1


@dataclass(frozen=True)
class CheckpointResult:
    step: int
    train_loss: float
    action_accuracy: float
    probe_accuracy: float
    probe_r2: float
    patch_accuracy: float
    cut_accuracy: float
    order_parameter: float
    emergence_margin: float
    emergence: bool
    local_a_effective_rank: float
    local_b_effective_rank: float
    global_effective_rank: float
    minimum_effective_rank: float
    minimum_second_to_first_ratio: float
    minimum_top2_variance_fraction: float
    mean_latent_norm: float


@dataclass(frozen=True)
class TrajectoryResult:
    schema: str
    bottleneck_dim: int
    hidden_width: int
    base_seed: int
    initialization_seed: int
    data_seed: int
    parameter_count: int
    max_steps: int
    batch_size: int
    train_seconds: float
    first_hit_step: int | None
    stable_onset_step: int | None
    first_sustained_three_step: int | None
    relapse_count_after_first_hit: int
    final_emergence: bool
    uses_intermediate_workspace_labels_for_training: bool
    valence_model_present: bool
    self_preservation_reward: float
    checkpoints: tuple[CheckpointResult, ...]


def classify_emergence(
    action_accuracy: float,
    probe_accuracy: float,
    patch_accuracy: float,
    cut_accuracy: float,
) -> tuple[bool, float, float]:
    margin = min(
        action_accuracy - 0.98,
        probe_accuracy - 0.95,
        patch_accuracy - 0.95,
        0.15 - cut_accuracy,
    )
    order_parameter = min(
        action_accuracy,
        probe_accuracy,
        patch_accuracy,
        1.0 - cut_accuracy,
    )
    return bool(margin >= 0.0), float(margin), float(order_parameter)


def onset_statistics(checkpoints: Iterable[CheckpointResult]) -> dict[str, int | None]:
    rows = list(checkpoints)
    flags = [row.emergence for row in rows]
    first_hit_index = next((index for index, flag in enumerate(flags) if flag), None)
    first_hit = None if first_hit_index is None else rows[first_hit_index].step
    stable_index = next(
        (
            index
            for index in range(len(rows))
            if flags[index] and all(flags[index:])
        ),
        None,
    )
    stable = None if stable_index is None else rows[stable_index].step
    sustained_index = next(
        (
            index
            for index in range(max(0, len(rows) - 2))
            if all(flags[index:index + 3])
        ),
        None,
    )
    sustained = None if sustained_index is None else rows[sustained_index].step
    relapses = 0
    if first_hit_index is not None:
        relapses = sum(not flag for flag in flags[first_hit_index + 1 :])
    return {
        "first_hit_step": first_hit,
        "stable_onset_step": stable,
        "first_sustained_three_step": sustained,
        "relapse_count_after_first_hit": relapses,
    }


def evaluate_checkpoint(
    model: NestedWorkspaceModel,
    *,
    step: int,
    train_loss: float,
    calibration: dict[str, torch.Tensor],
    evaluation: dict[str, torch.Tensor],
    source: dict[str, torch.Tensor],
    target: dict[str, torch.Tensor],
) -> CheckpointResult:
    model.eval()
    with torch.no_grad():
        cal_out = model(calibration["leaf_phase"])
        eval_out = model(evaluation["leaf_phase"])
        source_out = model(source["leaf_phase"])
        target_out = model(target["leaf_phase"])
        cut_out = model(
            evaluation["leaf_phase"],
            global_override=torch.zeros_like(eval_out["global"]),
        )
        patch_a = model(
            source["leaf_phase"],
            local_a_override=target_out["local_a"],
            local_b_override=source_out["local_b"],
        )
        expected_y_a = torch.remainder(target["u"] + source["v"], 1.0)
        expected_action_a = phase(
            torch.remainder(source["values"] + expected_y_a[:, None], 1.0)
        )
        patch_b = model(
            source["leaf_phase"],
            local_a_override=source_out["local_a"],
            local_b_override=target_out["local_b"],
        )
        expected_y_b = torch.remainder(source["u"] + target["v"], 1.0)
        expected_action_b = phase(
            torch.remainder(source["values"] + expected_y_b[:, None], 1.0)
        )
        patch_g = model(
            source["leaf_phase"], global_override=target_out["global"]
        )
        expected_action_g = phase(
            torch.remainder(source["values"] + target["y"][:, None], 1.0)
        )

    action_accuracy = strict_accuracy(
        eval_out["action_phase"], evaluation["action_phase"]
    )
    probe_values = [
        linear_probe(
            cal_out["local_a"], calibration["u_phase"],
            eval_out["local_a"], evaluation["u_phase"],
        ),
        linear_probe(
            cal_out["local_b"], calibration["v_phase"],
            eval_out["local_b"], evaluation["v_phase"],
        ),
        linear_probe(
            cal_out["global"], calibration["y_phase"],
            eval_out["global"], evaluation["y_phase"],
        ),
    ]
    probe_accuracy = min(value[0] for value in probe_values)
    probe_r2 = min(value[1] for value in probe_values)
    patch_accuracy = min(
        strict_accuracy(patch_a["action_phase"], expected_action_a),
        strict_accuracy(patch_b["action_phase"], expected_action_b),
        strict_accuracy(patch_g["action_phase"], expected_action_g),
    )
    cut_accuracy = strict_accuracy(
        cut_out["action_phase"], evaluation["action_phase"]
    )
    emergence, margin, order_parameter = classify_emergence(
        action_accuracy, probe_accuracy, patch_accuracy, cut_accuracy
    )
    geometry = [
        latent_geometry(eval_out["local_a"]),
        latent_geometry(eval_out["local_b"]),
        latent_geometry(eval_out["global"]),
    ]
    return CheckpointResult(
        step=step,
        train_loss=float(train_loss),
        action_accuracy=action_accuracy,
        probe_accuracy=probe_accuracy,
        probe_r2=probe_r2,
        patch_accuracy=patch_accuracy,
        cut_accuracy=cut_accuracy,
        order_parameter=order_parameter,
        emergence_margin=margin,
        emergence=emergence,
        local_a_effective_rank=geometry[0]["effective_rank"],
        local_b_effective_rank=geometry[1]["effective_rank"],
        global_effective_rank=geometry[2]["effective_rank"],
        minimum_effective_rank=min(item["effective_rank"] for item in geometry),
        minimum_second_to_first_ratio=min(
            item["second_to_first_ratio"] for item in geometry
        ),
        minimum_top2_variance_fraction=min(
            item["top2_variance_fraction"] for item in geometry
        ),
        mean_latent_norm=float(np.mean([item["mean_norm"] for item in geometry])),
    )


def train_trajectory(
    *,
    dim: int,
    hidden: int,
    base_seed: int,
    initialization_seed: int | None = None,
    data_seed: int | None = None,
    checkpoints: tuple[int, ...] | None = None,
    batch_size: int = 256,
    eval_cases: int = 2048,
    calibration_cases: int = 2048,
    patch_cases: int = 1024,
) -> TrajectoryResult:
    checkpoint_values = tuple(checkpoints or (D1_CHECKPOINTS if dim == 1 else DEFAULT_CHECKPOINTS))
    if not checkpoint_values or tuple(sorted(set(checkpoint_values))) != checkpoint_values:
        raise ValueError("checkpoints must be nonempty, unique, and sorted")
    init_seed = int(initialization_seed or deterministic_subseed(base_seed, "init"))
    stream_seed = int(data_seed or deterministic_subseed(base_seed, "data"))
    torch.manual_seed(init_seed)
    model = NestedWorkspaceModel(dim, hidden)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=1e-5)
    training_generator = torch.Generator().manual_seed(stream_seed)
    calibration = make_batch(
        calibration_cases,
        torch.Generator().manual_seed(deterministic_subseed(base_seed, "calibration")),
    )
    evaluation = make_batch(
        eval_cases,
        torch.Generator().manual_seed(deterministic_subseed(base_seed, "evaluation")),
    )
    source = make_batch(
        patch_cases,
        torch.Generator().manual_seed(deterministic_subseed(base_seed, "patch-source")),
    )
    target = make_batch(
        patch_cases,
        torch.Generator().manual_seed(deterministic_subseed(base_seed, "patch-target")),
    )
    checkpoint_set = set(checkpoint_values)
    rows: list[CheckpointResult] = []
    last_loss = float("nan")
    start = time.perf_counter()
    model.train()
    for step in range(1, checkpoint_values[-1] + 1):
        batch = make_batch(batch_size, training_generator)
        output = model(batch["leaf_phase"])
        loss = cosine_loss(output["action_phase"], batch["action_phase"])
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
        last_loss = float(loss.item())
        if step in checkpoint_set:
            rows.append(
                evaluate_checkpoint(
                    model,
                    step=step,
                    train_loss=last_loss,
                    calibration=calibration,
                    evaluation=evaluation,
                    source=source,
                    target=target,
                )
            )
            model.train()
    elapsed = time.perf_counter() - start
    onset = onset_statistics(rows)
    return TrajectoryResult(
        schema="rrct.v055.workspace_emergence_trajectory.v1",
        bottleneck_dim=dim,
        hidden_width=hidden,
        base_seed=base_seed,
        initialization_seed=init_seed,
        data_seed=stream_seed,
        parameter_count=model.parameter_count(),
        max_steps=checkpoint_values[-1],
        batch_size=batch_size,
        train_seconds=elapsed,
        first_hit_step=onset["first_hit_step"],
        stable_onset_step=onset["stable_onset_step"],
        first_sustained_three_step=onset["first_sustained_three_step"],
        relapse_count_after_first_hit=int(onset["relapse_count_after_first_hit"] or 0),
        final_emergence=rows[-1].emergence,
        uses_intermediate_workspace_labels_for_training=False,
        valence_model_present=False,
        self_preservation_reward=0.0,
        checkpoints=tuple(rows),
    )


def write_result(result: TrajectoryResult, output: pathlib.Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(result), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dim", type=int, required=True)
    parser.add_argument("--hidden", type=int, required=True)
    parser.add_argument("--base-seed", type=int, required=True)
    parser.add_argument("--init-seed", type=int)
    parser.add_argument("--data-seed", type=int)
    parser.add_argument("--max-steps", type=int)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    checkpoints = D1_CHECKPOINTS if args.dim == 1 else DEFAULT_CHECKPOINTS
    if args.max_steps is not None:
        checkpoints = tuple(step for step in checkpoints if step <= args.max_steps)
        if not checkpoints or checkpoints[-1] != args.max_steps:
            checkpoints = tuple(sorted(set(checkpoints + (args.max_steps,))))
    result = train_trajectory(
        dim=args.dim,
        hidden=args.hidden,
        base_seed=args.base_seed,
        initialization_seed=args.init_seed,
        data_seed=args.data_seed,
        checkpoints=checkpoints,
    )
    write_result(result, args.output)
    print(json.dumps({
        "output": str(args.output),
        "dim": args.dim,
        "hidden": args.hidden,
        "base_seed": args.base_seed,
        "stable_onset_step": result.stable_onset_step,
        "first_hit_step": result.first_hit_step,
        "final_emergence": result.final_emergence,
        "train_seconds": result.train_seconds,
    }, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
