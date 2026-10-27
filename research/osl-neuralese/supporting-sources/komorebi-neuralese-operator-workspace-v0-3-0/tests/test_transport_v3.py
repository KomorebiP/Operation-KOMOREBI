from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import komorebi_neuralese

from komorebi_neuralese.transport import AffineTransport
from komorebi_neuralese.transport_assays import (
    TRANSPORT_ASSAY_SCHEMA,
    AssayMetadata,
    AttributeHoldout,
    PairedRepresentations,
    StateInducedOperatorTransport,
    build_holdout_partition,
    conditional_fidelity_metrics,
    fit_stable_affine_transport,
    fit_transport_assay,
    fit_transport_assay_from_datasets,
    operator_intertwining_metrics,
    score_component_patches,
    transport_operator_patch,
    transport_state_patch,
)


def _orthogonal(dimension: int, seed: int, *, dtype: torch.dtype) -> torch.Tensor:
    generator = torch.Generator().manual_seed(seed)
    values = torch.randn(dimension, dimension, generator=generator, dtype=dtype)
    return torch.linalg.qr(values).Q


def _codebook_residual_fixture() -> tuple[
    PairedRepresentations,
    object,
    tuple[str, ...],
    torch.Tensor,
]:
    """Eight labels plus within-label context variation and operator codes."""

    dtype = torch.float64
    generator = torch.Generator().manual_seed(4001)
    train_contexts = tuple(f"fit-{index}" for index in range(20))
    test_contexts = tuple(f"heldout-{index}" for index in range(8))
    all_contexts = train_contexts + test_contexts
    labels: list[int] = []
    contexts: list[str] = []
    context_features: list[torch.Tensor] = []
    feature_by_context = {
        context: torch.randn(3, generator=generator, dtype=dtype)
        for context in all_contexts
    }
    for context in all_contexts:
        for label in range(8):
            labels.append(label)
            contexts.append(context)
            context_features.append(feature_by_context[context])

    label_tensor = torch.tensor(labels, dtype=torch.long)
    one_hot = torch.nn.functional.one_hot(label_tensor, num_classes=8).to(dtype)
    residual = torch.stack(context_features)
    source = torch.cat((one_hot, residual), dim=1)
    state_weight = _orthogonal(source.shape[1], 4003, dtype=dtype)
    target = source @ state_weight

    # Codes are context-dependent but shared across starts within a context.
    code_features = torch.stack(
        (
            residual[:, 0],
            residual[:, 1],
            residual[:, 2],
            residual[:, 0] + 0.5 * residual[:, 2],
        ),
        dim=1,
    )
    source_operators = torch.stack((code_features, code_features.roll(1, dims=1)), dim=1)
    operator_weight = torch.randn(4, 6, generator=generator, dtype=dtype)
    target_operators = source_operators @ operator_weight

    data = PairedRepresentations(
        source_states=source,
        target_states=target,
        attributes=label_tensor[:, None],
        context_ids=tuple(contexts),
        source_operators=source_operators,
        target_operators=target_operators,
    )
    partition = build_holdout_partition(
        data.attributes,
        data.context_ids,
        heldout_context_ids=test_contexts,
    )
    return data, partition, test_contexts, state_weight


def test_holdout_partition_excludes_each_factor_and_uses_intersection_for_eval() -> None:
    attributes = torch.tensor(
        [[first, second] for first in range(3) for second in range(4) for _ in range(2)]
    )
    contexts = tuple("heldout" if index % 2 else "fit" for index in range(24))
    partition = build_holdout_partition(
        attributes,
        contexts,
        attribute_holdouts=(AttributeHoldout(0, (2,)), AttributeHoldout(1, (3,))),
        heldout_context_ids=("heldout",),
    )

    fit_attributes = attributes[partition.fit_mask]
    eval_attributes = attributes[partition.evaluation_mask]
    fit_contexts = [context for context, keep in zip(contexts, partition.fit_mask) if bool(keep)]
    eval_contexts = [
        context for context, keep in zip(contexts, partition.evaluation_mask) if bool(keep)
    ]
    assert not bool((fit_attributes[:, 0] == 2).any())
    assert not bool((fit_attributes[:, 1] == 3).any())
    assert set(fit_contexts) == {"fit"}
    assert bool((eval_attributes[:, 0] == 2).all())
    assert bool((eval_attributes[:, 1] == 3).all())
    assert set(eval_contexts) == {"heldout"}
    assert not bool((partition.fit_mask & partition.evaluation_mask).any())


