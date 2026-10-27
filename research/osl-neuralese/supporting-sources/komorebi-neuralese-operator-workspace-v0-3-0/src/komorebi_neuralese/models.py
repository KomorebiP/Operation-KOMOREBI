from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import torch
from torch import nn
from torch.nn import functional as F

from .algebra import N_OPERATORS, N_STATES


@dataclass
class RunTrace:
    logits: torch.Tensor
    hidden: list[torch.Tensor]
    operator_codes: torch.Tensor | None


class RecurrentOperatorModel(nn.Module, ABC):
    model_name: str

    @abstractmethod
    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    def run(self, tables: torch.Tensor, op_slots: torch.Tensor, start: torch.Tensor) -> RunTrace:
        codes = self.encode_operators(tables)
        hidden = self.initial_hidden(start)
        trajectory = [hidden]
        rows = torch.arange(start.shape[0], device=start.device)
        for t in range(op_slots.shape[1]):
            selected = codes[rows, op_slots[:, t]]
            hidden = self.step_hidden(hidden, selected)
            trajectory.append(hidden)
        return RunTrace(self.decode_hidden(hidden), trajectory, codes)

    def continue_from_hidden(
        self,
        hidden: torch.Tensor,
        operator_codes: torch.Tensor,
        op_slots: torch.Tensor,
    ) -> RunTrace:
        trajectory = [hidden]
        rows = torch.arange(hidden.shape[0], device=hidden.device)
        for t in range(op_slots.shape[1]):
            selected = operator_codes[rows, op_slots[:, t]]
            hidden = self.step_hidden(hidden, selected)
            trajectory.append(hidden)
        return RunTrace(self.decode_hidden(hidden), trajectory, operator_codes)

    def forward(self, tables: torch.Tensor, op_slots: torch.Tensor, start: torch.Tensor) -> torch.Tensor:
        return self.run(tables, op_slots, start).logits


def whiten_hidden(
    hidden: torch.Tensor,
    whitener: torch.Tensor,
    inverse_whitener: torch.Tensor | None = None,
) -> torch.Tensor:
    """Map row-batched hidden vectors to coordinates with Euclidean metric."""
    del inverse_whitener
    return F.linear(hidden, whitener)


def unwhiten_hidden(
    hidden: torch.Tensor,
    whitener: torch.Tensor,
    inverse_whitener: torch.Tensor,
) -> torch.Tensor:
    """Undo :func:`whiten_hidden`."""
    del whitener
    return F.linear(hidden, inverse_whitener)


def whiten_operators(
    operator_codes: torch.Tensor,
    whitener: torch.Tensor,
    inverse_whitener: torch.Tensor,
) -> torch.Tensor:
    """Conjugate latent operators into whitened coordinates."""
    return torch.matmul(torch.matmul(whitener, operator_codes), inverse_whitener)


def unwhiten_operators(
    operator_codes: torch.Tensor,
    whitener: torch.Tensor,
    inverse_whitener: torch.Tensor,
) -> torch.Tensor:
    """Undo :func:`whiten_operators`."""
    return torch.matmul(torch.matmul(inverse_whitener, operator_codes), whitener)


