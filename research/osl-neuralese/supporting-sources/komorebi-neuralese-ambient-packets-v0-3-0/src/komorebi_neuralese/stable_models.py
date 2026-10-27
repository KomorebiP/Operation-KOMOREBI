from __future__ import annotations

import copy

import torch

from .models import LinearHyperOperatorRNN, RecurrentOperatorModel
from .stability import anchor_basis, anchor_closed_codes, anchor_metric, metric_polar_codes


class ProjectiveLinearHyperOperatorRNN(LinearHyperOperatorRNN):
    """Trainable raw operator encoder on the positive-ray quotient."""

    model_name = "projective_linear_hyper"

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        updated = super().step_hidden(hidden, code)
        return torch.nn.functional.normalize(updated, dim=-1, eps=1e-12)


class _LinearWrapper(RecurrentOperatorModel):
    def __init__(self, base: LinearHyperOperatorRNN):
        super().__init__()
        self.base = copy.deepcopy(base)
        self.hidden_dim = base.hidden_dim
        for parameter in self.parameters():
            parameter.requires_grad_(False)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return self.base.initial_hidden(start)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return self.base.decode_hidden(hidden)


class AnchorClosedOperatorRNN(_LinearWrapper):
    """Exact latent table transport in the learned state-anchor coordinates."""

    model_name = "anchor_closed"

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return anchor_closed_codes(self.base, tables)

    @property
    def invariant_metric(self) -> torch.Tensor:
        return anchor_metric(self.base)


class MetricPolarOperatorRNN(_LinearWrapper):
    """Norm-preserving control that does not impose semantic table closure."""

    model_name = "metric_polar"

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        raw = self.base.encode_operators(tables)
        return metric_polar_codes(raw, anchor_metric(self.base))

    @property
    def invariant_metric(self) -> torch.Tensor:
        return anchor_metric(self.base)


class NormalizedRawOperatorRNN(_LinearWrapper):
    """Projective-gauge control: raw codes with per-step positive normalization."""

    model_name = "normalized_raw"

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return self.base.encode_operators(tables)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        updated = super().step_hidden(hidden, code)
        return torch.nn.functional.normalize(updated, dim=-1, eps=1e-12)

    @property
    def invariant_metric(self) -> torch.Tensor:
        return anchor_metric(self.base)


class SemanticChartClosedOperatorRNN(_LinearWrapper):
    """Anchor-closed dynamics expressed in canonical one-hot semantic coordinates."""

    model_name = "semantic_chart_closed"

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return tables.transpose(-1, -2)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return torch.nn.functional.one_hot(start, num_classes=self.hidden_dim).to(
            self.base.state_embedding.weight.dtype
        )

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        ambient = (anchor_basis(self.base) @ hidden.unsqueeze(-1)).squeeze(-1)
        return self.base.decode_hidden(ambient)

    @property
    def invariant_metric(self) -> torch.Tensor:
        return torch.eye(
            self.hidden_dim,
            dtype=self.base.state_embedding.weight.dtype,
            device=self.base.state_embedding.weight.device,
        )