def test_affine_transport_preserves_within_codebook_context_that_baselines_lose() -> None:
    data, partition, _, state_weight = _codebook_residual_fixture()
    metadata = AssayMetadata(
        source_id="seed-0",
        target_id="seed-1",
        anchor_seed=11,
        evaluation_seed=29,
        anchor_partition="train",
        evaluation_partition="test",
    )
    assay = fit_transport_assay(
        data,
        partition,
        metadata=metadata,
        codebook_columns=(0,),
        ridge=1e-10,
        shuffle_seed=31,
    )
    evaluation = data.subset(partition.evaluation_mask)

    def source_decode(hidden: torch.Tensor) -> torch.Tensor:
        return hidden[:, :8].argmax(dim=1)

    def target_decode(hidden: torch.Tensor) -> torch.Tensor:
        return (hidden @ state_weight.T)[:, :8].argmax(dim=1)

    metrics = assay.evaluate_latents(
        evaluation,
        source_decode=source_decode,
        target_reembed=lambda labels: assay.target_centroids.apply(labels),
        target_decode=target_decode,
        source_reembed=lambda labels: assay.source_centroids.apply(labels),
    )

    assert metrics["schema"] == TRANSPORT_ASSAY_SCHEMA
    assert metrics["metadata"] == metadata.to_serializable()
    assert metrics["state"]["forward"]["r2"] > 1.0 - 1e-8
    assert metrics["state"]["forward"]["conditional_residual_r2"] > 1.0 - 1e-8
    assert metrics["state"]["target_centroid_baseline"]["conditional_residual_r2"] == pytest.approx(0.0)
    assert metrics["state"]["forward_decode_reembed_baseline"][
        "conditional_residual_r2"
    ] == pytest.approx(0.0)
    assert metrics["state"]["forward_codebook_contrast"][
        "conditional_residual_r2_minus_centroid"
    ] > 0.99
    assert metrics["state"]["forward_codebook_contrast"][
        "conditional_residual_r2_minus_within_codebook_shuffle"
    ] > 0.25
    assert metrics["state"]["cycle"]["source_cycle"]["r2"] > 1.0 - 1e-7
    assert metrics["state"]["cycle"]["target_cycle"]["r2"] > 1.0 - 1e-7
    assert metrics["state"]["cycle"]["source_cycle_attribute_accuracy"] == 1.0
    assert metrics["operator"]["available"] is True
    assert metrics["operator"]["forward"]["r2"] > 1.0 - 1e-8
    assert metrics["operator"]["reverse"]["r2"] > 1.0 - 1e-8
    assert metrics["operator"]["cycle"]["source_cycle"]["r2"] > 1.0 - 1e-7
    assert metrics["operator"]["forward_shuffled_control"]["r2"] < 0.5
    assert metrics["operator"]["forward_random_map"]["r2"] < 0.5
    assert metrics["fit_diagnostics"]["state_forward"]["calculation_dtype"] == "float64"
    assert metrics["fit_diagnostics"]["state_forward"]["centered_rank"] == 10

    with pytest.raises(ValueError, match="contexts leaked"):
        assay.evaluate_latents(data.subset(partition.fit_mask))