class LearnedSPDMetric(nn.Module):
    """A bounded, scale-fixed, learned positive-definite latent metric.

    The unconstrained parameter is symmetrized and made trace-free in log
    coordinates.  Its Frobenius norm is then smoothly bounded before matrix
    exponentiation.  Thus ``G`` is SPD, ``log(det(G)) = 0``, and neither global
    scale collapse nor an unbounded condition number can minimize the loss.
    """

    def __init__(self, dimension: int, log_frobenius_bound: float = 2.0):
        super().__init__()
        if dimension < 1:
            raise ValueError("dimension must be positive")
        if log_frobenius_bound <= 0.0:
            raise ValueError("log_frobenius_bound must be positive")
        self.dimension = int(dimension)
        self.log_frobenius_bound = float(log_frobenius_bound)
        self.raw_log_metric = nn.Parameter(torch.zeros(self.dimension, self.dimension))

    def log_matrix(self) -> torch.Tensor:
        """Return the bounded symmetric trace-free matrix ``log(G)``."""
        symmetric = 0.5 * (self.raw_log_metric + self.raw_log_metric.transpose(-1, -2))
        identity = torch.eye(self.dimension, dtype=symmetric.dtype, device=symmetric.device)
        trace_free = symmetric - symmetric.trace() * identity / self.dimension
        norm = torch.linalg.matrix_norm(trace_free, ord="fro")
        ratio = norm / self.log_frobenius_bound
        # tanh(r) / r has limit one at zero.  The explicit near-zero branch
        # keeps initialization finite and preserves the identity derivative.
        denominator = ratio.clamp_min(torch.finfo(trace_free.dtype).eps)
        regular_scale = torch.tanh(ratio) / denominator
        taylor_scale = 1.0 - ratio.square() / 3.0
        scale = torch.where(ratio > 1e-6, regular_scale, taylor_scale)
        return trace_free * scale

    def bounded_log_metric(self) -> torch.Tensor:
        return self.log_matrix()

    def matrix(self) -> torch.Tensor:
        """Return the learned SPD metric ``G``."""
        return torch.matrix_exp(self.log_matrix())

    def metric_matrix(self) -> torch.Tensor:
        return self.matrix()

    def forward(self) -> torch.Tensor:
        return self.matrix()

    def factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        """Return symmetric ``(W, W^-1)`` with ``G = W.T @ W``."""
        log_metric = self.log_matrix()
        return torch.matrix_exp(0.5 * log_metric), torch.matrix_exp(-0.5 * log_metric)

    def whitener(self) -> torch.Tensor:
        return self.factors()[0]

    def inverse_whitener(self) -> torch.Tensor:
        return self.factors()[1]

    def condition_number(self) -> torch.Tensor:
        eigenvalues = torch.linalg.eigvalsh(self.log_matrix())
        return torch.exp(eigenvalues[-1] - eigenvalues[0])

    def whiten(self, hidden: torch.Tensor) -> torch.Tensor:
        return whiten_hidden(hidden, *self.factors())

    def unwhiten(self, hidden: torch.Tensor) -> torch.Tensor:
        return unwhiten_hidden(hidden, *self.factors())

    def whiten_operators(self, operator_codes: torch.Tensor) -> torch.Tensor:
        return whiten_operators(operator_codes, *self.factors())

    def unwhiten_operators(self, operator_codes: torch.Tensor) -> torch.Tensor:
        return unwhiten_operators(operator_codes, *self.factors())


class LinearHyperOperatorRNN(RecurrentOperatorModel):
    """A compact recurrent model whose dynamic operator is a learned latent matrix."""

    model_name = "linear_hyper"

    def __init__(self, hidden_dim: int = 8, operator_init_std: float = 0.01):
        super().__init__()
        self.hidden_dim = int(hidden_dim)
        if operator_init_std <= 0.0:
            raise ValueError("operator_init_std must be positive")
        self.operator_init_std = float(operator_init_std)
        self.state_embedding = nn.Embedding(N_STATES, self.hidden_dim)
        self.operator_encoder = nn.Linear(N_STATES * N_STATES, self.hidden_dim * self.hidden_dim, bias=False)
        self.decoder = nn.Linear(self.hidden_dim, N_STATES, bias=False)
        nn.init.normal_(self.state_embedding.weight, std=0.30)
        nn.init.normal_(self.operator_encoder.weight, std=self.operator_init_std)
        nn.init.normal_(self.decoder.weight, std=0.30)

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        batch, operators = tables.shape[:2]
        matrices = self.operator_encoder(tables.reshape(batch * operators, -1))
        return matrices.reshape(batch, operators, self.hidden_dim, self.hidden_dim)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.state_embedding(start)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)

    def metric_matrix(self) -> torch.Tensor:
        """Return the fixed Euclidean metric used by this control arm."""
        return torch.eye(
            self.hidden_dim,
            dtype=self.state_embedding.weight.dtype,
            device=self.state_embedding.weight.device,
        )

    def metric_factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        identity = self.metric_matrix()
        return identity, identity

    def whiten_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return whiten_hidden(hidden, *self.metric_factors())

    def unwhiten_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return unwhiten_hidden(hidden, *self.metric_factors())

    def whiten_operators(self, operator_codes: torch.Tensor) -> torch.Tensor:
        return whiten_operators(operator_codes, *self.metric_factors())

    def unwhiten_operators(self, operator_codes: torch.Tensor) -> torch.Tensor:
        return unwhiten_operators(operator_codes, *self.metric_factors())


class LinearHyperMetricOperatorRNN(LinearHyperOperatorRNN):
    """Linear hypernetwork recurrence with a learned intrinsic SPD metric."""

    model_name = "linear_hyper_metric"

    def __init__(
        self,
        hidden_dim: int = 8,
        log_metric_bound: float = 2.0,
        operator_init_std: float = 0.01,
    ):
        super().__init__(hidden_dim=hidden_dim, operator_init_std=operator_init_std)
        self.learned_metric = LearnedSPDMetric(hidden_dim, log_frobenius_bound=log_metric_bound)

    def metric_matrix(self) -> torch.Tensor:
        return self.learned_metric.matrix()

    def metric_factors(self) -> tuple[torch.Tensor, torch.Tensor]:
        return self.learned_metric.factors()


