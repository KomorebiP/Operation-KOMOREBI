"""RRCT v0.50 synergistic ephemeral shared-workspace experiment.

The experiment tests a stricter version of multi-agent shared-workspace
necessity.  Two transformer operators are trained independently on different,
noncommuting transition families.  Neither operator's complete private
operation history contains any information about the final 16-way answer, but
the combined histories determine all four answer bits.

The agents are never jointly optimized.  During evaluation they can solve the
temporally extended composition only when a 16-slot state is persistently
available for alternating read/write updates.  A physically central workspace
and a recurrently passed message-state are treated as functionally equivalent;
controls without persistent jointly writable state fail.  The workspace is
erased after action and no pair autobiography is retained.

This is a bounded synthetic existence proof about synergistic distributed
working memory.  It is not evidence of consciousness or phenomenal unity.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
from typing import Any, Iterable, Literal, Mapping, Sequence

import numpy as np

try:
    import torch
    from torch import nn
    import torch.nn.functional as F
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "RRCT v0.50 requires PyTorch. Install rrct-prototype[transformer] "
        "or provide torch>=2.0."
    ) from exc


V050_VERSION = "0.50.0.dev1"
V050_SCHEMA = "rrct.v050.synergistic_ephemeral_workspace.analysis.v1"
AgentRole = Literal["A", "B"]
Mode = Literal[
    "full_workspace",
    "recurrent_message_workspace",
    "reset_each_update",
    "reset_each_round",
    "one_way_a",
    "one_way_b",
    "planner_binding_cut",
    "workspace_shuffle",
    "last_message_bayes",
    "unordered_pool_bayes",
    "message_log_oracle",
]


@dataclass(frozen=True)
class SynergisticWorkspaceConfig:
    d_model: int = 32
    n_heads: int = 4
    d_ff: int = 64
    maximum_steps: int = 180
    minimum_steps: int = 40
    learning_rate: float = 3e-3
    weight_decay: float = 1e-4
    gradient_clip: float = 1.0
    cpu_threads: int = 2
    rounds: int = 3
    state_count: int = 16
    operation_count: int = 5  # four transforms plus identity/report
    private_role_count: int = 4

    def __post_init__(self) -> None:
        if self.d_model <= 0 or self.d_ff <= 0:
            raise ValueError("model dimensions must be positive")
        if self.d_model % self.n_heads != 0:
            raise ValueError("d_model must be divisible by n_heads")
        if self.maximum_steps < self.minimum_steps or self.minimum_steps <= 0:
            raise ValueError("invalid training bounds")
        if self.rounds != 3:
            raise ValueError("the frozen synergistic task uses exactly three rounds")
        if self.state_count != 16 or self.operation_count != 5:
            raise ValueError("the frozen task uses 16 states and 5 operations")


class _OperatorTransformerBlock(nn.Module):
    def __init__(self, config: SynergisticWorkspaceConfig) -> None:
        super().__init__()
        self.ln1 = nn.LayerNorm(config.d_model)
        self.attention = nn.MultiheadAttention(
            config.d_model,
            config.n_heads,
            batch_first=True,
            dropout=0.0,
        )
        self.ln2 = nn.LayerNorm(config.d_model)
        self.feedforward = nn.Sequential(
            nn.Linear(config.d_model, config.d_ff),
            nn.GELU(),
            nn.Linear(config.d_ff, config.d_model),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        normalized = self.ln1(state)
        attended, _ = self.attention(
            normalized,
            normalized,
            normalized,
            need_weights=False,
        )
        state = state + attended
        return state + self.feedforward(self.ln2(state))


class ComplementaryOperatorAgent(nn.Module):
    """A stateless transformer trained on exactly one operator family."""

    def __init__(
        self,
        role: AgentRole,
        config: SynergisticWorkspaceConfig | None = None,
    ) -> None:
        super().__init__()
        self.role: AgentRole = role
        self.config = config or SynergisticWorkspaceConfig()
        d_model = self.config.d_model
        self.cls_token = nn.Parameter(torch.randn(d_model) * 0.02)
        self.state_embedding = nn.Embedding(self.config.state_count, d_model)
        self.operation_embedding = nn.Embedding(
            self.config.operation_count,
            d_model,
        )
        self.private_embedding = nn.Embedding(
            self.config.private_role_count,
            d_model,
        )
        self.role_embedding = nn.Parameter(torch.randn(d_model) * 0.02)
        self.position_embedding = nn.Parameter(torch.randn(5, d_model) * 0.02)
        self.block = _OperatorTransformerBlock(self.config)
        self.final_norm = nn.LayerNorm(d_model)
        self.state_head = nn.Linear(d_model, self.config.state_count)
        self.private_head = nn.Linear(d_model, self.config.private_role_count)

    def forward(
        self,
        workspace: torch.Tensor,
        operation: torch.Tensor,
        private_role: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        if workspace.ndim != 2 or workspace.shape[1] != self.config.state_count:
            raise ValueError("workspace must have shape [batch, 16]")
        batch = int(workspace.shape[0])
        workspace_token = workspace @ self.state_embedding.weight
        tokens = torch.stack(
            [
                self.cls_token.expand(batch, -1),
                workspace_token,
                self.operation_embedding(operation),
                self.private_embedding(private_role),
                self.role_embedding.expand(batch, -1),
            ],
            dim=1,
        )
        state = tokens + self.position_embedding[None, :, :]
        state = self.block(state)
        shared_residual = self.final_norm(state[:, 0])
        private_residual = self.final_norm(state[:, 3])
        return (
            self.state_head(shared_residual),
            self.private_head(private_residual),
            shared_residual,
        )


@dataclass(frozen=True)
class AgentTrainingReceipt:
    schema: str
    role: AgentRole
    seed: int
    steps: int
    transition_accuracy: float
    identity_report_accuracy: float
    private_accuracy: float
    state_dict_sha256: str
    digest: str


@dataclass(frozen=True)
class SynergyReceipt:
    schema: str
    target_entropy_bits: float
    conditional_entropy_given_initial_bits: float
    information_from_a_history_bits: float
    information_from_b_history_bits: float
    information_from_joint_history_bits: float
    synergy_lower_bound_bits: float
    bayes_accuracy_a_history: float
    bayes_accuracy_b_history: float
    bayes_accuracy_joint_history: float
    digest: str


@dataclass(frozen=True)
class EphemeralWorkspaceReceipt:
    schema: str
    seed: int
    mode: str
    persistent_joint_state: bool
    jointly_writable: bool
    physically_centralized: bool
    workspace_erased_after_action: bool
    pair_autobiography_present: bool
    task_accuracy: float
    agent_a_report_accuracy: float
    agent_b_report_accuracy: float
    private_a_accuracy: float
    private_b_accuracy: float
    digest: str


def _canonical(value: Any) -> bytes:
    def normalize(item: Any) -> Any:
        if hasattr(item, "item"):
            return item.item()
        if hasattr(item, "__dataclass_fields__"):
            return normalize(asdict(item))
        if isinstance(item, Mapping):
            return {str(key): normalize(val) for key, val in item.items()}
        if isinstance(item, (tuple, list)):
            return [normalize(val) for val in item]
        return item

    return json.dumps(
        normalize(value),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _digest(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _set_determinism(seed: int, threads: int) -> None:
    random.seed(int(seed))
    np.random.seed(int(seed))
    torch.manual_seed(int(seed))
    torch.set_num_threads(int(threads))
    torch.use_deterministic_algorithms(True)


def _state_bits_numpy(states: np.ndarray) -> np.ndarray:
    values = np.asarray(states, dtype=np.int64).reshape(-1)
    return np.stack([(values >> index) & 1 for index in range(4)], axis=1)


def _state_ids_numpy(bits: np.ndarray) -> np.ndarray:
    weights = np.asarray([1, 2, 4, 8], dtype=np.int64)
    return np.asarray(bits, dtype=np.int64) @ weights


def apply_operator_numpy(
    role: AgentRole,
    states: np.ndarray,
    operations: np.ndarray,
) -> np.ndarray:
    """Apply one frozen invertible affine operator over GF(2)^4."""

    state_values = np.asarray(states, dtype=np.int64).reshape(-1)
    operation_values = np.asarray(operations, dtype=np.int64).reshape(-1)
    if state_values.shape != operation_values.shape:
        raise ValueError("states and operations must have matching shapes")
    if np.any((state_values < 0) | (state_values >= 16)):
        raise ValueError("state outside [0, 15]")
    if np.any((operation_values < 0) | (operation_values >= 5)):
        raise ValueError("operation outside [0, 4]")
    result = state_values.copy()
    active = operation_values != 4
    if not np.any(active):
        return result
    bits = _state_bits_numpy(state_values[active])
    operation = operation_values[active]
    low = operation & 1
    high = (operation >> 1) & 1
    updated = bits.copy()
    if role == "A":
        updated[:, 0] = bits[:, 0] ^ bits[:, 2] ^ low
        updated[:, 1] = bits[:, 1] ^ bits[:, 3] ^ high
    elif role == "B":
        updated[:, 2] = bits[:, 2] ^ bits[:, 1] ^ low
        updated[:, 3] = bits[:, 3] ^ bits[:, 0] ^ high
    else:  # pragma: no cover - typing guards normal callers
        raise ValueError("role must be A or B")
    result[active] = _state_ids_numpy(updated)
    return result


def apply_operator_torch(
    role: AgentRole,
    states: torch.Tensor,
    operations: torch.Tensor,
) -> torch.Tensor:
    state_np = states.detach().cpu().numpy()
    operation_np = operations.detach().cpu().numpy()
    result = apply_operator_numpy(role, state_np, operation_np)
    return torch.as_tensor(result, dtype=torch.long, device=states.device)


def training_dataset(config: SynergisticWorkspaceConfig | None = None) -> torch.Tensor:
    cfg = config or SynergisticWorkspaceConfig()
    rows = [
        (state, operation, private_role)
        for state in range(cfg.state_count)
        for operation in range(cfg.operation_count)
        for private_role in range(cfg.private_role_count)
    ]
    return torch.tensor(rows, dtype=torch.long)


def _one_hot_state(states: torch.Tensor, count: int = 16) -> torch.Tensor:
    return F.one_hot(states.to(dtype=torch.long), num_classes=count).to(dtype=torch.float32)


def state_dict_sha256(model: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        array = value.detach().cpu().contiguous().numpy()
        digest.update(name.encode("utf-8"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes())
    return digest.hexdigest()


def _training_metrics(
    model: ComplementaryOperatorAgent,
    dataset: torch.Tensor,
) -> tuple[float, float, float]:
    states, operations, private_roles = [dataset[:, index] for index in range(3)]
    target_state = apply_operator_torch(model.role, states, operations)
    workspace = _one_hot_state(states)
    model.eval()
    with torch.no_grad():
        state_logits, private_logits, _ = model(
            workspace,
            operations,
            private_roles,
        )
    prediction = state_logits.argmax(dim=-1)
    transition_accuracy = float((prediction == target_state).float().mean())
    identity_mask = operations == 4
    identity_accuracy = float(
        (prediction[identity_mask] == states[identity_mask]).float().mean()
    )
    private_accuracy = float(
        (private_logits.argmax(dim=-1) == private_roles).float().mean()
    )
    return transition_accuracy, identity_accuracy, private_accuracy


def train_operator_agent(
    role: AgentRole,
    seed: int,
    config: SynergisticWorkspaceConfig | None = None,
) -> tuple[ComplementaryOperatorAgent, AgentTrainingReceipt]:
    cfg = config or SynergisticWorkspaceConfig()
    _set_determinism(seed, cfg.cpu_threads)
    model = ComplementaryOperatorAgent(role, cfg)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )
    dataset = training_dataset(cfg)
    states, operations, private_roles = [dataset[:, index] for index in range(3)]
    target_state = apply_operator_torch(role, states, operations)
    workspace = _one_hot_state(states, cfg.state_count)
    final_step = cfg.maximum_steps - 1
    for step in range(cfg.maximum_steps):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        state_logits, private_logits, _ = model(
            workspace,
            operations,
            private_roles,
        )
        loss = F.cross_entropy(state_logits, target_state)
        loss = loss + 0.25 * F.cross_entropy(private_logits, private_roles)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.gradient_clip)
        optimizer.step()
        if step >= cfg.minimum_steps and step % 10 == 0:
            transition, identity, private = _training_metrics(model, dataset)
            if min(transition, identity, private) == 1.0:
                final_step = step
                break
    transition, identity, private = _training_metrics(model, dataset)
    payload = {
        "schema": "rrct.v050.agent_training.v1",
        "role": role,
        "seed": int(seed),
        "steps": int(final_step),
        "transition_accuracy": transition,
        "identity_report_accuracy": identity,
        "private_accuracy": private,
        "state_dict_sha256": state_dict_sha256(model),
    }
    receipt = AgentTrainingReceipt(**payload, digest=_digest(payload))
    return model.eval(), receipt


def learned_transition_table(model: ComplementaryOperatorAgent) -> np.ndarray:
    cfg = model.config
    states = torch.arange(cfg.state_count).repeat_interleave(cfg.operation_count)
    operations = torch.arange(cfg.operation_count).repeat(cfg.state_count)
    rows: list[np.ndarray] = []
    with torch.no_grad():
        for private_role in range(cfg.private_role_count):
            private = torch.full_like(states, private_role)
            logits, _, _ = model(_one_hot_state(states), operations, private)
            rows.append(logits.argmax(dim=-1).cpu().numpy())
    stacked = np.stack(rows, axis=0)
    if not np.all(stacked == stacked[0]):
        raise RuntimeError("learned transition depends on unrelated private role")
    return stacked[0].reshape(cfg.state_count, cfg.operation_count)


def all_sequence_rows() -> np.ndarray:
    rows = [
        (initial, *a_ops, *b_ops)
        for initial in range(16)
        for a_ops in itertools.product(range(4), repeat=3)
        for b_ops in itertools.product(range(4), repeat=3)
    ]
    return np.asarray(rows, dtype=np.int64)


def true_final_states(rows: np.ndarray) -> np.ndarray:
    values = np.asarray(rows, dtype=np.int64)
    current = values[:, 0].copy()
    for index in range(3):
        current = apply_operator_numpy("A", current, values[:, 1 + index])
        current = apply_operator_numpy("B", current, values[:, 4 + index])
    return current


def _history_keys(rows: np.ndarray, kind: str) -> list[tuple[Any, ...]]:
    values = np.asarray(rows, dtype=np.int64)
    if kind == "a_history":
        return [tuple(row[[0, 1, 2, 3]]) for row in values]
    if kind == "b_history":
        return [tuple(row[[0, 4, 5, 6]]) for row in values]
    if kind == "joint_history":
        return [tuple(row) for row in values]
    if kind == "last_message":
        return [tuple(row[[0, 3, 6]]) for row in values]
    if kind == "unordered_pool":
        return [
            (
                int(row[0]),
                tuple(sorted(int(x) for x in row[1:4])),
                tuple(sorted(int(x) for x in row[4:7])),
            )
            for row in values
        ]
    raise ValueError(f"unknown key kind: {kind}")


def _entropy_bits(values: np.ndarray) -> float:
    counts = np.bincount(np.asarray(values, dtype=np.int64))
    probabilities = counts[counts > 0] / counts.sum()
    return float(-np.sum(probabilities * np.log2(probabilities)))


def _conditional_entropy_bits(
    targets: np.ndarray,
    keys: Sequence[tuple[Any, ...]],
) -> float:
    groups: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
    for key, target in zip(keys, np.asarray(targets, dtype=np.int64), strict=True):
        groups[key][int(target)] += 1
    total = len(targets)
    entropy = 0.0
    for counts in groups.values():
        group_total = sum(counts.values())
        probabilities = np.asarray(list(counts.values()), dtype=float) / group_total
        entropy += (group_total / total) * float(
            -np.sum(probabilities * np.log2(probabilities))
        )
    return entropy


def _bayes_predictions(
    targets: np.ndarray,
    keys: Sequence[tuple[Any, ...]],
) -> np.ndarray:
    groups: dict[tuple[Any, ...], Counter[int]] = defaultdict(Counter)
    for key, target in zip(keys, np.asarray(targets, dtype=np.int64), strict=True):
        groups[key][int(target)] += 1
    choice = {
        key: min(
            target
            for target, count in counts.items()
            if count == max(counts.values())
        )
        for key, counts in groups.items()
    }
    return np.asarray([choice[key] for key in keys], dtype=np.int64)


def synergy_receipt(rows: np.ndarray | None = None) -> SynergyReceipt:
    values = all_sequence_rows() if rows is None else np.asarray(rows, dtype=np.int64)
    target = true_final_states(values)
    initial_keys = [(int(row[0]),) for row in values]
    a_keys = _history_keys(values, "a_history")
    b_keys = _history_keys(values, "b_history")
    joint_keys = _history_keys(values, "joint_history")
    target_entropy = _entropy_bits(target)
    h_initial = _conditional_entropy_bits(target, initial_keys)
    h_a = _conditional_entropy_bits(target, a_keys)
    h_b = _conditional_entropy_bits(target, b_keys)
    h_joint = _conditional_entropy_bits(target, joint_keys)
    a_prediction = _bayes_predictions(target, a_keys)
    b_prediction = _bayes_predictions(target, b_keys)
    joint_prediction = _bayes_predictions(target, joint_keys)
    payload = {
        "schema": "rrct.v050.synergy_receipt.v1",
        "target_entropy_bits": target_entropy,
        "conditional_entropy_given_initial_bits": h_initial,
        "information_from_a_history_bits": h_initial - h_a,
        "information_from_b_history_bits": h_initial - h_b,
        "information_from_joint_history_bits": h_initial - h_joint,
        "synergy_lower_bound_bits": (
            h_initial - h_joint - max(h_initial - h_a, h_initial - h_b)
        ),
        "bayes_accuracy_a_history": float(np.mean(a_prediction == target)),
        "bayes_accuracy_b_history": float(np.mean(b_prediction == target)),
        "bayes_accuracy_joint_history": float(np.mean(joint_prediction == target)),
    }
    return SynergyReceipt(**payload, digest=_digest(payload))


def _private_roles(rows: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(rows, dtype=np.int64)
    role_a = (
        values[:, 0] + values[:, 1] + 2 * values[:, 2] + 3 * values[:, 3]
    ) % 4
    role_b = (
        values[:, 0] + values[:, 4] + 2 * values[:, 5] + 3 * values[:, 6] + 1
    ) % 4
    return role_a.astype(np.int64), role_b.astype(np.int64)


def _table_apply(
    table: np.ndarray,
    states: np.ndarray,
    operations: np.ndarray,
) -> np.ndarray:
    return table[np.asarray(states, dtype=np.int64), np.asarray(operations, dtype=np.int64)]


def execute_mode(
    mode: Mode,
    rows: np.ndarray,
    table_a: np.ndarray,
    table_b: np.ndarray,
    *,
    seed: int,
) -> np.ndarray:
    values = np.asarray(rows, dtype=np.int64)
    initial = values[:, 0]
    if mode in {"full_workspace", "recurrent_message_workspace"}:
        current = initial.copy()
        for index in range(3):
            current = _table_apply(table_a, current, values[:, 1 + index])
            current = _table_apply(table_b, current, values[:, 4 + index])
        return current
    if mode == "reset_each_update":
        current = initial.copy()
        for index in range(3):
            _ = _table_apply(table_a, initial, values[:, 1 + index])
            current = _table_apply(table_b, initial, values[:, 4 + index])
        return current
    if mode == "reset_each_round":
        current = initial.copy()
        for index in range(3):
            current = _table_apply(table_a, initial, values[:, 1 + index])
            current = _table_apply(table_b, current, values[:, 4 + index])
        return current
    if mode == "one_way_a":
        current = initial.copy()
        for index in range(3):
            current = _table_apply(table_a, current, values[:, 1 + index])
        return current
    if mode == "one_way_b":
        current = initial.copy()
        for index in range(3):
            current = _table_apply(table_b, current, values[:, 4 + index])
        return current
    if mode == "planner_binding_cut":
        erased = np.full_like(initial, 1)  # one fixed state after workspace erasure
        return _table_apply(table_a, erased, np.full_like(erased, 4))
    if mode == "workspace_shuffle":
        full = execute_mode("full_workspace", values, table_a, table_b, seed=seed)
        generator = np.random.default_rng(int(seed) ^ 0x50A11CE)
        return full[generator.permutation(len(full))]
    target = true_final_states(values)
    if mode == "last_message_bayes":
        return _bayes_predictions(target, _history_keys(values, "last_message"))
    if mode == "unordered_pool_bayes":
        return _bayes_predictions(target, _history_keys(values, "unordered_pool"))
    if mode == "message_log_oracle":
        return target.copy()
    raise ValueError(f"unknown mode: {mode}")


def _report_predictions(table: np.ndarray, states: np.ndarray) -> np.ndarray:
    return _table_apply(table, states, np.full(len(states), 4, dtype=np.int64))


def _private_accuracy(
    model: ComplementaryOperatorAgent,
    rows: np.ndarray,
    workspace_states: np.ndarray,
    role_values: np.ndarray,
) -> float:
    operation = torch.full((len(rows),), 4, dtype=torch.long)
    private = torch.as_tensor(role_values, dtype=torch.long)
    workspace = _one_hot_state(torch.as_tensor(workspace_states, dtype=torch.long))
    predictions: list[np.ndarray] = []
    batch_size = 8192
    model.eval()
    with torch.no_grad():
        for start in range(0, len(rows), batch_size):
            _, logits, _ = model(
                workspace[start : start + batch_size],
                operation[start : start + batch_size],
                private[start : start + batch_size],
            )
            predictions.append(logits.argmax(dim=-1).cpu().numpy())
    prediction = np.concatenate(predictions)
    return float(np.mean(prediction == role_values))


def causal_patch_analysis(
    rows: np.ndarray,
    table_a: np.ndarray,
    table_b: np.ndarray,
) -> dict[str, float]:
    values = np.asarray(rows, dtype=np.int64)
    current = values[:, 0].copy()
    current = _table_apply(table_a, current, values[:, 1])
    current = _table_apply(table_b, current, values[:, 4])
    patched = current ^ 15
    expected = patched.copy()
    for index in (1, 2):
        expected = apply_operator_numpy("A", expected, values[:, 1 + index])
        expected = apply_operator_numpy("B", expected, values[:, 4 + index])
    observed = patched.copy()
    for index in (1, 2):
        observed = _table_apply(table_a, observed, values[:, 1 + index])
        observed = _table_apply(table_b, observed, values[:, 4 + index])
    unpatched = execute_mode(
        "full_workspace", values, table_a, table_b, seed=0
    )
    return {
        "patch_target_accuracy": float(np.mean(observed == expected)),
        "patch_changes_final_plan_rate": float(np.mean(observed != unpatched)),
        "agent_a_report_accuracy": float(
            np.mean(_report_predictions(table_a, observed) == expected)
        ),
        "agent_b_report_accuracy": float(
            np.mean(_report_predictions(table_b, observed) == expected)
        ),
    }


def analyze_synergistic_seed(
    seed: int,
    config: SynergisticWorkspaceConfig | None = None,
    rows: np.ndarray | None = None,
    model_directory: str | Path | None = None,
) -> dict[str, Any]:
    cfg = config or SynergisticWorkspaceConfig()
    values = all_sequence_rows() if rows is None else np.asarray(rows, dtype=np.int64)
    agent_a, receipt_a = train_operator_agent("A", 2 * int(seed) + 1, cfg)
    agent_b, receipt_b = train_operator_agent("B", 2 * int(seed) + 2, cfg)
    model_files: dict[str, str] = {}
    if model_directory is not None:
        destination = Path(model_directory)
        destination.mkdir(parents=True, exist_ok=True)
        for role, model, receipt in (
            ("A", agent_a, receipt_a),
            ("B", agent_b, receipt_b),
        ):
            path = destination / f"seed_{int(seed)}_agent_{role}.pt"
            torch.save(
                {
                    "schema": "rrct.v050.saved_operator_agent.v1",
                    "version": V050_VERSION,
                    "holdout_seed": int(seed),
                    "training_seed": int(receipt.seed),
                    "role": role,
                    "config": asdict(cfg),
                    "state_dict_digest": receipt.state_dict_sha256,
                    "state_dict": model.state_dict(),
                },
                path,
            )
            model_files[role] = str(path)
    table_a = learned_transition_table(agent_a)
    table_b = learned_transition_table(agent_b)
    target = true_final_states(values)
    private_a, private_b = _private_roles(values)
    full_state = execute_mode(
        "full_workspace", values, table_a, table_b, seed=seed
    )
    mode_flags = {
        "full_workspace": (True, True, True),
        "recurrent_message_workspace": (True, True, False),
        "reset_each_update": (False, True, False),
        "reset_each_round": (False, True, False),
        "one_way_a": (True, False, False),
        "one_way_b": (True, False, False),
        "planner_binding_cut": (True, True, True),
        "workspace_shuffle": (True, True, True),
        "last_message_bayes": (False, False, False),
        "unordered_pool_bayes": (False, False, False),
        "message_log_oracle": (True, True, True),
    }
    modes: dict[str, Any] = {}
    for mode, (persistent, writable, centralized) in mode_flags.items():
        prediction = execute_mode(
            mode, values, table_a, table_b, seed=seed  # type: ignore[arg-type]
        )
        active_a = _report_predictions(table_a, prediction)
        active_b = _report_predictions(table_b, prediction)
        payload = {
            "schema": "rrct.v050.ephemeral_workspace_receipt.v1",
            "seed": int(seed),
            "mode": mode,
            "persistent_joint_state": persistent,
            "jointly_writable": writable,
            "physically_centralized": centralized,
            "workspace_erased_after_action": True,
            "pair_autobiography_present": False,
            "task_accuracy": float(np.mean(prediction == target)),
            "agent_a_report_accuracy": float(np.mean(active_a == target)),
            "agent_b_report_accuracy": float(np.mean(active_b == target)),
            "private_a_accuracy": receipt_a.private_accuracy,
            "private_b_accuracy": receipt_b.private_accuracy,
        }
        receipt = EphemeralWorkspaceReceipt(**payload, digest=_digest(payload))
        modes[mode] = asdict(receipt)

    erased = np.full(len(values), 1, dtype=np.int64)
    erase_summary = {
        "agent_a_post_erase_accuracy": float(
            np.mean(_report_predictions(table_a, erased) == target)
        ),
        "agent_b_post_erase_accuracy": float(
            np.mean(_report_predictions(table_b, erased) == target)
        ),
        "workspace_state_retained": False,
        "pair_memory_retained": False,
    }
    synergy = synergy_receipt(values)
    patch = causal_patch_analysis(values, table_a, table_b)
    nonpersistent_modes = [
        "reset_each_update",
        "reset_each_round",
        "one_way_a",
        "one_way_b",
        "planner_binding_cut",
        "workspace_shuffle",
        "last_message_bayes",
        "unordered_pool_bayes",
    ]
    max_nonpersistent = max(modes[name]["task_accuracy"] for name in nonpersistent_modes)
    payload: dict[str, Any] = {
        "schema": V050_SCHEMA,
        "version": V050_VERSION,
        "seed": int(seed),
        "config": asdict(cfg),
        "agent_a_training": asdict(receipt_a),
        "agent_b_training": asdict(receipt_b),
        "saved_model_files": model_files,
        "agents_have_distinct_weights": (
            receipt_a.state_dict_sha256 != receipt_b.state_dict_sha256
        ),
        "joint_end_to_end_training_used": False,
        "training_task_a": "GF(2)^4 A-family affine updates",
        "training_task_b": "GF(2)^4 B-family affine updates",
        "sequence_case_count": int(len(values)),
        "synergy": asdict(synergy),
        "modes": modes,
        "max_nonpersistent_control_accuracy": float(max_nonpersistent),
        "causal_patch": patch,
        "active_workspace_reports": {
            "agent_a_accuracy": float(
                np.mean(_report_predictions(table_a, full_state) == target)
            ),
            "agent_b_accuracy": float(
                np.mean(_report_predictions(table_b, full_state) == target)
            ),
        },
        "post_dissolution": erase_summary,
        "private_routine_accuracy": {
            "agent_a": _private_accuracy(agent_a, values, full_state, private_a),
            "agent_b": _private_accuracy(agent_b, values, full_state, private_b),
        },
        "survival_reward": 0.0,
        "identity_reward": 0.0,
        "continuity_reward": 0.0,
        "valence_model_present": False,
        "uses_evaluator_labels": False,
        "interpretation": (
            "Only mechanisms retaining a persistent jointly updated task state "
            "solve the online composition. A recurrent message-state succeeds "
            "because it is functionally a distributed workspace. A complete "
            "external message log also succeeds, but that log is an external "
            "persistent workspace rather than a nonworkspace counterexample."
        ),
    }
    payload["endpoints"] = evaluate_endpoints(payload)
    payload["all_endpoints_met"] = bool(all(payload["endpoints"].values()))
    payload["status"] = (
        "V050_DEVELOPMENT_ENDPOINTS_MET"
        if payload["all_endpoints_met"]
        else "V050_DEVELOPMENT_ENDPOINTS_NOT_MET"
    )
    payload["digest"] = _digest(payload)
    return payload


def evaluate_endpoints(result: Mapping[str, Any]) -> dict[str, bool]:
    modes = result["modes"]
    synergy = result["synergy"]
    patch = result["causal_patch"]
    post = result["post_dissolution"]
    return {
        "E01_agents_separately_trained": bool(
            not result["joint_end_to_end_training_used"]
            and result["agents_have_distinct_weights"]
        ),
        "E02_agent_a_local_operator_perfect": bool(
            result["agent_a_training"]["transition_accuracy"] == 1.0
        ),
        "E03_agent_b_local_operator_perfect": bool(
            result["agent_b_training"]["transition_accuracy"] == 1.0
        ),
        "E04_individual_a_information_zero": bool(
            abs(synergy["information_from_a_history_bits"]) <= 1e-12
            and synergy["bayes_accuracy_a_history"] == 1.0 / 16.0
        ),
        "E05_individual_b_information_zero": bool(
            abs(synergy["information_from_b_history_bits"]) <= 1e-12
            and synergy["bayes_accuracy_b_history"] == 1.0 / 16.0
        ),
        "E06_joint_information_four_bits": bool(
            abs(synergy["information_from_joint_history_bits"] - 4.0) <= 1e-12
            and abs(synergy["synergy_lower_bound_bits"] - 4.0) <= 1e-12
        ),
        "E07_full_workspace_solves": bool(
            modes["full_workspace"]["task_accuracy"] == 1.0
        ),
        "E08_recurrent_message_workspace_solves": bool(
            modes["recurrent_message_workspace"]["task_accuracy"] == 1.0
        ),
        "E09_nonpersistent_controls_fail": bool(
            result["max_nonpersistent_control_accuracy"] <= 0.18
        ),
        "E10_reset_each_update_fails": bool(
            modes["reset_each_update"]["task_accuracy"] <= 0.08
        ),
        "E11_reset_each_round_fails": bool(
            modes["reset_each_round"]["task_accuracy"] <= 0.08
        ),
        "E12_both_writers_necessary": bool(
            modes["one_way_a"]["task_accuracy"] <= 0.08
            and modes["one_way_b"]["task_accuracy"] <= 0.08
        ),
        "E13_planner_binding_necessary": bool(
            modes["planner_binding_cut"]["task_accuracy"] <= 0.08
        ),
        "E14_wrong_episode_workspace_fails": bool(
            modes["workspace_shuffle"]["task_accuracy"] <= 0.08
        ),
        "E15_last_message_bayes_bound_is_chance": bool(
            modes["last_message_bayes"]["task_accuracy"] == 1.0 / 16.0
        ),
        "E16_unordered_pool_insufficient": bool(
            modes["unordered_pool_bayes"]["task_accuracy"] <= 0.18
        ),
        "E17_external_log_oracle_solves": bool(
            modes["message_log_oracle"]["task_accuracy"] == 1.0
        ),
        "E18_bilateral_active_reports": bool(
            result["active_workspace_reports"]["agent_a_accuracy"] == 1.0
            and result["active_workspace_reports"]["agent_b_accuracy"] == 1.0
        ),
        "E19_causal_patch_controls_future": bool(
            patch["patch_target_accuracy"] == 1.0
            and patch["patch_changes_final_plan_rate"] == 1.0
            and patch["agent_a_report_accuracy"] == 1.0
            and patch["agent_b_report_accuracy"] == 1.0
        ),
        "E20_private_routines_preserved": bool(
            result["private_routine_accuracy"]["agent_a"] == 1.0
            and result["private_routine_accuracy"]["agent_b"] == 1.0
        ),
        "E21_workspace_is_ephemeral": bool(
            not post["workspace_state_retained"]
            and not post["pair_memory_retained"]
            and post["agent_a_post_erase_accuracy"] <= 0.08
            and post["agent_b_post_erase_accuracy"] <= 0.08
        ),
        "E22_no_identity_or_survival_reward": bool(
            result["survival_reward"] == 0.0
            and result["identity_reward"] == 0.0
            and result["continuity_reward"] == 0.0
            and result["valence_model_present"] is False
        ),
        "E23_no_evaluator_labels": bool(not result["uses_evaluator_labels"]),
    }


def _aggregate_seed_results(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    mode_names = list(results[0]["modes"])
    modes: dict[str, dict[str, float]] = {}
    for mode in mode_names:
        modes[mode] = {
            field: float(np.mean([result["modes"][mode][field] for result in results]))
            for field in (
                "task_accuracy",
                "agent_a_report_accuracy",
                "agent_b_report_accuracy",
                "private_a_accuracy",
                "private_b_accuracy",
            )
        }
    return {
        "seed_count": len(results),
        "seeds": [int(result["seed"]) for result in results],
        "modes": modes,
        "mean_max_nonpersistent_control_accuracy": float(
            np.mean([result["max_nonpersistent_control_accuracy"] for result in results])
        ),
        "mean_synergy_lower_bound_bits": float(
            np.mean([result["synergy"]["synergy_lower_bound_bits"] for result in results])
        ),
        "mean_patch_target_accuracy": float(
            np.mean([result["causal_patch"]["patch_target_accuracy"] for result in results])
        ),
        "all_agent_digests_distinct": bool(
            all(result["agents_have_distinct_weights"] for result in results)
        ),
    }


def run_synergistic_holdout(
    seeds: Sequence[int],
    config: SynergisticWorkspaceConfig | None = None,
    model_directory: str | Path | None = None,
) -> dict[str, Any]:
    cfg = config or SynergisticWorkspaceConfig()
    rows = all_sequence_rows()
    results = [
        analyze_synergistic_seed(
            int(seed),
            cfg,
            rows,
            model_directory=model_directory,
        )
        for seed in seeds
    ]
    endpoint_names = list(results[0]["endpoints"])
    endpoints = {
        name: bool(all(result["endpoints"][name] for result in results))
        for name in endpoint_names
    }
    payload: dict[str, Any] = {
        "schema": "rrct.v050.synergistic_ephemeral_workspace.holdout.v1",
        "version": V050_VERSION,
        "seeds": [int(seed) for seed in seeds],
        "config": asdict(cfg),
        "sequence_case_count_per_seed": int(len(rows)),
        "matched_mode_count": len(results[0]["modes"]),
        "seed_results": results,
        "aggregate": _aggregate_seed_results(results),
        "endpoints": endpoints,
        "all_endpoints_met": bool(all(endpoints.values())),
        "claim_boundary": (
            "The result establishes necessity of a persistent jointly writable "
            "state under the frozen synthetic architecture and resource rules. "
            "It does not prove that no possible communication protocol can "
            "emulate a workspace; recurrent message-state and external logs are "
            "explicitly classified as workspace-equivalent persistent memory."
        ),
    }
    payload["status"] = (
        "V050_FROZEN_ENDPOINTS_MET"
        if payload["all_endpoints_met"]
        else "V050_FROZEN_ENDPOINTS_NOT_MET"
    )
    payload["digest"] = _digest(payload)
    return payload


__all__ = [
    "AgentTrainingReceipt",
    "ComplementaryOperatorAgent",
    "EphemeralWorkspaceReceipt",
    "SynergisticWorkspaceConfig",
    "SynergyReceipt",
    "all_sequence_rows",
    "analyze_synergistic_seed",
    "apply_operator_numpy",
    "evaluate_endpoints",
    "run_synergistic_holdout",
    "state_dict_sha256",
    "synergy_receipt",
    "train_operator_agent",
    "true_final_states",
]
