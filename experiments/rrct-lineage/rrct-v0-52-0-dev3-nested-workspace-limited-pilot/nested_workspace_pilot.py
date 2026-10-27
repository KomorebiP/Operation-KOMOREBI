"""RRCT v0.52 dev3: limited two-level nested-workspace pilot.

Four leaf agents form two local learned bottlenecks.  Those bottlenecks act as
agents for one smaller global bottleneck.  The global state is written back to
both local coalitions before the leaves act.  The finite task has exact synergy
at both levels.

This is a controlled functional architecture test.  It is not a brain model or
consciousness test.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random
from typing import Any, Literal, Mapping, Sequence

import numpy as np
import torch
from torch import nn
import torch.nn.functional as F

VERSION = "0.52.0.dev3"
Mode = Literal[
    "intact", "leaf_a1_cut", "leaf_a2_cut", "leaf_b1_cut", "leaf_b2_cut",
    "local_a_cut", "local_b_cut", "global_cut", "topdown_cut",
]


@dataclass(frozen=True)
class Config:
    leaf_dim: int = 8
    local_dim: int = 5
    global_dim: int = 4
    hidden_dim: int = 64
    local_max_steps: int = 800
    local_min_steps: int = 100
    global_max_steps: int = 500
    global_min_steps: int = 50
    topdown_max_steps: int = 700
    topdown_min_steps: int = 50
    private_max_steps: int = 250
    private_min_steps: int = 25
    flat_max_steps: int = 500
    flat_min_steps: int = 50
    learning_rate: float = 5e-3
    weight_decay: float = 1e-5
    gradient_clip: float = 1.0
    threads: int = 2

    def __post_init__(self) -> None:
        if self.local_dim >= 2 * self.leaf_dim:
            raise ValueError("local workspace must compress two leaf codes")
        if self.global_dim >= 2 * self.local_dim:
            raise ValueError("global workspace must compress two local states")


def set_determinism(seed: int, threads: int = 2) -> None:
    random.seed(int(seed))
    np.random.seed(int(seed))
    torch.manual_seed(int(seed))
    torch.set_num_threads(int(threads))
    torch.use_deterministic_algorithms(True)


def canonical(value: Any) -> bytes:
    def norm(x: Any) -> Any:
        if hasattr(x, "item"):
            return x.item()
        if hasattr(x, "__dataclass_fields__"):
            return norm(asdict(x))
        if isinstance(x, Mapping):
            return {str(k): norm(v) for k, v in x.items()}
        if isinstance(x, (tuple, list)):
            return [norm(v) for v in x]
        return x
    return json.dumps(norm(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def state_dict_sha256(model: nn.Module) -> str:
    h = hashlib.sha256()
    for key, value in sorted(model.state_dict().items()):
        h.update(key.encode())
        tensor = value.detach().cpu().contiguous()
        h.update(str(tensor.dtype).encode())
        h.update(np.asarray(tensor.shape, dtype=np.int64).tobytes())
        h.update(tensor.numpy().tobytes())
    return h.hexdigest()


def codebook(seed: int, dim: int) -> torch.Tensor:
    generator = torch.Generator().manual_seed(int(seed))
    return F.normalize(torch.randn(4, dim, generator=generator), dim=1)


class LocalWorkspace(nn.Module):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(2 * config.leaf_dim, config.hidden_dim), nn.ReLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim), nn.ReLU(),
            nn.Linear(config.hidden_dim, config.local_dim), nn.Tanh(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(config.local_dim, config.hidden_dim), nn.ReLU(),
            nn.Linear(config.hidden_dim, 4),
        )

    def forward(self, first: torch.Tensor, second: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        state = self.encoder(torch.cat([first, second], dim=1))
        return state, self.decoder(state)


class GlobalWorkspace(nn.Module):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(2 * config.local_dim, config.hidden_dim), nn.ReLU(),
            nn.Linear(config.hidden_dim, config.hidden_dim), nn.ReLU(),
            nn.Linear(config.hidden_dim, config.global_dim), nn.Tanh(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(config.global_dim, config.hidden_dim), nn.ReLU(),
            nn.Linear(config.hidden_dim, 4),
        )

    def forward(self, first: torch.Tensor, second: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        state = self.encoder(torch.cat([first, second], dim=1))
        return state, self.decoder(state)


class NestedModel(nn.Module):
    def __init__(self, seed: int, config: Config | None = None) -> None:
        super().__init__()
        self.seed = int(seed)
        self.config = config or Config()
        for index in range(4):
            self.register_buffer(f"task_code_{index}", codebook(seed * 17 + index, self.config.leaf_dim))
            self.register_buffer(f"private_code_{index}", codebook(seed * 31 + index, self.config.leaf_dim))
        self.local_a = LocalWorkspace(self.config)
        self.local_b = LocalWorkspace(self.config)
        self.global_workspace = GlobalWorkspace(self.config)
        self.revise_a = nn.Sequential(
            nn.Linear(self.config.local_dim + self.config.global_dim, self.config.hidden_dim), nn.ReLU(),
            nn.Linear(self.config.hidden_dim, self.config.local_dim), nn.Tanh(),
        )
        self.revise_b = nn.Sequential(
            nn.Linear(self.config.local_dim + self.config.global_dim, self.config.hidden_dim), nn.ReLU(),
            nn.Linear(self.config.hidden_dim, self.config.local_dim), nn.Tanh(),
        )
        self.action_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(self.config.leaf_dim + self.config.local_dim, self.config.hidden_dim), nn.ReLU(),
                nn.Linear(self.config.hidden_dim, 4),
            ) for _ in range(4)
        ])
        self.private_heads = nn.ModuleList([nn.Linear(self.config.leaf_dim, 4) for _ in range(4)])

    def task_codes(self, values: torch.Tensor) -> list[torch.Tensor]:
        return [getattr(self, f"task_code_{i}")[values[:, i]] for i in range(4)]

    def private_logits(self, private_roles: torch.Tensor) -> list[torch.Tensor]:
        return [self.private_heads[i](getattr(self, f"private_code_{i}")[private_roles[:, i]]) for i in range(4)]

    def forward(
        self,
        values: torch.Tensor,
        private_roles: torch.Tensor,
        *,
        mode: Mode = "intact",
        patch_global: torch.Tensor | None = None,
        patch_local_a: torch.Tensor | None = None,
        patch_local_b: torch.Tensor | None = None,
    ) -> dict[str, Any]:
        codes = self.task_codes(values)
        private = self.private_logits(private_roles)
        if mode == "leaf_a1_cut": codes[0] = torch.zeros_like(codes[0])
        if mode == "leaf_a2_cut": codes[1] = torch.zeros_like(codes[1])
        if mode == "leaf_b1_cut": codes[2] = torch.zeros_like(codes[2])
        if mode == "leaf_b2_cut": codes[3] = torch.zeros_like(codes[3])

        local_a, logits_a = self.local_a(codes[0], codes[1])
        local_b, logits_b = self.local_b(codes[2], codes[3])
        if mode == "local_a_cut":
            local_a = torch.zeros_like(local_a); logits_a = self.local_a.decoder(local_a)
        if mode == "local_b_cut":
            local_b = torch.zeros_like(local_b); logits_b = self.local_b.decoder(local_b)
        if patch_local_a is not None:
            local_a = patch_local_a; logits_a = self.local_a.decoder(local_a)
        if patch_local_b is not None:
            local_b = patch_local_b; logits_b = self.local_b.decoder(local_b)

        global_state, global_logits = self.global_workspace(local_a, local_b)
        if mode == "global_cut":
            global_state = torch.zeros_like(global_state); global_logits = self.global_workspace.decoder(global_state)
        if patch_global is not None:
            global_state = patch_global; global_logits = self.global_workspace.decoder(global_state)

        if mode == "topdown_cut":
            revised_a, revised_b = local_a, local_b
        else:
            revised_a = self.revise_a(torch.cat([local_a, global_state], dim=1))
            revised_b = self.revise_b(torch.cat([local_b, global_state], dim=1))
        actions = [
            self.action_heads[i](torch.cat([codes[i], revised_a if i < 2 else revised_b], dim=1))
            for i in range(4)
        ]
        return {
            "local_a": local_a, "local_b": local_b,
            "local_a_logits": logits_a, "local_b_logits": logits_b,
            "global_state": global_state, "global_logits": global_logits,
            "actions": actions, "private": private,
        }


class FlatController(nn.Module):
    def __init__(self, codebooks: Sequence[torch.Tensor], config: Config) -> None:
        super().__init__()
        for i, table in enumerate(codebooks):
            self.register_buffer(f"task_code_{i}", table.clone())
        self.trunk = nn.Sequential(
            nn.Linear(4 * config.leaf_dim, 2 * config.hidden_dim), nn.ReLU(),
            nn.Linear(2 * config.hidden_dim, config.hidden_dim), nn.ReLU(),
        )
        self.global_head = nn.Linear(config.hidden_dim, 4)
        self.action_heads = nn.ModuleList([nn.Linear(config.hidden_dim, 4) for _ in range(4)])

    def forward(self, values: torch.Tensor) -> dict[str, Any]:
        x = torch.cat([getattr(self, f"task_code_{i}")[values[:, i]] for i in range(4)], dim=1)
        h = self.trunk(x)
        return {"global_logits": self.global_head(h), "actions": [head(h) for head in self.action_heads]}


def values_grid() -> torch.Tensor:
    return torch.cartesian_prod(*[torch.arange(4) for _ in range(4)])


def private_grid(n: int) -> torch.Tensor:
    base = torch.arange(n)
    return torch.stack([(base + i) % 4 for i in range(4)], dim=1)


def targets(values: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, list[torch.Tensor]]:
    u = (values[:, 0] + values[:, 1]) % 4
    v = (values[:, 2] + values[:, 3]) % 4
    y = (u + v) % 4
    return u, v, y, [(values[:, i] + y) % 4 for i in range(4)]


def entropy(x: np.ndarray) -> float:
    _, counts = np.unique(x, axis=0, return_counts=True)
    p = counts / counts.sum()
    return float(-(p * np.log2(p)).sum())


def mutual_information(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x); y = np.asarray(y)
    if x.ndim == 1: x = x[:, None]
    if y.ndim == 1: y = y[:, None]
    return entropy(x) + entropy(y) - entropy(np.concatenate([x, y], axis=1))


def information_receipt() -> dict[str, float]:
    x = values_grid().numpy()
    u = (x[:, 0] + x[:, 1]) % 4
    v = (x[:, 2] + x[:, 3]) % 4
    y = (u + v) % 4
    return {
        "H_U": entropy(u), "H_V": entropy(v), "H_Y": entropy(y),
        "I_U_A1": mutual_information(u, x[:, 0]), "I_U_A2": mutual_information(u, x[:, 1]),
        "I_U_A1A2": mutual_information(u, x[:, :2]),
        "I_V_B1": mutual_information(v, x[:, 2]), "I_V_B2": mutual_information(v, x[:, 3]),
        "I_V_B1B2": mutual_information(v, x[:, 2:]),
        "I_Y_U": mutual_information(y, u), "I_Y_V": mutual_information(y, v),
        "I_Y_UV": mutual_information(y, np.stack([u, v], axis=1)),
        "I_Y_A_PAIR": mutual_information(y, x[:, :2]),
        "I_Y_B_PAIR": mutual_information(y, x[:, 2:]),
        "I_Y_ALL": mutual_information(y, x),
    }


def accuracy(logits: torch.Tensor, target: torch.Tensor) -> float:
    return float((logits.argmax(1) == target).float().mean())


def set_trainable(module: nn.Module, enabled: bool) -> None:
    for p in module.parameters(): p.requires_grad = enabled


def train_until(optimizer, loss_fn, done_fn, max_steps: int, min_steps: int, modules: Sequence[nn.Module], clip: float) -> int:
    params = [p for m in modules for p in m.parameters() if p.requires_grad]
    for step in range(max_steps):
        loss = loss_fn(); optimizer.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(params, clip); optimizer.step()
        if step + 1 >= min_steps and done_fn(): return step + 1
    return max_steps


def evaluate(model: NestedModel, mode: Mode = "intact") -> dict[str, Any]:
    x = values_grid(); p = private_grid(len(x)); u, v, y, a = targets(x)
    with torch.no_grad(): out = model(x, p, mode=mode)
    act = [accuracy(out["actions"][i], a[i]) for i in range(4)]
    priv = [accuracy(out["private"][i], p[:, i]) for i in range(4)]
    return {
        "local_a": accuracy(out["local_a_logits"], u), "local_b": accuracy(out["local_b_logits"], v),
        "global": accuracy(out["global_logits"], y), "actions": act, "mean_action": float(np.mean(act)),
        "private": priv, "mean_private": float(np.mean(priv)),
    }


def evaluate_flat(model: FlatController) -> dict[str, Any]:
    x = values_grid(); _, _, y, a = targets(x)
    with torch.no_grad(): out = model(x)
    acts = [accuracy(out["actions"][i], a[i]) for i in range(4)]
    return {"global": accuracy(out["global_logits"], y), "actions": acts, "mean_action": float(np.mean(acts))}


def patch_tests(model: NestedModel) -> dict[str, Any]:
    x = values_grid(); p = private_grid(len(x))
    target_a = x.clone(); target_a[:, 0] = (target_a[:, 0] + 1) % 4
    target_b = x.clone(); target_b[:, 2] = (target_b[:, 2] + 1) % 4
    tp = torch.roll(p, 1, 0)
    su, sv, _, _ = targets(x); tu, _, ty, _ = targets(target_a); _, tv, _, _ = targets(target_b)
    mixed_a = (tu + sv) % 4; mixed_b = (su + tv) % 4
    with torch.no_grad():
        ta = model(target_a, tp); tb = model(target_b, tp)
        pg = model(x, p, patch_global=ta["global_state"])
        pa = model(x, p, patch_local_a=ta["local_a"])
        pb = model(x, p, patch_local_b=tb["local_b"])
    def actions(out, y): return [accuracy(out["actions"][i], (x[:, i] + y) % 4) for i in range(4)]
    def private(out): return [accuracy(out["private"][i], p[:, i]) for i in range(4)]
    return {
        "global": {"global": accuracy(pg["global_logits"], ty), "actions": actions(pg, ty), "private": private(pg)},
        "local_a": {"local": accuracy(pa["local_a_logits"], tu), "global": accuracy(pa["global_logits"], mixed_a), "actions": actions(pa, mixed_a), "private": private(pa)},
        "local_b": {"local": accuracy(pb["local_b_logits"], tv), "global": accuracy(pb["global_logits"], mixed_b), "actions": actions(pb, mixed_b), "private": private(pb)},
    }


def train(seed: int, config: Config | None = None) -> tuple[NestedModel, FlatController, dict[str, Any]]:
    c = config or Config(); set_determinism(seed, c.threads)
    model = NestedModel(seed, c); x = values_grid(); p = private_grid(len(x)); u, v, y, a = targets(x)

    local_modules = [model.local_a, model.local_b]
    opt = torch.optim.AdamW([q for m in local_modules for q in m.parameters()], lr=c.learning_rate, weight_decay=c.weight_decay)
    def local_loss():
        o = model(x, p); return F.cross_entropy(o["local_a_logits"], u) + F.cross_entropy(o["local_b_logits"], v)
    def local_done():
        with torch.no_grad(): o = model(x, p)
        return bool((o["local_a_logits"].argmax(1) == u).all() and (o["local_b_logits"].argmax(1) == v).all())
    local_steps = train_until(opt, local_loss, local_done, c.local_max_steps, c.local_min_steps, local_modules, c.gradient_clip)
    set_trainable(model.local_a, False); set_trainable(model.local_b, False)

    opt = torch.optim.AdamW(model.global_workspace.parameters(), lr=c.learning_rate, weight_decay=c.weight_decay)
    def global_loss(): return F.cross_entropy(model(x, p)["global_logits"], y)
    def global_done():
        with torch.no_grad(): o = model(x, p)
        return bool((o["global_logits"].argmax(1) == y).all())
    global_steps = train_until(opt, global_loss, global_done, c.global_max_steps, c.global_min_steps, [model.global_workspace], c.gradient_clip)
    set_trainable(model.global_workspace, False)

    td_modules = [model.revise_a, model.revise_b, model.action_heads]
    opt = torch.optim.AdamW([q for m in td_modules for q in m.parameters()], lr=c.learning_rate, weight_decay=c.weight_decay)
    ta = x.clone(); ta[:, 0] = (ta[:, 0] + 1) % 4
    tb = x.clone(); tb[:, 2] = (tb[:, 2] + 1) % 4
    tp = torch.roll(p, 1, 0)
    tu, _, ty, _ = targets(ta); _, tv, _, _ = targets(tb)
    mixed_a = (tu + v) % 4; mixed_b = (u + tv) % 4
    def patched_loss(out, gy): return sum(F.cross_entropy(out["actions"][i], (x[:, i] + gy) % 4) for i in range(4))
    def td_loss():
        natural = model(x, p)
        with torch.no_grad():
            oa = model(ta, tp); ob = model(tb, tp)
            gstate = oa["global_state"].detach(); lastate = oa["local_a"].detach(); lbstate = ob["local_b"].detach()
        pg = model(x, p, patch_global=gstate); pa = model(x, p, patch_local_a=lastate); pb = model(x, p, patch_local_b=lbstate)
        return sum(F.cross_entropy(natural["actions"][i], a[i]) for i in range(4)) + patched_loss(pg, ty) + patched_loss(pa, mixed_a) + patched_loss(pb, mixed_b)
    def td_done():
        with torch.no_grad():
            o = model(x, p); intact = all((o["actions"][i].argmax(1) == a[i]).all() for i in range(4)); patches = patch_tests(model)
        return bool(intact and min(patches["global"]["actions"] + patches["local_a"]["actions"] + patches["local_b"]["actions"]) >= 0.999999)
    td_steps = train_until(opt, td_loss, td_done, c.topdown_max_steps, c.topdown_min_steps, td_modules, c.gradient_clip)

    opt = torch.optim.AdamW(model.private_heads.parameters(), lr=c.learning_rate, weight_decay=c.weight_decay)
    def priv_loss(): return sum(F.cross_entropy(model.private_logits(p)[i], p[:, i]) for i in range(4))
    def priv_done():
        with torch.no_grad(): q = model.private_logits(p)
        return all((q[i].argmax(1) == p[:, i]).all() for i in range(4))
    priv_steps = train_until(opt, priv_loss, priv_done, c.private_max_steps, c.private_min_steps, [model.private_heads], c.gradient_clip)

    flat = FlatController([getattr(model, f"task_code_{i}") for i in range(4)], c)
    opt = torch.optim.AdamW(flat.parameters(), lr=c.learning_rate, weight_decay=c.weight_decay)
    def flat_loss():
        o = flat(x); return F.cross_entropy(o["global_logits"], y) + sum(F.cross_entropy(o["actions"][i], a[i]) for i in range(4))
    def flat_done():
        with torch.no_grad(): o = flat(x)
        return bool((o["global_logits"].argmax(1) == y).all() and all((o["actions"][i].argmax(1) == a[i]).all() for i in range(4)))
    flat_steps = train_until(opt, flat_loss, flat_done, c.flat_max_steps, c.flat_min_steps, [flat], c.gradient_clip)

    receipt = {
        "seed": int(seed), "local_steps": local_steps, "global_steps": global_steps,
        "topdown_steps": td_steps, "private_steps": priv_steps, "flat_steps": flat_steps,
        "model_sha256": state_dict_sha256(model), "flat_sha256": state_dict_sha256(flat),
    }
    receipt["digest"] = digest(receipt)
    return model, flat, receipt


def endpoints(result: Mapping[str, Any]) -> dict[str, bool]:
    i = result["information"]; m = result["modes"]; p = result["patches"]; intact = m["intact"]
    leaf_cuts = [m[k] for k in ("leaf_a1_cut", "leaf_a2_cut", "leaf_b1_cut", "leaf_b2_cut")]
    all_private = [v for mode in m.values() for v in mode["private"]] + p["global"]["private"] + p["local_a"]["private"] + p["local_b"]["private"]
    return {
        "N01_local_a_exact_synergy": abs(i["I_U_A1"]) < 1e-12 and abs(i["I_U_A2"]) < 1e-12 and i["I_U_A1A2"] > 1.999999,
        "N02_local_b_exact_synergy": abs(i["I_V_B1"]) < 1e-12 and abs(i["I_V_B2"]) < 1e-12 and i["I_V_B1B2"] > 1.999999,
        "N03_global_exact_synergy": abs(i["I_Y_U"]) < 1e-12 and abs(i["I_Y_V"]) < 1e-12 and i["I_Y_UV"] > 1.999999,
        "N04_intact_solves": min(intact["local_a"], intact["local_b"], intact["global"], intact["mean_action"], intact["mean_private"]) >= .99,
        "N05_each_leaf_is_necessary": max(q["global"] for q in leaf_cuts) <= .30 and min(q["mean_private"] for q in leaf_cuts) >= .99,
        "N06_local_a_is_necessary": m["local_a_cut"]["local_a"] <= .30 and m["local_a_cut"]["local_b"] >= .99 and m["local_a_cut"]["global"] <= .30,
        "N07_local_b_is_necessary": m["local_b_cut"]["local_b"] <= .30 and m["local_b_cut"]["local_a"] >= .99 and m["local_b_cut"]["global"] <= .30,
        "N08_global_is_separable": m["global_cut"]["local_a"] >= .99 and m["global_cut"]["local_b"] >= .99 and m["global_cut"]["global"] <= .30 and m["global_cut"]["mean_action"] <= .30,
        "N09_topdown_is_necessary": m["topdown_cut"]["local_a"] >= .99 and m["topdown_cut"]["local_b"] >= .99 and m["topdown_cut"]["global"] >= .99 and m["topdown_cut"]["mean_action"] <= .30,
        "N10_global_patch": p["global"]["global"] >= .99 and min(p["global"]["actions"]) >= .99,
        "N11_local_a_patch": p["local_a"]["local"] >= .99 and p["local_a"]["global"] >= .99 and min(p["local_a"]["actions"]) >= .99,
        "N12_local_b_patch": p["local_b"]["local"] >= .99 and p["local_b"]["global"] >= .99 and min(p["local_b"]["actions"]) >= .99,
        "N13_private_preserved": min(all_private) >= .99,
        "N14_flat_also_solves": result["flat"]["global"] >= .99 and result["flat"]["mean_action"] >= .99,
        "N15_local_compression": result["architecture"]["local_dim"] < result["architecture"]["leaf_pair_dim"],
        "N16_global_compression": result["architecture"]["global_dim"] < result["architecture"]["combined_local_dim"],
        "N17_no_valence_shortcut": not result["valence_model_present"] and result["survival_reward"] == result["identity_reward"] == result["continuity_reward"] == 0.0,
        "N18_bidirectional_hierarchy": p["local_a"]["global"] >= .99 and p["global"]["global"] >= .99 and m["topdown_cut"]["mean_action"] <= .30,
    }


def analyze(seed: int, save_model: Path | None = None) -> dict[str, Any]:
    model, flat, training = train(seed)
    mode_names = ("intact", "leaf_a1_cut", "leaf_a2_cut", "leaf_b1_cut", "leaf_b2_cut", "local_a_cut", "local_b_cut", "global_cut", "topdown_cut")
    result = {
        "schema": "rrct.v052.dev3.seed_result.v1", "version": VERSION, "seed": int(seed),
        "information": information_receipt(), "training": training,
        "modes": {k: evaluate(model, k) for k in mode_names}, "patches": patch_tests(model), "flat": evaluate_flat(flat),
        "architecture": {"leaf_agents": 4, "local_workspaces": 2, "global_workspaces": 1, "leaf_pair_dim": 2 * model.config.leaf_dim, "local_dim": model.config.local_dim, "combined_local_dim": 2 * model.config.local_dim, "global_dim": model.config.global_dim},
        "survival_reward": 0.0, "identity_reward": 0.0, "continuity_reward": 0.0, "valence_model_present": False,
    }
    result["endpoints"] = endpoints(result); result["all_endpoints_met"] = all(result["endpoints"].values()); result["digest"] = digest(result)
    if save_model:
        save_model.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"seed": seed, "model": model.state_dict(), "flat": flat.state_dict(), "training": training}, save_model)
    return result


def aggregate(seed_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    names = list(seed_results[0]["endpoints"])
    eps = {k: all(r["endpoints"][k] for r in seed_results) for k in names}
    modes = {}
    for mode in seed_results[0]["modes"]:
        modes[mode] = {key: float(np.mean([r["modes"][mode][key] for r in seed_results])) for key in ("local_a", "local_b", "global", "mean_action", "mean_private")}
    out = {
        "schema": "rrct.v052.dev3.summary.v1", "version": VERSION, "scientific_status": "limited_two_level_pilot",
        "seeds": [r["seed"] for r in seed_results], "seed_count": len(seed_results), "endpoints": eps, "all_endpoints_met": all(eps.values()),
        "modes": modes, "flat_global": float(np.mean([r["flat"]["global"] for r in seed_results])), "flat_actions": float(np.mean([r["flat"]["mean_action"] for r in seed_results])),
        "claim_boundary": "Two-level synthetic existence and causal-dissociation pilot only; no spontaneous hierarchy, brain equivalence, awareness, or subjective-experience claim.",
    }
    out["status"] = "V052_LIMITED_NESTED_WORKSPACE_ENDPOINTS_MET" if out["all_endpoints_met"] else "V052_LIMITED_NESTED_WORKSPACE_ENDPOINTS_NOT_MET"
    out["digest"] = digest(out)
    return out