class GRUOperatorRNN(RecurrentOperatorModel):
    """Unconstrained recurrent comparison with a compressed operator code."""

    model_name = "gru"

    def __init__(self, hidden_dim: int = 32, operator_dim: int = 32):
        super().__init__()
        self.hidden_dim = int(hidden_dim)
        self.operator_dim = int(operator_dim)
        self.state_embedding = nn.Embedding(N_STATES, self.hidden_dim)
        self.operator_encoder = nn.Sequential(
            nn.Linear(N_STATES * N_STATES, 128),
            nn.GELU(),
            nn.Linear(128, self.operator_dim),
        )
        self.cell = nn.GRUCell(self.operator_dim, self.hidden_dim)
        self.decoder = nn.Linear(self.hidden_dim, N_STATES)

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        batch, operators = tables.shape[:2]
        codes = self.operator_encoder(tables.reshape(batch * operators, -1))
        return codes.reshape(batch, operators, self.operator_dim)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.state_embedding(start)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return self.cell(code, hidden)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)


class TokenOnlyRNN(RecurrentOperatorModel):
    """Negative control that cannot inspect episode-specific operator tables."""

    model_name = "token_only"

    def __init__(self, hidden_dim: int = 32, operator_dim: int = 16):
        super().__init__()
        self.hidden_dim = int(hidden_dim)
        self.operator_dim = int(operator_dim)
        self.state_embedding = nn.Embedding(N_STATES, self.hidden_dim)
        self.slot_embedding = nn.Embedding(N_OPERATORS, self.operator_dim)
        self.cell = nn.GRUCell(self.operator_dim, self.hidden_dim)
        self.decoder = nn.Linear(self.hidden_dim, N_STATES)

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        batch = tables.shape[0]
        slots = torch.arange(N_OPERATORS, device=tables.device)
        return self.slot_embedding(slots).unsqueeze(0).expand(batch, -1, -1)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.state_embedding(start)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return self.cell(code, hidden)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.decoder(hidden)


class OneShotMLP(nn.Module):
    """Nonrecurrent baseline with a fixed maximum sequence canvas."""

    model_name = "one_shot"

    def __init__(self, max_length: int = 12, width: int = 128):
        super().__init__()
        self.max_length = int(max_length)
        input_dim = N_STATES + N_OPERATORS * N_STATES * N_STATES + self.max_length * N_OPERATORS + self.max_length
        self.network = nn.Sequential(
            nn.Linear(input_dim, width),
            nn.GELU(),
            nn.Linear(width, width),
            nn.GELU(),
            nn.Linear(width, N_STATES),
        )

    def forward(self, tables: torch.Tensor, op_slots: torch.Tensor, start: torch.Tensor) -> torch.Tensor:
        batch, length = op_slots.shape
        if length > self.max_length:
            raise ValueError(f"sequence length {length} exceeds max_length {self.max_length}")
        sequence = torch.zeros(batch, self.max_length, N_OPERATORS, device=tables.device)
        if length:
            sequence[:, :length].scatter_(2, op_slots.unsqueeze(-1), 1.0)
        mask = torch.zeros(batch, self.max_length, device=tables.device)
        mask[:, :length] = 1.0
        features = torch.cat(
            (
                F.one_hot(start, num_classes=N_STATES).float(),
                tables.reshape(batch, -1),
                sequence.reshape(batch, -1),
                mask,
            ),
            dim=1,
        )
        return self.network(features)


def build_model(
    name: str,
    max_length: int = 12,
    operator_init_std: float | None = None,
    orthogonal_parameterization: str = "qr",
) -> nn.Module:
    key = name.lower()
    if key == "linear_hyper":
        return LinearHyperOperatorRNN(
            hidden_dim=8,
            operator_init_std=0.01 if operator_init_std is None else operator_init_std,
        )
    if key == "linear_hyper_metric":
        return LinearHyperMetricOperatorRNN(
            hidden_dim=8,
            operator_init_std=0.01 if operator_init_std is None else operator_init_std,
        )
    if key == "linear_hyper_hard":
        from .hard_operator import HardOperatorRNN

        return HardOperatorRNN(
            hidden_dim=8,
            parameterization=orthogonal_parameterization,
            operator_init_std=0.08 if operator_init_std is None else operator_init_std,
        )
    if key == "linear_hyper_hard_metric":
        from .hard_operator import HardMetricOperatorRNN

        return HardMetricOperatorRNN(
            hidden_dim=8,
            parameterization=orthogonal_parameterization,
            operator_init_std=0.08 if operator_init_std is None else operator_init_std,
        )
    if key == "gru":
        return GRUOperatorRNN(hidden_dim=32, operator_dim=32)
    if key == "token_only":
        return TokenOnlyRNN(hidden_dim=32, operator_dim=16)
    if key == "one_shot":
        return OneShotMLP(max_length=max_length, width=128)
    raise ValueError(f"Unknown model: {name}")


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
