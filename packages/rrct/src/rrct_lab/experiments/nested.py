from __future__ import annotations

import math
from typing import Any

import numpy as np

from rrct_lab.dependencies import available
from rrct_lab.exceptions import DependencyError
from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.orchestration import RunContext
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import seed_everything
from rrct_lab.version import __version__


TAU = 2.0 * math.pi


def run(config: dict[str, Any], context: RunContext | None = None) -> ExperimentResult:
    if not available("torch"):
        raise DependencyError("nested_workspace requires PyTorch")
    import torch
    from torch import nn
    import torch.nn.functional as F

    seed = int(cfg(config, "run.seed", 580001))
    seed_everything(seed, bool(cfg(config, "run.deterministic", True)))
    threads = int(cfg(config, "runtime.threads", 0))
    if threads > 0:
        torch.set_num_threads(threads)
    device_name = str(cfg(config, "runtime.device", "auto"))
    if device_name == "auto":
        device_name = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_name)
    hierarchy_depth = int(cfg(config, "workspace.hierarchy_depth", 2))
    if hierarchy_depth != 2:
        raise ValueError("nested_workspace currently implements exactly workspace.hierarchy_depth=2")
    workspace_active = enabled(config, "workspace", "workspace_cut")
    hierarchical = enabled(config, "hierarchical_workspace")
    top_down = enabled(config, "top_down_broadcast", "top_down_cut")
    planner = enabled(config, "planner_binding", "planner_binding_cut")
    emergence_training = enabled(config, "emergence_training")
    patching = enabled(config, "causal_patching")
    local_dim = int(cfg(config, "workspace.local_dimension", 2))
    global_dim = int(cfg(config, "workspace.global_dimension", 2))
    hidden = int(cfg(config, "training.hidden_width", 32))
    steps = int(cfg(config, "training.steps", 1000)) if bool(cfg(config, "training.enabled", False)) and emergence_training else 0
    batch_size = int(cfg(config, "training.batch_size", 256))
    learning_rate = float(cfg(config, "training.learning_rate", 0.003))
    holdout = int(cfg(config, "experiment.holdout_episodes", 1024))
    calibration = int(cfg(config, "experiment.calibration_episodes", 1024))

    def phase(values: torch.Tensor) -> torch.Tensor:
        return torch.stack((torch.cos(TAU * values), torch.sin(TAU * values)), dim=-1)

    def make_batch(count: int, generator: torch.Generator) -> dict[str, torch.Tensor]:
        u = torch.rand(count, generator=generator, device=device)
        v = torch.rand(count, generator=generator, device=device)
        ra = torch.rand(count, generator=generator, device=device)
        rb = torch.rand(count, generator=generator, device=device)
        values = torch.stack((ra, torch.remainder(u - ra, 1.0), rb, torch.remainder(v - rb, 1.0)), dim=1)
        y = torch.remainder(u + v, 1.0)
        actions = torch.remainder(values + y[:, None], 1.0)
        return {
            "leaf": phase(values),
            "actions": phase(actions),
            "u": phase(u),
            "v": phase(v),
            "y": phase(y),
            "values": values,
            "u_raw": u,
            "v_raw": v,
            "y_raw": y,
        }

    class Block(nn.Module):
        def __init__(self, da: int, db: int, output: int) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(da + db + da * db, hidden),
                nn.Tanh(),
                nn.Linear(hidden, output),
                nn.Tanh(),
            )

        def forward(self, a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
            tensor = (a.unsqueeze(-1) * b.unsqueeze(-2)).flatten(1)
            return self.net(torch.cat((a, b, tensor), dim=1))

    class Model(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.local_a = Block(2, 2, local_dim)
            self.local_b = Block(2, 2, local_dim)
            self.global_workspace = Block(local_dim, local_dim, global_dim)
            self.action_heads = nn.ModuleList(Block(2, global_dim, 2) for _ in range(4))

        def forward(
            self,
            leaf: torch.Tensor,
            *,
            leaf_cut: int | None = None,
            local_a_override: torch.Tensor | None = None,
            local_b_override: torch.Tensor | None = None,
            global_override: torch.Tensor | None = None,
            topdown_cut: bool = False,
        ) -> dict[str, torch.Tensor]:
            local_leaf = leaf.clone()
            if leaf_cut is not None:
                local_leaf[:, leaf_cut] = 0.0
            za = self.local_a(local_leaf[:, 0], local_leaf[:, 1]) if local_a_override is None else local_a_override
            zb = self.local_b(local_leaf[:, 2], local_leaf[:, 3]) if local_b_override is None else local_b_override
            zg = self.global_workspace(za, zb) if global_override is None else global_override
            if not workspace_active or not hierarchical:
                za = torch.zeros_like(za)
                zb = torch.zeros_like(zb)
                zg = torch.zeros_like(zg)
            active = torch.zeros_like(zg) if topdown_cut or not top_down or not planner else zg
            actions = torch.stack(
                [F.normalize(self.action_heads[index](leaf[:, index], active), dim=-1) for index in range(4)],
                dim=1,
            )
            return {"actions": actions, "local_a": za, "local_b": zb, "global": zg}

    model = Model().to(device)
    generator = torch.Generator(device=device).manual_seed(seed ^ 0x580053)
    if steps > 0:
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=float(cfg(config, "training.weight_decay", 1e-5)),
        )
        model.train()
        for _ in range(steps):
            batch = make_batch(batch_size, generator)
            output = model(batch["leaf"])
            loss = (1.0 - (output["actions"] * batch["actions"]).sum(dim=-1)).mean()
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            clip = float(cfg(config, "training.gradient_clip", 1.0))
            if clip > 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
            optimizer.step()
    model.eval()

    eval_generator = torch.Generator(device=device).manual_seed(seed ^ 0xA11CE)
    calibration_generator = torch.Generator(device=device).manual_seed(seed ^ 0xCA11B)
    patch_generator = torch.Generator(device=device).manual_seed(seed ^ 0xFA7C4)
    with torch.no_grad():
        cal = make_batch(calibration, calibration_generator)
        test = make_batch(holdout, eval_generator)
        source = make_batch(min(holdout, 1024), patch_generator)
        target = make_batch(min(holdout, 1024), patch_generator)
        cal_out = model(cal["leaf"])
        out = model(test["leaf"])

        def strict(pred: torch.Tensor, truth: torch.Tensor) -> float:
            threshold = float(cfg(config, "evaluation.strict_cosine_threshold", 0.99))
            return float((((pred * truth).sum(dim=-1)) >= threshold).float().mean().item())

        intact = strict(out["actions"], test["actions"])
        cuts = []
        for index in range(4):
            cuts.append(strict(model(test["leaf"], leaf_cut=index)["actions"], test["actions"]))
        global_cut = strict(
            model(test["leaf"], global_override=torch.zeros_like(out["global"]))["actions"],
            test["actions"],
        )
        topdown_cut = strict(model(test["leaf"], topdown_cut=True)["actions"], test["actions"])

        def probe(cal_z: torch.Tensor, cal_t: torch.Tensor, eval_z: torch.Tensor, eval_t: torch.Tensor) -> float:
            ca = torch.cat((cal_z, torch.ones(len(cal_z), 1, device=device)), dim=1)
            ea = torch.cat((eval_z, torch.ones(len(eval_z), 1, device=device)), dim=1)
            weights = torch.linalg.lstsq(ca, cal_t).solution
            pred = F.normalize(ea @ weights, dim=-1)
            return strict(pred, eval_t)

        probe_a = probe(cal_out["local_a"], cal["u"], out["local_a"], test["u"])
        probe_b = probe(cal_out["local_b"], cal["v"], out["local_b"], test["v"])
        probe_g = probe(cal_out["global"], cal["y"], out["global"], test["y"])
        source_out = model(source["leaf"])
        target_out = model(target["leaf"])
        patched = model(
            source["leaf"],
            local_a_override=target_out["local_a"],
            local_b_override=source_out["local_b"],
        )
        expected_y = torch.remainder(target["u_raw"] + source["v_raw"], 1.0)
        expected_actions = phase(torch.remainder(source["values"] + expected_y[:, None], 1.0))
        patch_accuracy = strict(patched["actions"], expected_actions) if patching else 0.0

    artifacts: list[str] = []
    if bool(cfg(config, "run.save_models", False)) and context is not None:
        model_path = context.run_dir / "model.pt"
        torch.save(
            {
                "version": __version__,
                "family": "nested_workspace",
                "seed": seed,
                "state_dict": model.state_dict(),
                "local_dimension": local_dim,
                "global_dimension": global_dim,
                "hidden_width": hidden,
            "hierarchy_depth": hierarchy_depth,
            "workspace_active": workspace_active and hierarchical,
            },
            model_path,
        )
        artifacts.append(str(model_path.relative_to(context.run_dir)))

    metrics = {
        "task_accuracy": intact,
        "workspace_decodability": float(np.mean([probe_a, probe_b, probe_g])),
        "local_a_probe_accuracy": probe_a,
        "local_b_probe_accuracy": probe_b,
        "global_probe_accuracy": probe_g,
        "causal_patch_effect": patch_accuracy,
        "leaf_cut_accuracy": float(np.mean(cuts)),
        "global_cut_accuracy": global_cut,
        "top_down_cut_accuracy": topdown_cut,
        "ablation_drop": intact - global_cut,
        "planner_binding_rate": 1.0 - topdown_cut,
        "parameter_count": int(sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)),
        "emergence_rate": 1.0 if intact >= 0.98 and probe_g >= 0.95 and patch_accuracy >= 0.95 and global_cut <= 0.15 else 0.0,
    }
    return ExperimentResult(
        family="nested_workspace",
        status="completed",
        metrics=metrics,
        artifacts=artifacts,
        metadata={
            "device": str(device),
            "training_steps": steps,
            "local_dimension": local_dim,
            "global_dimension": global_dim,
            "hidden_width": hidden,
            "hierarchy_depth": hierarchy_depth,
            "workspace_active": workspace_active and hierarchical,
        },
        warnings=[] if steps > 0 else ["Training was disabled; metrics describe an untrained architecture smoke run."],
    )
