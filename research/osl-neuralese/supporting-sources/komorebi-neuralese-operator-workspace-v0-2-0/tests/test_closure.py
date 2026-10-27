from __future__ import annotations

import sys
from pathlib import Path

import torch
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import N_STATES
from komorebi_neuralese.closure import (
    anonymous_closure_loss,
    anonymous_composition_metrics,
    compose_action_tables,
    compose_latent_matrices,
    cross_context_state_patch_metrics,
    deep_accuracy_stability,
    expand_neighbor_depths,
    operator_geometry_metrics,
    word_action_tables,
)
from komorebi_neuralese.models import GRUOperatorRNN, RecurrentOperatorModel


class ExactPermutationModel(RecurrentOperatorModel):
    """Parameter-free oracle using column one-hot latent states."""

    model_name = "exact_permutation_oracle"

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        return tables.transpose(-1, -2)

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        return F.one_hot(start, num_classes=N_STATES).to(dtype=torch.float32)

    def step_hidden(self, hidden: torch.Tensor, code: torch.Tensor) -> torch.Tensor:
        return torch.bmm(code, hidden.unsqueeze(-1)).squeeze(-1)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return hidden


class SimilarityExactPermutationModel(ExactPermutationModel):
    """The same oracle in non-Euclidean coordinates with an exact learned-G API."""

    model_name = "similarity_exact_permutation_oracle"

    def __init__(self) -> None:
        super().__init__()
        scales = torch.linspace(0.55, 2.10, N_STATES)
        self.register_buffer("similarity", torch.diag(scales))
        self.register_buffer("similarity_inverse", torch.diag(scales.reciprocal()))

    def encode_operators(self, tables: torch.Tensor) -> torch.Tensor:
        base = tables.transpose(-1, -2)
        return self.similarity @ base @ self.similarity_inverse

    def initial_hidden(self, start: torch.Tensor) -> torch.Tensor:
        canonical = F.one_hot(start, num_classes=N_STATES).to(dtype=self.similarity.dtype)
        return canonical @ self.similarity.transpose(-1, -2)

    def decode_hidden(self, hidden: torch.Tensor) -> torch.Tensor:
        return hidden @ self.similarity_inverse.transpose(-1, -2)

    def metric_matrix(self) -> torch.Tensor:
        return self.similarity_inverse.transpose(-1, -2) @ self.similarity_inverse

    def whiten_operators(self, matrices: torch.Tensor) -> torch.Tensor:
        return self.similarity_inverse @ matrices @ self.similarity


def _table(permutation: list[int]) -> torch.Tensor:
    return F.one_hot(torch.tensor(permutation), num_classes=len(permutation)).float()


def test_neighbor_depth_expansion_includes_requested_and_adjacent_depths() -> None:
    assert expand_neighbor_depths((1, 4), (-1, 0, 1)) == (0, 1, 2, 3, 4, 5)


def test_external_table_composition_has_correct_row_action_order() -> None:
    first_map = torch.tensor([[1, 2, 0, 4, 3]])
    second_map = torch.tensor([[2, 0, 1, 3, 4]])
    first = F.one_hot(first_map, num_classes=5).float()
    second = F.one_hot(second_map, num_classes=5).float()
    observed = compose_action_tables(first, second).argmax(dim=-1)
    expected = torch.gather(second_map, 1, first_map)
    assert torch.equal(observed, expected)


def test_word_action_tables_handles_empty_and_batched_anonymous_words() -> None:
    a = _table([1, 2, 0, 4, 3])
    b = _table([2, 0, 1, 3, 4])
    tables = torch.stack((torch.stack((a, b)), torch.stack((b, a))))
    empty = word_action_tables(tables, torch.empty((2, 0), dtype=torch.long))
    assert torch.equal(empty, torch.eye(5).expand(2, -1, -1))

    slots = torch.tensor([[0, 1, 0], [1, 0, 1]])
    product = word_action_tables(tables, slots)
    maps = tables.argmax(dim=-1)
    state = torch.arange(5).expand(2, -1).clone()
    rows = torch.arange(2)[:, None]
    for step in range(slots.shape[1]):
        selected = maps[torch.arange(2), slots[:, step]]
        state = torch.gather(selected, 1, state)
    assert torch.equal(product.argmax(dim=-1), state)


def test_latent_composition_reverses_matrix_order_for_column_states() -> None:
    first = torch.tensor([[1.0, 1.0], [0.0, 1.0]])
    second = torch.tensor([[1.0, 0.0], [1.0, 1.0]])
    state = torch.tensor([2.0, -1.0])
    sequential = second @ (first @ state)
    correct = compose_latent_matrices(first, second)
    reversed_wrong = first @ second
    assert torch.equal(correct @ state, sequential)
    assert not torch.equal(reversed_wrong @ state, sequential)


def test_anonymous_closure_loss_is_exact_and_differentiable_for_oracle() -> None:
    model = ExactPermutationModel()
    a = _table([1, 2, 0, 4, 3, 6, 7, 5])
    b = _table([2, 0, 1, 3, 4, 7, 5, 6])
    tables = torch.stack((a, b)).unsqueeze(0).repeat(3, 1, 1, 1).requires_grad_(True)
    first_slots = torch.tensor([0, 1, 0])
    second_slots = 1 - first_slots
    loss = anonymous_closure_loss(model, tables, first_slots, second_slots)
    assert loss.ndim == 0
    assert loss.dtype == tables.dtype
    assert torch.isfinite(loss)
    assert float(loss.detach()) < 1e-12
    loss.backward()
    assert tables.grad is not None
    assert torch.isfinite(tables.grad).all()


