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


class LinearHyperOperatorRNN(RecurrentOperatorModel):
    """A compact recurrent model whose dynamic operator is a learned latent matrix."""

    model_name = "linear_hyper"

    def __init__(self, hidden_dim: int = 8):
        super().__init__()
        self.hidden_dim = int(hidden_dim)
        self.state_embedding = nn.Embedding(N_STATES, self.hidden_dim)
        self.operator_encoder = nn.Linear(N_STATES * N_STATES, self.hidden_dim * self.hidden_dim, bias=False)
        self.decoder = nn.Linear(self.hidden_dim, N_STATES, bias=False)
        nn.init.normal_(self.state_embedding.weight, std=0.30)
        nn.init.normal_(self.operator_encoder.weight, std=0.01)
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


def build_model(name: str, max_length: int = 12) -> nn.Module:
    key = name.lower()
    if key == "linear_hyper":
        return LinearHyperOperatorRNN(hidden_dim=8)
    if key == "gru":
        return GRUOperatorRNN(hidden_dim=32, operator_dim=32)
    if key == "token_only":
        return TokenOnlyRNN(hidden_dim=32, operator_dim=16)
    if key == "one_shot":
        return OneShotMLP(max_length=max_length, width=128)
    raise ValueError(f"Unknown model: {name}")


def parameter_count(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
