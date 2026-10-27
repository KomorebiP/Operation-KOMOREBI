from __future__ import annotations

from typing import Any

import numpy as np

from rrct_lab.dependencies import available
from rrct_lab.exceptions import DependencyError
from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.orchestration import RunContext
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import entropy, seed_everything
from rrct_lab.version import __version__


def run(config: dict[str, Any], context: RunContext | None = None) -> ExperimentResult:
    if not available("torch"):
        raise DependencyError("fuzzy_coalitions requires PyTorch")
    import torch
    from torch import nn
    import torch.nn.functional as F

    seed = int(cfg(config, "run.seed", 580001))
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))
    device_name = str(cfg(config, "runtime.device", "auto"))
    if device_name == "auto":
        device_name = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_name)
    workspace_active = enabled(config, "workspace", "workspace_cut")
    fuzzy_enabled = enabled(config, "fuzzy_packets")
    dynamic_formation = enabled(config, "dynamic_formation")
    cost_regularized = enabled(config, "cost_regularization")
    patching = enabled(config, "causal_patching")
    agents = int(cfg(config, "experiment.agent_count", 4))
    packets = int(cfg(config, "workspace.packet_count", 4))
    shared_packets = min(packets - 1, int(cfg(config, "workspace.shared_packet_count", 3)))
    steps = int(cfg(config, "training.steps", 1000)) if bool(cfg(config, "training.enabled", False)) else 0
    batch_size = int(cfg(config, "training.batch_size", 256))
    hidden = int(cfg(config, "training.hidden_width", 32))
    temperature = float(cfg(config, "workspace.temperature", 1.0))
    idempotence_weight = float(cfg(config, "workspace.idempotence_penalty", 0.0))
    entropy_weight = float(cfg(config, "workspace.entropy_penalty", 0.0))
    holdout = int(cfg(config, "experiment.holdout_episodes", 1024))

    # Fixed packet templates create crisp, overlapping, and diffuse task families.
    crisp_templates = []
    for offset in range(3):
        membership = np.zeros((agents, packets), dtype=np.float32)
        membership[:, 0] = 0.05
        for agent in range(agents):
            packet = 1 + ((agent + offset) % max(1, shared_packets))
            membership[agent, packet] = 0.95
        membership /= membership.sum(axis=1, keepdims=True)
        crisp_templates.append(membership)

    def sample(count: int, torch_generator: torch.Generator) -> dict[str, torch.Tensor]:
        family = torch.randint(0, 3, (count,), generator=torch_generator, device=device)
        left = torch.randint(0, len(crisp_templates), (count,), generator=torch_generator, device=device)
        right = torch.randint(0, len(crisp_templates), (count,), generator=torch_generator, device=device)
        alpha = torch.rand(count, generator=torch_generator, device=device)
        templates = torch.tensor(np.stack(crisp_templates), device=device)
        u_left = templates[left]
        u_right = templates[right]
        crisp = u_left
        overlap = 0.5 * u_left + 0.5 * u_right
        diffuse = alpha[:, None, None] * u_left + (1.0 - alpha[:, None, None]) * u_right
        target_u = torch.where(
            (family == 0)[:, None, None],
            crisp,
            torch.where((family == 1)[:, None, None], overlap, diffuse),
        )
        target_u = target_u / target_u.sum(dim=-1, keepdim=True)
        cue = target_u.flatten(1)
        cue = cue + float(cfg(config, "experiment.noise_std", 0.05)) * torch.randn(
            cue.shape, generator=torch_generator, device=device
        )
        x = torch.randn(count, agents, generator=torch_generator, device=device)
        gains = torch.linspace(0.6, 1.2, shared_packets, device=device)
        shared = target_u[:, :, 1 : 1 + shared_packets]
        c = torch.zeros(count, agents, agents, device=device)
        for packet in range(shared_packets):
            vector = shared[:, :, packet]
            c += gains[packet] * vector[:, :, None] * vector[:, None, :]
        diagonal = torch.arange(agents, device=device)
        c[:, diagonal, diagonal] = 0.0
        y = torch.tanh(x + 0.55 * torch.einsum("bij,bj->bi", c, x))
        return {"cue": cue, "x": x, "y": y, "u": target_u, "family": family}

    class MembershipModel(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.static_logits = nn.Parameter(torch.zeros(agents, packets))
            self.net = nn.Sequential(
                nn.Linear(agents * packets, hidden),
                nn.Tanh(),
                nn.Linear(hidden, agents * packets),
            )

        def memberships(self, cue: torch.Tensor) -> torch.Tensor:
            if dynamic_formation:
                logits = self.net(cue).reshape(-1, agents, packets)
            else:
                logits = self.static_logits.unsqueeze(0).expand(len(cue), -1, -1)
            if bool(cfg(config, "interventions.random_membership", False)):
                logits = torch.randn_like(logits)
            u = torch.softmax(logits / max(temperature, 1e-5), dim=-1)
            if (not fuzzy_enabled) or bool(cfg(config, "interventions.hardening", False)) or bool(cfg(config, "features.hard_packets", False)):
                hard = F.one_hot(u.argmax(dim=-1), packets).float()
                u = hard + (u - u.detach())
            if not workspace_active:
                u = torch.zeros_like(u)
                u[:, :, 0] = 1.0
            return u

        def forward(self, cue: torch.Tensor, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
            u = self.memberships(cue)
            shared = u[:, :, 1 : 1 + shared_packets]
            gains = torch.linspace(0.6, 1.2, shared_packets, device=cue.device)
            c = torch.zeros(len(cue), agents, agents, device=cue.device)
            for packet in range(shared_packets):
                vector = shared[:, :, packet]
                c += gains[packet] * vector[:, :, None] * vector[:, None, :]
            diagonal = torch.arange(agents, device=cue.device)
            c[:, diagonal, diagonal] = 0.0
            y = torch.tanh(x + 0.55 * torch.einsum("bij,bj->bi", c, x))
            return y, u

    model = MembershipModel().to(device)
    generator = torch.Generator(device=device).manual_seed(seed ^ 0xF02257)
    if steps > 0:
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=float(cfg(config, "training.learning_rate", 0.003)),
            weight_decay=float(cfg(config, "training.weight_decay", 1e-5)),
        )
        model.train()
        for _ in range(steps):
            batch = sample(batch_size, generator)
            predicted, memberships = model(batch["cue"], batch["x"])
            base_loss = F.mse_loss(predicted, batch["y"])
            idem = torch.mean(torch.sum(torch.square(memberships * memberships - memberships), dim=(-1, -2)))
            ent = torch.mean(-torch.sum(memberships * torch.log(torch.clamp(memberships, min=1e-8)), dim=-1))
            formation = torch.mean(memberships[:, :, 1:])
            formation_weight = float(cfg(config, "workspace.formation_cost", 0.12)) if cost_regularized else 0.0
            loss = base_loss + idempotence_weight * idem + entropy_weight * ent + 0.001 * formation_weight * formation
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
    model.eval()

    eval_generator = torch.Generator(device=device).manual_seed(seed ^ 0xA11CE57)
    with torch.no_grad():
        batch = sample(holdout, eval_generator)
        predicted, memberships = model(batch["cue"], batch["x"])
        base_mse = float(F.mse_loss(predicted, batch["y"]).item())
        hard = F.one_hot(memberships.argmax(dim=-1), packets).float()
        original_flag = bool(cfg(config, "interventions.hardening", False))
        shared = hard[:, :, 1 : 1 + shared_packets]
        gains = torch.linspace(0.6, 1.2, shared_packets, device=device)
        c = torch.zeros(holdout, agents, agents, device=device)
        for packet in range(shared_packets):
            vector = shared[:, :, packet]
            c += gains[packet] * vector[:, :, None] * vector[:, None, :]
        diagonal = torch.arange(agents, device=device)
        c[:, diagonal, diagonal] = 0.0
        hard_y = torch.tanh(batch["x"] + 0.55 * torch.einsum("bij,bj->bi", c, batch["x"]))
        hard_mse = float(F.mse_loss(hard_y, batch["y"]).item())
        membership_np = memberships.cpu().numpy()
        family_np = batch["family"].cpu().numpy()
        entropies = entropy(membership_np, axis=-1).mean(axis=1)
        idem_values = np.sqrt(np.sum(np.square(membership_np * membership_np - membership_np), axis=(1, 2)))

        strengths: list[float] = []
        effects: list[float] = []
        sample_count = min(256, holdout)
        for episode in range(sample_count):
            for agent in range(agents):
                for packet in range(1, 1 + shared_packets):
                    u = memberships[episode : episode + 1].clone()
                    strength = float(u[0, agent, packet].item())
                    removed = u[0, agent, packet].item()
                    u[0, agent, packet] = 0.0
                    u[0, agent, 0] += removed
                    shared_one = u[:, :, 1 : 1 + shared_packets]
                    c_one = torch.zeros(1, agents, agents, device=device)
                    for packet_index in range(shared_packets):
                        vector = shared_one[:, :, packet_index]
                        c_one += gains[packet_index] * vector[:, :, None] * vector[:, None, :]
                    c_one[:, diagonal, diagonal] = 0.0
                    altered = torch.tanh(batch["x"][episode : episode + 1] + 0.55 * torch.einsum("bij,bj->bi", c_one, batch["x"][episode : episode + 1]))
                    effect = float(F.mse_loss(altered, predicted[episode : episode + 1]).item())
                    strengths.append(strength)
                    effects.append(effect)
        correlation = float(np.corrcoef(strengths, effects)[0, 1]) if patching and np.std(strengths) > 1e-12 and np.std(effects) > 1e-12 else 0.0

    artifacts: list[str] = []
    if bool(cfg(config, "run.save_models", False)) and context is not None:
        model_path = context.run_dir / "model.pt"
        torch.save(
            {
                "version": __version__,
                "family": "fuzzy_coalitions",
                "seed": seed,
                "state_dict": model.state_dict(),
                "agents": agents,
                "packets": packets,
                "shared_packets": shared_packets,
            "dynamic_formation": dynamic_formation,
            "fuzzy_packets": fuzzy_enabled,
            "cost_regularization": cost_regularized,
            },
            model_path,
        )
        artifacts.append(str(model_path.relative_to(context.run_dir)))

    crisp_mask = family_np == 0
    fuzzy_mask = family_np != 0
    metrics = {
        "task_mse": base_mse,
        "task_accuracy": float(np.mean(np.mean(np.square(predicted.cpu().numpy() - batch["y"].cpu().numpy()), axis=1) < 0.01)),
        "fuzzy_task_accuracy": float(np.exp(-10.0 * base_mse)),
        "hardened_mse": hard_mse,
        "hardening_error_ratio": hard_mse / max(base_mse, 1e-12),
        "membership_entropy": float(np.mean(entropies)),
        "crisp_membership_entropy": float(np.mean(entropies[crisp_mask])) if np.any(crisp_mask) else 0.0,
        "fuzzy_membership_entropy": float(np.mean(entropies[fuzzy_mask])) if np.any(fuzzy_mask) else 0.0,
        "idempotence_defect": float(np.mean(idem_values)),
        "crisp_idempotence_defect": float(np.mean(idem_values[crisp_mask])) if np.any(crisp_mask) else 0.0,
        "fuzzy_idempotence_defect": float(np.mean(idem_values[fuzzy_mask])) if np.any(fuzzy_mask) else 0.0,
        "causal_membership_calibration": correlation,
        "partition_unity_error": float(np.max(np.abs(membership_np.sum(axis=-1) - 1.0))),
        "parameter_count": int(sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)),
    }
    warnings = [] if steps > 0 else ["Training was disabled; this is an untrained fuzzy-membership smoke run."]
    return ExperimentResult(
        family="fuzzy_coalitions",
        status="completed",
        metrics=metrics,
        warnings=warnings,
        artifacts=artifacts,
        metadata={
            "device": str(device),
            "training_steps": steps,
            "agents": agents,
            "packets": packets,
            "shared_packets": shared_packets,
            "dynamic_formation": dynamic_formation,
            "fuzzy_packets": fuzzy_enabled,
            "cost_regularization": cost_regularized,
        },
    )