def test_deliberately_reversed_latent_order_has_nonzero_residual() -> None:
    a = _table([1, 0, 2, 3, 4, 5, 6, 7])
    b = _table([0, 2, 1, 3, 4, 5, 6, 7])
    first_code = a.transpose(-1, -2)
    second_code = b.transpose(-1, -2)
    direct = compose_action_tables(a, b).transpose(-1, -2)
    correct = compose_latent_matrices(first_code, second_code)
    wrong = first_code @ second_code
    assert torch.equal(direct, correct)
    assert float(torch.linalg.matrix_norm(direct - wrong)) > 0.0


def test_deep_stability_reports_neighbors_and_constant_g_norm_for_exact_model() -> None:
    model = SimilarityExactPermutationModel()
    result = deep_accuracy_stability(
        model,
        family="random",
        depths=(3,),
        examples_per_depth=24,
        batch_size=7,
        seed=101,
        device=torch.device("cpu"),
        coordinate_split="test",
        neighbor_offsets=(-1, 0, 1),
    )
    assert result["evaluated_depths"] == [2, 3, 4]
    assert result["coordinate_split"] == "test"
    for record in result["by_depth"].values():
        assert record["endpoint_accuracy"] == 1.0
        assert record["mean_step_accuracy"] == 1.0
        assert record["all_steps_exact_fraction"] == 1.0
        assert record["finite_trajectory_fraction"] == 1.0
        assert abs(record["g_endpoint_ratio_median"] - 1.0) < 1e-5
        assert abs(record["g_transient_gain_p95"] - 1.0) < 1e-5


def test_operator_geometry_uses_learned_metric_whitening() -> None:
    model = SimilarityExactPermutationModel()
    result = operator_geometry_metrics(
        model,
        family="random",
        examples=25,
        batch_size=8,
        seed=211,
        device="cpu",
        coordinate_split="test",
    )
    assert result["available"] is True
    assert result["coordinate_split"] == "test"
    assert set(result["per_visible_slot"]) == {"0", "1"}
    assert abs(result["aggregate"]["spectral_radius_mean"] - 1.0) < 1e-5
    singular = result["aggregate"]["whitened_singular_values_mean_by_rank"]
    assert max(abs(value - 1.0) for value in singular) < 1e-5
    assert result["aggregate"]["normalized_g_isometry_defect_p95"] < 1e-5
    assert result["metric"]["minimum_eigenvalue"] > 0.0
    assert result["metric"]["condition_number"] > 1.0


def test_operator_geometry_fails_closed_for_vector_codes() -> None:
    model = GRUOperatorRNN(hidden_dim=8, operator_dim=5)
    result = operator_geometry_metrics(
        model,
        family="d4",
        examples=4,
        batch_size=4,
        seed=307,
        device="cpu",
        coordinate_split="dev",
    )
    assert result["available"] is False
    assert "not square" in result["reason"]
    assert result["coordinate_split"] == "dev"


def test_anonymous_composed_table_substitution_beats_both_controls() -> None:
    model = SimilarityExactPermutationModel()
    result = anonymous_composition_metrics(
        model,
        family="random",
        examples=31,
        batch_size=8,
        seed=401,
        device="cpu",
        coordinate_split="test",
    )
    assert result["native_two_step_accuracy"] == 1.0
    assert result["true_substitution_accuracy"] == 1.0
    assert result["true_substitution_output_agreement"] == 1.0
    assert result["reversed_distinguishing_fraction"] > 0.0
    assert result["reversed_accuracy_on_distinguishing_examples"] == 0.0
    assert result["wrong_distinguishing_fraction"] == 1.0
    assert result["wrong_accuracy_on_distinguishing_examples"] == 0.0
    assert result["reversed_control_self_accuracy"] == 1.0
    assert result["wrong_control_self_accuracy"] == 1.0
    assert result["ambient_operator_closure_residual"]["maximum"] < 1e-5
    assert result["metric_operator_closure_residual"]["maximum"] < 1e-5


def test_cross_context_patch_uses_distinct_tables_and_on_manifold_wrong_state() -> None:
    model = SimilarityExactPermutationModel()
    result = cross_context_state_patch_metrics(
        model,
        examples=29,
        batch_size=8,
        seed=503,
        device="cpu",
        coordinate_split="test",
        prefix_length=3,
        suffix_length=4,
        donor_family="random",
        recipient_family="random",
    )
    assert result["distinct_operator_context_fraction"] == 1.0
    assert result["distinct_wrong_state_fraction"] == 1.0
    assert result["donor_prefix_accuracy"] == 1.0
    assert result["recipient_native_accuracy"] == 1.0
    assert result["reencoded_state_continuation_accuracy"] == 1.0
    assert result["cross_context_state_patch_accuracy"] == 1.0
    assert result["on_manifold_wrong_state_control_accuracy"] == 0.0
    assert result["cross_context_patch_margin"] == 1.0
    assert result["donor_vs_reencoded_hidden_normalized_g_distance"]["maximum"] < 1e-5