def test_component_patch_reports_invariance_and_native_conditioned_fidelity() -> None:
    factual = torch.tensor(
        [
            [0, 1, 2, 3],
            [1, 2, 3, 4],
            [2, 3, 4, 0],
            [3, 4, 0, 1],
        ]
    )
    patch_mask = torch.eye(4, dtype=torch.bool)
    counterfactual = factual.clone()
    counterfactual[patch_mask] = (counterfactual[patch_mask] + 1) % 5
    aligned = torch.where(patch_mask, counterfactual, factual)
    aligned[-1, -1] = factual[-1, -1]  # one failure, on a native-failed row
    pose_codebook = factual.clone()  # label-only patch changes nothing
    native_prediction = factual.clone()
    native_prediction[-1, 0] = (native_prediction[-1, 0] + 1) % 5

    result = score_component_patches(
        {"affine": aligned, "pose_codebook": pose_codebook},
        counterfactual,
        factual,
        patched_components=patch_mask,
        invariant_components=~patch_mask,
        condition_mask=torch.tensor([True, True, False, True]),
        native_prediction=native_prediction,
        native_target=factual,
        baseline="pose_codebook",
    )
    affine = result["by_method"]["affine"]
    baseline = result["by_method"]["pose_codebook"]
    assert affine["patched_row_accuracy"] == 0.75
    assert affine["invariant_row_accuracy"] == 1.0
    assert affine["joint_component_fidelity"] == 0.75
    assert affine["joint_fidelity_on_native_success"] == 1.0
    assert affine["joint_fidelity_on_native_and_condition"] == 1.0
    assert affine["distinguishing_fraction"] == 1.0
    assert baseline["patched_row_accuracy"] == 0.0
    assert baseline["invariant_row_accuracy"] == 1.0
    assert result["joint_fidelity_minus_baseline"]["affine"] == 0.75

    conditional = conditional_fidelity_metrics(
        aligned,
        torch.where(patch_mask, counterfactual, factual),
        conditions={
            "native_success": (native_prediction == factual).all(dim=1),
            "protocol_eligible": torch.tensor([True, True, False, True]),
        },
    )
    assert conditional["joint_fidelity"] == 0.75
    assert conditional["conditions"]["native_success"]["joint_fidelity"] == 1.0
    assert conditional["all_conditions"]["joint_fidelity"] == 1.0


def test_state_induced_operator_transport_closes_commuting_square_and_patch() -> None:
    dtype = torch.float64
    generator = torch.Generator().manual_seed(5001)
    transform = _orthogonal(3, 5003, dtype=dtype)
    weight = transform.T  # AffineTransport uses row vectors; T = weight.T.
    zero = torch.zeros(3, dtype=dtype)
    state_transport = AffineTransport(weight, zero, zero, zero)
    operator_transport = StateInducedOperatorTransport.from_state_transport(state_transport)

    source_hidden = torch.randn(32, 3, generator=generator, dtype=dtype)
    source_operator = torch.randn(32, 3, 3, generator=generator, dtype=dtype)
    target_hidden = state_transport.apply(source_hidden)
    target_operator = torch.matmul(
        torch.matmul(transform, source_operator),
        transform.T,
    )

    def step(hidden: torch.Tensor, operator: torch.Tensor) -> torch.Tensor:
        return torch.bmm(operator, hidden.unsqueeze(-1)).squeeze(-1)

    metrics = operator_intertwining_metrics(
        source_hidden,
        target_hidden,
        source_operator,
        target_operator,
        state_transport,
        operator_transport,
        source_step=step,
        target_step=step,
    )
    assert metrics["commuting_square"]["mse"] < 1e-24
    assert metrics["transported_step_vs_native_target"]["mse"] < 1e-24
    assert metrics["transported_operator_vs_paired_target"]["mse"] < 1e-24

    patch = transport_operator_patch(
        target_hidden,
        source_operator,
        operator_transport,
        target_step=step,
        target_decode=lambda hidden: hidden,
    )
    assert torch.allclose(patch.transported_code, target_operator, atol=1e-12, rtol=1e-12)
    assert torch.allclose(patch.next_hidden, step(target_hidden, target_operator), atol=1e-12, rtol=1e-12)

    state_patch = transport_state_patch(
        source_hidden,
        state_transport,
        target_continue=lambda hidden: step(hidden, target_operator),
        target_decode=lambda hidden: hidden,
    )
    assert torch.allclose(state_patch.transported_hidden, target_hidden, atol=1e-12, rtol=1e-12)
    assert torch.allclose(
        state_patch.continued_hidden,
        step(target_hidden, target_operator),
        atol=1e-12,
        rtol=1e-12,
    )


