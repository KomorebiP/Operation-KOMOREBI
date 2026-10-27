from __future__ import annotations

import argparse
import json
import math
import pathlib
import time
from dataclasses import asdict, dataclass

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

TAU = 2.0 * math.pi
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
    values = torch.stack((ra, torch.remainder(u-ra, 1.0), rb, torch.remainder(v-rb, 1.0)), 1)
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
        self.global_workspace = TensorProductBlock(bottleneck_dim, bottleneck_dim, bottleneck_dim, hidden)
        self.action_heads = nn.ModuleList(
            TensorProductBlock(2, bottleneck_dim, 2, hidden) for _ in range(4)
        )

    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def forward(
        self,
        leaf_phase: torch.Tensor,
        *,
        local_a_override: torch.Tensor | None = None,
        local_b_override: torch.Tensor | None = None,
        global_override: torch.Tensor | None = None,
        topdown_cut: bool = False,
    ) -> dict[str, torch.Tensor]:
        za = self.local_a(leaf_phase[:, 0], leaf_phase[:, 1]) if local_a_override is None else local_a_override
        zb = self.local_b(leaf_phase[:, 2], leaf_phase[:, 3]) if local_b_override is None else local_b_override
        zg = self.global_workspace(za, zb) if global_override is None else global_override
        action_global = torch.zeros_like(zg) if topdown_cut else zg
        actions = torch.stack(
            [
                F.normalize(self.action_heads[i](leaf_phase[:, i], action_global), dim=-1)
                for i in range(4)
            ],
            dim=1,
        )
        return {"action_phase": actions, "local_a": za, "local_b": zb, "global": zg}


def cosine_loss(prediction: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return (1.0 - (prediction * target).sum(-1)).mean()


def strict_accuracy(prediction: torch.Tensor, target: torch.Tensor, threshold: float = 0.99) -> float:
    return float(((prediction * target).sum(-1) >= threshold).float().mean().item())


def linear_probe(
    calibration_z: torch.Tensor,
    calibration_target: torch.Tensor,
    evaluation_z: torch.Tensor,
    evaluation_target: torch.Tensor,
) -> float:
    calibration_aug = torch.cat((calibration_z, torch.ones((len(calibration_z), 1))), dim=1)
    evaluation_aug = torch.cat((evaluation_z, torch.ones((len(evaluation_z), 1))), dim=1)
    gram = calibration_aug.T @ calibration_aug
    ridge = 1e-5 * torch.eye(gram.shape[0])
    weights = torch.linalg.solve(gram + ridge, calibration_aug.T @ calibration_target)
    prediction = F.normalize(evaluation_aug @ weights, dim=-1)
    return strict_accuracy(prediction, evaluation_target)


@dataclass(frozen=True)
class TrialResult:
    bottleneck_dim: int
    hidden_width: int
    steps: int
    seed: int
    parameter_count: int
    parameter_updates: int
    sample_parameter_product: int
    train_seconds: float
    action_accuracy: float
    probe_accuracy: float
    patch_accuracy: float
    cut_accuracy: float
    emergence: bool


def train_and_evaluate(
    *,
    dim: int,
    hidden: int,
    steps: int,
    seed: int,
    batch_size: int = 256,
    eval_cases: int = 1024,
    calibration_cases: int = 1024,
    patch_cases: int = 512,
) -> TrialResult:
    torch.manual_seed(seed)
    generator = torch.Generator().manual_seed(seed ^ 0x5400A11)
    model = NestedWorkspaceModel(dim, hidden)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003, weight_decay=1e-5)
    start = time.perf_counter()
    model.train()
    for _ in range(steps):
        batch = make_batch(batch_size, generator)
        output = model(batch["leaf_phase"])
        loss = cosine_loss(output["action_phase"], batch["action_phase"])
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    train_seconds = time.perf_counter() - start
    model.eval()

    calibration = make_batch(calibration_cases, torch.Generator().manual_seed(seed ^ 0xCA11B))
    evaluation = make_batch(eval_cases, torch.Generator().manual_seed(seed ^ 0xA11CE))
    source = make_batch(patch_cases, torch.Generator().manual_seed(seed ^ 0xFA7C4))
    target = make_batch(patch_cases, torch.Generator().manual_seed(seed ^ 0xBEE55))
    with torch.no_grad():
        cal_out = model(calibration["leaf_phase"])
        eval_out = model(evaluation["leaf_phase"])
        source_out = model(source["leaf_phase"])
        target_out = model(target["leaf_phase"])
        cut_out = model(evaluation["leaf_phase"], global_override=torch.zeros_like(eval_out["global"]))
        patch_a = model(
            source["leaf_phase"],
            local_a_override=target_out["local_a"],
            local_b_override=source_out["local_b"],
        )
        expected_y_a = torch.remainder(target["u"] + source["v"], 1.0)
        expected_action_a = phase(torch.remainder(source["values"] + expected_y_a[:, None], 1.0))
        patch_b = model(
            source["leaf_phase"],
            local_a_override=source_out["local_a"],
            local_b_override=target_out["local_b"],
        )
        expected_y_b = torch.remainder(source["u"] + target["v"], 1.0)
        expected_action_b = phase(torch.remainder(source["values"] + expected_y_b[:, None], 1.0))
        patch_g = model(source["leaf_phase"], global_override=target_out["global"])
        expected_action_g = phase(torch.remainder(source["values"] + target["y"][:, None], 1.0))

    action_accuracy = strict_accuracy(eval_out["action_phase"], evaluation["action_phase"])
    probe_accuracy = min(
        linear_probe(cal_out["local_a"], calibration["u_phase"], eval_out["local_a"], evaluation["u_phase"]),
        linear_probe(cal_out["local_b"], calibration["v_phase"], eval_out["local_b"], evaluation["v_phase"]),
        linear_probe(cal_out["global"], calibration["y_phase"], eval_out["global"], evaluation["y_phase"]),
    )
    patch_accuracy = min(
        strict_accuracy(patch_a["action_phase"], expected_action_a),
        strict_accuracy(patch_b["action_phase"], expected_action_b),
        strict_accuracy(patch_g["action_phase"], expected_action_g),
    )
    cut_accuracy = strict_accuracy(cut_out["action_phase"], evaluation["action_phase"])
    emergence = bool(
        action_accuracy >= 0.98
        and probe_accuracy >= 0.95
        and patch_accuracy >= 0.95
        and cut_accuracy <= 0.15
    )
    params = model.parameter_count()
    return TrialResult(
        bottleneck_dim=dim,
        hidden_width=hidden,
        steps=steps,
        seed=seed,
        parameter_count=params,
        parameter_updates=params * steps,
        sample_parameter_product=params * steps * batch_size,
        train_seconds=train_seconds,
        action_accuracy=action_accuracy,
        probe_accuracy=probe_accuracy,
        patch_accuracy=patch_accuracy,
        cut_accuracy=cut_accuracy,
        emergence=emergence,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dim", type=int, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    parser.add_argument("--hidden", type=int, default=None)
    args = parser.parse_args()
    widths = [args.hidden] if args.hidden is not None else [8, 16, 32, 64]
    steps_grid = [25, 50, 100, 200, 400, 800, 1400]
    seeds = [54011, 54029, 54047]
    results: list[dict[str, object]] = []
    for hidden in widths:
        for steps in steps_grid:
            for seed in seeds:
                result = train_and_evaluate(dim=args.dim, hidden=hidden, steps=steps, seed=seed)
                results.append(asdict(result))
                print(json.dumps(asdict(result), sort_keys=True), flush=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
