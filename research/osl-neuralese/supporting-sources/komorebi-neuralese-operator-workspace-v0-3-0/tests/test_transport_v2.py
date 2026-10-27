from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import N_OPERATORS, N_STATES
from komorebi_neuralese.models import RecurrentOperatorModel
from komorebi_neuralese.splits import maps_all_in_split
from komorebi_neuralese.transport import (
    AffineTransport,
    collect_paired_hidden,
    evaluate_transport,
    fit_affine_transport,
    fit_shuffled_pair_transport,
    metric_compatibility_metrics,
    random_matched_transport,
)


class CountingRNN(RecurrentOperatorModel):
    model_name = "counting"

    def __init__(self):
        super().__init__()
        self.seen_maps: list[torch.Tensor] = []

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        self.seen_maps.append(tables.argmax(dim=-1).detach().cpu())
        return torch.zeros(tables.shape[0], N_OPERATORS, 1, device=tables.device)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return torch.zeros(start.shape[0], 1, device=start.device)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return hidden + 1.0

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return torch.zeros(hidden.shape[0], N_STATES, device=hidden.device)


class FixedMetric(nn.Module):
    def __init__(self, matrix: torch.Tensor):
        super().__init__()
        self.register_buffer("value", matrix)

    def metric(self) -> torch.Tensor:
        return self.value


class ExactPermutationRNN(RecurrentOperatorModel):
    model_name = "exact_permutation"

    def __init__(self, metric: torch.Tensor | None = None):
        super().__init__()
        self.seen_maps: list[torch.Tensor] = []
        if metric is not None:
            self.metric = FixedMetric(metric)

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        # Episode tables store output one-hots in rows.  Transposing gives the
        # column-vector action used by step_hidden.
        self.seen_maps.append(tables.argmax(dim=-1).detach().cpu())
        return tables.transpose(-1, -2)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return F.one_hot(start, num_classes=N_STATES).float()

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return 20.0 * hidden


def test_anchor_collection_balances_endpoint_depths_and_excludes_h0() -> None:
    source = CountingRNN()
    target = CountingRNN()
    source_hidden, target_hidden = collect_paired_hidden(
        source,
        target,
        seed=101,
        examples=14,
        batch_size=3,
        max_length=4,
        device=torch.device("cpu"),
        coordinate_split="train",
    )
    assert source_hidden.shape == target_hidden.shape == (14, 1)
    assert not torch.any(source_hidden == 0)
    observed = {depth: int((source_hidden[:, 0] == depth).sum()) for depth in range(1, 5)}
    assert observed == {1: 4, 2: 4, 3: 3, 4: 3}
    seen_maps = torch.cat(source.seen_maps, dim=0).numpy()
    assert np.all(maps_all_in_split(seen_maps, "train"))


def test_shuffled_pair_affine_control_destroys_correspondence() -> None:
    generator = torch.Generator().manual_seed(103)
    source = torch.randn(512, 6, generator=generator)
    transform = torch.randn(6, 5, generator=generator)
    bias = torch.randn(5, generator=generator)
    target = source @ transform + bias
    groups = torch.arange(4).repeat_interleave(128)

    fitted = fit_affine_transport(source, target, ridge=1e-7)
    shuffled = fit_shuffled_pair_transport(source, target, seed=107, ridge=1e-7, groups=groups)
    fitted_mse = F.mse_loss(fitted.apply(source), target)
    shuffled_mse = F.mse_loss(shuffled.apply(source), target)
    assert float(fitted_mse) < 1e-8
    assert float(shuffled_mse) > 0.2


def test_metric_compatibility_uses_requested_pullback() -> None:
    transform = torch.tensor([[1.2, 0.3], [-0.2, 0.9]], dtype=torch.float32)
    target_metric = torch.tensor([[2.0, 0.1], [0.1, 1.0]], dtype=torch.float32)
    source_metric = transform.T @ target_metric @ transform
    source = ExactPermutationRNN()
    target = ExactPermutationRNN()
    source.metric = FixedMetric(source_metric)
    target.metric = FixedMetric(target_metric)
    transport = AffineTransport(
        weight=transform.T,
        bias=torch.zeros(2),
        source_mean=torch.zeros(2),
        target_mean=torch.zeros(2),
    )
    metrics = metric_compatibility_metrics(source, target, transport)
    assert metrics["metric_compatibility_available"] is True
    assert metrics["metric_compatibility_normalized_defect"] < 1e-7
    assert metrics["metric_compatibility_cosine"] > 1.0 - 1e-7


def test_transport_evaluation_reports_controls_and_operator_behavior() -> None:
    identity = torch.eye(N_STATES)
    source = ExactPermutationRNN(metric=identity)
    target = ExactPermutationRNN(metric=identity)
    zero = torch.zeros(N_STATES)
    transport = AffineTransport(identity.clone(), zero.clone(), zero.clone(), zero.clone())
    random_control = random_matched_transport(transport, seed=109)

    metrics = evaluate_transport(
        source,
        target,
        transport,
        random_control,
        seed=113,
        examples=48,
        batch_size=11,
        device=torch.device("cpu"),
        length=6,
        split=3,
        family="d4",
        shuffled_transport=random_control,
        coordinate_split="test",
    )
    assert metrics["coordinate_split"] == "test"
    assert metrics["word_product_scope"] == "terminal"
    assert metrics["word_product_split"] == "test"
    assert metrics["aligned_state_patch_accuracy"] == 1.0
    assert metrics["decode_reembed_state_patch_accuracy"] == 1.0
    assert metrics["source_native_accuracy"] == 1.0
    assert metrics["target_native_accuracy"] == 1.0
    assert metrics["shuffled_pair_state_patch_accuracy"] is not None
    assert metrics["operator_intertwining_available"] is True
    assert metrics["operator_intertwining_normalized_frobenius_mean"] < 1e-7
    assert metrics["operator_intertwining_behavior_agreement"] == 1.0
    assert metrics["operator_intertwining_left_next_state_accuracy"] == 1.0
    assert metrics["operator_intertwining_right_next_state_accuracy"] == 1.0
    assert metrics["metric_compatibility_available"] is True
    assert metrics["metric_compatibility_normalized_defect"] < 1e-7
    seen_maps = torch.cat(source.seen_maps, dim=0).numpy()
    assert np.all(maps_all_in_split(seen_maps, "test"))