def test_metadata_prevents_reusing_anchor_seed_or_partition() -> None:
    with pytest.raises(ValueError, match="seeds must be distinct"):
        AssayMetadata("a", "b", 7, 7, "train", "test")
    with pytest.raises(ValueError, match="partitions must be distinct"):
        AssayMetadata("a", "b", 7, 8, "test", "test")


def test_stable_fit_handles_rank_deficiency_and_records_conditioning() -> None:
    generator = torch.Generator().manual_seed(6001)
    independent = torch.randn(64, 3, generator=generator, dtype=torch.float32)
    source = torch.cat((independent, independent[:, :1]), dim=1)
    target = independent @ torch.randn(3, 2, generator=generator)
    transport, diagnostics = fit_stable_affine_transport(source, target, ridge=0.0)
    assert diagnostics.calculation_dtype == "float64"
    assert diagnostics.centered_rank == 3
    assert diagnostics.maximum_rank == 4
    assert torch.isfinite(transport.weight).all()
    assert torch.mean((transport.apply(source) - target).square()) < 1e-10


def test_attribute_only_holdout_allows_shared_context_but_rejects_value_leak() -> None:
    dtype = torch.float64
    generator = torch.Generator().manual_seed(7001)
    anchor_attributes = torch.tensor([[0], [0], [1], [1]])
    eval_attributes = torch.tensor([[2], [2], [2]])
    anchor_source = torch.randn(4, 2, generator=generator, dtype=dtype)
    eval_source = torch.randn(3, 2, generator=generator, dtype=dtype)
    weight = torch.tensor([[1.2, 0.1], [-0.2, 0.9]], dtype=dtype)
    anchors = PairedRepresentations(
        anchor_source,
        anchor_source @ weight,
        anchor_attributes,
        ("shared",) * 4,
    )
    evaluation = PairedRepresentations(
        eval_source,
        eval_source @ weight,
        eval_attributes,
        ("shared",) * 3,
    )
    combined = PairedRepresentations(
        torch.cat((anchor_source, eval_source)),
        torch.cat((anchor_source @ weight, eval_source @ weight)),
        torch.cat((anchor_attributes, eval_attributes)),
        ("shared",) * 7,
    )
    partition = build_holdout_partition(
        combined.attributes,
        combined.context_ids,
        attribute_holdouts=(AttributeHoldout(0, (2,)),),
    )
    assay = fit_transport_assay(
        combined,
        partition,
        metadata=AssayMetadata("a", "b", 1, 2, "attribute-fit", "attribute-heldout"),
        codebook_columns=(0,),
        ridge=1e-8,
    )
    assert assay.evaluate_latents(evaluation)["evaluation_examples"] == 3
    with pytest.raises(ValueError, match="outside held-out attribute"):
        assay.evaluate_latents(anchors)

    disjoint_eval = PairedRepresentations(
        eval_source,
        eval_source @ weight,
        eval_attributes,
        ("eval-a", "eval-b", "eval-c"),
    )
    direct = fit_transport_assay_from_datasets(
        PairedRepresentations(
            anchor_source,
            anchor_source @ weight,
            anchor_attributes,
            ("fit-a", "fit-a", "fit-b", "fit-b"),
        ),
        disjoint_eval,
        metadata=AssayMetadata("a", "b", 3, 4, "train", "test"),
        codebook_columns=(0,),
        heldout_attribute_columns=(0,),
        ridge=1e-8,
    )
    assert direct.evaluate_latents(disjoint_eval)["evaluation_examples"] == 3
