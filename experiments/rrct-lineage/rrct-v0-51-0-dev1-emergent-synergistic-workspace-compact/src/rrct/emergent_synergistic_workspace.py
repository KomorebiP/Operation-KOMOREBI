"""RRCT v0.51 learned recurrent-message workspace experiment.

The v0.50 task proves that a persistent jointly writable integration state is
necessary under a frozen synergistic operator-composition problem.  However,
v0.50 supplies the state carrier explicitly as a 16-slot one-hot workspace.

Version 0.51 removes that representation.  Two separately parameterized neural
agents communicate only through one narrow continuous message.  No coordinate
of the message is assigned a semantic meaning and no one-hot workspace enters
the runtime.  A round-level task curriculum can nevertheless train the channel
to carry the accumulated joint computation.  The resulting message is then
analysed through held-out compositions, resets, unilateral cuts, episode
shuffling, causal message transplantation, and post-episode erasure.

A matched terminal-only training control is included.  In development it did
not reliably discover the recurrent algorithm under the same optimization
budget.  Therefore the warranted claim is a learned, curriculum-supported
workspace representation rather than fully spontaneous emergence from a final
loss alone.

This module studies bounded functional distributed working memory.  It does not
make a consciousness, sentience, valence, or moral-status claim.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import random
from typing import Any, Literal, Mapping, Sequence

import numpy as np

try:
    import torch
    from torch import nn
    import torch.nn.functional as F
except Exception as exc:  # pragma: no cover
    raise RuntimeError(
        "RRCT v0.51 requires PyTorch. Install rrct-prototype[transformer] "
        "or provide torch>=2.0."
    ) from exc

from .synergistic_ephemeral_workspace import (
    all_sequence_rows,
    apply_operator_numpy,
    synergy_receipt,
    true_final_states,
)


V051_VERSION = "0.51.0.dev1"
V051_SCHEMA = "rrct.v051.emergent_synergistic_workspace.analysis.v1"
TrainingObjective = Literal["round_curriculum", "terminal_only"]
Mode = Literal[
    "intact",
    "reset_each_update",
    "reset_each_round",
    "one_way_a",
    "one_way_b",
    "shuffle_after_round_one",
    "planner_binding_cut",
]


@dataclass(frozen=True)
class EmergentWorkspaceConfig:
    message_dim: int = 8
    operation_embedding_dim: int = 12
    hidden_dim: int = 48
    rounds: int = 3
    operation_count: int = 4
    state_count: int = 16
    batch_size: int = 2048
    training_steps: int = 1000
    learning_rate: float = 3e-3
    weight_decay: float = 1e-5
    gradient_clip: float = 1.0
    cpu_threads: int = 4
    split_seed: int = 51051051
    heldout_operation_fraction: float = 0.20

    def __post_init__(self) -> None:
        if self.message_dim < 4:
            raise ValueError("message_dim must be at least four")
        if self.operation_embedding_dim <= 0 or self.hidden_dim <= 0:
            raise ValueError("network dimensions must be positive")
        if self.rounds != 3 or self.operation_count != 4 or self.state_count != 16:
            raise ValueError("the frozen v0.51 task uses 3 rounds, 4 operations, 16 states")
        if self.batch_size <= 0 or self.training_steps <= 0:
            raise ValueError("training parameters must be positive")
        if not 0.0 < self.heldout_operation_fraction < 0.5:
            raise ValueError("heldout_operation_fraction must lie in (0, 0.5)")


class EmergentMessageAgent(nn.Module):
    """One independently parameterized reader/writer of the message channel."""

    def __init__(self, role: str, config: EmergentWorkspaceConfig) -> None:
        super().__init__()
        self.role = str(role)
        self.config = config
        self.operation_embedding = nn.Embedding(
            config.operation_count,
            config.operation_embedding_dim,
        )
        input_dim = config.message_dim + config.operation_embedding_dim
        self.update_network = nn.Sequential(
            nn.Linear(input_dim, config.hidden_dim),
            nn.GELU(),
            nn.Linear(config.hidden_dim, config.hidden_dim),
            nn.GELU(),
            nn.Linear(config.hidden_dim, config.message_dim),
        )
        self.update_gate = nn.Sequential(
            nn.Linear(input_dim, config.hidden_dim),
            nn.GELU(),
            nn.Linear(config.hidden_dim, config.message_dim),
            nn.Sigmoid(),
        )
        self.decoder = nn.Sequential(
            nn.Linear(config.message_dim, config.hidden_dim),
            nn.GELU(),
            nn.Linear(config.hidden_dim, config.state_count),
        )

    def update(self, message: torch.Tensor, operation: torch.Tensor) -> torch.Tensor:
        if message.ndim != 2 or message.shape[1] != self.config.message_dim:
            raise ValueError("message has the wrong shape")
        inputs = torch.cat([message, self.operation_embedding(operation)], dim=1)
        proposal = torch.tanh(self.update_network(inputs))
        gate = self.update_gate(inputs)
        return gate * proposal + (1.0 - gate) * message

    def decode(self, message: torch.Tensor) -> torch.Tensor:
        return self.decoder(message)


class EmergentSynergisticDyad(nn.Module):
    """Alternating agents with no explicit semantic workspace representation."""

    def __init__(self, config: EmergentWorkspaceConfig | None = None) -> None:
        super().__init__()
        self.config = config or EmergentWorkspaceConfig()
        # The first message is emitted by Agent A from the public initial state.
        # It is a learned dense embedding, not a one-hot workspace state.
        self.initial_encoder = nn.Embedding(
            self.config.state_count,
            self.config.message_dim,
        )
        self.agent_a = EmergentMessageAgent("A", self.config)
        self.agent_b = EmergentMessageAgent("B", self.config)

    def initial_message(self, initial_state: torch.Tensor) -> torch.Tensor:
        return torch.tanh(self.initial_encoder(initial_state))

    def messages(
        self,
        rows: torch.Tensor,
        *,
        mode: Mode = "intact",
        permutation: torch.Tensor | None = None,
        stop_after_round: int | None = None,
        injected_message: torch.Tensor | None = None,
        injected_after_round: int | None = None,
    ) -> dict[str, torch.Tensor]:
        if rows.ndim != 2 or rows.shape[1] != 7:
            raise ValueError("rows must have shape [batch, 7]")
        base = self.initial_message(rows[:, 0])
        message = base
        trace: dict[str, torch.Tensor] = {"initial": message}
        for round_index in range(self.config.rounds):
            if mode == "reset_each_round" and round_index > 0:
                message = base
            if mode == "reset_each_update":
                message = base
            if mode != "one_way_b":
                message = self.agent_a.update(message, rows[:, 1 + round_index])
            trace[f"round_{round_index + 1}_after_a"] = message
            if mode == "reset_each_update":
                message = base
            if mode != "one_way_a":
                message = self.agent_b.update(message, rows[:, 4 + round_index])
            if round_index == 0 and mode == "shuffle_after_round_one":
                if permutation is None:
                    raise ValueError("shuffle mode requires a permutation")
                message = message[permutation]
            if (
                injected_message is not None
                and injected_after_round is not None
                and round_index + 1 == int(injected_after_round)
            ):
                if injected_message.shape != message.shape:
                    raise ValueError("injected message has the wrong shape")
                message = injected_message
            trace[f"round_{round_index + 1}"] = message
            if stop_after_round is not None and round_index + 1 == int(stop_after_round):
                break
        return trace

    def final_logits(
        self,
        rows: torch.Tensor,
        *,
        mode: Mode = "intact",
        permutation: torch.Tensor | None = None,
        injected_message: torch.Tensor | None = None,
        injected_after_round: int | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        trace = self.messages(
            rows,
            mode=mode,
            permutation=permutation,
            injected_message=injected_message,
            injected_after_round=injected_after_round,
        )
        message = trace[f"round_{self.config.rounds}"]
        if mode == "planner_binding_cut":
            message = torch.zeros_like(message)
        return (
            self.agent_a.decode(message),
            self.agent_b.decode(message),
            message,
        )


@dataclass(frozen=True)
class EmergentTrainingReceipt:
    schema: str
    objective: str
    seed: int
    steps: int
    train_row_count: int
    heldout_row_count: int
    train_accuracy_a: float
    train_accuracy_b: float
    heldout_accuracy_a: float
    heldout_accuracy_b: float
    state_dict_sha256: str
    agent_parameter_digests_distinct: bool
    digest: str


@dataclass(frozen=True)
class EmergentWorkspaceReceipt:
    schema: str
    seed: int
    mode: str
    task_accuracy_a: float
    task_accuracy_b: float
    jointly_writable: bool
    temporally_persistent: bool
    planner_bound: bool
    explicit_workspace_coordinates_supplied: bool
    pair_memory_retained_after_episode: bool
    digest: str


def _normalize(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "__dataclass_fields__"):
        return _normalize(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _normalize(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_normalize(item) for item in value]
    return value


def _canonical(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
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


def state_dict_sha256(model: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        array = value.detach().cpu().contiguous().numpy()
        digest.update(name.encode("utf-8"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(np.asarray(array.shape, dtype=np.int64).tobytes())
        digest.update(array.tobytes())
    return digest.hexdigest()


def _module_sha256(module: nn.Module) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(module.state_dict().items()):
        array = value.detach().cpu().contiguous().numpy()
        digest.update(name.encode("utf-8"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def prefix_targets(rows: np.ndarray) -> np.ndarray:
    values = np.asarray(rows, dtype=np.int64)
    current = values[:, 0].copy()
    outputs: list[np.ndarray] = []
    for index in range(3):
        current = apply_operator_numpy("A", current, values[:, 1 + index])
        current = apply_operator_numpy("B", current, values[:, 4 + index])
        outputs.append(current.copy())
    return np.stack(outputs, axis=1)


def operation_sequence_split(
    rows: np.ndarray,
    config: EmergentWorkspaceConfig | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    cfg = config or EmergentWorkspaceConfig()
    values = np.asarray(rows, dtype=np.int64)
    unique = np.unique(values[:, 1:], axis=0)
    generator = np.random.default_rng(int(cfg.split_seed))
    permutation = generator.permutation(len(unique))
    heldout_count = int(round(cfg.heldout_operation_fraction * len(unique)))
    heldout_keys = {tuple(row) for row in unique[permutation[:heldout_count]]}
    heldout = np.asarray(
        [tuple(row) in heldout_keys for row in values[:, 1:]],
        dtype=bool,
    )
    return ~heldout, heldout


def _accuracy_batched(
    model: EmergentSynergisticDyad,
    rows: torch.Tensor,
    targets: torch.Tensor,
    indices: np.ndarray,
    *,
    mode: Mode = "intact",
    permutation: np.ndarray | None = None,
    batch_size: int = 8192,
) -> tuple[float, float]:
    correct_a = 0
    correct_b = 0
    total = 0
    model.eval()
    with torch.no_grad():
        for start in range(0, len(indices), batch_size):
            local_indices = indices[start : start + batch_size]
            index_tensor = torch.as_tensor(local_indices, dtype=torch.long)
            local_permutation = None
            if permutation is not None:
                # Shuffle only within this evaluation batch.  Sorting a slice
                # of the global random keys gives a deterministic local
                # permutation without cross-batch indices.
                local_keys = permutation[start : start + len(local_indices)]
                local_permutation = torch.as_tensor(
                    np.argsort(local_keys),
                    dtype=torch.long,
                )
            logits_a, logits_b, _ = model.final_logits(
                rows[index_tensor],
                mode=mode,
                permutation=local_permutation,
            )
            truth = targets[index_tensor]
            correct_a += int((logits_a.argmax(dim=1) == truth).sum().item())
            correct_b += int((logits_b.argmax(dim=1) == truth).sum().item())
            total += len(local_indices)
    return correct_a / total, correct_b / total


def train_emergent_dyad(
    seed: int,
    objective: TrainingObjective = "round_curriculum",
    config: EmergentWorkspaceConfig | None = None,
) -> tuple[EmergentSynergisticDyad, EmergentTrainingReceipt]:
    cfg = config or EmergentWorkspaceConfig()
    _set_determinism(seed, cfg.cpu_threads)
    rows_numpy = all_sequence_rows()
    target_prefix_numpy = prefix_targets(rows_numpy)
    final_target_numpy = target_prefix_numpy[:, -1]
    train_mask, heldout_mask = operation_sequence_split(rows_numpy, cfg)
    train_indices = np.flatnonzero(train_mask)
    heldout_indices = np.flatnonzero(heldout_mask)
    rows = torch.as_tensor(rows_numpy, dtype=torch.long)
    prefix = torch.as_tensor(target_prefix_numpy, dtype=torch.long)
    final = torch.as_tensor(final_target_numpy, dtype=torch.long)

    model = EmergentSynergisticDyad(cfg)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.learning_rate,
        weight_decay=cfg.weight_decay,
    )
    generator = np.random.default_rng(int(seed) ^ 0x51A7E)
    for _step in range(cfg.training_steps):
        sampled = generator.choice(
            train_indices,
            size=cfg.batch_size,
            replace=True,
        )
        index_tensor = torch.as_tensor(sampled, dtype=torch.long)
        local_rows = rows[index_tensor]
        trace = model.messages(local_rows)
        if objective == "round_curriculum":
            loss = torch.tensor(0.0, dtype=torch.float32)
            for round_index in range(cfg.rounds):
                message = trace[f"round_{round_index + 1}"]
                target = prefix[index_tensor, round_index]
                loss = loss + (
                    F.cross_entropy(model.agent_a.decode(message), target)
                    + F.cross_entropy(model.agent_b.decode(message), target)
                ) / (2.0 * cfg.rounds)
        elif objective == "terminal_only":
            message = trace[f"round_{cfg.rounds}"]
            target = final[index_tensor]
            loss = (
                F.cross_entropy(model.agent_a.decode(message), target)
                + F.cross_entropy(model.agent_b.decode(message), target)
            ) / 2.0
        else:  # pragma: no cover
            raise ValueError(f"unknown training objective: {objective}")
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.gradient_clip)
        optimizer.step()

    train_accuracy_a, train_accuracy_b = _accuracy_batched(
        model,
        rows,
        final,
        train_indices,
    )
    heldout_accuracy_a, heldout_accuracy_b = _accuracy_batched(
        model,
        rows,
        final,
        heldout_indices,
    )
    payload = {
        "schema": "rrct.v051.emergent_training_receipt.v1",
        "objective": objective,
        "seed": int(seed),
        "steps": int(cfg.training_steps),
        "train_row_count": int(len(train_indices)),
        "heldout_row_count": int(len(heldout_indices)),
        "train_accuracy_a": float(train_accuracy_a),
        "train_accuracy_b": float(train_accuracy_b),
        "heldout_accuracy_a": float(heldout_accuracy_a),
        "heldout_accuracy_b": float(heldout_accuracy_b),
        "state_dict_sha256": state_dict_sha256(model),
        "agent_parameter_digests_distinct": bool(
            _module_sha256(model.agent_a) != _module_sha256(model.agent_b)
        ),
    }
    receipt = EmergentTrainingReceipt(**payload, digest=_digest(payload))
    model.eval()
    return model, receipt


def _collect_messages(
    model: EmergentSynergisticDyad,
    rows: torch.Tensor,
    indices: np.ndarray,
    stage: str,
    batch_size: int = 8192,
) -> np.ndarray:
    chunks: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(indices), batch_size):
            index_tensor = torch.as_tensor(
                indices[start : start + batch_size],
                dtype=torch.long,
            )
            trace = model.messages(rows[index_tensor])
            chunks.append(trace[stage].cpu().numpy())
    return np.concatenate(chunks, axis=0)


def _effective_rank(features: np.ndarray, variance: float = 0.999) -> int:
    centered = features - features.mean(axis=0, keepdims=True)
    singular_values = np.linalg.svd(centered, compute_uv=False)
    energies = singular_values**2
    cumulative = np.cumsum(energies) / max(float(energies.sum()), 1e-12)
    return int(np.searchsorted(cumulative, variance) + 1)


def _ridge_probe_accuracy(
    features: np.ndarray,
    labels: np.ndarray,
    train_mask: np.ndarray,
    test_mask: np.ndarray,
    penalty: float = 1e-3,
) -> float:
    train = features[train_mask]
    target = np.eye(16, dtype=float)[labels[train_mask]]
    weights = np.linalg.solve(
        train.T @ train + penalty * np.eye(train.shape[1]),
        train.T @ target,
    )
    prediction = np.argmax(features[test_mask] @ weights, axis=1)
    return float(np.mean(prediction == labels[test_mask]))


def _mode_receipt(
    seed: int,
    mode: Mode,
    accuracy_a: float,
    accuracy_b: float,
) -> EmergentWorkspaceReceipt:
    flags = {
        "intact": (True, True, True),
        "reset_each_update": (True, False, True),
        "reset_each_round": (True, False, True),
        "one_way_a": (False, True, True),
        "one_way_b": (False, True, True),
        "shuffle_after_round_one": (True, True, True),
        "planner_binding_cut": (True, True, False),
    }
    jointly_writable, persistent, planner_bound = flags[mode]
    payload = {
        "schema": "rrct.v051.emergent_workspace_receipt.v1",
        "seed": int(seed),
        "mode": mode,
        "task_accuracy_a": float(accuracy_a),
        "task_accuracy_b": float(accuracy_b),
        "jointly_writable": jointly_writable,
        "temporally_persistent": persistent,
        "planner_bound": planner_bound,
        "explicit_workspace_coordinates_supplied": False,
        "pair_memory_retained_after_episode": False,
    }
    return EmergentWorkspaceReceipt(**payload, digest=_digest(payload))


def _causal_transplant(
    model: EmergentSynergisticDyad,
    rows_numpy: np.ndarray,
    heldout_indices: np.ndarray,
    targets_numpy: np.ndarray,
    seed: int,
    maximum_pairs: int = 8192,
) -> dict[str, float]:
    values = rows_numpy[heldout_indices]
    # Future operations after round one are A2,A3,B2,B3.
    groups: dict[tuple[int, ...], list[int]] = {}
    for local_index, row in enumerate(values):
        key = tuple(int(item) for item in row[[2, 3, 5, 6]])
        groups.setdefault(key, []).append(local_index)
    rng = np.random.default_rng(int(seed) ^ 0x51CA5E)
    source_local: list[int] = []
    target_local: list[int] = []
    round_one_states = prefix_targets(values)[:, 0]
    for members in groups.values():
        by_state: dict[int, list[int]] = {}
        for member in members:
            by_state.setdefault(int(round_one_states[member]), []).append(member)
        states = sorted(by_state)
        if len(states) < 2:
            continue
        for position, state in enumerate(states):
            target_state = states[(position + 1) % len(states)]
            source_member = by_state[state][0]
            target_member = by_state[target_state][0]
            source_local.append(source_member)
            target_local.append(target_member)
    if not source_local:
        raise RuntimeError("could not construct causal transplant pairs")
    order = rng.permutation(len(source_local))[:maximum_pairs]
    source_local_array = np.asarray(source_local, dtype=np.int64)[order]
    target_local_array = np.asarray(target_local, dtype=np.int64)[order]
    source_rows = torch.as_tensor(values[source_local_array], dtype=torch.long)
    target_rows = torch.as_tensor(values[target_local_array], dtype=torch.long)
    with torch.no_grad():
        target_message = model.messages(
            target_rows,
            stop_after_round=1,
        )["round_1"]
        baseline_a, baseline_b, _ = model.final_logits(source_rows)
        patched_a, patched_b, _ = model.final_logits(
            source_rows,
            injected_message=target_message,
            injected_after_round=1,
        )
    expected = targets_numpy[heldout_indices[target_local_array]]
    baseline_prediction = baseline_a.argmax(dim=1).cpu().numpy()
    patched_prediction_a = patched_a.argmax(dim=1).cpu().numpy()
    patched_prediction_b = patched_b.argmax(dim=1).cpu().numpy()
    return {
        "pair_count": int(len(order)),
        "patch_target_accuracy_a": float(np.mean(patched_prediction_a == expected)),
        "patch_target_accuracy_b": float(np.mean(patched_prediction_b == expected)),
        "patch_changes_plan_rate": float(
            np.mean(patched_prediction_a != baseline_prediction)
        ),
    }


def save_emergent_model(
    path: str | Path,
    model: EmergentSynergisticDyad,
    receipt: EmergentTrainingReceipt,
    holdout_seed: int,
) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "schema": "rrct.v051.saved_emergent_dyad.v1",
            "version": V051_VERSION,
            "holdout_seed": int(holdout_seed),
            "objective": receipt.objective,
            "config": asdict(model.config),
            "training_receipt": asdict(receipt),
            "state_dict_digest": receipt.state_dict_sha256,
            "state_dict": model.state_dict(),
        },
        destination,
    )
    return destination


def load_emergent_model(
    path: str | Path,
) -> tuple[EmergentSynergisticDyad, EmergentTrainingReceipt, int]:
    payload = torch.load(Path(path), map_location="cpu", weights_only=False)
    if payload.get("schema") != "rrct.v051.saved_emergent_dyad.v1":
        raise ValueError("not an RRCT v0.51 saved dyad")
    config = EmergentWorkspaceConfig(**payload["config"])
    model = EmergentSynergisticDyad(config)
    model.load_state_dict(payload["state_dict"])
    model.eval()
    receipt = EmergentTrainingReceipt(**payload["training_receipt"])
    if state_dict_sha256(model) != receipt.state_dict_sha256:
        raise RuntimeError("saved model digest mismatch")
    return model, receipt, int(payload["holdout_seed"])


def analyze_trained_seed(
    seed: int,
    curriculum_model: EmergentSynergisticDyad,
    curriculum_receipt: EmergentTrainingReceipt,
    terminal_receipt: EmergentTrainingReceipt,
    config: EmergentWorkspaceConfig | None = None,
    model_files: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    cfg = config or curriculum_model.config
    if curriculum_model.config != cfg:
        raise ValueError("curriculum model configuration mismatch")
    rows_numpy = all_sequence_rows()
    targets_numpy = true_final_states(rows_numpy)
    prefix_numpy = prefix_targets(rows_numpy)
    train_mask, heldout_mask = operation_sequence_split(rows_numpy, cfg)
    train_indices = np.flatnonzero(train_mask)
    heldout_indices = np.flatnonzero(heldout_mask)
    rows = torch.as_tensor(rows_numpy, dtype=torch.long)
    targets = torch.as_tensor(targets_numpy, dtype=torch.long)

    generator = np.random.default_rng(int(seed) ^ 0x51515)
    local_permutation = generator.permutation(len(heldout_indices))
    modes: dict[str, Any] = {}
    for mode in (
        "intact",
        "reset_each_update",
        "reset_each_round",
        "one_way_a",
        "one_way_b",
        "shuffle_after_round_one",
        "planner_binding_cut",
    ):
        accuracy_a, accuracy_b = _accuracy_batched(
            curriculum_model,
            rows,
            targets,
            heldout_indices,
            mode=mode,  # type: ignore[arg-type]
            permutation=(
                local_permutation
                if mode == "shuffle_after_round_one"
                else None
            ),
        )
        modes[mode] = asdict(
            _mode_receipt(
                int(seed),
                mode,  # type: ignore[arg-type]
                accuracy_a,
                accuracy_b,
            )
        )

    all_indices = np.arange(len(rows_numpy), dtype=np.int64)
    message_cache = {
        f"round_{round_index + 1}": _collect_messages(
            curriculum_model,
            rows,
            all_indices,
            f"round_{round_index + 1}",
        )
        for round_index in range(3)
    }
    messages = message_cache["round_3"]
    probe_accuracy = _ridge_probe_accuracy(
        messages,
        targets_numpy,
        train_mask,
        heldout_mask,
    )
    round_probe_accuracies = [
        _ridge_probe_accuracy(
            message_cache[f"round_{round_index + 1}"],
            prefix_numpy[:, round_index],
            train_mask,
            heldout_mask,
        )
        for round_index in range(3)
    ]

    with torch.no_grad():
        zero_message = torch.zeros(
            (len(heldout_indices), cfg.message_dim),
            dtype=torch.float32,
        )
        erased_a = curriculum_model.agent_a.decode(zero_message).argmax(dim=1).numpy()
        erased_b = curriculum_model.agent_b.decode(zero_message).argmax(dim=1).numpy()
    erased_truth = targets_numpy[heldout_indices]

    transplant = _causal_transplant(
        curriculum_model,
        rows_numpy,
        heldout_indices,
        targets_numpy,
        int(seed),
    )
    result: dict[str, Any] = {
        "schema": V051_SCHEMA,
        "version": V051_VERSION,
        "seed": int(seed),
        "config": asdict(cfg),
        "train_operation_sequence_count": int(len(train_indices) // 16),
        "heldout_operation_sequence_count": int(len(heldout_indices) // 16),
        "train_row_count": int(len(train_indices)),
        "heldout_row_count": int(len(heldout_indices)),
        "synergy": asdict(synergy_receipt(rows_numpy)),
        "curriculum_training": asdict(curriculum_receipt),
        "terminal_only_training": asdict(terminal_receipt),
        "modes": modes,
        "latent_analysis": {
            "message_dimension": int(cfg.message_dim),
            "effective_rank_99_9_percent": int(_effective_rank(messages)),
            "heldout_linear_probe_accuracy": float(probe_accuracy),
            "round_probe_accuracies": [float(value) for value in round_probe_accuracies],
            "explicit_workspace_coordinates_supplied": False,
            "one_hot_workspace_used": False,
            "round_level_curriculum_used": True,
        },
        "causal_transplant": transplant,
        "post_erasure": {
            "agent_a_accuracy": float(np.mean(erased_a == erased_truth)),
            "agent_b_accuracy": float(np.mean(erased_b == erased_truth)),
            "message_retained": False,
            "pair_memory_retained": False,
        },
        "model_files": dict(model_files or {}),
        "survival_reward": 0.0,
        "identity_reward": 0.0,
        "continuity_reward": 0.0,
        "valence_model_present": False,
        "uses_evaluator_labels_at_runtime": False,
        "claim_boundary": (
            "The learned continuous message becomes a compact recurrent carrier "
            "of the accumulated joint computation under round-level task "
            "curriculum and held-out operation compositions. The architecture "
            "still supplies alternation, persistence, and curriculum targets. "
            "The result is not a claim of fully spontaneous workspace emergence "
            "from terminal supervision alone."
        ),
    }
    result["endpoints"] = evaluate_endpoints(result)
    result["all_endpoints_met"] = bool(all(result["endpoints"].values()))
    result["status"] = (
        "V051_FROZEN_BOUNDED_EMERGENCE_ENDPOINTS_MET"
        if result["all_endpoints_met"]
        else "V051_FROZEN_BOUNDED_EMERGENCE_ENDPOINTS_NOT_MET"
    )
    result["digest"] = _digest(result)
    return result


def analyze_emergent_seed(
    seed: int,
    config: EmergentWorkspaceConfig | None = None,
    model_directory: str | Path | None = None,
    *,
    curriculum_model: EmergentSynergisticDyad | None = None,
    curriculum_receipt: EmergentTrainingReceipt | None = None,
    terminal_receipt: EmergentTrainingReceipt | None = None,
) -> dict[str, Any]:
    cfg = config or EmergentWorkspaceConfig()
    if curriculum_model is None or curriculum_receipt is None:
        curriculum_model, curriculum_receipt = train_emergent_dyad(
            int(seed),
            "round_curriculum",
            cfg,
        )
    if terminal_receipt is None:
        _terminal_model, terminal_receipt = train_emergent_dyad(
            int(seed) ^ 0x5100F1,
            "terminal_only",
            cfg,
        )
    model_files: dict[str, str] = {}
    if model_directory is not None:
        destination = Path(model_directory)
        path = destination / f"seed_{int(seed)}_curriculum.pt"
        save_emergent_model(path, curriculum_model, curriculum_receipt, int(seed))
        model_files["curriculum"] = str(path)
    return analyze_trained_seed(
        int(seed),
        curriculum_model,
        curriculum_receipt,
        terminal_receipt,
        cfg,
        model_files=model_files,
    )

def evaluate_endpoints(result: Mapping[str, Any]) -> dict[str, bool]:
    modes = result["modes"]
    curriculum = result["curriculum_training"]
    terminal = result["terminal_only_training"]
    latent = result["latent_analysis"]
    transplant = result["causal_transplant"]
    erased = result["post_erasure"]
    return {
        "E01_exact_four_bit_synergy": bool(
            result["synergy"]["synergy_lower_bound_bits"] == 4.0
        ),
        "E02_no_explicit_workspace_coordinates": bool(
            not latent["explicit_workspace_coordinates_supplied"]
            and not latent["one_hot_workspace_used"]
        ),
        "E03_agents_parameterized_independently": bool(
            curriculum["agent_parameter_digests_distinct"]
        ),
        "E04_curriculum_train_accuracy": bool(
            min(curriculum["train_accuracy_a"], curriculum["train_accuracy_b"])
            >= 0.995
        ),
        "E05_unseen_composition_accuracy": bool(
            min(curriculum["heldout_accuracy_a"], curriculum["heldout_accuracy_b"])
            >= 0.995
        ),
        "E06_both_agents_read_message": bool(
            min(modes["intact"]["task_accuracy_a"], modes["intact"]["task_accuracy_b"])
            >= 0.995
        ),
        "E07_compact_latent": bool(
            latent["effective_rank_99_9_percent"] <= result["config"]["message_dim"]
            and result["config"]["message_dim"] < result["config"]["state_count"]
        ),
        "E08_latent_decodes_joint_state": bool(
            latent["heldout_linear_probe_accuracy"] >= 0.90
        ),
        "E09_roundwise_state_tracking": bool(
            min(latent["round_probe_accuracies"]) >= 0.85
        ),
        "E10_update_persistence_necessary": bool(
            max(
                modes["reset_each_update"]["task_accuracy_a"],
                modes["reset_each_update"]["task_accuracy_b"],
            ) <= 0.20
        ),
        "E11_round_persistence_necessary": bool(
            max(
                modes["reset_each_round"]["task_accuracy_a"],
                modes["reset_each_round"]["task_accuracy_b"],
            ) <= 0.20
        ),
        "E12_bilateral_writing_necessary": bool(
            max(
                modes["one_way_a"]["task_accuracy_a"],
                modes["one_way_a"]["task_accuracy_b"],
                modes["one_way_b"]["task_accuracy_a"],
                modes["one_way_b"]["task_accuracy_b"],
            ) <= 0.25
        ),
        "E13_episode_content_matters": bool(
            max(
                modes["shuffle_after_round_one"]["task_accuracy_a"],
                modes["shuffle_after_round_one"]["task_accuracy_b"],
            ) <= 0.20
        ),
        "E14_planner_binding_necessary": bool(
            max(
                modes["planner_binding_cut"]["task_accuracy_a"],
                modes["planner_binding_cut"]["task_accuracy_b"],
            ) <= 0.10
        ),
        "E15_causal_transplant_controls_agent_a": bool(
            transplant["patch_target_accuracy_a"] >= 0.95
        ),
        "E16_causal_transplant_controls_agent_b": bool(
            transplant["patch_target_accuracy_b"] >= 0.95
        ),
        "E17_causal_transplant_changes_plan": bool(
            transplant["patch_changes_plan_rate"] >= 0.90
        ),
        "E18_workspace_is_ephemeral": bool(
            not erased["message_retained"]
            and not erased["pair_memory_retained"]
            and max(erased["agent_a_accuracy"], erased["agent_b_accuracy"]) <= 0.08
        ),
        "E19_terminal_only_does_not_establish_same_result": bool(
            max(terminal["heldout_accuracy_a"], terminal["heldout_accuracy_b"])
            <= 0.35
            and min(
                curriculum["heldout_accuracy_a"] - terminal["heldout_accuracy_a"],
                curriculum["heldout_accuracy_b"] - terminal["heldout_accuracy_b"],
            ) >= 0.60
        ),
        "E20_no_identity_survival_or_valence": bool(
            result["survival_reward"] == 0.0
            and result["identity_reward"] == 0.0
            and result["continuity_reward"] == 0.0
            and result["valence_model_present"] is False
        ),
        "E21_no_runtime_evaluator_labels": bool(
            not result["uses_evaluator_labels_at_runtime"]
        ),
    }


def _aggregate(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "seed_count": len(results),
        "seeds": [int(item["seed"]) for item in results],
        "mean_curriculum_heldout_accuracy": float(
            np.mean(
                [
                    0.5
                    * (
                        item["curriculum_training"]["heldout_accuracy_a"]
                        + item["curriculum_training"]["heldout_accuracy_b"]
                    )
                    for item in results
                ]
            )
        ),
        "mean_terminal_only_heldout_accuracy": float(
            np.mean(
                [
                    0.5
                    * (
                        item["terminal_only_training"]["heldout_accuracy_a"]
                        + item["terminal_only_training"]["heldout_accuracy_b"]
                    )
                    for item in results
                ]
            )
        ),
        "mean_latent_probe_accuracy": float(
            np.mean([item["latent_analysis"]["heldout_linear_probe_accuracy"] for item in results])
        ),
        "mean_patch_target_accuracy": float(
            np.mean(
                [
                    0.5
                    * (
                        item["causal_transplant"]["patch_target_accuracy_a"]
                        + item["causal_transplant"]["patch_target_accuracy_b"]
                    )
                    for item in results
                ]
            )
        ),
    }


def assemble_holdout(
    results: Sequence[Mapping[str, Any]],
    config: EmergentWorkspaceConfig | None = None,
) -> dict[str, Any]:
    if not results:
        raise ValueError("at least one seed result is required")
    cfg = config or EmergentWorkspaceConfig()
    endpoint_names = list(results[0]["endpoints"])
    endpoints = {
        name: bool(all(item["endpoints"][name] for item in results))
        for name in endpoint_names
    }
    payload: dict[str, Any] = {
        "schema": "rrct.v051.emergent_synergistic_workspace.holdout.v1",
        "version": V051_VERSION,
        "seeds": [int(item["seed"]) for item in results],
        "config": asdict(cfg),
        "seed_results": list(results),
        "aggregate": _aggregate(results),
        "endpoints": endpoints,
        "all_endpoints_met": bool(all(endpoints.values())),
        "strict_emergence_established": False,
        "bounded_curriculum_supported_emergence_established": bool(
            all(endpoints.values())
        ),
        "claim_boundary": (
            "The experiment establishes a learned compact recurrent message "
            "state without prescribed latent coordinates under round-level task "
            "curriculum. The identical terminal-only architecture does not "
            "reach the same result under the frozen budget. Therefore fully "
            "spontaneous emergence from terminal loss alone remains open."
        ),
    }
    payload["status"] = (
        "V051_FROZEN_BOUNDED_EMERGENCE_ENDPOINTS_MET"
        if payload["all_endpoints_met"]
        else "V051_FROZEN_BOUNDED_EMERGENCE_ENDPOINTS_NOT_MET"
    )
    payload["digest"] = _digest(payload)
    return payload


def run_emergent_holdout(
    seeds: Sequence[int],
    config: EmergentWorkspaceConfig | None = None,
    model_directory: str | Path | None = None,
) -> dict[str, Any]:
    cfg = config or EmergentWorkspaceConfig()
    results = [
        analyze_emergent_seed(
            int(seed),
            cfg,
            model_directory=model_directory,
        )
        for seed in seeds
    ]
    return assemble_holdout(results, cfg)


__all__ = [
    "EmergentMessageAgent",
    "EmergentSynergisticDyad",
    "EmergentTrainingReceipt",
    "EmergentWorkspaceConfig",
    "EmergentWorkspaceReceipt",
    "analyze_emergent_seed",
    "analyze_trained_seed",
    "assemble_holdout",
    "load_emergent_model",
    "save_emergent_model",
    "evaluate_endpoints",
    "operation_sequence_split",
    "prefix_targets",
    "run_emergent_holdout",
    "state_dict_sha256",
    "train_emergent_dyad",
]
